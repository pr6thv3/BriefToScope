"use client";

import posthog from "posthog-js";

let initialized = false;

export type AnalyticsEvent =
  | "signup"
  | "workspace_synced"
  | "generation_started"
  | "generation_completed"
  | "generation_failed"
  | "sow_edited"
  | "pdf_exported"
  | "signed_url_requested"
  | "esign_sent"
  | "checkout_started"
  | "subscription_changed"
  | "quota_reached";

export function initAnalytics() {
  if (initialized || typeof window === "undefined") {
    return;
  }

  const key = process.env.NEXT_PUBLIC_POSTHOG_KEY;
  if (!key) {
    return;
  }

  posthog.init(key, {
    api_host: process.env.NEXT_PUBLIC_POSTHOG_HOST || "https://us.i.posthog.com",
    capture_pageview: true,
    autocapture: false,
    person_profiles: "identified_only",
  });
  initialized = true;
}

export function identifyUser(userId: string, properties: Record<string, unknown> = {}) {
  if (!initialized) {
    return;
  }
  posthog.identify(userId, properties);
}

export function trackEvent(event: AnalyticsEvent, properties: Record<string, unknown> = {}) {
  if (!initialized) {
    return;
  }
  posthog.capture(event, properties);
}
