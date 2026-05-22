import type { ApiAuth } from "@/lib/api";
import type {
  ESignResponse,
  PDFExportResponse,
  RegenerateSectionResponse,
  SendSignaturePayload,
  SOWDetail,
  SOWSectionKey,
  UpdateSOWPayload,
  UpdateSOWResponse,
} from "@/lib/types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "http://localhost:8000";

type RequestOptions = {
  method?: "GET" | "POST" | "PUT";
  body?: unknown;
  auth?: ApiAuth;
};

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const token =
    typeof options.auth?.token === "function"
      ? await options.auth.token()
      : options.auth?.token ?? null;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
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
      // Keep status-based message when the backend does not return JSON.
    }
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

async function sowRequest<T>(
  apiPath: string,
  backendPath: string,
  options: RequestOptions = {}
) {
  try {
    return await request<T>(apiPath, options);
  } catch (error) {
    const message = error instanceof Error ? error.message : "";
    if (!message.includes("404") && !message.includes("Not Found")) {
      throw error;
    }
    return request<T>(backendPath, options);
  }
}

export function getSOW(id: string, auth?: ApiAuth) {
  return sowRequest<SOWDetail>(`/api/sows/${id}`, `/sows/${id}`, { auth });
}

export function updateSOW(id: string, payload: UpdateSOWPayload, auth?: ApiAuth) {
  return sowRequest<UpdateSOWResponse>(`/api/sows/${id}`, `/sows/${id}`, {
    method: "PUT",
    body: payload,
    auth,
  });
}

export function exportSOWPDF(id: string, auth?: ApiAuth) {
  return sowRequest<PDFExportResponse>(
    `/api/sows/${id}/export-pdf`,
    `/sows/${id}/export-pdf`,
    {
      method: "POST",
      auth,
    }
  );
}

export function sendSOWSignature(
  id: string,
  payload: SendSignaturePayload = {},
  auth?: ApiAuth
) {
  return sowRequest<ESignResponse>(
    `/api/sows/${id}/send-signature`,
    `/sows/${id}/send-signature`,
    {
      method: "POST",
      body: payload,
      auth,
    }
  );
}

export async function regenerateSOWSection(
  id: string,
  sectionKey: SOWSectionKey,
  currentMarkdown: string,
  auth?: ApiAuth
) {
  return sowRequest<RegenerateSectionResponse>(
    `/api/sows/${id}/regenerate-section`,
    `/sows/${id}/regenerate-section`,
    {
      method: "POST",
      body: {
        section_key: sectionKey,
        current_markdown: currentMarkdown,
      },
      auth,
    }
  );
}
