"""
Shared helpers for mock platform modules.
"""

from __future__ import annotations

import hashlib
import random
from datetime import date, timedelta


def _seed(campaign_id: str) -> random.Random:
    seed = int(hashlib.md5(campaign_id.encode()).hexdigest(), 16) % (2**32)
    return random.Random(seed)


def generate_mock_metrics(campaign_id: str, days: int = 7) -> list[dict]:
    """
    Return deterministic day-by-day metric rows seeded by campaign_id.
    Repeated calls with the same arguments always return identical data.
    """
    rng = _seed(campaign_id)
    rows = []
    for i in range(days):
        impressions = rng.randint(1_000, 50_000)
        clicks = rng.randint(10, max(11, int(impressions * 0.05)))
        spend = round(rng.uniform(5.0, 150.0), 2)
        conversions = rng.randint(0, max(1, clicks // 5))
        ctr = round(clicks / impressions, 4) if impressions else 0.0
        conversion_value = round(conversions * rng.uniform(20.0, 200.0), 2)
        rows.append(
            {
                "date": (date.today() - timedelta(days=i)).isoformat(),
                "impressions": impressions,
                "clicks": clicks,
                "spend": spend,
                "ctr": ctr,
                "conversions": conversions,
                "conversion_value": conversion_value,
            }
        )
    return rows
