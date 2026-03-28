'use client';

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ApiError,
  content,
  type ContentWithBodyData,
  type MnemonicData,
} from "@/lib/api-client";
import { toastSuccess, toastError } from "@/lib/toast";

export function useUnitContent(token: string | null, unitId: string | null) {
  return useQuery<ContentWithBodyData, ApiError>({
    queryKey: ["content", "unit", token, unitId],
    queryFn: () => content.getForUnit(unitId as string, token as string),
    enabled: Boolean(token && unitId),
  });
}

export function useGenerateMnemonic(token: string | null, unitId: string | null) {
  const queryClient = useQueryClient();

  return useMutation<
    MnemonicData,
    ApiError,
    { contentId: string; mnemonicType: string; language: string }
  >({
    mutationFn: ({ contentId, mnemonicType, language }) =>
      content.generateMnemonic(
        {
          content_id: contentId,
          mnemonic_type: mnemonicType,
          language,
        },
        token as string
      ),
    onSuccess: (mnemonic) => {
      queryClient.setQueryData<ContentWithBodyData | undefined>(
        ["content", "unit", token, unitId],
        (current) => {
          if (!current) {
            return current;
          }

          return {
            ...current,
            mnemonics: [...current.mnemonics, mnemonic],
          };
        }
      );
      toastSuccess("Eselsbrücke erstellt");
    },
    onError: (error: ApiError) => toastError(error.detail ?? "Fehler aufgetreten"),
  });
}

export function useRateMnemonic(token: string | null, unitId: string | null) {
  const queryClient = useQueryClient();

  return useMutation<MnemonicData, ApiError, { mnemonicId: string; score: number }>({
    mutationFn: ({ mnemonicId, score }) => content.rateMnemonic(mnemonicId, score, token as string),
    onSuccess: (updatedMnemonic) => {
      queryClient.setQueryData<ContentWithBodyData | undefined>(
        ["content", "unit", token, unitId],
        (current) => {
          if (!current) {
            return current;
          }

          return {
            ...current,
            mnemonics: current.mnemonics.map((mnemonic) =>
              mnemonic.id === updatedMnemonic.id ? updatedMnemonic : mnemonic
            ),
          };
        }
      );
    },
  });
}