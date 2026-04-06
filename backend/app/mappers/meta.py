"""
ApiMediaPlan → Meta Shopping / Catalog Sales campaign payload.
Pure function — no side effects.
"""

from __future__ import annotations

from shared.models.plan import ApiMediaPlan


def map_to_meta(plan: ApiMediaPlan) -> dict:
    primary_text = plan.creative_pack.primary_texts[0] if plan.creative_pack.primary_texts else ""
    headline = plan.creative_pack.headlines[0] if plan.creative_pack.headlines else ""
    image_url = plan.creative_pack.image_urls[0] if plan.creative_pack.image_urls else None

    return {
        "campaign": {
            "name": f"Meta Shopping - {plan.objective}",
            "objective": "OUTCOME_SALES",
            "special_ad_categories": [],
        },
        "adset": {
            "name": f"AdSet - {', '.join(plan.product_categories[:2])}",
            "daily_budget": int(plan.daily_budget * 100),  # cents
            "geo_locations": {"countries": plan.geo},
            "locales": plan.lang,
            "targeting": {
                "age_min": 18,
                "interests": plan.targeting_hints.audiences,
                "publisher_platforms": plan.targeting_hints.placements,
            },
            "billing_event": "IMPRESSIONS",
            "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
        },
        "ad": {
            "name": f"Ad - {headline[:40]}",
            "message": primary_text,
            "headline": headline,
            "image_url": image_url,
            "call_to_action": {"type": "SHOP_NOW"},
        },
    }
