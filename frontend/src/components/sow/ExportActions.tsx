"use client";

import { motion } from "framer-motion";
import { ExternalLink, FileDown, LoaderCircle, PenSquare } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { toast } from "sonner";
import { useAppAuth } from "@/components/auth/AppAuthProvider";
import { Button, buttonVariants } from "@/components/ui/button";
import { useApiClient } from "@/lib/use-api-client";
import { trackEvent } from "@/lib/analytics";
import { cn } from "@/lib/utils";

export function ExportActions({ sowId }: { sowId: string }) {
  const api = useApiClient();
  const auth = useAppAuth();
  const [isExporting, setIsExporting] = useState(false);

  if (!sowId) return null;

  async function handleExport() {
    if (!auth.can("sow:export")) {
      toast.error("Export unavailable", {
        description: "Your workspace role cannot export PDFs.",
      });
      return;
    }
    setIsExporting(true);
    try {
      const response = await api.exportPdf(sowId);
      trackEvent("pdf_exported", {
        workspace_id: auth.workspaceId,
        sow_id: sowId,
        export_id: response.export_id,
        status: response.status ?? "ready",
      });
      toast.success(response.status === "queued" ? "PDF export queued" : "PDF export ready", {
        description:
          response.status === "queued"
            ? "The worker is generating the private PDF."
            : "The private signed PDF URL is ready.",
      });
      const url = response.download_url ?? response.pdf_url;
      if (url) {
        trackEvent("signed_url_requested", {
          workspace_id: auth.workspaceId,
          sow_id: sowId,
          export_id: response.export_id,
        });
        window.open(url, "_blank", "noopener,noreferrer");
      }
    } catch (error) {
      toast.error("PDF export failed", {
        description: error instanceof Error ? error.message : "Could not export this SOW.",
      });
    } finally {
      setIsExporting(false);
    }
  }

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
      
      <Button
        variant="outline"
        className="gap-2 h-11"
        disabled={isExporting || !auth.can("sow:export")}
        onClick={handleExport}
      >
        {isExporting ? (
          <LoaderCircle className="size-4 animate-spin" />
        ) : (
          <FileDown className="size-4" />
        )}
        Export PDF
      </Button>
      
      <Link
        href={`/sow/${sowId}`}
        className={cn(
          buttonVariants(),
          "gap-2 bg-slate-900 text-white hover:bg-slate-800 h-11"
        )}
      >
        <ExternalLink className="size-4" />
        Signature Setup
      </Link>
    </motion.div>
  );
}
