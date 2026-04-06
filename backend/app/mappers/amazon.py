"""
ApiMediaPlan → Amazon Sponsored Brands campaign payload.
Pure function — no side effects.
"""

from __future__ import annotations

from datetime import date

from shared.models.plan import ApiMediaPlan


def map_to_amazon(plan: ApiMediaPlan) -> dict:
    long_headline = (
        plan.creative_pack.long_headlines[0] if plan.creative_pack.long_headlines else ""
    )

    return {
        "campaign": {
            "name": f"SB - {', '.join(plan.product_categories[:2])}",
            "campaignType": "sponsoredBrands",
            "dailyBudget": plan.daily_budget,
            "startDate": date.today().isoformat(),
            "state": "enabled",
            "bidding": {
                "strategy": "legacyForSales",
            },
        },
        "adGroup": {
            "name": "AdGroup 1",
            "keywords": [
                {"keywordText": kw, "matchType": "broad"}
                for kw in plan.targeting_hints.keywords[:10]
            ],
        },
        "creative": {
            "brandName": "AdPilot Brand",
            "headline": long_headline[:50],
            "logoAssetId": plan.creative_pack.logo_url,
            "asins": [],
        },
    }
