"use client";

import { motion } from "framer-motion";
import { Award, Target, FileSearch, ShieldCheck, FileCheck } from "lucide-react";
import { Progress } from "@/components/ui/progress";
import { useEffect, useState } from "react";

function AnimatedProgress({ value, colorClass }: { value: number; colorClass: string }) {
  const [current, setCurrent] = useState(0);
  useEffect(() => {
    const timer = setTimeout(() => setCurrent(value), 300);
    return () => clearTimeout(timer);
  }, [value]);
  return <Progress value={current} className={`h-2 bg-slate-100 [&>div]:transition-all [&>div]:duration-1000 [&>div]:ease-out ${colorClass}`} />;
}

export function QualityPanel({
  extractionScore = 91,
  clarityScore = 84,
  riskScore = 93,
  exportScore = 88,
  qualityScore,
}: {
  extractionScore?: number;
  clarityScore?: number;
  riskScore?: number;
  exportScore?: number;
  qualityScore: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="flex items-center gap-3 border-b pb-4">
        <div className="flex size-10 items-center justify-center rounded-xl bg-slate-900 text-white shadow-sm">
          <Award className="size-5" />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-slate-800">Quality Review</h2>
          <p className="text-xs text-slate-500">Overall Score: {Math.round(qualityScore)}/100</p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-xl border bg-white p-4 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2 text-sm font-medium text-slate-700">
              <FileSearch className="size-4 text-sky-500" /> Brief Extraction
            </div>
            <span className="text-sm font-bold text-slate-800">{Math.round(extractionScore)}%</span>
          </div>
          <AnimatedProgress value={extractionScore} colorClass="[&>div]:bg-sky-500" />
        </div>

        <div className="rounded-xl border bg-white p-4 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2 text-sm font-medium text-slate-700">
              <Target className="size-4 text-indigo-500" /> Scope Clarity
            </div>
            <span className="text-sm font-bold text-slate-800">{Math.round(clarityScore)}%</span>
          </div>
          <AnimatedProgress value={clarityScore} colorClass="[&>div]:bg-indigo-500" />
        </div>

        <div className="rounded-xl border bg-white p-4 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2 text-sm font-medium text-slate-700">
              <ShieldCheck className="size-4 text-emerald-500" /> Risk Detection
            </div>
            <span className="text-sm font-bold text-slate-800">{Math.round(riskScore)}%</span>
          </div>
          <AnimatedProgress value={riskScore} colorClass="[&>div]:bg-emerald-500" />
        </div>

        <div className="rounded-xl border bg-white p-4 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2 text-sm font-medium text-slate-700">
              <FileCheck className="size-4 text-amber-500" /> Export Readiness
            </div>
            <span className="text-sm font-bold text-slate-800">{Math.round(exportScore)}%</span>
          </div>
          <AnimatedProgress value={exportScore} colorClass="[&>div]:bg-amber-500" />
        </div>
      </div>
    </motion.div>
  );
}
