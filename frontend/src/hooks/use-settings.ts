'use client';

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ApiError,
  io,
  preferences,
  type IOCapabilityData,
  type IOType,
  type UserIOPreferenceData,
  type UserPreferenceData,
} from "@/lib/api-client";

function preferencesKey(token: string | null) {
  return ["settings", "preferences", token] as const;
}

function capabilitiesKey(token: string | null) {
  return ["settings", "io-capabilities", token] as const;
}

function ioPreferencesKey(token: string | null) {
  return ["settings", "io-preferences", token] as const;
}

export function useUserPreferences(token: string | null) {
  return useQuery<UserPreferenceData, ApiError>({
    queryKey: preferencesKey(token),
    queryFn: () => preferences.get(token as string),
    enabled: Boolean(token),
  });
}

export function useIOCapabilities(token: string | null) {
  return useQuery<IOCapabilityData[], ApiError>({
    queryKey: capabilitiesKey(token),
    queryFn: () => io.listCapabilities(token as string),
    enabled: Boolean(token),
  });
}

export function useUserIOPreferences(token: string | null) {
  return useQuery<UserIOPreferenceData, ApiError>({
    queryKey: ioPreferencesKey(token),
    queryFn: () => io.getPreferences(token as string),
    enabled: Boolean(token),
  });
}

export function useUpdateUserPreferences(token: string | null) {
  const queryClient = useQueryClient();

  return useMutation<
    UserPreferenceData,
    ApiError,
    {
      theme?: string;
      high_contrast?: boolean;
      reduced_motion?: boolean;
      font_size?: number;
      locale?: string;
    }
  >({
    mutationFn: (data) => preferences.update(data, token as string),
    onSuccess: (data) => {
      queryClient.setQueryData(preferencesKey(token), data);
    },
  });
}

export function useUpdateUserIOPreferences(token: string | null) {
  const queryClient = useQueryClient();

  return useMutation<
    UserIOPreferenceData,
    ApiError,
    { input_mode?: IOType; output_mode?: IOType }
  >({
    mutationFn: (data) => io.updatePreferences(data, token as string),
    onSuccess: (data) => {
      queryClient.setQueryData(ioPreferencesKey(token), data);
    },
  });
}