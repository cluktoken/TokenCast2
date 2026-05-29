"use client";

import { useEffect, useRef, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import { WS_URL } from "@/lib/utils";
import { WidgetRenderer } from "@/widgets";
import type { DisplayPlayerView } from "@/lib/types";

export default function PlayerPage() {
  const params = useParams<{ displayId: string }>();
  const displayId = Number(params.displayId);
  const [view, setView] = useState<DisplayPlayerView | null>(null);
  const [error, setError] = useState("");
  const wsRef = useRef<WebSocket | null>(null);

  async function load() {
    try {
      setView(await api.playerView(displayId));
    } catch (e: any) {
      setError(e.message || "Failed to load display");
    }
  }

  // Initial load + heartbeat loop
  useEffect(() => {
    void load();
    const beat = () => api.heartbeat(displayId).catch(() => {});
    void beat();
    const t = setInterval(beat, 30_000);
    return () => clearInterval(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [displayId]);

  // Realtime: reload when the layout is reassigned or edited
  useEffect(() => {
    const ws = new WebSocket(`${WS_URL}/ws/displays/${displayId}`);
    wsRef.current = ws;
    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data);
        if (["layout_assigned", "layout_updated"].includes(msg.event)) void load();
      } catch { /* ignore */ }
    };
    return () => ws.close();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [displayId]);

  if (error) {
    return <div className="flex h-screen items-center justify-center text-red-400">{error}</div>;
  }
  if (!view) {
    return <div className="flex h-screen items-center justify-center">Loading display…</div>;
  }
  if (!view.layout) {
    return (
      <div className="flex h-screen flex-col items-center justify-center gap-2">
        <div className="text-xl font-semibold">{view.display.name}</div>
        <div className="opacity-60">No layout assigned</div>
      </div>
    );
  }

  const grid = view.layout.grid_config;
  return (
    <div
      data-theme={view.layout.theme}
      className="relative h-screen w-screen overflow-hidden"
      style={{ background: "var(--tc-bg)", color: "var(--tc-text)" }}
    >
      {view.layout.widgets.map((w) => (
        <div
          key={w.id}
          className="absolute overflow-hidden"
          style={{
            left: `${(w.position_x / grid.columns) * 100}%`,
            top: `${(w.position_y / grid.rows) * 100}%`,
            width: `${(w.width / grid.columns) * 100}%`,
            height: `${(w.height / grid.rows) * 100}%`,
            padding: grid.gap / 2,
          }}
        >
          <div
            className="h-full w-full overflow-hidden rounded-lg"
            style={{ background: "var(--tc-surface)" }}
          >
            <WidgetRenderer widget={w} />
          </div>
        </div>
      ))}
    </div>
  );
}
