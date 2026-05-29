"""Idempotent seeding of built-in system templates.

Run at startup. Creates a handful of ready-to-use layout templates (crypto
command center, NFT wall, family dashboard, business dashboard) if they don't
already exist. Templates are stored as serialized definitions so instantiating
one produces a real Layout owned by the user.
"""
from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.template import Template
from app.services.ai_builder import AIBuilderService

logger = logging.getLogger("tokencast.seed")

_SYSTEM_TEMPLATES = [
    {
        "name": "Crypto Command Center",
        "category": "crypto",
        "description": "Live prices, a TradingView chart, watchlist and trending tokens.",
        "prompt": "crypto trading command center with chart watchlist and trending tokens",
        "theme": "cyberpunk",
    },
    {
        "name": "NFT Wall",
        "category": "nft",
        "description": "Fullscreen NFT gallery slideshow with a clock.",
        "prompt": "nft gallery wall slideshow with clock",
        "theme": "dark",
    },
    {
        "name": "Family Dashboard",
        "category": "home",
        "description": "Clock, weather and a family photo slideshow.",
        "prompt": "family dashboard with clock weather and photo slideshow",
        "theme": "light",
    },
    {
        "name": "Business Dashboard",
        "category": "business",
        "description": "Clock, weather and announcement feeds for the office.",
        "prompt": "business dashboard with clock weather and discord announcements",
        "theme": "corporate",
    },
]


def seed_system_templates(db: Session) -> None:
    builder = AIBuilderService()
    for spec in _SYSTEM_TEMPLATES:
        exists = db.scalar(
            select(Template).where(
                Template.name == spec["name"], Template.is_system.is_(True)
            )
        )
        if exists:
            continue
        plan = builder.build(spec["prompt"], theme=spec["theme"])
        template = Template(
            user_id=None,
            name=spec["name"],
            description=spec["description"],
            category=spec["category"],
            is_system=True,
            definition={
                "theme": plan["theme"],
                "grid_config": plan["grid_config"],
                "widgets": plan["widgets"],
            },
        )
        db.add(template)
        logger.info("Seeded system template: %s", spec["name"])
    db.commit()
