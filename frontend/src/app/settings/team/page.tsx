import { MailPlus, ShieldCheck, Users } from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { PlatformPage } from "@/components/platform-page";

export default function TeamSettingsPage() {
  return (
    <AppShell>
      <PlatformPage
        eyebrow="Team settings"
        title="Workspace roles for real agency review workflows."
        description="Owner and admin users manage seats, members create/edit SOWs, reviewers can review risk and comment, and client viewers stay outside the internal workspace."
        items={[
          { title: "Roles", description: "Owner, admin, member, reviewer, and client-viewer roles are mirrored in PostgreSQL for backend authorization.", icon: ShieldCheck, badge: "Security" },
          { title: "Invites", description: "Invite team members by email with role, token expiry, and seat limit checks before acceptance.", icon: MailPlus },
          { title: "Seat limits", description: "Studio includes 5 seats, Agency includes 15, and downgrades freeze new invites without deleting data.", icon: Users },
        ]}
      />
    </AppShell>
  );
}
