'use client';

import { useMutation } from "@tanstack/react-query";
import { analyzer, ApiError, type ProjectAnalysisData } from "@/lib/api-client";
import { toastSuccess, toastError } from "@/lib/toast";

export function useProjectAnalysis() {
  return useMutation<ProjectAnalysisData, ApiError, { idea: string; use_ai?: boolean }>({
    mutationFn: (data) => analyzer.analyze(data),
    onSuccess: () => toastSuccess("Analyse abgeschlossen"),
    onError: (error: ApiError) => toastError(error.detail ?? "Analyse fehlgeschlagen"),
  });
}