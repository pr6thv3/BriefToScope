import {
  CheckCircle2,
  FileCheck2,
  Gauge,
  ShieldCheck,
  TriangleAlert,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";

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

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            AI quality review
          </p>
          <h3 className="mt-1 text-lg font-semibold text-slate-950">
            Ready for client review
          </h3>
        </div>
        <Badge
          variant="outline"
          className="border-emerald-200 bg-emerald-50 text-emerald-700"
        >
          <ShieldCheck data-icon="inline-start" />
          Ready
        </Badge>
      </div>

      <div className="mt-5 space-y-5">
        <MetricBar
          icon={Gauge}
          label="Quality Score"
          value={Math.round(qualityScore)}
          colorClass="[&_[data-slot=progress-indicator]]:bg-blue-600"
        />
        <MetricBar
          icon={FileCheck2}
          label="Scope Confidence"
          value={Math.round(normalizedConfidence)}
          colorClass="[&_[data-slot=progress-indicator]]:bg-emerald-600"
        />
      </div>

      <div className="mt-5 grid grid-cols-2 gap-2 border-t border-slate-100 pt-4">
        <ScoreTile label="Risk Level" value={capitalize(riskLevel)} />
        <ScoreTile label="Missing Items" value={String(missingItemsCount)} />
        <ScoreTile label="Vague Phrases" value={String(vaguePhrasesCount)} />
        <ScoreTile label="E-sign" value={formatStatus(esignStatus)} />
      </div>

      <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50 p-3">
        <div className="flex items-center gap-2 text-sm font-medium text-slate-800">
          {exportReadiness.toLowerCase() === "ready" ? (
            <CheckCircle2 className="size-4 text-emerald-600" aria-hidden="true" />
          ) : (
            <TriangleAlert className="size-4 text-amber-600" aria-hidden="true" />
          )}
          Export Readiness: {formatStatus(exportReadiness)}
        </div>
      </div>
    </section>
  );
}

function MetricBar({
  icon: Icon,
  label,
  value,
  colorClass,
}: {
  icon: typeof Gauge;
  label: string;
  value: number;
  colorClass: string;
}) {
  return (
    <div>
      <div className="mb-2 flex items-center justify-between gap-3 text-sm">
        <span className="flex items-center gap-2 font-medium text-slate-700">
          <Icon className="size-4 text-slate-400" aria-hidden="true" />
          {label}
        </span>
        <span className="font-semibold text-slate-950">{value}</span>
      </div>
      <Progress
        value={value}
        className={`[&_[data-slot=progress-track]]:bg-slate-100 ${colorClass}`}
      />
    </div>
  );
}

function ScoreTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white px-3 py-3">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="mt-1 truncate text-sm font-semibold text-slate-950">
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
