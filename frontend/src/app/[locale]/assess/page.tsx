"use client";

import { useState } from "react";
import { useSearchParams } from "next/navigation";
import { useTranslations, useLocale } from "next-intl";
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
import { Select } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { Progress } from "@/components/ui/progress";
import { useExams, useStartExam, useSubmitExam } from "@/hooks/use-assessment";
import { useSubjectsWithModules } from "@/hooks/use-modules";
import {
  type QuestionData,
  type ExamResultData,
  type StartExamData,
  ApiError,
} from "@/lib/api-client";
import { useAuthStore } from "@/stores/auth-store";
import {
  ClipboardCheck,
  Clock,
  ChevronRight,
  ChevronLeft,
  CheckCircle2,
  XCircle,
  ArrowLeft,
} from "lucide-react";

type Phase = "browse" | "exam" | "result";

export default function AssessPage() {
  const t = useTranslations("assessment");
  const tc = useTranslations("common");
  const locale = useLocale();
  const searchParams = useSearchParams();
  const preselectedModule = searchParams.get("module");
  const token = useAuthStore((s) => s.token);

  // Browse state
  const [selectedModuleId, setSelectedModuleId] = useState<string>(preselectedModule || "");

  // Exam state
  const [phase, setPhase] = useState<Phase>("browse");
  const [examData, setExamData] = useState<StartExamData | null>(null);
  const [currentQ, setCurrentQ] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [error, setError] = useState<string | null>(null);

  // Result state
  const [result, setResult] = useState<ExamResultData | null>(null);

  const modulesQuery = useSubjectsWithModules(token);
  const examsQuery = useExams(token, selectedModuleId || null);
  const startExamMutation = useStartExam(token);
  const submitExamMutation = useSubmitExam(token);
  const allModules = Object.values(modulesQuery.data?.modulesBySubject ?? {}).flat();
  const loading = modulesQuery.isLoading;
  const loadingExams = examsQuery.isLoading;
  const exams = examsQuery.data ?? [];
  const n = (obj: { name_de: string; name_en: string }) =>
    locale === "de" ? obj.name_de : obj.name_en;

  async function handleStart(examId: string) {
    if (!token) return;
    try {
      setError(null);
      const data = await startExamMutation.mutateAsync({ examId });
      setExamData(data);
      setCurrentQ(0);
      setAnswers({});
      setPhase("exam");
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Failed to start exam");
    }
  }

  async function handleSubmit() {
    if (!token || !examData) return;
    const unanswered = examData.questions.length - Object.keys(answers).length;
    if (unanswered > 0) {
      if (!confirm(`${unanswered} ${t("unanswered")}. ${t("confirmSubmit")}`)) return;
    }
    try {
      setError(null);
      const answerList = examData.questions.map((q) => ({
        question_id: q.id,
        answer_data: { answer: answers[q.id] || "" },
      }));
      const res = await submitExamMutation.mutateAsync({
        attemptId: examData.attempt_id,
        answers: answerList,
      });
      setResult(res);
      setPhase("result");
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Submit failed");
    }
  }

  // ── Browse Phase ──

  if (phase === "browse") {
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

            {loading ? (
              <div className="space-y-4">
                <Skeleton className="h-10 w-64" />
                <Skeleton className="h-48 w-full" />
              </div>
            ) : (
              <>
                <Select
                  label={t("selectModule")}
                  value={selectedModuleId}
                  onChange={(e) => setSelectedModuleId(e.target.value)}
                  className="mb-6 max-w-md"
                >
                  <option value="">-- {t("selectModule")} --</option>
                  {allModules.map((mod) => (
                    <option key={mod.id} value={mod.id}>
                      {mod.code} — {n(mod)}
                    </option>
                  ))}
                </Select>

                {modulesQuery.error && (
                  <Card className="mb-6">
                    <CardContent className="py-6 text-center">
                      <p className="text-(--destructive)">{modulesQuery.error.detail}</p>
                      <Button type="button" variant="outline" className="mt-4" onClick={() => void modulesQuery.refetch()}>
                        {tc("retry")}
                      </Button>
                    </CardContent>
                  </Card>
                )}

                {loadingExams && <Skeleton className="h-32 w-full" />}

                {error && (
                  <Card className="mb-6">
                    <CardContent className="py-6 text-center">
                      <p className="text-(--destructive)">{error}</p>
                    </CardContent>
                  </Card>
                )}

                {examsQuery.error && selectedModuleId && (
                  <Card className="mb-6">
                    <CardContent className="py-6 text-center">
                      <p className="text-(--destructive)">{examsQuery.error.detail}</p>
                      <Button type="button" variant="outline" className="mt-4" onClick={() => void examsQuery.refetch()}>
                        {tc("retry")}
                      </Button>
                    </CardContent>
                  </Card>
                )}

                {!loadingExams && selectedModuleId && exams.length === 0 && (
                  <Card>
                    <CardContent className="py-12 text-center">
                      <ClipboardCheck className="mx-auto mb-4 h-12 w-12 text-(--muted-foreground)" />
                      <p className="text-(--muted-foreground)">{t("noExams")}</p>
                    </CardContent>
                  </Card>
                )}

                {exams.length > 0 && (
                  <div className="space-y-3">
                    {exams.map((exam) => (
                      <Card key={exam.id}>
                        <CardContent className="flex items-center justify-between py-4">
                          <div>
                            <h3 className="font-semibold">{exam.title}</h3>
                            <div className="mt-1 flex items-center gap-2">
                              <Badge variant="outline">
                                {t(exam.exam_type === "pen_and_paper" ? "penAndPaper" : exam.exam_type)}
                              </Badge>
                              {exam.time_limit_minutes && (
                                <span className="flex items-center gap-1 text-xs text-(--muted-foreground)">
                                  <Clock className="h-3 w-3" />
                                  {exam.time_limit_minutes} {t("minutes")}
                                </span>
                              )}
                            </div>
                          </div>
                          <Button onClick={() => handleStart(exam.id)} disabled={startExamMutation.isPending}>
                            <ClipboardCheck className="mr-2 h-4 w-4" />
                            {t("startExam")}
                          </Button>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </>
            )}
          </main>
        </div>
      </div>
    );
  }

  // ── Exam Phase ──

  if (phase === "exam" && examData) {
    const question = examData.questions[currentQ];
    const total = examData.questions.length;
    const answered = Object.keys(answers).length;

    return (
      <div className="flex h-screen">
        <Sidebar />
        <div className="flex flex-1 flex-col">
          <Header />
          <main className="flex-1 overflow-y-auto p-8">
            {/* Progress */}
            <div className="mb-6">
              <div className="mb-2 flex items-center justify-between text-sm">
                <span>
                  {t("question")} {currentQ + 1} {t("of")} {total}
                </span>
                <span className="text-(--muted-foreground)">
                  {answered}/{total} {t("answered")}
                </span>
              </div>
              <Progress value={answered} max={total} />
            </div>

            {error && (
              <Card className="mb-6">
                <CardContent className="py-4 text-center">
                  <p className="text-(--destructive)">{error}</p>
                </CardContent>
              </Card>
            )}

            {/* Question Card */}
            <Card className="mb-6">
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Badge>{t("question")} {currentQ + 1}</Badge>
                  <Badge variant="outline">{t(question.difficulty)}</Badge>
                </div>
                <CardTitle className="mt-2 text-lg">
                  {locale === "de" ? question.question_de : question.question_en}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <QuestionInput
                  question={question}
                  value={answers[question.id] || ""}
                  onChange={(val) =>
                    setAnswers((prev) => ({ ...prev, [question.id]: val }))
                  }
                />
              </CardContent>
            </Card>

            {/* Navigation */}
            <div className="flex items-center justify-between">
              <Button
                variant="outline"
                onClick={() => setCurrentQ((q) => Math.max(0, q - 1))}
                disabled={currentQ === 0}
              >
                <ChevronLeft className="mr-2 h-4 w-4" />
                {t("previousQuestion")}
              </Button>

              {currentQ < total - 1 ? (
                <Button onClick={() => setCurrentQ((q) => q + 1)}>
                  {t("nextQuestion")}
                  <ChevronRight className="ml-2 h-4 w-4" />
                </Button>
              ) : (
                <Button onClick={handleSubmit} disabled={submitExamMutation.isPending}>
                  <ClipboardCheck className="mr-2 h-4 w-4" />
                  {submitExamMutation.isPending ? tc("loading") : t("submitExam")}
                </Button>
              )}
            </div>

            {/* Question dots */}
            <div className="mt-6 flex flex-wrap gap-2">
              {examData.questions.map((q, i) => (
                <button
                  type="button"
                  key={q.id}
                  onClick={() => setCurrentQ(i)}
                  className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-medium transition-colors ${
                    i === currentQ
                      ? "bg-(--primary) text-(--primary-foreground)"
                      : answers[q.id]
                        ? "bg-emerald-500/20 text-emerald-700"
                        : "bg-(--muted) text-(--muted-foreground)"
                  }`}
                >
                  {i + 1}
                </button>
              ))}
            </div>
          </main>
        </div>
      </div>
    );
  }

  // ── Result Phase ──

  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <Header />
        <main className="flex-1 overflow-y-auto p-8">
          {result && (
            <div className="mx-auto max-w-lg">
              <Card>
                <CardContent className="py-12 text-center">
                  {result.passed ? (
                    <>
                      <CheckCircle2 className="mx-auto mb-4 h-16 w-16 text-emerald-500" />
                      <h2 className="text-2xl font-bold text-emerald-600">
                        {t("congratulations")}
                      </h2>
                      <Badge variant="success" className="mt-2 text-lg">
                        {t("passed")}
                      </Badge>
                    </>
                  ) : (
                    <>
                      <XCircle className="mx-auto mb-4 h-16 w-16 text-red-500" />
                      <h2 className="text-2xl font-bold text-red-600">
                        {t("tryAgain")}
                      </h2>
                      <Badge variant="destructive" className="mt-2 text-lg">
                        {t("failed")}
                      </Badge>
                    </>
                  )}

                  <div className="mt-8">
                    <p className="text-sm text-(--muted-foreground)">
                      {t("yourScore")}
                    </p>
                    <p className="text-5xl font-bold">
                      {result.total_score?.toFixed(0) ?? 0}%
                    </p>
                    <Progress
                      value={result.total_score ?? 0}
                      max={100}
                      className="mx-auto mt-4 max-w-xs"
                    />
                  </div>

                  <div className="mt-8 flex justify-center gap-3">
                    <Button
                      variant="outline"
                      onClick={() => {
                        setPhase("browse");
                        setResult(null);
                        setExamData(null);
                      }}
                    >
                      <ArrowLeft className="mr-2 h-4 w-4" />
                      {t("backToExams")}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

// ── Question Input Component ──────────────────────────────────────

function QuestionInput({
  question,
  value,
  onChange,
}: {
  question: QuestionData;
  value: string;
  onChange: (val: string) => void;
}) {
  const t = useTranslations("assessment");
  if (question.question_type === "multiple_choice" && question.answer_options?.options) {
    return (
      <div className="space-y-2">
        {question.answer_options.options.map((option) => (
          <label
            key={option}
            className={`flex cursor-pointer items-center gap-3 rounded-lg border p-3 transition-colors ${
              value === option
                ? "border-(--primary) bg-(--primary)/5"
                : "border-(--border) hover:bg-(--accent)"
            }`}
          >
            <input
              type="radio"
              name={question.id}
              value={option}
              checked={value === option}
              onChange={() => onChange(option)}
              className="h-4 w-4 accent-(--primary)"
            />
            <span className="text-sm">{option}</span>
          </label>
        ))}
      </div>
    );
  }

  // Free text
  return (
    <textarea
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={t("yourAnswer")}
      className="min-h-30 w-full rounded-md border border-(--input) bg-(--background) px-3 py-2 text-sm ring-offset-(--background) focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-(--ring)"
    />
  );
}
