import { LegalPage } from "@/components/legal-page";

export default function PrivacyPage() {
  return (
    <LegalPage
      title="Privacy Policy"
      updated="May 21, 2026"
      intro="BriefToScope handles agency briefs, transcripts, generated SOWs, account data, and billing metadata so users can create and manage commercially safer scope documents."
      sections={[
        { title: "Data we collect", body: "We collect account information, workspace membership data, client/project inputs, transcripts, generated SOW content, usage events, export records, and billing provider identifiers needed to operate the service." },
        { title: "How we use data", body: "We use data to authenticate users, generate and edit SOWs, detect scope risks, process exports and signatures, manage subscriptions, improve reliability, prevent abuse, and support customers." },
        { title: "AI processing", body: "Project inputs may be sent to configured AI providers to clean transcripts, extract scope details, generate clauses, and validate SOW quality. Production provider settings should disable training on customer data where available." },
        { title: "Retention", body: "Workspace content is retained while an account is active unless deletion is requested or a custom retention policy applies. Logs and webhook events may be retained for security, billing, and audit purposes." },
        { title: "Security", body: "BriefToScope uses authenticated API access, workspace authorization, row-level security policies, private storage strategy, webhook verification, and audit logging to protect customer data." },
        { title: "Contact", body: "Privacy requests should be sent to privacy@brieftoscope.com. Enterprise customers should use their agreement-specific support channel when available." },
      ]}
    />
  );
}
