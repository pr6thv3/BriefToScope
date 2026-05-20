"use client";

import { motion } from "framer-motion";
import { CheckCircle2, Box } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export function DeliverableCards({ deliverables, confidence = 0.9 }: { deliverables: string[]; confidence?: number }) {
  if (!deliverables?.length) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-3"
    >
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-semibold text-slate-700">Detected Deliverables</h4>
        <Badge variant="outline" className="text-xs bg-emerald-50 text-emerald-700 border-emerald-200">
          {(confidence * 100).toFixed(0)}% Confidence
        </Badge>
      </div>
      <div className="grid gap-2">
        {deliverables.map((del, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.1 }}
            className="flex items-center justify-between rounded-lg border bg-white p-3 shadow-sm"
          >
            <div className="flex items-center gap-3">
              <Box className="size-4 text-sky-500" />
              <span className="text-sm font-medium">{del}</span>
            </div>
            <CheckCircle2 className="size-4 text-emerald-500" />
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
