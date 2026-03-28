'use client';

import { useMutation, useQuery } from "@tanstack/react-query";
import {
  ApiError,
  assessments,
  type ExamData,
  type ExamResultData,
  type StartExamData,
} from "@/lib/api-client";
import { toastSuccess, toastError } from "@/lib/toast";

export function useExams(token: string | null, moduleId: string | null) {
  return useQuery<ExamData[], ApiError>({
    queryKey: ["assessment", "exams", token, moduleId],
    queryFn: () => assessments.list(moduleId as string, token as string),
    enabled: Boolean(token && moduleId),
  });
}

export function useStartExam(token: string | null) {
  return useMutation<StartExamData, ApiError, { examId: string }>({
    mutationFn: ({ examId }) => assessments.start(examId, token as string),
    onSuccess: () => toastSuccess("Prüfung gestartet"),
    onError: (error: ApiError) => toastError(error.detail ?? "Fehler aufgetreten"),
  });
}

export function useSubmitExam(token: string | null) {
  return useMutation<
    ExamResultData,
    ApiError,
    {
      attemptId: string;
      answers: Array<{ question_id: string; answer_data: Record<string, unknown> }>;
    }
  >({
    mutationFn: ({ attemptId, answers }) =>
      assessments.submit(attemptId, { answers }, token as string),
    onSuccess: () => toastSuccess("Prüfung abgegeben"),
    onError: (error: ApiError) => toastError(error.detail ?? "Fehler aufgetreten"),
  });
}