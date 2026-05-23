"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowRight,
  CheckCircle2,
  FileText,
  Play,
  ShieldCheck,
  Sparkles,
  Workflow,
} from "lucide-react";
import { Button, buttonVariants } from "@/components/ui/button";
import { Brand } from "@/components/brand";
import { cn } from "@/lib/utils";

const features = [
  {
    title: "Contextual Understanding",
    description: "AI analyzes voice and text for nuance.",
    icon: Sparkles,
  },
  {
    title: "Automated Structuring",
    description: "Instantly formats into industry-standard sections.",
    icon: Workflow,
  },
  {
    title: "Risk Mitigation",
    description: "Identifies potential scope creep and legal gaps.",
    icon: ShieldCheck,
  },
];

export function LandingPage() {
  return (
    <main className="min-h-screen overflow-hidden bg-slate-950 text-white">
      <div className="dark-grid relative min-h-screen">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_72%_22%,rgba(14,165,233,0.22),transparent_34%),radial-gradient(circle_at_38%_28%,rgba(139,92,246,0.12),transparent_28%)]" />
        <header className="relative z-10 mx-auto flex h-16 max-w-6xl items-center justify-between px-5">
          <Brand className="text-white" markClassName="bg-blue-500" />
          <nav className="hidden items-center gap-8 text-sm text-slate-200 md:flex">
            <a href="#features">Features</a>
            <a href="#pricing">Pricing</a>
            <a href="#resources">Resources</a>
            <a href="#contact">Contact</a>
          </nav>
          <div className="flex items-center gap-2">
            <Link
              href="/dashboard"
              className={cn(
                buttonVariants({ variant: "outline" }),
                "border-white/15 bg-white/5 text-white hover:bg-white/10 hover:text-white"
              )}
            >
              Login
            </Link>
            <Link
              href="/generate"
              className={cn(
                buttonVariants(),
                "bg-sky-500 text-white shadow-lg shadow-sky-500/30 hover:bg-sky-400"
              )}
            >
                Generate your first SOW
                <ArrowRight data-icon="inline-end" />
            </Link>
          </div>
        </header>

        <section className="relative z-10 mx-auto grid max-w-6xl gap-12 px-5 pb-12 pt-10 lg:grid-cols-[1fr_0.92fr] lg:items-center lg:pt-16">
          <div className="flex flex-col gap-8">
            <div className="flex flex-col gap-5">
              <motion.h1
                initial={{ opacity: 0, y: 18 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.55 }}
                className="max-w-2xl text-4xl font-semibold leading-tight tracking-normal md:text-5xl"
              >
                Turn messy client calls into polished Statements of Work in 90
                seconds.
              </motion.h1>
              <p className="max-w-xl text-base leading-7 text-slate-300 md:text-lg">
                The AI-powered SOW workflow that extracts scope, flags risk,
                generates clauses, and produces an editable document ready for
                PDF export and signature.
              </p>
            </div>

            <motion.div
              initial={{ opacity: 0, scale: 0.96 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.18, duration: 0.55 }}
              className="relative h-64 max-w-xl rounded-3xl border border-sky-400/15 bg-slate-900/55 shadow-2xl shadow-sky-500/10"
            >
              <div className="absolute inset-0 rounded-3xl bg-[radial-gradient(circle_at_50%_45%,rgba(56,189,248,0.28),transparent_32%)]" />
              <div className="absolute left-1/2 top-1/2 flex size-32 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-3xl border border-sky-300/40 bg-sky-400/10 shadow-[0_0_80px_rgba(56,189,248,0.45)]">
                <div className="flex size-24 items-center justify-center rounded-2xl border border-violet-300/40 bg-violet-500/15 text-3xl font-semibold">
                  AI
                </div>
              </div>
              <div className="absolute inset-x-8 top-1/2 h-px bg-gradient-to-r from-transparent via-sky-300/80 to-transparent" />
              <div className="absolute bottom-5 left-5 right-5 grid grid-cols-[1fr_auto_1fr] items-center gap-4">
                <div className="rounded-xl border border-white/10 bg-white/8 p-4">
                  <p className="text-sm font-medium">Before</p>
                  <p className="mt-1 text-xs text-slate-300">
                    Hours of inconsistent notes and scope gaps.
                  </p>
                </div>
                <ArrowRight className="size-5 text-slate-400" aria-hidden="true" />
                <div className="rounded-xl border border-sky-300/30 bg-sky-400/10 p-4">
                  <p className="text-sm font-medium">After</p>
                  <p className="mt-1 text-xs text-slate-300">
                    Accurate, compliant SOW drafts.
                  </p>
                </div>
              </div>
            </motion.div>
          </div>

          <motion.div
            initial={{ opacity: 0, x: 24 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.24, duration: 0.55 }}
            className="glass-panel relative rounded-3xl border-white/15 bg-white/8 p-5 text-white"
          >
            <div className="grid gap-5 md:grid-cols-[1fr_1.08fr]">
              <div className="flex flex-col justify-center gap-5 rounded-2xl bg-slate-950/55 p-5">
                <p className="text-xl leading-snug">
                  Client wants a new website, mobile responsive, SEO pages,
                  launch in 4 weeks...
                </p>
                <div className="flex gap-2">
                  <Link
                    href="/generate"
                    className={cn(
                      buttonVariants(),
                      "bg-sky-500 text-white shadow-lg shadow-sky-500/30 hover:bg-sky-400"
                    )}
                  >
                      Generate SOW
                      <Sparkles data-icon="inline-end" />
                  </Link>
                  <Button
                    variant="outline"
                    className="border-white/15 bg-white/5 text-white hover:bg-white/10 hover:text-white"
                  >
                    <Play data-icon="inline-start" />
                    Watch Demo
                  </Button>
                </div>
              </div>
              <div className="rounded-2xl border border-white/20 bg-white p-5 text-slate-950 shadow-2xl shadow-sky-500/20">
                <div className="mb-4 flex items-center justify-between">
                  <div>
                    <p className="text-sm font-semibold">SOW</p>
                    <p className="text-xs text-slate-500">Project Scope</p>
                  </div>
                  <CheckCircle2 className="size-5 text-sky-500" aria-hidden="true" />
                </div>
                {["Deliverables", "Timeline", "Investment", "Terms"].map(
                  (item) => (
                    <div key={item} className="mb-4 rounded-lg border p-3">
                      <div className="mb-2 flex items-center justify-between">
                        <p className="text-xs font-semibold">{item}</p>
                        <CheckCircle2
                          className="size-4 text-sky-500"
                          aria-hidden="true"
                        />
                      </div>
                      <div className="flex flex-col gap-1">
                        <span className="h-1.5 rounded bg-slate-200" />
                        <span className="h-1.5 w-5/6 rounded bg-slate-200" />
                      </div>
                    </div>
                  )
                )}
              </div>
            </div>
          </motion.div>
        </section>

        <section
          id="features"
          className="relative z-10 mx-auto grid max-w-6xl gap-5 px-5 pb-12 md:grid-cols-3"
        >
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <div
                key={feature.title}
                className="rounded-2xl border border-sky-300/20 bg-white/8 p-5 shadow-lg shadow-sky-500/5"
              >
                <Icon className="mb-4 size-8 text-sky-300" aria-hidden="true" />
                <h2 className="text-base font-semibold">{feature.title}</h2>
                <p className="mt-2 text-sm leading-6 text-slate-300">
                  {feature.description}
                </p>
              </div>
            );
          })}
        </section>

        <footer className="relative z-10 mx-auto flex max-w-6xl flex-col gap-4 border-t border-white/10 px-5 py-6 text-xs text-slate-400 md:flex-row md:items-center md:justify-between">
          <div className="flex flex-wrap gap-5">
            <Link href="/privacy">Privacy</Link>
            <Link href="/terms">Terms</Link>
            <Link href="/ai-disclosure">AI disclosure</Link>
            <Link href="/data-retention">Data retention</Link>
            <Link href="/refund-policy">Refunds</Link>
            <Link href="/support">Support</Link>
          </div>
          <div className="flex items-center gap-2">
            <FileText className="size-4" aria-hidden="true" />
            <span>BriefToScope MVP workspace</span>
          </div>
        </footer>
      </div>
    </main>
  );
}
