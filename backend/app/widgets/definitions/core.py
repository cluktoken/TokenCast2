"""Built-in 'core' widget definitions (clock, weather, media, html)."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.widgets.registry import WidgetDefinition, registry


class ClockConfig(BaseModel):
    timezone: str = "UTC"
    format: Literal["24h", "12h"] = "24h"
    show_seconds: bool = True
    show_date: bool = True
    label: str = ""


class WeatherConfig(BaseModel):
    location: str = "London"
    latitude: float | None = None
    longitude: float | None = None
    units: Literal["metric", "imperial"] = "metric"
    refresh_seconds: int = Field(default=900, ge=60)


class PhotoConfig(BaseModel):
    image_urls: list[str] = Field(default_factory=list)
    interval_seconds: int = Field(default=10, ge=2)
    fit: Literal["cover", "contain", "fill"] = "cover"
    transition: Literal["fade", "slide", "none"] = "fade"
    shuffle: bool = False


class VideoConfig(BaseModel):
    source_url: str = ""
    loop: bool = True
    muted: bool = True
    autoplay: bool = True
    fit: Literal["cover", "contain"] = "cover"


class CustomHtmlConfig(BaseModel):
    html: str = "<div style='display:grid;place-items:center;height:100%'>Custom HTML</div>"
    # When true the HTML is rendered inside a sandboxed iframe on the player.
    sandboxed: bool = True


registry.register(WidgetDefinition(
    type="clock", name="Clock", category="core", icon="clock",
    description="Configurable digital clock with date and timezone support.",
    config_model=ClockConfig, default_width=3, default_height=2, tags=["time"],
))
registry.register(WidgetDefinition(
    type="weather", name="Weather", category="core", icon="cloud-sun",
    description="Current conditions and forecast for any location.",
    config_model=WeatherConfig, default_width=3, default_height=3, tags=["weather"],
))
registry.register(WidgetDefinition(
    type="photo", name="Photo Slideshow", category="media", icon="image",
    description="Auto-advancing photo slideshow.",
    config_model=PhotoConfig, default_width=4, default_height=4, tags=["media", "photos"],
))
registry.register(WidgetDefinition(
    type="video", name="Video", category="media", icon="video",
    description="Looping video playback from any URL or HLS stream.",
    config_model=VideoConfig, default_width=4, default_height=4, tags=["media", "video"],
))
registry.register(WidgetDefinition(
    type="custom_html", name="Custom HTML", category="advanced", icon="code",
    description="Render arbitrary sandboxed HTML.",
    config_model=CustomHtmlConfig, default_width=4, default_height=3, tags=["advanced"],
))
