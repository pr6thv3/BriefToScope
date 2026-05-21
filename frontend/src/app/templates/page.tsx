import { FileText, Library, ShieldAlert } from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { PlatformPage } from "@/components/platform-page";

export default function TemplatesPage() {
  return (
    <AppShell>
      <PlatformPage
        eyebrow="Template library"
        title="Clause intelligence should live in templates, not buried inside prompts."
        description="Use industry templates for standard deliverables, scope traps, payment structures, revision limits, and reusable commercial protections."
        items={[
          { title: "Industry templates", description: "Web design, branding, SEO, marketing, consulting, app development, copywriting, video, and e-commerce defaults.", icon: Library, badge: "MVP" },
          { title: "Clause library", description: "Reusable payment, revision, out-of-scope, client responsibility, change request, and IP ownership clauses.", icon: FileText },
          { title: "Risk triggers", description: "Trigger terms detect hidden scope creep such as SEO later, unlimited revisions, unclear hosting, or missing content ownership.", icon: ShieldAlert },
        ]}
      />
    </AppShell>
  );
}
