"use client";

import { useEffect, useRef, useState } from "react";
import { useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus, Trash2, ExternalLink, Save } from "lucide-react";
import { api } from "@/lib/api";
import { AppShell } from "@/components/shell";
import { Button, Card, Spinner } from "@/components/ui";
import { WidgetRenderer } from "@/widgets";
import type { Widget } from "@/lib/types";

interface Drag {
  id: number;
  mode: "move" | "resize";
  startX: number;
  startY: number;
  origX: number;
  origY: number;
  origW: number;
  origH: number;
}

export default function LayoutBuilderPage() {
  const params = useParams<{ id: string }>();
  const layoutId = Number(params.id);
  const qc = useQueryClient();
  const canvasRef = useRef<HTMLDivElement>(null);
  const [cell, setCell] = useState({ w: 60, h: 60 });
  const [drag, setDrag] = useState<Drag | null>(null);
  const [local, setLocal] = useState<Record<number, Partial<Widget>>>({});

  const layout = useQuery({
    queryKey: ["layout", layoutId],
    queryFn: () => api.getLayout(layoutId),
  });
  const catalog = useQuery({ queryKey: ["catalog"], queryFn: api.widgetCatalog });

  const grid = layout.data?.grid_config ?? { columns: 12, rows: 8, gap: 8 };

  useEffect(() => {
    function resize() {
      const el = canvasRef.current;
      if (!el) return;
      setCell({
        w: el.clientWidth / grid.columns,
        h: el.clientHeight / grid.rows,
      });
    }
    resize();
    window.addEventListener("resize", resize);
    return () => window.removeEventListener("resize", resize);
  }, [grid.columns, grid.rows, layout.data]);

  const addWidget = useMutation({
    mutationFn: (type: string) => {
      const def = catalog.data?.widgets.find((w) => w.type === type)!;
      return api.addWidget(layoutId, {
        widget_type: type,
        config: def.default_config as any,
        position_x: 0,
        position_y: 0,
        width: def.default_width,
        height: def.default_height,
      });
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["layout", layoutId] }),
  });
  const removeWidget = useMutation({
    mutationFn: (wid: number) => api.deleteWidget(layoutId, wid),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["layout", layoutId] }),
  });
  const saveWidget = useMutation({
    mutationFn: ({ wid, body }: { wid: number; body: Partial<Widget> }) =>
      api.updateWidget(layoutId, wid, body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["layout", layoutId] }),
  });

  function onPointerDown(e: React.PointerEvent, w: Widget, mode: "move" | "resize") {
    e.preventDefault();
    e.stopPropagation();
    setDrag({
      id: w.id, mode,
      startX: e.clientX, startY: e.clientY,
      origX: w.position_x, origY: w.position_y, origW: w.width, origH: w.height,
    });
  }

  useEffect(() => {
    if (!drag) return;
    function onMove(e: PointerEvent) {
      const dx = Math.round((e.clientX - drag!.startX) / cell.w);
      const dy = Math.round((e.clientY - drag!.startY) / cell.h);
      setLocal((prev) => {
        if (drag!.mode === "move") {
          return {
            ...prev,
            [drag!.id]: {
              position_x: Math.max(0, Math.min(grid.columns - drag!.origW, drag!.origX + dx)),
              position_y: Math.max(0, Math.min(grid.rows - drag!.origH, drag!.origY + dy)),
            },
          };
        }
        return {
          ...prev,
          [drag!.id]: {
            width: Math.max(1, Math.min(grid.columns - drag!.origX, drag!.origW + dx)),
            height: Math.max(1, Math.min(grid.rows - drag!.origY, drag!.origH + dy)),
          },
        };
      });
    }
    function onUp() {
      const body = local[drag!.id];
      if (body) saveWidget.mutate({ wid: drag!.id, body });
      setDrag(null);
    }
    window.addEventListener("pointermove", onMove);
    window.addEventListener("pointerup", onUp);
    return () => {
      window.removeEventListener("pointermove", onMove);
      window.removeEventListener("pointerup", onUp);
    };
  }, [drag, cell, grid, local, saveWidget]);

  if (layout.isLoading || !layout.data) return <AppShell><Spinner /></AppShell>;

  return (
    <AppShell>
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-2xl font-bold">{layout.data.name}</h1>
        <a href={`/layouts/${layoutId}/preview`} className="hidden" />
      </div>

      <div className="grid grid-cols-[240px_1fr] gap-4">
        <Card className="h-fit">
          <div className="mb-3 flex items-center gap-2 font-semibold"><Plus className="h-4 w-4" /> Widgets</div>
          <div className="space-y-1">
            {catalog.data?.widgets.map((w) => (
              <button
                key={w.type}
                onClick={() => addWidget.mutate(w.type)}
                className="tc-surface flex w-full items-center justify-between rounded-lg border px-3 py-2 text-left text-sm hover:opacity-80"
                style={{ borderColor: "var(--tc-border)" }}
              >
                <span>{w.name}</span>
                <Plus className="h-3.5 w-3.5 opacity-60" />
              </button>
            ))}
          </div>
        </Card>

        <div
          data-theme={layout.data.theme}
          ref={canvasRef}
          className="relative w-full overflow-hidden rounded-xl border"
          style={{
            aspectRatio: `${grid.columns} / ${grid.rows}`,
            borderColor: "var(--tc-border)",
            background: "var(--tc-bg)",
            backgroundImage:
              "linear-gradient(var(--tc-border) 1px, transparent 1px), linear-gradient(90deg, var(--tc-border) 1px, transparent 1px)",
            backgroundSize: `${100 / grid.columns}% ${100 / grid.rows}%`,
          }}
        >
          {layout.data.widgets.map((w) => {
            const o = { ...w, ...local[w.id] };
            return (
              <div
                key={w.id}
                className="group absolute overflow-hidden rounded-lg border"
                style={{
                  left: `${(o.position_x! / grid.columns) * 100}%`,
                  top: `${(o.position_y! / grid.rows) * 100}%`,
                  width: `${(o.width! / grid.columns) * 100}%`,
                  height: `${(o.height! / grid.rows) * 100}%`,
                  borderColor: "var(--tc-border)",
                  background: "var(--tc-surface)",
                }}
              >
                <div
                  className="flex cursor-move items-center justify-between px-2 py-1 text-xs opacity-0 transition group-hover:opacity-100"
                  style={{ background: "var(--tc-border)" }}
                  onPointerDown={(e) => onPointerDown(e, w, "move")}
                >
                  <span>{w.widget_type}</span>
                  <button onClick={() => removeWidget.mutate(w.id)}><Trash2 className="h-3.5 w-3.5" /></button>
                </div>
                <div className="pointer-events-none h-[calc(100%-1.5rem)]">
                  <WidgetRenderer widget={w} />
                </div>
                <div
                  className="absolute bottom-0 right-0 h-4 w-4 cursor-se-resize opacity-0 group-hover:opacity-100"
                  style={{ background: "var(--tc-accent)" }}
                  onPointerDown={(e) => onPointerDown(e, w, "resize")}
                />
              </div>
            );
          })}
          {layout.data.widgets.length === 0 ? (
            <div className="flex h-full items-center justify-center tc-muted">
              Add widgets from the palette →
            </div>
          ) : null}
        </div>
      </div>
      <p className="mt-3 flex items-center gap-2 text-sm tc-muted">
        <Save className="h-4 w-4" /> Changes save automatically. Drag headers to move, corner to resize.
      </p>
    </AppShell>
  );
}
