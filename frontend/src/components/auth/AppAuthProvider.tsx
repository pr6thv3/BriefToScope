"use client";

import { ClerkProvider, useAuth, useUser } from "@clerk/nextjs";
import {
  createContext,
  type ReactNode,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { identifyUser, trackEvent } from "@/lib/analytics";
import { can, normalizeRole, type WorkspacePermission, type WorkspaceRole } from "@/lib/rbac";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "http://localhost:8000";
const CLERK_PUBLISHABLE_KEY = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;

type WorkspaceState = {
  id: string;
  name: string;
  role: WorkspaceRole;
  plan?: string;
  subscription_status?: string;
};

type AuthSyncResponse = {
  user?: unknown;
  workspace?: {
    id?: string;
    name?: string;
    role?: string;
    plan?: string;
    subscription_status?: string;
  };
};

type AppAuthContextValue = {
  isLoaded: boolean;
  isSignedIn: boolean;
  userId: string | null;
  workspace: WorkspaceState | null;
  workspaceId: string | null;
  role: WorkspaceRole | null;
  syncError: string | null;
  getToken: () => Promise<string | null>;
  refreshWorkspace: () => Promise<void>;
  can: (permission: WorkspacePermission) => boolean;
};

const AppAuthContext = createContext<AppAuthContextValue | null>(null);

const unauthenticatedContext: AppAuthContextValue = {
  isLoaded: true,
  isSignedIn: false,
  userId: null,
  workspace: null,
  workspaceId: null,
  role: null,
  syncError: null,
  getToken: async () => null,
  refreshWorkspace: async () => undefined,
  can: () => false,
};

export function AppAuthProvider({ children }: { children: ReactNode }) {
  if (!CLERK_PUBLISHABLE_KEY) {
    return (
      <AppAuthContext.Provider value={unauthenticatedContext}>
        {children}
      </AppAuthContext.Provider>
    );
  }

  return (
    <ClerkProvider publishableKey={CLERK_PUBLISHABLE_KEY}>
      <ClerkSessionBridge>{children}</ClerkSessionBridge>
    </ClerkProvider>
  );
}

function ClerkSessionBridge({ children }: { children: ReactNode }) {
  const { isLoaded, isSignedIn, getToken, userId } = useAuth();
  const { user } = useUser();
  const [workspace, setWorkspace] = useState<WorkspaceState | null>(null);
  const [syncError, setSyncError] = useState<string | null>(null);

  const refreshWorkspace = useCallback(async () => {
    if (!isLoaded || !isSignedIn) {
      setWorkspace(null);
      return;
    }

    const token = await getToken();
    if (!token) {
      setWorkspace(null);
      setSyncError("Unable to read Clerk session token.");
      return;
    }

    const preferredWorkspaceId =
      typeof window !== "undefined" ? window.localStorage.getItem("brieftoscope.workspace_id") : null;

    const response = await fetch(`${API_BASE_URL}/api/auth/sync`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
        ...(preferredWorkspaceId ? { "X-Workspace-Id": preferredWorkspaceId } : {}),
      },
      cache: "no-store",
    });

    if (!response.ok) {
      const payload = (await response.json().catch(() => ({}))) as { detail?: string };
      throw new Error(payload.detail ?? `Auth sync failed with status ${response.status}`);
    }

    const payload = (await response.json()) as AuthSyncResponse;
    const role = normalizeRole(payload.workspace?.role) ?? "owner";
    const nextWorkspace = payload.workspace?.id
      ? {
          id: payload.workspace.id,
          name: payload.workspace.name ?? user?.primaryEmailAddress?.emailAddress ?? "Workspace",
          role,
          plan: payload.workspace.plan,
          subscription_status: payload.workspace.subscription_status,
        }
      : null;

    setWorkspace(nextWorkspace);
    setSyncError(null);

    if (nextWorkspace && typeof window !== "undefined") {
      window.localStorage.setItem("brieftoscope.workspace_id", nextWorkspace.id);
      identifyUser(userId ?? currentUserId(payload), {
        email: user?.primaryEmailAddress?.emailAddress,
        workspace_id: nextWorkspace.id,
        workspace_role: nextWorkspace.role,
        plan: nextWorkspace.plan,
      });
      trackEvent("workspace_synced", {
        workspace_id: nextWorkspace.id,
        role: nextWorkspace.role,
        plan: nextWorkspace.plan,
        subscription_status: nextWorkspace.subscription_status,
      });
      const signupMarker = `brieftoscope.signup_seen.${userId ?? "unknown"}`;
      if (!window.localStorage.getItem(signupMarker)) {
        window.localStorage.setItem(signupMarker, "1");
        trackEvent("signup", { workspace_id: nextWorkspace.id });
      }
    }
  }, [getToken, isLoaded, isSignedIn, user?.primaryEmailAddress?.emailAddress, userId]);

  useEffect(() => {
    if (!isLoaded) {
      return;
    }

    if (!isSignedIn) {
      queueMicrotask(() => setWorkspace(null));
      return;
    }

    queueMicrotask(() => {
      void refreshWorkspace().catch((error: unknown) => {
        setWorkspace(null);
        setSyncError(error instanceof Error ? error.message : "Workspace sync failed.");
      });
    });
  }, [isLoaded, isSignedIn, refreshWorkspace]);

  const value = useMemo<AppAuthContextValue>(
    () => ({
      isLoaded,
      isSignedIn: Boolean(isSignedIn),
      userId: userId ?? null,
      workspace,
      workspaceId: workspace?.id ?? null,
      role: workspace?.role ?? null,
      syncError,
      getToken,
      refreshWorkspace,
      can: (permission) => can(workspace?.role, permission),
    }),
    [getToken, isLoaded, isSignedIn, refreshWorkspace, syncError, userId, workspace]
  );

  return <AppAuthContext.Provider value={value}>{children}</AppAuthContext.Provider>;
}

export function useAppAuth() {
  const context = useContext(AppAuthContext);
  if (!context) {
    throw new Error("useAppAuth must be used inside AppAuthProvider.");
  }

  return context;
}

function currentUserId(payload: AuthSyncResponse) {
  if (payload.user && typeof payload.user === "object" && "id" in payload.user) {
    return String((payload.user as { id?: unknown }).id ?? "");
  }
  return "";
}
