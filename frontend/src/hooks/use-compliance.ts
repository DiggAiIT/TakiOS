'use client';

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ApiError,
  compliance,
  type ComplianceEvidenceData,
  type ComplianceRequirementData,
  type ComplianceStatusData,
} from "@/lib/api-client";
import { toastSuccess, toastError } from "@/lib/toast";

function requirementsKey(token: string | null, framework: string) {
  return ["compliance", "requirements", token, framework] as const;
}

function statusKey(token: string | null) {
  return ["compliance", "status", token] as const;
}

export function useComplianceRequirements(token: string | null, framework: string) {
  return useQuery<ComplianceRequirementData[], ApiError>({
    queryKey: requirementsKey(token, framework),
    queryFn: () => compliance.listRequirements(token as string, framework || undefined),
    enabled: Boolean(token),
  });
}

export function useComplianceStatus(token: string | null) {
  return useQuery<ComplianceStatusData, ApiError>({
    queryKey: statusKey(token),
    queryFn: () => compliance.getStatus(token as string),
    enabled: Boolean(token),
  });
}

export function useCreateComplianceEvidence(token: string | null, framework: string) {
  const queryClient = useQueryClient();

  return useMutation<
    ComplianceEvidenceData,
    ApiError,
    { requirement_id: string; evidence_type: string; description: string }
  >({
    mutationFn: (data) => compliance.createEvidence(data, token as string),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: requirementsKey(token, framework) });
      void queryClient.invalidateQueries({ queryKey: statusKey(token) });
      toastSuccess("Nachweis gespeichert");
    },
    onError: (error: ApiError) => toastError(error.detail ?? "Fehler aufgetreten"),
  });
}