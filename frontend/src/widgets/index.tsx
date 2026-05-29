"use client";

import { useEffect, useRef, useState } from "react";
import type { Widget } from "@/lib/types";

type Cfg = Record<string, any>;

// --- Clock ---
function ClockWidget({ config }: { config: Cfg }) {
  const [now, setNow] = useState(() => new Date());
  useEffect(() => {
    const t = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(t);
  }, []);
  const opts: Intl.DateTimeFormatOptions = {
    hour: "2-digit",
    minute: "2-digit",
    hour12: config.format === "12h",
  };
  if (config.show_seconds) opts.second = "2-digit";
  if (config.timezone) opts.timeZone = config.timezone;
  const time = now.toLocaleTimeString([], opts);
  return (
    <div className="flex h-full w-full flex-col items-center justify-center">
      {config.label ? <div className="mb-1 text-sm opacity-70">{config.label}</div> : null}
      <div className="font-mono text-4xl font-bold tabular-nums md:text-5xl">{time}</div>
      {config.show_date ? (
        <div className="mt-2 text-sm opacity-70">
          {now.toLocaleDateString([], { weekday: "long", month: "long", day: "numeric" })}
        </div>
      ) : null}
    </div>
  );
}

// --- Weather (open-meteo, no API key) ---
function WeatherWidget({ config }: { config: Cfg }) {
  const [data, setData] = useState<any>(null);
  const [err, setErr] = useState(false);
  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        let lat = config.latitude, lon = config.longitude;
        if (lat == null || lon == null) {
          const geo = await fetch(
            `https://geocoding-api.open-meteo.com/v1/search?count=1&name=${encodeURIComponent(config.location || "London")}`,
          ).then((r) => r.json());
          lat = geo?.results?.[0]?.latitude;
          lon = geo?.results?.[0]?.longitude;
        }
        const unit = config.units === "imperial" ? "fahrenheit" : "celsius";
        const w = await fetch(
          `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current=temperature_2m,weather_code&temperature_unit=${unit}`,
        ).then((r) => r.json());
        if (!cancelled) setData(w.current);
      } catch {
        if (!cancelled) setErr(true);
      }
    }
    load();
    const t = setInterval(load, (config.refresh_seconds || 900) * 1000);
    return () => { cancelled = true; clearInterval(t); };
  }, [config.location, config.units, config.latitude, config.longitude, config.refresh_seconds]);

  if (err) return <Centered>Weather unavailable</Centered>;
  if (!data) return <Centered>Loading weather…</Centered>;
  const symbol = config.units === "imperial" ? "°F" : "°C";
  return (
    <div className="flex h-full w-full flex-col items-center justify-center">
      <div className="text-sm opacity-70">{config.location}</div>
      <div className="text-5xl font-bold">{Math.round(data.temperature_2m)}{symbol}</div>
    </div>
  );
}

// --- Crypto price (CoinGecko) ---
function CryptoPriceWidget({ config }: { config: Cfg }) {
  const [prices, setPrices] = useState<any>(null);
  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const ids = (config.symbols || []).join(",");
        const vs = config.vs_currency || "usd";
        const r = await fetch(
          `https://api.coingecko.com/api/v3/simple/price?ids=${ids}&vs_currencies=${vs}&include_24hr_change=true`,
        ).then((x) => x.json());
        if (!cancelled) setPrices(r);
      } catch { /* keep last */ }
    }
    load();
    const t = setInterval(load, (config.refresh_seconds || 60) * 1000);
    return () => { cancelled = true; clearInterval(t); };
  }, [JSON.stringify(config.symbols), config.vs_currency, config.refresh_seconds]);

  const vs = (config.vs_currency || "usd").toUpperCase();
  return (
    <div className="flex h-full w-full flex-col justify-center gap-2 p-3">
      {(config.symbols || []).map((s: string) => {
        const row = prices?.[s];
        const change = row?.[`${(config.vs_currency || "usd")}_24h_change`];
        return (
          <div key={s} className="flex items-center justify-between">
            <span className="font-semibold capitalize">{s}</span>
            <span className="text-right">
              <span className="font-mono">
                {row ? `${row[config.vs_currency || "usd"]?.toLocaleString()} ${vs}` : "—"}
              </span>
              {config.show_change && change != null ? (
                <span className={change >= 0 ? "ml-2 text-green-400" : "ml-2 text-red-400"}>
                  {change >= 0 ? "▲" : "▼"} {Math.abs(change).toFixed(2)}%
                </span>
              ) : null}
            </span>
          </div>
        );
      })}
    </div>
  );
}

