from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Query
from shared.models.campaign import ApiAdCampaign, ApiCampaignStatus
from shared.models.plan import ApiMediaPlan

from app.database import get_db
from app.mappers.amazon import map_to_amazon
from app.mappers.google import map_to_google
from app.mappers.meta import map_to_meta
from app.mocks import amazon as amazon_mock
from app.mocks import google as google_mock
from app.mocks import meta as meta_mock

router = APIRouter()
logger = logging.getLogger(__name__)


async def _create_one(
    platform: str,
    campaign_type: str,
    campaign_name: str,
    payload: dict,
    mock_module,
    plan: ApiMediaPlan,
) -> ApiAdCampaign:
    mock_response = await asyncio.to_thread(mock_module.create_campaign, payload)
    campaign_id = str(uuid.uuid4())
    external_id = mock_response.get("campaign_id")
    now = datetime.now(UTC).isoformat()

    async with get_db() as db:
        await db.execute(
            "INSERT INTO campaigns"
            " (id, platform, campaign_name, campaign_type,"
            "  status, external_id, plan_json, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                campaign_id,
                platform,
                campaign_name,
                campaign_type,
                ApiCampaignStatus.created.value,
                external_id,
                plan.model_dump_json(),
                now,
            ),
        )
        await db.commit()

    return ApiAdCampaign(
        id=campaign_id,
        platform=platform,
        campaign_name=campaign_name,
        campaign_type=campaign_type,
        status=ApiCampaignStatus.created,
        external_id=external_id,
        created_at=datetime.fromisoformat(now),
    )


async def _create_one_safe(
    platform: str,
    campaign_type: str,
    campaign_name: str,
    payload: dict,
    mock_module,
    plan: ApiMediaPlan,
) -> ApiAdCampaign:
    """On failure, stores a 'failed' row and returns it — never raises."""
    try:
        return await _create_one(platform, campaign_type, campaign_name, payload, mock_module, plan)
    except Exception:
        logger.exception("Failed to create %s campaign", platform)
        campaign_id = str(uuid.uuid4())
        now = datetime.now(UTC).isoformat()
        async with get_db() as db:
            await db.execute(
                "INSERT INTO campaigns"
                " (id, platform, campaign_name, campaign_type,"
                "  status, external_id, plan_json, created_at)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    campaign_id,
                    platform,
                    campaign_name,
                    campaign_type,
                    ApiCampaignStatus.failed.value,
                    None,
                    plan.model_dump_json(),
                    now,
                ),
            )
            await db.commit()
        return ApiAdCampaign(
            id=campaign_id,
            platform=platform,
            campaign_name=campaign_name,
            campaign_type=campaign_type,
            status=ApiCampaignStatus.failed,
            external_id=None,
            created_at=datetime.fromisoformat(now),
        )


@router.post("/create-all", response_model=list[ApiAdCampaign])
async def create_all_campaigns(plan: ApiMediaPlan) -> list[ApiAdCampaign]:
    categories = ", ".join(plan.product_categories[:2])

    results = await asyncio.gather(
        _create_one_safe(
            platform="google",
            campaign_type="pmax",
            campaign_name=f"PMax - {categories}",
            payload=map_to_google(plan),
            mock_module=google_mock,
            plan=plan,
        ),
        _create_one_safe(
            platform="meta",
            campaign_type="shopping",
            campaign_name=f"Meta Shopping - {plan.objective}",
            payload=map_to_meta(plan),
            mock_module=meta_mock,
            plan=plan,
        ),
        _create_one_safe(
            platform="amazon",
            campaign_type="sponsored_brands",
            campaign_name=f"SB - {categories}",
            payload=map_to_amazon(plan),
            mock_module=amazon_mock,
            plan=plan,
        ),
    )
    return list(results)


@router.get("", response_model=list[ApiAdCampaign])
async def list_campaigns(
    platform: str | None = Query(default=None),
    campaign_type: str | None = Query(default=None),
) -> list[ApiAdCampaign]:
    sql = "SELECT * FROM campaigns WHERE 1=1"
    params: list = []
    if platform:
        sql += " AND platform = ?"
        params.append(platform)
    if campaign_type:
        sql += " AND campaign_type = ?"
        params.append(campaign_type)
    sql += " ORDER BY created_at DESC"

    async with get_db() as db:
        async with db.execute(sql, params) as cursor:
            rows = await cursor.fetchall()

    return [
        ApiAdCampaign(
            id=row["id"],
            platform=row["platform"],
            campaign_name=row["campaign_name"],
            campaign_type=row["campaign_type"],
            status=ApiCampaignStatus(row["status"]),
            external_id=row["external_id"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )
        for row in rows
    ]
