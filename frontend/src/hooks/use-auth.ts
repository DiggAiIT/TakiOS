'use client';

import { useMutation, useQuery } from "@tanstack/react-query";
import { auth, ApiError, type UserData } from "@/lib/api-client";
import { useAuthStore } from "@/stores/auth-store";
import { toastSuccess } from "@/lib/toast";

export function useCurrentUser() {
  const token = useAuthStore((state) => state.token);

  return useQuery<UserData, ApiError>({
    queryKey: ["auth", "me", token],
    queryFn: () => auth.me(token as string),
    enabled: Boolean(token),
  });
}

export function useLogin() {
  const setAuth = useAuthStore((state) => state.setAuth);

  return useMutation({
    mutationFn: async ({ email, password }: { email: string; password: string }) => {
      const { access_token } = await auth.login(email, password);
      const user = await auth.me(access_token);
      return { accessToken: access_token, user };
    },
    onSuccess: ({ accessToken, user }) => {
      setAuth(accessToken, user);
      toastSuccess("Erfolgreich angemeldet");
    },
  });
}