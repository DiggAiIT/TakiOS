'use client';

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ApiError,
  collaboration,
  type FacultyProfileData,
  type ReviewRequestData,
} from "@/lib/api-client";
import { toastSuccess, toastError } from "@/lib/toast";

function facultyKey(token: string | null) {
  return ["collaboration", "faculty", token] as const;
}

function incomingReviewsKey(token: string | null) {
  return ["collaboration", "incoming-reviews", token] as const;
}

export function useFacultyList(token: string | null) {
  return useQuery<FacultyProfileData[], ApiError>({
    queryKey: facultyKey(token),
    queryFn: () => collaboration.listFaculty(token as string),
    enabled: Boolean(token),
  });
}

export function useIncomingReviews(token: string | null, enabled = true) {
  return useQuery<ReviewRequestData[], ApiError>({
    queryKey: incomingReviewsKey(token),
    queryFn: () => collaboration.incomingReviews(token as string),
    enabled: Boolean(token) && enabled,
  });
}

export function useRequestReview(token: string | null) {
  const queryClient = useQueryClient();

  return useMutation<ReviewRequestData, ApiError, { project_id: string; faculty_id: string }>({
    mutationFn: (data) => collaboration.requestReview(data, token as string),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: incomingReviewsKey(token) });
      toastSuccess("Überprüfung angefragt");
    },
    onError: (error: ApiError) => toastError(error.detail ?? "Fehler aufgetreten"),
  });
}

export function useAcceptReview(token: string | null) {
  const queryClient = useQueryClient();

  return useMutation<ReviewRequestData, ApiError, { reviewId: string }>({
    mutationFn: ({ reviewId }) => collaboration.acceptReview(reviewId, token as string),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: incomingReviewsKey(token) });
      toastSuccess("Überprüfung angenommen");
    },
  });
}

export function useDeclineReview(token: string | null) {
  const queryClient = useQueryClient();

  return useMutation<ReviewRequestData, ApiError, { reviewId: string }>({
    mutationFn: ({ reviewId }) => collaboration.declineReview(reviewId, token as string),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: incomingReviewsKey(token) });
      toastSuccess("Überprüfung abgelehnt");
    },
  });
}

export function useCompleteReview(token: string | null) {
  const queryClient = useQueryClient();

  return useMutation<ReviewRequestData, ApiError, { reviewId: string; reviewText: string }>({
    mutationFn: ({ reviewId, reviewText }) =>
      collaboration.completeReview(reviewId, reviewText, token as string),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: incomingReviewsKey(token) });
      toastSuccess("Überprüfung abgeschlossen");
    },
  });
}