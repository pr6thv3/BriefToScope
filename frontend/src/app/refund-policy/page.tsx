import { LegalPage } from "@/components/legal-page";

export default function RefundPolicyPage() {
  return (
    <LegalPage
      title="Refund Policy"
      updated="May 23, 2026"
      intro="BriefToScope subscriptions are designed for self-serve agency use. This policy explains how cancellations, failed payments, and refund requests are handled during paid beta."
      sections={[
        { title: "Subscriptions", body: "Subscriptions renew monthly through PayPal unless canceled from billing settings or by contacting support. Canceling stops future renewals but does not automatically delete workspace data." },
        { title: "Refund requests", body: "Refund requests are reviewed case by case. Contact support with your workspace email, PayPal receipt, and reason for the request within 7 days of the charge." },
        { title: "Usage-based limits", body: "Plan limits are enforced before AI generation, private PDF exports, and e-signature sends. Exhausted quotas do not automatically create a refund right." },
        { title: "Failed payments", body: "If PayPal reports a failed, reversed, suspended, or canceled subscription, paid features may be blocked until billing is restored." },
        { title: "Beta expectations", body: "AI-assisted SOWs are drafts, not legal advice. Customers are responsible for reviewing outputs before sending them to clients." },
      ]}
    />
  );
}
