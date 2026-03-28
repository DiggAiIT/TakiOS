"use client";

import { useState } from "react";
import { useTranslations, useLocale } from "next-intl";
import { useParams } from "next/navigation";
import { Link } from "@/i18n/navigation";
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
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { ApiError, type MnemonicData } from "@/lib/api-client";
import { useGenerateMnemonic, useRateMnemonic, useUnitContent } from "@/hooks/use-content";
import { useAuthStore } from "@/stores/auth-store";
import {
  ArrowLeft,
  BookOpen,
  Lightbulb,
  Sparkles,
  Star,
} from "lucide-react";

const MNEMONIC_TYPES = ["acronym", "story", "visual", "rhyme", "analogy"] as const;

export default function LearnUnitPage() {
  const t = useTranslations("learn");
  const te = useTranslations("eselsbruecke");
  const tc = useTranslations("common");
  const locale = useLocale();
  const params = useParams();
  const unitId = params.unitId as string;
  const token = useAuthStore((s) => s.token);
  const [error, setError] = useState<string | null>(null);
  const [selectedType, setSelectedType] = useState<string>("analogy");
  const contentQuery = useUnitContent(token, unitId);
  const generateMnemonic = useGenerateMnemonic(token, unitId);
  const rateMnemonic = useRateMnemonic(token, unitId);
  const data = contentQuery.data ?? null;
  const loading = contentQuery.isLoading;
  const generating = generateMnemonic.isPending;

  async function handleGenerate() {
    if (!token || !data) return;
    try {
      setError(null);
      await generateMnemonic.mutateAsync({
        contentId: data.id,
        mnemonicType: selectedType,
        language: locale,
      });
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Generation failed");
    }
  }

  async function handleRate(mnemonicId: string, score: number) {
    if (!token) return;
    try {
      setError(null);
      await rateMnemonic.mutateAsync({ mnemonicId, score });
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Rating failed");
    }
  }

  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <Header />
        <main className="flex-1 overflow-y-auto p-8">
          <Link
            href="/learn"
            className="mb-4 inline-flex items-center gap-1 text-sm text-(--muted-foreground) hover:text-(--foreground)"
          >
            <ArrowLeft className="h-4 w-4" />
            {t("backToModule")}
          </Link>

          {loading && (
            <div className="space-y-4">
              <Skeleton className="h-8 w-64" />
              <Skeleton className="h-96 w-full" />
            </div>
          )}

          {((contentQuery.error && !data) || (error && !data)) && (
            <Card>
              <CardContent className="py-8 text-center">
                <p className="text-(--destructive)">{error ?? contentQuery.error?.detail}</p>
                <Button
                  type="button"
                  variant="outline"
                  className="mt-4"
                  onClick={() => void contentQuery.refetch()}
                >
                  {tc("retry")}
                </Button>
              </CardContent>
            </Card>
          )}

          {data && (
            <Tabs defaultValue="content">
              <TabsList>
                <TabsTrigger value="content">
                  <BookOpen className="mr-2 h-4 w-4" />
                  {t("content")}
                </TabsTrigger>
                <TabsTrigger value="mnemonics">
                  <Lightbulb className="mr-2 h-4 w-4" />
                  {t("mnemonics")} ({data.mnemonics.length})
                </TabsTrigger>
              </TabsList>

              {/* Content Tab */}
              <TabsContent value="content">
                <Card>
                  <CardContent className="prose prose-sm max-w-none py-6 dark:prose-invert">
                    {data.body_markdown ? (
                      <MarkdownRenderer content={data.body_markdown} />
                    ) : (
                      <p className="text-(--muted-foreground)">
                        {t("noContent")}
                      </p>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Mnemonics Tab */}
              <TabsContent value="mnemonics">
                <div className="space-y-4">
                  {/* Generator */}
                  <Card className="border-(--primary)/30">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Sparkles className="h-5 w-5 text-(--primary)" />
                        {te("generate")}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex flex-wrap items-end gap-3">
                        <div>
                          <label className="mb-1 block text-sm font-medium">
                            {te("type")}
                          </label>
                          <div className="flex gap-1">
                            {MNEMONIC_TYPES.map((type) => (
                              <Button
                                key={type}
                                variant={
                                  selectedType === type ? "default" : "outline"
                                }
                                size="sm"
                                onClick={() => setSelectedType(type)}
                              >
                                {te(type)}
                              </Button>
                            ))}
                          </div>
                        </div>
                        <Button
                          onClick={handleGenerate}
                          disabled={generating}
                        >
                          <Sparkles className="mr-2 h-4 w-4" />
                          {generating ? te("generating") : te("generate")}
                        </Button>
                      </div>
                      {error && data && (
                        <p className="mt-4 text-sm text-(--destructive)">{error}</p>
                      )}
                    </CardContent>
                  </Card>

                  {/* Existing Mnemonics */}
                  {data.mnemonics.length === 0 ? (
                    <Card>
                      <CardContent className="py-12 text-center">
                        <Lightbulb className="mx-auto mb-4 h-12 w-12 text-(--muted-foreground)" />
                        <p className="font-medium">{te("noMnemonics")}</p>
                        <p className="text-sm text-(--muted-foreground)">
                          {te("generateFirst")}
                        </p>
                      </CardContent>
                    </Card>
                  ) : (
                    data.mnemonics.map((mnemonic) => (
                      <MnemonicCard
                        key={mnemonic.id}
                        mnemonic={mnemonic}
                        te={te}
                        onRate={(score) => void handleRate(mnemonic.id, score)}
                      />
                    ))
                  )}
                </div>
              </TabsContent>
            </Tabs>
          )}
        </main>
      </div>
    </div>
  );
}

