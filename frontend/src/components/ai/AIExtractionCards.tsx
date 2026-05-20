"use client";

import { motion } from "framer-motion";
import { Briefcase, Building, Target, HelpCircle, Calendar, DollarSign, Users, Package } from "lucide-react";
import type { ExtractedBrief } from "@/lib/types";

export function AIExtractionCards({ brief }: { brief: ExtractedBrief }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="grid gap-4 sm:grid-cols-2"
    >
      <div className="rounded-xl border bg-white p-4 shadow-sm">
        <div className="flex items-center gap-2 text-sm font-medium text-slate-500 mb-2">
          <Building className="size-4 text-slate-400" />
          Detected Client
        </div>
        <p className="text-base font-semibold text-slate-800">{brief.client_name || "Unknown"}</p>
      </div>
      
      <div className="rounded-xl border bg-white p-4 shadow-sm">
        <div className="flex items-center gap-2 text-sm font-medium text-slate-500 mb-2">
          <Briefcase className="size-4 text-slate-400" />
          Project Type
        </div>
        <p className="text-base font-semibold text-slate-800">{brief.project_type || "General"}</p>
      </div>

      <div className="rounded-xl border bg-white p-4 shadow-sm">
        <div className="flex items-center gap-2 text-sm font-medium text-slate-500 mb-2">
          <Calendar className="size-4 text-slate-400" />
          Timeline
        </div>
        <p className="text-sm font-medium text-slate-700">{brief.timeline || "TBD (Not specified)"}</p>
      </div>

      <div className="rounded-xl border bg-white p-4 shadow-sm">
        <div className="flex items-center gap-2 text-sm font-medium text-slate-500 mb-2">
          <DollarSign className="size-4 text-slate-400" />
          Budget
        </div>
        <p className="text-sm font-medium text-slate-700">{brief.budget || "TBD (Not specified)"}</p>
      </div>

      <div className="rounded-xl border bg-white p-4 shadow-sm sm:col-span-2">
        <div className="flex items-center gap-2 text-sm font-medium text-slate-500 mb-2">
          <Target className="size-4 text-sky-500" />
          Primary Goals
        </div>
        <ul className="list-inside list-disc space-y-1 text-sm text-slate-700">
          {brief.goals?.length > 0 ? (
            brief.goals.map((goal, i) => <li key={i}>{goal}</li>)
          ) : (
            <li className="text-slate-400 italic">No explicit goals detected</li>
          )}
        </ul>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 sm:col-span-2">
        <div className="rounded-xl border bg-slate-50/50 p-4 shadow-sm">
          <div className="flex items-center gap-2 text-sm font-medium text-slate-500 mb-2">
            <Users className="size-4 text-indigo-400" />
            Stakeholders
          </div>
          <ul className="list-inside list-disc space-y-1 text-sm text-slate-600">
            {brief.stakeholders?.length ? (
              brief.stakeholders.map((s, i) => <li key={i}>{s}</li>)
            ) : (
              <li className="text-slate-400 italic">No specific stakeholders mentioned</li>
            )}
          </ul>
        </div>
        <div className="rounded-xl border bg-slate-50/50 p-4 shadow-sm">
          <div className="flex items-center gap-2 text-sm font-medium text-slate-500 mb-2">
            <Package className="size-4 text-emerald-400" />
            Assets Needed
          </div>
          <ul className="list-inside list-disc space-y-1 text-sm text-slate-600">
            {brief.assets_needed?.length ? (
              brief.assets_needed.map((a, i) => <li key={i}>{a}</li>)
            ) : (
              <li className="text-slate-400 italic">No specific assets mentioned</li>
            )}
          </ul>
        </div>
      </div>

      {brief.unclear_items?.length > 0 && (
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 shadow-sm sm:col-span-2">
          <div className="flex items-center gap-2 text-sm font-medium text-amber-700 mb-2">
            <HelpCircle className="size-4" />
            Unclear Items
          </div>
          <ul className="list-inside list-disc space-y-1 text-sm text-amber-800">
            {brief.unclear_items.map((item, i) => <li key={i}>{item}</li>)}
          </ul>
        </div>
      )}
    </motion.div>
  );
}
