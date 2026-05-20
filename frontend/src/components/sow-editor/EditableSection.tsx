"use client";

import { Textarea } from "@/components/ui/textarea";

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
      <Textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        className="min-h-52 resize-y border-slate-200 bg-white text-[15px] leading-7 text-slate-800 shadow-none focus-visible:ring-2 focus-visible:ring-blue-200"
        autoFocus
      />
    );
  }

  return <MarkdownPreview markdown={value} placeholder={placeholder} />;
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
      <p className="rounded-lg border border-dashed border-slate-200 bg-slate-50 px-4 py-6 text-sm italic text-slate-400">
        {placeholder}
      </p>
    );
  }

  return (
    <div className="space-y-4 text-[15px] leading-7 text-slate-700">
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
          <li key={`${line}-${index}`} className="flex gap-3">
            <span className="mt-3 size-1.5 rounded-full bg-blue-500" />
            <span>{line.replace(/^[-*]\s+/, "")}</span>
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
              className="pt-1 text-sm font-semibold uppercase tracking-wide text-slate-500"
            >
              {line.replace(/^#{1,6}\s+/, "")}
            </p>
          );
        }

        if (/^[-*]\s+/.test(line)) {
          return (
            <p key={`${line}-${index}`} className="flex gap-3">
              <span className="mt-3 size-1.5 rounded-full bg-blue-500" />
              <span>{line.replace(/^[-*]\s+/, "")}</span>
            </p>
          );
        }

        return <p key={`${line}-${index}`}>{line}</p>;
      })}
    </div>
  );
}
