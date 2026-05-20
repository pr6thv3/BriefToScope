"use client";

import { motion } from "framer-motion";
import { Sparkles, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type SectionRegenerateButtonProps = {
  isRegenerating: boolean;
  onRegenerate: () => void;
};

export function SectionRegenerateButton({
  isRegenerating,
  onRegenerate,
}: SectionRegenerateButtonProps) {
  return (
    <Button
      type="button"
      variant="outline"
      size="sm"
      className={cn(
        "relative h-8 overflow-hidden border-indigo-200/80 bg-gradient-to-r from-indigo-50 to-indigo-100/60 text-indigo-700 hover:from-indigo-100 hover:to-indigo-200/80 hover:text-indigo-800 transition-all shadow-sm font-medium",
        isRegenerating && "border-indigo-300 ring-2 ring-indigo-100"
      )}
      onClick={onRegenerate}
      disabled={isRegenerating}
    >
      {isRegenerating ? (
        <RefreshCw className="mr-1.5 size-3.5 animate-spin text-indigo-600" />
      ) : (
        <motion.span
          animate={{
            scale: [1, 1.15, 1],
          }}
          transition={{
            repeat: Infinity,
            duration: 2,
            ease: "easeInOut",
          }}
          className="mr-1.5 flex items-center"
        >
          <Sparkles className="size-3.5 text-indigo-500 fill-indigo-200" />
        </motion.span>
      )}
      
      <span className="text-xs font-semibold">
        {isRegenerating ? "Rewriting block..." : "Regenerate"}
      </span>

      {/* Shimmer Effect */}
      {!isRegenerating && (
        <span className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/40 to-transparent group-hover:animate-[shimmer_1.5s_infinite]" />
      )}
    </Button>
  );
}
