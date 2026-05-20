import { defaultSectionQuality } from "@/lib/sow";
import type {
  ESignResponse,
  PDFExportResponse,
  RegenerateSectionResponse,
  SendSignaturePayload,
  SOWDetail,
  SOWSection,
  SOWSectionKey,
  UpdateSOWPayload,
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

export function getSOW(id: string) {
  return sowRequest<SOWDetail>(`/api/sows/${id}`, `/sows/${id}`);
}

export function updateSOW(id: string, payload: UpdateSOWPayload) {
  return sowRequest<UpdateSOWResponse>(`/api/sows/${id}`, `/sows/${id}`, {
    method: "PUT",
    body: payload,
  });
}

export function exportSOWPDF(id: string) {
  return sowRequest<PDFExportResponse>(
    `/api/sows/${id}/export-pdf`,
    `/sows/${id}/export-pdf`,
    {
      method: "POST",
    }
  );
}

export function sendSOWSignature(
  id: string,
  payload: SendSignaturePayload = {}
) {
  return sowRequest<ESignResponse>(
    `/api/sows/${id}/send-signature`,
    `/sows/${id}/send-signature`,
    {
      method: "POST",
      body: payload,
    }
  );
}

export async function regenerateSOWSection(
  id: string,
  sectionKey: SOWSectionKey,
  currentMarkdown: string
) {
  try {
    return await sowRequest<RegenerateSectionResponse>(
      `/api/sows/${id}/regenerate-section`,
      `/sows/${id}/regenerate-section`,
      {
        method: "POST",
        body: {
          section_key: sectionKey,
          current_markdown: currentMarkdown,
        },
      }
    );
  } catch {
    return {
      section: buildMockRegeneratedSection(sectionKey, currentMarkdown),
    };
  }
}

function buildMockRegeneratedSection(
  sectionKey: SOWSectionKey,
  currentMarkdown: string
): SOWSection {
  const additions: Record<SOWSectionKey, string> = {
    project_overview:
      "This language has been tightened to read as a client-ready commercial summary with clearer responsibility boundaries.",
    objectives:
      "- Confirm project outcomes through measurable approval checkpoints.\n- Keep scope decisions tied to the agreed brand and website deliverables.",
    scope_of_work:
      "- Clarify that any added pages, integrations, or content services require a written change order.",
    deliverables:
      "- Delivery includes source-ready brand and Webflow assets after final payment is received.",
    timeline:
      "- Timeline is dependent on client feedback windows and timely delivery of final content/assets.",
    payment_schedule:
      "- Work may pause if milestone payments are not received by the agreed due date.",
    client_responsibilities:
      "- Client will name one final decision-maker for approvals and launch readiness.",
    revision_policy:
      "Additional revisions beyond the two included rounds will be estimated and approved before work continues.",
    out_of_scope:
      "- Hosting ownership, copywriting, photography, and third-party integrations remain excluded unless added in writing.",
    assumptions:
      "- The agency is relying on complete, accurate, and timely client-provided content and platform access.",
    acceptance_criteria:
      "- Final acceptance occurs when the agreed deliverables are provided and no blocking defects remain against the approved scope.",
    signature_section:
      "Authorized representatives will confirm acceptance of scope, payment terms, and project responsibilities below.",
  };

  return {
    section_key: sectionKey,
    section_title: sectionKey
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" "),
    content_markdown: `${currentMarkdown.trim()}\n\n${additions[sectionKey]}`.trim(),
    order: 1,
    quality_score: Math.min(defaultSectionQuality(sectionKey) + 3, 99),
    last_regenerated_at: new Date().toISOString(),
  };
}
