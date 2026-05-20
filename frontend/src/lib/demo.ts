import type { RiskFlag, SOWContent, SOWListItem, SOWSection, SOWDetail } from "@/lib/types";

export const sampleTranscript = `Client: Luma Retail Co.
Project: Brand Identity + Webflow Website
Industry: Web Design / Branding
Deliverables:
- brand strategy workshop
- logo system with 3 concepts
- brand guidelines
- 8-page Webflow website
Risks:
- copywriting mentioned but not confirmed
- photography responsibility unclear
- revision rounds undefined
- launch date tentative
Payment:
- 50/25/25 milestone structure`;

export const industries = [
  "Technology & Software Development",
  "Web Design",
  "Branding & Identity",
  "Marketing & Growth",
  "E-commerce",
  "Consulting",
  "Content & Copywriting",
  "Video Production",
  "Product Design",
  "Operations",
];

export const tones = [
  "Professional, Concise",
  "Premium Agency",
  "Friendly Consultant",
  "Legal-Forward",
  "Executive Summary",
];

export const fallbackSows: SOWListItem[] = [
  {
    id: "demo-001",
    title: "SOW-Demo-001",
    client_name: "Acme Corp",
    project_name: "Website Redesign",
    industry: "Technology & Software Development",
    status: "draft",
    created_at: "2026-05-20T09:15:00.000Z",
    updated_at: "2026-05-20T10:10:00.000Z",
    confidence_score: 0.89,
  },
  {
    id: "demo-002",
    title: "SOW-Demo-002",
    client_name: "Beta Solutions",
    project_name: "Mobile App Development",
    industry: "Product Design",
    status: "final",
    created_at: "2026-05-18T11:30:00.000Z",
    updated_at: "2026-05-19T08:20:00.000Z",
    confidence_score: 0.94,
  },
  {
    id: "demo-003",
    title: "SOW-Demo-003",
    client_name: "Gamma Industries",
    project_name: "Cloud Migration",
    industry: "Operations",
    status: "signed",
    created_at: "2026-05-16T14:05:00.000Z",
    updated_at: "2026-05-17T15:44:00.000Z",
    confidence_score: 0.91,
  },
];

export const fallbackSowContent: SOWContent = {
  project_overview:
    "Luma Retail Co. is engaging the agency to refresh its brand identity and design an 8-page Webflow marketing website. The work will turn current discovery notes into a clear scope covering brand strategy, identity development, website structure, milestone payments, revision limits, client responsibilities, and explicit exclusions.",
  objectives: [
    "Clarify Luma Retail Co.'s visual positioning and brand system.",
    "Create a conversion-minded Webflow website for priority retail audiences.",
    "Define a commercially safe delivery scope with clear exclusions and approval checkpoints.",
  ],
  scope_of_work: [
    "Brand strategy workshop and discovery synthesis.",
    "Logo system exploration with 3 initial concepts.",
    "Brand guidelines covering logo usage, colors, typography, and core visual rules.",
    "Design and Webflow build for up to 8 marketing website pages.",
  ],
  deliverables: [
    "Brand strategy workshop summary.",
    "Logo system with 3 initial creative concepts and one refined direction.",
    "Brand guidelines PDF.",
    "8-page Webflow website with responsive layouts.",
    "Launch handoff checklist.",
  ],
  timeline: [
    "Week 1: Strategy workshop, discovery synthesis, and project kickoff.",
    "Weeks 2-3: Logo concepts, brand direction, and approval checkpoint.",
    "Weeks 4-6: Website design, Webflow build, QA, and launch handoff.",
  ],
  payment_schedule: [
    "50% due at project kickoff to reserve production capacity.",
    "25% due after approval of brand direction and website structure.",
    "25% due before final website handoff and launch support.",
  ],
  client_responsibilities: [
    "Provide final website copy, product information, brand references, and approved assets.",
    "Assign one decision-maker to consolidate feedback and approvals.",
    "Provide Webflow, domain, analytics, and hosting access where required.",
    "Review deliverables within three business days of each milestone submission.",
  ],
  revision_policy:
    "Two rounds of revisions are included for each major design deliverable. Additional revisions, new features, or changes after approval will be handled through the change request process.",
  out_of_scope: [
    "Copywriting is excluded unless separately approved in writing.",
    "Original photography, image licensing, or large-scale content production is excluded.",
    "Third-party integrations beyond standard embed/configuration are excluded.",
    "Ongoing hosting ownership, maintenance, SEO retainers, and paid media are excluded unless added by change order.",
  ],
  assumptions: [
    "The client will provide final content and assets before Webflow implementation begins.",
    "The 6-week timeline depends on timely feedback and consolidated approvals.",
    "Hosting, Webflow subscription, domain, plugin, and third-party service costs are billed separately.",
  ],
  acceptance_criteria: [
    "Brand guidelines and logo system are delivered in approved formats.",
    "The Webflow website includes up to 8 approved responsive pages.",
    "All included revision rounds are completed or waived by the client.",
    "Final launch approval is confirmed by the designated client approver.",
  ],
  signature_section:
    "Client Signature: ____________________  Provider Signature: ____________________  Date: __________",
};

