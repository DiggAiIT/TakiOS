"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
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
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { type ImpactAssessmentData, type SurveyData } from "@/lib/api-client";
import { useAssessments, useSubmitSurveyResponse, useSurveys } from "@/hooks/use-impact";
import { useAuthStore } from "@/stores/auth-store";
import {
  Globe,
  ClipboardList,
  ShieldAlert,
  AlertTriangle,
  CheckCircle2,
  Send,
} from "lucide-react";

const RISK_COLORS: Record<string, "secondary" | "success" | "warning" | "destructive"> = {
  low: "success",
  medium: "secondary",
  high: "warning",
  critical: "destructive",
};

function RiskBadge({ level, t }: { level: string; t: (key: string) => string }) {
  return <Badge variant={RISK_COLORS[level] || "secondary"}>{t(level)}</Badge>;
}

function AssessmentCard({
  assessment,
  t,
}: {
  assessment: ImpactAssessmentData;
  t: (key: string) => string;
}) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="text-sm font-medium">{assessment.title}</CardTitle>
            <CardDescription className="mt-1">
              <Badge variant="outline" className="mr-2">
                {assessment.category}
              </Badge>
              <RiskBadge level={assessment.risk_level} t={t} />
            </CardDescription>
          </div>
          {assessment.risk_level === "critical" ? (
            <ShieldAlert className="h-5 w-5 text-(--destructive)" />
          ) : assessment.risk_level === "high" ? (
            <AlertTriangle className="h-5 w-5 text-amber-500" />
          ) : (
            <CheckCircle2 className="h-5 w-5 text-green-500" />
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <p className="text-sm text-(--muted-foreground)">{assessment.description}</p>
        <div className="rounded-lg bg-(--muted) p-3">
          <p className="text-xs font-medium uppercase tracking-wide text-(--muted-foreground)">
            {t("mitigation")}
          </p>
          <p className="mt-1 text-sm">{assessment.mitigation}</p>
        </div>
      </CardContent>
    </Card>
  );
}

function SurveyCard({
  survey,
  onSubmit,
  t,
}: {
  survey: SurveyData;
  onSubmit: (surveyId: string, responses: Record<string, string>) => Promise<boolean>;
  t: (key: string) => string;
}) {
  const questions = Array.isArray(survey.questions) ? survey.questions : [];
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    setSubmitting(true);
    const success = await onSubmit(survey.id, answers);
    setSubmitting(false);
    if (success) {
      setSubmitted(true);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-sm font-medium">
          <ClipboardList className="h-4 w-4" />
          {survey.title}
        </CardTitle>
        <CardDescription>
          {questions.length} {t("questions")}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {submitted ? (
          <div className="flex items-center gap-2 text-green-600">
            <CheckCircle2 className="h-5 w-5" />
            <p className="text-sm font-medium">{t("responseSubmitted")}</p>
          </div>
        ) : (
          <div className="space-y-4">
            {questions.map((questionValue, index) => {
              const question = typeof questionValue === "string" ? questionValue : String(questionValue);
              const key = `q${index}`;

              return (
                <div key={key}>
                  <label className="mb-1 block text-sm font-medium">
                    {index + 1}. {question}
                  </label>
                  <textarea
                    value={answers[key] || ""}
                    onChange={(event) =>
                      setAnswers((previous) => ({ ...previous, [key]: event.target.value }))
                    }
                    placeholder={t("yourAnswer")}
                    className="w-full rounded-md border border-(--border) bg-(--background) p-2 text-sm"
                    rows={2}
                  />
                </div>
              );
            })}
            <Button
              type="button"
              size="sm"
              disabled={submitting || Object.keys(answers).length === 0}
              onClick={() => void handleSubmit()}
            >
              <Send className="mr-1 h-4 w-4" />
              {t("submitResponse")}
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default function ImpactPage() {
  const t = useTranslations("impact");
  const tc = useTranslations("common");
  const token = useAuthStore((state) => state.token);

  const [actionError, setActionError] = useState<string | null>(null);

  const assessmentsQuery = useAssessments(token);
  const surveysQuery = useSurveys(token);
  const submitSurveyResponse = useSubmitSurveyResponse(token);

  const assessments = assessmentsQuery.data ?? [];
  const surveys = surveysQuery.data ?? [];
  const categories = [...new Set(assessments.map((assessment) => assessment.category))];

  const loading = token ? assessmentsQuery.isLoading || surveysQuery.isLoading : false;
  const queryError = assessmentsQuery.error?.message || surveysQuery.error?.message || null;

  const retryLoad = () => {
    setActionError(null);
    void assessmentsQuery.refetch();
    void surveysQuery.refetch();
  };

  const handleSurveySubmit = async (surveyId: string, responses: Record<string, string>) => {
    if (!token) {
      return false;
    }

    try {
      setActionError(null);
      await submitSurveyResponse.mutateAsync({ survey_id: surveyId, responses });
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

              <Tabs defaultValue="assessments">
                <TabsList>
                  <TabsTrigger value="assessments">
                    <Globe className="mr-1 h-4 w-4" />
                    {t("assessments")}
                    {assessments.length > 0 && (
                      <Badge variant="secondary" className="ml-2">
                        {assessments.length}
                      </Badge>
                    )}
                  </TabsTrigger>
                  <TabsTrigger value="surveys">
                    <ClipboardList className="mr-1 h-4 w-4" />
                    {t("surveys")}
                    {surveys.length > 0 && (
                      <Badge variant="secondary" className="ml-2">
                        {surveys.length}
                      </Badge>
                    )}
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="assessments" className="mt-6">
                  {assessments.length === 0 ? (
                    <Card>
                      <CardContent className="py-12 text-center">
                        <Globe className="mx-auto mb-4 h-12 w-12 text-(--muted-foreground)" />
                        <p className="text-lg font-medium">{t("noAssessments")}</p>
                      </CardContent>
                    </Card>
                  ) : (
                    <div className="space-y-6">
                      {categories.map((category) => (
                        <div key={category}>
                          <h3 className="mb-3 text-lg font-semibold">{category}</h3>
                          <div className="space-y-4">
                            {assessments
                              .filter((assessment) => assessment.category === category)
                              .map((assessment) => (
                                <AssessmentCard key={assessment.id} assessment={assessment} t={t} />
                              ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </TabsContent>

                <TabsContent value="surveys" className="mt-6">
                  {surveys.length === 0 ? (
                    <Card>
                      <CardContent className="py-12 text-center">
                        <ClipboardList className="mx-auto mb-4 h-12 w-12 text-(--muted-foreground)" />
                        <p className="text-lg font-medium">{t("noSurveys")}</p>
                      </CardContent>
                    </Card>
                  ) : (
                    <div className="space-y-4">
                      {surveys.map((survey) => (
                        <SurveyCard key={survey.id} survey={survey} onSubmit={handleSurveySubmit} t={t} />
                      ))}
                    </div>
                  )}
                </TabsContent>
              </Tabs>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}