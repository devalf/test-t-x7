from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel


class ApiCampaignStatus(str, Enum):
    pending = "pending"
    created = "created"
    failed = "failed"


class ApiAdCampaign(BaseModel):
    id: str
    platform: Literal["google", "meta", "amazon"]
    campaign_name: str
    campaign_type: Literal["pmax", "shopping", "sponsored_brands"]
    status: ApiCampaignStatus
    external_id: str | None = None  # mock campaign ID from platform
    created_at: datetime


class ApiCreateCampaignRequest(BaseModel):
    objective: Literal["sales", "leads"]
    daily_budget: float
    product_categories: list[str]
    geo: list[str] = ["US"]
    lang: list[str] = ["en"]
