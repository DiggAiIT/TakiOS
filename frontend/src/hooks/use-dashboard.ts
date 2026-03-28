'use client';

import { useQuery } from "@tanstack/react-query";

import { ApiError, assessments, type KnowledgeLevelData, type LevelStatus } from "@/lib/api-client";
import { useProjectsList } from "@/hooks/use-projects";
import { usePyramid } from "@/hooks/use-pyramid";
import { useSubjectsWithModules } from "@/hooks/use-modules";

export interface DashboardStatsData {
  completedLevels: number;
  inProgressLevels: number;
  lockedLevels: number;
  totalLevels: number;
  moduleCount: number;
  examCount: number;
  activeProjectCount: number;
  availableProjectCount: number;
  progressByLevel: Record<string, LevelStatus>;
  levels: KnowledgeLevelData[];
}

export function useDashboardStats(token: string | null) {
  const pyramidQuery = usePyramid(token);
  const modulesQuery = useSubjectsWithModules(token);
  const projectsQuery = useProjectsList(token);
  const moduleIds = Object.values(modulesQuery.data?.modulesBySubject ?? {})
    .flat()
    .map((module) => module.id);

  const examStatsQuery = useQuery<{ examCount: number }, ApiError>({
    queryKey: ["dashboard", "exam-count", token, moduleIds],
    enabled: Boolean(token) && moduleIds.length > 0,
    queryFn: async () => {
      const exams = await Promise.all(
        moduleIds.map(async (moduleId) => assessments.list(moduleId, token as string))
      );

      return {
        examCount: exams.reduce((sum, current) => sum + current.length, 0),
      };
    },
  });

  const levels = pyramidQuery.data?.levels ?? [];
  const progressByLevel = pyramidQuery.data?.progress ?? {};
  const completedLevels = Object.values(progressByLevel).filter(
    (status) => status === "completed"
  ).length;
  const inProgressLevels = Object.values(progressByLevel).filter(
    (status) => status === "in_progress"
  ).length;
  const lockedLevels = levels.length - completedLevels - inProgressLevels;
  const moduleCount = moduleIds.length;
  const projects = projectsQuery.data ?? [];
  const activeProjectCount = projects.filter(
    (project) => project.status === "active" || project.status === "review"
  ).length;

  return {
    isLoading:
      pyramidQuery.isLoading ||
      modulesQuery.isLoading ||
      projectsQuery.isLoading ||
      examStatsQuery.isLoading,
    error:
      pyramidQuery.error ??
      modulesQuery.error ??
      projectsQuery.error ??
      examStatsQuery.error ??
      null,
    refetch: async () => {
      await Promise.all([
        pyramidQuery.refetch(),
        modulesQuery.refetch(),
        projectsQuery.refetch(),
        examStatsQuery.refetch(),
      ]);
    },
    data: {
      completedLevels,
      inProgressLevels,
      lockedLevels,
      totalLevels: levels.length,
      moduleCount,
      examCount: examStatsQuery.data?.examCount ?? 0,
      activeProjectCount,
      availableProjectCount: projects.length,
      progressByLevel,
      levels,
    } satisfies DashboardStatsData,
  };
}