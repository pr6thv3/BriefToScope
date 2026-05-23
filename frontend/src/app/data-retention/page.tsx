import { LegalPage } from "@/components/legal-page";

export default function DataRetentionPage() {
  return (
    <LegalPage
      title="Data Retention Policy"
      updated="May 23, 2026"
      intro="BriefToScope stores agency workspace data only for as long as it is needed to operate the product, meet billing and security obligations, and support customer-controlled exports."
      sections={[
        { title: "Workspace data", body: "Projects, transcripts, generated SOWs, section edits, risk flags, export records, usage events, and audit logs are retained while a workspace is active unless the customer requests deletion or the account is closed." },
        { title: "Generated documents", body: "PDF exports are stored in private Supabase Storage buckets. Downloads are provided through short-lived signed URLs instead of public links." },
        { title: "Deletion requests", body: "Workspace owners may request deletion of account data by contacting support. We may retain limited billing, tax, abuse-prevention, and security audit records where legally or operationally required." },
        { title: "Backups", body: "Production backups may retain deleted data for a limited recovery window before normal backup rotation removes it." },
        { title: "AI processing", body: "AI-assisted drafts are generated from user-provided inputs. Users must not upload data they are not authorized to process, and must review outputs before client use." },
      ]}
    />
  );
}
