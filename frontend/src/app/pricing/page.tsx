import Link from "next/link";
import { CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Brand } from "@/components/brand";

const plans = [
  { name: "Free", price: "$0", limit: "3 SOWs/month", features: ["Watermarked PDF", "Risk audit preview", "No e-sign"] },
  { name: "Solo", price: "$29", limit: "30 SOWs/month", features: ["PDF export", "Basic templates", "Section regeneration"] },
  { name: "Studio", price: "$79", limit: "5 seats", features: ["Team workspace", "Brand settings", "DocuSign integration"] },
  { name: "Agency", price: "$199", limit: "15 seats", features: ["Advanced risk audit", "Custom templates", "Clause library"] },
];

export default function PricingPage() {
  return (
    <main className="min-h-screen bg-slate-50 px-4 py-8 md:px-8">
      <div className="mx-auto max-w-6xl">
        <div className="mb-10 flex items-center justify-between">
          <Brand href="/" />
          <Button render={<Link href="/generate" />}>Start generating</Button>
        </div>
        <p className="text-sm font-semibold uppercase tracking-wide text-blue-700">
          Pricing
        </p>
        <h1 className="mt-2 text-4xl font-semibold tracking-normal text-slate-950">
          Scale scope intelligence with your agency.
        </h1>
        <p className="mt-3 max-w-2xl text-slate-600">
          Start free, then upgrade when PDF export, team seats, e-signature, and custom clauses become part of your workflow.
        </p>
        <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {plans.map((plan) => (
            <Card key={plan.name} className="bg-white">
              <CardHeader>
                <CardTitle>{plan.name}</CardTitle>
                <div className="text-3xl font-semibold">{plan.price}<span className="text-sm font-normal text-slate-500">/mo</span></div>
                <p className="text-sm text-slate-500">{plan.limit}</p>
              </CardHeader>
              <CardContent className="space-y-3">
                {plan.features.map((feature) => (
                  <div key={feature} className="flex gap-2 text-sm text-slate-700">
                    <CheckCircle2 className="mt-0.5 size-4 text-emerald-600" />
                    {feature}
                  </div>
                ))}
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </main>
  );
}
