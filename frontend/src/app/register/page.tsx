"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Sparkles } from "lucide-react";
import { useAuth } from "@/store/auth";
import { Button, Card, Input } from "@/components/ui";

export default function RegisterPage() {
  const { register, loading } = useAuth();
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      await register(email, password, fullName || undefined);
      router.replace("/dashboard");
    } catch (err: any) {
      setError(err.message || "Registration failed");
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <Card className="w-full max-w-sm">
        <div className="mb-6 flex items-center gap-2 text-xl font-bold">
          <Sparkles className="tc-accent-text h-6 w-6" /> Create your account
        </div>
        <form onSubmit={onSubmit} className="space-y-3">
          <Input placeholder="Full name (optional)" value={fullName} onChange={(e) => setFullName(e.target.value)} />
          <Input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <Input type="password" placeholder="Password (min 8 chars)" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8} />
          {error ? <p className="text-sm text-red-400">{error}</p> : null}
          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? "Creating…" : "Create account"}
          </Button>
        </form>
        <p className="mt-4 text-center text-sm tc-muted">
          Have an account?{" "}
          <Link href="/login" className="tc-accent-text">Sign in</Link>
        </p>
      </Card>
    </div>
  );
}
