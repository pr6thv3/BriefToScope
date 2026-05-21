import { LegalPage } from "@/components/legal-page";

export default function AIDisclosurePage() {
  return (
    <LegalPage
      title="AI Disclosure"
      updated="May 21, 2026"
      intro="BriefToScope uses AI to accelerate scope extraction, risk detection, clause drafting, and SOW composition. Human review remains required for client-ready documents."
      sections={[
        { title: "Where AI is used", body: "AI assists with transcript cleaning, brief extraction, scope planning, risk detection, clause generation, SOW drafting, and quality review." },
        { title: "Human review", body: "Generated SOWs may contain errors, omissions, or commercially inappropriate language. Users must review and approve every document before sending it to clients." },
        { title: "Risk intelligence", body: "Risk scores and warnings are decision-support signals, not guarantees. They help users find ambiguity around deliverables, timelines, revisions, payment, ownership, and assumptions." },
        { title: "Provider processing", body: "Inputs may be processed by configured AI providers. Production deployments should use provider settings and agreements appropriate for confidential business data." },
        { title: "No legal advice", body: "BriefToScope does not replace legal counsel. Contract clauses and SOW language should be reviewed by qualified professionals where required." },
      ]}
    />
  );
}
