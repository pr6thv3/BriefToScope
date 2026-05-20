"use client";

import { motion } from "framer-motion";
import { ExternalLink, FileDown, PenSquare, Save } from "lucide-react";
import Link from "next/link";
import { Button, buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export function ExportActions({ sowId }: { sowId: string }) {
  if (!sowId) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-end"
    >
      <Link
        href={`/sow/${sowId}`}
        className={cn(buttonVariants({ variant: "outline" }), "gap-2 h-11")}
      >
        <PenSquare className="size-4" />
        Edit SOW
      </Link>
      
      <Button variant="outline" className="gap-2 h-11" onClick={() => alert("Draft Saved")}>
        <Save className="size-4" />
        Save Draft
      </Button>
      
      <Button variant="outline" className="gap-2 h-11" onClick={() => alert("Mock PDF Export")}>
        <FileDown className="size-4" />
        Export PDF
      </Button>
      
      <Button className="gap-2 bg-slate-900 text-white hover:bg-slate-800 h-11" onClick={() => alert("Mock Send Signature")}>
        <ExternalLink className="size-4" />
        Send for Signature
      </Button>
    </motion.div>
  );
}
