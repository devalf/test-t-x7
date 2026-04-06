"""
Keyword-based RAG retriever for platform advertising policies.

Reads platform_policies.md and extracts sections relevant to the requested
platforms. The extracted text is injected into the planner prompt as constraints.

No embeddings needed — the policies file is small and platform names are
well-defined tokens. Section headers use platform slugs (google, meta, amazon)
as anchors.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

_POLICIES_PATH = Path(__file__).parent / "platform_policies.md"

# Supported platform slugs — must match section headers in platform_policies.md
SUPPORTED_PLATFORMS = {"google", "meta", "amazon"}


def _load_policies() -> str:
    return _POLICIES_PATH.read_text(encoding="utf-8")


def _parse_sections(text: str) -> dict[str, str]:
    """
    Split the markdown into a dict keyed by platform slug.
    Sections are delimited by `## <slug>` headers.
    """
    sections: dict[str, str] = {}
    # Match top-level ## headers that are platform slugs
    pattern = re.compile(r"^## (\w+)", re.MULTILINE)
    matches = list(pattern.finditer(text))

    for i, match in enumerate(matches):
        slug = match.group(1).lower()
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections[slug] = text[start:end].strip()

    return sections


def retrieve_constraints(platforms: list[str]) -> str:
    """
    Return the policy sections for the requested platforms as a single string,
    ready to be injected into a prompt.

    Args:
        platforms: list of platform slugs, e.g. ["google", "meta", "amazon"]

    Returns:
        Concatenated policy text for the requested platforms.
        Falls back to all platforms if none match or list is empty.
    """
    try:
        text = _load_policies()
        sections = _parse_sections(text)
    except Exception:
        logger.exception("Failed to load platform policies")
        return ""

    requested = {p.lower() for p in platforms} & SUPPORTED_PLATFORMS
    if not requested:
        requested = SUPPORTED_PLATFORMS

    retrieved = [sections[slug] for slug in sorted(requested) if slug in sections]

    if not retrieved:
        logger.warning("No policy sections found for platforms: %s", platforms)
        return ""

    header = "=== Platform Advertising Constraints ===\n"
    return header + "\n\n".join(retrieved)
