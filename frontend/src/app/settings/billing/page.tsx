"use client";

import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, CheckCircle2, CreditCard, RefreshCcw } from "lucide-react";
import { toast } from "sonner";
import { AppShell } from "@/components/app-shell";
import { useAppAuth } from "@/components/auth/AppAuthProvider";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useApiClient } from "@/lib/use-api-client";

type BillingStatus = {
  plan: string;
  status: string;
  renewal_date?: string | null;
  cancel_at_period_end: boolean;
  seat_quantity: number;
  usage: {
    sow_generations_used: number;
    sow_generations_limit: number;
    pdf_exports_used: number;
    pdf_exports_limit: number;
    esign_requests_used: number;
    esign_requests_limit: number;
  };
  available_actions: string[];
};

const PAID_PLANS = ["solo", "studio", "agency"] as const;

export default function BillingSettingsPage() {
  const auth = useAppAuth();
  const api = useApiClient();
  const [billing, setBilling] = useState<BillingStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isWorking, setIsWorking] = useState<string | null>(null);

  const canManageBilling = auth.can("billing:manage");

  const returnUrls = useMemo(() => {
    if (typeof window === "undefined") {
      return { success_url: "", cancel_url: "" };
    }
    return {
      success_url: `${window.location.origin}/settings/billing?checkout=success`,
      cancel_url: `${window.location.origin}/settings/billing?checkout=cancelled`,
    };
  }, []);

  async function loadBilling() {
    if (!canManageBilling) {
      setIsLoading(false);
      return;
    }
    setIsLoading(true);
    try {
      const response = (await api.getBillingStatus()) as BillingStatus;
      setBilling(response);
    } catch (error) {
      toast.error("Billing unavailable", {
        description: error instanceof Error ? error.message : "Could not load billing status.",
      });
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void loadBilling();
    }, 0);
    return () => window.clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [canManageBilling, auth.workspaceId]);

  async function startCheckout(plan: string) {
    setIsWorking(plan);
    try {
      const response = await api.createCheckout({ plan, ...returnUrls });
      window.location.href = response.checkout_url;
    } catch (error) {
      toast.error("Checkout failed", {
        description: error instanceof Error ? error.message : "Could not start PayPal checkout.",
      });
    } finally {
      setIsWorking(null);
    }
  }

  async function cancelSubscription() {
    setIsWorking("cancel");
    try {
      await api.cancelSubscription();
      toast.success("Subscription cancelled");
      await loadBilling();
    } catch (error) {
      toast.error("Cancellation failed", {
        description: error instanceof Error ? error.message : "Could not cancel subscription.",
      });
    } finally {
      setIsWorking(null);
    }
  }

  async function reactivateSubscription() {
    setIsWorking("reactivate");
    try {
      await api.reactivateSubscription();
      toast.success("Subscription reactivated");
      await loadBilling();
    } catch (error) {
      toast.error("Reactivation failed", {
        description: error instanceof Error ? error.message : "Could not reactivate subscription.",
      });
    } finally {
      setIsWorking(null);
    }
  }

  return (
    <AppShell>
      <main className="mx-auto flex w-full max-w-6xl flex-col gap-6 p-6">
        <div className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-sm font-medium uppercase tracking-wide text-blue-700">
              Billing settings
            </p>
            <h1 className="mt-2 text-3xl font-semibold tracking-tight text-slate-950">
              PayPal subscription and usage controls
            </h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
              BriefToScope enforces plan limits before AI generation, private PDF export, and e-signature sends.
            </p>
          </div>
          <Button variant="outline" className="gap-2" onClick={loadBilling} disabled={isLoading}>
            <RefreshCcw className="size-4" />
            Refresh
          </Button>
        </div>

        {!canManageBilling ? (
          <Card>
            <CardContent className="flex items-start gap-3 p-6">
              <AlertTriangle className="mt-1 size-5 text-amber-600" />
              <div>
                <h2 className="font-semibold text-slate-950">Billing access restricted</h2>
                <p className="mt-1 text-sm text-slate-600">
                  Only workspace owners and admins can manage subscriptions.
                </p>
              </div>
            </CardContent>
          </Card>
        ) : isLoading ? (
          <BillingSkeleton />
        ) : billing ? (
          <>
            {["past_due", "suspended", "canceled", "expired", "unpaid"].includes(billing.status) ? (
              <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800">
                Payment status is {billing.status}. Expensive actions are blocked until billing is updated.
              </div>
            ) : null}

            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <CreditCard className="size-5" />
                    Current plan
                  </CardTitle>
                  <p className="mt-1 text-sm text-slate-500">
                    Renewal: {billing.renewal_date ? formatDate(billing.renewal_date) : "Free workspace"}
                  </p>
                </div>
                <Badge className="capitalize">{billing.plan}</Badge>
              </CardHeader>
              <CardContent className="grid gap-4 md:grid-cols-4">
                <UsageTile
                  label="SOW generations"
                  used={billing.usage.sow_generations_used}
                  limit={billing.usage.sow_generations_limit}
                />
                <UsageTile
                  label="PDF exports"
                  used={billing.usage.pdf_exports_used}
                  limit={billing.usage.pdf_exports_limit}
                />
                <UsageTile
                  label="E-sign sends"
                  used={billing.usage.esign_requests_used}
                  limit={billing.usage.esign_requests_limit}
                />
                <UsageTile label="Seats" used={billing.seat_quantity} limit={billing.seat_quantity} />
              </CardContent>
            </Card>

            <div className="grid gap-4 md:grid-cols-3">
              {PAID_PLANS.map((plan) => (
                <Card key={plan} className={billing.plan === plan ? "border-blue-300" : undefined}>
                  <CardHeader>
                    <CardTitle className="capitalize">{plan}</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <Button
                      className="w-full"
                      disabled={isWorking === plan || billing.plan === plan}
                      onClick={() => startCheckout(plan)}
                    >
                      {billing.plan === plan ? "Current plan" : "Choose plan"}
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>

            <div className="flex flex-wrap gap-3">
              <Button
                variant="outline"
                disabled={isWorking === "cancel" || billing.plan === "free"}
                onClick={cancelSubscription}
              >
                Cancel subscription
              </Button>
              <Button
                variant="outline"
                disabled={isWorking === "reactivate"}
                onClick={reactivateSubscription}
              >
                Reactivate
              </Button>
            </div>
          </>
        ) : null}
      </main>
    </AppShell>
  );
}

function UsageTile({ label, used, limit }: { label: string; used: number; limit: number }) {
  const percent = limit > 0 ? Math.min((used / limit) * 100, 100) : 100;
  return (
    <div className="rounded-lg border bg-slate-50 p-4">
      <div className="flex items-center justify-between gap-2">
        <p className="text-sm font-medium text-slate-700">{label}</p>
        <CheckCircle2 className="size-4 text-emerald-600" />
      </div>
      <p className="mt-3 text-2xl font-semibold text-slate-950">
        {used}
        <span className="text-sm font-normal text-slate-500"> / {limit}</span>
      </p>
      <div className="mt-3 h-2 rounded-full bg-slate-200">
        <div className="h-2 rounded-full bg-blue-600" style={{ width: `${percent}%` }} />
      </div>
    </div>
  );
}

function BillingSkeleton() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-40 rounded-xl" />
      <div className="grid gap-4 md:grid-cols-3">
        <Skeleton className="h-36 rounded-xl" />
        <Skeleton className="h-36 rounded-xl" />
        <Skeleton className="h-36 rounded-xl" />
      </div>
    </div>
  );
}

function formatDate(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "Not scheduled";
  }
  return new Intl.DateTimeFormat("en", { month: "short", day: "numeric", year: "numeric" }).format(date);
}
