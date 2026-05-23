import { Mail, ShieldCheck, Wrench } from "lucide-react";
import { Brand } from "@/components/brand";

const supportEmail = process.env.NEXT_PUBLIC_SUPPORT_EMAIL || "support@brieftoscope.com";
const securityEmail = `security@${supportEmail.split("@")[1] || "brieftoscope.com"}`;

const channels = [
  { title: "Product support", description: "Questions about generation, editing, exports, signatures, billing, or workspace setup.", icon: Mail, value: supportEmail },
  { title: "Security reports", description: "Report vulnerabilities or sensitive access issues through the private security channel.", icon: ShieldCheck, value: securityEmail },
  { title: "Operational status", description: "For incidents, contact support with the affected workspace, route, and approximate time window.", icon: Wrench, value: supportEmail },
];

export default function SupportPage() {
  return (
    <main className="min-h-screen bg-background text-foreground">
      <header className="border-b bg-background/95">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-5">
          <Brand />
        </div>
      </header>
      <section className="mx-auto max-w-5xl px-6 py-14">
        <div className="max-w-3xl space-y-4">
          <p className="text-sm font-medium uppercase tracking-[0.18em] text-muted-foreground">Support</p>
          <h1 className="text-4xl font-semibold tracking-tight">Get help with BriefToScope.</h1>
          <p className="text-lg leading-8 text-muted-foreground">
            Use the right channel for product help, security reports, and production incidents.
          </p>
        </div>
        <div className="mt-10 grid gap-4 md:grid-cols-3">
          {channels.map((channel) => (
            <div key={channel.title} className="rounded-lg border bg-card p-6 shadow-sm">
              <channel.icon className="mb-5 size-6 text-blue-600" aria-hidden="true" />
              <h2 className="text-lg font-semibold">{channel.title}</h2>
              <p className="mt-3 text-sm leading-6 text-muted-foreground">{channel.description}</p>
              <p className="mt-5 text-sm font-medium">{channel.value}</p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
