"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus, Copy, Trash2, Pencil } from "lucide-react";
import { api } from "@/lib/api";
import { AppShell } from "@/components/shell";
import { Button, Card, Input, Spinner } from "@/components/ui";

const THEMES = ["dark", "light", "cyberpunk", "neon", "corporate"];

export default function LayoutsPage() {
  const qc = useQueryClient();
  const router = useRouter();
  const [name, setName] = useState("");
  const [theme, setTheme] = useState("dark");

  const layouts = useQuery({ queryKey: ["layouts"], queryFn: api.listLayouts });
  const templates = useQuery({ queryKey: ["templates"], queryFn: api.listTemplates });
  const invalidate = () => {
    qc.invalidateQueries({ queryKey: ["layouts"] });
    qc.invalidateQueries({ queryKey: ["stats"] });
  };

  const create = useMutation({
    mutationFn: () => api.createLayout({ name, theme }),
    onSuccess: (l) => { invalidate(); router.push(`/layouts/${l.id}`); },
  });
  const clone = useMutation({ mutationFn: api.cloneLayout, onSuccess: invalidate });
  const remove = useMutation({ mutationFn: api.deleteLayout, onSuccess: invalidate });
  const useTemplate = useMutation({
    mutationFn: (id: number) => api.instantiateTemplate(id),
    onSuccess: (l) => { invalidate(); router.push(`/layouts/${l.id}`); },
  });

  return (
    <AppShell>
      <h1 className="mb-6 text-2xl font-bold">Layouts</h1>

      <Card className="mb-6">
        <div className="mb-3 flex items-center gap-2 font-semibold"><Plus className="h-4 w-4" /> New layout</div>
        <div className="flex flex-wrap gap-2">
          <Input className="max-w-xs" placeholder="Layout name" value={name} onChange={(e) => setName(e.target.value)} />
          <select
            className="tc-surface rounded-lg border px-3 py-2 text-sm"
            style={{ borderColor: "var(--tc-border)" }}
            value={theme}
            onChange={(e) => setTheme(e.target.value)}
          >
            {THEMES.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
          <Button onClick={() => create.mutate()} disabled={!name || create.isPending}>Create</Button>
        </div>
      </Card>

      {layouts.isLoading ? <Spinner /> : (
        <div className="mb-8 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {layouts.data?.map((l) => (
            <Card key={l.id}>
              <div className="mb-1 font-semibold">{l.name}</div>
              <div className="mb-3 text-sm tc-muted">Theme: {l.theme}</div>
              <div className="flex gap-2">
                <Link href={`/layouts/${l.id}`} className="flex-1">
                  <Button variant="ghost" className="w-full"><Pencil className="h-4 w-4" /> Edit</Button>
                </Link>
                <Button variant="ghost" onClick={() => clone.mutate(l.id)}><Copy className="h-4 w-4" /></Button>
                <Button variant="danger" onClick={() => remove.mutate(l.id)}><Trash2 className="h-4 w-4" /></Button>
              </div>
            </Card>
          ))}
          {layouts.data?.length === 0 ? <p className="tc-muted">No layouts yet.</p> : null}
        </div>
      )}

      <h2 className="mb-3 text-lg font-semibold">Templates</h2>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {templates.data?.map((t) => (
          <Card key={t.id}>
            <div className="mb-1 font-semibold">{t.name}</div>
            <div className="mb-3 text-sm tc-muted">{t.description}</div>
            <Button className="w-full" onClick={() => useTemplate.mutate(t.id)} disabled={useTemplate.isPending}>
              Use template
            </Button>
          </Card>
        ))}
      </div>
    </AppShell>
  );
}
