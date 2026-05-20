"use client";

import { Textarea } from "@/components/ui/textarea";
import { HelpCircle } from "lucide-react";
import { motion } from "framer-motion";

type EditableSectionProps = {
  value: string;
  isEditing: boolean;
  onChange: (value: string) => void;
  placeholder?: string;
};

export function EditableSection({
  value,
  isEditing,
  onChange,
  placeholder = "Add section content...",
}: EditableSectionProps) {
  if (isEditing) {
    return (
      <div className="relative rounded-lg border border-slate-200 bg-slate-50/50 p-2 shadow-inner focus-within:border-slate-300 focus-within:ring-2 focus-within:ring-indigo-100 transition-all">
        <Textarea
          value={value}
          onChange={(event) => onChange(event.target.value)}
          placeholder={placeholder}
          className="min-h-52 w-full resize-y border-0 bg-transparent px-3 py-2 text-[15px] leading-relaxed text-slate-800 focus-visible:ring-0 shadow-none focus:outline-none"
          autoFocus
        />
        <div className="flex items-center justify-between border-t border-slate-200/60 px-3 py-1.5 text-[11px] text-slate-400">
          <span className="flex items-center gap-1">
            <HelpCircle className="size-3 text-slate-400" />
            Supports standard markdown (*bold*, - bullets, # headings)
          </span>
          <span>Double-click outside to cancel</span>
        </div>
      </div>
    );
  }

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="transition-colors duration-150"
    >
      <MarkdownPreview markdown={value} placeholder={placeholder} />
    </motion.div>
  );
}

function MarkdownPreview({
  markdown,
  placeholder,
}: {
  markdown: string;
  placeholder: string;
}) {
  const blocks = markdown.trim().split(/\n{2,}/).filter(Boolean);

  if (blocks.length === 0) {
    return (
      <p className="rounded-lg border border-dashed border-slate-200 bg-slate-50/60 px-4 py-8 text-center text-sm italic text-slate-400">
        {placeholder}
      </p>
    );
  }

  return (
    <div className="space-y-4 text-[15px] leading-relaxed text-slate-700">
      {blocks.map((block, index) => (
        <MarkdownBlock key={`${block.slice(0, 16)}-${index}`} block={block} />
      ))}
    </div>
  );
}

function MarkdownBlock({ block }: { block: string }) {
  const lines = block.split("\n").map((line) => line.trim()).filter(Boolean);
  const bulletLines = lines.filter((line) => /^[-*]\s+/.test(line));

  if (bulletLines.length === lines.length) {
    return (
      <ul className="space-y-2">
        {bulletLines.map((line, index) => (
          <li key={`${line}-${index}`} className="flex items-start gap-3 group/item">
            <span className="mt-2.5 size-1.5 shrink-0 rounded-full bg-indigo-500 shadow-[0_0_4px_rgba(99,102,241,0.4)] group-hover/item:scale-125 transition-transform" />
            <span className="text-slate-700 leading-relaxed font-normal">{line.replace(/^[-*]\s+/, "")}</span>
          </li>
        ))}
      </ul>
    );
  }

  return (
    <div className="space-y-2">
      {lines.map((line, index) => {
        if (/^#{1,6}\s+/.test(line)) {
          return (
            <p
              key={`${line}-${index}`}
              className="pt-2 text-xs font-bold uppercase tracking-wider text-indigo-600/90"
            >
              {line.replace(/^#{1,6}\s+/, "")}
            </p>
          );
        }

        if (/^[-*]\s+/.test(line)) {
          return (
            <p key={`${line}-${index}`} className="flex items-start gap-3 group/item">
              <span className="mt-2.5 size-1.5 shrink-0 rounded-full bg-indigo-500 shadow-[0_0_4px_rgba(99,102,241,0.4)] group-hover/item:scale-125 transition-transform" />
              <span className="text-slate-700 leading-relaxed font-normal">{line.replace(/^[-*]\s+/, "")}</span>
            </p>
          );
        }

        // Bold formatting parser (very basic inline bold support)
        const formatBoldText = (text: string) => {
          const parts = text.split(/(\*\*.*?\*\*)/g);
          return parts.map((part, i) => {
            if (part.startsWith("**") && part.endsWith("**")) {
              return <strong key={i} className="font-semibold text-slate-900">{part.slice(2, -2)}</strong>;
            }
            return part;
          });
        };

        return <p key={`${line}-${index}`} className="leading-relaxed text-slate-700 font-normal">{formatBoldText(line)}</p>;
      })}
    </div>
  );
}
