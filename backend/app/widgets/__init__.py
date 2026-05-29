"""Widget subsystem.

Importing this package triggers registration of every built-in widget
definition. To add a new widget plugin: create a module under `definitions/`
that registers a `WidgetDefinition`, then import it here.
"""
from app.widgets import registry as _registry_module
from app.widgets.definitions import core as _core  # noqa: F401
from app.widgets.definitions import crypto as _crypto  # noqa: F401
from app.widgets.definitions import social as _social  # noqa: F401
from app.widgets.registry import WidgetDefinition, registry

__all__ = ["registry", "WidgetDefinition"]
