import { Building2, Palette, ShieldCheck } from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { PlatformPage } from "@/components/platform-page";

export default function OnboardingPage() {
  return (
    <AppShell>
      <PlatformPage
        eyebrow="Onboarding"
        title="Set up the workspace BriefToScope will use for tenancy, billing, and templates."
        description="The production flow syncs the Clerk user, creates a default workspace, captures brand defaults, and prepares quota tracking before generation starts."
        items={[
          { title: "Workspace identity", description: "Create the agency workspace and slug that every project, SOW, template, and usage event belongs to.", icon: Building2, badge: "Required" },
          { title: "Brand defaults", description: "Store logo, colors, and PDF footer text so exports feel client-ready from day one.", icon: Palette },
          { title: "Security baseline", description: "Mirror Clerk identity into PostgreSQL and authorize every request through workspace membership.", icon: ShieldCheck },
        ]}
      />
    </AppShell>
  );
}
