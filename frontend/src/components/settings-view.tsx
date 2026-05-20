"use client";

import { useState } from "react";
import {
  Bell,
  CreditCard,
  Grid2X2,
  ImageIcon,
  Link2,
  MessageSquare,
  Settings,
  Users,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";

const sections = [
  { label: "General", icon: Settings },
  { label: "Agency & Brand", icon: Grid2X2 },
  { label: "Users & Permissions", icon: Users },
  { label: "Billing & Plan", icon: CreditCard },
  { label: "Integrations", icon: Link2 },
  { label: "Notifications", icon: Bell },
  { label: "Support", icon: Settings },
];

export function SettingsView() {
  const [primary, setPrimary] = useState("#0066FF");
  const [secondary, setSecondary] = useState("#F5F7FA");
  const [paymentTerms, setPaymentTerms] = useState("Net 30");
  const [revisionPolicy, setRevisionPolicy] = useState(
    "2 rounds of revisions included"
  );

  return (
    <div className="grid min-h-[calc(100vh-4rem)] bg-slate-50 lg:grid-cols-[250px_1fr]">
      <aside className="hidden border-r bg-white p-4 lg:block">
        <nav className="flex flex-col gap-2">
          {sections.map((section) => {
            const Icon = section.icon;
            const active = section.label === "Agency & Brand";
            return (
              <button
                key={section.label}
                className={`flex h-11 items-center gap-3 rounded-lg px-3 text-left text-sm transition ${
                  active
                    ? "bg-blue-50 text-blue-700"
                    : "text-slate-700 hover:bg-slate-100"
                }`}
              >
                <Icon className="size-5" aria-hidden="true" />
                {section.label}
              </button>
            );
          })}
        </nav>
      </aside>

      <main className="px-4 py-8 md:px-8">
        <div className="mb-6">
          <h1 className="text-3xl font-semibold tracking-normal">
            Agency & Brand Settings
          </h1>
          <p className="mt-2 text-slate-600">
            Manage your agency profile and default settings for SOW generation.
          </p>
        </div>

        <div className="grid gap-6 2xl:grid-cols-[1fr_340px]">
          <div className="flex flex-col gap-5">
            <Card className="rounded-2xl bg-white">
              <CardHeader>
                <CardTitle className="text-xl">Brand Identity</CardTitle>
              </CardHeader>
              <CardContent className="flex flex-col gap-5">
                <div>
                  <label className="mb-2 block text-sm font-medium">
                    Logo Upload
                  </label>
                  <div className="flex max-w-md items-center gap-4 rounded-xl border border-dashed p-4">
                    <div className="flex size-16 items-center justify-center rounded-xl bg-slate-100 text-slate-500">
                      <ImageIcon className="size-7" aria-hidden="true" />
                    </div>
                    <Button variant="outline">Upload new logo</Button>
                  </div>
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <label className="flex min-w-0 flex-col gap-2 text-sm font-medium">
                    Primary
                    <div className="flex items-center gap-2 rounded-lg border px-2">
                      <input
                        type="color"
                        value={primary}
                        onChange={(event) => setPrimary(event.target.value)}
                        className="size-7 border-0 bg-transparent p-0"
                      />
                      <Input
                        value={primary}
                        onChange={(event) => setPrimary(event.target.value)}
                        className="border-0 px-0 shadow-none focus-visible:ring-0"
                      />
                    </div>
                  </label>
                  <label className="flex min-w-0 flex-col gap-2 text-sm font-medium">
                    Secondary
                    <div className="flex items-center gap-2 rounded-lg border px-2">
                      <input
                        type="color"
                        value={secondary}
                        onChange={(event) => setSecondary(event.target.value)}
                        className="size-7 border-0 bg-transparent p-0"
                      />
                      <Input
                        value={secondary}
                        onChange={(event) => setSecondary(event.target.value)}
                        className="border-0 px-0 shadow-none focus-visible:ring-0"
                      />
                    </div>
                  </label>
                  <label className="flex min-w-0 flex-col gap-2 text-sm font-medium">
                    Heading Font
                    <select className="h-10 rounded-lg border border-input bg-white px-3 text-sm outline-none focus:border-ring focus:ring-3 focus:ring-ring/50">
                      <option>Inter, Sans-serif</option>
                      <option>Geist, Sans-serif</option>
                    </select>
                  </label>
                  <label className="flex min-w-0 flex-col gap-2 text-sm font-medium">
                    Body Font
                    <select className="h-10 rounded-lg border border-input bg-white px-3 text-sm outline-none focus:border-ring focus:ring-3 focus:ring-ring/50">
                      <option>Roboto, Sans-serif</option>
                      <option>Inter, Sans-serif</option>
                    </select>
                  </label>
                </div>
              </CardContent>
            </Card>

            <Card className="rounded-2xl bg-white">
              <CardHeader>
                <CardTitle className="text-xl">Default Terms</CardTitle>
              </CardHeader>
              <CardContent className="grid gap-4 md:grid-cols-2">
                <label className="flex flex-col gap-2 text-sm font-medium">
                  Standard Payment Terms
                  <Input
                    value={paymentTerms}
                    onChange={(event) => setPaymentTerms(event.target.value)}
                  />
                </label>
                <label className="flex flex-col gap-2 text-sm font-medium">
                  Standard Revision Policy
                  <Input
                    value={revisionPolicy}
                    onChange={(event) => setRevisionPolicy(event.target.value)}
                  />
                </label>
              </CardContent>
            </Card>

            <Card className="rounded-2xl bg-white">
              <CardHeader>
                <CardTitle className="text-xl">Integrations</CardTitle>
              </CardHeader>
              <CardContent className="grid gap-4 md:grid-cols-2">
                <IntegrationCard name="DocuSign" accent="bg-yellow-300" />
                <IntegrationCard name="Slack" accent="bg-emerald-300" slack />
              </CardContent>
            </Card>
          </div>

          <Card className="h-fit rounded-2xl bg-white">
            <CardHeader>
              <CardTitle className="text-xl">Billing & Plan</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col gap-4">
              <div className="flex items-center justify-between">
                <span className="text-sm">Current Plan:</span>
                <span className="font-medium">Premium AI</span>
              </div>
              <div>
                <div className="mb-2 flex justify-between text-sm">
                  <span>Usage:</span>
                  <span>12,500 / 20,000 words this month</span>
                </div>
                <Progress value={62} />
              </div>
              <p className="text-sm">Next Renewal: Oct 1, 2026</p>
              <Button variant="link" className="justify-start px-0 text-blue-700">
                Manage Subscription
              </Button>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}

function IntegrationCard({
  name,
  accent,
  slack,
}: {
  name: string;
  accent: string;
  slack?: boolean;
}) {
  return (
    <div className="rounded-xl border p-4">
      <div className="mb-3 flex items-center justify-between gap-3">
        <div className="flex items-center gap-2 font-medium">
          <span
            className={`flex size-6 items-center justify-center rounded ${accent}`}
          >
            {slack ? (
              <MessageSquare className="size-4" aria-hidden="true" />
            ) : (
              <Link2 className="size-4" aria-hidden="true" />
            )}
          </span>
          {name}
        </div>
        <Badge variant="secondary">Disconnected</Badge>
      </div>
      <Button className="bg-blue-600 text-white hover:bg-blue-500">Connect</Button>
      <p className="mt-3 text-sm text-slate-500">Disconnected</p>
    </div>
  );
}
