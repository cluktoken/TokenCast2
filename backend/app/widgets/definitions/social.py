"""NFT and social-feed widget definitions."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.widgets.registry import WidgetDefinition, registry


class NftGalleryConfig(BaseModel):
    chain: Literal["ethereum", "solana", "polygon", "base"] = "ethereum"
    wallet_address: str = ""
    # Optionally pin specific token ids; empty means the whole wallet.
    contracts: list[str] = Field(default_factory=list)
    mode: Literal["grid", "slideshow", "fullscreen"] = "slideshow"
    interval_seconds: int = Field(default=12, ge=3)
    show_metadata: bool = True
    play_video_nfts: bool = True
    refresh_seconds: int = Field(default=900, ge=60)


class TelegramFeedConfig(BaseModel):
    feed_type: Literal["channel", "group"] = "channel"
    handle: str = ""  # e.g. @tokencast
    limit: int = Field(default=15, ge=1, le=100)
    refresh_seconds: int = Field(default=120, ge=30)


class DiscordFeedConfig(BaseModel):
    feed_type: Literal["announcements", "messages"] = "announcements"
    channel_id: str = ""
    limit: int = Field(default=15, ge=1, le=100)
    refresh_seconds: int = Field(default=120, ge=30)


registry.register(WidgetDefinition(
    type="nft_gallery", name="NFT Gallery", category="nft", icon="frame",
    description="Display NFTs from a wallet across ETH, SOL, Polygon and Base.",
    config_model=NftGalleryConfig, default_width=6, default_height=5,
    tags=["nft", "media"],
))
registry.register(WidgetDefinition(
    type="telegram_feed", name="Telegram Feed", category="social", icon="send",
    description="Live channel or group feed from Telegram.",
    config_model=TelegramFeedConfig, default_width=3, default_height=5, tags=["social"],
))
registry.register(WidgetDefinition(
    type="discord_feed", name="Discord Feed", category="social", icon="message-circle",
    description="Announcements or messages from a Discord channel.",
    config_model=DiscordFeedConfig, default_width=3, default_height=5, tags=["social"],
))
