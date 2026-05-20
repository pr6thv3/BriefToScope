"use client";

import { History, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";

export type VersionHistoryItem = {
  id: string;
  label: string;
  timestamp: string;
  summary: string;
};

type VersionHistoryDrawerProps = {
  open: boolean;
  versions: VersionHistoryItem[];
  selectedVersion?: string;
  onOpenChange: (open: boolean) => void;
  onSelectVersion: (versionId: string) => void;
};

export function VersionHistoryDrawer({
  open,
  versions,
  selectedVersion,
  onOpenChange,
  onSelectVersion,
}: VersionHistoryDrawerProps) {
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="w-[420px] max-w-[calc(100vw-2rem)]">
        <SheetHeader className="border-b">
          <SheetTitle className="flex items-center gap-2">
            <History className="size-4" aria-hidden="true" />
            Version history
          </SheetTitle>
          <SheetDescription>
            Lightweight local history for the current editing session.
          </SheetDescription>
        </SheetHeader>

        <div className="flex flex-col gap-3 p-4">
          {versions.map((version) => {
            const active = selectedVersion === version.id;
            return (
              <button
                key={version.id}
                onClick={() => onSelectVersion(version.id)}
                className={`rounded-xl border p-4 text-left transition ${
                  active
                    ? "border-blue-300 bg-blue-50"
                    : "border-slate-200 bg-white hover:border-slate-300"
                }`}
              >
                <div className="flex items-center justify-between gap-3">
                  <p className="font-medium text-slate-950">{version.label}</p>
                  {active ? (
                    <span className="text-xs font-medium text-blue-700">
                      Selected
                    </span>
                  ) : null}
                </div>
                <p className="mt-1 text-xs text-slate-500">
                  {formatTimestamp(version.timestamp)}
                </p>
                <p className="mt-3 text-sm leading-6 text-slate-600">
                  {version.summary}
                </p>
              </button>
            );
          })}
        </div>

        <div className="mt-auto border-t p-4">
          <Button variant="outline" className="w-full gap-2" disabled>
            <RotateCcw data-icon="inline-start" />
            Restore selected version
          </Button>
          <p className="mt-2 text-xs leading-5 text-slate-500">
            Restore is intentionally disabled until backend version diff support is
            added.
          </p>
        </div>
      </SheetContent>
    </Sheet>
  );
}

function formatTimestamp(timestamp: string) {
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(timestamp));
}
