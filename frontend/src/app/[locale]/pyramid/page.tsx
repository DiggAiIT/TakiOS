"use client";

import { useEffect, useState } from "react";
import { useTranslations, useLocale } from "next-intl";
import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { type KnowledgeLevelData, type LevelStatus } from "@/lib/api-client";
import { useLevelDetail, usePyramid } from "@/hooks/use-pyramid";
import { useAuthStore } from "@/stores/auth-store";
import { Lock, CheckCircle2, Loader2, Cpu } from "lucide-react";
import { PyramidView, LevelDetail } from "@/components/pyramid/PyramidView";

export default function PyramidPage() {
  const t = useTranslations("pyramid");
  const locale = useLocale();
  const token = useAuthStore((s) => s.token);

  const [selectedLevel, setSelectedLevel] = useState<KnowledgeLevelData | null>(null);
  const pyramidQuery = usePyramid(token);
  const pyramidLevels = pyramidQuery.data?.levels ?? [];
  const progress = pyramidQuery.data?.progress ?? {};
  const loading = pyramidQuery.isLoading;
  const detailQuery = useLevelDetail(token, selectedLevel?.id ?? null);
  const units = detailQuery.data?.units ?? [];
  const chains = detailQuery.data?.chains ?? [];
  const loadingDetail = detailQuery.isLoading;

  useEffect(() => {
    if (!selectedLevel && pyramidLevels.length > 0) {
      setSelectedLevel(pyramidLevels[0]);
    }
  }, [pyramidLevels, selectedLevel]);

  function getStatus(levelId: string): LevelStatus {
    return progress[levelId] || "locked";
  }

  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <Header />
        <main className="flex-1 overflow-y-auto p-8">
          <div className="mb-6">
            <h2 className="text-3xl font-bold">{t("title")}</h2>
            <p className="text-[var(--muted-foreground)]">{t("subtitle")}</p>
          </div>

          {/* Legend */}
          <div className="mb-6 flex flex-wrap gap-4">
            {(["locked", "in_progress", "completed"] as const).map((status) => (
              <div key={status} className="flex items-center gap-2 text-sm">
                {status === "locked" && <Lock className="h-4 w-4 text-gray-400" />}
                {status === "in_progress" && (
                  <Loader2 className="h-4 w-4 text-amber-500" />
                )}
                {status === "completed" && (
                  <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                )}
                <span className="text-[var(--muted-foreground)]">
                  {t(status === "in_progress" ? "inProgress" : status)}
                </span>
              </div>
            ))}
          </div>

          {loading ? (
            <div className="space-y-4">
              <Skeleton className="mx-auto h-[420px] w-full max-w-2xl" />
            </div>
          ) : pyramidQuery.isError ? (
            <Card>
              <CardContent className="py-8 text-center">
                <p className="text-[var(--destructive)]">{pyramidQuery.error.detail}</p>
              </CardContent>
            </Card>
          ) : (
            <div className="flex flex-col items-center gap-8 lg:flex-row lg:items-start lg:gap-12">
              {/* Interactive SVG Pyramid */}
              <div className="w-full max-w-2xl shrink-0 lg:w-[520px]">
                <PyramidView
                  levels={pyramidLevels}
                  progress={progress}
                  selectedLevel={selectedLevel}
                  onSelectLevel={setSelectedLevel}
                  locale={locale}
                  t={t}
                />
              </div>

              {/* Detail Panel */}
              <div className="w-full min-w-0 flex-1">
                {selectedLevel ? (
                  <LevelDetail
                    level={selectedLevel}
                    status={getStatus(selectedLevel.id)}
                    units={units}
                    chains={chains}
                    loading={loadingDetail}
                    locale={locale}
                    t={t}
                  />
                ) : (
                  <Card>
                    <CardContent className="py-12 text-center">
                      <Cpu className="mx-auto mb-4 h-12 w-12 text-[var(--muted-foreground)]" />
                      <p className="text-[var(--muted-foreground)]">
                        {t("selectLevel")}
                      </p>
                    </CardContent>
                  </Card>
                )}
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
