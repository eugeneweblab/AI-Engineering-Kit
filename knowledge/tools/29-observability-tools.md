---
id: tools/29-observability-tools
topic: tools
slug: observability-tools
title: "Observability Tools"
type: doc
order: 29
status: ready
tags: [tools, observability-tools, "@opentelemetry", NodeSDK, pino, rate, APP_ENV]
related: [tools/22-profilers, tools/21-debuggers, tools/23-api-clients, tools/20-local-environments, tools/30-engineering-principles, performance/17-monitoring, security/25-monitoring]
when_to_use: "Read before instrumenting an application — choosing error tracking, structured logging, and tracing, and deciding what to capture without leaking user data."
---
# Observability Tools

## Purpose

This document defines the tooling that tells you what production is doing: error tracking, structured logs, traces, and uptime checks — plus what must never end up in any of them.

## Why It Matters

Local debugging answers "why does this fail on my machine". Production failures are different: they happen once in ten thousand requests, to a user you cannot ask, on a device you do not have. The only evidence is what you captured before it happened.

The second reason is the inverse: instrumentation captures whatever you send it, and that is how customer data ends up in a third-party SaaS with an indefinite retention policy.

## Core Principles

- **Instrument for the question you will ask at 3am.** "Which users are affected and since when" needs a user identifier and a release marker attached to every event.
- **Structured over prose.** A log line you can filter and aggregate is worth ten you can only read.
- **Sample the volume, keep the errors.** Traces can be sampled aggressively; errors cannot.
- **Redact at the source.** A scrubbing rule in the vendor's UI runs after the data has already left your infrastructure.
- **An alert nobody acts on is noise.** Every alert should name the action it triggers.

## The Three Signals

| Signal | Answers | Tool shape |
|---|---|---|
| **Errors** | What broke, for whom, since which release | Sentry, Rollbar, Bugsnag |
| **Logs** | What the system did, in order | Structured JSON to stdout → aggregator |
| **Traces** | Where the time went across services | OpenTelemetry → Jaeger, Tempo, vendor APM |

Most projects need error tracking first, structured logging second, and tracing only once more than one service is involved. Adding all three at once usually produces three half-configured tools.

## Error Tracking

```ts
// instrumentation.ts
import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.SENTRY_DSN,

  // The two fields that make an error triageable:
  release: process.env.GIT_COMMIT_SHA,   // which deploy introduced it
  environment: process.env.APP_ENV,      // production | staging

  tracesSampleRate: process.env.APP_ENV === 'production' ? 0.1 : 1.0,

  // Redact before the event leaves the process.
  beforeSend(event) {
    if (event.request?.headers) {
      delete event.request.headers.authorization;
      delete event.request.headers.cookie;
    }
    if (event.request?.data) {
      event.request.data = redact(event.request.data, ['password', 'token', 'card']);
    }
    return event;
  },

  // Drop noise that is not actionable.
  ignoreErrors: [
    'ResizeObserver loop limit exceeded',   // browser quirk, harmless
    'Non-Error promise rejection captured', // extension noise
  ],
});
```

Two practices make error tracking useful rather than a wall of red:

- **Upload sourcemaps** as part of the deploy, keyed to the same `release`. Without them, production stack traces point at minified line numbers and are unreadable.
- **Attach a user identifier** — the internal ID, never the email. It answers "how many people hit this" and "is this the customer who just called".

```ts
Sentry.setUser({ id: session.userId });   // not email, not name
```

## Structured Logging

Log JSON to stdout and let the platform ship it. The application should not know where logs are stored.

```ts
// logger.ts
import pino from 'pino';

export const logger = pino({
  level: process.env.LOG_LEVEL ?? 'info',

  // Never log these keys, wherever they appear in the object.
  redact: {
    paths: ['req.headers.authorization', 'req.headers.cookie', '*.password', '*.token'],
    censor: '[redacted]',
  },

  base: { service: 'checkout', release: process.env.GIT_COMMIT_SHA },
});
```

```ts
// Good: structured fields, correlatable, no interpolation
logger.info({ orderId, userId, amountCents, durationMs }, 'order confirmed');

// Bad: a sentence you cannot filter, aggregate, or alert on
logger.info(`Order ${orderId} for user ${email} confirmed in ${durationMs}ms`);
```

The bad line has three defects: the email is now in the log store, `durationMs` cannot be aggregated, and finding all confirmations means matching a regex against prose.

Carry a **request ID** through every log line for a request, and return it in error responses — that identifier is what connects a user's screenshot to the server-side story. See [API Clients](23-api-clients.md).

## Tracing

OpenTelemetry is the vendor-neutral instrumentation layer; the backend is a separate choice.

```ts
// otel.ts
import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';

new NodeSDK({
  traceExporter: new OTLPTraceExporter({ url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT }),
  instrumentations: [getNodeAutoInstrumentations({
    // Filesystem spans are overwhelming and rarely useful.
    '@opentelemetry/instrumentation-fs': { enabled: false },
  })],
}).start();
```

Auto-instrumentation covers HTTP, database drivers, and common libraries. Add manual spans only around code whose cost is not otherwise visible:

```ts
import { trace } from '@opentelemetry/api';

const tracer = trace.getTracer('checkout');

await tracer.startActiveSpan('price.calculate', async (span) => {
  span.setAttribute('cart.items', items.length);   // attributes, not free text
  try {
    return await calculatePricing(items);
  } finally {
    span.end();
  }
});
```

Tracing answers a question profiling cannot: where time goes *across* services and I/O boundaries. Within one process, a profiler is the sharper tool — see [Profilers](22-profilers.md).

