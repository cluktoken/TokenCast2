"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { MonitorSmartphone, Wifi, LayoutGrid, Boxes, Sparkles } from "lucide-react";
import { api } from "@/lib/api";
import { AppShell } from "@/components/shell";
import { Button, Card, Input, Spinner } from "@/components/ui";

function Stat({ icon: Icon, label, value }: { icon: any; label: string; value: number }) {
  return (
    <Card className="flex items-center gap-4">
      <div className="tc-accent flex h-11 w-11 items-center justify-center rounded-lg text-white">
        <Icon className="h-5 w-5" />
      </div>
      <div>
        <div className="text-2xl font-bold">{value}</div>
        <div className="text-sm tc-muted">{label}</div>
      </div>
    </Card>
  );
}

export default function DashboardPage() {
  const qc = useQueryClient();
  const router = useRouter();
  const [prompt, setPrompt] = useState("");
  const { data: stats } = useQuery({ queryKey: ["stats"], queryFn: api.dashboardStats });

  const build = useMutation({
    mutationFn: () => api.aiBuild(prompt),
    onSuccess: (res) => {
      qc.invalidateQueries({ queryKey: ["stats"] });
      if (res.layout_id) router.push(`/layouts/${res.layout_id}`);
    },
  });

  return (
    <AppShell>
      <h1 className="mb-6 text-2xl font-bold">Dashboard</h1>
      {!stats ? (
        <Spinner />
      ) : (
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <Stat icon={MonitorSmartphone} label="Total Displays" value={stats.total_displays} />
          <Stat icon={Wifi} label="Online Displays" value={stats.online_displays} />
          <Stat icon={LayoutGrid} label="Total Layouts" value={stats.total_layouts} />
          <Stat icon={Boxes} label="Widgets" value={stats.widget_count} />
        </div>
      )}

      <Card className="mt-6">
        <div className="mb-3 flex items-center gap-2 font-semibold">
          <Sparkles className="tc-accent-text h-5 w-5" /> AI Layout Builder
        </div>
        <div className="flex gap-2">
          <Input
            placeholder='e.g. "Build me a crypto trading command center"'
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && prompt && build.mutate()}
          />
          <Button onClick={() => build.mutate()} disabled={!prompt || build.isPending}>
            {build.isPending ? "Building…" : "Generate"}
          </Button>
        </div>
        {build.isError ? <p className="mt-2 text-sm text-red-400">{(build.error as Error).message}</p> : null}
      </Card>

      <Card className="mt-6">
        <div className="mb-3 font-semibold">Recent Activity</div>
        {stats?.recent_activity?.length ? (
          <ul className="space-y-2 text-sm">
            {stats.recent_activity.map((a: any, i: number) => (
              <li key={i} className="flex justify-between border-b pb-2 last:border-0" style={{ borderColor: "var(--tc-border)" }}>
                <span>
                  <span className="tc-muted capitalize">{a.type}:</span> {a.name}
                </span>
                <span className="tc-muted">{a.at ? new Date(a.at).toLocaleString() : ""}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm tc-muted">No activity yet.</p>
        )}
      </Card>
    </AppShell>
  );
}
