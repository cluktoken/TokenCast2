"""AI Layout Builder.

Turns a natural-language prompt ("Build me a crypto trading command center")
into a concrete layout: a theme, a grid, and positioned widgets.

Two backends:
  * LLM backend (default when AI_API_KEY is set): calls any OpenAI-compatible
    /chat/completions endpoint and asks for a strict JSON layout.
  * Built-in backend (always available, zero-config): a deterministic
    keyword-driven planner that composes widgets from the registry and packs
    them into the grid. This guarantees the feature works out of the box.

Both backends return data validated against the widget registry, so the API
never persists an invalid layout regardless of what the model returns.
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any

import httpx

from app.core.config import settings
from app.widgets import registry

logger = logging.getLogger("tokencast.ai")

# Maps prompt keywords to widget types that should appear in the layout.
_KEYWORD_WIDGETS: list[tuple[tuple[str, ...], str]] = [
    (("crypto", "trading", "price", "market", "command center"), "crypto_price"),
    (("chart", "tradingview", "candles", "trading"), "tradingview"),
    (("watchlist", "portfolio", "tokens"), "watchlist"),
    (("wallet", "holdings", "balance"), "wallet_tracker"),
    (("trend", "trending", "momentum", "neural"), "neural_trend"),
    (("nft", "gallery", "art", "collection"), "nft_gallery"),
    (("telegram",), "telegram_feed"),
    (("discord",), "discord_feed"),
    (("weather", "forecast"), "weather"),
    (("clock", "time"), "clock"),
    (("photo", "family", "pictures", "slideshow"), "photo"),
    (("video", "stream"), "video"),
]

_THEME_KEYWORDS: list[tuple[tuple[str, ...], str]] = [
    (("cyberpunk", "command center", "trading"), "cyberpunk"),
    (("neon",), "neon"),
    (("corporate", "business", "office"), "corporate"),
    (("light", "bright", "minimal"), "light"),
]

_GRID_COLUMNS = 12
_GRID_ROWS = 8


class AIBuilderService:
    def build(self, prompt: str, theme: str | None = None) -> dict[str, Any]:
        if settings.AI_API_KEY:
            try:
                result = self._build_with_llm(prompt, theme)
                result["source"] = "llm"
                return self._validate(result)
            except Exception as exc:  # fall back rather than fail the request
                logger.warning("AI builder LLM call failed (%s); using built-in", exc)
        result = self._build_builtin(prompt, theme)
        result["source"] = "builtin"
        return self._validate(result)

    # ------------------------------------------------------------------ LLM
    def _build_with_llm(self, prompt: str, theme: str | None) -> dict[str, Any]:
        catalog = [
            {"type": d.type, "name": d.name, "category": d.category}
            for d in registry.all()
        ]
        system = (
            "You are a dashboard layout generator for a digital-signage platform. "
            "Return ONLY valid JSON, no prose, no markdown fences. Schema: "
            '{"name": str, "theme": one of [dark,light,cyberpunk,neon,corporate], '
            '"grid_config": {"columns": 12, "rows": 8, "gap": 8}, '
            '"widgets": [{"widget_type": str, "config": object, '
            '"position_x": int, "position_y": int, "width": int, "height": int}]}. '
            f"Use a 12x8 grid. Only use these widget_type values: "
            f"{json.dumps([c['type'] for c in catalog])}."
        )
        user = f"Build this display: {prompt}." + (f" Use the {theme} theme." if theme else "")
        resp = httpx.post(
            f"{settings.AI_API_BASE}/chat/completions",
            headers={"Authorization": f"Bearer {settings.AI_API_KEY}"},
            json={
                "model": settings.AI_MODEL,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": 0.4,
                "response_format": {"type": "json_object"},
            },
            timeout=45.0,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        content = re.sub(r"^```(?:json)?|```$", "", content.strip()).strip()
        return json.loads(content)

    # -------------------------------------------------------------- built-in
    def _build_builtin(self, prompt: str, theme: str | None) -> dict[str, Any]:
        lower = prompt.lower()

        chosen: list[str] = []
        for keywords, wtype in _KEYWORD_WIDGETS:
            if any(k in lower for k in keywords) and wtype not in chosen:
                chosen.append(wtype)
        if not chosen:
            chosen = ["clock", "weather", "crypto_price"]
        # Always anchor with a clock for context unless the prompt is media-only.
        if "clock" not in chosen and not {"photo", "video", "nft_gallery"} & set(chosen):
            chosen.insert(0, "clock")

        resolved_theme = theme
        if not resolved_theme:
            resolved_theme = "dark"
            for keywords, t in _THEME_KEYWORDS:
                if any(k in lower for k in keywords):
                    resolved_theme = t
                    break

        widgets = self._pack(chosen)
        name = self._title_from_prompt(prompt)
        return {
            "name": name,
            "theme": resolved_theme,
            "grid_config": {"columns": _GRID_COLUMNS, "rows": _GRID_ROWS, "gap": 8},
            "widgets": widgets,
        }

    def _pack(self, widget_types: list[str]) -> list[dict[str, Any]]:
        """Greedy left-to-right, top-to-bottom bin packing into the grid."""
        widgets: list[dict[str, Any]] = []
        cursor_x = 0
        cursor_y = 0
        row_height = 0
        for wtype in widget_types:
            definition = registry.get(wtype)
            w = min(definition.default_width, _GRID_COLUMNS)
            h = definition.default_height
            if cursor_x + w > _GRID_COLUMNS:
                cursor_x = 0
                cursor_y += row_height
                row_height = 0
            widgets.append({
                "widget_type": wtype,
                "config": definition.default_config(),
                "position_x": cursor_x,
                "position_y": cursor_y,
                "width": w,
                "height": h,
            })
            cursor_x += w
            row_height = max(row_height, h)
        return widgets

    @staticmethod
    def _title_from_prompt(prompt: str) -> str:
        cleaned = re.sub(r"^(build|make|create|generate)( me)?( a| an)?\s+", "", prompt.strip(), flags=re.I)
        cleaned = cleaned.strip(" .!").strip()
        if not cleaned:
            return "Generated Layout"
        return cleaned[:60].title()

    # -------------------------------------------------------------- validate
    def _validate(self, result: dict[str, Any]) -> dict[str, Any]:
        valid_widgets: list[dict[str, Any]] = []
        for w in result.get("widgets", []):
            wtype = w.get("widget_type")
            if not wtype or not registry.has(wtype):
                continue
            definition = registry.get(wtype)
            valid_widgets.append({
                "widget_type": wtype,
                "config": definition.validate_config(w.get("config")),
                "position_x": max(int(w.get("position_x", 0)), 0),
                "position_y": max(int(w.get("position_y", 0)), 0),
                "width": max(int(w.get("width", definition.default_width)), definition.min_width),
                "height": max(int(w.get("height", definition.default_height)), definition.min_height),
            })
        result["widgets"] = valid_widgets
        result.setdefault("name", "Generated Layout")
        result.setdefault("theme", "dark")
        result.setdefault("grid_config", {"columns": _GRID_COLUMNS, "rows": _GRID_ROWS, "gap": 8})
        return result
