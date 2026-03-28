"use client";

import { useLocale, useTranslations } from "next-intl";
import { useRouter, usePathname } from "@/i18n/navigation";
import { Button } from "@/components/ui/button";

export function LocaleSwitcher() {
  const t = useTranslations("common");
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  const switchLocale = () => {
    const newLocale = locale === "de" ? "en" : "de";
    router.replace(pathname, { locale: newLocale });
  };

  return (
    <Button variant="ghost" size="sm" onClick={switchLocale} aria-label={t("language")}>
      {locale === "de" ? "EN" : "DE"}
    </Button>
  );
}
