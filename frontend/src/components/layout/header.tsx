"use client";

import { useEffect } from "react";
import { useTranslations } from "next-intl";
import { LocaleSwitcher } from "./locale-switcher";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/stores/auth-store";
import { useUIStore } from "@/store/uiStore";
import { LogOut, Sun, Moon, Monitor } from "lucide-react";

export function Header() {
  const t = useTranslations("common");
  const { user, logout } = useAuthStore();
  const { theme, setTheme } = useUIStore();

  useEffect(() => {
    const root = document.documentElement;
    if (theme === "dark") {
      root.classList.add("dark");
    } else if (theme === "light") {
      root.classList.remove("dark");
    } else {
      const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      if (prefersDark) root.classList.add("dark");
      else root.classList.remove("dark");
    }
  }, [theme]);

  return (
    <header className="flex h-14 items-center justify-between border-b border-[var(--border)] px-6">
      <div />
      <div className="flex items-center gap-4">
        <LocaleSwitcher />
        <button
          onClick={() =>
            setTheme(theme === "light" ? "dark" : theme === "dark" ? "system" : "light")
          }
          className="rounded-md p-1.5 hover:bg-[var(--muted)] text-[var(--muted-foreground)] transition-colors"
          aria-label="Theme wechseln"
        >
          {theme === "dark" ? (
            <Moon className="h-4 w-4" />
          ) : theme === "light" ? (
            <Sun className="h-4 w-4" />
          ) : (
            <Monitor className="h-4 w-4" />
          )}
        </button>
        {user && (
          <>
            <span className="text-sm text-[var(--muted-foreground)]">{user.full_name}</span>
            <Button variant="ghost" size="icon" onClick={logout} aria-label={t("logout")}>
              <LogOut className="h-4 w-4" />
            </Button>
          </>
        )}
      </div>
    </header>
  );
}
