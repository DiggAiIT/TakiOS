"use client";

import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Link } from "@/i18n/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { LocaleSwitcher } from "@/components/layout/locale-switcher";
import { ApiError } from "@/lib/api-client";
import { useLogin } from "@/hooks/use-auth";
import { toastSuccess, toastError } from "@/lib/toast";

const loginSchema = z.object({
  email: z.string().email("Bitte eine gültige E-Mail eingeben"),
  password: z.string().min(8, "Passwort muss mindestens 8 Zeichen haben"),
});

type LoginFormValues = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const t = useTranslations("auth");
  const tc = useTranslations("common");
  const router = useRouter();
  const loginMutation = useLogin();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setError,
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormValues) => {
    try {
      await loginMutation.mutateAsync({ email: data.email, password: data.password });
      toastSuccess("Willkommen zurück!");
      router.replace("/");
    } catch (error) {
      const errorMessage = error instanceof ApiError ? error.detail : t("invalidCredentials");
      toastError(errorMessage);
      setError("root", { message: errorMessage });
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <div className="absolute right-4 top-4">
        <LocaleSwitcher />
      </div>

      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">TakiOS</CardTitle>
          <CardDescription>{t("loginTitle")}</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label htmlFor="email" className="mb-1 block text-sm font-medium">
                {tc("email")}
              </label>
              <Input
                id="email"
                type="email"
                autoComplete="email"
                {...register("email")}
              />
              {errors.email && (
                <p className="text-xs text-red-500 mt-1">{errors.email.message}</p>
              )}
            </div>
            <div>
              <label htmlFor="password" className="mb-1 block text-sm font-medium">
                {tc("password")}
              </label>
              <Input
                id="password"
                type="password"
                autoComplete="current-password"
                {...register("password")}
              />
              {errors.password && (
                <p className="text-xs text-red-500 mt-1">{errors.password.message}</p>
              )}
            </div>

            {errors.root && (
              <p className="text-sm text-[var(--destructive)]" role="alert">
                {errors.root.message}
              </p>
            )}

            <Button type="submit" className="w-full" disabled={isSubmitting || loginMutation.isPending}>
              {isSubmitting ? tc("loading") : tc("login")}
            </Button>

            <p className="text-center text-sm text-[var(--muted-foreground)]">
              {t("noAccount")}{" "}
              <Link href="/auth/register" className="text-[var(--primary)] hover:underline">
                {tc("register")}
              </Link>
            </p>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
