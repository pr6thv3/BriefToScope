import type { SOWContent, SOWSection, SOWSectionKey, SOWSectionsContent } from "@/lib/types";

const orderedSections: Array<{
  key: SOWSectionKey;
  title: string;
  type: "text" | "list";
}> = [
  { key: "project_overview", title: "Project Overview", type: "text" },
  { key: "objectives", title: "Objectives", type: "list" },
  { key: "scope_of_work", title: "Scope of Work", type: "list" },
  { key: "deliverables", title: "Deliverables", type: "list" },
  { key: "timeline", title: "Timeline", type: "list" },
  { key: "payment_schedule", title: "Payment Schedule", type: "list" },
  {
    key: "client_responsibilities",
    title: "Client Responsibilities",
    type: "list",
  },
  { key: "revision_policy", title: "Revision Policy", type: "text" },
  { key: "out_of_scope", title: "Out of Scope", type: "list" },
  { key: "assumptions", title: "Assumptions", type: "list" },
  { key: "acceptance_criteria", title: "Acceptance Criteria", type: "list" },
  { key: "signature_section", title: "Signature Section", type: "text" },
];

export function isSowContent(value: unknown): value is SOWContent {
  if (!value || typeof value !== "object") {
    return false;
  }

  return orderedSections.every(({ key }) => key in value);
}

export function sowToMarkdown(sow: SOWContent, clientName?: string) {
  const lines = ["# Statement of Work"];
  if (clientName) {
    lines.push(`**Client:** ${clientName}`);
  }
  lines.push("");

  for (const section of orderedSections) {
    const value = sow[section.key];
    lines.push(`## ${section.title}`);
    if (Array.isArray(value)) {
      for (const item of value) {
        lines.push(`- ${item}`);
      }
    } else {
      lines.push(value);
    }
    lines.push("");
  }

  return lines.join("\n");
}

export function sectionsToMarkdown(sections: SOWSection[], clientName?: string) {
  const lines = ["# Statement of Work"];
  if (clientName) {
    lines.push(`**Client:** ${clientName}`);
  }
  lines.push("");

  for (const section of [...sections].sort((a, b) => a.order - b.order)) {
    lines.push(`## ${section.section_title}`);
    lines.push(section.content_markdown.trim());
    lines.push("");
  }

  return lines.join("\n");
}

export function isSectionsContent(value: unknown): value is SOWSectionsContent {
  if (!value || typeof value !== "object" || !("sections" in value)) {
    return false;
  }

  const sections = (value as { sections?: unknown }).sections;
  return Array.isArray(sections);
}

export function contentToSections(content: unknown): SOWSection[] {
  if (isSectionsContent(content)) {
    return normalizeSowSections(
      content.sections.map((section, index) => ({
        section_key: section.section_key,
        section_title:
          section.section_title ??
          orderedSections.find((item) => item.key === section.section_key)?.title ??
          `Section ${index + 1}`,
        content_markdown: section.content_markdown ?? "",
        order: section.order ?? index + 1,
        quality_score: section.quality_score,
        last_regenerated_at: section.last_regenerated_at,
      }))
    );
  }

  if (isSowContent(content)) {
    return normalizeSowSections(orderedSections.map((section, index) => {
      const value = content[section.key];
      return {
        section_key: section.key,
        section_title: section.title,
        content_markdown: Array.isArray(value)
          ? value.map((item) => `- ${item}`).join("\n")
          : value,
        order: index + 1,
        quality_score: defaultSectionQuality(section.key),
      };
    }));
  }

  return normalizeSowSections(orderedSections.map((section, index) => ({
    section_key: section.key,
    section_title: section.title,
    content_markdown: "",
    order: index + 1,
    quality_score: defaultSectionQuality(section.key),
  })));
}

export function sectionsToContent(sections: SOWSection[]): SOWSectionsContent {
  return {
    sections: normalizeSowSections(sections),
  };
}

export function normalizeSowSections(sections: SOWSection[]) {
  const byKey = new Map<SOWSectionKey, SOWSection>();
  for (const section of sections) {
    if (orderedSections.some((item) => item.key === section.section_key)) {
      byKey.set(section.section_key, section);
    }
  }

  return orderedSections.map((definition, index) => {
    const existing = byKey.get(definition.key);
    return {
      section_key: definition.key,
      section_title: existing?.section_title || definition.title,
      content_markdown: existing?.content_markdown ?? "",
      order: index + 1,
      quality_score:
        existing?.quality_score ?? defaultSectionQuality(definition.key),
      last_regenerated_at: existing?.last_regenerated_at,
    };
  });
}

export function sectionMarkdownToText(markdown: string) {
  return markdown
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/^\-\s+/gm, "")
    .replace(/\*\*/g, "")
    .trim();
}

export function defaultSectionQuality(sectionKey: SOWSectionKey) {
  const quality: Record<SOWSectionKey, number> = {
    project_overview: 92,
    objectives: 90,
    scope_of_work: 91,
    deliverables: 93,
    timeline: 86,
    payment_schedule: 94,
    client_responsibilities: 88,
    revision_policy: 95,
    out_of_scope: 92,
    assumptions: 87,
    acceptance_criteria: 89,
    signature_section: 84,
  };

  return quality[sectionKey];
}

export function markdownToText(markdown: string) {
  return markdown
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/^\-\s+/gm, "")
    .replace(/\*\*/g, "")
    .trim();
}

export { orderedSections };
