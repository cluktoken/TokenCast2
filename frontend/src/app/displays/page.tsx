"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus, Trash2, Play, Circle } from "lucide-react";
import { api } from "@/lib/api";
import { AppShell } from "@/components/shell";
import { Button, Card, Input, Spinner } from "@/components/ui";
import type { DeviceType } from "@/lib/types";

const DEVICE_TYPES: DeviceType[] = [
  "browser", "windows", "linux", "raspberry_pi", "android_tv",
  "fire_tv", "samsung_tv", "lg_tv", "tablet", "other",
];

const STATUS_COLOR: Record<string, string> = {
  online: "#22c55e", offline: "#ef4444", unpaired: "#eab308",
};

export default function DisplaysPage() {
  const qc = useQueryClient();
  const [name, setName] = useState("");
  const [deviceType, setDeviceType] = useState<DeviceType>("browser");

  const displays = useQuery({ queryKey: ["displays"], queryFn: api.listDisplays });
  const layouts = useQuery({ queryKey: ["layouts"], queryFn: api.listLayouts });

  const invalidate = () => {
    qc.invalidateQueries({ queryKey: ["displays"] });
    qc.invalidateQueries({ queryKey: ["stats"] });
  };

  const create = useMutation({
    mutationFn: () => api.createDisplay({ name, device_type: deviceType }),
    onSuccess: () => { setName(""); invalidate(); },
  });
  const remove = useMutation({ mutationFn: api.deleteDisplay, onSuccess: invalidate });
  const assign = useMutation({
    mutationFn: ({ id, layoutId }: { id: number; layoutId: number | null }) =>
      api.assignLayout(id, layoutId),
    onSuccess: invalidate,
  });

  return (
    <AppShell>
      <h1 className="mb-6 text-2xl font-bold">Displays</h1>

      <Card className="mb-6">
        <div className="mb-3 flex items-center gap-2 font-semibold">
          <Plus className="h-4 w-4" /> Add a display
        </div>
        <div className="flex flex-wrap gap-2">
          <Input className="max-w-xs" placeholder="Display name" value={name} onChange={(e) => setName(e.target.value)} />
          <select
            className="tc-surface rounded-lg border px-3 py-2 text-sm"
            style={{ borderColor: "var(--tc-border)" }}
            value={deviceType}
            onChange={(e) => setDeviceType(e.target.value as DeviceType)}
          >
            {DEVICE_TYPES.map((d) => (
              <option key={d} value={d}>{d.replace("_", " ")}</option>
            ))}
          </select>
          <Button onClick={() => create.mutate()} disabled={!name || create.isPending}>Create</Button>
        </div>
      </Card>

      {displays.isLoading ? (
        <Spinner />
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {displays.data?.map((d) => (
            <Card key={d.id}>
              <div className="mb-2 flex items-center justify-between">
                <div className="font-semibold">{d.name}</div>
                <span className="flex items-center gap-1 text-xs tc-muted">
                  <Circle className="h-2.5 w-2.5" fill={STATUS_COLOR[d.status]} stroke="none" />
                  {d.status}
                </span>
              </div>
              <div className="mb-3 text-sm tc-muted">
                {d.device_type.replace("_", " ")} · code {d.pairing_code}
              </div>
              <select
                className="tc-surface mb-3 w-full rounded-lg border px-3 py-2 text-sm"
                style={{ borderColor: "var(--tc-border)" }}
                value={d.current_layout_id ?? ""}
                onChange={(e) =>
                  assign.mutate({ id: d.id, layoutId: e.target.value ? Number(e.target.value) : null })
                }
              >
                <option value="">— No layout —</option>
                {layouts.data?.map((l) => (
                  <option key={l.id} value={l.id}>{l.name}</option>
                ))}
              </select>
              <div className="flex gap-2">
                <a href={`/player/${d.id}`} target="_blank" rel="noreferrer" className="flex-1">
                  <Button variant="ghost" className="w-full"><Play className="h-4 w-4" /> Preview</Button>
                </a>
                <Button variant="danger" onClick={() => remove.mutate(d.id)}>
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </Card>
          ))}
          {displays.data?.length === 0 ? <p className="tc-muted">No displays yet.</p> : null}
        </div>
      )}
    </AppShell>
  );
}
