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

type RequestOptions = {
  method?: "GET" | "POST" | "PUT";
  body?: unknown;
  headers?: Record<string, string>;
};

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: options.method ?? "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: "Bearer demo",
      ...(options.headers ?? {}),
    },
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

export const api = {
  baseUrl: API_BASE_URL,
  health: () => request<{ status: string; version?: string }>("/health"),
  generateSow: (payload: GenerateSOWRequest) =>
    request<GenerateSOWResponse>("/generate-sow", {
      method: "POST",
      body: payload,
    }),
  listSows: () => request<SOWListItem[]>("/sows"),
  getSow: (sowId: string) => request<SOWDetail>(`/sows/${sowId}`),
  updateSow: (
    sowId: string,
    payload: { content_json: unknown; content_markdown: string }
  ) =>
    request<UpdateSOWResponse>(`/sows/${sowId}`, {
      method: "PUT",
      body: payload,
    }),
  exportPdf: (sowId: string) =>
    request<PDFExportResponse>(`/sows/${sowId}/export-pdf`, {
      method: "POST",
    }),
  sendSignature: (sowId: string) =>
    request<ESignResponse>(`/sows/${sowId}/send-signature`, {
      method: "POST",
    }),
  syncAuth: () => request<{ user: unknown; workspace: unknown }>("/api/auth/sync", { method: "POST" }),
  listWorkspaces: () => request<unknown[]>("/api/workspaces"),
  listProjects: () => request<unknown[]>("/api/projects"),
  createGeneration: (payload: GenerateSOWRequest) =>
    request<unknown>("/api/generations", { method: "POST", body: payload }),
  listBillingPlans: () => request<unknown[]>("/api/billing/plans"),
  getUsageSummary: () => request<unknown>("/api/billing/usage"),
  createCheckout: (payload: { plan: string; success_url: string; cancel_url: string }) =>
    request<{ checkout_url: string; demo_mode: boolean }>("/api/billing/checkout", {
      method: "POST",
      body: payload,
    }),
  listTemplateIndustries: () => request<{ industries: string[] }>("/api/templates"),
  getTemplate: (industry: string) => request<unknown>(`/api/templates/${encodeURIComponent(industry)}`),
};