## Front-End Signals

Real-user monitoring measures what synthetic tests cannot — actual devices on actual networks:

```ts
import { onLCP, onINP, onCLS } from 'web-vitals';

const report = (metric: { name: string; value: number; id: string }) =>
  navigator.sendBeacon('/api/vitals', JSON.stringify(metric));  // survives page unload

onLCP(report);
onINP(report);
onCLS(report);
```

Lab measurements (Lighthouse) are for catching regressions in CI; field measurements are the ones users experience. Both belong in the loop — see [Performance — Web Vitals](../performance/18-web-vitals.md).

## What Never Goes In

```
passwords, tokens, API keys, session cookies, authorization headers
full card numbers, CVV, bank details
national identifiers, health data
email addresses and phone numbers, in most jurisdictions
full request bodies from authenticated endpoints
```

Every observability tool is a third-party data processor. Before sending anything: know the retention period, know who on the team can read it, and know whether your privacy policy and DPAs cover it. Redact in the application — a vendor-side scrubbing rule is a second line of defence, not the first.

Log identifiers, not identities: `userId: 4471` answers the same operational questions as an email address and is not a disclosure if the log store is breached.

## Alerting

An alert is a promise that someone will act. Alert on symptoms users feel, not on causes:

| Alert on | Not on |
|---|---|
| Error rate above baseline for 5 minutes | A single exception |
| p95 latency past the SLO | CPU at 80% |
| Checkout success rate dropping | Queue depth briefly spiking |
| Failed backup or overdue cron | Disk at 70% |

Route by severity: paging for user-facing breakage, a channel message for degradation, a dashboard for everything else. An alert that fires nightly and is always dismissed has already stopped working.

## Examples

**Good Example** — one correlation id, carried across every signal

```ts
// Structured logs, with the fields you will actually filter on.
import pino from 'pino';

export const logger = pino({
  level: process.env.LOG_LEVEL ?? 'info',
  redact: ['req.headers.authorization', 'req.headers.cookie', '*.password', '*.token'],
});

// The same id appears on the access log, the application log, the trace, and
// the error report — so one incident is one query, not four.
logger.info({
  event: 'order.placed',
  orderId: order.id,
  userId: user.id,
  traceId: trace.getActiveSpan()?.spanContext().traceId,
  durationMs: Math.round(elapsed),
});
```

```yaml
# Alert on what users experience, with a window long enough not to page on noise.
- alert: CheckoutErrorRateHigh
  expr: |
    sum(rate(http_requests_total{route="/api/orders",status=~"5.."}[5m]))
      / sum(rate(http_requests_total{route="/api/orders"}[5m])) > 0.02
  for: 10m
  annotations:
    summary: "Checkout 5xx above 2% for 10 minutes"
    runbook: https://runbooks.example.com/checkout-errors
```

**Bad Example** — logs nobody can query, alerts nobody trusts

```ts
// Unstructured: no field to filter on, values interpolated into the message,
// and the token logged in full.
console.log(`order ${order.id} placed by ${user.email} token=${req.headers.authorization}`);
```

```yaml
# Fires on a single slow request, at any hour, with no runbook and no
# indication of user impact. Within a month it is muted, and with it the
# alerts that would have mattered.
- alert: SlowRequest
  expr: http_request_duration_seconds > 1
  for: 0m
  annotations:
    summary: "A request was slow"
```

An alert that pages without telling the responder what to do trains people to ignore the
pager. That is a worse outcome than having no alert at all.

---

## Common Mistakes

- Error tracking without sourcemaps or a release marker.
- Prose log messages that cannot be filtered or aggregated.
- PII in logs, traces, or error payloads.
- Redaction configured only in the vendor UI.
- Tracing everything at 100% in production, at enormous cost.
- No request ID, so client symptoms cannot be tied to server events.
- Alerting on causes rather than user-visible symptoms.
- Instrumentation added but never looked at — dashboards nobody opens.
- Logging inside a hot loop, making the logger the bottleneck.
- No environment separation, so staging noise buries production signal.

## Production Tips

- Set up error tracking on day one — it costs an hour and pays for itself on the first incident.
- Sample traces (1–10%) but keep 100% of errors and slow outliers; most vendors support tail-based sampling for exactly this.
- Include the release SHA everywhere: errors, logs, traces. "Since which deploy" is the first question every time.
- Give logs a retention policy and enforce it — indefinite retention is a growing liability with no operational benefit.
- Review alert noise monthly and delete what nobody acts on. Alert fatigue is the failure mode that makes the whole system useless.
- Verify the pipeline works before you need it: trigger a test error in staging and confirm it arrives, symbolicated, with the right release attached.

## AI Review Checklist

- Is error tracking configured with release, environment, and uploaded sourcemaps?
- Are logs structured, with a request ID carried through?
- Is redaction implemented in the application, not only vendor-side?
- Is any PII reaching logs, traces, or error payloads?
- Are traces sampled while errors are kept in full?
- Do alerts fire on user-visible symptoms and name an action?
- Is retention defined and defensible for the data being sent?
- Has the pipeline been verified end to end in staging?

## Related

- `knowledge/tools/22-profilers.md`
- `knowledge/tools/21-debuggers.md`
- `knowledge/tools/23-api-clients.md`
- `knowledge/tools/20-local-environments.md`
- `knowledge/tools/30-engineering-principles.md`
- `knowledge/performance/17-monitoring.md`
- `knowledge/security/25-monitoring.md`
