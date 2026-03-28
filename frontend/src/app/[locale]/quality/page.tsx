"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { type QualityDashboardMetricData } from "@/lib/api-client";
import { useCreateFeedback, useQualityDashboard } from "@/hooks/use-quality";
import { useAuthStore } from "@/stores/auth-store";
import {
  BarChart3,
  Target,
  TrendingUp,
  TrendingDown,
  MessageSquare,
  Star,
  Send,
} from "lucide-react";

function MetricCard({ metric }: { metric: QualityDashboardMetricData }) {
  const t = useTranslations("quality");
  const onTarget = metric.latest_value !== null && metric.latest_value >= metric.target_value;

  return (
    <Card>
      <CardContent className="p-6">
        <div className="mb-3 flex items-start justify-between">
          <div>
            <p className="text-sm font-medium">{metric.name}</p>
            <p className="text-xs text-(--muted-foreground)">
              {t("targetValue")}: {metric.target_value} {metric.unit}
            </p>
          </div>
          {metric.latest_value !== null ? (
            <Badge className={onTarget ? "bg-green-100 text-green-800" : "bg-amber-100 text-amber-800"}>
              {onTarget ? <TrendingUp className="mr-1 h-3 w-3" /> : <TrendingDown className="mr-1 h-3 w-3" />}
              {onTarget ? t("onTarget") : t("belowTarget")}
            </Badge>
          ) : (
            <Badge variant="outline">{t("noMeasurement")}</Badge>
          )}
        </div>

        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-bold">
            {metric.latest_value !== null ? metric.latest_value.toFixed(1) : "-"}
          </span>
          <span className="text-sm text-(--muted-foreground)">{metric.unit}</span>
        </div>

        {metric.latest_value !== null && metric.target_value > 0 && (
          <div className="mt-3">
            <progress
              className="h-2 w-full accent-green-500"
              max={metric.target_value}
              value={Math.min(metric.target_value, metric.latest_value)}
            />
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function FeedbackForm({
  onSubmit,
  isSubmitting,
}: {
  onSubmit: (data: { category: string; text: string; rating: number }) => Promise<boolean>;
  isSubmitting: boolean;
}) {
  const t = useTranslations("quality");
  const tc = useTranslations("common");
  const [category, setCategory] = useState("general");
  const [text, setText] = useState("");
  const [rating, setRating] = useState(3);
  const [submitted, setSubmitted] = useState(false);

  const categories = ["usability", "content", "performance", "accessibility", "general"] as const;

  useEffect(() => {
    if (!submitted) {
      return;
    }

    const timeoutId = window.setTimeout(() => setSubmitted(false), 3000);
    return () => window.clearTimeout(timeoutId);
  }, [submitted]);

  const handleSubmit = async () => {
    const success = await onSubmit({ category, text, rating });
    if (!success) {
      return;
    }

    setText("");
    setRating(3);
    setSubmitted(true);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <MessageSquare className="h-5 w-5" />
          {t("submitFeedback")}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {submitted && <div className="rounded-lg bg-green-100 p-3 text-sm text-green-800">{t("feedbackSubmitted")}</div>}

        <div>
          <label className="mb-1 block text-sm font-medium">{t("feedbackCategory")}</label>
          <select
            value={category}
            aria-label={t("feedbackCategory")}
            title={t("feedbackCategory")}
            onChange={(event) => setCategory(event.target.value)}
            className="w-full rounded-md border border-(--border) bg-(--background) p-2 text-sm"
          >
            {categories.map((item) => (
              <option key={item} value={item}>
                {t(item)}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium">{t("feedbackText")}</label>
          <textarea
            value={text}
            title={t("feedbackText")}
            placeholder={t("feedbackText")}
            onChange={(event) => setText(event.target.value)}
            className="w-full rounded-md border border-(--border) bg-(--background) p-2 text-sm"
            rows={4}
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium">{t("feedbackRating")}</label>
          <div className="flex gap-1">
            {[1, 2, 3, 4, 5].map((value) => (
              <button key={value} type="button" title={`${value}`} onClick={() => setRating(value)} className="p-1 transition-colors">
                <Star className={`h-6 w-6 ${value <= rating ? "fill-amber-400 text-amber-400" : "text-(--muted-foreground)"}`} />
              </button>
            ))}
          </div>
        </div>

        <Button type="button" disabled={isSubmitting || !text.trim()} onClick={() => void handleSubmit()}>
          <Send className="mr-1 h-4 w-4" />
          {tc("submit")}
        </Button>
      </CardContent>
    </Card>
  );
}

export default function QualityPage() {
  const t = useTranslations("quality");
  const tc = useTranslations("common");
  const token = useAuthStore((state) => state.token);

  const [actionError, setActionError] = useState<string | null>(null);

  const dashboardQuery = useQualityDashboard(token);
  const createFeedback = useCreateFeedback(token);

  const dashboard = dashboardQuery.data ?? null;
  const loading = token ? dashboardQuery.isLoading : false;
  const queryError = dashboardQuery.error?.message || null;

  const retryLoad = () => {
    setActionError(null);
    void dashboardQuery.refetch();
  };

  const handleFeedback = async (data: { category: string; text: string; rating: number }) => {
    if (!token) {
      return false;
    }

    try {
      setActionError(null);
      await createFeedback.mutateAsync(data);
      return true;
    } catch (error) {
      setActionError(error instanceof Error ? error.message : tc("retry"));
      return false;
    }
  };

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

          {loading && (
            <div className="space-y-4">
              {[1, 2, 3].map((index) => (
                <Card key={index}>
                  <CardHeader>
                    <Skeleton className="h-6 w-48" />
                    <Skeleton className="h-4 w-80" />
                  </CardHeader>
                </Card>
              ))}
            </div>
          )}

          {queryError && (
            <Card>
              <CardContent className="py-8 text-center">
                <p className="text-(--destructive)">{queryError}</p>
                <Button type="button" variant="outline" className="mt-4" onClick={retryLoad}>
                  {tc("retry")}
                </Button>
              </CardContent>
            </Card>
          )}

          {!loading && !queryError && (
            <div className="space-y-4">
              {actionError && (
                <Card>
                  <CardContent className="py-4">
                    <p className="text-sm text-(--destructive)">{actionError}</p>
                  </CardContent>
                </Card>
              )}

              <Tabs defaultValue="dashboard">
                <TabsList>
                  <TabsTrigger value="dashboard">
                    <BarChart3 className="mr-1 h-4 w-4" />
                    {t("dashboard")}
                  </TabsTrigger>
                  <TabsTrigger value="feedback">
                    <MessageSquare className="mr-1 h-4 w-4" />
                    {t("feedback")}
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="dashboard" className="mt-6">
                  {dashboard && (
                    <div className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
                      <Card>
                        <CardContent className="flex items-center gap-4 p-6">
                          <div className="rounded-lg bg-blue-100 p-3">
                            <BarChart3 className="h-6 w-6 text-blue-600" />
                          </div>
                          <div>
                            <p className="text-sm text-(--muted-foreground)">{t("metrics")}</p>
                            <p className="text-2xl font-bold">{dashboard.metrics.length}</p>
                          </div>
                        </CardContent>
                      </Card>
                      <Card>
                        <CardContent className="flex items-center gap-4 p-6">
                          <div className="rounded-lg bg-cyan-100 p-3">
                            <MessageSquare className="h-6 w-6 text-cyan-700" />
                          </div>
                          <div>
                            <p className="text-sm text-(--muted-foreground)">{t("totalFeedback")}</p>
                            <p className="text-2xl font-bold">{dashboard.total_feedback_count}</p>
                          </div>
                        </CardContent>
                      </Card>
                      <Card>
                        <CardContent className="flex items-center gap-4 p-6">
                          <div className="rounded-lg bg-amber-100 p-3">
                            <Star className="h-6 w-6 text-amber-600" />
                          </div>
                          <div>
                            <p className="text-sm text-(--muted-foreground)">{t("averageRating")}</p>
                            <p className="text-2xl font-bold">{dashboard.average_rating !== null ? dashboard.average_rating.toFixed(1) : "-"}</p>
                          </div>
                        </CardContent>
                      </Card>
                    </div>
                  )}

                  {dashboard && dashboard.metrics.length > 0 ? (
                    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                      {dashboard.metrics.map((metric) => (
                        <MetricCard key={metric.metric_id} metric={metric} />
                      ))}
                    </div>
                  ) : (
                    <Card>
                      <CardContent className="py-12 text-center">
                        <Target className="mx-auto mb-4 h-12 w-12 text-(--muted-foreground)" />
                        <p className="text-lg font-medium">{t("noMetrics")}</p>
                      </CardContent>
                    </Card>
                  )}
                </TabsContent>

                <TabsContent value="feedback" className="mt-6">
                  <FeedbackForm onSubmit={handleFeedback} isSubmitting={createFeedback.isPending} />
                </TabsContent>
              </Tabs>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}