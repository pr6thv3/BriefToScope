import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { AppAuthProvider } from "@/components/auth/AppAuthProvider";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Toaster } from "@/components/ui/sonner";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  metadataBase: new URL("https://brieftoscope.com"),
  title: {
    default: "BriefToScope | AI Scope Intelligence for Agencies",
    template: "%s | BriefToScope",
  },
  description:
    "BriefToScope turns messy discovery notes into commercially safe, editable Statements of Work with AI-powered scope risk intelligence.",
  keywords: ["scope intelligence", "statement of work", "agency operations", "AI SOW", "scope creep"],
  openGraph: {
    title: "BriefToScope",
    description: "AI scope intelligence for agencies that need client-ready SOWs and scope-risk protection.",
    url: "https://brieftoscope.com",
    siteName: "BriefToScope",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "BriefToScope",
    description: "AI scope intelligence for agencies.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="flex min-h-full flex-col">
        <AppAuthProvider>
          <TooltipProvider>
            {children}
            <Toaster richColors position="top-right" />
          </TooltipProvider>
        </AppAuthProvider>
      </body>
    </html>
  );
}
