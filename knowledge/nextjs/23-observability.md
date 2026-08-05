---
id: nextjs/23-observability
topic: nextjs
slug: observability
title: "Next.js Observability"
type: doc
order: 23
status: ready
tags: [nextjs, observability, NextResponse, useReportWebVitals, stringify, register, sendBeacon, charge]
related: [nextjs/26-deployment, nextjs/20-performance, architecture/18-observability]
when_to_use: "Read before adding logging, tracing, monitoring, or alerting to a Next.js app."
---
# Next.js Observability

## Purpose

This document defines the engineering standards for monitoring, logging, tracing, and alerting in Next.js applications.

The objective is to ensure production systems remain observable, diagnosable, and maintainable by providing visibility into application behavior, performance, and failures.

Observability should be designed into the application rather than added after incidents occur.

---

## Core Principle

If a problem cannot be observed, it cannot be diagnosed.

Every production application should expose enough information to understand its health and behavior.

---

## Observability Goals

Every application should provide:

- application health;
- structured logging;
- error reporting;
- performance metrics;
- distributed tracing;
- actionable alerts.

Observability should reduce the time required to detect and resolve production issues.

---

## Pillars of Observability

A complete observability strategy consists of:

```
Logs

↓

Metrics

↓

Traces
```

These three pillars complement each other.

---

## Logging

Applications should produce structured logs.

Each log entry should include:

- timestamp;
- severity;
- request identifier;
- message;
- relevant metadata.

Logs should be machine-readable.

In Next.js there is no bundled logging framework — server logs are whatever your
Server Components, Route Handlers, and Server Actions write to `stdout`/`stderr`
via `console.*`. Hosting platforms (Vercel, AWS, containers) collect that stream,
so the discipline is to make every line a single structured JSON object rather
than free text.

Good — a tiny structured logger that emits one JSON object per event and never
leaks secrets:

```ts
// lib/logger.ts — runs on the server only
type Level = "debug" | "info" | "warn" | "error";

function log(level: Level, message: string, meta: Record<string, unknown> = {}) {
  const line = JSON.stringify({
    level,
    message,
    time: new Date().toISOString(),
    env: process.env.NODE_ENV,
    ...meta,
  });
  // Route errors to stderr so platforms classify them correctly.
  if (level === "error") console.error(line);
  else console.log(line);
}

export const logger = {
  debug: (m: string, meta?: Record<string, unknown>) => log("debug", m, meta),
  info: (m: string, meta?: Record<string, unknown>) => log("info", m, meta),
  warn: (m: string, meta?: Record<string, unknown>) => log("warn", m, meta),
  error: (m: string, meta?: Record<string, unknown>) => log("error", m, meta),
};
```

Bad — unstructured, unparseable, and string-concatenated so fields cannot be
queried:

```ts
// ❌ free-form text; a log pipeline cannot filter or aggregate this
console.log("user " + userId + " failed to check out at " + Date.now());
```

Import this logger only in server code. Importing it into a `"use client"`
component ships it to the browser and its output lands in the user's console, not
your log drain.

---

## Log Levels

Use consistent log levels.

Typical levels include:

- Debug;
- Info;
- Warn;
- Error;
- Fatal.

Choose the appropriate level based on the severity of the event.

---

## Structured Logging

Prefer structured data over plain text.

Example fields:

- request ID;
- user ID (when appropriate);
- route;
- execution time;
- environment.

Avoid parsing free-form log messages.

---

## Request Tracing

Every request should be traceable.

Typical lifecycle:

```
Incoming Request

↓

Middleware

↓

Route

↓

Database

↓

External Service

↓

Response
```

Each step should share a common request identifier.

Mint the identifier once in `middleware.ts` and forward it to the route by
cloning the request headers — you cannot mutate `request.headers` in place. Reuse
an inbound `x-request-id` when a proxy already set one so the trace stays
continuous across services:

