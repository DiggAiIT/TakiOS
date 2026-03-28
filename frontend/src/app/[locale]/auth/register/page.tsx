"use client";

import { useTranslations } from "next-intl";
import { useLocale } from "next-intl";
import { Link, useRouter } from "@/i18n/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { LocaleSwitcher } from "@/components/layout/locale-switcher";
import { auth } from "@/lib/api-client";
import { toastSuccess, toastError } from "@/lib/toast";

const registerSchema = z.object({
  fullName: z.string().min(2, "Name muss mindestens 2 Zeichen haben"),
  email: z.string().email("Bitte eine gültige E-Mail eingeben"),
  password: z
    .string()
    .min(8, "Passwort muss mindestens 8 Zeichen haben")
    .regex(/[A-Z]/, "Mindestens ein Großbuchstabe")
    .regex(/[0-9]/, "Mindestens eine Zahl"),
  role: z.enum(["student", "faculty"]),
});

type RegisterFormValues = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const t = useTranslations("auth");
  const tc = useTranslations("common");
  const locale = useLocale();
  const router = useRouter();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setError,
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: { role: "student" },
  });

  const onSubmit = async (data: RegisterFormValues) => {
    try {
      await auth.register({
        email: data.email,
        password: data.password,
        full_name: data.fullName,
        role: data.role,
        locale,
      });
      toastSuccess("Konto erstellt! Bitte anmelden.");
      router.push("/auth/login");
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Registrierung fehlgeschlagen";
      toastError(message);
      setError("root", { message });
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
          <CardDescription>{t("registerTitle")}</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label htmlFor="fullName" className="mb-1 block text-sm font-medium">
                {tc("fullName")}
              </label>
              <Input
                id="fullName"
                type="text"
                autoComplete="name"
                {...register("fullName")}
              />
              {errors.fullName && (
                <p className="text-xs text-red-500 mt-1">{errors.fullName.message}</p>
              )}
            </div>
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
                autoComplete="new-password"
                {...register("password")}
              />
              {errors.password && (
                <p className="text-xs text-red-500 mt-1">{errors.password.message}</p>
              )}
            </div>
            <div>
              <label htmlFor="role" className="mb-1 block text-sm font-medium">
                {t("role")}
              </label>
              <select
                id="role"
                className="flex h-10 w-full rounded-md border border-[var(--border)] bg-transparent px-3 py-2 text-sm"
                {...register("role")}
              >
                <option value="student">{t("student")}</option>
                <option value="faculty">{t("faculty")}</option>
              </select>
            </div>

            {errors.root && (
              <p className="text-sm text-[var(--destructive)]" role="alert">
                {errors.root.message}
              </p>
            )}

            <Button type="submit" className="w-full" disabled={isSubmitting}>
              {isSubmitting ? tc("loading") : tc("register")}
            </Button>

            <p className="text-center text-sm text-[var(--muted-foreground)]">
              {t("hasAccount")}{" "}
              <Link href="/auth/login" className="text-[var(--primary)] hover:underline">
                {tc("login")}
              </Link>
            </p>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
