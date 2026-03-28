"use client";

import { type ElementType, useEffect, useState } from "react";
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
import { Skeleton } from "@/components/ui/skeleton";
import { type IOType } from "@/lib/api-client";
import {
  useIOCapabilities,
  useUpdateUserIOPreferences,
  useUpdateUserPreferences,
  useUserIOPreferences,
  useUserPreferences,
} from "@/hooks/use-settings";
import { useAuthStore } from "@/stores/auth-store";
import {
  Sun,
  Moon,
  Monitor,
  Eye,
  Zap,
  Type,
  Languages,
  Mic,
  Hand,
  FileText,
  MonitorSmartphone,
  Check,
} from "lucide-react";

// ── Theme Selector ──────────────────────────────────────────────

function ThemeSelector({
  value,
  onChange,
  t,
}: {
  value: string;
  onChange: (v: string) => void;
  t: (key: string) => string;
}) {
  const themes = [
    { key: "light", icon: Sun },
    { key: "dark", icon: Moon },
    { key: "system", icon: Monitor },
  ];

  return (
    <div className="flex gap-2">
      {themes.map(({ key, icon: Icon }) => (
        <button
          key={key}
          type="button"
          onClick={() => onChange(key)}
          className={`flex items-center gap-2 rounded-lg border px-4 py-2 text-sm transition-colors ${
            value === key
              ? "border-(--primary) bg-(--primary) text-white"
              : "border-(--border) hover:bg-(--accent)"
          }`}
        >
          <Icon className="h-4 w-4" />
          {t(key)}
        </button>
      ))}
    </div>
  );
}

// ── Toggle Switch ───────────────────────────────────────────────

