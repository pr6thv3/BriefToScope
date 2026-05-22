"use client";

import { LoaderCircle, Sparkles, RefreshCcw, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { industries, tones } from "@/lib/demo";

export type GeneratePayload = {
  transcript: string;
  industry: string;
  tone: string;
  clientName: string;
  projectName: string;
  budget: string;
  timeline: string;
};

type TranscriptPanelProps = {
  isGenerating: boolean;
  onGenerate: (payload: GeneratePayload) => void;
  onReset: () => void;
  onLoadSample: () => void;
  payload: GeneratePayload;
  onChange: (updates: Partial<GeneratePayload>) => void;
  canGenerate?: boolean;
  disabledReason?: string;
};

export function TranscriptPanel({
  isGenerating,
  onGenerate,
  onReset,
  onLoadSample,
  payload,
  onChange,
  canGenerate = true,
  disabledReason,
}: TranscriptPanelProps) {
  const isReady = payload.transcript.length > 10;

  return (
    <div className="flex flex-col gap-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm md:p-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-slate-800">Command Center</h2>
          <p className="text-sm text-slate-500 mt-1">Paste discovery notes to begin.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={onLoadSample} disabled={isGenerating}>
            <FileText className="size-4 mr-2" /> Sample
          </Button>
          <Button variant="ghost" size="sm" onClick={onReset} disabled={isGenerating}>
            <RefreshCcw className="size-4" />
          </Button>
        </div>
      </div>

      <div className="flex flex-col gap-2">
        <label className="text-sm font-medium text-slate-700">Raw Transcript</label>
        <Textarea
          value={payload.transcript}
          onChange={(e) => onChange({ transcript: e.target.value })}
          disabled={isGenerating}
          placeholder="Client wants a new website..."
          className="min-h-[220px] resize-none font-mono text-sm leading-6 shadow-inner bg-slate-50/50"
        />
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="flex flex-col gap-2">
          <label className="text-sm font-medium text-slate-700">Industry</label>
          <select
            value={payload.industry}
            onChange={(e) => onChange({ industry: e.target.value })}
            disabled={isGenerating}
            className="h-10 rounded-lg border border-input bg-white px-3 text-sm outline-none focus:border-ring focus:ring-2 focus:ring-ring/50 disabled:opacity-50"
          >
            {industries.map((item) => (
              <option key={item}>{item}</option>
            ))}
          </select>
        </div>
        <div className="flex flex-col gap-2">
          <label className="text-sm font-medium text-slate-700">Tone</label>
          <select
            value={payload.tone}
            onChange={(e) => onChange({ tone: e.target.value })}
            disabled={isGenerating}
            className="h-10 rounded-lg border border-input bg-white px-3 text-sm outline-none focus:border-ring focus:ring-2 focus:ring-ring/50 disabled:opacity-50"
          >
            {tones.map((item) => (
              <option key={item}>{item}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="flex flex-col gap-2">
          <label className="text-sm font-medium text-slate-700">Client Name</label>
          <Input
            value={payload.clientName}
            onChange={(e) => onChange({ clientName: e.target.value })}
            disabled={isGenerating}
            placeholder="e.g. Acme Corp"
          />
        </div>
        <div className="flex flex-col gap-2">
          <label className="text-sm font-medium text-slate-700">Project Name</label>
          <Input
            value={payload.projectName}
            onChange={(e) => onChange({ projectName: e.target.value })}
            disabled={isGenerating}
            placeholder="e.g. Website Redesign"
          />
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="flex flex-col gap-2">
          <label className="text-sm font-medium text-slate-700">Budget (Optional)</label>
          <Input
            value={payload.budget}
            onChange={(e) => onChange({ budget: e.target.value })}
            disabled={isGenerating}
            placeholder="$100k"
          />
        </div>
        <div className="flex flex-col gap-2">
          <label className="text-sm font-medium text-slate-700">Timeline (Optional)</label>
          <Input
            value={payload.timeline}
            onChange={(e) => onChange({ timeline: e.target.value })}
            disabled={isGenerating}
            placeholder="Q4 Launch"
          />
        </div>
      </div>

      <div className="mt-2 rounded-xl bg-slate-900 p-4">
        <Button
          className="h-12 w-full bg-sky-500 text-white hover:bg-sky-400 text-base font-semibold shadow-[0_0_20px_rgba(14,165,233,0.3)] transition-all"
          disabled={!isReady || isGenerating || !canGenerate}
          onClick={() => onGenerate(payload)}
        >
          {isGenerating ? (
            <>
              <LoaderCircle className="mr-2 size-5 animate-spin" />
              Processing Pipeline...
            </>
          ) : (
            <>
              <Sparkles className="mr-2 size-5" />
              Generate SOW
            </>
          )}
        </Button>
        {!canGenerate && disabledReason ? (
          <p className="mt-3 text-center text-xs text-slate-300">{disabledReason}</p>
        ) : null}
      </div>
    </div>
  );
}
