"use client";

import { useTranslations, useLocale } from "next-intl";
import { useParams } from "next/navigation";
import { Link } from "@/i18n/navigation";
import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { useModuleDetail } from "@/hooks/use-modules";
import { useAuthStore } from "@/stores/auth-store";
import {
  ArrowLeft,
  BookOpen,
  ChevronRight,
  ClipboardCheck,
  GraduationCap,
} from "lucide-react";

export default function ModuleDetailPage() {
  const t = useTranslations("modules");
  const tc = useTranslations("common");
  const locale = useLocale();
  const params = useParams();
  const moduleId = params.moduleId as string;
  const token = useAuthStore((s) => s.token);
  const moduleQuery = useModuleDetail(token, moduleId);
  const moduleData = moduleQuery.data ?? null;
  const loading = moduleQuery.isLoading;
  const error = moduleQuery.error?.detail ?? null;

  const n = (obj: { name_de?: string; name_en?: string; title_de?: string; title_en?: string }) =>
    locale === "de" ? (obj.name_de ?? obj.title_de ?? "") : (obj.name_en ?? obj.title_en ?? "");

  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <Header />
        <main className="flex-1 overflow-y-auto p-8">
          <Link
            href="/modules"
            className="mb-4 inline-flex items-center gap-1 text-sm text-(--muted-foreground) hover:text-(--foreground)"
          >
            <ArrowLeft className="h-4 w-4" />
            {t("backToModules")}
          </Link>

          {loading && (
            <div className="space-y-4">
              <Skeleton className="h-8 w-64" />
              <Skeleton className="h-4 w-96" />
              <Skeleton className="h-48 w-full" />
            </div>
          )}

          {error && (
            <Card>
              <CardContent className="py-8 text-center text-(--destructive)">
                <p>{error}</p>
                <Button
                  type="button"
                  variant="outline"
                  className="mt-4"
                  onClick={() => void moduleQuery.refetch()}
                >
                  {tc("retry")}
                </Button>
              </CardContent>
            </Card>
          )}

          {moduleData && (
            <>
              <div className="mb-6">
                <div className="flex items-center gap-3">
                  <Badge variant="outline" className="text-base">
                    {moduleData.code}
                  </Badge>
                  <Badge variant="secondary">
                    {t("semester")} {moduleData.semester}
                  </Badge>
                  <Badge>{moduleData.credits} {t("credits")}</Badge>
                </div>
                <h2 className="mt-2 text-3xl font-bold">{n(moduleData)}</h2>
                <p className="mt-1 text-(--muted-foreground)">
                  {locale === "de" ? moduleData.description_de : moduleData.description_en}
                </p>
              </div>

              <div className="flex gap-3 mb-6">
                <Link href={`/assess?module=${moduleId}`}>
                  <Button variant="outline">
                    <ClipboardCheck className="mr-2 h-4 w-4" />
                    {t("takeExam")}
                  </Button>
                </Link>
              </div>

              <Separator />

              <div className="mt-6">
                <h3 className="mb-4 flex items-center gap-2 text-xl font-semibold">
                  <BookOpen className="h-5 w-5" />
                  {t("learningUnits")} ({moduleData.units.length})
                </h3>

                {moduleData.units.length === 0 ? (
                  <p className="text-(--muted-foreground)">
                    Noch keine Lerneinheiten vorhanden.
                  </p>
                ) : (
                  <div className="space-y-2">
                    {moduleData.units
                      .sort((a, b) => a.position - b.position)
                      .map((unit) => (
                        <Link
                          key={unit.id}
                          href={`/learn/${unit.id}`}
                          className="group flex items-center justify-between rounded-lg border border-(--border) p-4 transition-colors hover:bg-(--accent)"
                        >
                          <div className="flex items-center gap-4">
                            <span className="flex h-8 w-8 items-center justify-center rounded-full bg-(--primary) text-sm font-bold text-(--primary-foreground)">
                              {unit.position}
                            </span>
                            <div>
                              <p className="font-medium">
                                {locale === "de" ? unit.title_de : unit.title_en}
                              </p>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <GraduationCap className="h-4 w-4 text-(--muted-foreground)" />
                            <span className="text-sm text-(--muted-foreground)">
                              {t("startLearning")}
                            </span>
                            <ChevronRight className="h-4 w-4 text-(--muted-foreground) transition-transform group-hover:translate-x-1" />
                          </div>
                        </Link>
                      ))}
                  </div>
                )}
              </div>
            </>
          )}
        </main>
      </div>
    </div>
  );
}
