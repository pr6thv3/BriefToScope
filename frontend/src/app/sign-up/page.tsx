import Link from "next/link";
import { SignUp } from "@clerk/nextjs";
import { Building2 } from "lucide-react";
import { Brand } from "@/components/brand";

export default function SignUpPage() {
  const clerkConfigured = Boolean(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY);

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-md rounded-2xl border bg-white p-8 shadow-sm">
        <Brand href="/" />
        {clerkConfigured ? (
          <div className="mt-8">
            <SignUp
              path="/sign-up"
              routing="path"
              signInUrl="/sign-in"
              fallbackRedirectUrl="/onboarding"
            />
          </div>
        ) : (
          <>
            <div className="mt-8 flex size-12 items-center justify-center rounded-xl bg-slate-950 text-white">
              <Building2 className="size-6" aria-hidden="true" />
            </div>
            <h1 className="mt-5 text-2xl font-semibold">Create your agency workspace</h1>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              Clerk is not configured in this environment. Add your Clerk keys to enable account creation.
            </p>
          </>
        )}
        <p className="mt-4 text-center text-sm text-slate-500">
          Already have an account? <Link href="/sign-in" className="font-medium text-blue-700">Sign in</Link>
        </p>
      </div>
    </main>
  );
}
