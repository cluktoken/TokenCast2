"""Plugin-based widget registry.

Every widget type is described by a `WidgetDefinition`. Definitions register
themselves with the global `registry` at import time. The rest of the system
(validation, the catalog endpoint, the AI builder, the frontend) is driven by
this registry, so adding a new widget means adding one definition module and
importing it -- no changes to the core entities, schema, or endpoints.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, ValidationError


@dataclass(frozen=True)
class WidgetDefinition:
    """Static description of a widget type."""

    type: str
    name: str
    category: str
    description: str
    # Pydantic model used to validate/normalize a widget's `config` JSON.
    config_model: type[BaseModel]
    # Default grid footprint in grid cells.
    default_width: int = 2
    default_height: int = 2
    min_width: int = 1
    min_height: int = 1
    icon: str = "square"
    tags: list[str] = field(default_factory=list)

    def default_config(self) -> dict[str, Any]:
        return self.config_model().model_dump(mode="json")

    def validate_config(self, raw: dict[str, Any] | None) -> dict[str, Any]:
        """Validate raw config against this widget's schema, filling defaults."""
        try:
            model = self.config_model(**(raw or {}))
        except ValidationError as exc:  # re-raised as a clean ValueError upstream
            raise ValueError(f"Invalid config for widget '{self.type}': {exc}") from exc
        return model.model_dump(mode="json")

    def to_catalog_entry(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "icon": self.icon,
            "tags": self.tags,
            "default_width": self.default_width,
            "default_height": self.default_height,
            "min_width": self.min_width,
            "min_height": self.min_height,
            "default_config": self.default_config(),
            "config_schema": self.config_model.model_json_schema(),
        }


class WidgetRegistry:
    def __init__(self) -> None:
        self._defs: dict[str, WidgetDefinition] = {}

    def register(self, definition: WidgetDefinition) -> WidgetDefinition:
        if definition.type in self._defs:
            raise ValueError(f"Widget type already registered: {definition.type}")
        self._defs[definition.type] = definition
        return definition

    def get(self, widget_type: str) -> WidgetDefinition:
        try:
            return self._defs[widget_type]
        except KeyError:
            raise ValueError(f"Unknown widget type: {widget_type}") from None

    def has(self, widget_type: str) -> bool:
        return widget_type in self._defs

    def all(self) -> list[WidgetDefinition]:
        return list(self._defs.values())

    def catalog(self) -> list[dict[str, Any]]:
        return [d.to_catalog_entry() for d in self._defs.values()]


registry = WidgetRegistry()
