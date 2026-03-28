'use client';

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ApiError,
  quality,
  type QualityDashboardData,
  type UserFeedbackData,
} from "@/lib/api-client";
import { toastSuccess, toastError } from "@/lib/toast";

function dashboardKey(token: string | null) {
  return ["quality", "dashboard", token] as const;
}

export function useQualityDashboard(token: string | null) {
  return useQuery<QualityDashboardData, ApiError>({
    queryKey: dashboardKey(token),
    queryFn: () => quality.getDashboard(token as string),
    enabled: Boolean(token),
  });
}

export function useCreateFeedback(token: string | null) {
  const queryClient = useQueryClient();

  return useMutation<
    UserFeedbackData,
    ApiError,
    { category: string; text: string; rating: number }
  >({
    mutationFn: (data) => quality.createFeedback(data, token as string),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: dashboardKey(token) });
      toastSuccess("Feedback gesendet");
    },
    onError: (error: ApiError) => toastError(error.detail ?? "Fehler aufgetreten"),
  });
}