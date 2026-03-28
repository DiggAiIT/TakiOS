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
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import {
  ApiError,
  type ProjectStatus,
  type MilestoneData,
} from "@/lib/api-client";
import {
  useAddMilestone,
  useCreateProject,
  useDeleteMilestone,
  useProjectDetail,
  useProjectsList,
  useUpdateMilestone,
  useUpdateProject,
  useUploadArtifact,
} from "@/hooks/use-projects";
import { useAuthStore } from "@/stores/auth-store";
import {
  FolderOpen,
  Plus,
  ArrowLeft,
  CheckCircle2,
  Circle,
  Trash2,
  FileUp,
  Rocket,
  ChevronRight,
} from "lucide-react";

// ── Status & Stage Helpers ─────────────────────────────────────────

const STATUS_COLORS: Record<ProjectStatus, string> = {
  draft: "bg-gray-100 text-gray-800",
  active: "bg-blue-100 text-blue-800",
  review: "bg-amber-100 text-amber-800",
  completed: "bg-green-100 text-green-800",
  archived: "bg-slate-100 text-slate-600",
};

const STAGE_ICONS: Record<string, string> = {
  idea: "💡",
  concept: "📐",
  mvp: "🚀",
  "2d": "📊",
  "3d": "🧊",
  real_world: "🏭",
  lifecycle: "♻️",
};

// ── Create Dialog ──────────────────────────────────────────────────

function CreateProjectDialog({
  onCreated,
  onCancel,
}: {
  onCreated: (projectId: string) => void;
  onCancel: () => void;
}) {
  const t = useTranslations("projects");
  const tc = useTranslations("common");
  const token = useAuthStore((s) => s.token);
  const createProject = useCreateProject(token);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token || !title.trim()) return;
    try {
      setError(null);
      const project = await createProject.mutateAsync({ title: title.trim(), description });
      onCreated(project.id);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : tc("error"));
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("createProject")}</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium">
              {t("projectTitle")}
            </label>
            <Input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder={t("projectTitle")}
              required
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">
              {t("projectDescription")}
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder={t("projectDescription")}
              className="w-full rounded-md border border-(--border) bg-(--background) p-2 text-sm"
              rows={3}
            />
          </div>
          {error && <p className="text-sm text-(--destructive)">{error}</p>}
          <div className="flex gap-2">
            <Button type="submit" disabled={createProject.isPending || !title.trim()}>
              {createProject.isPending ? tc("loading") : tc("save")}
            </Button>
            <Button type="button" variant="outline" onClick={onCancel}>
              {tc("cancel")}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}

// ── Milestone Item ─────────────────────────────────────────────────

function MilestoneItem({
  milestone,
  onToggle,
  onDelete,
}: {
  milestone: MilestoneData;
  onToggle: () => void;
  onDelete: () => void;
}) {
  return (
    <div className="flex items-center gap-3 rounded-lg border border-(--border) p-3">
      <button type="button" onClick={onToggle} className="shrink-0" aria-label={milestone.completed ? "Mark as open" : "Mark as completed"} title={milestone.completed ? "Mark as open" : "Mark as completed"}>
        {milestone.completed ? (
          <CheckCircle2 className="h-5 w-5 text-green-600" />
        ) : (
          <Circle className="h-5 w-5 text-(--muted-foreground)" />
        )}
      </button>
      <div className="min-w-0 flex-1">
        <p
          className={`text-sm font-medium ${
            milestone.completed ? "text-(--muted-foreground) line-through" : ""
          }`}
        >
          {milestone.title}
        </p>
        {milestone.description && (
          <p className="text-xs text-(--muted-foreground)">
            {milestone.description}
          </p>
        )}
      </div>
      <button
        type="button"
        onClick={onDelete}
        className="shrink-0 text-(--muted-foreground) hover:text-(--destructive)"
        aria-label="Delete milestone"
        title="Delete milestone"
      >
        <Trash2 className="h-4 w-4" />
      </button>
    </div>
  );
}

// ── Project Detail ─────────────────────────────────────────────────

