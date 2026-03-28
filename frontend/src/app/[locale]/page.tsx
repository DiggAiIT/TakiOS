"use client";

import { useLocale, useTranslations } from "next-intl";
import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useDashboardStats } from "@/hooks/use-dashboard";
import { useAuthStore } from "@/stores/auth-store";
import { Pyramid, BookOpen, ClipboardCheck, FolderKanban, CheckCircle2, Clock3, Lock } from "lucide-react";

const STATUS_STYLES = {
  completed: "border-emerald-200 bg-emerald-50 text-emerald-800",
  in_progress: "border-amber-200 bg-amber-50 text-amber-800",
  locked: "border-slate-200 bg-slate-100 text-slate-600",
} as const;

export default function DashboardPage() {
  const t = useTranslations("dashboard");
  const tc = useTranslations("common");
  const tn = useTranslations("nav");
  const tp = useTranslations("pyramid");
  const locale = useLocale();
  const token = useAuthStore((state) => state.token);
  const dashboard = useDashboardStats(token);
  const levels = [...dashboard.data.levels].sort((left, right) => right.pyramid_position - left.pyramid_position);
  const visibleLevels = levels.slice(0, 7);
  const getLevelName = (level: { name_de: string; name_en: string }) =>
    locale === "de" ? level.name_de : level.name_en;

  const stats = [
    {
      key: "yourProgress",
      icon: Pyramid,
      value: `${dashboard.data.completedLevels} / ${dashboard.data.totalLevels}`,
      sub: tp("completed"),
    },
    {
      key: "recentModules",
      icon: BookOpen,
      value: String(dashboard.data.moduleCount),
      sub: tn("modules"),
    },
    {
      key: "upcomingExams",
      icon: ClipboardCheck,
      value: String(dashboard.data.examCount),
      sub: tn("assess"),
    },
    {
      key: "activeProjects",
      icon: FolderKanban,
      value: String(dashboard.data.activeProjectCount),
      sub: `${dashboard.data.availableProjectCount} ${tn("projects")}`,
    },
  ];

  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <Header />
        <main className="flex-1 overflow-y-auto p-8">
          <div className="mb-8">
            <h2 className="text-3xl font-bold">{t("welcome")}</h2>
            <p className="text-(--muted-foreground)">{t("subtitle")}</p>
          </div>

          {dashboard.error && (
            <Card className="mb-6">
              <CardContent className="py-6 text-center">
                <p className="text-(--destructive)">{dashboard.error.detail}</p>
                <Button type="button" variant="outline" className="mt-4" onClick={() => void dashboard.refetch()}>
                  {tc("retry")}
                </Button>
              </CardContent>
            </Card>
          )}

          <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
            {dashboard.isLoading
              ? Array.from({ length: 4 }).map((_, index) => (
                  <Card key={index}>
                    <CardHeader>
                      <Skeleton className="h-4 w-24" />
                      <Skeleton className="h-8 w-16" />
                    </CardHeader>
                    <CardContent>
                      <Skeleton className="h-3 w-20" />
                    </CardContent>
                  </Card>
                ))
              : stats.map(({ key, icon: Icon, value, sub }) => (
                  <Card key={key}>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <CardDescription>{t(key)}</CardDescription>
                        <Icon className="h-5 w-5 text-(--muted-foreground)" />
                      </div>
                      <CardTitle>{value}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-xs text-(--muted-foreground)">{sub}</p>
                    </CardContent>
                  </Card>
                ))}
          </div>

          <Card className="mt-8">
            <CardHeader>
              <CardTitle>{tn("pyramid")}</CardTitle>
              <CardDescription>{tp("subtitle")}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
                <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-4">
                  <div className="flex items-center gap-2 text-sm font-medium text-emerald-800">
                    <CheckCircle2 className="h-4 w-4" />
                    {tp("completed")}
                  </div>
                  <p className="mt-2 text-3xl font-semibold text-emerald-900">
                    {dashboard.data.completedLevels}
                  </p>
                </div>
                <div className="rounded-lg border border-amber-200 bg-amber-50 p-4">
                  <div className="flex items-center gap-2 text-sm font-medium text-amber-800">
                    <Clock3 className="h-4 w-4" />
                    {tp("inProgress")}
                  </div>
                  <p className="mt-2 text-3xl font-semibold text-amber-900">
                    {dashboard.data.inProgressLevels}
                  </p>
                </div>
                <div className="rounded-lg border border-slate-200 bg-slate-100 p-4">
                  <div className="flex items-center gap-2 text-sm font-medium text-slate-700">
                    <Lock className="h-4 w-4" />
                    {tp("locked")}
                  </div>
                  <p className="mt-2 text-3xl font-semibold text-slate-800">
                    {dashboard.data.lockedLevels}
                  </p>
                </div>
              </div>

              {visibleLevels.length > 0 ? (
                <div className="space-y-3">
                  {visibleLevels.map((level) => {
                    const status = dashboard.data.progressByLevel[level.id] ?? "locked";
                    return (
                      <div
                        key={level.id}
                        className="flex items-center justify-between rounded-lg border border-(--border) px-4 py-3"
                      >
                        <div className="flex items-center gap-3">
                          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-(--secondary) text-sm font-semibold">
                            {level.pyramid_position}
                          </div>
                          <div>
                            <p className="font-medium">{getLevelName(level)}</p>
                            <p className="text-xs text-(--muted-foreground)">
                              {level.unlock_criteria?.required_module_codes?.length ?? 0} {tn("modules")}
                            </p>
                          </div>
                        </div>
                        <span className={`rounded-full border px-3 py-1 text-xs font-medium ${STATUS_STYLES[status]}`}>
                          {status === "in_progress" ? tp("inProgress") : tp(status)}
                        </span>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="rounded-lg border border-dashed border-(--border) px-4 py-8 text-center text-sm text-(--muted-foreground)">
                  {tc("noData")}
                </div>
              )}
            </CardContent>
          </Card>
        </main>
      </div>
    </div>
  );
}
