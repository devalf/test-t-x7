# AdPilot — Implementation Plan

## Stack & Decisions

| Layer | Choice | Reason |
|---|---|---|
| Backend | Python 3.14 + FastAPI + uvicorn | Required by TA |
| Database | SQLite via aiosqlite | Lightweight, persistent, async |
| LLM | Claude (Anthropic SDK) | claude-sonnet-4-6 |
| Frontend | Vite + React + TypeScript | Fast, minimal |
| Styling | Tailwind CSS + shadcn/ui | Utility-first, accessible components |
| Shared models | Pydantic → JSON Schema → TypeScript | Single source of truth |
| Platform APIs | Fully mocked | Per TA guidance |
| Monorepo | Root Makefile + root package.json | Single entry point for all commands |
| HTTP client | Axios | Typed, interceptors, consistent error handling |
| Data layer | TanStack Query (TQ) | Server state, caching, loading/error states |
| Linting/format (TS) | ESLint + Prettier | Auto-format on save via VS Code |
| Linting/format (Py) | Ruff | Single tool for lint + format, replaces Black + flake8 |

---

## Project Structure

> Working directory: `test-t-x7` — project name is `adpilot` throughout all configs, docs, and dependencies.

```
./ (adpilot project root)
├── .env.example
├── .env                          ← gitignored
├── .vscode/
│   └── settings.json             ← format on save for TS + Python
├── Makefile                      ← all dev commands live here
├── package.json                  ← root: concurrently, codegen scripts
├── shared/
│   ├── models/                   ← Python source of truth (Pydantic)
│   │   ├── __init__.py
│   │   ├── plan.py               ← ApiMediaPlan, ApiCreativePack, ApiTargetingHints
│   │   ├── campaign.py           ← ApiAdCampaign, ApiCreateCampaignRequest, ApiCampaignStatus
│   │   └── metrics.py            ← ApiCampaignMetrics, ApiOptimizationSuggestion
│   ├── types/                    ← AUTO-GENERATED TypeScript — do not edit manually
│   │   ├── plan.ts
│   │   ├── campaign.ts
│   │   └── metrics.ts
│   └── scripts/
│       └── generate_types.py     ← dumps JSON schemas → calls json-schema-to-typescript
├── backend/
│   ├── pyproject.toml            ← includes Ruff config
│   ├── .venv/                    ← gitignored
│   └── app/
│       ├── main.py               ← FastAPI app, CORS, router registration
│       ├── config.py             ← Settings (pydantic-settings, reads .env)
│       ├── database.py           ← SQLite connection, table init
│       ├── api/
│       │   ├── __init__.py
│       │   ├── plans.py          ← POST /api/plans/generate
│       │   ├── campaigns.py      ← POST /api/campaigns/create-all, GET /api/campaigns
│       │   └── metrics.py        ← GET /api/metrics, GET /api/metrics/suggestions
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── planner.py        ← multi-step Claude planner agent
│       │   └── optimizer.py      ← performance reasoning agent
│       ├── mappers/
│       │   ├── __init__.py
│       │   ├── google.py         ← ApiMediaPlan → Google PMax payload
│       │   ├── meta.py           ← ApiMediaPlan → Meta Shopping payload
│       │   └── amazon.py         ← ApiMediaPlan → Amazon Sponsored Brands payload
│       ├── mocks/
│       │   ├── __init__.py
│       │   ├── google.py         ← fake campaign creation + metrics
│       │   ├── meta.py
│       │   └── amazon.py
│       ├── reporting/
│       │   ├── __init__.py
│       │   └── aggregator.py     ← fetches metrics from mocks, normalizes to ApiCampaignMetrics
│       └── rag/
│           ├── __init__.py
│           ├── retriever.py      ← keyword-based constraint retrieval
│           └── platform_policies.md
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.ts
    ├── tsconfig.json
    ├── components.json           ← shadcn/ui config
    ├── eslint.config.ts
    ├── prettier.config.ts
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── types/                ← re-exports from ../../shared/types
        │   └── index.ts
        ├── lib/
        │   └── axiosClient.ts    ← axios instance, base URL, interceptors
        ├── repository/           ← axios functions, one file per domain
        │   ├── index.ts          ← re-exports campaigns, plans, metrics
        │   ├── campaigns.ts      ← fetchCampaigns, createAllCampaigns
        │   ├── plans.ts          ← fetchGeneratePlan
        │   └── metrics.ts        ← fetchMetrics, fetchSuggestions, approveSuggestion
        ├── hooks/
        │   └── data/             ← TanStack Query hooks
        │       ├── index.ts      ← re-exports all hooks
        │       ├── useCampaigns.ts
        │       ├── useGeneratePlan.ts
        │       ├── useMetrics.ts
        │       └── useSuggestions.ts
        └── components/
            ├── Dashboard/
            │   ├── index.tsx
            │   ├── CampaignTable.tsx
            │   └── Filters.tsx
            ├── CreateCampaign/
            │   ├── Modal.tsx
            │   ├── InputForm.tsx
            │   └── PlanPreview.tsx
            └── Optimization/
                └── SuggestionCard.tsx
```

