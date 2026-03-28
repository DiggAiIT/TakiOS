"use client";

import { useTranslations } from "next-intl";
import { Bot, ShieldCheck } from "lucide-react";

interface AiTransparencyBannerProps {
  modelUsed: string;
  confidenceScore: number;
}

export function AiTransparencyBanner({ modelUsed, confidenceScore }: AiTransparencyBannerProps) {
  const t = useTranslations("ai");

  const confidencePercent = Math.round(confidenceScore * 100);
  const isAi = modelUsed !== "local-fallback";
  const confidenceLevel =
    confidencePercent >= 80 ? "high" : confidencePercent >= 50 ? "medium" : "low";

  const barColor =
    confidenceLevel === "high"
      ? "bg-emerald-500"
      : confidenceLevel === "medium"
        ? "bg-amber-500"
        : "bg-red-500";

  return (
    <div className="rounded-lg border border-(--border) bg-(--secondary)/30 px-4 py-3">
      <div className="flex items-center gap-2 text-sm">
        {isAi ? (
          <Bot className="h-4 w-4 text-(--primary)" />
        ) : (
          <ShieldCheck className="h-4 w-4 text-(--muted-foreground)" />
        )}
        <span className="font-medium">
          {isAi ? t("aiGenerated") : t("heuristicGenerated")}
        </span>
        <span className="text-(--muted-foreground)">·</span>
        <span className="text-xs text-(--muted-foreground)">{t("model")}: {modelUsed}</span>
      </div>
      <div className="mt-2 flex items-center gap-3">
        <span className="text-xs text-(--muted-foreground)">{t("confidence")}:</span>
        <div className="h-2 flex-1 overflow-hidden rounded-full bg-(--muted)">
          <div
            className={`h-full rounded-full transition-all ${barColor}`}
            style={{ width: `${confidencePercent}%` }}
          />
        </div>
        <span className="text-xs font-medium">{confidencePercent}%</span>
      </div>
    </div>
  );
}
