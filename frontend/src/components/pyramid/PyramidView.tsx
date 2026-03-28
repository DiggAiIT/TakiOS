"use client";

import {
  type KnowledgeLevelData,
  type LevelStatus,
  type TechUnitChainData,
  type TechUnitData,
} from "@/lib/api-client";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Lock,
  CheckCircle2,
  Loader2,
  Cpu,
  ArrowRight,
  ChevronRight,
  AlertTriangle,
  Zap,
} from "lucide-react";

// Colors for each pyramid position (bottom=1 to top=7)
const LEVEL_COLORS: Record<number, string> = {
  1: "#e9d5ff",
  2: "#d8b4fe",
  3: "#c084fc",
  4: "#a855f7",
  5: "#8b5cf6",
  6: "#6366f1",
  7: "#3b82f6",
};

const LEVEL_BADGE_CLASSES: Record<number, string> = {
  1: "bg-[#e9d5ff] text-gray-800",
  2: "bg-[#d8b4fe] text-gray-800",
  3: "bg-[#c084fc] text-white",
  4: "bg-[#a855f7] text-white",
  5: "bg-[#8b5cf6] text-white",
  6: "bg-[#6366f1] text-white",
  7: "bg-[#3b82f6] text-white",
};

const STATUS_OVERLAY: Record<LevelStatus, { opacity: number; border: string }> = {
  locked: { opacity: 0.4, border: "transparent" },
  in_progress: { opacity: 0.9, border: "#f59e0b" },
  completed: { opacity: 1, border: "#10b981" },
};

// ── Interactive SVG Pyramid ─────────────────────────────────────

interface PyramidViewProps {
  levels: KnowledgeLevelData[];
  progress: Record<string, LevelStatus>;
  selectedLevel: KnowledgeLevelData | null;
  onSelectLevel: (level: KnowledgeLevelData) => void;
  locale: string;
  t: (key: string) => string;
}

