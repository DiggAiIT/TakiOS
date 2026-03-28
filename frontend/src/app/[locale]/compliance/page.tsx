"use client";

import { type ReactNode, useEffect, useState } from "react";
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
import { type ComplianceRequirementData } from "@/lib/api-client";
import {
  useComplianceRequirements,
  useComplianceStatus,
  useCreateComplianceEvidence,
} from "@/hooks/use-compliance";
import { useAuthStore } from "@/stores/auth-store";
import {
  ShieldCheck,
  FileCheck,
  CheckCircle2,
  AlertTriangle,
  Plus,
  Filter,
} from "lucide-react";

function StatusCard({
  label,
  value,
  icon,
  accent,
}: {
  label: string;
  value: string | number;
  icon: ReactNode;
  accent?: string;
}) {
  return (
    <Card>
      <CardContent className="flex items-center gap-4 p-6">
        <div className={`rounded-lg p-3 ${accent || "bg-(--muted)"}`}>{icon}</div>
        <div>
          <p className="text-sm text-(--muted-foreground)">{label}</p>
          <p className="text-2xl font-bold">{value}</p>
        </div>
      </CardContent>
    </Card>
  );
}

function EvidenceForm({
  requirementId,
  onSubmit,
  onCancel,
  isSubmitting,
}: {
  requirementId: string;
  onSubmit: (data: { requirement_id: string; evidence_type: string; description: string }) => Promise<boolean>;
  onCancel: () => void;
  isSubmitting: boolean;
}) {
  const t = useTranslations("compliance");
  const tc = useTranslations("common");
  const [evidenceType, setEvidenceType] = useState("document");
  const [description, setDescription] = useState("");
  const types = ["document", "test", "review", "audit"] as const;

  const handleSubmit = async () => {
    const success = await onSubmit({
      requirement_id: requirementId,
      evidence_type: evidenceType,
      description,
    });

    if (success) {
      setDescription("");
    }
  };

  return (
    <div className="mt-3 space-y-3 rounded-lg border border-(--border) p-4">
      <div>
        <label className="mb-1 block text-sm font-medium">{t("evidenceType")}</label>
        <select
          value={evidenceType}
          aria-label={t("evidenceType")}
          title={t("evidenceType")}
          onChange={(event) => setEvidenceType(event.target.value)}
          className="w-full rounded-md border border-(--border) bg-(--background) p-2 text-sm"
        >
          {types.map((type) => (
            <option key={type} value={type}>
              {t(type)}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium">{t("evidenceDescription")}</label>
        <textarea
          value={description}
          title={t("evidenceDescription")}
          placeholder={t("evidenceDescription")}
          onChange={(event) => setDescription(event.target.value)}
          className="w-full rounded-md border border-(--border) bg-(--background) p-2 text-sm"
          rows={3}
        />
      </div>
      <div className="flex gap-2">
        <Button type="button" size="sm" disabled={isSubmitting || !description.trim()} onClick={() => void handleSubmit()}>
          {tc("submit")}
        </Button>
        <Button type="button" size="sm" variant="outline" onClick={onCancel}>
          {tc("cancel")}
        </Button>
      </div>
    </div>
  );
}

function RequirementCard({
  requirement,
  onAddEvidence,
  isSubmitting,
}: {
  requirement: ComplianceRequirementData;
  onAddEvidence: (data: { requirement_id: string; evidence_type: string; description: string }) => Promise<boolean>;
  isSubmitting: boolean;
}) {
  const t = useTranslations("compliance");
  const [showForm, setShowForm] = useState(false);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="text-sm font-medium">{requirement.title}</CardTitle>
            <CardDescription className="mt-1 text-xs">
              <Badge variant="secondary" className="mr-2">{requirement.framework}</Badge>
              {requirement.clause}
            </CardDescription>
          </div>
          <Badge variant="outline">{requirement.applies_to}</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <p className="mb-3 text-sm text-(--muted-foreground)">{requirement.description}</p>
        {!showForm ? (
          <Button type="button" size="sm" variant="outline" onClick={() => setShowForm(true)}>
            <Plus className="mr-1 h-4 w-4" />
            {t("addEvidence")}
          </Button>
        ) : (
          <EvidenceForm
            requirementId={requirement.id}
            isSubmitting={isSubmitting}
            onSubmit={async (data) => {
              const success = await onAddEvidence(data);
              if (success) {
                setShowForm(false);
              }
              return success;
            }}
            onCancel={() => setShowForm(false)}
          />
        )}
      </CardContent>
    </Card>
  );
}

export default function CompliancePage() {
  const t = useTranslations("compliance");
  const tc = useTranslations("common");
  const token = useAuthStore((state) => state.token);

  const [frameworkFilter, setFrameworkFilter] = useState("");
  const [actionError, setActionError] = useState<string | null>(null);
  const [flashMessage, setFlashMessage] = useState<string | null>(null);

  const requirementsQuery = useComplianceRequirements(token, frameworkFilter);
  const statusQuery = useComplianceStatus(token);
  const createEvidence = useCreateComplianceEvidence(token, frameworkFilter);

  useEffect(() => {
    if (!flashMessage) {
      return;
    }

    const timeoutId = window.setTimeout(() => setFlashMessage(null), 2500);
    return () => window.clearTimeout(timeoutId);
  }, [flashMessage]);

  const requirements = requirementsQuery.data ?? [];
  const status = statusQuery.data ?? null;

  const loading = token ? requirementsQuery.isLoading || statusQuery.isLoading : false;
  const queryError = requirementsQuery.error?.message || statusQuery.error?.message || null;
  const frameworks = [...new Set(requirements.map((requirement) => requirement.framework))];

  const retryLoad = () => {
    setActionError(null);
    void requirementsQuery.refetch();
    void statusQuery.refetch();
  };

  const handleAddEvidence = async (data: {
    requirement_id: string;
    evidence_type: string;
    description: string;
  }) => {
    if (!token) {
      return false;
    }

    try {
      setActionError(null);
      await createEvidence.mutateAsync(data);
      setFlashMessage(t("evidenceAdded"));
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
          <div className="mb-6 flex items-center justify-between gap-4">
            <div>
              <h2 className="text-3xl font-bold">{t("title")}</h2>
              <p className="text-(--muted-foreground)">{t("subtitle")}</p>
            </div>
            {flashMessage && <Badge variant="success">{flashMessage}</Badge>}
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

              <Tabs defaultValue="status">
                <TabsList>
                  <TabsTrigger value="status">
                    <ShieldCheck className="mr-1 h-4 w-4" />
                    {t("status")}
                  </TabsTrigger>
                  <TabsTrigger value="requirements">
                    <FileCheck className="mr-1 h-4 w-4" />
                    {t("requirements")}
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="status" className="mt-6">
                  {status && (
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                      <StatusCard label={t("totalRequirements")} value={status.total_requirements} icon={<ShieldCheck className="h-6 w-6" />} />
                      <StatusCard label={t("evidenced")} value={status.evidenced_requirements} icon={<FileCheck className="h-6 w-6 text-blue-700" />} accent="bg-blue-100" />
                      <StatusCard label={t("verified")} value={status.verified_requirements} icon={<CheckCircle2 className="h-6 w-6 text-green-600" />} accent="bg-green-100" />
                      <StatusCard
                        label={t("complianceRate")}
                        value={`${status.compliance_percentage.toFixed(1)}%`}
                        icon={status.compliance_percentage >= 80 ? <CheckCircle2 className="h-6 w-6 text-green-600" /> : <AlertTriangle className="h-6 w-6 text-amber-600" />}
                        accent={status.compliance_percentage >= 80 ? "bg-green-100" : "bg-amber-100"}
                      />
                    </div>
                  )}

                  {status && status.total_requirements > 0 && (
                    <Card className="mt-6">
                      <CardContent className="p-6">
                        <div className="mb-2 flex justify-between text-sm">
                          <span>{t("complianceRate")}</span>
                          <span className="font-medium">{status.compliance_percentage.toFixed(1)}%</span>
                        </div>
                        <progress
                          className="h-3 w-full accent-green-500"
                          max={100}
                          value={status.compliance_percentage}
                        />
                      </CardContent>
                    </Card>
                  )}
                </TabsContent>

                <TabsContent value="requirements" className="mt-6">
                  {frameworks.length > 1 && (
                    <div className="mb-4 flex items-center gap-2">
                      <Filter className="h-4 w-4 text-(--muted-foreground)" />
                      <select
                        value={frameworkFilter}
                        aria-label={t("framework")}
                        title={t("framework")}
                        onChange={(event) => setFrameworkFilter(event.target.value)}
                        className="rounded-md border border-(--border) bg-(--background) px-3 py-1.5 text-sm"
                      >
                        <option value="">{t("allFrameworks")}</option>
                        {frameworks.map((framework) => (
                          <option key={framework} value={framework}>
                            {framework}
                          </option>
                        ))}
                      </select>
                    </div>
                  )}

                  {requirements.length === 0 ? (
                    <Card>
                      <CardContent className="py-12 text-center">
                        <ShieldCheck className="mx-auto mb-4 h-12 w-12 text-(--muted-foreground)" />
                        <p className="text-lg font-medium">{t("noRequirements")}</p>
                      </CardContent>
                    </Card>
                  ) : (
                    <div className="space-y-4">
                      {requirements.map((requirement) => (
                        <RequirementCard
                          key={requirement.id}
                          requirement={requirement}
                          onAddEvidence={handleAddEvidence}
                          isSubmitting={createEvidence.isPending}
                        />
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