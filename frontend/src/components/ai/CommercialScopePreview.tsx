"use client";

import { motion } from "framer-motion";
import { Check, X, ShieldAlert, Zap } from "lucide-react";
import type { SowDetails } from "@/lib/types";

export function CommercialScopePreview({ sow }: { sow?: SowDetails }) {
  if (!sow?.content_json) return null;

  const content = sow.content_json;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-4"
    >
      <h4 className="text-sm font-semibold text-slate-700">Commercial Scope Bounding</h4>
      
      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-xl border border-emerald-100 bg-emerald-50/50 p-4">
          <div className="flex items-center gap-2 font-medium text-emerald-800 mb-3 text-sm">
            <Check className="size-4" /> Included Work
          </div>
          <ul className="space-y-2">
            {(content.scope_of_work?.slice(0, 4) || []).map((item: string, i: number) => (
              <li key={i} className="flex gap-2 text-xs text-slate-700">
                <span className="mt-0.5 block size-1.5 shrink-0 rounded-full bg-emerald-400" />
                <span className="line-clamp-2">{item}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="rounded-xl border border-rose-100 bg-rose-50/50 p-4">
          <div className="flex items-center gap-2 font-medium text-rose-800 mb-3 text-sm">
            <X className="size-4" /> Excluded Work
          </div>
          <ul className="space-y-2">
            {(content.out_of_scope?.slice(0, 4) || []).map((item: string, i: number) => (
              <li key={i} className="flex gap-2 text-xs text-slate-700">
                <span className="mt-0.5 block size-1.5 shrink-0 rounded-full bg-rose-400" />
                <span className="line-clamp-2">{item}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-xl border bg-white p-4 shadow-sm">
          <div className="flex items-center gap-2 font-medium text-slate-700 mb-2 text-sm">
            <ShieldAlert className="size-4 text-amber-500" /> Dependencies
          </div>
          <p className="text-xs text-slate-500 line-clamp-3">
            {content.client_responsibilities?.[0] || "Client must provide timely feedback and assets."}
          </p>
        </div>

        <div className="rounded-xl border bg-white p-4 shadow-sm">
          <div className="flex items-center gap-2 font-medium text-slate-700 mb-2 text-sm">
            <Zap className="size-4 text-sky-500" /> Acceptance Criteria
          </div>
          <p className="text-xs text-slate-500 line-clamp-3">
            {content.acceptance_criteria?.[0] || "Deliverables must match agreed requirements."}
          </p>
        </div>
      </div>
    </motion.div>
  );
}
