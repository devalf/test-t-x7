from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Query
from shared.models.metrics import ApiCampaignMetrics, ApiOptimizationSuggestion

from app.agents.optimizer import generate_suggestions
from app.database import get_db
from app.reporting.aggregator import get_all_metrics

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("", response_model=list[ApiCampaignMetrics])
async def list_metrics(days: int = Query(default=7, ge=1, le=90)) -> list[ApiCampaignMetrics]:
    return await get_all_metrics(days=days)


@router.get("/suggestions", response_model=list[ApiOptimizationSuggestion])
async def list_suggestions() -> list[ApiOptimizationSuggestion]:
    return await generate_suggestions()


@router.post(
    "/suggestions/{suggestion_id}/approve",
    response_model=ApiOptimizationSuggestion,
)
async def approve_suggestion(suggestion_id: str) -> ApiOptimizationSuggestion:
    async with get_db() as db:
        async with db.execute(
            "SELECT * FROM optimization_suggestions WHERE id = ?", (suggestion_id,)
        ) as cursor:
            row = await cursor.fetchone()

        if row is None:
            raise HTTPException(status_code=404, detail="Suggestion not found")

        await db.execute(
            "UPDATE optimization_suggestions SET approved = 1 WHERE id = ?",
            (suggestion_id,),
        )
        await db.commit()

    return ApiOptimizationSuggestion(
        id=row["id"],
        campaign_id=row["campaign_id"],
        issue_detected=row["issue_detected"],
        recommended_action=row["recommended_action"],
        reasoning=row["reasoning"],
        confidence=row["confidence"],
        approved=True,
    )
