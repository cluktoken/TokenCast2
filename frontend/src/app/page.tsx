"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/store/auth";
import { Spinner } from "@/components/ui";

export default function Home() {
  const { user, initialized } = useAuth();
  const router = useRouter();
  useEffect(() => {
    if (initialized) router.replace(user ? "/dashboard" : "/login");
  }, [initialized, user, router]);
  return <Spinner />;
}
