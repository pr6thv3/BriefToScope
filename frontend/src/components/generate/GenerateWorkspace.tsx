"use client";

import { useEffect, useRef, useState } from "react";
import { GeneratePayload, TranscriptPanel } from "./TranscriptPanel";
import { LiveGenerationCanvas } from "./LiveGenerationCanvas";
import { useAppAuth } from "@/components/auth/AppAuthProvider";
import { useApiClient } from "@/lib/use-api-client";
import { sampleTranscript, industries, tones } from "@/lib/demo";
import { contentToSections } from "@/lib/sow";
import type { GenerateSOWResponse, GenerationStep, SOWDetail } from "@/lib/types";

const INITIAL_STEPS: GenerationStep[] = [
  { id: "s1", label: "Analyzing transcript", description: "Cleaning messy notes and identifying project signals.", status: "waiting", icon: "" },
  { id: "s2", label: "Extracting deliverables", description: "Pulling goals, deliverables, budget mentions, deadlines, and stakeholders.", status: "waiting", icon: "" },
  { id: "s3", label: "Detecting scope risks", description: "Checking for ambiguity, missing ownership, vague requests, and scope-creep traps.", status: "waiting", icon: "" },
  { id: "s4", label: "Building commercial scope", description: "Converting rough discussion into bounded agency-grade scope language.", status: "waiting", icon: "" },
  { id: "s5", label: "Generating clauses", description: "Creating revision, payment, out-of-scope, responsibility, and change-request clauses.", status: "waiting", icon: "" },
  { id: "s6", label: "Composing SOW", description: "Assembling final client-ready Statement of Work.", status: "waiting", icon: "" },
  { id: "s7", label: "Running quality checks", description: "Checking completeness, risky wording, missing terms, and export readiness.", status: "waiting", icon: "" },
];