export function PyramidView({
  levels,
  progress,
  selectedLevel,
  onSelectLevel,
  locale,
  t,
}: PyramidViewProps) {
  const sortedLevels = [...levels].sort(
    (a, b) => b.pyramid_position - a.pyramid_position
  );

  const n = (obj: { name_de: string; name_en: string }) =>
    locale === "de" ? obj.name_de : obj.name_en;

  function getStatus(levelId: string): LevelStatus {
    return progress[levelId] || "locked";
  }

  return (
    <svg
      viewBox="0 0 520 420"
      className="w-full"
      role="img"
      aria-label="Knowledge Pyramid"
    >
      {sortedLevels.map((level, i) => {
        const status = getStatus(level.id);
        const overlay = STATUS_OVERLAY[status];
        const baseColor = LEVEL_COLORS[level.pyramid_position] || "#a855f7";
        const isSelected = selectedLevel?.id === level.id;

        const centerX = 260;
        const rowHeight = 48;
        const gap = 4;
        const y = 10 + i * (rowHeight + gap);
        const topHalf = (70 + i * 62) / 2;
        const bottomHalf = (70 + (i + 1) * 62) / 2;

        const path = `M ${centerX - topHalf} ${y} L ${centerX + topHalf} ${y} L ${centerX + bottomHalf} ${y + rowHeight} L ${centerX - bottomHalf} ${y + rowHeight} Z`;

        return (
          <g
            key={level.id}
            onClick={() => onSelectLevel(level)}
            className="cursor-pointer"
            role="button"
            tabIndex={0}
            aria-label={`${n(level)} — ${t(status === "in_progress" ? "inProgress" : status)}`}
          >
            <path
              d={path}
              fill={baseColor}
              opacity={overlay.opacity}
              stroke={isSelected ? "var(--foreground)" : overlay.border}
              strokeWidth={isSelected ? 3 : overlay.border !== "transparent" ? 2 : 0}
              rx={4}
              className="transition-all duration-200"
            />
            <text
              x={centerX}
              y={y + rowHeight / 2 + 1}
              textAnchor="middle"
              dominantBaseline="middle"
              fill={level.pyramid_position <= 2 ? "#1f2937" : "white"}
              fontSize="13"
              fontWeight="600"
              className="pointer-events-none select-none"
            >
              {n(level)}
            </text>
            {status === "locked" && (
              <text
                x={centerX + topHalf - 8}
                y={y + 14}
                fontSize="12"
                fill={level.pyramid_position <= 2 ? "#6b7280" : "rgba(255,255,255,0.7)"}
                className="pointer-events-none"
              >
                🔒
              </text>
            )}
            {status === "completed" && (
              <text
                x={centerX + topHalf - 8}
                y={y + 14}
                fontSize="12"
                className="pointer-events-none"
              >
                ✓
              </text>
            )}
            {status === "in_progress" && (
              <circle
                cx={centerX + topHalf - 4}
                cy={y + 10}
                r={4}
                fill="#f59e0b"
                className="pointer-events-none"
              >
                <animate
                  attributeName="opacity"
                  values="1;0.3;1"
                  dur="2s"
                  repeatCount="indefinite"
                />
              </circle>
            )}
            <text
              x={centerX - topHalf + 14}
              y={y + rowHeight / 2 + 1}
              textAnchor="middle"
              dominantBaseline="middle"
              fill={level.pyramid_position <= 2 ? "#374151" : "rgba(255,255,255,0.6)"}
              fontSize="11"
              fontWeight="500"
              className="pointer-events-none select-none"
            >
              {level.pyramid_position}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

// ── Level Detail Panel ──────────────────────────────────────────

interface LevelDetailProps {
  level: KnowledgeLevelData;
  status: LevelStatus;
  units: TechUnitData[];
  chains: TechUnitChainData[];
  loading: boolean;
  locale: string;
  t: (key: string) => string;
}

export function LevelDetail({
  level,
  status,
  units,
  chains,
  loading,
  locale,
  t,
}: LevelDetailProps) {
  const n = (obj: { name_de: string; name_en: string }) =>
    locale === "de" ? obj.name_de : obj.name_en;
  const dd = (obj: { description_de: string; description_en: string }) =>
    locale === "de" ? obj.description_de : obj.description_en;

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex items-center gap-3">
            <span
              className={`flex h-10 w-10 items-center justify-center rounded-full text-lg font-bold ${LEVEL_BADGE_CLASSES[level.pyramid_position] ?? "bg-slate-500 text-white"}`}
            >
              {level.pyramid_position}
            </span>
            <div>
              <CardTitle>{n(level)}</CardTitle>
              <CardDescription>{dd(level)}</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2">
            <Badge
              variant={
                status === "completed"
                  ? "success"
                  : status === "in_progress"
                    ? "warning"
                    : "secondary"
              }
            >
              {status === "locked" && <Lock className="mr-1 h-3 w-3" />}
              {status === "in_progress" && <Loader2 className="mr-1 h-3 w-3" />}
              {status === "completed" && <CheckCircle2 className="mr-1 h-3 w-3" />}
              {t(status === "in_progress" ? "inProgress" : status)}
            </Badge>
          </div>

          {level.unlock_criteria?.required_module_codes ? (
            <div className="mt-3">
              <p className="text-sm font-medium">{t("requiredModules")}:</p>
              <div className="mt-1 flex flex-wrap gap-1">
                {level.unlock_criteria.required_module_codes.map((code) => (
                  <Badge key={code} variant="outline">
                    {code}
                  </Badge>
                ))}
              </div>
              {status === "locked" && (
                <p className="mt-2 text-xs text-[var(--muted-foreground)]">
                  {t("unlockHint")}
                </p>
              )}
            </div>
          ) : (
            <p className="mt-3 text-sm text-[var(--muted-foreground)]">
              {t("baseLevel")}
            </p>
          )}
        </CardContent>
      </Card>

      {loading ? (
        <div className="space-y-3">
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-24 w-full" />
        </div>
      ) : (
        <>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <Cpu className="h-5 w-5 text-[var(--primary)]" />
                {t("techUnits")} ({units.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              {units.length === 0 ? (
                <p className="text-sm text-[var(--muted-foreground)]">
                  {t("noUnits")}
                </p>
              ) : (
                <div className="space-y-3">
                  {units.map((unit) => (
                    <TechUnitCard key={unit.id} unit={unit} locale={locale} t={t} />
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {chains.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Zap className="h-5 w-5 text-[var(--primary)]" />
                  {t("chains")} ({chains.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                {chains.map((chain) => (
                  <ChainVisualization
                    key={chain.id}
                    chain={chain}
                    locale={locale}
                  />
                ))}
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  );
}

// ── Tech Unit Card ──────────────────────────────────────────────

function TechUnitCard({
  unit,
  locale,
  t,
}: {
  unit: TechUnitData;
  locale: string;
  t: (key: string) => string;
}) {
  const n = locale === "de" ? unit.name_de : unit.name_en;
  const desc = locale === "de" ? unit.description_de : unit.description_en;

  return (
    <div className="rounded-lg border border-[var(--border)] p-3">
      <p className="font-medium">{n}</p>
      <p className="mt-1 text-xs text-[var(--muted-foreground)]">{desc}</p>

      {unit.io_spec && (
        <div className="mt-2 flex items-center gap-2 text-xs">
          <Badge variant="outline" className="gap-1">
            <ChevronRight className="h-3 w-3" />
            {t("input")}: {unit.io_spec.input}
          </Badge>
          <ArrowRight className="h-3 w-3 text-[var(--muted-foreground)]" />
          <Badge variant="outline" className="gap-1">
            {t("output")}: {unit.io_spec.output}
          </Badge>
        </div>
      )}

      {unit.limitations && (
        <div className="mt-2 flex items-start gap-1 text-xs text-[var(--muted-foreground)]">
          <AlertTriangle className="mt-0.5 h-3 w-3 shrink-0" />
          <span>{unit.limitations}</span>
        </div>
      )}
    </div>
  );
}

// ── Chain Visualization ─────────────────────────────────────────

function ChainVisualization({
  chain,
  locale,
}: {
  chain: TechUnitChainData;
  locale: string;
}) {
  return (
    <div className="mb-4 last:mb-0">
      <p className="mb-2 text-sm font-medium">{chain.name}</p>
      <p className="mb-3 text-xs text-[var(--muted-foreground)]">
        {chain.description}
      </p>
      <div className="flex flex-wrap items-center gap-2">
        {chain.units.map((unit, i) => (
          <div key={unit.id} className="flex items-center gap-2">
            <div className="rounded-md border border-[var(--primary)]/30 bg-[var(--primary)]/5 px-3 py-2 text-center">
              <p className="text-xs font-medium">
                {locale === "de" ? unit.name_de : unit.name_en}
              </p>
              {unit.io_spec && (
                <p className="mt-0.5 text-[10px] text-[var(--muted-foreground)]">
                  {unit.io_spec.output}
                </p>
              )}
            </div>
            {i < chain.units.length - 1 && (
              <ArrowRight className="h-4 w-4 shrink-0 text-[var(--primary)]" />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
