import { PenLine, ShieldCheck } from "lucide-react";
import { Brand } from "@/components/brand";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function PublicSignPage() {
  return (
    <main className="min-h-screen bg-slate-50 px-4 py-8 md:px-8">
      <div className="mx-auto max-w-3xl">
        <Brand href="/" />
        <Card className="mt-8 bg-white">
          <CardHeader>
            <div className="mb-3 flex size-11 items-center justify-center rounded-xl bg-slate-950 text-white">
              <PenLine className="size-5" aria-hidden="true" />
            </div>
            <CardTitle>Client signature handoff</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-sm leading-6 text-slate-600">
            <p>This token route gives clients a controlled handoff to DocuSign or PandaDoc without making them workspace members.</p>
            <div className="flex gap-2 rounded-lg border border-blue-200 bg-blue-50 p-3 text-blue-900">
              <ShieldCheck className="mt-0.5 size-4" aria-hidden="true" />
              The backend should validate token expiry, envelope status, and recipient before redirecting.
            </div>
            <Button className="bg-slate-950 text-white">Continue to signing provider</Button>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
