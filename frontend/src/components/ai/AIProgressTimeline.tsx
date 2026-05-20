"use client";

import { motion } from "framer-motion";
import { Check, CircleAlert, CircleDashed, LoaderCircle } from "lucide-react";
import type { GenerationStep } from "@/lib/types";
import { cn } from "@/lib/utils";

export function AIProgressTimeline({ steps }: { steps: GenerationStep[] }) {
  return (
    <div className="relative border-l border-slate-200/60 pl-6 ml-4 space-y-8 py-2">
      {steps.map((step) => {
        const isActive = step.status === "active";
        const isComplete = step.status === "complete";
        const isError = step.status === "error";
        const isWarning = step.status === "warning";
        const isWaiting = step.status === "waiting";

        return (
          <div key={step.id} className="relative group">
            {/* Node Marker */}
            <div
              className={cn(
                "absolute -left-[35px] top-1 flex size-5 items-center justify-center rounded-full border ring-4 ring-white transition-all duration-300",
                isActive
                  ? "border-sky-500 bg-sky-50 text-sky-500 ring-sky-50 shadow-[0_0_12px_rgba(14,165,233,0.5)]"
                  : isComplete
                  ? "border-emerald-500 bg-emerald-500 text-white"
                  : isError || isWarning
                  ? "border-amber-500 bg-amber-50 text-amber-500"
                  : "border-slate-200 bg-slate-50 text-slate-300"
              )}
            >
              {isActive ? (
                <LoaderCircle className="size-3 animate-spin" />
              ) : isComplete ? (
                <Check className="size-3" />
              ) : isError || isWarning ? (
                <CircleAlert className="size-3" />
              ) : (
                <CircleDashed className="size-3" />
              )}
            </div>

            {/* Content block */}
            <div className={cn("transition-opacity duration-300", isWaiting ? "opacity-40" : "opacity-100")}>
              <div className="flex items-center justify-between gap-4">
                <h4 className={cn("text-sm font-semibold tracking-tight", isActive ? "text-sky-600" : "text-slate-700")}>
                  {step.label}
                </h4>
                {(isComplete || isActive) && (
                  <motion.span 
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="text-[10px] font-medium uppercase tracking-wider text-slate-400"
                  >
                    {isActive ? "Running..." : "Done"}
                  </motion.span>
                )}
              </div>
              <p className="mt-1 text-sm text-slate-500 leading-relaxed max-w-sm">
                {step.description}
              </p>
              
              {/* Optional Inline Preview of AI output */}
              {step.outputPreview && (
                <motion.div
                  initial={{ opacity: 0, y: 5 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-3 overflow-hidden rounded-xl border border-slate-100 bg-slate-50/50 p-3 text-xs text-slate-600 shadow-sm"
                >
                  <p className="line-clamp-2">{step.outputPreview}</p>
                </motion.div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