---

## Phase 0 — Repo Scaffolding

**Goal:** Empty project wired up end-to-end before any real code.

### Steps

1. Project root is `test-t-x7` — no folder creation needed, `cd` there. Git already initialized.
2. Create `.gitignore` — exclude `.env`, `__pycache__`, `.venv`, `node_modules`, `shared/types/`
4. Create root `package.json`:
   ```json
   {
     "name": "adpilot",
     "private": true,
     "scripts": {
       "dev": "concurrently \"make backend\" \"make frontend\" --names backend,frontend",
       "generate-types": "python3 shared/scripts/generate_types.py && yarn ts-gen",
       "ts-gen": "json2ts -i shared/schemas -o shared/types --unreachableDefinitions"
     },
     "devDependencies": {
       "concurrently": "^9.x",
       "json-schema-to-typescript": "^15.x"
     }
   }
   ```
5. Create `Makefile`:
   ```makefile
   .PHONY: setup install dev backend frontend generate-types db-init

   setup: install db-init generate-types

   install:
       cd backend && python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
       yarn install

   dev:
       yarn dev

   backend:
       cd backend && .venv/bin/uvicorn app.main:app --reload --port 8000

   frontend:
       cd frontend && yarn dev

   generate-types:
       cd backend && .venv/bin/python ../shared/scripts/generate_types.py
       yarn ts-gen

   db-init:
       cd backend && .venv/bin/python -c "import asyncio; from app.database import init_db; asyncio.run(init_db())"

   lint:
       cd backend && .venv/bin/ruff check .
       cd frontend && yarn eslint src

   format:
       cd backend && .venv/bin/ruff format .
       cd frontend && yarn prettier --write src
   ```
6. Create `.env.example`:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   DATABASE_URL=./adpilot.db
   FRONTEND_URL=http://localhost:5173
   LOG_LEVEL=INFO
   ```

---

## Phase 1 — Shared Models (Source of Truth)

**Goal:** Define all API data shapes once in Python. Generate TypeScript automatically.

### 1.1 Pydantic Models

All models use the `Api` prefix. All models inherit from `pydantic.BaseModel`.

**`shared/models/plan.py`**
```python
class ApiCreativePack(BaseModel):
    headlines: list[str]           # max 15, each max 30 chars (Google)
    descriptions: list[str]        # max 4, each max 90 chars
    long_headlines: list[str]      # max 5, each max 90 chars
    primary_texts: list[str]       # Meta: max 5, each max 125 chars
    callouts: list[str]
    image_urls: list[str]
    logo_url: str

class ApiTargetingHints(BaseModel):
    keywords: list[str]
    audiences: list[str]
    placements: list[str]

class ApiMediaPlan(BaseModel):
    objective: Literal["sales", "leads"]
    daily_budget: float
    geo: list[str]
    lang: list[str]
    product_categories: list[str]
    creative_pack: ApiCreativePack
    targeting_hints: ApiTargetingHints
    bidding_strategy: str
