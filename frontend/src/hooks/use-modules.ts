'use client';

import { useQuery } from "@tanstack/react-query";
import {
  ApiError,
  subjects,
  type ModuleData,
  type ModuleDetailData,
  type SubjectData,
} from "@/lib/api-client";

export function useSubjectsWithModules(token: string | null) {
  return useQuery<
    { subjectList: SubjectData[]; modulesBySubject: Record<string, ModuleData[]> },
    ApiError
  >({
    queryKey: ["subjects", "with-modules", token],
    queryFn: async () => {
      const subjectList = await subjects.list(token as string);
      const modulesEntries = await Promise.all(
        subjectList.map(async (subject) => [subject.id, await subjects.modules(subject.id, token as string)] as const)
      );

      return {
        subjectList,
        modulesBySubject: Object.fromEntries(modulesEntries),
      };
    },
    enabled: Boolean(token),
  });
}

export function useModuleDetail(token: string | null, moduleId: string | null) {
  return useQuery<ModuleDetailData, ApiError>({
    queryKey: ["subjects", "module-detail", token, moduleId],
    queryFn: () => subjects.moduleDetail(moduleId as string, token as string),
    enabled: Boolean(token && moduleId),
  });
}