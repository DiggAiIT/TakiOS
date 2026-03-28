"use client";

import { useTranslations, useLocale } from "next-intl";
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
import { Skeleton } from "@/components/ui/skeleton";
import { useSubjectsWithModules } from "@/hooks/use-modules";
import { useAuthStore } from "@/stores/auth-store";
import { GraduationCap, ChevronRight, BookOpen, Lightbulb } from "lucide-react";

export default function LearnPage() {
  const t = useTranslations("learn");
  const te = useTranslations("eselsbruecke");
  const tc = useTranslations("common");
  const locale = useLocale();
  const token = useAuthStore((s) => s.token);
  const modulesQuery = useSubjectsWithModules(token);
  const subjectList = modulesQuery.data?.subjectList ?? [];
  const modulesBySubject = modulesQuery.data?.modulesBySubject ?? {};
  const loading = modulesQuery.isLoading;
  const error = modulesQuery.error?.detail ?? null;

  const n = (obj: { name_de: string; name_en: string }) =>
    locale === "de" ? obj.name_de : obj.name_en;

  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <Header />
        <main className="flex-1 overflow-y-auto p-8">
          <div className="mb-6">
            <h2 className="text-3xl font-bold">{t("title")}</h2>
            <p className="text-(--muted-foreground)">{t("subtitle")}</p>
          </div>

          {/* Eselsbrücken feature highlight */}
          <Card className="mb-8 border-(--primary)/30 bg-(--primary)/5">
            <CardContent className="flex items-center gap-4 py-6">
              <Lightbulb className="h-10 w-10 text-(--primary)" />
              <div>
                <h3 className="text-lg font-semibold">{te("title")}</h3>
                <p className="text-sm text-(--muted-foreground)">
                  {te("personalized")}
                </p>
              </div>
            </CardContent>
          </Card>

          {loading && (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-24 w-full" />
              ))}
            </div>
          )}

          {!loading && error && (
            <Card>
              <CardContent className="py-8 text-center">
                <p className="text-(--destructive)">{error}</p>
                <button type="button" className="mt-4 text-sm underline" onClick={() => void modulesQuery.refetch()}>
                  {tc("retry")}
                </button>
              </CardContent>
            </Card>
          )}

          {!loading && !error && (
            <div className="space-y-6">
              {subjectList.map((subject) => {
                const mods = modulesBySubject[subject.id] || [];
                if (mods.length === 0) return null;
                return (
                  <div key={subject.id}>
                    <h3 className="mb-3 flex items-center gap-2 text-lg font-semibold">
                      <BookOpen className="h-4 w-4 text-(--primary)" />
                      {n(subject)}
                    </h3>
                    <div className="grid grid-cols-1 gap-2 md:grid-cols-2 lg:grid-cols-3">
                      {mods.map((mod) => (
                        <Link
                          key={mod.id}
                          href={`/modules/${mod.id}`}
                          className="group flex items-center justify-between rounded-lg border border-(--border) p-3 transition-colors hover:bg-(--accent)"
                        >
                          <div className="min-w-0">
                            <div className="flex items-center gap-2">
                              <Badge variant="outline" className="text-xs">
                                {mod.code}
                              </Badge>
                            </div>
                            <p className="mt-1 text-sm font-medium">{n(mod)}</p>
                          </div>
                          <ChevronRight className="h-4 w-4 shrink-0 text-(--muted-foreground) transition-transform group-hover:translate-x-1" />
                        </Link>
                      ))}
                    </div>
                  </div>
                );
              })}

              {subjectList.length === 0 && (
                <Card>
                  <CardContent className="py-12 text-center">
                    <GraduationCap className="mx-auto mb-4 h-12 w-12 text-(--muted-foreground)" />
                    <p className="text-(--muted-foreground)">{t("selectUnit")}</p>
                  </CardContent>
                </Card>
              )}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