```ts
// middleware.ts
import { NextResponse, type NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const requestId = request.headers.get("x-request-id") ?? crypto.randomUUID();

  const requestHeaders = new Headers(request.headers);
  requestHeaders.set("x-request-id", requestId);

  const response = NextResponse.next({ request: { headers: requestHeaders } });
  // Echo it back so clients and the CDN can correlate too.
  response.headers.set("x-request-id", requestId);
  return response;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
```

Any Server Component, Route Handler, or Server Action then reads the id from the
request-scoped `headers()` and attaches it to every log line:

```ts
// app/api/orders/route.ts
import { headers } from "next/headers";
import { logger } from "@/lib/logger";

export async function POST(request: Request) {
  const requestId = (await headers()).get("x-request-id") ?? "unknown";

  logger.info("order.create.start", { requestId });
  // ...business logic...
  logger.info("order.create.done", { requestId });

  return Response.json({ success: true });
}
```

`headers()` is async in Next.js 15+ and must be awaited. Reading it opts the
route into dynamic rendering, which is correct for a request-specific trace id.

---

## Error Reporting

Capture unexpected errors automatically.

Include:

- stack trace;
- request context;
- environment;
- application version.

Do not expose internal error details to users.

Next.js exposes a first-class hook for this: export `onRequestError` from
`instrumentation.ts` at the project root. The framework calls it for every
uncaught server error (Server Components, Route Handlers, Server Actions,
middleware) with structured request context, making it the single funnel to your
error tracker:

```ts
// instrumentation.ts (project root, or src/ if you use that layout)
import type { Instrumentation } from "next";

export const onRequestError: Instrumentation.onRequestError = async (
  error,
  request,
  context,
) => {
  // Ships to Sentry/Datadog/etc. Runs on the server only.
  console.error(
    JSON.stringify({
      level: "error",
      message: error instanceof Error ? error.message : String(error),
      stack: error instanceof Error ? error.stack : undefined,
      path: request.path,
      method: request.method,
      // Which Next.js phase failed: "render" | "route" | "action" | "middleware".
      renderSource: context.renderSource,
      routeType: context.routeType,
      requestId: request.headers["x-request-id"],
      release: process.env.APP_VERSION,
    }),
  );
};
```

For the *user-facing* side of a failure, surface a friendly boundary and report
from it, never a raw stack trace. A `global-error.tsx` catches errors in the root
layout; per-segment `error.tsx` files catch the rest. Both are Client Components:

```tsx
// app/global-error.tsx
"use client";

import { useEffect } from "react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // `digest` correlates this UI error with the server log from onRequestError.
    reportToTracker(error);
  }, [error]);

  return (
    <html>
      <body>
        <h1>Something went wrong</h1>
        <button onClick={() => reset()}>Try again</button>
      </body>
    </html>
  );
}
```

Bad — swallowing the error and rendering the raw message to the user:

```tsx
// ❌ leaks internals, and the failure is never reported
export default function Error({ error }: { error: Error }) {
  return <pre>{error.stack}</pre>;
}
```

In production Next.js already strips server error messages sent to the client and
replaces them with an opaque `digest`; log the full detail server-side via
`onRequestError` and correlate with that `digest`.

---

## Metrics

Collect operational metrics such as:

- request count;
- response time;
- error rate;
- memory usage;
- CPU utilization;
- active users.

Metrics should support trend analysis.

---

## Performance Monitoring

Monitor:

- Core Web Vitals;
- API latency;
- server response time;
- rendering duration;
- cache performance.

Performance monitoring should be continuous.

Next.js reports Core Web Vitals from the browser through the `useReportWebVitals`
hook. It only runs on the client, so it lives in a `"use client"` component that
you mount once in the root layout:

```tsx
// app/web-vitals.tsx
"use client";

import { useReportWebVitals } from "next/web-vitals";

export function WebVitals() {
  useReportWebVitals((metric) => {
    // metric.name is "LCP" | "CLS" | "INP" | "FCP" | "TTFB" | "FID".
    const body = JSON.stringify({
      name: metric.name,
      value: metric.value,
      id: metric.id,
      path: window.location.pathname,
    });
    // sendBeacon survives page unload; fall back to fetch with keepalive.
    if (navigator.sendBeacon) navigator.sendBeacon("/api/vitals", body);
    else fetch("/api/vitals", { body, method: "POST", keepalive: true });
  });

  return null;
}
```

