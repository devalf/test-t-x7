from __future__ import annotations

from datetime import date

from pydantic import BaseModel, field_validator


class ApiCampaignMetrics(BaseModel):
    platform: str
    campaign_id: str
    campaign_name: str
    campaign_type: str
    date: date
    spend: float
    impressions: int
    clicks: int
    ctr: float  # computed: clicks / impressions, guarded against /0
    conversions: int
    conversion_value: float
    currency: str = "USD"

    @field_validator("ctr", mode="before")
    @classmethod
    def compute_ctr(cls, v: float) -> float:
        # ctr is passed pre-computed; validator just ensures it's non-negative
        return max(0.0, float(v))


class ApiOptimizationSuggestion(BaseModel):
    id: str
    campaign_id: str
    issue_detected: str
    recommended_action: str
    reasoning: str
    confidence: float  # 0.0 – 1.0
    approved: bool = False
