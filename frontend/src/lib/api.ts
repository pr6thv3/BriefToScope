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
};

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: options.method ?? "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: "Bearer demo",
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
};
