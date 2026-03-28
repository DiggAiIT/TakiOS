"use client";

import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import {
  LayoutDashboard,
  Pyramid,
  BookOpen,
  GraduationCap,
  ClipboardCheck,
  FolderKanban,
  Users,
  ShieldCheck,
  BarChart3,
  Globe,
  Settings,
} from "lucide-react";

const navItems = [
  { key: "dashboard", href: "/", icon: LayoutDashboard },
  { key: "pyramid", href: "/pyramid", icon: Pyramid },
  { key: "modules", href: "/modules", icon: BookOpen },
  { key: "learn", href: "/learn", icon: GraduationCap },
  { key: "assess", href: "/assess", icon: ClipboardCheck },
  { key: "projects", href: "/projects", icon: FolderKanban },
  { key: "collaborate", href: "/collaborate", icon: Users },
  { key: "compliance", href: "/compliance", icon: ShieldCheck },
  { key: "quality", href: "/quality", icon: BarChart3 },
  { key: "impact", href: "/impact", icon: Globe },
  { key: "settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const t = useTranslations("nav");

  return (
    <aside className="flex h-full w-64 flex-col border-r border-[var(--border)] bg-[var(--secondary)] p-4">
      <div className="mb-8 px-2">
        <h1 className="text-2xl font-bold text-[var(--primary)]">TakiOS</h1>
        <p className="text-xs text-[var(--muted-foreground)]">Medizintechnik HAW Hamburg</p>
      </div>

      <nav className="flex-1 space-y-1" role="navigation" aria-label="Main navigation">
        {navItems.map(({ key, href, icon: Icon }) => (
          <Link
            key={key}
            href={href}
            className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-[var(--foreground)] transition-colors hover:bg-[var(--accent)]"
          >
            <Icon className="h-4 w-4" aria-hidden="true" />
            {t(key)}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
