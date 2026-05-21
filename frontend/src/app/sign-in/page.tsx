import Link from "next/link";
import { ShieldCheck } from "lucide-react";
import { Brand } from "@/components/brand";
import { Button } from "@/components/ui/button";

export default function SignInPage() {
  return <AuthShell mode="Sign in" />;
}

function AuthShell({ mode }: { mode: string }) {
  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-md rounded-2xl border bg-white p-8 shadow-sm">
        <Brand href="/" />
        <div className="mt-8 flex size-12 items-center justify-center rounded-xl bg-slate-950 text-white">
          <ShieldCheck className="size-6" aria-hidden="true" />
        </div>
        <h1 className="mt-5 text-2xl font-semibold">{mode} to BriefToScope</h1>
        <p className="mt-2 text-sm leading-6 text-slate-600">
          Clerk authentication mounts here in production. Demo mode keeps using the backend demo bearer token.
        </p>
        <Button className="mt-6 w-full bg-slate-950 text-white" render={<Link href="/dashboard" />}>
          Continue to dashboard
        </Button>
        <p className="mt-4 text-center text-sm text-slate-500">
          New here? <Link href="/sign-up" className="font-medium text-blue-700">Create an account</Link>
        </p>
      </div>
    </main>
  );
}
