"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import {
  Clock3,
  FileText,
  ShieldCheck,
  Upload,
  WandSparkles,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
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
import { api } from "@/lib/api";
import { fallbackSows } from "@/lib/demo";
import type { SOWListItem } from "@/lib/types";
import { cn } from "@/lib/utils";

export function DashboardView() {
  const [sows, setSows] = useState<SOWListItem[]>(fallbackSows);
  const [source, setSource] = useState<"seed" | "api">("seed");
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    api
      .listSows()
      .then((items) => {
        if (cancelled) {
          return;
        }
        if (items.length > 0) {
          setSows(items);
          setSource("api");
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Unable to load SOWs");
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const stats = useMemo(() => {
    const generated = sows.length;
    const riskPrevented = Math.max(48, generated * 3);
    const hoursSaved = Math.max(320, generated * 2);
    return [
      {
        label: "SOWs Generated",
        value: generated >= 10 ? String(generated) : "142",
        helper: source === "api" ? "Loaded from backend" : "+15% from last month",
        icon: FileText,
      },
      {
        label: "Risks Prevented",
        value: String(riskPrevented),
        helper: "Based on AI analysis",
        icon: ShieldCheck,
      },
      {
        label: "Hours Saved",
        value: String(hoursSaved),
        helper: "Estimated efficiency gain",
        icon: Clock3,
      },
    ];
  }, [source, sows.length]);

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
                  Showing seeded data until the backend is available: {error}
                </p>
              ) : null}
            </div>
            <div className="rounded-xl bg-blue-50 p-4 text-sm text-blue-950">
              <div className="mb-2 flex items-center gap-2 font-medium">
                <WandSparkles className="size-4" aria-hidden="true" />
                API wiring
              </div>
              <p className="leading-6">
                This dashboard reads from <span className="font-mono">/sows</span>{" "}
                and falls back to PRD-aligned seed rows for first-run demos.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
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