export const fallbackSowSections: SOWSection[] = [
  {
    section_key: "project_overview",
    section_title: "Project Overview",
    content_markdown: fallbackSowContent.project_overview,
    order: 1,
    quality_score: 92,
  },
  {
    section_key: "objectives",
    section_title: "Objectives",
    content_markdown: fallbackSowContent.objectives.map((item) => `- ${item}`).join("\n"),
    order: 2,
    quality_score: 90,
  },
  {
    section_key: "scope_of_work",
    section_title: "Scope of Work",
    content_markdown: fallbackSowContent.scope_of_work.map((item) => `- ${item}`).join("\n"),
    order: 3,
    quality_score: 91,
  },
  {
    section_key: "deliverables",
    section_title: "Deliverables",
    content_markdown: fallbackSowContent.deliverables.map((item) => `- ${item}`).join("\n"),
    order: 4,
    quality_score: 93,
  },
  {
    section_key: "timeline",
    section_title: "Timeline",
    content_markdown: fallbackSowContent.timeline.map((item) => `- ${item}`).join("\n"),
    order: 5,
    quality_score: 86,
  },
  {
    section_key: "payment_schedule",
    section_title: "Payment Schedule",
    content_markdown: fallbackSowContent.payment_schedule.map((item) => `- ${item}`).join("\n"),
    order: 6,
    quality_score: 94,
  },
  {
    section_key: "client_responsibilities",
    section_title: "Client Responsibilities",
    content_markdown: fallbackSowContent.client_responsibilities.map((item) => `- ${item}`).join("\n"),
    order: 7,
    quality_score: 88,
  },
  {
    section_key: "revision_policy",
    section_title: "Revision Policy",
    content_markdown: fallbackSowContent.revision_policy,
    order: 8,
    quality_score: 95,
  },
  {
    section_key: "out_of_scope",
    section_title: "Out of Scope",
    content_markdown: fallbackSowContent.out_of_scope.map((item) => `- ${item}`).join("\n"),
    order: 9,
    quality_score: 92,
  },
  {
    section_key: "assumptions",
    section_title: "Assumptions",
    content_markdown: fallbackSowContent.assumptions.map((item) => `- ${item}`).join("\n"),
    order: 10,
    quality_score: 87,
  },
  {
    section_key: "acceptance_criteria",
    section_title: "Acceptance Criteria",
    content_markdown: fallbackSowContent.acceptance_criteria.map((item) => `- ${item}`).join("\n"),
    order: 11,
    quality_score: 89,
  },
  {
    section_key: "signature_section",
    section_title: "Signature Section",
    content_markdown: fallbackSowContent.signature_section,
    order: 12,
    quality_score: 84,
  },
];

export const fallbackRisks: RiskFlag[] = [
  {
    severity: "medium",
    title: "Copywriting Responsibility Unclear",
    description:
      "Website copy is required for the Webflow build, but ownership has not been fully confirmed.",
    suggested_fix:
      "Keep copywriting excluded unless separately approved, and require final client-provided copy before implementation.",
  },
  {
    severity: "medium",
    title: "Hosting Responsibility Unclear",
    description:
      "Hosting ownership, Webflow subscription, and domain responsibility need explicit confirmation.",
    suggested_fix:
      "Add an assumption that third-party platform costs and hosting ownership remain with the client.",
  },
  {
    severity: "low",
    title: "Final Launch Approval Not Confirmed",
    description:
      "The launch timeline is defined, but the final approving stakeholder is not named.",
    suggested_fix:
      "Identify a single approval authority for final launch signoff.",
  },
];

export const fallbackEditorSow: SOWDetail = {
  id: "demo-001",
  title: "Brand Identity + Webflow Website SOW",
  client_name: "Luma Retail Co.",
  project_name: "Brand Identity + Webflow Website",
  industry: "Branding & Web Design",
  status: "draft",
  content_json: { sections: fallbackSowSections },
  content_markdown: "",
  risk_flags: fallbackRisks,
  risk_flags_json: fallbackRisks,
  quality_score: 91,
  confidence_score: 0.88,
  scope_confidence_score: 0.88,
  risk_level: "medium",
  missing_information: ["Hosting owner", "Final launch approver"],
  vague_warnings: ["Future integrations may expand implementation scope"],
  pdf_url: null,
  created_at: "2026-05-20T09:15:00.000Z",
  updated_at: "2026-05-20T10:10:00.000Z",
  transcript_summary: fallbackSowContent.project_overview,
  export_status: "ready",
  esign_status: "not_sent",
};
