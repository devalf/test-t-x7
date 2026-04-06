from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.campaigns import router as campaigns_router
from app.api.metrics import router as metrics_router
from app.api.plans import router as plans_router
from app.config import settings
from app.database import init_db

logging.basicConfig(level=settings.log_level.upper())
logger = logging.getLogger(__name__)

app = FastAPI(title="AdPilot API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(plans_router, prefix="/api/plans", tags=["plans"])
app.include_router(campaigns_router, prefix="/api/campaigns", tags=["campaigns"])
app.include_router(metrics_router, prefix="/api/metrics", tags=["metrics"])


@app.on_event("startup")
async def startup() -> None:
    await init_db()
    logger.info("AdPilot API started")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
