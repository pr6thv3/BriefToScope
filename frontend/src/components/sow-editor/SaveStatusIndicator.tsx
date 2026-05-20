"use client";

import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, Cloud, Loader2, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";

export type SaveStatus = "idle" | "saving" | "saved" | "error";

type SaveStatusIndicatorProps = {
  status: SaveStatus;
};

export function SaveStatusIndicator({ status }: SaveStatusIndicatorProps) {
  const config = {
    idle: {
      icon: Cloud,
      label: "Autosave active",
      className: "text-slate-400 bg-slate-50 border-slate-200/60",
      dotClass: "bg-slate-300",
    },
    saving: {
      icon: Loader2,
      label: "Syncing changes...",
      className: "text-amber-700 bg-amber-50/60 border-amber-200/50",
      dotClass: "bg-amber-500 animate-pulse shadow-[0_0_8px_rgba(245,158,11,0.5)]",
    },
    saved: {
      icon: CheckCircle2,
      label: "All changes saved",
      className: "text-emerald-700 bg-emerald-50/60 border-emerald-200/50",
      dotClass: "bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]",
    },
    error: {
      icon: AlertCircle,
      label: "Sync failed",
      className: "text-rose-700 bg-rose-50/60 border-rose-200/50",
      dotClass: "bg-rose-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]",
    },
  }[status];

  const Icon = config.icon;

  return (
    <div className="relative inline-flex items-center">
      <AnimatePresence mode="wait">
        <motion.div
          key={status}
          initial={{ opacity: 0, y: -6, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 6, scale: 0.95 }}
          transition={{ duration: 0.15, ease: "easeOut" }}
          className={cn(
            "flex items-center gap-2 rounded-full border px-2.5 py-1 text-xs font-medium backdrop-blur-sm shadow-sm transition-all",
            config.className
          )}
        >
          {/* Status Dot */}
          <span className={cn("size-1.5 rounded-full transition-all duration-300", config.dotClass)} />
          
          <Icon
            className={cn("size-3.5 opacity-90", status === "saving" && "animate-spin text-amber-500")}
            aria-hidden="true"
          />
          <span className="tracking-tight">{config.label}</span>
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
