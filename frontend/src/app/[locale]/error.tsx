"use client";

import { useTranslations } from "next-intl";
import { useEffect } from "react";
import { AlertTriangle, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

export default function ErrorPage({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const t = useTranslations("errors");

  useEffect(() => {
    console.error("[TakiOS] Page error:", error);
  }, [error]);

  return (
    <div className="flex min-h-screen items-center justify-center p-6">
      <Card className="w-full max-w-md">
        <CardContent className="pt-8 pb-6 text-center">
          <AlertTriangle className="mx-auto mb-4 h-12 w-12 text-amber-500" />
          <h2 className="mb-2 text-xl font-semibold">{t("title")}</h2>
          <p className="mb-6 text-sm text-(--muted-foreground)">{t("description")}</p>
          <Button type="button" onClick={reset} className="gap-2">
            <RotateCcw className="h-4 w-4" />
            {t("tryAgain")}
          </Button>
          {error.digest && (
            <p className="mt-4 text-xs text-(--muted-foreground)">
              {t("errorId")}: {error.digest}
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
