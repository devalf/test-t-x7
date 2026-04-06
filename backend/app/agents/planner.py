"""
Multi-step Claude planner agent.

Workflow:
  1. Validate input (ApiCreateCampaignRequest)
  2. Retrieve RAG constraints for all 3 platforms
  3. Load memory (most recent media plan from DB)
  4. Call Claude to generate ApiMediaPlan JSON
  5. Validate response as ApiMediaPlan (retry up to 3x on failure)
  6. Persist plan to media_plans table
  7. Return ApiMediaPlan
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import UTC, datetime

import anthropic
from shared.models.campaign import ApiCreateCampaignRequest
from shared.models.plan import ApiCreativePack, ApiMediaPlan, ApiTargetingHints
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.config import settings
from app.database import get_db
from app.rag.retriever import retrieve_constraints

logger = logging.getLogger(__name__)

MAX_PLANNING_STEPS = 5
MAX_TOKENS = 2048
MODEL = "claude-sonnet-4-6"

# Fallback plan used when all LLM calls fail — never blocks the user
_FALLBACK_PLAN = ApiMediaPlan(
    objective="sales",
    daily_budget=50.0,
    geo=["US"],
    lang=["en"],
    product_categories=["general"],
    creative_pack=ApiCreativePack(
        headlines=["Shop Now", "Great Deals", "Best Products"],
        descriptions=["Find the best products at great prices.", "Shop our full collection today."],
        long_headlines=["Discover Amazing Products at Unbeatable Prices"],
        primary_texts=["Shop our collection and find exactly what you need."],
        callouts=["Free Shipping", "Easy Returns"],
        image_urls=[],
        logo_url="",
    ),
    targeting_hints=ApiTargetingHints(
        keywords=["buy online", "best deals", "shop now"],
        audiences=["shoppers", "deal seekers"],
        placements=["search", "display"],
    ),
    bidding_strategy="maximize_conversion_value",
)

_PLAN_SCHEMA = json.dumps(ApiMediaPlan.model_json_schema(), indent=2)


def _build_system_prompt(rag_constraints: str) -> str:
    role = (
        "You are a performance marketing strategist with deep expertise"
        " in Google, Meta, and Amazon advertising."
    )
    return f"""{role}

Generate a JSON media plan that EXACTLY matches this schema:
{_PLAN_SCHEMA}

{rag_constraints}

Critical rules:
- Return ONLY valid JSON. No markdown fences, no explanation, no extra text.
- headlines: max 15 items, each max 30 characters
- descriptions: max 4 items, each max 90 characters
- long_headlines: max 5 items, each max 90 characters
- primary_texts: max 5 items, each max 125 characters
- daily_budget must be > 0
- product_categories must be non-empty
- objective must be exactly "sales" or "leads"
- bidding_strategy should match the platform constraints above"""


def _build_user_prompt(
    request: ApiCreateCampaignRequest,
    memory_hint: str | None,
) -> str:
    lines = [
        f"Objective: {request.objective}",
        f"Daily budget: ${request.daily_budget:.2f}",
        f"Product categories: {', '.join(request.product_categories)}",
        f"Geo: {', '.join(request.geo)}",
        f"Language: {', '.join(request.lang)}",
    ]
    if memory_hint:
        lines.append(f"\nPrevious plan context (use as defaults where appropriate):\n{memory_hint}")
    return "\n".join(lines)


def _build_repair_prompt(validation_error: str, bad_json: str) -> str:
    return (
        f"The JSON you returned failed validation:\n{validation_error}\n\n"
        f"Here is what you returned:\n{bad_json}\n\n"
        "Fix the issues and return ONLY the corrected JSON. "
        "No markdown, no explanation."
    )


@retry(
    wait=wait_exponential(min=1, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(anthropic.RateLimitError),
)
async def _call_claude(
    client: anthropic.AsyncAnthropic,
    system: str,
    messages: list[dict],
) -> str:
    response = await client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system,
        messages=messages,
    )
    return response.content[0].text


async def _load_memory() -> str | None:
    """Return a short summary of the most recent media plan for use as a hint."""
    try:
        async with get_db() as db:
            async with db.execute(
                "SELECT plan_json FROM media_plans ORDER BY created_at DESC LIMIT 1"
            ) as cursor:
                row = await cursor.fetchone()
        if row is None:
            return None
        plan = ApiMediaPlan.model_validate_json(row["plan_json"])
        return (
            f"geo={plan.geo}, lang={plan.lang}, "
            f"bidding_strategy={plan.bidding_strategy}, "
            f"budget=${plan.daily_budget:.2f}"
        )
    except Exception:
        logger.exception("Failed to load memory plan")
        return None


async def _persist_plan(plan: ApiMediaPlan) -> None:
    plan_id = str(uuid.uuid4())
    now = datetime.now(UTC).isoformat()
    async with get_db() as db:
        await db.execute(
            "INSERT INTO media_plans (id, plan_json, created_at) VALUES (?, ?, ?)",
            (plan_id, plan.model_dump_json(), now),
        )
        await db.commit()
    logger.info("Persisted media plan %s", plan_id)


async def generate_plan(request: ApiCreateCampaignRequest) -> ApiMediaPlan:
    """
    Full multi-step planner workflow. Returns ApiMediaPlan.
    Never raises — falls back to _FALLBACK_PLAN on total failure.
    """
    # Step 1: Validate (Pydantic already does this via type annotation)
    if request.daily_budget <= 0 or not request.product_categories:
        logger.warning("Invalid request; returning fallback plan")
        return _FALLBACK_PLAN

    # Step 2: RAG constraints
    rag_constraints = retrieve_constraints(["google", "meta", "amazon"])

    # Step 3: Memory
    memory_hint = await _load_memory()

    # Step 4 + 5: Generate + validate with retry loop
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    system = _build_system_prompt(rag_constraints)
    messages: list[dict] = [
        {"role": "user", "content": _build_user_prompt(request, memory_hint)}
    ]

    plan: ApiMediaPlan | None = None
    last_raw = ""

    for attempt in range(1, MAX_PLANNING_STEPS + 1):
        try:
            raw = await _call_claude(client, system, messages)
            last_raw = raw
            logger.debug("Claude attempt %d raw response: %.200s", attempt, raw)

            # Strip accidental markdown fences
            stripped = raw.strip()
            if stripped.startswith("```"):
                stripped = "\n".join(stripped.split("\n")[1:])
                if stripped.endswith("```"):
                    stripped = stripped[: stripped.rfind("```")]

            plan = ApiMediaPlan.model_validate_json(stripped.strip())
            logger.info("Plan validated on attempt %d", attempt)
            break

        except anthropic.APIError as exc:
            logger.error("Anthropic API error on attempt %d: %s", attempt, exc)
            break  # non-rate-limit API errors won't improve with retry

        except Exception as exc:
            logger.warning("Validation failed on attempt %d: %s", attempt, exc)
            if attempt < MAX_PLANNING_STEPS:
                # Repair: append assistant reply + new user repair request
                messages.append({"role": "assistant", "content": last_raw})
                messages.append(
                    {"role": "user", "content": _build_repair_prompt(str(exc), last_raw)}
                )
            continue

    if plan is None:
        logger.error("All planning attempts failed; using fallback plan")
        plan = _FALLBACK_PLAN

    # Step 6: Persist
    try:
        await _persist_plan(plan)
    except Exception:
        logger.exception("Failed to persist plan; continuing anyway")

    # Step 7: Return
    return plan
