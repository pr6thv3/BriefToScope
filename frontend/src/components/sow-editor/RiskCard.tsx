import { AlertTriangle, Info, ShieldAlert } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { RiskFlag } from "@/lib/types";

type RiskCardProps = {
  risk: RiskFlag;
};

export function RiskCard({ risk }: RiskCardProps) {
  const config = {
    high: {
      icon: ShieldAlert,
      badge: "border-rose-200 bg-rose-50 text-rose-700",
      card: "border-rose-200 bg-rose-50/70",
      iconClass: "text-rose-600",
    },
    medium: {
      icon: AlertTriangle,
      badge: "border-amber-200 bg-amber-50 text-amber-700",
      card: "border-amber-200 bg-amber-50/70",
      iconClass: "text-amber-600",
    },
    low: {
      icon: Info,
      badge: "border-blue-200 bg-blue-50 text-blue-700",
      card: "border-blue-200 bg-blue-50/70",
      iconClass: "text-blue-600",
    },
  }[risk.severity];

  const Icon = config.icon;

  return (
    <article className={`rounded-xl border p-4 ${config.card}`}>
      <div className="flex items-start gap-3">
        <div className="mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-lg bg-white/80">
          <Icon className={`size-4 ${config.iconClass}`} aria-hidden="true" />
        </div>
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <h4 className="text-sm font-semibold text-slate-950">
              {risk.title}
            </h4>
            <Badge
              variant="outline"
              className={`h-5 capitalize ${config.badge}`}
            >
              {risk.severity}
            </Badge>
          </div>
          <p className="mt-2 text-sm leading-6 text-slate-700">
            {risk.description}
          </p>
          <p className="mt-3 text-xs font-medium leading-5 text-slate-600">
            Suggested fix: {risk.suggested_fix}
          </p>
        </div>
      </div>
    </article>
  );
}
