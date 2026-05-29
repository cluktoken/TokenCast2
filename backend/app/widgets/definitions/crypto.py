"""Crypto and market widget definitions."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.widgets.registry import WidgetDefinition, registry


class CryptoPriceConfig(BaseModel):
    # CoinGecko-style ids. CLUK + arbitrary custom tokens supported via `custom`.
    symbols: list[str] = Field(default_factory=lambda: ["bitcoin", "ethereum", "solana"])
    vs_currency: str = "usd"
    show_change: bool = True
    refresh_seconds: int = Field(default=60, ge=15)
    # Custom token definitions: {"symbol": "CLUK", "contract": "0x..", "chain": "base"}
    custom_tokens: list[dict] = Field(default_factory=list)


class TradingViewConfig(BaseModel):
    symbol: str = "BINANCE:BTCUSDT"
    interval: Literal["1", "5", "15", "60", "240", "D", "W"] = "60"
    theme: Literal["dark", "light"] = "dark"
    style: Literal["candles", "line", "area"] = "candles"


class WatchlistConfig(BaseModel):
    symbols: list[str] = Field(default_factory=lambda: ["bitcoin", "ethereum", "solana"])
    vs_currency: str = "usd"
    refresh_seconds: int = Field(default=60, ge=15)
    columns: list[str] = Field(default_factory=lambda: ["price", "change_24h", "market_cap"])


class WalletTrackerConfig(BaseModel):
    chain: Literal["ethereum", "solana", "polygon", "base"] = "ethereum"
    address: str = ""
    refresh_seconds: int = Field(default=120, ge=30)
    show_tokens: bool = True
    show_total_value: bool = True


class NeuralTrendConfig(BaseModel):
    # Architecture for custom API integrations: point at any compatible source.
    source_url: str = ""
    limit: int = Field(default=10, ge=1, le=100)
    metric: Literal["momentum", "vote_velocity", "rank"] = "momentum"
    refresh_seconds: int = Field(default=120, ge=30)


registry.register(WidgetDefinition(
    type="crypto_price", name="Crypto Price", category="crypto", icon="bitcoin",
    description="Live prices for BTC, ETH, SOL, CLUK and custom tokens.",
    config_model=CryptoPriceConfig, default_width=3, default_height=2, tags=["crypto"],
))
registry.register(WidgetDefinition(
    type="tradingview", name="TradingView Chart", category="crypto", icon="line-chart",
    description="Embedded TradingView advanced chart.",
    config_model=TradingViewConfig, default_width=6, default_height=4, tags=["crypto", "chart"],
))
registry.register(WidgetDefinition(
    type="watchlist", name="Watchlist", category="crypto", icon="list",
    description="Multi-token watchlist table.",
    config_model=WatchlistConfig, default_width=4, default_height=4, tags=["crypto"],
))
registry.register(WidgetDefinition(
    type="wallet_tracker", name="Wallet Tracker", category="crypto", icon="wallet",
    description="Track balances and token holdings of any wallet.",
    config_model=WalletTrackerConfig, default_width=4, default_height=4, tags=["crypto", "wallet"],
))
registry.register(WidgetDefinition(
    type="neural_trend", name="Neural Trend", category="crypto", icon="trending-up",
    description="Trending tokens with momentum, rankings and vote velocity.",
    config_model=NeuralTrendConfig, default_width=4, default_height=5, tags=["crypto", "trends"],
))