```

**`shared/models/campaign.py`**
```python
class ApiCampaignStatus(str, Enum):
    pending = "pending"
    created = "created"
    failed = "failed"

class ApiAdCampaign(BaseModel):
    id: str
    platform: Literal["google", "meta", "amazon"]
    campaign_name: str
    campaign_type: Literal["pmax", "shopping", "sponsored_brands"]
    status: ApiCampaignStatus
    external_id: str | None       # mock campaign ID from platform
    created_at: datetime

class ApiCreateCampaignRequest(BaseModel):
    objective: Literal["sales", "leads"]
    daily_budget: float
    product_categories: list[str]
    geo: list[str] = ["US"]
    lang: list[str] = ["en"]
```

**`shared/models/metrics.py`**
```python
class ApiCampaignMetrics(BaseModel):
    platform: Literal["google", "meta", "amazon"]
    campaign_id: str
    campaign_name: str
    campaign_type: str
    date: date
    spend: float
    impressions: int
    clicks: int
    ctr: float                    # computed: clicks / impressions, guard /0
    conversions: int
    conversion_value: float
    currency: str = "USD"

class ApiOptimizationSuggestion(BaseModel):
    campaign_id: str
    issue_detected: str
    recommended_action: str
    reasoning: str
    confidence: float             # 0.0 – 1.0
    approved: bool = False
```

### 1.2 Type Generation Script

**`shared/scripts/generate_types.py`**

```python
# Imports all ApiXxx models, calls model_json_schema(),
# writes one JSON schema file per module to shared/schemas/*.json
# Then Makefile runs json-schema-to-typescript on those files
```

Flow:
1. Import each model module
2. Build a `$defs`-style JSON schema per file using `model_json_schema()`
3. Write to `shared/schemas/plan.json`, `campaign.json`, `metrics.json`
4. `json2ts` CLI converts each to `shared/types/plan.ts` etc.
5. Generated TS interfaces are named exactly as the Pydantic classes: `ApiMediaPlan`, `ApiAdCampaign`, etc.

> Run: `make generate-types` — never edit `shared/types/` manually.

---

## Phase 2 — Backend Setup

### 2.1 Dependencies (`backend/pyproject.toml`)

```toml
[project]
name = "adpilot-backend"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.32",
    "pydantic>=2.9",
    "pydantic-settings>=2.6",
    "anthropic>=0.40",
    "aiosqlite>=0.20",
    "python-dotenv>=1.0",
    "httpx>=0.28",
    "tenacity>=9.0",
]

[project.optional-dependencies]
dev = ["ruff>=0.9"]
```

### 2.2 Config (`app/config.py`)

```python
class Settings(BaseSettings):
    anthropic_api_key: str
    database_url: str = "./adpilot.db"
    frontend_url: str = "http://localhost:5173"
    log_level: str = "INFO"
    model_config = SettingsConfigDict(env_file="../.env")

settings = Settings()
```

### 2.3 Database (`app/database.py`)

Tables:

| Table | Columns |
|---|---|
| `campaigns` | id, platform, campaign_name, campaign_type, status, external_id, plan_json, created_at |
| `campaign_metrics` | id, campaign_id, date, spend, impressions, clicks, ctr, conversions, conversion_value, currency |
| `media_plans` | id, plan_json, created_at (last plan memory) |
| `optimization_suggestions` | id, campaign_id, issue_detected, recommended_action, reasoning, confidence, approved, created_at |

Use `aiosqlite` with async context managers. `init_db()` creates tables if not exist.

### 2.4 Main App (`app/main.py`)

```python
app = FastAPI(title="AdPilot API")

