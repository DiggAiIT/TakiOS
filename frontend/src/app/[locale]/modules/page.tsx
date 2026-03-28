"use client";

import { useState } from "react";
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
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { type ModuleData } from "@/lib/api-client";
import { useSubjectsWithModules } from "@/hooks/use-modules";
import { useAuthStore } from "@/stores/auth-store";
import { BookOpen, ChevronRight, GraduationCap } from "lucide-react";

export default function ModulesPage() {
  const t = useTranslations("modules");
  const tc = useTranslations("common");
  const locale = useLocale();
  const token = useAuthStore((s) => s.token);
  const [semesterFilter, setSemesterFilter] = useState<string>("all");
  const modulesQuery = useSubjectsWithModules(token);
  const subjectList = modulesQuery.data?.subjectList ?? [];
  const modulesBySubject = modulesQuery.data?.modulesBySubject ?? {};
  const loading = modulesQuery.isLoading;
  const error = modulesQuery.error?.detail ?? null;

  const n = (obj: { name_de: string; name_en: string }) =>
    locale === "de" ? obj.name_de : obj.name_en;

  const d = (obj: { description_de: string; description_en: string }) =>
    locale === "de" ? obj.description_de : obj.description_en;

  const filteredModules = (mods: ModuleData[]) => {
    if (semesterFilter === "all") return mods;
    return mods.filter((m) => m.semester === parseInt(semesterFilter));
  };

  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <Header />
        <main className="flex-1 overflow-y-auto p-8">
          <div className="mb-6 flex items-start justify-between">
            <div>
              <h2 className="text-3xl font-bold">{t("title")}</h2>
              <p className="text-[var(--muted-foreground)]">{t("subtitle")}</p>
            </div>
            <Select
              value={semesterFilter}
              onChange={(e) => setSemesterFilter(e.target.value)}
              className="w-48"
              label={t("semester")}
            >
              <option value="all">{t("allSemesters")}</option>
              {[1, 2, 3, 4, 5, 6, 7].map((s) => (
                <option key={s} value={s}>
                  {t("semester")} {s}
                </option>
              ))}
            </Select>
          </div>

          {loading && (
            <div className="space-y-6">
              {[1, 2, 3].map((i) => (
                <Card key={i}>
                  <CardHeader>
                    <Skeleton className="h-6 w-48" />
                    <Skeleton className="h-4 w-80" />
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
                      <Skeleton className="h-20 w-full" />
                      <Skeleton className="h-20 w-full" />
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {error && (
            <Card>
              <CardContent className="py-8 text-center">
                <p className="text-[var(--destructive)]">{error}</p>
                <Button
                  type="button"
                  variant="outline"
                  className="mt-4"
                  onClick={() => void modulesQuery.refetch()}
                >
                  {tc("retry")}
                </Button>
              </CardContent>
            </Card>
          )}

          {!loading && !error && !token && (
            <Card>
              <CardContent className="py-12 text-center">
                <GraduationCap className="mx-auto mb-4 h-12 w-12 text-[var(--muted-foreground)]" />
                <p className="text-lg font-medium">{tc("login")}</p>
                <p className="text-sm text-[var(--muted-foreground)]">
                  {t("pleaseLogin")}
                </p>
                <Link href="/auth/login">
                  <Button type="button" className="mt-4">{tc("login")}</Button>
                </Link>
              </CardContent>
            </Card>
          )}

          {!loading && !error && token && (
            <div className="space-y-8">
              {subjectList.map((subject) => {
                const mods = filteredModules(modulesBySubject[subject.id] || []);
                if (mods.length === 0 && semesterFilter !== "all") return null;

                return (
                  <Card key={subject.id}>
                    <CardHeader>
                      <div className="flex items-center gap-3">
                        <BookOpen className="h-5 w-5 text-[var(--primary)]" />
                        <div>
                          <CardTitle>{n(subject)}</CardTitle>
                          <CardDescription>{d(subject)}</CardDescription>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      {mods.length === 0 ? (
                        <p className="text-sm text-[var(--muted-foreground)]">
                          {t("noModules")}
                        </p>
                      ) : (
                        <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
                          {mods.map((mod) => (
                            <Link
                              key={mod.id}
                              href={`/modules/${mod.id}`}
                              className="group flex items-center justify-between rounded-lg border border-[var(--border)] p-4 transition-colors hover:bg-[var(--accent)]"
                            >
                              <div className="min-w-0 flex-1">
                                <div className="flex items-center gap-2">
                                  <Badge variant="outline">{mod.code}</Badge>
                                  <Badge variant="secondary">
                                    {t("semester")} {mod.semester}
                                  </Badge>
                                </div>
                                <p className="mt-1 font-medium">{n(mod)}</p>
                                <p className="text-xs text-[var(--muted-foreground)]">
                                  {mod.credits} {t("credits")}
                                </p>
                              </div>
                              <ChevronRight className="h-4 w-4 text-[var(--muted-foreground)] transition-transform group-hover:translate-x-1" />
                            </Link>
                          ))}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
