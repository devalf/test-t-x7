"""
Rule-based optimizer agent.

Aggregates the last N days of metrics per platform, runs heuristic checks,
produces ApiOptimizationSuggestion entries, and persists them to the DB.
"""

from __future__ import annotations

import logging
import uuid
from collections import defaultdict
from datetime import UTC, datetime

from shared.models.metrics import ApiCampaignMetrics, ApiOptimizationSuggestion

from app.database import get_db
from app.reporting.aggregator import get_all_metrics

logger = logging.getLogger(__name__)

_LOW_CTR_THRESHOLD = 0.01  # < 1 %
_SPEND_DOMINANCE_THRESHOLD = 0.70  # one platform > 70 % of total
_ZERO_CONV_SPEND_THRESHOLD = 50.0  # $50 with 0 conversions


def _aggregate(metrics: list[ApiCampaignMetrics]) -> dict[str, dict]:
    """
    Collapse daily rows → per-platform totals/averages.
    Returns {platform: {spend, impressions, clicks, conversions, avg_ctr}}.
    """
    buckets: dict[str, dict] = defaultdict(
        lambda: {
            "spend": 0.0,
            "impressions": 0,
            "clicks": 0,
            "conversions": 0,
            "ctr_sum": 0.0,
            "rows": 0,
            "campaign_ids": set(),
        }
    )
    for m in metrics:
        b = buckets[m.platform]
        b["spend"] += m.spend
        b["impressions"] += m.impressions
        b["clicks"] += m.clicks
        b["conversions"] += m.conversions
        b["ctr_sum"] += m.ctr
        b["rows"] += 1
        b["campaign_ids"].add(m.campaign_id)

    result = {}
    for platform, b in buckets.items():
        avg_ctr = b["ctr_sum"] / b["rows"] if b["rows"] else 0.0
        result[platform] = {
            "spend": b["spend"],
            "impressions": b["impressions"],
            "clicks": b["clicks"],
            "conversions": b["conversions"],
            "avg_ctr": avg_ctr,
            "campaign_ids": b["campaign_ids"],
        }
    return result


def _build_suggestion(
    campaign_id: str,
    issue: str,
    action: str,
    reasoning: str,
    confidence: float,
) -> ApiOptimizationSuggestion:
    return ApiOptimizationSuggestion(
        id=str(uuid.uuid4()),
        campaign_id=campaign_id,
        issue_detected=issue,
        recommended_action=action,
        reasoning=reasoning,
        confidence=round(confidence, 2),
        approved=False,
    )


def _run_rules(agg: dict[str, dict]) -> list[ApiOptimizationSuggestion]:
    suggestions: list[ApiOptimizationSuggestion] = []
    total_spend = sum(v["spend"] for v in agg.values())

    for platform, stats in agg.items():
        # Pick a representative campaign_id for this platform
        campaign_ids = stats["campaign_ids"]
        campaign_id = next(iter(campaign_ids)) if campaign_ids else "unknown"

        avg_ctr = stats["avg_ctr"]
        spend = stats["spend"]
        conversions = stats["conversions"]

        # Rule 1: Low CTR
        if avg_ctr < _LOW_CTR_THRESHOLD:
            suggestions.append(
                _build_suggestion(
                    campaign_id=campaign_id,
                    issue=f"Low CTR on {platform} ({avg_ctr:.2%})",
                    action=(
                        "Refresh creative assets or reallocate budget"
                        " to higher-performing platforms."
                    ),
                    reasoning=(
                        f"{platform.capitalize()} average CTR of {avg_ctr:.2%} is below the "
                        f"{_LOW_CTR_THRESHOLD:.0%} threshold. Stale creatives or poor audience "
                        "targeting are likely causes."
                    ),
                    confidence=0.85 if avg_ctr < _LOW_CTR_THRESHOLD / 2 else 0.65,
                )
            )

        # Rule 2: Spend dominance
        if total_spend > 0 and spend / total_spend > _SPEND_DOMINANCE_THRESHOLD:
            suggestions.append(
                _build_suggestion(
                    campaign_id=campaign_id,
                    issue=(
                        f"Spend imbalance: {platform} consuming"
                        f" {spend/total_spend:.0%} of budget"
                    ),
                    action="Rebalance daily budgets across platforms to diversify reach.",
                    reasoning=(
                        f"{platform.capitalize()} is consuming {spend/total_spend:.0%} of total "
                        f"spend (${spend:.2f} of ${total_spend:.2f}). Concentration risk may "
                        "limit overall campaign reach and increase CPC over time."
                    ),
                    confidence=0.90,
                )
            )

        # Rule 3: Zero conversions with significant spend
        if conversions == 0 and spend > _ZERO_CONV_SPEND_THRESHOLD:
            suggestions.append(
                _build_suggestion(
                    campaign_id=campaign_id,
                    issue=f"Zero conversions on {platform} with ${spend:.2f} spend",
                    action=(
                        "Review audience targeting and keyword match types."
                        " Consider pausing underperforming ad groups."
                    ),
                    reasoning=(
                        f"{platform.capitalize()} has spent ${spend:.2f} with zero conversions. "
                        "Possible causes: wrong audience, poor landing page, or conversion "
                        "tracking issues."
                    ),
                    confidence=0.75,
                )
            )

    return suggestions


async def _persist_suggestions(suggestions: list[ApiOptimizationSuggestion]) -> None:
    now = datetime.now(UTC).isoformat()
    async with get_db() as db:
        for s in suggestions:
            await db.execute(
                """INSERT OR REPLACE INTO optimization_suggestions
                   (id, campaign_id, issue_detected, recommended_action,
                    reasoning, confidence, approved, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    s.id,
                    s.campaign_id,
                    s.issue_detected,
                    s.recommended_action,
                    s.reasoning,
                    s.confidence,
                    int(s.approved),
                    now,
                ),
            )
        await db.commit()
    logger.info("Persisted %d optimization suggestions", len(suggestions))


async def generate_suggestions(days: int = 7) -> list[ApiOptimizationSuggestion]:
    """
    Full optimizer workflow. Never raises — returns [] on total failure.
    """
    try:
        metrics = await get_all_metrics(days=days)
    except Exception:
        logger.exception("Failed to fetch metrics for optimizer")
        return []

    if not metrics:
        logger.info("No metrics available; skipping optimization")
        return []

    agg = _aggregate(metrics)
    suggestions = _run_rules(agg)

    if suggestions:
        try:
            await _persist_suggestions(suggestions)
        except Exception:
            logger.exception("Failed to persist suggestions")

    return suggestions
