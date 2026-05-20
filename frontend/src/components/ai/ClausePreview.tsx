"use client";

import { motion } from "framer-motion";
import { CreditCard, RotateCcw } from "lucide-react";
import type { SowDetails } from "@/lib/types";

export function ClausePreview({ sow }: { sow?: SowDetails }) {
  if (!sow?.content_json) return null;

  const content = sow.content_json;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-4"
    >
      <h4 className="text-sm font-semibold text-slate-700">Generated Legal & Commercial Clauses</h4>
      
      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-xl border bg-slate-50 p-4">
          <div className="flex items-center gap-2 font-medium text-slate-700 mb-2 text-sm">
            <RotateCcw className="size-4 text-indigo-500" /> Revision Policy
          </div>
          <p className="text-xs text-slate-600 italic border-l-2 border-indigo-200 pl-3">
            &quot;{content.revision_policy}&quot;
          </p>
        </div>

        <div className="rounded-xl border bg-slate-50 p-4">
          <div className="flex items-center gap-2 font-medium text-slate-700 mb-2 text-sm">
            <CreditCard className="size-4 text-emerald-500" /> Payment Schedule
          </div>
          <ul className="space-y-1">
            {(content.payment_schedule || []).map((payment: string, i: number) => (
              <li key={i} className="text-xs text-slate-600 border-b border-slate-200/50 pb-1 last:border-0 last:pb-0">
                {payment}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </motion.div>
  );
}