// ── Simple Markdown Renderer ──────────────────────────────────────

function MarkdownRenderer({ content: md }: { content: string }) {
  // Convert markdown to simple HTML for display
  const html = md
    // Headers
    .replace(/^### (.+)$/gm, '<h3 class="text-lg font-semibold mt-6 mb-2">$1</h3>')
    .replace(/^## (.+)$/gm, '<h2 class="text-xl font-bold mt-8 mb-3">$1</h2>')
    .replace(/^# (.+)$/gm, '<h1 class="text-2xl font-bold mt-4 mb-4">$1</h1>')
    // Bold & italic
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    // Inline code
    .replace(/`([^`]+)`/g, '<code class="rounded bg-(--muted) px-1.5 py-0.5 text-sm font-mono">$1</code>')
    // Code blocks
    .replace(
      /```(\w+)?\n([\s\S]*?)```/g,
      '<pre class="overflow-x-auto rounded-lg bg-(--muted) p-4 my-4"><code class="text-sm font-mono">$2</code></pre>'
    )
    // Tables
    .replace(
      /\|(.+)\|\n\|[-| ]+\|\n((?:\|.+\|\n?)*)/g,
      (_match, header: string, body: string) => {
        const headers = header
          .split("|")
          .map((h: string) => h.trim())
          .filter(Boolean);
        const rows = body
          .trim()
          .split("\n")
          .map((row: string) =>
            row
              .split("|")
              .map((c: string) => c.trim())
              .filter(Boolean)
          );
        return `<div class="overflow-x-auto my-4"><table class="min-w-full border-collapse border border-(--border)">
          <thead><tr>${headers.map((h: string) => `<th class="border border-(--border) bg-(--muted) px-3 py-2 text-left text-sm font-semibold">${h}</th>`).join("")}</tr></thead>
          <tbody>${rows.map((row: string[]) => `<tr>${row.map((c: string) => `<td class="border border-(--border) px-3 py-2 text-sm">${c}</td>`).join("")}</tr>`).join("")}</tbody>
        </table></div>`;
      }
    )
    // Unordered lists
    .replace(/^- (.+)$/gm, '<li class="ml-4 list-disc text-sm leading-relaxed">$1</li>')
    // Ordered lists
    .replace(/^\d+\. (.+)$/gm, '<li class="ml-4 list-decimal text-sm leading-relaxed">$1</li>')
    // Math (display as-is with styled block)
    .replace(
      /\$\$(.+?)\$\$/g,
      '<div class="my-2 rounded bg-(--muted) px-4 py-2 text-center font-mono text-sm">$1</div>'
    )
    .replace(
      /\$(.+?)\$/g,
      '<span class="font-mono text-sm bg-(--muted) px-1 rounded">$1</span>'
    )
    // Paragraphs (double newlines)
    .replace(/\n\n/g, '</p><p class="my-2 text-sm leading-relaxed">')
    // Single newlines in non-list context
    .replace(/\n(?!<)/g, "<br/>");

  return (
    <div
      className="leading-relaxed"
      dangerouslySetInnerHTML={{ __html: `<p class="my-2 text-sm leading-relaxed">${html}</p>` }}
    />
  );
}

// ── Mnemonic Card ─────────────────────────────────────────────────

function MnemonicCard({
  mnemonic,
  te,
  onRate,
}: {
  mnemonic: MnemonicData;
  te: (key: string) => string;
  onRate: (score: number) => void;
}) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <Badge variant={mnemonic.ai_generated ? "default" : "secondary"}>
            {mnemonic.ai_generated ? te("aiGenerated") : "Manual"}
          </Badge>
          <Badge variant="outline">{te(mnemonic.mnemonic_type)}</Badge>
          <Badge variant="outline">{mnemonic.language.toUpperCase()}</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <p className="whitespace-pre-wrap text-sm leading-relaxed">
          {mnemonic.mnemonic_text}
        </p>

        <Separator className="my-4" />

        <div className="flex items-center justify-between">
          <span className="text-sm text-(--muted-foreground)">
            {te("effectiveness")}:{" "}
            {mnemonic.effectiveness_score
              ? `${mnemonic.effectiveness_score}/5`
              : "—"}
          </span>
          <div className="flex gap-1">
            {[1, 2, 3, 4, 5].map((score) => (
              <button
                key={score}
                onClick={() => onRate(score)}
                className="rounded p-1 transition-colors hover:bg-(--accent)"
                aria-label={`${te("rate")} ${score}/5`}
              >
                <Star
                  className={`h-4 w-4 ${
                    mnemonic.effectiveness_score &&
                    score <= mnemonic.effectiveness_score
                      ? "fill-yellow-400 text-yellow-400"
                      : "text-(--muted-foreground)"
                  }`}
                />
              </button>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
