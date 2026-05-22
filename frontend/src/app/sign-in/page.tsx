import Link from "next/link";
import { SignIn } from "@clerk/nextjs";
import { ShieldCheck } from "lucide-react";
import { Brand } from "@/components/brand";

export default function SignInPage() {
  const clerkConfigured = Boolean(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY);
  return <AuthShell clerkConfigured={clerkConfigured} />;
}

function AuthShell({ clerkConfigured }: { clerkConfigured: boolean }) {
  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-md rounded-2xl border bg-white p-8 shadow-sm">
        <Brand href="/" />
        {clerkConfigured ? (
          <div className="mt-8">
            <SignIn
              path="/sign-in"
              routing="path"
              signUpUrl="/sign-up"
              fallbackRedirectUrl="/dashboard"
            />
          </div>
        ) : (
          <>
            <div className="mt-8 flex size-12 items-center justify-center rounded-xl bg-slate-950 text-white">
              <ShieldCheck className="size-6" aria-hidden="true" />
            </div>
            <h1 className="mt-5 text-2xl font-semibold">Sign in to BriefToScope</h1>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              Clerk is not configured in this environment. Add your publishable and secret keys before
              accessing protected workspace pages.
            </p>
          </>
        )}
        <p className="mt-4 text-center text-sm text-slate-500">
          New here? <Link href="/sign-up" className="font-medium text-blue-700">Create an account</Link>
        </p>
      </div>
    </main>
  );
}