function Toggle({
  checked,
  onChange,
  label,
}: {
  checked: boolean;
  onChange: (v: boolean) => void;
  label: string;
}) {
  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      onClick={() => onChange(!checked)}
      className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors ${
        checked ? "bg-(--primary)" : "bg-(--muted)"
      }`}
    >
      <span
        className={`pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow-sm transition-transform ${
          checked ? "translate-x-5" : "translate-x-0"
        }`}
      />
    </button>
  );
}

// ── Font Size Selector ──────────────────────────────────────────

function FontSizeSelector({
  value,
  onChange,
  t,
}: {
  value: number;
  onChange: (v: number) => void;
  t: (key: string) => string;
}) {
  const sizes = [
    { label: t("small"), value: 12 },
    { label: t("medium"), value: 16 },
    { label: t("large"), value: 20 },
    { label: t("extraLarge"), value: 24 },
  ];

  return (
    <div className="flex gap-2">
      {sizes.map((s) => (
        <button
          key={s.value}
          type="button"
          onClick={() => onChange(s.value)}
          className={`rounded-lg border px-4 py-2 text-sm transition-colors ${
            value === s.value
              ? "border-(--primary) bg-(--primary) text-white"
              : "border-(--border) hover:bg-(--accent)"
          }`}
        >
          {s.label}
        </button>
      ))}
    </div>
  );
}

// ── I/O Mode Selector ───────────────────────────────────────────

const IO_ICONS: Record<string, ElementType> = {
  voice: Mic,
  touch: Hand,
  text: FileText,
  visual: MonitorSmartphone,
};

function IOSelector({
  value,
  onChange,
  t,
}: {
  value: string;
  onChange: (v: string) => void;
  t: (key: string) => string;
}) {
  const modes = ["voice", "touch", "text", "visual"];

  return (
    <div className="flex gap-2">
      {modes.map((mode) => {
        const Icon = IO_ICONS[mode] || FileText;
        return (
          <button
            key={mode}
            type="button"
            onClick={() => onChange(mode)}
            className={`flex items-center gap-2 rounded-lg border px-4 py-2 text-sm transition-colors ${
              value === mode
                ? "border-(--primary) bg-(--primary) text-white"
                : "border-(--border) hover:bg-(--accent)"
            }`}
          >
            <Icon className="h-4 w-4" />
            {t(mode)}
          </button>
        );
      })}
    </div>
  );
}

// ── Main Page ───────────────────────────────────────────────────

export default function SettingsPage() {
  const t = useTranslations("settings");
  const tc = useTranslations("common");
  const token = useAuthStore((s) => s.token);

  const [saved, setSaved] = useState(false);

  const preferencesQuery = useUserPreferences(token);
  const capabilitiesQuery = useIOCapabilities(token);
  const ioPreferencesQuery = useUserIOPreferences(token);
  const updatePreferences = useUpdateUserPreferences(token);
  const updateIOPreferences = useUpdateUserIOPreferences(token);

  useEffect(() => {
    if (!saved) {
      return;
    }

    const timeoutId = window.setTimeout(() => setSaved(false), 2000);
    return () => window.clearTimeout(timeoutId);
  }, [saved]);

  const flashSaved = () => {
    setSaved(true);
  };

  const prefs = preferencesQuery.data ?? null;
  const capabilities = capabilitiesQuery.data ?? [];
  const inputMode = ioPreferencesQuery.data?.input_mode ?? "text";
  const outputMode = ioPreferencesQuery.data?.output_mode ?? "text";
  const loading = token
    ? preferencesQuery.isLoading || capabilitiesQuery.isLoading || ioPreferencesQuery.isLoading
    : false;
  const error =
    preferencesQuery.error?.message ||
    capabilitiesQuery.error?.message ||
    ioPreferencesQuery.error?.message ||
    updatePreferences.error?.message ||
    updateIOPreferences.error?.message ||
    null;

  const retryLoad = () => {
    void preferencesQuery.refetch();
    void capabilitiesQuery.refetch();
    void ioPreferencesQuery.refetch();
  };

  const updatePref = async (patch: {
    theme?: string;
    high_contrast?: boolean;
    reduced_motion?: boolean;
    font_size?: number;
    locale?: string;
  }) => {
    if (!token) {
      return;
    }

    await updatePreferences.mutateAsync(patch);
    flashSaved();
  };

  const updateIO = async (patch: { input_mode?: IOType; output_mode?: IOType }) => {
    if (!token) {
      return;
    }

    await updateIOPreferences.mutateAsync(patch);
    flashSaved();
  };

  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <Header />
        <main className="flex-1 overflow-y-auto p-8">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <h2 className="text-3xl font-bold">{t("title")}</h2>
              <p className="text-(--muted-foreground)">{t("subtitle")}</p>
            </div>
            {saved && (
              <Badge variant="success" className="flex items-center gap-1">
                <Check className="h-3 w-3" />
                {t("saved")}
              </Badge>
            )}
          </div>

          {loading && (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <Card key={i}>
                  <CardHeader>
                    <Skeleton className="h-6 w-48" />
                    <Skeleton className="h-4 w-80" />
                  </CardHeader>
                </Card>
              ))}
            </div>
          )}

          {error && (
            <Card>
              <CardContent className="py-8 text-center">
                <p className="text-(--destructive)">{error}</p>
                <Button
                  type="button"
                  variant="outline"
                  className="mt-4"
                  onClick={retryLoad}
                >
                  {tc("retry")}
                </Button>
              </CardContent>
            </Card>
          )}

          {!loading && !error && (
            <div className="space-y-6">
              {/* Appearance */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Sun className="h-5 w-5" />
                    {t("appearance")}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Theme */}
                  <div>
                    <label className="mb-2 block text-sm font-medium">
                      {t("theme")}
                    </label>
                    <ThemeSelector
                      value={prefs?.theme || "system"}
                      onChange={(v) => updatePref({ theme: v })}
                      t={t}
                    />
                  </div>

                  {/* High Contrast */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Eye className="h-4 w-4 text-(--muted-foreground)" />
                      <div>
                        <p className="text-sm font-medium">{t("highContrast")}</p>
                        <p className="text-xs text-(--muted-foreground)">
                          {t("highContrastDesc")}
                        </p>
                      </div>
                    </div>
                    <Toggle
                      checked={prefs?.high_contrast || false}
                      label={t("highContrast")}
                      onChange={(v) => updatePref({ high_contrast: v })}
                    />
                  </div>

                  {/* Reduced Motion */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Zap className="h-4 w-4 text-(--muted-foreground)" />
                      <div>
                        <p className="text-sm font-medium">{t("reducedMotion")}</p>
                        <p className="text-xs text-(--muted-foreground)">
                          {t("reducedMotionDesc")}
                        </p>
                      </div>
                    </div>
                    <Toggle
                      checked={prefs?.reduced_motion || false}
                      label={t("reducedMotion")}
                      onChange={(v) => updatePref({ reduced_motion: v })}
                    />
                  </div>

                  {/* Font Size */}
                  <div>
                    <div className="mb-2 flex items-center gap-2">
                      <Type className="h-4 w-4 text-(--muted-foreground)" />
                      <label className="text-sm font-medium">{t("fontSize")}</label>
                    </div>
                    <p className="mb-2 text-xs text-(--muted-foreground)">
                      {t("fontSizeDesc")}
                    </p>
                    <FontSizeSelector
                      value={prefs?.font_size || 16}
                      onChange={(v) => updatePref({ font_size: v })}
                      t={t}
                    />
                  </div>

                  {/* Language */}
                  <div>
                    <div className="mb-2 flex items-center gap-2">
                      <Languages className="h-4 w-4 text-(--muted-foreground)" />
                      <label className="text-sm font-medium">{t("language")}</label>
                    </div>
                    <p className="mb-2 text-xs text-(--muted-foreground)">
                      {t("languageDesc")}
                    </p>
                    <div className="flex gap-2">
                      {["en", "de"].map((loc) => (
                        <button
                          key={loc}
                          type="button"
                          onClick={() => updatePref({ locale: loc })}
                          className={`rounded-lg border px-4 py-2 text-sm transition-colors ${
                            (prefs?.locale || "en") === loc
                              ? "border-(--primary) bg-(--primary) text-white"
                              : "border-(--border) hover:bg-(--accent)"
                          }`}
                        >
                          {loc === "en" ? tc("english") : tc("german")}
                        </button>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Interaction / I/O */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Mic className="h-5 w-5" />
                    {t("interaction")}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div>
                    <label className="mb-2 block text-sm font-medium">
                      {t("inputMode")}
                    </label>
                    <IOSelector
                      value={inputMode}
                      onChange={(v) => void updateIO({ input_mode: v as IOType })}
                      t={t}
                    />
                  </div>

                  <div>
                    <label className="mb-2 block text-sm font-medium">
                      {t("outputMode")}
                    </label>
                    <IOSelector
                      value={outputMode}
                      onChange={(v) => void updateIO({ output_mode: v as IOType })}
                      t={t}
                    />
                  </div>

                  {/* Available capabilities */}
                  {capabilities.length > 0 && (
                    <div>
                      <label className="mb-2 block text-sm font-medium">
                        {t("ioCapabilities")}
                      </label>
                      <div className="flex flex-wrap gap-2">
                        {capabilities.map((cap) => (
                          <Badge
                            key={cap.id}
                            variant={cap.enabled ? "success" : "secondary"}
                          >
                            {cap.name} ({cap.type})
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
