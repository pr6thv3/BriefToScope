"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  Check,
  CircleDot,
  Edit3,
  ShieldCheck,
  X,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { EditableSection } from "@/components/sow-editor/EditableSection";
import { SectionRegenerateButton } from "@/components/sow-editor/SectionRegenerateButton";
import type { SOWSection, SOWSectionKey } from "@/lib/types";

type SOWSectionBlockProps = {
  section: SOWSection;
  isActive: boolean;
  isSaving: boolean;
  onActivate: (sectionKey: SOWSectionKey) => void;
  onCancel: () => void;
  onSave: (sectionKey: SOWSectionKey, contentMarkdown: string) => Promise<boolean>;
  onRegenerate: (
    sectionKey: SOWSectionKey,
    currentMarkdown: string
  ) => Promise<string | undefined>;
};

export function SOWSectionBlock({
  section,
  isActive,
  isSaving,
  onActivate,
  onCancel,
  onSave,
  onRegenerate,
}: SOWSectionBlockProps) {
  const [draft, setDraft] = useState(section.content_markdown);
  const [isRegenerating, setIsRegenerating] = useState(false);

  async function handleSave() {
    const saved = await onSave(section.section_key, draft);
    if (saved) {
      onCancel();
    }
  }

  function handleCancel() {
    setDraft(section.content_markdown);
    onCancel();
  }

  async function handleRegenerate() {
    setIsRegenerating(true);
    const nextContent = await onRegenerate(
      section.section_key,
      isActive ? draft : section.content_markdown
    );
    if (nextContent) {
      setDraft(nextContent);
    }
    setIsRegenerating(false);
  }

  function startEditing() {
    setDraft(section.content_markdown);
    onActivate(section.section_key);
  }

  const quality = Math.round(section.quality_score ?? 88);

  return (
    <motion.section
      layout
      data-section-key={section.section_key}
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.24 }}
      className={`group rounded-xl border bg-white p-5 shadow-sm transition-all md:p-6 ${
        isActive
          ? "border-blue-300 ring-4 ring-blue-100"
          : "border-slate-200 hover:border-slate-300 hover:shadow-md"
      }`}
      onDoubleClick={startEditing}
    >
      <div className="mb-5 flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <span className="flex size-7 items-center justify-center rounded-lg bg-slate-100 text-xs font-semibold text-slate-600">
              {section.order}
            </span>
            <h2 className="text-lg font-semibold text-slate-950">
              {section.section_title}
            </h2>
            <Badge
              variant="outline"
              className="gap-1 border-emerald-200 bg-emerald-50 text-emerald-700"
            >
              <ShieldCheck data-icon="inline-start" />
              AI reviewed
            </Badge>
          </div>
          <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-slate-500">
            <span className="flex items-center gap-1.5">
              <CircleDot className="size-3.5 text-blue-500" aria-hidden="true" />
              Section quality {quality}
            </span>
            <span>
              {isActive ? "Edit mode" : "Preview mode"}
            </span>
          </div>
        </div>

        <AnimatePresence mode="wait">
          {isActive ? (
            <motion.div
              key="editing-actions"
              initial={{ opacity: 0, y: -4 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -4 }}
              className="flex flex-wrap items-center gap-2"
            >
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="h-8 gap-1.5"
                onClick={handleCancel}
                disabled={isSaving || isRegenerating}
              >
                <X data-icon="inline-start" />
                Cancel
              </Button>
              <SectionRegenerateButton
                isRegenerating={isRegenerating}
                onRegenerate={handleRegenerate}
              />
              <Button
                type="button"
                size="sm"
                className="h-8 gap-1.5 bg-slate-950 text-white hover:bg-slate-800"
                onClick={handleSave}
                disabled={isSaving || isRegenerating}
              >
                <Check data-icon="inline-start" />
                Save changes
              </Button>
            </motion.div>
          ) : (
            <motion.div
              key="preview-actions"
              initial={{ opacity: 0, y: -4 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -4 }}
              className="flex flex-wrap items-center gap-2 opacity-100 transition md:opacity-0 md:group-hover:opacity-100"
            >
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="h-8 gap-1.5"
                onClick={startEditing}
                disabled={isRegenerating}
              >
                <Edit3 data-icon="inline-start" />
                Edit
              </Button>
              <SectionRegenerateButton
                isRegenerating={isRegenerating}
                onRegenerate={handleRegenerate}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {isRegenerating ? (
        <div className="mb-4 rounded-lg border border-blue-100 bg-blue-50 px-4 py-3 text-sm font-medium text-blue-800">
          Rewriting this section with agency-grade language...
        </div>
      ) : null}

      <EditableSection
        value={isActive ? draft : section.content_markdown}
        isEditing={isActive}
        onChange={setDraft}
      />
    </motion.section>
  );
}
