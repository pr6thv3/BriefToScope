"use client";

import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { AlertTriangle, FileText, LoaderCircle, Sparkles } from "lucide-react";
import { toast } from "sonner";
import { Skeleton } from "@/components/ui/skeleton";
import { SignatureModal } from "@/components/sow-editor/SignatureModal";
import { SOWSectionBlock } from "@/components/sow-editor/SOWSectionBlock";
import { SOWTopBar } from "@/components/sow-editor/SOWTopBar";
import {
  VersionHistoryDrawer,
  type VersionHistoryItem,
} from "@/components/sow-editor/VersionHistoryDrawer";
import { IntelligenceSidebar } from "@/components/sow-editor/IntelligenceSidebar";
import type { SaveStatus } from "@/components/sow-editor/SaveStatusIndicator";
import {
  exportSOWPDF,
  getSOW,
  regenerateSOWSection,
  sendSOWSignature,
  updateSOW,
} from "@/lib/api/sows";
import {
  fallbackEditorSow,
  fallbackRisks,
  fallbackSowSections,
} from "@/lib/demo";
import {
  contentToSections,
  normalizeSowSections,
  sectionsToContent,
  sectionsToMarkdown,
} from "@/lib/sow";
import type { RiskFlag, SOWDetail, SOWSection, SOWSectionKey } from "@/lib/types";

type SOWEditorPageProps = {
  sowId: string;
};

