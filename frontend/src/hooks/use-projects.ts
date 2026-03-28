'use client';

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ApiError,
  projects,
  type ArtifactData,
  type MilestoneData,
  type ProjectData,
  type ProjectDetailData,
  type ProjectStatus,
  type RealizationStage,
} from "@/lib/api-client";
import { toastSuccess, toastError } from "@/lib/toast";

function listKey(token: string | null) {
  return ["projects", "list", token] as const;
}

function detailKey(token: string | null, projectId: string | null) {
  return ["projects", "detail", token, projectId] as const;
}

export function useProjectsList(token: string | null) {
  return useQuery<ProjectData[], ApiError>({
    queryKey: listKey(token),
    queryFn: () => projects.list(token as string),
    enabled: Boolean(token),
  });
}

export function useProjectDetail(token: string | null, projectId: string | null) {
  return useQuery<ProjectDetailData, ApiError>({
    queryKey: detailKey(token, projectId),
    queryFn: () => projects.get(projectId as string, token as string),
    enabled: Boolean(token && projectId),
  });
}

export function useCreateProject(token: string | null) {
  const queryClient = useQueryClient();

  return useMutation<
    ProjectData,
    ApiError,
    { title: string; description: string; module_id?: string }
  >({
    mutationFn: (data) => projects.create(data, token as string),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: listKey(token) });
      toastSuccess("Projekt erstellt");
    },
    onError: (error: ApiError) => toastError(error.detail ?? "Fehler beim Erstellen"),
  });
}

export function useUpdateProject(token: string | null, projectId: string) {
  const queryClient = useQueryClient();

  return useMutation<
    ProjectData,
    ApiError,
    { title?: string; description?: string; status?: ProjectStatus; realization_stage?: RealizationStage }
  >({
    mutationFn: (data) => projects.update(projectId, data, token as string),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: listKey(token) });
      void queryClient.invalidateQueries({ queryKey: detailKey(token, projectId) });
      toastSuccess("Projekt gespeichert");
    },
    onError: (error: ApiError) => toastError(error.detail ?? "Fehler aufgetreten"),
  });
}

export function useAddMilestone(token: string | null, projectId: string) {
  const queryClient = useQueryClient();

  return useMutation<MilestoneData, ApiError, { title: string; description?: string }>({
    mutationFn: (data) => projects.addMilestone(projectId, data, token as string),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: detailKey(token, projectId) });
      toastSuccess("Meilenstein hinzugefügt");
    },
    onError: (error: ApiError) => toastError(error.detail ?? "Fehler aufgetreten"),
  });
}

export function useUpdateMilestone(token: string | null, projectId: string) {
  const queryClient = useQueryClient();

  return useMutation<
    MilestoneData,
    ApiError,
    { milestoneId: string; title?: string; description?: string; completed?: boolean }
  >({
    mutationFn: ({ milestoneId, ...data }) => projects.updateMilestone(milestoneId, data, token as string),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: detailKey(token, projectId) });
      toastSuccess("Meilenstein aktualisiert");
    },
  });
}

export function useDeleteMilestone(token: string | null, projectId: string) {
  const queryClient = useQueryClient();

  return useMutation<void, ApiError, { milestoneId: string }>({
    mutationFn: ({ milestoneId }) => projects.deleteMilestone(milestoneId, token as string),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: detailKey(token, projectId) });
      toastSuccess("Meilenstein gelöscht");
    },
  });
}

export function useUploadArtifact(token: string | null, projectId: string) {
  const queryClient = useQueryClient();

  return useMutation<ArtifactData, ApiError, { file: File }>({
    mutationFn: ({ file }) => projects.uploadArtifact(projectId, file, token as string),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: detailKey(token, projectId) });
      toastSuccess("Datei hochgeladen");
    },
    onError: (error: ApiError) => toastError(error.detail ?? "Upload fehlgeschlagen"),
  });
}