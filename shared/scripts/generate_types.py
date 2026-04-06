"""
Generate JSON schemas from Pydantic models, to be consumed by json-schema-to-typescript.

Run via: make generate-types
  → python shared/scripts/generate_types.py   (exports JSON schemas)
  → yarn ts-gen                                (converts schemas to TypeScript)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Allow running from project root or from within shared/scripts/
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from pydantic import TypeAdapter  # noqa: E402

from shared.models.campaign import ApiAdCampaign, ApiCampaignStatus, ApiCreateCampaignRequest  # noqa: E402
from shared.models.metrics import ApiCampaignMetrics, ApiOptimizationSuggestion  # noqa: E402
from shared.models.plan import ApiCreativePack, ApiMediaPlan, ApiTargetingHints  # noqa: E402

SCHEMAS_DIR = ROOT / "shared" / "schemas"
SCHEMAS_DIR.mkdir(exist_ok=True)

# Each entry: (output filename, list of models to include in that schema file)
SCHEMA_GROUPS: list[tuple[str, list[type]]] = [
    (
        "plan.json",
        [ApiCreativePack, ApiTargetingHints, ApiMediaPlan],
    ),
    (
        "campaign.json",
        [ApiCampaignStatus, ApiAdCampaign, ApiCreateCampaignRequest],
    ),
    (
        "metrics.json",
        [ApiCampaignMetrics, ApiOptimizationSuggestion],
    ),
]


def build_schema(models: list[type]) -> dict:
    """
    Build a single JSON schema with $defs containing all provided models.
    json-schema-to-typescript will generate one interface per $def entry.
    """
    defs: dict = {}
    for model in models:
        # BaseModel subclasses have model_json_schema(); enums/others use TypeAdapter
        if hasattr(model, "model_json_schema"):
            schema = model.model_json_schema()
        else:
            schema = TypeAdapter(model).json_schema()

        # Hoist nested $defs up to the top level
        nested = schema.pop("$defs", {})
        defs.update(nested)
        # Use the model title (class name) as the key
        title = schema.get("title", model.__name__)
        defs[title] = schema

    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$defs": defs,
    }


def main() -> None:
    for filename, models in SCHEMA_GROUPS:
        schema = build_schema(models)
        out_path = SCHEMAS_DIR / filename
        out_path.write_text(json.dumps(schema, indent=2))
        print(f"  wrote {out_path.relative_to(ROOT)}")

    print("Schema generation complete.")


if __name__ == "__main__":
    main()
