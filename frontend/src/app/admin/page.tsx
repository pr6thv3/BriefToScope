import { Activity, Database, ShieldAlert } from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { PlatformPage } from "@/components/platform-page";

export default function AdminPage() {
  return (
    <AppShell>
      <PlatformPage
        eyebrow="Internal admin"
        title="Operational dashboard for jobs, traces, webhook health, and production readiness."
        description="This route should be gated to internal operators only before production launch."
        items={[
          { title: "Generation jobs", description: "Inspect queued, running, failed, and completed background jobs with retry paths.", icon: Activity },
          { title: "AI traces", description: "Review A1-A7 run metadata, prompt versions, quality scores, fallback markers, and cost.", icon: Database },
          { title: "Security events", description: "Monitor audit logs, export events, signing requests, billing webhooks, and suspicious access.", icon: ShieldAlert },
        ]}
      />
    </AppShell>
  );
}
