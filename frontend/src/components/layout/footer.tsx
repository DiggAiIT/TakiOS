"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";

type HealthStatus = "ok" | "degraded" | "offline";

interface HealthData {
  status: string;
  version: string;
  uptime_seconds: number;
}

export function Footer() {
  const t = useTranslations("footer");
  const [health, setHealth] = useState<HealthStatus>("offline");
  const [version, setVersion] = useState<string>("");

  useEffect(() => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
    const healthUrl = apiUrl.replace(/\/api\/v1\/?$/, "/health");

    let mounted = true;

    async function check() {
      try {
        const res = await fetch(healthUrl, { cache: "no-store" });
        if (!mounted) return;
        if (res.ok) {
          const data: HealthData = await res.json();
          setHealth(data.status === "ok" ? "ok" : "degraded");
          setVersion(data.version || "");
        } else {
          setHealth("degraded");
        }
      } catch {
        if (mounted) setHealth("offline");
      }
    }

    void check();
    const interval = setInterval(() => void check(), 30_000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  const dotColor =
    health === "ok"
      ? "bg-emerald-500"
      : health === "degraded"
        ? "bg-amber-500"
        : "bg-red-500";

  return (
    <footer className="flex items-center justify-between border-t border-(--border) px-6 py-2 text-xs text-(--muted-foreground)">
      <span>TakiOS{version ? ` v${version}` : ""}</span>
      <div className="flex items-center gap-2">
        <span className={`inline-block h-2 w-2 rounded-full ${dotColor}`} />
        <span>{t(health)}</span>
      </div>
    </footer>
  );
}
