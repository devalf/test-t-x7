"""
Fetch mock metrics for every campaign in the DB and normalize to ApiCampaignMetrics.
"""

from __future__ import annotations

import logging
from datetime import date

from shared.models.metrics import ApiCampaignMetrics

from app.database import get_db
from app.mocks import amazon as amazon_mock
from app.mocks import google as google_mock
from app.mocks import meta as meta_mock

logger = logging.getLogger(__name__)

_MOCK = {
    "google": google_mock,
    "meta": meta_mock,
    "amazon": amazon_mock,
}


async def get_all_metrics(days: int = 7) -> list[ApiCampaignMetrics]:
    """
    Load all campaigns from DB, call each platform mock, return normalized metrics.
    Failures per campaign are logged and skipped — never raises.
    """
    async with get_db() as db:
        async with db.execute(
            "SELECT id, platform, campaign_name, campaign_type, external_id FROM campaigns"
            " WHERE status = 'created'"
        ) as cursor:
            rows = await cursor.fetchall()

    results: list[ApiCampaignMetrics] = []
    for row in rows:
        campaign_id: str = row["id"]
        platform: str = row["platform"]
        external_id: str | None = row["external_id"]
        mock_id = external_id or campaign_id

        mock_module = _MOCK.get(platform)
        if mock_module is None:
            logger.warning("No mock for platform %s, skipping campaign %s", platform, campaign_id)
            continue

        try:
            raw_rows = mock_module.get_metrics(mock_id, days=days)
        except Exception:
            logger.exception("Mock metrics failed for campaign %s", campaign_id)
            continue

        for r in raw_rows:
            impressions = r.get("impressions", 0)
            clicks = r.get("clicks", 0)
            ctr = round(clicks / impressions, 4) if impressions > 0 else 0.0
            try:
                results.append(
                    ApiCampaignMetrics(
                        platform=platform,
                        campaign_id=campaign_id,
                        campaign_name=row["campaign_name"],
                        campaign_type=row["campaign_type"],
                        date=date.fromisoformat(r["date"]),
                        spend=r.get("spend", 0.0),
                        impressions=impressions,
                        clicks=clicks,
                        ctr=ctr,
                        conversions=r.get("conversions", 0),
                        conversion_value=r.get("conversion_value", 0.0),
                        currency=r.get("currency", "USD"),
                    )
                )
            except Exception:
                logger.exception("Failed to build ApiCampaignMetrics for row %s", r)

    return results
