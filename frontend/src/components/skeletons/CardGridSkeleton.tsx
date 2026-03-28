import { Skeleton } from "@/components/ui/skeleton";

interface CardGridSkeletonProps {
  count?: number;
}

export function CardGridSkeleton({ count = 6 }: CardGridSkeletonProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="border border-[var(--border)] rounded-xl p-4 space-y-3">
          <Skeleton className="h-5 w-3/4" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-2/3" />
          <Skeleton className="h-8 w-24 mt-2" />
        </div>
      ))}
    </div>
  );
}
