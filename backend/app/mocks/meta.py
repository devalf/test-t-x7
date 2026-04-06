"""
Mock Meta Ads platform layer.

Simulates Shopping / Catalog Sales campaign creation and metric retrieval.
Logs the full intended request body before returning (TA requirement).
"""

from __future__ import annotations

import logging
import uuid

from app.mocks._base import generate_mock_metrics

logger = logging.getLogger(__name__)


def create_campaign(payload: dict) -> dict:
    """
    Simulate Meta Shopping campaign creation.
    Returns a fake campaign ID and status.
    """
    logger.info(
        "[MOCK Meta] create_campaign called with payload: %s",
        payload,
    )
    campaign_id = f"meta-mock-{uuid.uuid4().hex[:12]}"
    adset_id = f"meta-adset-{uuid.uuid4().hex[:12]}"
    ad_id = f"meta-ad-{uuid.uuid4().hex[:12]}"
    response = {
        "campaign_id": campaign_id,
        "adset_id": adset_id,
        "ad_id": ad_id,
        "status": "created",
        "platform": "meta",
    }
    logger.info("[MOCK Meta] create_campaign response: %s", response)
    return response


def get_metrics(campaign_id: str, days: int = 7) -> list[dict]:
    """
    Return deterministic mock metrics for a Meta Shopping campaign.
    """
    logger.info("[MOCK Meta] get_metrics called: campaign_id=%s days=%d", campaign_id, days)
    rows = generate_mock_metrics(campaign_id, days)
    for row in rows:
        row["currency"] = "USD"
    return rows