```tsx
// app/layout.tsx — Server Component; renders the client reporter once
import { WebVitals } from "./web-vitals";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <WebVitals />
        {children}
      </body>
    </html>
  );
}
```

Server-side latency and render timing are already captured by the OpenTelemetry
spans from `register()` above; the hook covers the field data that only the
user's browser can measure.

---

## Health Checks

Provide lightweight health endpoints.

Typical checks include:

- application status;
- database connectivity;
- cache availability;
- external dependencies.

Health checks should execute quickly.

Implement them as a Route Handler. A health probe must reflect *live* state, so
force dynamic execution and never let its response be cached. In Next.js 15+ a
`GET` Route Handler is already uncached by default, but pinning it with
`export const dynamic = "force-dynamic"` documents the intent and survives future
refactors:

```ts
// app/api/health/route.ts
import { NextResponse } from "next/server";
import { db } from "@/lib/db";

// A health check must never be statically cached.
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    await db.$queryRaw`SELECT 1`; // Cheap connectivity probe.
    return NextResponse.json({ status: "ok" }, { status: 200 });
  } catch {
    // 503 lets load balancers pull the instance out of rotation.
    return NextResponse.json({ status: "degraded" }, { status: 503 });
  }
}
```

Bad — a health check that fetches an upstream with `force-cache` reports the
cached snapshot forever and hides real outages:

```ts
// ❌ cached response; the probe lies once the dependency goes down
export async function GET() {
  const res = await fetch("https://payments.internal/ping", {
    cache: "force-cache",
  });
  return NextResponse.json({ status: res.ok ? "ok" : "down" });
}
```

Keep the check cheap: a single connectivity query, not a full business workflow.
Separate a shallow liveness probe (process is up) from a deeper readiness probe
(dependencies reachable) when your platform distinguishes them.

---

## Distributed Tracing

Trace requests across services.

Examples:

- frontend;
- API;
- authentication provider;
- database;
- payment provider.

Tracing should identify latency bottlenecks.

Next.js has built-in OpenTelemetry instrumentation. Initialize it from the
`register()` export of `instrumentation.ts`, which runs once when the server
process starts. The `@vercel/otel` package wires up the exporter and Next.js's
own spans in a few lines:

```ts
// instrumentation.ts
import { registerOTel } from "@vercel/otel";

export function register() {
  registerOTel({ serviceName: "storefront" });
}
```

That alone produces spans for each request, render, and `fetch` call. To add your
own spans around a slow dependency, use the OpenTelemetry API directly:

```ts
// lib/payments.ts
import { trace } from "@opentelemetry/api";

const tracer = trace.getTracer("storefront.payments");

export async function charge(orderId: string) {
  return tracer.startActiveSpan("payments.charge", async (span) => {
    try {
      span.setAttribute("order.id", orderId);
      const result = await paymentProvider.charge(orderId);
      return result;
    } catch (error) {
      span.recordException(error as Error);
      throw error;
    } finally {
      span.end(); // Always end the span, even on error.
    }
  });
}
```

`register()` may run under either the Node.js or Edge runtime. Guard runtime-only
setup with `process.env.NEXT_RUNTIME === "nodejs"` when a collector library is not
Edge-compatible:

```ts
export async function register() {
  if (process.env.NEXT_RUNTIME === "nodejs") {
    await import("./instrumentation.node");
  }
}
```

Do not build spans by hand in application code — lean on the framework's
auto-instrumentation and add manual spans only around the boundaries you actually
need to measure.

---

## External Services

Monitor integrations such as:

- authentication providers;
- payment gateways;
- email services;
- cloud storage;
- third-party APIs.

Failures should be visible immediately.

---

## Alerting

Create alerts for:

- elevated error rates;
- service outages;
- slow response times;
- failed deployments;
- infrastructure failures.