export function GenerateWorkspace() {
  const api = useApiClient();
  const auth = useAppAuth();
  const [payload, setPayload] = useState<GeneratePayload>({
    transcript: "",
    industry: industries[0],
    tone: tones[0],
    clientName: "",
    projectName: "",
    budget: "",
    timeline: "",
  });

  const [status, setStatus] = useState<"idle" | "generating" | "completed" | "error">("idle");
  const [steps, setSteps] = useState<GenerationStep[]>(INITIAL_STEPS);
  const [result, setResult] = useState<GenerateSOWResponse | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Cinematic timer reference
  const timerRef = useRef<number | null>(null);

  useEffect(() => {
    return () => {
      if (timerRef.current) window.clearInterval(timerRef.current);
    };
  }, []);

  const handleGenerate = async (submitPayload: GeneratePayload) => {
    if (!auth.can("sow:generate")) {
      setStatus("error");
      setErrorMsg("Your workspace role cannot generate SOWs.");
      return;
    }

    setStatus("generating");
    setResult(null);
    setErrorMsg(null);
    setSteps(INITIAL_STEPS.map(s => ({ ...s, status: "waiting" })));

    // Start cinematic progression
    let currentStepIndex = 0;
    
    // Function to visually advance steps while waiting for backend
    const advanceVisuals = () => {
      setSteps(prev => {
        const next = [...prev];
        // Mark previous as complete if not already
        if (currentStepIndex > 0 && next[currentStepIndex - 1].status === "active") {
          next[currentStepIndex - 1].status = "complete";
        }
        // Activate current
        if (currentStepIndex < next.length) {
          next[currentStepIndex].status = "active";
        }
        return next;
      });
      currentStepIndex++;
    };

    // First visual tick immediately
    advanceVisuals();
    // Tick every ~1.5 seconds for dramatic effect while API runs
    timerRef.current = window.setInterval(() => {
      if (currentStepIndex < INITIAL_STEPS.length) {
        advanceVisuals();
      } else if (timerRef.current) {
        window.clearInterval(timerRef.current);
      }
    }, 1500);

    try {
      const generationPayload = {
        transcript_text: submitPayload.transcript,
        industry: submitPayload.industry,
        tone: submitPayload.tone,
        client_name: submitPayload.clientName,
        project_name: submitPayload.projectName,
        budget: submitPayload.budget,
        timeline: submitPayload.timeline,
      };
      const job = (await api.createGeneration(generationPayload)) as {
        id: string;
        status: string;
        sow_id?: string;
        error?: string;
      };
      const completedJob = await waitForGeneration(job.id);
      if (!completedJob.sow_id) {
        throw new Error("Generation completed without a SOW id.");
      }
      const sow = (await api.getSow(completedJob.sow_id)) as SOWDetail;
      const response = buildGenerationResult(completedJob.sow_id, sow, submitPayload);

      // Clear interval and force all to complete
      if (timerRef.current) window.clearInterval(timerRef.current);
      setSteps(prev => prev.map(s => ({ ...s, status: "complete" })));
      setResult(response);
      setStatus("completed");

    } catch (err) {
      if (timerRef.current) window.clearInterval(timerRef.current);
      setSteps(prev => {
        const next = [...prev];
        const activeIdx = next.findIndex(s => s.status === "active");
        if (activeIdx !== -1) {
          next[activeIdx].status = "error";
        }
        return next;
      });
      setErrorMsg(err instanceof Error ? err.message : "Generation failed.");
      setStatus("error");
    }
  };

  async function waitForGeneration(generationId: string) {
    for (let attempt = 0; attempt < 180; attempt += 1) {
      const job = (await api.getGeneration(generationId)) as {
        id: string;
        status: string;
        progress?: number;
        current_step?: string;
        sow_id?: string;
        error?: string;
      };
      if (job.status === "completed") {
        return job;
      }
      if (job.status === "failed") {
        throw new Error(job.error || "Generation job failed.");
      }
      await delay(1000);
    }
    throw new Error("Generation timed out.");
  }

  const loadSample = () => {
    setPayload({
      transcript: sampleTranscript,
      industry: "Web Design / Branding",
      tone: "Premium Agency",
      clientName: "Luma Retail Co.",
      projectName: "Brand Identity + Webflow Website",
      budget: "$150k",
      timeline: "3 Months",
    });
  };

  const reset = () => {
    setPayload({ transcript: "", industry: industries[0], tone: tones[0], clientName: "", projectName: "", budget: "", timeline: "" });
    setStatus("idle");
    setResult(null);
    setSteps(INITIAL_STEPS);
    if (timerRef.current) window.clearInterval(timerRef.current);
  };

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 md:px-8">
      <div className="mb-8">
        <h1 className="text-3xl font-semibold tracking-tight text-slate-900">
          AI SOW Generator
        </h1>
        <p className="mt-2 text-sm text-slate-500">
          Transform messy discovery calls into polished, bounded Statements of Work.
        </p>
      </div>

      <div className="grid gap-8 lg:grid-cols-[400px_1fr]">
        <div className="order-2 lg:order-1">
          <TranscriptPanel 
            isGenerating={status === "generating"} 
            onGenerate={handleGenerate} 
            onReset={reset}
            onLoadSample={loadSample}
            payload={payload}
            onChange={(updates) => setPayload(p => ({ ...p, ...updates }))}
            canGenerate={auth.can("sow:generate")}
            disabledReason={
              auth.syncError ??
              "Your workspace role can review SOWs but cannot generate new documents."
            }
          />
        </div>
        <div className="order-1 lg:order-2">
          <LiveGenerationCanvas 
            steps={steps}
            status={status}
            result={result}
            errorMsg={errorMsg}
            onRetry={() => handleGenerate(payload)}
          />
        </div>
      </div>
    </div>
  );
}

function buildGenerationResult(
  sowId: string,
  sow: SOWDetail,
  payload: GeneratePayload
): GenerateSOWResponse {
  const sections = contentToSections(sow.content_json);
  return {
    success: true,
    project_id: "",
    transcript_id: "",
    sow_id: sowId,
    status: "generated",
    ai_pipeline: {},
    sow: {
      title: sow.title,
      content_json: sow.content_json as GenerateSOWResponse["sow"]["content_json"],
      content_markdown: sow.content_markdown,
      sections: sections.map((section) => ({
        key: section.section_key,
        title: section.section_title,
        content: section.content_markdown,
        order: section.order,
      })),
    },
    extracted_brief: {
      client_name: sow.client_name || payload.clientName,
      project_type: sow.project_name || payload.projectName,
      goals: [],
      deliverables: sections
        .filter((section) => section.section_key === "deliverables")
        .flatMap((section) => section.content_markdown.split("\n").filter(Boolean)),
      budget_mentions: payload.budget ? [payload.budget] : [],
      deadline_mentions: payload.timeline ? [payload.timeline] : [],
      unclear_items: [],
    },
    confidence_score: sow.confidence_score,
    risk_flags: sow.risk_flags ?? sow.risk_flags_json ?? [],
    quality: {
      overall_quality_score: sow.quality_score ?? 80,
      approval_status: "approved_with_warnings",
      ready_for_export: true,
      warnings: [],
    },
    metadata: {
      generation_time_ms: 0,
      demo_mode: false,
      model_used: "worker",
      fallback_used: false,
    },
  };
}

function delay(milliseconds: number) {
  return new Promise((resolve) => window.setTimeout(resolve, milliseconds));
}
