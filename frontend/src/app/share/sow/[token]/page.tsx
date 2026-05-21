import { FileText, ShieldCheck } from "lucide-react";
import { Brand } from "@/components/brand";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function SharedSOWPage() {
  return (
    <main className="min-h-screen bg-slate-50 px-4 py-8 md:px-8">
      <div className="mx-auto max-w-3xl">
        <Brand href="/" />
        <Card className="mt-8 bg-white">
          <CardHeader>
            <div className="mb-3 flex size-11 items-center justify-center rounded-xl bg-slate-950 text-white">
              <FileText className="size-5" aria-hidden="true" />
            </div>
            <CardTitle>Shared SOW preview</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-sm leading-6 text-slate-600">
            <p>This public token route is for client-safe, read-only SOW review links.</p>
            <div className="flex gap-2 rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-emerald-800">
              <ShieldCheck className="mt-0.5 size-4" aria-hidden="true" />
              Tokens should be signed, expiring, non-guessable, and audited when viewed.
            </div>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
