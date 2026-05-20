"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  FileCheck2,
  Gauge,
  ShieldCheck,
  TriangleAlert,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

type QualityScoreCardProps = {
  qualityScore: number;
  confidenceScore: number;
  riskLevel: "low" | "medium" | "high";
  exportReadiness: string;
  missingItemsCount: number;
  vaguePhrasesCount: number;
  esignStatus: string;
};

export function QualityScoreCard({
  qualityScore,
  confidenceScore,
  riskLevel,
  exportReadiness,
  missingItemsCount,
  vaguePhrasesCount,
  esignStatus,
}: QualityScoreCardProps) {
  const normalizedConfidence =
    confidenceScore > 1 ? confidenceScore : confidenceScore * 100;

  // Let's create an animated counter for numbers
  const [displayQuality, setDisplayQuality] = useState(0);
  const [displayConfidence, setDisplayConfidence] = useState(0);

  useEffect(() => {
    const qTarget = Math.round(qualityScore);
    const cTarget = Math.round(normalizedConfidence);

    let qCurrent = 0;
    let cCurrent = 0;

    const qInterval = setInterval(() => {
      if (qCurrent < qTarget) {
        qCurrent += Math.ceil((qTarget - qCurrent) / 6);
        setDisplayQuality(qCurrent);
      } else {
        setDisplayQuality(qTarget);
        clearInterval(qInterval);
      }
    }, 30);

    const cInterval = setInterval(() => {
      if (cCurrent < cTarget) {
        cCurrent += Math.ceil((cTarget - cCurrent) / 6);
        setDisplayConfidence(cCurrent);
      } else {
        setDisplayConfidence(cTarget);
        clearInterval(cInterval);
      }
    }, 35);

    return () => {
      clearInterval(qInterval);
      clearInterval(cInterval);
    };
  }, [qualityScore, normalizedConfidence]);

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
            AI Quality Review
          </p>
          <h3 className="mt-1 text-base font-semibold text-slate-900">
            Document Health Check
          </h3>
        </div>
        <Badge
          variant="outline"
          className="border-emerald-200 bg-emerald-50 text-emerald-700 font-semibold"
        >
          <ShieldCheck className="mr-1 size-3 text-emerald-600" />
          Optimal
        </Badge>
      </div>

      <div className="mt-5 space-y-5">
        <MetricBar
          icon={Gauge}
          label="Quality Score"
          value={qualityScore}
          displayValue={displayQuality}
          colorClass="bg-gradient-to-r from-indigo-500 to-indigo-600"
        />
        <MetricBar
          icon={FileCheck2}
          label="Scope Confidence"
          value={normalizedConfidence}
          displayValue={displayConfidence}
          colorClass="bg-gradient-to-r from-emerald-500 to-emerald-600"
        />
      </div>

      <div className="mt-5 grid grid-cols-2 gap-2 border-t border-slate-100 pt-4">
        <ScoreTile 
          label="Risk Level" 
          value={capitalize(riskLevel)} 
          theme={riskLevel === "high" ? "danger" : riskLevel === "medium" ? "warning" : "success"}
        />
        <ScoreTile 
          label="Missing Items" 
          value={String(missingItemsCount)} 
          theme={missingItemsCount > 0 ? "warning" : "success"}
        />
        <ScoreTile 
          label="Vague Phrases" 
          value={String(vaguePhrasesCount)} 
          theme={vaguePhrasesCount > 0 ? "warning" : "success"}
        />
        <ScoreTile 
          label="E-sign Handoff" 
          value={formatStatus(esignStatus)} 
          theme={esignStatus === "signed" ? "success" : esignStatus === "sent" ? "info" : "default"}
        />
      </div>

      <div className={cn(
        "mt-4 rounded-lg border p-3 flex items-center gap-2 text-xs font-semibold shadow-sm transition-all",
        exportReadiness.toLowerCase() === "ready" 
          ? "bg-emerald-50/60 border-emerald-100 text-emerald-800" 
          : "bg-amber-50/60 border-amber-100 text-amber-800"
      )}>
        {exportReadiness.toLowerCase() === "ready" ? (
          <ShieldCheck className="size-4 text-emerald-600 shrink-0" aria-hidden="true" />
        ) : (
          <TriangleAlert className="size-4 text-amber-600 shrink-0" aria-hidden="true" />
        )}
        <span>Export readiness: <span className="underline">{formatStatus(exportReadiness)}</span></span>
      </div>
    </section>
  );
}

function MetricBar({
  icon: Icon,
  label,
  value,
  displayValue,
  colorClass,
}: {
  icon: typeof Gauge;
  label: string;
  value: number;
  displayValue: number;
  colorClass: string;
}) {
  return (
    <div>
      <div className="mb-2 flex items-center justify-between gap-3 text-xs font-semibold text-slate-600">
        <span className="flex items-center gap-1.5">
          <Icon className="size-4 text-slate-400" aria-hidden="true" />
          {label}
        </span>
        <span className="text-slate-900">{displayValue}%</span>
      </div>
      <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${value}%` }}
          transition={{ duration: 1.2, ease: "easeOut" }}
          className={cn("h-full rounded-full", colorClass)}
        />
      </div>
    </div>
  );
}

function ScoreTile({ 
  label, 
  value,
  theme = "default"
}: { 
  label: string; 
  value: string;
  theme?: "success" | "warning" | "danger" | "info" | "default";
}) {
  const styles = {
    success: "bg-emerald-50/40 border-emerald-100 text-emerald-700",
    warning: "bg-amber-50/40 border-amber-100 text-amber-700",
    danger: "bg-rose-50/40 border-rose-100 text-rose-700",
    info: "bg-blue-50/40 border-blue-100 text-blue-700",
    default: "bg-slate-50/40 border-slate-100 text-slate-600",
  }[theme];

  return (
    <div className={cn("rounded-lg border px-3 py-2.5 transition-colors", styles)}>
      <p className="text-[10px] font-bold uppercase tracking-wider opacity-80">{label}</p>
      <p className="mt-1 truncate text-xs font-bold leading-none">
        {value}
      </p>
    </div>
  );
}

function capitalize(value: string) {
  return value.charAt(0).toUpperCase() + value.slice(1);
}

function formatStatus(value: string) {
  return value
    .replace(/_/g, " ")
    .split(" ")
    .map(capitalize)
    .join(" ");
}
