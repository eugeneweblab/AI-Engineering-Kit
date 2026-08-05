---
id: testing/26-observability
topic: testing
slug: observability
title: "Testing Observability"
type: doc
order: 26
status: ready
tags: [testing, observability]
related: [testing/25-production-testing, testing/23-debugging-tests, testing/15-performance-testing, testing/04-e2e-testing, testing/27-quality-gates]
when_to_use: "Read before relying on production signals to test behavior, or when writing tests that assert on emitted telemetry."
---
# Testing Observability

## Purpose

This document explains observability from a testing angle: how to use production signals
(logs, metrics, traces) to verify behavior, and how to test that the instrumentation
itself is correct. Observability is what makes [production testing](25-production-testing.md)
possible — a canary you cannot measure is just a gamble.

Two directions matter here. **Testing with observability:** using telemetry as the oracle
for whether the live system behaves. **Testing of observability:** confirming that your
alerts fire, your metrics are accurate, and your traces connect — because a broken alert
is a silent single point of failure.

## Why It Matters

You cannot assert on what you cannot see. A pre-merge test proves code was correct in a
controlled box; observability proves the system is correct now, under real load, with
real dependencies. But telemetry is code too, and untested telemetry rots: a renamed
field silently zeroes a dashboard, an alert threshold no one verified never fires, a
trace breaks at a service boundary. When the instrumentation lies, every downstream
decision — rollback or promote, page or ignore — is made on bad data. Treat the
observability pipeline as a tested asset, not free output.

## Core Principles

- **Signals are test oracles.** In production the assertion is "error rate stayed within
  budget," "the trace shows all five hops," "the metric moved as expected." Design code to
  emit those signals deliberately.
- **Test the alert, not just the metric.** An alert that has never fired in a drill is
  unproven. Inject the failing condition and confirm it pages.
- **Structured over stringly.** Emit structured events (key/value) so tests and queries
  can assert on fields, not parse free-text logs.
- **Correlate everything.** Every request carries a trace/correlation id end-to-end, so a
  failing synthetic check can be traced to the exact failing span.
- **Cardinality and cost are constraints.** High-cardinality labels (user id, request id)
  on metrics explode storage. Put those on traces/logs, keep metrics low-cardinality.

## Best Practices

- Emit **structured logs** with stable field names; write unit tests that assert the
  event shape (level, keys, values) for security- and billing-relevant actions.
- Instrument the **three pillars** deliberately: metrics for aggregate health (RED/USE),
  traces for per-request causality, logs for detail. Don't reach for logs where a metric
  belongs.
- Define **SLOs and error budgets**, and let [quality gates](27-quality-gates.md) and
  rollouts consume them as pass/fail thresholds.
- Add **assertions on telemetry** in integration/e2e tests: after the action, verify the
  expected metric incremented and the trace has the expected spans.
- **Test alerts on a schedule**: run a game-day or automated synthetic failure that trips
  each critical alert, proving the path from condition to page still works.
- Propagate a **trace context** header across every service and async boundary (queue,
  job) so no hop drops the correlation id.
- Keep telemetry field names in a **shared schema** and fail CI when a renamed field would
  break a dashboard or alert query.

## Examples

**Good Example** — structured event, tested shape, trace propagation

```ts
// The emitted event has a stable schema, so tests and dashboards can rely on it.
function recordCharge(ctx: Ctx, amount: number, ok: boolean) {
  log.info("payment.charge", {
    traceId: ctx.traceId,      // correlation id propagated from the inbound request
    amountCents: amount,
    outcome: ok ? "success" : "declined",
  });
  metrics.increment("payment_charge_total", { outcome: ok ? "success" : "declined" });
  // low-cardinality label (outcome), NOT amount or user id, on the metric
}

test("emits a declined payment event with the trace id", () => {
  const events = captureLogs(() => recordCharge(ctx, 999, false));
  expect(events).toContainEqual(
    expect.objectContaining({ event: "payment.charge", outcome: "declined", traceId: ctx.traceId }),
  );
});
```

**Bad Example** — unstructured, unverifiable, high-cardinality

```ts
function recordCharge(amount: number, ok: boolean) {
  console.log(`charge ${amount} ${ok}`);          // free text: no field to assert or query
  metrics.increment(`charge_${userId}_${amount}`); // user id + amount in metric name → cardinality blowup
  // No trace id, so a production failure cannot be tied back to its request.
}
// There is no test, and the alert built on this metric has never been proven to fire.
```

## Common Mistakes

- Building dashboards and alerts but never testing that the alert actually fires.
- Free-text logs that no test or query can assert on reliably.
- Putting unbounded labels (user id, URL with ids) on metrics, exploding cardinality.
- Dropping the trace context at an async boundary, so traces end at the queue.
- Treating log volume as coverage — noisy logs hide the one line that matters.
- Renaming a telemetry field without updating the alert/dashboard that reads it.
- Measuring only averages; p50 hides the p99 pain real users feel.

## Production Tips

- Run alert drills (game days) on a cadence; an alert unfired for a year is unproven.
- Sample traces, but keep 100% of error traces — the rare failure is the one you need.
- Version your telemetry schema and treat a breaking field change like an API change.

## AI Review Checklist

- Are important actions emitted as structured events with stable field names?
- Do tests assert on the shape of security-, billing-, or SLO-relevant telemetry?
- Is a trace/correlation id propagated across every service and async hop?
- Are metric labels low-cardinality (no user/request ids)?
- Has each critical alert been proven to fire via a drill or synthetic failure?
- Are SLOs defined and consumed by rollouts and quality gates as thresholds?
- Do error traces get retained even when normal traces are sampled down?

## Related

- `knowledge/testing/25-production-testing.md`
- `knowledge/testing/23-debugging-tests.md`
- `knowledge/testing/15-performance-testing.md`
- `knowledge/testing/04-e2e-testing.md`
- `knowledge/testing/27-quality-gates.md`
