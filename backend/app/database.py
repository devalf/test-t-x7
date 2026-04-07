from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import aiosqlite

from app.config import settings

logger = logging.getLogger(__name__)

CREATE_CAMPAIGNS = """
CREATE TABLE IF NOT EXISTS campaigns (
    id TEXT PRIMARY KEY,
    platform TEXT NOT NULL,
    campaign_name TEXT NOT NULL,
    campaign_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    external_id TEXT,
    plan_json TEXT,
    created_at TEXT NOT NULL
)
"""

CREATE_CAMPAIGN_METRICS = """
CREATE TABLE IF NOT EXISTS campaign_metrics (
    id TEXT PRIMARY KEY,
    campaign_id TEXT NOT NULL,
    date TEXT NOT NULL,
    spend REAL NOT NULL DEFAULT 0.0,
    impressions INTEGER NOT NULL DEFAULT 0,
    clicks INTEGER NOT NULL DEFAULT 0,
    ctr REAL NOT NULL DEFAULT 0.0,
    conversions INTEGER NOT NULL DEFAULT 0,
    conversion_value REAL NOT NULL DEFAULT 0.0,
    currency TEXT NOT NULL DEFAULT 'USD',
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
)
"""

CREATE_MEDIA_PLANS = """
CREATE TABLE IF NOT EXISTS media_plans (
    id TEXT PRIMARY KEY,
    plan_json TEXT NOT NULL,
    created_at TEXT NOT NULL
)
"""

CREATE_OPTIMIZATION_SUGGESTIONS = """
CREATE TABLE IF NOT EXISTS optimization_suggestions (
    id TEXT PRIMARY KEY,
    campaign_id TEXT NOT NULL,
    issue_detected TEXT NOT NULL,
    recommended_action TEXT NOT NULL,
    reasoning TEXT NOT NULL,
    confidence REAL NOT NULL DEFAULT 0.0,
    approved INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
)
"""


async def init_db() -> None:
    async with aiosqlite.connect(settings.database_url) as db:
        await db.execute(CREATE_CAMPAIGNS)
        await db.execute(CREATE_CAMPAIGN_METRICS)
        await db.execute(CREATE_MEDIA_PLANS)
        await db.execute(CREATE_OPTIMIZATION_SUGGESTIONS)
        await db.commit()
    logger.info("Database initialized: %s", settings.database_url)


@asynccontextmanager
async def get_db() -> AsyncIterator[aiosqlite.Connection]:
    async with aiosqlite.connect(settings.database_url) as db:
        db.row_factory = aiosqlite.Row
        yield db
