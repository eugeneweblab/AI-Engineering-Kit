---
id: frontend/23-monitoring
topic: frontend
slug: monitoring
title: "Frontend Monitoring"
type: doc
order: 23
status: ready
tags: [frontend, monitoring, sendBeacon, beforeSend, stringify, keepalive, "@sentry", onLCP]
related: [frontend/08-performance, frontend/13-error-handling, frontend/14-security, frontend/26-production]
when_to_use: "Read before instrumenting a frontend app with error tracking, performance, or analytics — or reviewing existing telemetry."
---
# Frontend Monitoring

## Purpose

This document defines how to observe a frontend in production: error tracking,
real-user performance metrics, and product analytics. It is written so an agent can add
or review client-side telemetry without leaking user data, degrading performance, or
flying blind on real-world failures.

The browser is an environment you don't control — thousands of device, network, and
extension combinations. Monitoring is how you learn what actually breaks for real users,
which local testing and CI can never fully reveal. It closes the loop on
[performance](08-performance.md) and [error handling](13-error-handling.md) by measuring
them in the field.

## Why It Matters

Frontend bugs are largely invisible to the server: a failed render, a broken lazy chunk,
or a JavaScript exception often returns HTTP 200 while the user sees a blank screen. If
you're not capturing client-side errors and metrics, most of your reliability signal is
missing. At the same time, telemetry runs on the user's device and often sends personal
data, so careless instrumentation becomes both a performance tax and a privacy/compliance
liability. Monitoring done right turns silent field failures into actionable alerts; done
wrong it slows every session and violates user trust.

## Core Principles

- **Capture what the server can't see.** Uncaught exceptions, unhandled promise
  rejections, failed chunk loads, and Core Web Vitals all originate in the browser.
- **Measure real users, not lab averages.** Field metrics (RUM/CrUX) reflect actual
  devices and networks; a fast local run hides the p75 tail that hurts ranking.
- **Never send secrets or PII you don't need.** Scrub tokens, emails, and form values
  before anything leaves the device. Telemetry is a data-processing activity.
- **Instrumentation must not degrade the app.** Load monitoring async, sample high-volume
  events, and never block rendering or the main thread on beacons.
- **Every signal needs an owner and an action.** An alert nobody responds to is noise.
  Tie errors and regressions to thresholds, ownership, and runbooks.

## Best Practices

- Install error tracking (e.g. Sentry) that captures uncaught errors, promise rejections,
  and React/Vue error boundaries, with source maps uploaded privately for readable stacks.
- Attach release/version and user-flow context (breadcrumbs) to errors so you can tell
  which deploy regressed and reproduce the path.
- Collect Core Web Vitals (LCP, INP, CLS) from real users with `web-vitals` and report at
  the p75 the platforms grade against, segmented by device and route.
- Send telemetry with `navigator.sendBeacon` or `fetch(..., { keepalive: true })` so it
  survives page unload without blocking navigation.
- Sample noisy events and set per-key rate limits to control cost and payload; keep 100%
  of errors but sample high-frequency analytics.
- Scrub PII in a `beforeSend` hook: strip auth headers, tokens, emails, and input values;
  mask sensitive DOM in session replay.
- Respect consent and Do-Not-Track/privacy regulations; gate analytics behind consent
  where required, and document what you collect.
- Alert on error-rate spikes, new error signatures per release, and Web Vitals regressions
  — not just raw counts.

## Examples

**Good Example** — scrubbed, release-tagged, non-blocking

```ts
import * as Sentry from "@sentry/browser";
import { onLCP, onINP, onCLS } from "web-vitals";

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  release: __APP_VERSION__,        // ties each error to the deploy that caused it
  tracesSampleRate: 0.1,           // sample perf traces to control cost
  beforeSend(event) {
    // Scrub PII before anything leaves the device.
    delete event.request?.headers?.["Authorization"];
    return event;
  },
});

// Report real-user vitals without blocking unload.
function report(metric: { name: string; value: number }) {
  navigator.sendBeacon("/rum", JSON.stringify({ ...metric, v: __APP_VERSION__ }));
}
onLCP(report); onINP(report); onCLS(report);
```

**Bad Example** — leaks data, blocks the page, no release context

```ts
window.onerror = (msg, url, line, col, err) => {
  // WHY BAD: synchronous fetch of the full state can include tokens, emails, form input
  // — PII shipped to a third party — and blocks until the request completes.
  fetch("/log", {
    method: "POST",
    body: JSON.stringify({ err, state: store.getState(), cookies: document.cookie }),
  });
  // No release tag → can't tell which deploy broke; no promise-rejection handler;
  // fires on unload without keepalive so events are dropped exactly when they matter.
};
```

## Common Mistakes

- Shipping tokens, emails, cookies, or raw form values to a telemetry backend.
- No source maps uploaded, leaving stack traces minified and unreadable.
- Missing release/version tags, so you can't attribute a spike to a deploy.
- Measuring performance only in the lab and ignoring the field p75 tail.
- Blocking beacons that don't use `sendBeacon`/`keepalive`, dropping events on unload.
- Not capturing unhandled promise rejections or failed chunk loads.
- Collecting analytics without consent where regulation requires it.
- Alert fatigue: paging on raw counts instead of rates, new signatures, and regressions.

## Production Tips

- Roll out behind a release health dashboard: crash-free sessions per version, with
  automatic regression alerts on new deploys.
- Sample session replay for errored sessions only, with sensitive fields masked, to
  reproduce hard bugs without recording everyone.
- Budget the monitoring script's own weight and main-thread time — observability should
  cost single-digit kilobytes, not tens.
- Reconcile client error rates with server logs to distinguish network flakiness from
  real app bugs.

## AI Review Checklist

- Are uncaught errors, promise rejections, and failed chunk loads all captured?
- Are source maps uploaded privately so stacks are readable, with release tags attached?
- Are Core Web Vitals collected from real users at p75, segmented by device/route?
- Is telemetry sent via `sendBeacon`/`keepalive` so it doesn't block or drop on unload?
- Is PII scrubbed before send, with consent respected where required?
- Do alerts fire on error rates, new signatures, and Web Vitals regressions — with owners?

## Related

- `knowledge/frontend/08-performance.md`
- `knowledge/frontend/13-error-handling.md`
- `knowledge/frontend/14-security.md`
- `knowledge/frontend/26-production.md`
