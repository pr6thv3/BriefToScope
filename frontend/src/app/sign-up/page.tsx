import Link from "next/link";
import { Building2 } from "lucide-react";
import { Brand } from "@/components/brand";
import { Button } from "@/components/ui/button";

export default function SignUpPage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-md rounded-2xl border bg-white p-8 shadow-sm">
        <Brand href="/" />
        <div className="mt-8 flex size-12 items-center justify-center rounded-xl bg-slate-950 text-white">
          <Building2 className="size-6" aria-hidden="true" />
        </div>
        <h1 className="mt-5 text-2xl font-semibold">Create your agency workspace</h1>
        <p className="mt-2 text-sm leading-6 text-slate-600">
          Clerk sign-up mounts here in production, then redirects to onboarding to create the default workspace.
        </p>
        <Button className="mt-6 w-full bg-slate-950 text-white" render={<Link href="/onboarding" />}>
          Continue to onboarding
        </Button>
        <p className="mt-4 text-center text-sm text-slate-500">
          Already have an account? <Link href="/sign-in" className="font-medium text-blue-700">Sign in</Link>
        </p>
      </div>
    </main>
  );
}
