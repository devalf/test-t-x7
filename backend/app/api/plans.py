from __future__ import annotations

from fastapi import APIRouter
from shared.models.campaign import ApiCreateCampaignRequest
from shared.models.plan import ApiMediaPlan

from app.agents.planner import generate_plan

router = APIRouter()


@router.post("/generate", response_model=ApiMediaPlan)
async def generate_plan_endpoint(request: ApiCreateCampaignRequest) -> ApiMediaPlan:
    return await generate_plan(request)
