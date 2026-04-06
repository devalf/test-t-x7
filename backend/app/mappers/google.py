"""
ApiMediaPlan → Google Performance Max campaign payload.
Pure function — no side effects.
"""

from __future__ import annotations

from shared.models.plan import ApiMediaPlan


def map_to_google(plan: ApiMediaPlan) -> dict:
    name = "PMax - " + ", ".join(plan.product_categories[:2])
    return {
        "campaign": {
            "name": name,
            "advertising_channel_type": "PERFORMANCE_MAX",
            "campaign_budget": {
                "amount_micros": int(plan.daily_budget * 1_000_000),
            },
            "maximize_conversion_value": {},
            "geo_targets": plan.geo,
            "language_codes": plan.lang,
        },
        "asset_group": {
            "name": f"{name} - Asset Group 1",
            "headlines": plan.creative_pack.headlines[:15],
            "descriptions": plan.creative_pack.descriptions[:4],
            "long_headlines": plan.creative_pack.long_headlines[:5],
            "callouts": plan.creative_pack.callouts,
            "final_urls": ["https://example.com"],
            "images": plan.creative_pack.image_urls,
            "logo": plan.creative_pack.logo_url,
        },
        "targeting": {
            "keywords": plan.targeting_hints.keywords,
            "audiences": plan.targeting_hints.audiences,
        },
    }
