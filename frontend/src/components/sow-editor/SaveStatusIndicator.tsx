import { CheckCircle2, Cloud, LoaderCircle, TriangleAlert } from "lucide-react";
import { cn } from "@/lib/utils";

export type SaveStatus = "idle" | "saving" | "saved" | "error";

type SaveStatusIndicatorProps = {
  status: SaveStatus;
};

export function SaveStatusIndicator({ status }: SaveStatusIndicatorProps) {
  const config = {
    idle: {
      icon: Cloud,
      label: "Autosave ready",
      className: "text-slate-500",
    },
    saving: {
      icon: LoaderCircle,
      label: "Saving changes...",
      className: "text-amber-600",
    },
    saved: {
      icon: CheckCircle2,
      label: "Saved",
      className: "text-emerald-600",
    },
    error: {
      icon: TriangleAlert,
      label: "Save failed",
      className: "text-rose-600",
    },
  }[status];

  const Icon = config.icon;

  return (
    <div
      className={cn(
        "flex items-center gap-1.5 text-xs font-medium",
        config.className
      )}
    >
      <Icon
        className={cn("size-3.5", status === "saving" && "animate-spin")}
        aria-hidden="true"
      />
      {config.label}
    </div>
  );
}
