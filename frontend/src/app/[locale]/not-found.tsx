"use client";

import { useTranslations } from "next-intl";
import { FileQuestion, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useRouter } from "next/navigation";

export default function NotFoundPage() {
  const t = useTranslations("errors");
  const router = useRouter();

  return (
    <div className="flex min-h-screen items-center justify-center p-6">
      <Card className="w-full max-w-md">
        <CardContent className="pt-8 pb-6 text-center">
          <FileQuestion className="mx-auto mb-4 h-12 w-12 text-(--muted-foreground)" />
          <h2 className="mb-2 text-xl font-semibold">{t("notFoundTitle")}</h2>
          <p className="mb-6 text-sm text-(--muted-foreground)">{t("notFoundDescription")}</p>
          <Button type="button" onClick={() => router.back()} variant="outline" className="gap-2">
            <ArrowLeft className="h-4 w-4" />
            {t("goBack")}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
