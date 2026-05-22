import type {
  ESignResponse,
  GenerateSOWRequest,
  GenerateSOWResponse,
  PDFExportResponse,
  SOWDetail,
  SOWListItem,
  UpdateSOWResponse,
} from "@/lib/types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "http://localhost:8000";

export type ApiAuth = {
  token?: string | null | (() => Promise<string | null>);
  workspaceId?: string | null;
};

type RequestOptions = {
  method?: "GET" | "POST" | "PUT";
  body?: unknown;
  headers?: Record<string, string>;
  auth?: ApiAuth;
};

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const token =
    typeof options.auth?.token === "function"
      ? await options.auth.token()
      : options.auth?.token ?? null;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers ?? {}),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  if (options.auth?.workspaceId) {
    headers["X-Workspace-Id"] = options.auth.workspaceId;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: options.method ?? "GET",
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
    cache: "no-store",
  });

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const payload = (await response.json()) as { detail?: string };
      message = payload.detail ?? message;
    } catch {
      // Keep the HTTP status message when the backend returns non-JSON errors.
    }
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export function createApiClient(auth: ApiAuth) {
  return {
    baseUrl: API_BASE_URL,
    health: () => request<{ status: string; version?: string }>("/health"),
    generateSow: (payload: GenerateSOWRequest) =>
      request<GenerateSOWResponse>("/generate-sow", {
        method: "POST",
        body: payload,
        auth,
      }),
    listSows: () => request<SOWListItem[]>("/sows", { auth }),
    getSow: (sowId: string) => request<SOWDetail>(`/sows/${sowId}`, { auth }),
    updateSow: (
      sowId: string,
      payload: { content_json: unknown; content_markdown: string }
    ) =>
      request<UpdateSOWResponse>(`/sows/${sowId}`, {
        method: "PUT",
        body: payload,
        auth,
      }),
    exportPdf: (sowId: string) =>
      request<PDFExportResponse>(`/sows/${sowId}/export-pdf`, {
        method: "POST",
        auth,
      }),
    sendSignature: (sowId: string) =>
      request<ESignResponse>(`/sows/${sowId}/send-signature`, {
        method: "POST",
        auth,
      }),
    syncAuth: () =>
      request<{ user: unknown; workspace: unknown }>("/api/auth/sync", {
        method: "POST",
        auth,
      }),
    listWorkspaces: () => request<unknown[]>("/api/workspaces", { auth }),
    listProjects: () => request<unknown[]>("/api/projects", { auth }),
    createGeneration: (payload: GenerateSOWRequest) =>
      request<unknown>("/api/generations", { method: "POST", body: payload, auth }),
    getGeneration: (generationId: string) =>
      request<unknown>(`/api/generations/${generationId}`, { auth }),
    listBillingPlans: () => request<unknown[]>("/api/billing/plans"),
    getBillingStatus: () => request<unknown>("/api/billing/status", { auth }),
    getUsageSummary: () => request<unknown>("/api/billing/usage", { auth }),
    createCheckout: (payload: { plan: string; success_url: string; cancel_url: string }) =>
      request<{ checkout_url: string; demo_mode: boolean }>("/api/billing/checkout", {
        method: "POST",
        body: payload,
        auth,
      }),
    changePlan: (payload: { plan: string; success_url: string; cancel_url: string }) =>
      request<{ checkout_url?: string; status: string; message?: string }>("/api/billing/change-plan", {
        method: "POST",
        body: payload,
        auth,
      }),
    cancelSubscription: () =>
      request<{ status: string; message?: string }>("/api/billing/cancel", {
        method: "POST",
        auth,
      }),
    reactivateSubscription: () =>
      request<{ status: string; message?: string }>("/api/billing/reactivate", {
        method: "POST",
        auth,
      }),
    listTemplateIndustries: () => request<{ industries: string[] }>("/api/templates", { auth }),
    getTemplate: (industry: string) =>
      request<unknown>(`/api/templates/${encodeURIComponent(industry)}`, { auth }),
  };
}

export const publicApi = {
  baseUrl: API_BASE_URL,
  health: () => request<{ status: string; version?: string }>("/health"),
  listBillingPlans: () => request<unknown[]>("/api/billing/plans"),
};

export const api = createApiClient({});
