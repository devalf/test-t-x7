# AdPilot

AI-powered ad campaign manager. Generates cross-platform media plans with Claude, launches campaigns on Google, Meta, and Amazon (mocked), and surfaces optimization suggestions from real-time mock metrics.

---

## Setup

### Prerequisites

- Python 3.12+
- Node.js 18+ with Yarn
- An Anthropic API key

### One-command setup

```bash
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env

make setup
```

`make setup` runs in sequence:
1. Creates a Python virtualenv in `backend/.venv` and installs all dependencies
2. Installs Node dependencies (root + frontend)
3. Initializes the SQLite database (`backend/adpilot.db`)
4. Generates TypeScript types from Pydantic models

---

## Running

```bash
make dev
```

Starts both servers concurrently:

| Service | URL |
|---|---|
| Frontend (Vite + React) | http://localhost:5173 |
| Backend (FastAPI) | http://localhost:8000 |
| API docs (Swagger) | http://localhost:8000/docs |

---

## Environment Variables

### Root `.env`

| Variable | Default | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | *(required)* | Claude API key |
| `DATABASE_URL` | `./adpilot.db` | SQLite file path |
| `FRONTEND_URL` | `http://localhost:5173` | Allowed CORS origin |
| `LOG_LEVEL` | `INFO` | Python log level |
| `VITE_API_URL` | `http://localhost:8000` | Backend URL for the frontend |

Copy `.env.example` to `.env` and fill in your key. The file is gitignored.

---

## Real vs Mocked APIs

All three ad platform APIs are **fully mocked**. No real ad accounts or billing are required.

| Platform | Mocked endpoints | Mock behaviour |
|---|---|---|
| **Google Ads** | Campaign creation, metrics | Deterministic random metrics seeded by campaign ID |
| **Meta Ads** | Campaign + AdSet + Ad creation, metrics | Same seeding strategy |
| **Amazon Ads** | Sponsored Brands campaign + ad group creation, metrics | Same seeding strategy |

Each mock module logs the full intended request body before returning, satisfying the requirement that the platform payload is observable. Mock campaign IDs are persisted to SQLite so repeated metric fetches return consistent data.

---

## Planner Agent

**File:** `backend/app/agents/planner.py`

The planner is a multi-step, Claude-powered agent that converts a `ApiCreateCampaignRequest` into a validated `ApiMediaPlan`.

### Workflow

```
1. Validate input   — budget > 0, product_categories non-empty
2. RAG retrieval    — extract platform policy constraints from platform_policies.md
3. Load memory      — fetch the most recent media plan from SQLite as a default hint
4. Claude call      — generate plan JSON (claude-sonnet-4-6, max_tokens=2048)
5. Validate         — parse response as ApiMediaPlan via Pydantic
6. Repair loop      — on validation failure, append error + bad JSON and retry (up to 5 attempts)
7. Persist          — save plan to media_plans table for future memory
8. Return           — ApiMediaPlan (or safe fallback if all attempts fail)
```

### Prompt structure

```
SYSTEM:
  You are a performance marketing strategist.
  Generate a JSON media plan that EXACTLY matches this schema: {schema}
  Constraints from platform policies:
  {rag_constraints}
  Return ONLY valid JSON. No markdown, no explanation.

USER:
  Objective: {objective}
  Daily budget: ${daily_budget}
  Product categories: {categories}
  Geo: {geo}, Language: {lang}
  {memory_hint if available}
```

### Guardrails

- `MAX_PLANNING_STEPS = 5` — hard cap on the repair loop
- `MAX_TOKENS = 2048` — token ceiling per Claude call
- Exponential backoff via `tenacity` for `RateLimitError` (1–10s, max 3 retries)
- Hardcoded fallback plan returned when all LLM attempts fail — the UI never blocks
- Markdown fence stripping applied before JSON parsing to handle model formatting drift

---

## Optimization Logic

**File:** `backend/app/agents/optimizer.py`

Rule-based, no LLM call required. Runs against the last 7 days of mock metrics.

| Rule | Trigger | Confidence |
|---|---|---|
| **Low CTR** | Platform avg CTR < 1% | 0.65 – 0.85 |
| **Spend imbalance** | One platform > 70% of total spend | 0.90 |
| **Zero conversions** | Conversions = 0 with spend > $50 | 0.75 |

Each detected issue produces an `ApiOptimizationSuggestion` with an `issue_detected` label, `recommended_action`, `reasoning`, and `confidence` score. Suggestions are persisted to SQLite and can be approved via the UI (`POST /api/metrics/suggestions/{id}/approve`).

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/plans/generate` | Generate a media plan via Claude |
| `POST` | `/api/campaigns/create-all` | Launch campaigns on all 3 platforms in parallel |
| `GET` | `/api/campaigns` | List campaigns (filterable by `platform`, `campaign_type`) |
| `GET` | `/api/metrics` | Aggregated metrics for all campaigns (`?days=7`) |
| `GET` | `/api/metrics/suggestions` | Generate and return optimization suggestions |
| `POST` | `/api/metrics/suggestions/{id}/approve` | Approve a suggestion |

---

## Architecture

```
Browser (React + MUI)
     │
     │ HTTP/JSON (Axios + TanStack Query)
     ▼
FastAPI (port 8000)
     │
     ├── POST /api/plans/generate
     │        └── Planner Agent
     │                ├── RAG Retriever (rag/platform_policies.md)
     │                ├── Memory (media_plans table)
     │                └── Claude API (claude-sonnet-4-6)
     │
     ├── POST /api/campaigns/create-all
     │        └── Mappers (google / meta / amazon)
     │                └── Mock Platform Layer → SQLite (campaigns)
     │
     ├── GET /api/campaigns
     │        └── SQLite (campaigns, filtered)
     │
     ├── GET /api/metrics
     │        └── Reporting Aggregator
     │                └── Mock Metrics → SQLite (campaign_metrics)
     │
     └── GET /api/metrics/suggestions
              └── Optimizer Agent → SQLite (optimization_suggestions)

Shared Models (single source of truth)
  shared/models/ (Pydantic) → shared/schemas/ (JSON Schema) → shared/types/ (TypeScript)
```

### Key engineering decisions

- **No circular imports** — `shared/models` has zero dependencies on backend code. Backend imports from shared via `PYTHONPATH=..`.
- **Platform independence** — each platform mapper + mock runs in `asyncio.gather(return_exceptions=True)`. One platform failure never affects the others.
- **Retry logic** — `tenacity` exponential backoff for Anthropic rate limits; repair-loop retries for schema validation failures.
- **CTR guard** — `ctr = clicks / impressions if impressions > 0 else 0.0` enforced in both the aggregator and the Pydantic model validator.
- **Memory** — the last media plan is stored in `media_plans`. On the next generation call, it is retrieved and injected as a hint so the planner maintains continuity across sessions.
- **Secrets** — only `.env`, never hardcoded. `.env` is gitignored.
- **Generated types** — `shared/types/` is gitignored and always regenerated from Python source via `make generate-types`. This ensures the TypeScript and Python models are never out of sync.

---

## Other Commands

```bash
make lint       # ruff (backend) + eslint (frontend)
make format     # ruff format (backend) + prettier (frontend)
make db-init    # (re)create SQLite tables
make generate-types  # regenerate shared/types/ from Pydantic models
```
