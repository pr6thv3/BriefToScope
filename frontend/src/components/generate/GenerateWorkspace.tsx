"use client";

import { useEffect, useRef, useState } from "react";
import { GeneratePayload, TranscriptPanel } from "./TranscriptPanel";
import { LiveGenerationCanvas } from "./LiveGenerationCanvas";
import { api } from "@/lib/api";
import { sampleTranscript, industries, tones } from "@/lib/demo";
import type { GenerateSOWResponse, GenerationStep } from "@/lib/types";

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
      const response = await api.generateSow({
        transcript_text: submitPayload.transcript,
        industry: submitPayload.industry,
        tone: submitPayload.tone,
        client_name: submitPayload.clientName,
        project_name: submitPayload.projectName,
        budget: submitPayload.budget,
        timeline: submitPayload.timeline,
      });

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
