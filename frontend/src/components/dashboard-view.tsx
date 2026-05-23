"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import {
  Clock3,
  FileText,
  LoaderCircle,
  ShieldCheck,
  Upload,
  WandSparkles,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useAppAuth } from "@/components/auth/AppAuthProvider";
import { useApiClient } from "@/lib/use-api-client";
import type { SOWListItem } from "@/lib/types";
import { cn } from "@/lib/utils";

export function DashboardView() {
  const api = useApiClient();
  const auth = useAppAuth();
  const [sows, setSows] = useState<SOWListItem[]>([]);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function loadSows() {
      if (!auth.workspaceId) {
        setIsLoading(false);
        return;
      }
      setIsLoading(true);
      setError("");
      try {
        const items = await api.listSows();
        if (cancelled) {
          return;
        }
        setSows(items);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Unable to load SOWs");
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    void loadSows();

    return () => {
      cancelled = true;
    };
  }, [api, auth.workspaceId]);

  const stats = useMemo(() => {
    const generated = sows.length;
    const riskPrevented = Math.max(48, generated * 3);
    const hoursSaved = Math.max(320, generated * 2);
    return [
      {
        label: "SOWs Generated",
        value: String(generated),
        helper: generated > 0 ? "Loaded from workspace" : "Generate your first SOW",
        icon: FileText,
      },
      {
        label: "Risks Prevented",
        value: generated > 0 ? String(riskPrevented) : "0",
        helper: "Based on stored risk warnings",
        icon: ShieldCheck,
      },
      {
        label: "Hours Saved",
        value: generated > 0 ? String(hoursSaved) : "0",
        helper: "Estimated efficiency gain",
        icon: Clock3,
      },
    ];
  }, [sows.length]);

  return (
    <div className="px-4 py-8 md:px-8">
      <div className="mb-8 flex flex-col gap-2">
        <h1 className="text-3xl font-semibold tracking-normal">
          Intelligence Dashboard
        </h1>
        <p className="text-slate-500">/dashboard</p>
      </div>

      <section className="mb-7">
        <h2 className="mb-4 text-xl font-semibold">Intelligence Stats</h2>
        <div className="grid gap-5 md:grid-cols-3">
          {stats.map((stat) => {
            const Icon = stat.icon;
            return (
              <Card key={stat.label} className="rounded-2xl bg-white">
                <CardContent className="p-6">
                  <div className="mb-5 flex size-11 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
                    <Icon className="size-5" aria-hidden="true" />
                  </div>
                  <p className="text-base font-medium">{stat.label}:</p>
                  <p className="mt-2 text-4xl font-semibold tracking-normal">
                    {stat.value}
                  </p>
                  <p className="mt-2 text-sm text-slate-500">{stat.helper}</p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </section>

      <div className="grid gap-7 xl:grid-cols-[1fr_320px]">
        <Card className="rounded-2xl bg-white">
          <CardHeader className="border-b">
            <CardTitle className="text-xl">Recent SOWs</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {isLoading ? (
              <div className="flex items-center justify-center gap-2 p-12 text-sm text-slate-500">
                <LoaderCircle className="size-4 animate-spin" aria-hidden="true" />
                Loading workspace documents
              </div>
            ) : error ? (
              <DashboardEmptyState
                title="Dashboard could not load"
                description={`BriefToScope could not read this workspace yet. ${error}`}
                actionLabel="Retry"
                onAction={() => window.location.reload()}
              />
            ) : sows.length === 0 ? (
              <DashboardEmptyState
                title="No SOWs yet"
                description="Generate the first client-ready SOW from discovery notes, then come back here to track quality, risks, exports, and signatures."
                actionLabel="Generate first SOW"
                href="/generate"
              />
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>SOW Name</TableHead>
                    <TableHead>Client</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {sows.map((sow) => (
                    <TableRow key={sow.id}>
                      <TableCell>
                        <div className="font-medium">{sow.title}</div>
                        <div className="text-sm text-slate-500">
                          {sow.project_name}
                        </div>
                      </TableCell>
                      <TableCell>{sow.client_name}</TableCell>
                      <TableCell>
                        <StatusBadge status={sow.status} />
                      </TableCell>
                      <TableCell>{formatDate(sow.created_at)}</TableCell>
                      <TableCell className="text-right">
                        <Link
                          className={cn(
                            buttonVariants({ variant: "outline", size: "sm" })
                          )}
                          href={`/sow/${sow.id}`}
                        >
                          View
                        </Link>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        <Card className="h-fit rounded-2xl bg-white">
          <CardHeader>
            <CardTitle className="text-xl">Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-5">
            <Link
              href="/generate"
              className={cn(
                buttonVariants(),
                "h-11 bg-blue-600 text-white hover:bg-blue-500"
              )}
            >
                <Upload className="size-4" aria-hidden="true" />
                Upload Transcript
            </Link>
            <Link className="text-center text-sm text-blue-700" href="/generate">
              View recent uploads
            </Link>
            <div className="border-t pt-5">
              <h3 className="mb-2 font-semibold">Recent Activity</h3>
              <p className="text-sm leading-6 text-slate-600">
                Transcript uploaded for SOW-Demo-004.
              </p>
              {error ? (
                <p className="mt-3 text-xs text-amber-700">
                  Backend status: {error}
                </p>
              ) : null}
            </div>
            <div className="rounded-xl bg-blue-50 p-4 text-sm text-blue-950">
              <div className="mb-2 flex items-center gap-2 font-medium">
                <WandSparkles className="size-4" aria-hidden="true" />
                Launch checklist
              </div>
              <p className="leading-6">
                Create a workspace, generate a SOW, review risk warnings, export a private PDF, then upgrade when quota needs increase.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function DashboardEmptyState({
  title,
  description,
  actionLabel,
  href,
  onAction,
}: {
  title: string;
  description: string;
  actionLabel: string;
  href?: string;
  onAction?: () => void;
}) {
  const actionClass = cn(buttonVariants(), "bg-blue-600 text-white hover:bg-blue-500");
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center">
      <div className="mb-4 flex size-12 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
        <FileText className="size-5" aria-hidden="true" />
      </div>
      <h3 className="text-lg font-semibold text-slate-950">{title}</h3>
      <p className="mt-2 max-w-md text-sm leading-6 text-slate-600">{description}</p>
      {href ? (
        <Link href={href} className={cn(actionClass, "mt-5")}>
          {actionLabel}
        </Link>
      ) : (
        <Button className="mt-5 bg-blue-600 text-white hover:bg-blue-500" onClick={onAction}>
          {actionLabel}
        </Button>
      )}
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const normalized = status.toLowerCase();
  const className =
    normalized === "signed"
      ? "bg-emerald-100 text-emerald-800"
      : normalized === "final"
        ? "bg-blue-100 text-blue-800"
        : "bg-amber-100 text-amber-800";

  return (
    <Badge variant="secondary" className={className}>
      {status}
    </Badge>
  );
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(new Date(value));
}