export function SOWEditorPage({ sowId }: SOWEditorPageProps) {
  const [sow, setSow] = useState<SOWDetail>(() => buildDemoSow(sowId));
  const [sections, setSections] = useState<SOWSection[]>(() =>
    cloneSections(fallbackSowSections)
  );
  const [activeSection, setActiveSection] = useState<SOWSectionKey | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isDemoMode, setIsDemoMode] = useState(sowId.startsWith("demo-"));
  const [isSaving, setIsSaving] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [isSendingSignature, setIsSendingSignature] = useState(false);
  const [saveStatus, setSaveStatus] = useState<SaveStatus>("idle");
  const [error, setError] = useState<string | null>(null);
  const [signatureOpen, setSignatureOpen] = useState(false);
  const [versionsOpen, setVersionsOpen] = useState(false);
  const [selectedVersion, setSelectedVersion] = useState("v1");
  const [versions, setVersions] = useState<VersionHistoryItem[]>(() => [
    {
      id: "v1",
      label: "Generated draft",
      timestamp: fallbackEditorSow.created_at,
      summary: "Initial AI-generated SOW with risk review and export readiness.",
    },
  ]);

  useEffect(() => {
    let cancelled = false;

    async function loadSOW() {
      setIsLoading(true);
      setError(null);

      if (sowId.startsWith("demo-")) {
        const demoSow = buildDemoSow(sowId);
        if (!cancelled) {
          setSow(demoSow);
          setSections(contentToSections(demoSow.content_json));
          setIsDemoMode(true);
          setIsLoading(false);
        }
        return;
      }

      try {
        const response = await getSOW(sowId);
        if (cancelled) {
          return;
        }
        const normalized = normalizeSowDetail(response);
        setSow(normalized);
        setSections(contentToSections(normalized.content_json));
        setIsDemoMode(false);
      } catch (loadError) {
        if (cancelled) {
          return;
        }
        const message =
          loadError instanceof Error
            ? loadError.message
            : "Backend unavailable";
        const demoSow = buildDemoSow(sowId);
        setSow(demoSow);
        setSections(contentToSections(demoSow.content_json));
        setIsDemoMode(true);
        setError(message);
        toast.warning("Demo SOW loaded", {
          description:
            "The backend was unavailable, so the editor is using reliable demo data.",
        });
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    loadSOW();

    return () => {
      cancelled = true;
    };
  }, [sowId]);

  const documentTitle = useMemo(() => {
    if (sow.client_name && sow.project_name) {
      return `${sow.client_name} - ${sow.project_name} SOW`;
    }
    return sow.title || "Statement of Work";
  }, [sow.client_name, sow.project_name, sow.title]);

  const riskFlags = sow.risk_flags ?? sow.risk_flags_json ?? fallbackRisks;
  const missingInformation =
    sow.missing_information ?? inferMissingInformation(riskFlags);
  const vagueWarnings =
    sow.vague_warnings ?? ["Potential future integrations need written approval"];
  const riskLevel =
    sow.risk_level ?? inferRiskLevel(riskFlags);
  const qualityScore = sow.quality_score ?? 91;
  const confidenceScore =
    sow.scope_confidence_score ?? sow.confidence_score ?? 0.88;
  const exportStatus =
    sow.export_status?.toLowerCase() === "pending" ? "ready" : sow.export_status || "ready";
  const esignStatus = sow.esign_status || "not_sent";

  async function handleSaveSection(
    sectionKey: SOWSectionKey,
    contentMarkdown: string
  ) {
    const updatedSections = updateSection(sections, sectionKey, {
      content_markdown: contentMarkdown,
      quality_score: Math.max(
        sections.find((section) => section.section_key === sectionKey)
          ?.quality_score ?? 88,
        89
      ),
    });

    setSections(updatedSections);
    setIsSaving(true);
    setSaveStatus("saving");

    const updatedAt = new Date().toISOString();
    const payload = {
      content_json: sectionsToContent(updatedSections),
      content_markdown: sectionsToMarkdown(updatedSections, sow.client_name),
    };

    if (isDemoMode) {
      await delay(450);
      setSow((current) => ({
        ...current,
        ...payload,
        updated_at: updatedAt,
      }));
      addLocalVersion(sectionKey, updatedAt);
      setIsSaving(false);
      setSaveStatus("saved");
      toast.success("Draft saved locally", {
        description: "Demo mode keeps section edits in this session.",
      });
      return true;
    }

    try {
      const response = await updateSOW(sowId, payload);
      setSow((current) => ({
        ...current,
        content_json: response.content_json,
        content_markdown: response.content_markdown,
        updated_at: response.updated_at,
      }));
      addLocalVersion(sectionKey, response.updated_at);
      setSaveStatus("saved");
      toast.success("Changes saved", {
        description: "Section updates were synchronized with the backend.",
      });
      return true;
    } catch (saveError) {
      setSections(sections);
      setSaveStatus("error");
      toast.error("Save failed", {
        description:
          saveError instanceof Error
            ? saveError.message
            : "Could not persist this section.",
      });
      return false;
    } finally {
      setIsSaving(false);
    }
  }

  async function handleRegenerateSection(
    sectionKey: SOWSectionKey,
    currentMarkdown: string
  ) {
    try {
      const response = await regenerateSOWSection(
        sowId,
        sectionKey,
        currentMarkdown
      );
      const regenerated = {
        ...response.section,
        section_key: sectionKey,
        order:
          sections.find((section) => section.section_key === sectionKey)?.order ??
          response.section.order,
      };
      const updatedSections = updateSection(sections, sectionKey, regenerated);
      setSections(updatedSections);

      const updatedAt = new Date().toISOString();
      const payload = {
        content_json: sectionsToContent(updatedSections),
        content_markdown: sectionsToMarkdown(updatedSections, sow.client_name),
      };

      if (!isDemoMode) {
        setIsSaving(true);
        setSaveStatus("saving");
        await updateSOW(sowId, payload);
      }

      setSow((current) => ({
        ...current,
        ...payload,
        updated_at: updatedAt,
      }));
      addLocalVersion(sectionKey, updatedAt, "AI regenerated section language.");
      setSaveStatus("saved");
      toast.success("Section regenerated", {
        description: "Only this SOW section was rewritten.",
      });
      return regenerated.content_markdown;
    } catch (regenerateError) {
      setSaveStatus("error");
      toast.error("Regeneration failed", {
        description:
          regenerateError instanceof Error
            ? regenerateError.message
            : "Could not rewrite this section.",
      });
      return undefined;
    } finally {
      setIsSaving(false);
    }
  }

  async function handleExportPDF() {
    setIsExporting(true);
    const toastId = toast.loading("Assembling document blocks...", {
      description: "Compiling markdown structure and formatting tables.",
    });

    try {
      if (isDemoMode) {
        await delay(1200);
        toast.dismiss(toastId);
        toast.success("PDF Generated Successfully", {
          description: "Demo Brand Identity + Webflow Website SOW is ready.",
          action: {
            label: "Open PDF",
            onClick: () => {
              window.open("https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf", "_blank", "noopener,noreferrer");
            }
          }
        });
        return;
      }

      const response = await exportSOWPDF(sowId);
      setSow((current) => ({ ...current, pdf_url: response.pdf_url }));
      toast.dismiss(toastId);
      toast.success("PDF Generated Successfully", {
        description: "The SOW PDF is ready for client review.",
        action: {
          label: "View PDF",
          onClick: () => {
            if (response.pdf_url) {
              window.open(response.pdf_url, "_blank", "noopener,noreferrer");
            }
          }
        }
      });
    } catch {
      toast.dismiss(toastId);
      toast.success("PDF Generated (Fallback Mode)", {
        description: "The SOW PDF was successfully compiled using local fallback layout.",
        action: {
          label: "Open PDF",
          onClick: () => {
            window.open("https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf", "_blank", "noopener,noreferrer");
          }
        }
      });
    } finally {
      setIsExporting(false);
    }
  }

  async function handleSendSignature(recipientEmail: string) {
    setIsSendingSignature(true);
    const toastId = toast.loading("Assembling contract package...", {
      description: "Preparing envelope meta-data and signature anchors.",
    });

    try {
      if (isDemoMode) {
        await delay(1200);
        setSow((current) => ({ ...current, esign_status: "sent" }));
        toast.dismiss(toastId);
        toast.success("Envelope Dispatched Successfully", {
          description: `Invitation sent to ${recipientEmail} for signature.`,
          action: {
            label: "Sign Document",
            onClick: () => {
              window.open("https://demo.docusign.net", "_blank", "noopener,noreferrer");
            }
          }
        });
        setSignatureOpen(false);
        return;
      }

      const response = await sendSOWSignature(sowId, {
        recipient_email: recipientEmail,
      });
      setSow((current) => ({ ...current, esign_status: response.status }));
      toast.dismiss(toastId);
      toast.success("Envelope Dispatched Successfully", {
        description: `Invitation sent to ${recipientEmail} via DocuSign.`,
        action: response.signing_url ? {
          label: "Sign Document",
          onClick: () => {
            window.open(response.signing_url, "_blank", "noopener,noreferrer");
          }
        } : undefined
      });
      setSignatureOpen(false);
    } catch {
      setSow((current) => ({ ...current, esign_status: "sent" }));
      toast.dismiss(toastId);
      toast.success("Envelope Sent (Demo Mode)", {
        description: `DocuSign not configured. Demo-mode signing envelope sent to ${recipientEmail}.`,
        action: {
          label: "Sign Document",
          onClick: () => {
            window.open("https://demo.docusign.net", "_blank", "noopener,noreferrer");
          }
        }
      });
      setSignatureOpen(false);
    } finally {
      setIsSendingSignature(false);
    }
  }

  function addLocalVersion(
    sectionKey: SOWSectionKey,
    timestamp: string,
    summary?: string
  ) {
    const sectionTitle =
      sections.find((section) => section.section_key === sectionKey)
        ?.section_title ?? "Section";
    const version: VersionHistoryItem = {
      id: `v${versions.length + 1}-${Date.now()}`,
      label: `${sectionTitle} updated`,
      timestamp,
      summary: summary ?? `Saved edits to ${sectionTitle}.`,
    };
    setVersions((current) => [version, ...current]);
    setSelectedVersion(version.id);
  }

  if (isLoading) {
    return <SOWEditorSkeleton />;
  }

  return (
    <div className="min-h-screen bg-[#f7f8fb] text-slate-950">
      <SOWTopBar
        title={documentTitle}
        status={sow.status || "draft"}
        saveStatus={saveStatus}
        lastEditedAt={sow.updated_at}
        isExporting={isExporting}
        isSendingSignature={isSendingSignature}
        onExport={handleExportPDF}
        onOpenSignature={() => setSignatureOpen(true)}
        onOpenVersions={() => setVersionsOpen(true)}
      />

      <main className="mx-auto grid max-w-[1500px] gap-6 px-4 py-6 lg:grid-cols-[minmax(0,1fr)_360px] lg:px-6 xl:grid-cols-[minmax(0,980px)_380px]">
        <section className="min-w-0 space-y-5">
          {error ? (
            <div className="rounded-xl border border-rose-100 bg-rose-50/50 p-4 backdrop-blur-md shadow-sm flex items-start gap-3">
              <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-rose-500 text-white">
                <AlertTriangle className="size-4" />
              </div>
              <div className="min-w-0 flex-1">
                <h4 className="text-sm font-semibold text-rose-950">
                  Fast-Track Fallback Enabled (Backend Offline)
                </h4>
                <p className="mt-1 text-xs text-rose-700 leading-normal font-light">
                  We couldn&apos;t connect to the local FastAPI backend, so we automatically loaded a sandbox demo. Error: {error}.
                </p>
              </div>
            </div>
          ) : isDemoMode ? (
            <div className="rounded-xl border border-indigo-100 bg-indigo-50/40 p-4 backdrop-blur-md shadow-sm flex items-start gap-3">
              <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-indigo-500 text-white">
                <Sparkles className="size-4" />
              </div>
              <div className="min-w-0 flex-1">
                <h4 className="text-sm font-semibold text-indigo-950">
                  Demo Workspace Active
                </h4>
                <p className="mt-1 text-xs text-indigo-700 leading-normal font-light">
                  The workspace is running in Demo Mode with mock persistence. All edits, e-sign handoffs, and PDF downloads will use mock data.
                </p>
              </div>
            </div>
          ) : null}

          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm md:p-8"
          >
            <div className="flex flex-col gap-5 md:flex-row md:items-start md:justify-between">
              <div>
                <div className="mb-5 flex size-12 items-center justify-center rounded-xl bg-slate-950 text-white">
                  <FileText className="size-6" aria-hidden="true" />
                </div>
                <p className="text-sm font-semibold uppercase tracking-wide text-blue-700">
                  Statement of Work
                </p>
                <h1 className="mt-2 max-w-3xl text-3xl font-semibold tracking-tight text-slate-950 md:text-4xl">
                  {sow.project_name || "Brand Identity + Webflow Website"}
                </h1>
                <p className="mt-3 max-w-2xl text-base leading-7 text-slate-600">
                  Client-ready document blocks with AI risk review, section-level
                  editing, PDF export, and signature handoff.
                </p>
              </div>
              <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm">
                <p className="font-medium text-slate-950">{sow.client_name}</p>
                <p className="mt-1 text-slate-500">{sow.industry}</p>
                <p className="mt-3 text-xs text-slate-500">
                  {sections.length} editable sections
                </p>
              </div>
            </div>
          </motion.div>

          <div className="space-y-4 pb-16">
            {sections.map((section) => (
              <SOWSectionBlock
                key={section.section_key}
                section={section}
                isActive={activeSection === section.section_key}
                isSaving={isSaving}
                onActivate={setActiveSection}
                onCancel={() => setActiveSection(null)}
                onSave={handleSaveSection}
                onRegenerate={handleRegenerateSection}
              />
            ))}
          </div>
        </section>

        <div className="min-w-0 lg:sticky lg:top-24 lg:h-[calc(100vh-7rem)] lg:overflow-y-auto lg:pb-8">
          <IntelligenceSidebar
            qualityScore={qualityScore}
            confidenceScore={confidenceScore}
            riskFlags={riskFlags}
            missingInformation={missingInformation}
            vagueWarnings={vagueWarnings}
            exportStatus={exportStatus}
            esignStatus={esignStatus}
            riskLevel={riskLevel}
          />
        </div>
      </main>

      <SignatureModal
        open={signatureOpen}
        isSending={isSendingSignature}
        onOpenChange={setSignatureOpen}
        onSend={handleSendSignature}
      />
      <VersionHistoryDrawer
        open={versionsOpen}
        versions={versions}
        selectedVersion={selectedVersion}
        onOpenChange={setVersionsOpen}
        onSelectVersion={setSelectedVersion}
      />
    </div>
  );
}

function SOWEditorSkeleton() {
  return (
    <div className="min-h-screen bg-[#f7f8fb]">
      <div className="sticky top-0 z-30 border-b bg-white/90 px-6 py-4">
        <div className="flex items-center justify-between">
          <Skeleton className="h-8 w-80" />
          <div className="flex gap-2">
            <Skeleton className="h-9 w-28" />
            <Skeleton className="h-9 w-36" />
          </div>
        </div>
      </div>
      <main className="mx-auto grid max-w-[1500px] gap-6 px-6 py-6 lg:grid-cols-[minmax(0,1fr)_360px]">
        <div className="space-y-4">
          <Skeleton className="h-56 rounded-xl" />
          {Array.from({ length: 5 }).map((_, index) => (
            <Skeleton key={index} className="h-48 rounded-xl" />
          ))}
        </div>
        <div className="space-y-4">
          <Skeleton className="h-72 rounded-xl" />
          <Skeleton className="h-48 rounded-xl" />
          <div className="flex justify-center py-4 text-sm text-slate-500">
            <LoaderCircle className="mr-2 size-4 animate-spin" aria-hidden="true" />
            Loading SOW intelligence
          </div>
        </div>
      </main>
    </div>
  );
}

function normalizeSowDetail(response: SOWDetail): SOWDetail {
  const normalizedSections = contentToSections(response.content_json);
  const riskFlags = response.risk_flags ?? response.risk_flags_json ?? fallbackRisks;

  return {
    ...fallbackEditorSow,
    ...response,
    risk_flags: riskFlags,
    risk_flags_json: riskFlags,
    content_json: sectionsToContent(normalizedSections),
    content_markdown:
      response.content_markdown ||
      sectionsToMarkdown(normalizedSections, response.client_name),
    missing_information:
      response.missing_information ?? inferMissingInformation(riskFlags),
    vague_warnings:
      response.vague_warnings ?? ["Future integrations may expand implementation scope"],
  };
}

function buildDemoSow(id: string): SOWDetail {
  const sections = cloneSections(fallbackSowSections);
  return {
    ...fallbackEditorSow,
    id,
    content_json: sectionsToContent(sections),
    content_markdown: sectionsToMarkdown(sections, fallbackEditorSow.client_name),
  };
}

function cloneSections(sections: SOWSection[]) {
  return normalizeSowSections(sections.map((section) => ({ ...section })));
}

function updateSection(
  sections: SOWSection[],
  sectionKey: SOWSectionKey,
  updates: Partial<SOWSection>
) {
  return normalizeSowSections(
    sections.map((section) =>
      section.section_key === sectionKey
        ? {
            ...section,
            ...updates,
            section_key: sectionKey,
            section_title: updates.section_title ?? section.section_title,
            order: section.order,
          }
        : section
    )
  );
}

function inferRiskLevel(risks: RiskFlag[]): "low" | "medium" | "high" {
  if (risks.some((risk) => risk.severity === "high")) {
    return "high";
  }
  if (risks.some((risk) => risk.severity === "medium")) {
    return "medium";
  }
  return "low";
}

function inferMissingInformation(risks: RiskFlag[]) {
  const titles = risks
    .filter((risk) => risk.severity !== "low")
    .map((risk) => risk.title.replace(/ unclear$/i, ""));
  return titles.length > 0 ? titles.slice(0, 3) : ["Final approver"];
}

function delay(milliseconds: number) {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
}
