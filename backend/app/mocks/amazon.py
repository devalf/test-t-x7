"""
Mock Amazon Ads platform layer.

Simulates Sponsored Brands campaign creation and metric retrieval.
Logs the full intended request body before returning (TA requirement).
"""

from __future__ import annotations

import logging
import uuid

from app.mocks._base import generate_mock_metrics

logger = logging.getLogger(__name__)


def create_campaign(payload: dict) -> dict:
    """
    Simulate Amazon Sponsored Brands campaign creation.
    Returns a fake campaign ID and status.
    """
    logger.info(
        "[MOCK Amazon] create_campaign called with payload: %s",
        payload,
    )
    campaign_id = f"amazon-mock-{uuid.uuid4().hex[:12]}"
    response = {
        "campaign_id": campaign_id,
        "status": "created",
        "platform": "amazon",
        "adGroupId": f"amazon-ag-{uuid.uuid4().hex[:12]}",
    }
    logger.info("[MOCK Amazon] create_campaign response: %s", response)
    return response


def get_metrics(campaign_id: str, days: int = 7) -> list[dict]:
    """
    Return deterministic mock metrics for an Amazon Sponsored Brands campaign.
    """
    logger.info("[MOCK Amazon] get_metrics called: campaign_id=%s days=%d", campaign_id, days)
    rows = generate_mock_metrics(campaign_id, days)
    for row in rows:
        row["currency"] = "USD"
    return rows
