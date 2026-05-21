import { CreditCard, Gauge, LockKeyhole } from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { PlatformPage } from "@/components/platform-page";

export default function BillingSettingsPage() {
  return (
    <AppShell>
      <PlatformPage
        eyebrow="Billing settings"
        title="Usage-based SaaS controls for SOW generation, exports, seats, and signatures."
        description="PayPal owns subscription approval and billing events. BriefToScope enforces plan gates before expensive AI, PDF, e-sign, and team actions."
        items={[
          { title: "Plans", description: "Free, Solo, Studio, Agency, and Enterprise plans map to PayPal plan IDs and PostgreSQL subscription state.", icon: CreditCard, badge: "PayPal" },
          { title: "Usage limits", description: "Track SOW generations, PDF exports, e-sign sends, token cost, and seats by workspace billing period.", icon: Gauge },
          { title: "Downgrades", description: "Do not delete data. Freeze over-limit actions until the workspace upgrades or reduces usage.", icon: LockKeyhole },
        ]}
      />
    </AppShell>
  );
}
