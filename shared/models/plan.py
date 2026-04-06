from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, field_validator


class ApiCreativePack(BaseModel):
    headlines: list[str]  # max 15, each max 30 chars (Google)
    descriptions: list[str]  # max 4, each max 90 chars
    long_headlines: list[str]  # max 5, each max 90 chars
    primary_texts: list[str]  # Meta: max 5, each max 125 chars
    callouts: list[str]
    image_urls: list[str]
    logo_url: str

    @field_validator("headlines")
    @classmethod
    def validate_headlines(cls, v: list[str]) -> list[str]:
        if len(v) > 15:
            raise ValueError("headlines: max 15 items")
        for h in v:
            if len(h) > 30:
                raise ValueError(f"headline too long (max 30 chars): {h!r}")
        return v

    @field_validator("descriptions")
    @classmethod
    def validate_descriptions(cls, v: list[str]) -> list[str]:
        if len(v) > 4:
            raise ValueError("descriptions: max 4 items")
        for d in v:
            if len(d) > 90:
                raise ValueError(f"description too long (max 90 chars): {d!r}")
        return v

    @field_validator("long_headlines")
    @classmethod
    def validate_long_headlines(cls, v: list[str]) -> list[str]:
        if len(v) > 5:
            raise ValueError("long_headlines: max 5 items")
        for h in v:
            if len(h) > 90:
                raise ValueError(f"long_headline too long (max 90 chars): {h!r}")
        return v

    @field_validator("primary_texts")
    @classmethod
    def validate_primary_texts(cls, v: list[str]) -> list[str]:
        if len(v) > 5:
            raise ValueError("primary_texts: max 5 items")
        for t in v:
            if len(t) > 125:
                raise ValueError(f"primary_text too long (max 125 chars): {t!r}")
        return v


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

    @field_validator("daily_budget")
    @classmethod
    def validate_budget(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("daily_budget must be > 0")
        return v

    @field_validator("product_categories")
    @classmethod
    def validate_categories(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("product_categories must not be empty")
        return v
