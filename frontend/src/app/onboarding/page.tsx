import Link from "next/link";
import { Building2, CheckCircle2, FileDown, ScanSearch, Sparkles, TrendingUp } from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { Card, CardContent } from "@/components/ui/card";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const checklist = [
  {
    title: "Create workspace",
    description: "Clerk identity is mirrored into PostgreSQL and attached to a default agency workspace.",
    icon: Building2,
    href: "/settings/team",
  },
  {
    title: "Generate first SOW",
    description: "Paste discovery notes and run the structured AI generation job.",
    icon: Sparkles,
    href: "/generate",
  },
  {
    title: "Review risk warnings",
    description: "Open the SOW editor and resolve ambiguous deliverables, timeline, payment, and ownership risks.",
    icon: ScanSearch,
    href: "/dashboard",
  },
  {
    title: "Export private PDF",
    description: "Generate a private Supabase PDF export and use a short-lived signed download URL.",
    icon: FileDown,
    href: "/dashboard",
  },
  {
    title: "Upgrade plan",
    description: "Move from free quota to Solo, Studio, or Agency when client work needs paid limits.",
    icon: TrendingUp,
    href: "/settings/billing",
  },
];

export default function OnboardingPage() {
  return (
    <AppShell>
      <main className="mx-auto flex w-full max-w-5xl flex-col gap-6 px-4 py-8 md:px-8">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-blue-700">
            Onboarding
          </p>
          <h1 className="mt-2 max-w-3xl text-3xl font-semibold tracking-tight text-slate-950 md:text-4xl">
            Get the workspace ready for paid client work.
          </h1>
          <p className="mt-3 max-w-3xl text-base leading-7 text-slate-600">
            Finish these steps before sending a real SOW: workspace sync, first generation, risk review, private export, and plan readiness.
          </p>
        </div>

        <Card className="bg-white">
          <CardContent className="p-0">
            {checklist.map((item, index) => {
              const Icon = item.icon;
              return (
                <div
                  key={item.title}
                  className="flex flex-col gap-4 border-b p-5 last:border-b-0 md:flex-row md:items-center md:justify-between"
                >
                  <div className="flex gap-4">
                    <div className="flex size-11 shrink-0 items-center justify-center rounded-lg bg-slate-950 text-white">
                      <Icon className="size-5" aria-hidden="true" />
                    </div>
                    <div>
                      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                        Step {index + 1}
                      </p>
                      <h2 className="mt-1 text-lg font-semibold text-slate-950">
                        {item.title}
                      </h2>
                      <p className="mt-1 max-w-2xl text-sm leading-6 text-slate-600">
                        {item.description}
                      </p>
                    </div>
                  </div>
                  <Link
                    href={item.href}
                    className={cn(buttonVariants({ variant: "outline" }), "h-9 gap-2")}
                  >
                    <CheckCircle2 className="size-4" aria-hidden="true" />
                    Open
                  </Link>
                </div>
              );
            })}
          </CardContent>
        </Card>
      </main>
    </AppShell>
  );
}
