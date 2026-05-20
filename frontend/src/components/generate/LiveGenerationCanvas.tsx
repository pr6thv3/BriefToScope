"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, AlertCircle } from "lucide-react";
import type { GenerateSOWResponse, GenerationStep } from "@/lib/types";
import { AIProgressTimeline } from "@/components/ai/AIProgressTimeline";
import { AIExtractionCards } from "@/components/ai/AIExtractionCards";
import { DeliverableCards } from "@/components/ai/DeliverableCards";
import { ScopeRiskCards } from "@/components/ai/ScopeRiskCards";
import { CommercialScopePreview } from "@/components/ai/CommercialScopePreview";
import { ClausePreview } from "@/components/ai/ClausePreview";
import { SOWPreviewEditor } from "@/components/sow/SOWPreviewEditor";
import { QualityPanel } from "@/components/sow/QualityPanel";
import { ExportActions } from "@/components/sow/ExportActions";
import { Button } from "@/components/ui/button";

type LiveGenerationCanvasProps = {
  steps: GenerationStep[];
  status: "idle" | "generating" | "completed" | "error";
  result: GenerateSOWResponse | null;
  errorMsg: string | null;
  onRetry: () => void;
};

export function LiveGenerationCanvas({ steps, status, result, errorMsg, onRetry }: LiveGenerationCanvasProps) {
  
  if (status === "idle") {
    return (
      <div className="flex h-full min-h-[600px] flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-slate-50/50 p-8 text-center">
        <div className="mb-4 flex size-16 items-center justify-center rounded-2xl bg-white shadow-sm border border-slate-100 text-sky-500">
          <Sparkles className="size-8" />
        </div>
        <h3 className="mb-2 text-xl font-semibold text-slate-800">AI Intelligence Canvas</h3>
        <p className="max-w-md text-sm text-slate-500 leading-relaxed">
          Paste your messy call notes on the left and click Generate. 
          Watch as our expert AI agents clean the transcript, detect scope risks, and author a premium Statement of Work in seconds.
        </p>
        <div className="mt-8 flex flex-wrap justify-center gap-3 opacity-60">
          {["Extraction", "Risk Detection", "Scope Building", "Clauses", "SOW Authoring"].map(label => (
            <div key={label} className="rounded-full bg-slate-200 px-3 py-1 text-xs font-medium text-slate-600">
              {label}
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="flex h-full min-h-[600px] flex-col items-center justify-center rounded-2xl border border-rose-200 bg-rose-50 p-8 text-center">
        <div className="mb-4 flex size-16 items-center justify-center rounded-2xl bg-white shadow-sm border border-rose-100 text-rose-500">
          <AlertCircle className="size-8" />
        </div>
        <h3 className="mb-2 text-xl font-semibold text-rose-800">Generation Failed</h3>
        <p className="max-w-md text-sm text-rose-600 mb-6">{errorMsg || "An unexpected error occurred."}</p>
        <Button onClick={onRetry} variant="outline" className="border-rose-300 text-rose-700 hover:bg-rose-100">
          Try Again
        </Button>
      </div>
    );
  }

  // Active or Completed state
  const activeStepIndex = steps.findIndex(s => s.status === "active" || s.status === "error");
  const progressIndex = activeStepIndex === -1 ? steps.length : activeStepIndex;

  return (
    <div className="flex flex-col gap-8 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm min-h-[800px]">
      <div className="flex items-center gap-3 border-b pb-4">
        <div className="flex size-10 items-center justify-center rounded-xl bg-slate-900 text-white shadow-sm">
          <Sparkles className="size-5" />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-slate-800">Live AI Generation</h2>
          <p className="text-xs text-slate-500">Progressive reasoning and bounding</p>
        </div>
      </div>

      <div className="grid gap-8 lg:grid-cols-[280px_1fr] items-start">
        
        {/* Timeline Column */}
        <div className="sticky top-24">
          <AIProgressTimeline steps={steps} />
        </div>

        {/* Content Column */}
        <div className="space-y-12">
          
          <AnimatePresence>
            {/* Step 1: Extraction */}
            {progressIndex >= 1 && result && (
              <AIExtractionCards key="extraction-cards" brief={result.extracted_brief} />
            )}

            {/* Step 2: Deliverables */}
            {progressIndex >= 2 && result && (
              <DeliverableCards key="deliverable-cards" deliverables={result.extracted_brief.deliverables} confidence={result.confidence_score} />
            )}

            {/* Step 3: Risks */}
            {progressIndex >= 3 && result && (
              <ScopeRiskCards key="risk-cards" risks={result.risk_flags} />
            )}

            {/* Step 4: Commercial Scope */}
            {progressIndex >= 4 && result && (
              <CommercialScopePreview key="commercial-scope" sow={result.sow} />
            )}

            {/* Step 5: Clauses */}
            {progressIndex >= 5 && result && (
              <ClausePreview key="clauses" sow={result.sow} />
            )}

            {/* Step 6 & 7: Final SOW & Quality */}
            {status === "completed" && result && (
              <motion.div
                key="final-sow-container"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-8 border-t pt-8"
              >
                <SOWPreviewEditor sow={result.sow} sowId={result.sow_id} />
                <QualityPanel 
                  qualityScore={result.quality.overall_quality_score}
                  extractionScore={91}
                  clarityScore={84}
                  riskScore={93}
                  exportScore={88}
                />
                <ExportActions sowId={result.sow_id} />
              </motion.div>
            )}
          </AnimatePresence>

        </div>
      </div>
    </div>
  );
}
