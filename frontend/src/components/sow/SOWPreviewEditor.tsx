"use client";

import { motion } from "framer-motion";
import { ExternalLink, FileText } from "lucide-react";
import Link from "next/link";
import { buttonVariants } from "@/components/ui/button";
import type { SowDetails } from "@/lib/types";
import { cn } from "@/lib/utils";
import { SOWSectionBlock } from "./SOWSectionBlock";

export function SOWPreviewEditor({
  sow,
  sowId,
}: {
  sow?: SowDetails;
  sowId: string;
}) {
  if (!sow?.content_json) return null;

  const content = sow.content_json;
  const formatContent = (value: string | string[] | undefined) =>
    Array.isArray(value) ? value.map((item) => `- ${item}`).join("\n") : value ?? "";

  const sections = [
    { title: "Project Overview", content: formatContent(content.project_overview) },
    { title: "Objectives", content: formatContent(content.objectives) },
    { title: "Scope of Work", content: formatContent(content.scope_of_work) },
    { title: "Out of Scope", content: formatContent(content.out_of_scope) },
    { title: "Timeline", content: formatContent(content.timeline) },
    { title: "Payment Schedule", content: formatContent(content.payment_schedule) },
    {
      title: "Client Responsibilities",
      content: formatContent(content.client_responsibilities),
    },
    { title: "Revision Policy", content: formatContent(content.revision_policy) },
    { title: "Assumptions", content: formatContent(content.assumptions) },
    {
      title: "Acceptance Criteria",
      content: formatContent(content.acceptance_criteria),
    },
  ].filter((section) => section.content.trim().length > 0);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      className="rounded-2xl border bg-slate-50/50 p-6 shadow-xl shadow-sky-500/10"
    >
      <div className="mb-6 flex items-center justify-between gap-3 border-b pb-4">
        <div className="flex items-center gap-2 text-slate-800">
          <div className="flex size-10 items-center justify-center rounded-xl border border-slate-200 bg-white shadow-sm">
            <FileText className="size-5 text-sky-500" />
          </div>
          <div>
            <h2 className="text-lg font-semibold">Editable SOW Draft</h2>
            <p className="text-xs text-slate-500">
              Review and refine AI-generated sections
            </p>
          </div>
        </div>
        <Link
          href={`/sow/${sowId}`}
          className={cn(
            buttonVariants({ variant: "outline", size: "sm" }),
            "h-8 gap-1 bg-white text-xs"
          )}
        >
          Open Full Editor
          <ExternalLink className="size-3" aria-hidden="true" />
        </Link>
      </div>

      <div className="space-y-4">
        {sections.map((section) => (
          <SOWSectionBlock
            key={section.title}
            title={section.title}
            content={section.content}
          />
        ))}

        <div className="mt-8 rounded-xl border border-dashed border-slate-300 bg-white p-5">
          <h4 className="mb-4 font-semibold text-slate-800">Signatures</h4>
          <div className="grid grid-cols-2 gap-8">
            <div>
              <div className="mb-2 h-10 border-b border-slate-300" />
              <p className="text-xs text-slate-500">Agency Representative</p>
            </div>
            <div>
              <div className="mb-2 h-10 border-b border-slate-300" />
              <p className="text-xs text-slate-500">Client Representative</p>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
