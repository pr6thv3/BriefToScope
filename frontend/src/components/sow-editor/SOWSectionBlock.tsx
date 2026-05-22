"use client";

import { useState, useEffect } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  Check,
  CircleDot,
  Edit3,
  ShieldCheck,
  X,
  Sparkles,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { EditableSection } from "@/components/sow-editor/EditableSection";
import { SectionRegenerateButton } from "@/components/sow-editor/SectionRegenerateButton";
import type { SOWSection, SOWSectionKey } from "@/lib/types";
import { cn } from "@/lib/utils";

type SOWSectionBlockProps = {
  section: SOWSection;
  isActive: boolean;
  isSaving: boolean;
  canEdit: boolean;
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
  canEdit,
  onActivate,
  onCancel,
  onSave,
  onRegenerate,
}: SOWSectionBlockProps) {
  const [draft, setDraft] = useState(section.content_markdown);
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);

  // Sync draft with section content updates (e.g. from version history reverts)
  useEffect(() => {
    let active = true;
    if (!isActive && !isStreaming) {
      const timer = setTimeout(() => {
        if (active) {
          setDraft(section.content_markdown);
        }
      }, 0);
      return () => {
        active = false;
        clearTimeout(timer);
      };
    }
  }, [section.content_markdown, isActive, isStreaming]);

  async function handleSave() {
    if (!canEdit) return;
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
    if (!canEdit) return;
    setIsRegenerating(true);
    const nextContent = await onRegenerate(
      section.section_key,
      isActive ? draft : section.content_markdown
    );
    setIsRegenerating(false);

    if (nextContent) {
      // Start streaming typing effect
      setIsStreaming(true);
      onActivate(section.section_key); // Focus the block
      
      const words = nextContent.split(" ");
      let currentWordIndex = 0;
      setDraft("");

      const interval = setInterval(() => {
        if (currentWordIndex < words.length) {
          setDraft((prev) => prev + (currentWordIndex === 0 ? "" : " ") + words[currentWordIndex]);
          currentWordIndex++;
        } else {
          clearInterval(interval);
          setIsStreaming(false);
        }
      }, 25); // Cinematic typing speed
    }
  }

  function startEditing() {
    if (isStreaming || !canEdit) return;
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
      className={cn(
        "group relative rounded-xl border bg-white p-5 shadow-sm transition-all md:p-6",
        isActive
          ? "border-indigo-300 ring-4 ring-indigo-50 shadow-md"
          : "border-slate-200/80 hover:border-slate-300 hover:shadow-md hover:bg-slate-50/20"
      )}
      onDoubleClick={canEdit ? startEditing : undefined}
    >
      {/* Top Banner indicating Streaming */}
      <AnimatePresence>
        {isStreaming && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-4 overflow-hidden rounded-lg bg-indigo-50 border border-indigo-100 px-4 py-2 flex items-center gap-2 text-xs font-semibold text-indigo-700"
          >
            <Sparkles className="size-3.5 animate-pulse text-indigo-600" />
            AI Writer: Streaming improved contract clauses...
          </motion.div>
        )}
      </AnimatePresence>

      <div className="mb-5 flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <span className="flex size-7 items-center justify-center rounded-lg bg-slate-100 text-xs font-semibold text-slate-600 group-hover:bg-slate-200/60 transition-colors">
              {section.order}
            </span>
            <h2 className="text-lg font-semibold text-slate-950">
              {section.section_title}
            </h2>
            <Badge
              variant="outline"
              className="gap-1 border-emerald-100 bg-emerald-50/80 text-emerald-700 shadow-sm"
            >
              <ShieldCheck className="size-3.5 text-emerald-600" />
              AI reviewed
            </Badge>
          </div>
          <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-slate-500">
            <span className="flex items-center gap-1.5 font-medium">
              <CircleDot className="size-3.5 text-indigo-500" aria-hidden="true" />
              Quality index {quality}%
            </span>
            <span className="text-slate-400">/</span>
            <span className="font-light">
              {isActive
                ? "Inline Editing"
                : canEdit
                  ? "Double-click block to edit"
                  : "View-only for your role"}
            </span>
          </div>
        </div>

        <AnimatePresence mode="wait">
          {isActive && canEdit ? (
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
                className="h-8 gap-1.5 text-slate-500 hover:text-slate-900"
                onClick={handleCancel}
                disabled={isSaving || isRegenerating || isStreaming}
              >
                <X className="size-3.5" />
                Cancel
              </Button>
              <SectionRegenerateButton
                isRegenerating={isRegenerating}
                onRegenerate={handleRegenerate}
              />
              <Button
                type="button"
                size="sm"
                className="h-8 gap-1.5 bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm"
                onClick={handleSave}
                disabled={isSaving || isRegenerating || isStreaming}
              >
                <Check className="size-3.5" />
                {isSaving ? "Saving..." : "Save changes"}
              </Button>
            </motion.div>
          ) : canEdit ? (
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
                className="h-8 gap-1.5 text-slate-500 hover:bg-slate-100 hover:text-slate-900"
                onClick={startEditing}
                disabled={isRegenerating}
              >
                <Edit3 className="size-3.5" />
                Edit block
              </Button>
              <SectionRegenerateButton
                isRegenerating={isRegenerating}
                onRegenerate={handleRegenerate}
              />
            </motion.div>
          ) : null}
        </AnimatePresence>
      </div>

      <AnimatePresence>
        {isRegenerating && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="mb-4 rounded-lg border border-indigo-100 bg-indigo-50/40 p-4 text-sm font-medium text-indigo-800"
          >
            <div className="flex items-center gap-3">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
              </span>
              <span>Rebuilding with professional agency language and clauses...</span>
            </div>
            <div className="mt-3 h-1.5 w-full bg-indigo-100 rounded-full overflow-hidden">
              <motion.div 
                initial={{ width: 0 }}
                animate={{ width: "100%" }}
                transition={{ duration: 1.5, ease: "easeInOut" }}
                className="h-full bg-indigo-500"
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className={cn("relative transition-opacity duration-300", isRegenerating && "opacity-20")}>
        <EditableSection
          value={isActive ? draft : section.content_markdown}
          isEditing={isActive && !isStreaming}
          onChange={setDraft}
        />
      </div>
    </motion.section>
  );
}
