"use client";

import { motion } from "framer-motion";
import { AlertTriangle, Info } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import type { RiskFlag } from "@/lib/types";
import { cn } from "@/lib/utils";

export function ScopeRiskCards({ risks }: { risks: RiskFlag[] }) {
  if (!risks?.length) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="rounded-xl border border-emerald-200 bg-emerald-50 p-4"
      >
        <div className="flex items-center gap-2 text-emerald-700">
          <Info className="size-4" />
          <p className="text-sm font-medium">No major scope risks detected.</p>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-3"
    >
      <h4 className="text-sm font-semibold text-slate-700">Detected Scope Risks</h4>
      <div className="grid gap-3">
        {risks.map((risk, i) => {
          const isHigh = risk.severity === "high";
          const isMedium = risk.severity === "medium";
          
          return (
            <motion.div
              key={i}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.15, type: "spring", stiffness: 300, damping: 25 }}
            >
              <Alert 
                className={cn(
                  "border-l-4 transition-colors",
                  isHigh ? "border-l-red-500 border-red-200 bg-red-50" :
                  isMedium ? "border-l-amber-500 border-amber-200 bg-amber-50" :
                  "border-l-sky-500 border-sky-200 bg-sky-50"
                )}
              >
                <AlertTriangle className={cn(
                  "size-4",
                  isHigh ? "text-red-600" : isMedium ? "text-amber-600" : "text-sky-600"
                )} />
                <AlertTitle className="flex items-center gap-2 text-sm font-semibold">
                  {risk.title}
                  <Badge 
                    variant="outline" 
                    className={cn(
                      "text-[10px] uppercase tracking-wider",
                      isHigh ? "bg-red-100 text-red-700 border-red-200" : 
                      isMedium ? "bg-amber-100 text-amber-700 border-amber-200" : 
                      "bg-sky-100 text-sky-700 border-sky-200"
                    )}
                  >
                    {risk.severity}
                  </Badge>
                </AlertTitle>
                <AlertDescription className="mt-2 flex flex-col gap-2 text-xs">
                  <span className="text-slate-600">{risk.description}</span>
                  <div className="rounded bg-white/60 p-2 font-medium">
                    <span className="text-slate-500">Suggested Fix: </span>
                    <span className="text-slate-700">{risk.suggested_fix}</span>
                  </div>
                </AlertDescription>
              </Alert>
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
}
