"use client";

import { motion } from "framer-motion";
import {
  CheckCircle2,
  FileText,
  Info,
  ScanSearch,
  ShieldAlert,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { QualityScoreCard } from "@/components/sow-editor/QualityScoreCard";
import { RiskCard } from "@/components/sow-editor/RiskCard";
import type { RiskFlag } from "@/lib/types";

type IntelligenceSidebarProps = {
  qualityScore: number;
  confidenceScore: number;
  riskFlags: RiskFlag[];
  missingInformation: string[];
  vagueWarnings: string[];
  exportStatus: string;
  esignStatus: string;
  riskLevel: "low" | "medium" | "high";
};

export function IntelligenceSidebar({
  qualityScore,
  confidenceScore,
  riskFlags,
  missingInformation,
  vagueWarnings,
  exportStatus,
  esignStatus,
  riskLevel,
}: IntelligenceSidebarProps) {
  return (
    <aside className="space-y-5">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Agency intelligence
          </p>
          <h2 className="mt-1 text-lg font-semibold text-slate-950">
            Scope risk review
          </h2>
        </div>
        <Badge
          variant="outline"
          className="border-blue-200 bg-blue-50 text-blue-700"
        >
          <ScanSearch data-icon="inline-start" />
          AI review
        </Badge>
      </div>

      <motion.div
        initial={{ opacity: 0, x: 16 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.22 }}
      >
        <QualityScoreCard
          qualityScore={qualityScore}
          confidenceScore={confidenceScore}
          riskLevel={riskLevel}
          exportReadiness={exportStatus}
          missingItemsCount={missingInformation.length}
          vaguePhrasesCount={vagueWarnings.length}
          esignStatus={esignStatus}
        />
      </motion.div>

      <motion.section
        initial={{ opacity: 0, x: 16 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.06, duration: 0.22 }}
        className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
      >
        <h3 className="flex items-center gap-2 text-sm font-semibold text-slate-950">
          <CheckCircle2 className="size-4 text-emerald-600" aria-hidden="true" />
          AI reviewed this SOW
        </h3>
        <div className="mt-4 space-y-3 text-sm text-slate-700">
          <ChecklistItem label="Payment terms included" />
          <ChecklistItem label="Revision policy defined" />
          <ChecklistItem label="Ready for export" />
          <ChecklistItem label="No risky guarantees detected" />
        </div>
      </motion.section>

      <motion.section
        initial={{ opacity: 0, x: 16 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.1, duration: 0.22 }}
        className="space-y-3"
      >
        <div className="flex items-center justify-between gap-3">
          <h3 className="flex items-center gap-2 text-sm font-semibold text-slate-950">
            <ShieldAlert className="size-4 text-amber-600" aria-hidden="true" />
            {riskFlags.length} scope risks detected
          </h3>
        </div>
        {riskFlags.length > 0 ? (
          riskFlags.map((risk) => <RiskCard key={risk.title} risk={risk} />)
        ) : (
          <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800">
            No material scope risks detected.
          </div>
        )}
      </motion.section>

      <motion.section
        initial={{ opacity: 0, x: 16 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.14, duration: 0.22 }}
        className="grid gap-3"
      >
        <SignalPanel
          icon={Info}
          title="Missing information"
          items={missingInformation}
          emptyLabel="No required items missing"
        />
        <SignalPanel
          icon={FileText}
          title="Vague wording warnings"
          items={vagueWarnings}
          emptyLabel="No vague phrases detected"
        />
      </motion.section>
    </aside>
  );
}

function ChecklistItem({ label }: { label: string }) {
  return (
    <div className="flex items-center gap-2">
      <CheckCircle2 className="size-4 text-emerald-600" aria-hidden="true" />
      <span>{label}</span>
    </div>
  );
}

function SignalPanel({
  icon: Icon,
  title,
  items,
  emptyLabel,
}: {
  icon: typeof Info;
  title: string;
  items: string[];
  emptyLabel: string;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <h3 className="flex items-center gap-2 text-sm font-semibold text-slate-950">
        <Icon className="size-4 text-slate-500" aria-hidden="true" />
        {title}
      </h3>
      <div className="mt-3 space-y-2">
        {items.length > 0 ? (
          items.map((item) => (
            <div
              key={item}
              className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-700"
            >
              {item}
            </div>
          ))
        ) : (
          <p className="text-sm text-slate-500">{emptyLabel}</p>
        )}
      </div>
    </div>
  );
}
