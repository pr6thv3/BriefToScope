"use client";

import { useMemo } from "react";
import { useAppAuth } from "@/components/auth/AppAuthProvider";
import { createApiClient } from "@/lib/api";

export function useApiClient() {
  const { getToken, workspaceId } = useAppAuth();

  return useMemo(
    () =>
      createApiClient({
        token: getToken,
        workspaceId,
      }),
    [getToken, workspaceId]
  );
}

export function useApiAuth() {
  const { getToken, workspaceId } = useAppAuth();

  return useMemo(
    () => ({
      workspaceId,
      getToken,
    }),
    [getToken, workspaceId]
  );
}