// --- TradingView embed ---
function TradingViewWidget({ config, id }: { config: Cfg; id: number }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!ref.current) return;
    ref.current.innerHTML = "";
    const script = document.createElement("script");
    script.src = "https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js";
    script.async = true;
    script.innerHTML = JSON.stringify({
      symbol: config.symbol || "BINANCE:BTCUSDT",
      interval: config.interval || "60",
      theme: config.theme || "dark",
      style: config.style === "line" ? "2" : config.style === "area" ? "3" : "1",
      autosize: true,
    });
    ref.current.appendChild(script);
  }, [config.symbol, config.interval, config.theme, config.style, id]);
  return <div ref={ref} className="h-full w-full" />;
}

// --- Photo slideshow ---
function PhotoWidget({ config }: { config: Cfg }) {
  const urls: string[] = config.image_urls || [];
  const [i, setI] = useState(0);
  useEffect(() => {
    if (urls.length < 2) return;
    const t = setInterval(
      () => setI((p) => (p + 1) % urls.length),
      (config.interval_seconds || 10) * 1000,
    );
    return () => clearInterval(t);
  }, [urls.length, config.interval_seconds]);
  if (!urls.length) return <Centered>No photos configured</Centered>;
  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={urls[i]}
      alt=""
      className="h-full w-full"
      style={{ objectFit: config.fit || "cover" }}
    />
  );
}

// --- Video ---
function VideoWidget({ config }: { config: Cfg }) {
  if (!config.source_url) return <Centered>No video configured</Centered>;
  return (
    <video
      className="h-full w-full"
      style={{ objectFit: config.fit || "cover" }}
      src={config.source_url}
      autoPlay={config.autoplay ?? true}
      loop={config.loop ?? true}
      muted={config.muted ?? true}
      playsInline
    />
  );
}

// --- Custom HTML (sandboxed) ---
function CustomHtmlWidget({ config }: { config: Cfg }) {
  if (config.sandboxed) {
    return (
      <iframe
        title="custom-html"
        className="h-full w-full border-0"
        sandbox="allow-scripts"
        srcDoc={config.html || ""}
      />
    );
  }
  return <div className="h-full w-full" dangerouslySetInnerHTML={{ __html: config.html || "" }} />;
}

// --- Generic feed placeholder shell for data-source widgets ---
function FeedShell({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <div className="flex h-full w-full flex-col p-3">
      <div className="mb-2 text-sm font-semibold">{title}</div>
      <div className="flex flex-1 items-center justify-center text-center text-xs opacity-60">
        {subtitle}
      </div>
    </div>
  );
}

function Centered({ children }: { children: React.ReactNode }) {
  return <div className="flex h-full w-full items-center justify-center text-sm opacity-60">{children}</div>;
}

// --- Registry ---
type RendererProps = { config: Cfg; id: number };
const RENDERERS: Record<string, (p: RendererProps) => React.ReactNode> = {
  clock: ({ config }) => <ClockWidget config={config} />,
  weather: ({ config }) => <WeatherWidget config={config} />,
  crypto_price: ({ config }) => <CryptoPriceWidget config={config} />,
  tradingview: ({ config, id }) => <TradingViewWidget config={config} id={id} />,
  photo: ({ config }) => <PhotoWidget config={config} />,
  video: ({ config }) => <VideoWidget config={config} />,
  custom_html: ({ config }) => <CustomHtmlWidget config={config} />,
  watchlist: ({ config }) => <CryptoPriceWidget config={config} />,
  nft_gallery: ({ config }) => (
    <FeedShell title="NFT Gallery" subtitle={`Wallet: ${config.wallet_address || "not set"} · ${config.chain}`} />
  ),
  wallet_tracker: ({ config }) => (
    <FeedShell title="Wallet Tracker" subtitle={`${config.chain}: ${config.address || "not set"}`} />
  ),
  neural_trend: ({ config }) => (
    <FeedShell title="Neural Trend" subtitle={`Top ${config.limit} by ${config.metric}`} />
  ),
  telegram_feed: ({ config }) => (
    <FeedShell title="Telegram" subtitle={`${config.feed_type}: ${config.handle || "not set"}`} />
  ),
  discord_feed: ({ config }) => (
    <FeedShell title="Discord" subtitle={`${config.feed_type}: ${config.channel_id || "not set"}`} />
  ),
};

export function WidgetRenderer({ widget }: { widget: Widget }) {
  const render = RENDERERS[widget.widget_type];
  if (!render) {
    return <Centered>Unknown widget: {widget.widget_type}</Centered>;
  }
  return <>{render({ config: widget.config, id: widget.id })}</>;
}

export const KNOWN_WIDGET_TYPES = Object.keys(RENDERERS);
