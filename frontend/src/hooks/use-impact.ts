'use client';

import { useMutation, useQuery } from "@tanstack/react-query";
import {
  ApiError,
  impact,
  type ImpactAssessmentData,
  type SurveyData,
  type SurveyResponseData,
} from "@/lib/api-client";
import { toastSuccess, toastError } from "@/lib/toast";

export function useAssessments(token: string | null) {
  return useQuery<ImpactAssessmentData[], ApiError>({
    queryKey: ["impact", "assessments", token],
    queryFn: () => impact.listAssessments(token as string),
    enabled: Boolean(token),
  });
}

export function useSurveys(token: string | null) {
  return useQuery<SurveyData[], ApiError>({
    queryKey: ["impact", "surveys", token],
    queryFn: () => impact.listSurveys(token as string),
    enabled: Boolean(token),
  });
}

export function useSubmitSurveyResponse(token: string | null) {
  return useMutation<
    SurveyResponseData,
    ApiError,
    { survey_id: string; responses: Record<string, string> }
  >({
    mutationFn: (data) => impact.submitSurveyResponse(data, token as string),
    onSuccess: () => toastSuccess("Umfrage eingereicht"),
    onError: (error: ApiError) => toastError(error.detail ?? "Fehler aufgetreten"),
  });
}