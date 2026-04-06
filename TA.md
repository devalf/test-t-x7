Coretas Take-Home Assessment
Dashboard-First Auto-Builder

Product Goal
Build a mini application where:
The user sees a single dashboard listing all connected ad platforms and their campaigns.


With minimal input (objective + daily budget + product categories), the system generates a media plan and creates campaigns on:


Google Ads — Performance Max (+ 1 asset group)


Meta — Shopping / Catalog Sales (Advantage+ eligible setup is fine)


Amazon Ads — Sponsored Brands (one ad group + one creative)


The dashboard compares campaign performance across platforms using five key metrics:


Spend


Impressions


Clicks


CTR


Conversion Value (fallback to Conversions if value unavailable)



Important Note
We do not expect a production-ready system. Mock where appropriate.
The goal is to evaluate:
System architecture


Agentic AI workflow design


Engineering judgment


Clean abstractions


Practical trade-offs


Recommended time investment: 10–12 hours

End-to-End Workflow

A) Dashboard (Landing Page)
Unified table listing all campaigns across platforms.
Required Columns
Platform


Campaign Name


Campaign Type


Spend


Impressions


Clicks


CTR


Conversion Value / Conversions


Filters
By platform


By campaign type


Primary button: “+ Create Campaigns”

B) Minimal Input Modal
Fields:
Objective → Sales | Leads


Daily Budget → numeric


Product Categories → comma-separated or tags


(Optional) Country / Language


On submit:
Generate a structured media plan


Show a preview


User clicks Create All to execute campaign creation



C) Auto-Plan Generation (Planner Agent)
The system must generate a platform-agnostic strategy plan that is later mapped into Google, Meta, and Amazon payloads.
Example Plan Schema
{
 "objective": "sales",
 "daily_budget": 150,
 "geo": ["US"],
 "lang": ["en"],
 "product_categories": ["running shoes", "trail gear"],
 "creative_pack": {
   "headlines": ["...","...","..."],
   "descriptions": ["...","..."],
   "long_headlines": ["..."],
   "primary_texts": ["..."],
   "callouts": ["Free returns","Fast shipping"],
   "image_urls": ["https://.../hero1.jpg","https://.../lifestyle1.jpg"],
   "logo_url": "https://.../logo.png"
 },
 "targeting_hints": {
   "keywords": ["trail shoes","gore-tex running"],
   "audiences": ["runners","outdoor enthusiasts"],
   "placements": ["shopping surfaces"]
 },
 "bidding_strategy": "maximize_conversion_value"
}

Planner & Agent Requirements
The planning component should behave like a structured, multi-step workflow rather than a single unvalidated prompt.
Recommended Flow
Normalize and validate input


Generate initial plan draft


Self-check (schema + logical constraints)


Return strict JSON


Hard Requirements
Plan must validate against a schema (Pydantic/Zod/etc.)


If invalid JSON is produced → implement retry or repair logic


Add guardrails:


Max planning steps (e.g., 3–5)


Basic token/cost awareness


Safe fallback if model fails


Clear separation between:


Planner


Platform mappers


Reporting layer


Persistence



Tool-Oriented Architecture
Design the system so planning is modular and composable.
Example internal tool interfaces:
generate_plan(input) -> plan


validate_plan(plan) -> issues


map_to_google(plan) -> payload


map_to_meta(plan) -> payload


map_to_amazon(plan) -> payload


We want to see structured boundaries and thoughtful orchestration.

Optional Enhancements (Encouraged)
Retrieval-Augmented Planning
Include a small local file (e.g., platform_policies.md) with:
Headline character limits


Creative constraints


Platform-specific rules


Use a retrieval approach (embedding-based or simplified keyword retrieval) to inject relevant constraints into the planning step.

Memory
Persist a summary of the last generated plan.
 If the user creates another campaign, reuse relevant defaults unless overridden.

D) Platform Mapping (Campaign Creation)
Google Ads — Performance Max
Campaign with daily budget


Bidding = Max conversion value


Asset Group using creative_pack


Placeholder final URLs


Apply targeting hints if possible



Meta — Shopping / Catalog Sales
Campaign objective = Sales


Ad Set with geo + daily budget


Broad targeting


Ad using primary text + headline + image/catalog



Amazon — Sponsored Brands
Campaign with daily budget


Start date = today


Bidding = dynamic down only


Ad Group with keywords from targeting_hints


Creative with brand name, headline, logo/image



If sandbox APIs do not allow creation:
Log intended request body


Store mock campaign ID


Continue without blocking other platforms


Each platform must fail gracefully and independently.

E) Reporting → Dashboard
Retrieve metrics for last 7 days (or since creation).
Map into:
{
 "platform": "google|meta|amazon",
 "campaign_id": "string",
 "campaign_name": "string",
 "campaign_type": "pmax|shopping|sponsored_brands",
 "date": "YYYY-MM-DD",
 "spend": 0.0,
 "impressions": 0,
 "clicks": 0,
 "ctr": 0.0,
 "conversions": 0,
 "conversion_value": 0.0,
 "currency": "USD"
}
CTR = clicks / impressions (guard divide-by-zero)


Show Conversions if Conversion Value unavailable



F) Optimization Suggestions (Performance Reasoning)
After retrieving performance metrics, implement a lightweight optimization module.
The system should:
Analyze performance data


Detect simple issues (e.g., low CTR, spend imbalance)


Produce a structured recommendation


Display it in the dashboard


Require human approval before execution


Example Suggestion Output
{
 "campaign_id": "123",
 "issue_detected": "Low CTR on Meta",
 "recommended_action": "Reallocate $30/day from Meta to Google",
 "reasoning": "Google CTR 3.2% vs Meta 0.8%",
 "confidence": 0.76
}
Autonomous execution is not required, but the architecture should make it possible.

Technical Requirements
Backend: Python (FastAPI)
 Frontend: React 
Database: SQLite or in-memory
No OAuth required — use API keys, sandbox tokens, or mocked credentials.

Engineering Expectations
Clear modular architecture


Retries with exponential backoff for 429/5xx


Graceful failure per platform


Config via .env


Reasonable logging


Clean separation of concerns



UI Minimums
Dashboard table


Filters


Create Campaign modal


Plan Preview panel


“Create All” button


Status indicators (Created / Pending / Failed)


Optimization suggestion display



Deliverables
Git repository with runnable app.
README must include:
Setup instructions


Environment variables


Real vs mocked APIs


Planner/agent design approach:


Prompt structure


Schema validation


Guardrails


Failure handling


Optimization logic approach


Platform endpoints used


Architecture diagram (PNG):


UI ↔ API ↔ Planner ↔ Platform Mappers ↔ Reporting ↔ DB

Acceptance Criteria
User can input Objective + Budget + Categories


Structured plan is generated and previewed


“Create All” creates three campaigns


Dashboard displays performance metrics


Optimization suggestions appear after metrics load


System shows thoughtful architecture and practical trade-offs



What We’re Evaluating
Full-stack system design


Agentic workflow architecture


Structured reasoning


Safety & guardrails thinking


Engineering clarity


Pragmatic decision-making


Mocks, simplifications, and stubs are encouraged where appropriate.


