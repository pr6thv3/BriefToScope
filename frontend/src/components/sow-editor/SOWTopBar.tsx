"use client";

import Link from "next/link";
import { ArrowLeft, Clock3, History } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ExportPDFButton } from "@/components/sow-editor/ExportPDFButton";
import { SaveStatus, SaveStatusIndicator } from "@/components/sow-editor/SaveStatusIndicator";
import { SendSignatureButton } from "@/components/sow-editor/SendSignatureButton";
import type { SOWStatus } from "@/lib/types";

type SOWTopBarProps = {
  title: string;
  status: SOWStatus | string;
  saveStatus: SaveStatus;
  lastEditedAt: string;
  isExporting: boolean;
  isSendingSignature: boolean;
  onExport: () => void;
  onOpenSignature: () => void;
  onOpenVersions: () => void;
};

export function SOWTopBar({
  title,
  status,
  saveStatus,
  lastEditedAt,
  isExporting,
  isSendingSignature,
  onExport,
  onOpenSignature,
  onOpenVersions,
}: SOWTopBarProps) {
  return (
    <header className="sticky top-0 z-30 border-b bg-white/90 backdrop-blur-xl">
      <div className="flex min-h-16 flex-wrap items-center justify-between gap-3 px-4 py-3 lg:px-6">
        <div className="flex min-w-0 items-center gap-3">
          <Link
            href="/dashboard"
            className="flex size-9 items-center justify-center rounded-lg border bg-white text-slate-500 transition hover:bg-slate-50 hover:text-slate-950"
            aria-label="Back to dashboard"
          >
            <ArrowLeft className="size-4" aria-hidden="true" />
          </Link>
          <div className="min-w-0">
            <div className="flex min-w-0 items-center gap-2">
              <h1 className="truncate text-base font-semibold text-slate-950 md:text-lg">
                {title}
              </h1>
              <StatusBadge status={status} />
            </div>
            <div className="mt-1 flex flex-wrap items-center gap-3 text-xs text-slate-500">
              <SaveStatusIndicator status={saveStatus} />
              <span className="flex items-center gap-1.5">
                <Clock3 className="size-3.5" aria-hidden="true" />
                Last edited {formatRelative(lastEditedAt)}
              </span>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            className="h-9 gap-2 bg-white"
            onClick={onOpenVersions}
          >
            <History data-icon="inline-start" />
            Versions
          </Button>
          <ExportPDFButton isExporting={isExporting} onExport={onExport} />
          <SendSignatureButton
            disabled={isSendingSignature}
            onClick={onOpenSignature}
          />
        </div>
      </div>
    </header>
  );
}

function StatusBadge({ status }: { status: SOWStatus | string }) {
  const normalized = status.toLowerCase();
  const classes =
    normalized === "signed"
      ? "border-emerald-200 bg-emerald-50 text-emerald-700"
      : normalized === "sent"
        ? "border-blue-200 bg-blue-50 text-blue-700"
        : normalized === "ready" || normalized === "final"
          ? "border-violet-200 bg-violet-50 text-violet-700"
          : "border-slate-200 bg-slate-100 text-slate-700";

  return (
    <Badge variant="outline" className={`shrink-0 text-xs capitalize ${classes}`}>
      {normalized}
    </Badge>
  );
}

function formatRelative(timestamp: string) {
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) {
    return "just now";
  }

  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(date);
}