app.add_middleware(CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(plans_router, prefix="/api/plans")
app.include_router(campaigns_router, prefix="/api/campaigns")
app.include_router(metrics_router, prefix="/api/metrics")

@app.on_event("startup")
async def startup(): await init_db()
```

---

## Phase 3 — RAG: Platform Policies

**Goal:** Inject platform-specific constraints into the planner prompt at generation time.

### 3.1 `rag/platform_policies.md`

```markdown
## Google Performance Max
- Headlines: max 15, each max 30 characters
- Descriptions: max 4, each max 90 characters
- Long headlines: max 5, each max 90 characters
- Final URLs required
- Bidding: Maximize conversion value

## Meta Shopping / Catalog Sales
- Primary text: max 125 characters
- Headline: max 40 characters
- Image aspect ratio: 1:1 or 1.91:1
- Objective must be OUTCOME_SALES

## Amazon Sponsored Brands
- Brand name: max 30 characters
- Headline: max 50 characters
- Logo image required
- Keywords: exact/phrase/broad match types
- Bidding: dynamic-bids-down-only
```

### 3.2 `rag/retriever.py`

Simple keyword retrieval (no embeddings needed — file is small):

```python
def retrieve_constraints(product_categories: list[str], platforms: list[str]) -> str:
    """
    Reads platform_policies.md, extracts sections matching requested platforms.
    Returns a concatenated string injected into the planner prompt.
    """
```

---

## Phase 4 — Planner Agent

**Goal:** Multi-step, validated, Claude-powered plan generator with retry logic.

### 4.1 Workflow (`agents/planner.py`)

```
Step 1: Normalize input
  - Validate ApiCreateCampaignRequest
  - Check daily_budget > 0, product_categories non-empty

Step 2: Retrieve constraints (RAG)
  - Call retriever.retrieve_constraints()
  - Inject into system prompt

Step 3: Load memory (last plan if exists)
  - Query media_plans table for most recent entry
  - Extract defaults (geo, lang, bidding_strategy) to suggest

Step 4: Generate plan draft (Claude API call)
  - System prompt: role, constraints from RAG, output format (strict JSON)
  - User prompt: objective, budget, categories, geo, lang, memory defaults
  - Request: claude-sonnet-4-6, max_tokens=2048, temperature=0.3

Step 5: Validate (Pydantic)
  - Parse response as ApiMediaPlan
  - If validation fails → repair prompt → retry (max 3 attempts)
  - If all retries fail → return safe fallback plan

Step 6: Persist plan to DB (memory)
  - Upsert into media_plans table

Step 7: Return ApiMediaPlan
```

### 4.2 Guardrails

- `MAX_PLANNING_STEPS = 5` — hard cap on retry loop iterations
- `MAX_TOKENS = 2048` — token ceiling per call
- Exponential backoff via `tenacity` for 429/5xx from Anthropic API:
  ```python
  @retry(wait=wait_exponential(min=1, max=10), stop=stop_after_attempt(3),
         retry=retry_if_exception_type(anthropic.RateLimitError))
  ```
- Safe fallback plan hardcoded for when all LLM calls fail — never blocks the user

### 4.3 Prompt Structure

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

---

## Phase 5 — Platform Mappers

**Goal:** Pure functions. `ApiMediaPlan` in → platform-specific payload dict out. No side effects.

### `mappers/google.py`
```python
def map_to_google(plan: ApiMediaPlan) -> dict:
    return {
        "campaign": {
            "name": f"PMax - {', '.join(plan.product_categories[:2])}",
            "advertising_channel_type": "PERFORMANCE_MAX",
            "campaign_budget": {"amount_micros": int(plan.daily_budget * 1_000_000)},
            "maximize_conversion_value": {},
        },
        "asset_group": {
            "headlines": plan.creative_pack.headlines[:15],
            "descriptions": plan.creative_pack.descriptions[:4],
            "long_headlines": plan.creative_pack.long_headlines[:5],
            "final_urls": ["https://example.com"],
            "images": plan.creative_pack.image_urls,
        }
    }
```

### `mappers/meta.py`
```python
def map_to_meta(plan: ApiMediaPlan) -> dict:
    return {
        "campaign": {
            "name": f"Meta Shopping - {plan.objective}",
            "objective": "OUTCOME_SALES",
            "special_ad_categories": [],
        },
        "adset": {
            "daily_budget": int(plan.daily_budget * 100),  # cents
            "geo_locations": {"countries": plan.geo},
            "targeting": {"age_min": 18},
            "billing_event": "IMPRESSIONS",
            "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
        },
        "ad": {
            "message": plan.creative_pack.primary_texts[0],
            "headline": plan.creative_pack.headlines[0],
            "image_url": plan.creative_pack.image_urls[0] if plan.creative_pack.image_urls else None,
        }
    }
```

### `mappers/amazon.py`
```python
def map_to_amazon(plan: ApiMediaPlan) -> dict:
    return {
        "campaign": {
            "name": f"SB - {', '.join(plan.product_categories[:2])}",
            "campaignType": "sponsoredBrands",
            "dailyBudget": plan.daily_budget,
            "startDate": date.today().isoformat(),
            "bidding": {"strategy": "legacyForSales"},
        },
        "adGroup": {
            "name": "AdGroup 1",
            "keywords": [{"keywordText": k, "matchType": "broad"} for k in plan.targeting_hints.keywords[:10]],
        },
        "creative": {
            "brandName": "AdPilot Brand",
            "headline": plan.creative_pack.long_headlines[0],
            "logoAssetId": plan.creative_pack.logo_url,
        }
    }
```

---

## Phase 6 — Mock Platform Layer

**Goal:** Simulate realistic API responses. Store fake campaign IDs. Generate plausible mock metrics.

Each mock module exposes two functions:
- `create_campaign(payload: dict) -> dict` — returns `{ "campaign_id": "mock-xxx", "status": "created" }`
- `get_metrics(campaign_id: str, days: int = 7) -> list[dict]` — returns day-by-day metric rows

### Mock metrics generation strategy

Generate deterministic-ish random metrics seeded by `campaign_id` so repeated calls return the same data:

```python
import random, hashlib

def _seed(campaign_id: str) -> random.Random:
    seed = int(hashlib.md5(campaign_id.encode()).hexdigest(), 16) % (2**32)
    return random.Random(seed)

def get_metrics(campaign_id: str, days: int = 7) -> list[dict]:
    rng = _seed(campaign_id)
    rows = []
    for i in range(days):
        impressions = rng.randint(1000, 50000)
        clicks = rng.randint(10, int(impressions * 0.05))
        spend = round(rng.uniform(5.0, 150.0), 2)
        conversions = rng.randint(0, clicks // 5)
        rows.append({
            "date": (date.today() - timedelta(days=i)).isoformat(),
            "impressions": impressions,
            "clicks": clicks,
            "spend": spend,
            "ctr": round(clicks / impressions, 4) if impressions else 0.0,
            "conversions": conversions,
            "conversion_value": round(conversions * rng.uniform(20, 200), 2),
        })
    return rows
```

Each platform mock logs the full intended request body before returning — satisfies the TA requirement.

---

## Phase 7 — API Routes

### `POST /api/plans/generate`
- Body: `ApiCreateCampaignRequest`
- Calls planner agent
- Returns: `ApiMediaPlan`
- Stores plan in `media_plans` table

### `POST /api/campaigns/create-all`
- Body: `ApiMediaPlan`
- Runs all 3 mappers → all 3 mocks in parallel (`asyncio.gather`)
- Each platform fails independently (try/except per platform)
- Stores 3 `ApiAdCampaign` rows in DB
- Returns: `list[ApiAdCampaign]` with per-platform status

### `GET /api/campaigns`
- Query params: `platform?`, `campaign_type?`
- Returns: `list[ApiAdCampaign]` (from DB, filtered)

### `GET /api/metrics`
- Query params: `days=7`
- Fetches metrics from mock layer for all campaigns in DB
- Normalizes via `reporting/aggregator.py`
- Returns: `list[ApiCampaignMetrics]`

### `GET /api/metrics/suggestions`
- Reads latest metrics
- Calls optimizer agent
- Returns: `list[ApiOptimizationSuggestion]`

### `POST /api/metrics/suggestions/{id}/approve`
- Sets `approved=True` in DB
- Returns updated suggestion

---

## Phase 8 — Optimizer Agent

**Goal:** Lightweight performance reasoning. Detect issues, produce structured suggestions.

### Logic (`agents/optimizer.py`)

Rule-based first, optionally Claude-enhanced:

```
1. Aggregate metrics per platform (sum/avg last 7 days)
2. Run rule checks:
   - Low CTR: platform CTR < 1.0% → suggest creative refresh or budget reallocation
   - Spend imbalance: one platform > 70% of total spend → suggest rebalancing
   - Zero conversions with spend > $50 → suggest audience/keyword review
3. For each detected issue → build ApiOptimizationSuggestion
4. Persist suggestions to DB
5. Return list
```

Confidence score: simple heuristic (e.g., 0.9 for clear imbalance, 0.6 for borderline CTR).

> Claude call is optional here — rule-based is sufficient and more predictable for the TA demo.

---

## Phase 9 — Frontend Setup

### 9.1 Scaffold

```bash
# Run from project root (test-t-x7)
yarn create vite frontend --template react-ts
cd frontend
yarn dlx shadcn@latest init
```

### 9.2 Install dependencies

```bash
yarn add axios @tanstack/react-query

yarn add -D tailwindcss @tailwindcss/vite eslint @eslint/js typescript-eslint eslint-plugin-react-hooks prettier eslint-config-prettier eslint-plugin-prettier
```

### 9.3 shadcn/ui components needed

```bash
yarn dlx shadcn@latest add table button dialog input badge select card tooltip
```

### 9.4 Vite config — path alias for shared types

```typescript
// vite.config.ts
resolve: {
  alias: {
    "@shared": path.resolve(__dirname, "../shared/types"),
    "@": path.resolve(__dirname, "./src"),
  }
}
```

### 9.5 ESLint config (`eslint.config.ts`)

```typescript
import js from "@eslint/js";
import tseslint from "typescript-eslint";
import reactHooks from "eslint-plugin-react-hooks";
import prettier from "eslint-config-prettier";

export default tseslint.config(
  js.configs.recommended,
  ...tseslint.configs.recommended,
  { plugins: { "react-hooks": reactHooks }, rules: reactHooks.configs.recommended.rules },
  prettier,
);
```

### 9.6 Prettier config (`prettier.config.ts`)

```typescript
export default {
  semi: true,
  singleQuote: true,
  trailingComma: "all",
  printWidth: 100,
  tabWidth: 2,
};
```

### 9.7 Ruff config (in `backend/pyproject.toml`)

```toml
[tool.ruff]
line-length = 100
target-version = "py314"

[tool.ruff.lint]
select = ["E", "F", "I", "UP"]   # pycodestyle, pyflakes, isort, pyupgrade

[tool.ruff.format]
quote-style = "double"
```

### 9.8 VS Code settings (`.vscode/settings.json`)

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff"
  },
  "ruff.organizeImports": true,
  "eslint.validate": ["typescript", "typescriptreact"],
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": "explicit"
  }
}
```

> Required VS Code extensions: `esbenp.prettier-vscode`, `charliermarsh.ruff`, `dbaeumer.vscode-eslint`
> Add to `.vscode/extensions.json` as recommendations.

### 9.9 Axios client (`src/lib/axiosClient.ts`)

```typescript
import axios from 'axios';

export const axiosClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
});

// Response interceptor — unwrap errors consistently
axiosClient.interceptors.response.use(
  (res) => res,
  (err) => Promise.reject(err),
);
```

### 9.10 Repository layer (`src/repository/`)

One file per domain. Each file exports typed async functions using `axiosClient`.
All files re-exported from `src/repository/index.ts`.

Example — `src/repository/campaigns.ts`:
```typescript
import { AxiosResponse } from 'axios';
import { ApiAdCampaign, ApiMediaPlan } from '@shared/campaign';
import { axiosClient } from '@/lib/axiosClient';

export const fetchCampaigns = async (filters?: CampaignFilters): Promise<ApiAdCampaign[]> => {
  const { data }: AxiosResponse<ApiAdCampaign[]> = await axiosClient.get('/api/campaigns', {
    params: filters,
  });
  return data;
};

export const createAllCampaigns = async (plan: ApiMediaPlan): Promise<ApiAdCampaign[]> => {
  const { data }: AxiosResponse<ApiAdCampaign[]> = await axiosClient.post(
    '/api/campaigns/create-all',
    plan,
  );
  return data;
};
```

`src/repository/index.ts`:
```typescript
export * from './campaigns';
export * from './plans';
export * from './metrics';
```

### 9.11 TanStack Query hooks (`src/hooks/data/`)

One hook per domain. Each wraps a repository function with `useQuery` or `useMutation`.
All hooks re-exported from `src/hooks/data/index.ts`.

Example — `src/hooks/data/useCampaigns.ts`:
```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ApiAdCampaign, ApiMediaPlan } from '@shared/campaign';
import { fetchCampaigns, createAllCampaigns } from '@/repository';

export const useCampaigns = (filters?: CampaignFilters) => {
  const { isPending, error, data } = useQuery<ApiAdCampaign[], Error>({
    queryKey: ['campaigns', filters],
    queryFn: () => fetchCampaigns(filters),
  });
  return { data, error, isLoading: isPending };
};

export const useCreateAllCampaigns = () => {
  const queryClient = useQueryClient();
  return useMutation<ApiAdCampaign[], Error, ApiMediaPlan>({
    mutationFn: createAllCampaigns,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['campaigns'] }),
  });
};
```

`src/hooks/data/index.ts`:
```typescript
export * from './useCampaigns';
export * from './useGeneratePlan';
export * from './useMetrics';
export * from './useSuggestions';
```

Components import like:
```typescript
import { useCampaigns, useMetrics } from '@/hooks/data';
import { fetchCampaigns } from '@/repository';
```

### 9.12 TanStack Query provider setup (`src/main.tsx`)

```typescript
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 30_000, retry: 2 } },
});

ReactDOM.createRoot(document.getElementById('root')!).render(
  <QueryClientProvider client={queryClient}>
    <App />
  </QueryClientProvider>,
);
```

---

## Phase 10 — Frontend Components

### Dashboard (`components/Dashboard/index.tsx`)

- Loads campaigns + metrics on mount
- Polls metrics every 30s (or manual refresh button)
- Renders `<CampaignTable>` + `<Filters>` + `<SuggestionCard>` list
- "+ Create Campaigns" button opens modal

### CampaignTable (`components/Dashboard/CampaignTable.tsx`)

shadcn `<Table>` with columns:

| Platform | Campaign Name | Type | Spend | Impressions | Clicks | CTR | Conv. Value |
|---|---|---|---|---|---|---|---|

- Platform shown as colored badge (Google=blue, Meta=indigo, Amazon=orange)
- Status badge (Created / Pending / Failed) with color
- CTR formatted as percentage
- Spend formatted as currency

### Filters (`components/Dashboard/Filters.tsx`)

Two `<Select>` dropdowns: Platform filter, Campaign Type filter. State lifted to Dashboard.

### Create Campaign Modal (`components/CreateCampaign/Modal.tsx`)

Two-step modal:
1. **Step 1 — Input form** (`InputForm.tsx`):
   - Objective (Radio: Sales / Leads)
   - Daily Budget (numeric input)
   - Product Categories (tag input — comma-separated)
   - Country + Language (optional selects)
   - "Generate Plan" button → calls `/api/plans/generate`, shows loading state

2. **Step 2 — Plan Preview** (`PlanPreview.tsx`):
   - Shows generated `ApiMediaPlan` in readable format
   - Headlines, descriptions, keywords, budget per platform
   - "Create All" button → calls `/api/campaigns/create-all`
   - Per-platform status indicators update as responses arrive

### Optimization Panel (`components/Optimization/SuggestionCard.tsx`)

For each `ApiOptimizationSuggestion`:
- Issue badge + confidence score
- Reasoning text
- Recommended action
- "Approve" button (calls approve endpoint, updates UI)
- Approved suggestions show green checkmark

---

## Phase 11 — Environment & Config

### `.env.example`
```
# LLM
ANTHROPIC_API_KEY=sk-ant-...

# App
DATABASE_URL=./adpilot.db
FRONTEND_URL=http://localhost:5173
LOG_LEVEL=INFO

# Frontend (Vite)
VITE_API_URL=http://localhost:8000
```

### Frontend `.env`
```
VITE_API_URL=http://localhost:8000
```

---

## Phase 12 — README & Deliverables

### README sections
1. Setup instructions (single `make setup` command)
2. Running the app (`make dev`)
3. Environment variables table
4. Real vs mocked APIs (all three ad platforms fully mocked)
5. Planner/agent design (prompt structure, schema validation, guardrails, failure handling)
6. Optimization logic approach
7. Platform endpoints used (documented even though mocked)
8. Architecture diagram (ASCII in README + PNG export)

### Architecture diagram
```
Browser (React)
     │
     │ HTTP/JSON
     ▼
FastAPI (port 8000)
     │
     ├── /api/plans ──────► Planner Agent ──► Claude API
     │                           │
     │                           ├── RAG Retriever (platform_policies.md)
     │                           └── Memory (media_plans table)
     │
     ├── /api/campaigns ──► Mappers (google/meta/amazon)
     │                           │
     │                           └── Mock Platform Layer ──► SQLite (campaigns)
     │
     ├── /api/metrics ────► Reporting Aggregator
     │                           │
     │                           └── Mock Metrics ──► SQLite (campaign_metrics)
     │
     └── /api/metrics/suggestions ──► Optimizer Agent ──► SQLite (suggestions)

Shared Models (Python Pydantic → JSON Schema → TypeScript)
     └── shared/models/ ──► shared/schemas/ ──► shared/types/
```

---

## Implementation Order

| # | Phase | Output |
|---|---|---|
| 0 | Scaffolding | Folder structure, Makefile, root package.json |
| 1 | Shared models | Pydantic models, generate-types working |
| 2 | Backend setup | FastAPI running, DB initialized, config loading |
| 3 | RAG | platform_policies.md + retriever |
| 4 | Planner agent | `/api/plans/generate` working with Claude |
| 5 | Mappers | Pure mapper functions, unit-testable |
| 6 | Mock layer | Fake campaign creation + metric generation |
| 7 | API routes | All endpoints wired up |
| 8 | Optimizer | Suggestions endpoint working |
| 9 | Frontend scaffold | Vite + Tailwind + shadcn running |
| 10 | Dashboard | Campaign table with mock data |
| 11 | Create modal | Full flow: input → plan → create all |
| 12 | Suggestions UI | Optimization panel + approve |
| 13 | Polish | README, env docs, architecture diagram |

---

## Key Engineering Decisions

- **No circular imports:** `shared/models` has zero dependencies on backend code. Backend imports from shared.
- **Platform independence:** Each platform mapper + mock is isolated. Failure in one never affects others (`asyncio.gather(return_exceptions=True)`).
- **Retry logic:** `tenacity` with exponential backoff on LLM calls (429/5xx) and platform mock calls.
- **CTR guard:** `ctr = clicks / impressions if impressions > 0 else 0.0` enforced in both aggregator and Pydantic validator.
- **Memory:** Last plan stored in `media_plans`. On next generation, most recent entry is retrieved and passed as hint to planner prompt.
- **Secrets:** Only `.env` file, never hardcoded. `.env` gitignored.
- **Generated types:** `shared/types/` is gitignored. Always regenerated from Python source. CI can run `make generate-types` to verify sync.
