"use client";

import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "./button";

interface PaginationProps {
  page: number;
  pages: number;
  total: number;
  perPage: number;
  onPageChange: (page: number) => void;
}

export function Pagination({ page, pages, total, perPage, onPageChange }: PaginationProps) {
  if (pages <= 1) return null;

  const from = (page - 1) * perPage + 1;
  const to = Math.min(page * perPage, total);

  const pageNums: (number | "…")[] = [];
  for (let i = 1; i <= pages; i++) {
    if (i === 1 || i === pages || Math.abs(i - page) <= 2) {
      pageNums.push(i);
    } else if (pageNums[pageNums.length - 1] !== "…") {
      pageNums.push("…");
    }
  }

  return (
    <div className="flex items-center justify-between pt-4 text-sm text-[var(--muted-foreground)]">
      <span>
        {from}–{to} von {total}
      </span>
      <div className="flex items-center gap-1">
        <Button
          variant="outline"
          size="icon"
          onClick={() => onPageChange(page - 1)}
          disabled={page <= 1}
          aria-label="Vorherige Seite"
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>
        {pageNums.map((p, i) =>
          p === "…" ? (
            <span key={`ellipsis-${i}`} className="px-2">
              …
            </span>
          ) : (
            <Button
              key={p}
              variant={p === page ? "default" : "outline"}
              size="sm"
              onClick={() => onPageChange(p as number)}
              className="min-w-[2rem]"
            >
              {p}
            </Button>
          )
        )}
        <Button
          variant="outline"
          size="icon"
          onClick={() => onPageChange(page + 1)}
          disabled={page >= pages}
          aria-label="Nächste Seite"
        >
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