Alerts should be actionable and meaningful.

---

## Dashboards

Maintain dashboards for:

- application health;
- infrastructure health;
- business metrics;
- deployment status.

Dashboards should provide an overview before detailed investigation.

---

## Incident Investigation

During production incidents collect:

- logs;
- traces;
- metrics;
- deployment history;
- infrastructure events.

Diagnosis should rely on evidence rather than assumptions.

---

## Data Retention

Define retention policies for:

- logs;
- metrics;
- traces;
- audit events.

Retention should satisfy operational and compliance requirements.

---

## Security

Never log:

- passwords;
- access tokens;
- API keys;
- payment details;
- personal information unless explicitly required and protected.

Logs are production assets and must be secured.

---

## Accessibility

Observability should not negatively affect application accessibility or user experience.

Monitoring must remain lightweight.

---

## AI Execution Checklist

## Investigation

☐ Identify critical workflows.

☐ Review monitoring requirements.

☐ Review logging strategy.

☐ Review alerting needs.

---

## Planning

☐ Implement structured logging.

☐ Capture performance metrics.

☐ Configure tracing.

☐ Define health checks.

---

## Verification

☐ Logs structured.

☐ Metrics collected.

☐ Tracing available.

☐ Alerts configured.

☐ Health checks operational.

☐ Sensitive information protected.

---

## Examples

**Good Example** — errors reported with context, real-user metrics collected

```ts
// instrumentation.ts — runs once per runtime, before the app handles a request.
export async function register() {
  if (process.env.NEXT_RUNTIME === 'nodejs') {
    const { initTracing } = await import('./lib/tracing');
    await initTracing();
  }
}

// Every uncaught server-side error, with the request context attached.
export async function onRequestError(
  error: unknown,
  request: { path: string; method: string; headers: Record<string, string> },
  context: { routerKind: string; routePath: string; renderSource: string },
) {
  await reportError({
    message: error instanceof Error ? error.message : String(error),
    stack: error instanceof Error ? error.stack : undefined,
    path: request.path,
    route: context.routePath,          // the pattern, not the filled-in URL
    renderSource: context.renderSource,
    requestId: request.headers['x-request-id'],
  });
}
```

```tsx
// app/web-vitals.tsx — field data from real users, not a lab score.
'use client';

export function WebVitals() {
  useReportWebVitals((metric) => {
    navigator.sendBeacon(
      '/api/vitals',
      JSON.stringify({ name: metric.name, value: metric.value, id: metric.id, path: location.pathname }),
    );
  });
  return null;
}
```

**Bad Example** — logs to the console, errors swallowed by the boundary

```tsx
'use client';

export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  // The boundary renders a friendly message and the error is never reported,
  // so nobody learns that this route is failing for a quarter of users.
  console.error(error);

  return <p>Something went wrong. <button onClick={reset}>Try again</button></p>;
}
```

```ts
// A structured logger writing to stdout with no request identifier: lines from
// concurrent requests interleave and cannot be reassembled into one trace.
export async function GET() {
  console.log('fetching orders');
  const orders = await getOrders();
  console.log('done', orders.length);
  return Response.json(orders);
}
```

---

## Common Mistakes

Avoid:

Logging sensitive information.

Using inconsistent log formats.

Ignoring request identifiers.

Monitoring only infrastructure.

Creating noisy alerts.

Skipping health checks.

Ignoring performance metrics.

Investigating incidents without historical data.

---

## Completion Criteria

An observability strategy is complete when:

- application health is measurable;
- structured logs are available;
- metrics are continuously collected;
- distributed tracing is implemented where appropriate;
- alerts are actionable;
- sensitive information is protected.

---

## Summary

Observability is essential for operating production Next.js applications.

By combining structured logging, meaningful metrics, distributed tracing, health checks, and actionable alerts, engineering teams can detect problems earlier, diagnose them faster, and maintain reliable production systems with confidence.

## Related

- `knowledge/nextjs/26-deployment.md`
- `knowledge/nextjs/20-performance.md`
- `knowledge/architecture/18-observability.md`
