import { LegalPage } from "@/components/legal-page";

export default function TermsPage() {
  return (
    <LegalPage
      title="Terms of Service"
      updated="May 23, 2026"
      intro="These terms describe the operating rules for using BriefToScope. They should be reviewed by counsel before public launch."
      sections={[
        { title: "Service", body: "BriefToScope provides AI-assisted tools for drafting, editing, auditing, exporting, and sending Statements of Work. SOWs are AI-assisted drafts that must be reviewed by the user before sending. The service does not provide legal advice." },
        { title: "Customer responsibility", body: "Users are responsible for reviewing generated content, confirming commercial terms, obtaining legal review when needed, and ensuring they have rights to upload client materials." },
        { title: "Acceptable use", body: "Users may not upload unlawful content, attempt to bypass access controls, abuse generation limits, reverse engineer the service, or use BriefToScope to mislead clients." },
        { title: "Billing", body: "Paid subscriptions are processed through PayPal. BriefToScope owns the in-app subscription experience, plan gates, usage limits, cancellations, failed-payment handling, and refund review process." },
        { title: "Availability", body: "BriefToScope aims for reliable service but may be unavailable during maintenance, provider outages, or incidents. Enterprise availability commitments require a separate agreement." },
        { title: "Termination", body: "Accounts may be suspended or terminated for non-payment, abuse, security risk, or material terms violations. Data export and deletion requests are handled according to the privacy and retention policy." },
      ]}
    />
  );
}
