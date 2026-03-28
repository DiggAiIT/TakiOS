'use client';

import { useQuery } from "@tanstack/react-query";
import {
  ApiError,
  levels,
  techUnits,
  type PyramidData,
  type TechUnitChainData,
  type TechUnitData,
} from "@/lib/api-client";

export function usePyramid(token: string | null) {
  return useQuery<PyramidData, ApiError>({
    queryKey: ["levels", "pyramid", token],
    queryFn: () => levels.pyramid(token as string),
    enabled: Boolean(token),
  });
}

export function useLevelDetail(token: string | null, levelId: string | null) {
  return useQuery<{ units: TechUnitData[]; chains: TechUnitChainData[] }, ApiError>({
    queryKey: ["levels", "detail", token, levelId],
    queryFn: async () => {
      const [units, chains] = await Promise.all([
        techUnits.list(token as string, levelId as string),
        techUnits.chains(levelId as string, token as string),
      ]);
      return { units, chains };
    },
    enabled: Boolean(token && levelId),
  });
}