function ProjectDetail({
  projectId,
  onBack,
}: {
  projectId: string;
  onBack: () => void;
}) {
  const t = useTranslations("projects");
  const tc = useTranslations("common");
  const token = useAuthStore((s) => s.token);
  const projectQuery = useProjectDetail(token, projectId);
  const updateProject = useUpdateProject(token, projectId);
  const addMilestone = useAddMilestone(token, projectId);
  const updateMilestone = useUpdateMilestone(token, projectId);
  const deleteMilestone = useDeleteMilestone(token, projectId);
  const uploadArtifact = useUploadArtifact(token, projectId);
  const [newMilestone, setNewMilestone] = useState("");
  const [artifactError, setArtifactError] = useState<string | null>(null);
  const project = projectQuery.data ?? null;
  const loading = projectQuery.isLoading;

  const handleAddMilestone = async () => {
    if (!token || !newMilestone.trim()) return;
    try {
      await addMilestone.mutateAsync({ title: newMilestone.trim() });
      setNewMilestone("");
    } catch {
      // visible retry path lives on the detail card state
    }
  };

  const handleToggleMilestone = async (m: MilestoneData) => {
    if (!token) return;
    await updateMilestone.mutateAsync({ milestoneId: m.id, completed: !m.completed });
  };

  const handleDeleteMilestone = async (m: MilestoneData) => {
    if (!token) return;
    await deleteMilestone.mutateAsync({ milestoneId: m.id });
  };

  const handleStatusChange = async (status: ProjectStatus) => {
    if (!token) return;
    await updateProject.mutateAsync({ status });
  };

  const handleArtifactChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (file.size > 10 * 1024 * 1024) {
      setArtifactError(t("maxFileSize"));
      event.target.value = "";
      return;
    }

    try {
      setArtifactError(null);
      await uploadArtifact.mutateAsync({ file });
      event.target.value = "";
    } catch (err) {
      setArtifactError(err instanceof ApiError ? err.detail : t("uploadFailed"));
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-40 w-full" />
      </div>
    );
  }

  if (!project) {
    return (
      <Card>
        <CardContent className="py-8 text-center">
          <p>{projectQuery.error?.detail ?? tc("noData")}</p>
          <Button type="button" variant="outline" className="mt-4" onClick={() => void projectQuery.refetch()}>
            {tc("retry")}
          </Button>
        </CardContent>
      </Card>
    );
  }

  const completedMilestones = project.milestones.filter((m) => m.completed).length;
  const totalMilestones = project.milestones.length;
  const progressPct = totalMilestones > 0 ? Math.round((completedMilestones / totalMilestones) * 100) : 0;

  const statusKey = project.status as string;
  const stageKey = project.realization_stage === "2d"
    ? "prototype2d"
    : project.realization_stage === "3d"
    ? "prototype3d"
    : project.realization_stage === "real_world"
    ? "realWorld"
    : project.realization_stage;

  return (
    <div className="space-y-6">
      {/* Back + Header */}
      <button
        type="button"
        onClick={onBack}
        className="flex items-center gap-1 text-sm text-(--muted-foreground) hover:text-(--foreground)"
      >
        <ArrowLeft className="h-4 w-4" />
        {t("backToProjects")}
      </button>

      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="text-2xl">{project.title}</CardTitle>
              <CardDescription>{project.description || "—"}</CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Badge className={STATUS_COLORS[project.status]}>
                {t(statusKey as string)}
              </Badge>
              <span className="text-lg" title={t(stageKey as string)}>
                {STAGE_ICONS[project.realization_stage] || "📦"}
              </span>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {/* Status Actions */}
          <div className="mb-4 flex flex-wrap gap-2">
            {(["draft", "active", "review", "completed", "archived"] as ProjectStatus[]).map(
              (s) => (
                <Button
                  key={s}
                  type="button"
                  variant={project.status === s ? "default" : "outline"}
                  size="sm"
                  onClick={() => handleStatusChange(s)}
                >
                  {t(s as string)}
                </Button>
              )
            )}
          </div>

          {/* Progress Bar */}
          {totalMilestones > 0 && (
            <div className="mb-4">
              <div className="mb-1 flex justify-between text-xs text-(--muted-foreground)">
                <span>{t("progress")}</span>
                <span>
                  {completedMilestones}/{totalMilestones} ({progressPct}%)
                </span>
              </div>
              <Progress value={progressPct} max={100} className="h-2" />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Milestones */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">{t("milestones")}</CardTitle>
        </CardHeader>
        <CardContent>
          {project.milestones.length === 0 ? (
            <p className="mb-4 text-sm text-(--muted-foreground)">
              {t("noMilestones")}
            </p>
          ) : (
            <div className="mb-4 space-y-2">
              {[...project.milestones]
                .sort((a, b) => a.position - b.position)
                .map((m) => (
                  <MilestoneItem
                    key={m.id}
                    milestone={m}
                    onToggle={() => handleToggleMilestone(m)}
                    onDelete={() => handleDeleteMilestone(m)}
                  />
                ))}
            </div>
          )}

          <Separator className="my-4" />

          <div className="flex gap-2">
            <Input
              value={newMilestone}
              onChange={(e) => setNewMilestone(e.target.value)}
              placeholder={t("milestoneTitle")}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleAddMilestone();
              }}
            />
            <Button
              type="button"
              onClick={handleAddMilestone}
              disabled={addMilestone.isPending || !newMilestone.trim()}
              size="sm"
            >
              <Plus className="mr-1 h-4 w-4" />
              {addMilestone.isPending ? tc("loading") : t("addMilestone")}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Artifacts */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between gap-4">
            <CardTitle className="text-lg">{t("artifacts")}</CardTitle>
            <label className="inline-flex cursor-pointer items-center gap-2 rounded-md border border-(--border) px-3 py-2 text-sm font-medium hover:bg-(--accent)">
              <FileUp className="h-4 w-4" />
              {uploadArtifact.isPending ? t("uploading") : t("uploadArtifact")}
              <input type="file" className="hidden" onChange={handleArtifactChange} disabled={uploadArtifact.isPending} />
            </label>
          </div>
        </CardHeader>
        <CardContent>
          {artifactError && <p className="mb-4 text-sm text-(--destructive)">{artifactError}</p>}
          {project.artifacts.length === 0 ? (
            <p className="text-sm text-(--muted-foreground)">
              {t("noArtifacts")}
            </p>
          ) : (
            <div className="space-y-2">
              {project.artifacts.map((a) => (
                <div
                  key={a.id}
                  className="flex items-center gap-3 rounded-lg border border-(--border) p-3"
                >
                  <FileUp className="h-4 w-4 text-(--muted-foreground)" />
                  <span className="text-sm">{a.file_url.split("/").pop()}</span>
                  <Badge variant="outline" className="ml-auto">
                    {a.file_type}
                  </Badge>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

// ── Main Page ──────────────────────────────────────────────────────

export default function ProjectsPage() {
  const t = useTranslations("projects");
  const tc = useTranslations("common");
  const token = useAuthStore((s) => s.token);
  const projectsQuery = useProjectsList(token);
  const [showCreate, setShowCreate] = useState(false);
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
  const projectList = projectsQuery.data ?? [];
  const loading = projectsQuery.isLoading;
  const error = projectsQuery.error?.detail ?? null;

  // ── Detail View ──
  if (selectedProjectId) {
    return (
      <div className="flex h-screen">
        <Sidebar />
        <div className="flex flex-1 flex-col">
          <Header />
          <main className="flex-1 overflow-y-auto p-8">
            <ProjectDetail
              projectId={selectedProjectId}
              onBack={() => {
                setSelectedProjectId(null);
                void projectsQuery.refetch();
              }}
            />
          </main>
        </div>
      </div>
    );
  }

  // ── List View ──
  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <Header />
        <main className="flex-1 overflow-y-auto p-8">
          <div className="mb-6 flex items-start justify-between">
            <div>
              <h2 className="text-3xl font-bold">{t("title")}</h2>
              <p className="text-(--muted-foreground)">{t("subtitle")}</p>
            </div>
            <Button type="button" onClick={() => setShowCreate(true)}>
              <Plus className="mr-2 h-4 w-4" />
              {t("createProject")}
            </Button>
          </div>

          {showCreate && (
            <div className="mb-6">
              <CreateProjectDialog
                onCreated={(projectId) => {
                  setShowCreate(false);
                  setSelectedProjectId(projectId);
                }}
                onCancel={() => setShowCreate(false)}
              />
            </div>
          )}

          {loading && (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
              {[1, 2, 3].map((i) => (
                <Card key={i}>
                  <CardHeader>
                    <Skeleton className="h-6 w-40" />
                    <Skeleton className="h-4 w-60" />
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
                  onClick={() => {
                    void projectsQuery.refetch();
                  }}
                >
                  {tc("retry")}
                </Button>
              </CardContent>
            </Card>
          )}

          {!loading && !error && projectList.length === 0 && !showCreate && (
            <Card>
              <CardContent className="py-12 text-center">
                <FolderOpen className="mx-auto mb-4 h-12 w-12 text-(--muted-foreground)" />
                <p className="text-lg font-medium">{t("noProjects")}</p>
                <p className="text-sm text-(--muted-foreground)">
                  {t("createFirst")}
                </p>
                <Button
                  type="button"
                  className="mt-4"
                  onClick={() => setShowCreate(true)}
                >
                  <Rocket className="mr-2 h-4 w-4" />
                  {t("createProject")}
                </Button>
              </CardContent>
            </Card>
          )}

          {!loading && !error && projectList.length > 0 && (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
              {projectList.map((project) => {
                const statusKey = project.status as string;
                return (
                  <button
                    key={project.id}
                    onClick={() => setSelectedProjectId(project.id)}
                    className="group text-left"
                  >
                    <Card className="h-full transition-shadow hover:shadow-md">
                      <CardHeader>
                        <div className="flex items-start justify-between">
                          <div className="min-w-0 flex-1">
                            <CardTitle className="truncate text-base">
                              {project.title}
                            </CardTitle>
                            <CardDescription className="line-clamp-2">
                              {project.description || "—"}
                            </CardDescription>
                          </div>
                          <ChevronRight className="mt-1 h-4 w-4 shrink-0 text-(--muted-foreground) transition-transform group-hover:translate-x-1" />
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="flex items-center gap-2">
                          <Badge className={STATUS_COLORS[project.status]}>
                            {t(statusKey as string)}
                          </Badge>
                          <span className="text-sm">
                            {STAGE_ICONS[project.realization_stage] || "📦"}{" "}
                            {t(
                              (project.realization_stage === "2d"
                                ? "prototype2d"
                                : project.realization_stage === "3d"
                                ? "prototype3d"
                                : project.realization_stage === "real_world"
                                ? "realWorld"
                                : project.realization_stage) as string
                            )}
                          </span>
                        </div>
                      </CardContent>
                    </Card>
                  </button>
                );
              })}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
