---
id: performance/22-load-testing
topic: performance
slug: load-testing
title: "Performance Load Testing"
type: doc
order: 22
status: ready
tags: [performance, load-testing]
related: [performance/20-capacity-planning, performance/21-scalability, performance/02-metrics, performance/19-benchmarking, performance/25-production-monitoring]
when_to_use: "Read before running a load, stress, soak, or spike test against a service."
---
# Performance Load Testing

## Purpose

This document defines how to test a whole system under realistic traffic: the test types
(load, stress, soak, spike), how to model arrival correctly, and how to read the results.
It exists so an agent can find a system's real limits *before* production traffic does.

Load testing measures the system end-to-end, where [benchmarking](19-benchmarking.md)
measures one function. Its output — max sustainable throughput and the latency curve —
feeds [capacity planning](20-capacity-planning.md) and validates
[scalability](21-scalability.md).

## Why It Matters

A system that is fast for one user can collapse under a thousand, and you cannot predict
where from staring at code. Contention, connection limits, queue buildup, and GC pauses
only appear under concurrency. The alternative to a load test is a "load test in
production" during your launch — with real users and real revenue as the test subjects.
Load testing moves that discovery into a controlled environment where a failure is a
finding, not an incident.

## Core Principles

- **Model arrival as open, not closed.** Real users arrive independently at some rate
  (open model); a fixed pool of looping virtual users (closed model) throttles itself when
  the system slows, hiding the collapse. Use an open/arrival-rate model to find true
  limits.
- **Each test type answers a different question.** *Load*: does it meet SLO at expected
  peak? *Stress*: where does it break and how? *Soak*: does it degrade over hours (leaks,
  fragmentation)? *Spike*: does a sudden surge recover? Run the one your question needs.
- **Test against production-like everything.** Same instance sizes, same data volume, same
  network. A test on an empty database or a laptop proves nothing about production.
- **Report the latency curve, not one number.** Plot p50/p95/p99 against throughput. The
  interesting point is the *knee* where latency turns up — that is the real capacity limit.
- **Ramp, don't slam.** Increase load gradually so you can locate the exact throughput at
  which latency breaks, instead of just observing that it did.

## Best Practices

- Use a purpose-built tool — **k6**, **Gatling**, **Locust**, or **JMeter** — driven from
  enough load generators that the *generator* is not the bottleneck (verify its own CPU).
- Define pass/fail as an **SLO threshold** ("p99 < 300ms at 5,000 req/s with < 0.1%
  errors"), not "it didn't crash," so the result is a clear go/no-go.
- Use **realistic scenarios and data**: real endpoint mix, think-time between actions,
  varied inputs, and a warm cache state that matches production.
- Ramp load in stages and hold each plateau long enough for the system to reach steady
  state before reading the number.
- Run a **soak test** (hours at moderate load) before major launches to catch memory
  leaks and resource exhaustion that a short test misses.
- Correlate the test with server-side [metrics](02-metrics.md) — the client latency curve
  plus USE saturation tells you *which resource* broke, not just that it did.

## Examples

**Good Example** — open model, staged ramp, SLO threshold

```js
// k6: open model — requests arrive at a fixed RATE, independent of response time,
// so a slowing system does NOT throttle the load (it reveals the collapse).
export const options = {
  scenarios: {
    ramp: {
      executor: "ramping-arrival-rate",
      startRate: 100, timeUnit: "1s",
      stages: [
        { target: 1000, duration: "2m" },  // ramp
        { target: 5000, duration: "5m" },  // hold at expected peak
      ],
      preAllocatedVUs: 500, maxVUs: 5000,
    },
  },
  thresholds: { http_req_duration: ["p(99)<300"], http_req_failed: ["rate<0.001"] },
};
```

**Bad Example** — closed model, no threshold, toy data

```js
// 50 virtual users each looping as fast as they can (closed model).
// When the server slows, these users slow with it → offered load drops automatically,
// so the test NEVER pushes past the knee. You measure a comfortable number and miss the cliff.
export const options = { vus: 50, duration: "30s" };
export default function () {
  http.get("http://localhost:8080/api");   // localhost + empty DB ≠ production behavior
  // No think time, no SLO threshold: "it responded" is not a pass/fail signal.
}
```

## Common Mistakes

- Using a closed (fixed-VU) model, which self-throttles and hides the saturation point.
- Testing against a laptop, an empty database, or a cold cache — none of it reflects prod.
- Reporting a single average latency instead of the p99-vs-throughput curve and its knee.
- The load generator itself saturating, so you measure the client, not the server.
- No SLO pass/fail criterion, leaving "did it pass?" a matter of opinion.
- Skipping soak tests, then hitting a slow memory leak in production hours after deploy.

## Production Tips

- Load-test in a staging environment that mirrors production, or in production with a
  clearly bounded, off-peak, canary-scoped test and a kill switch.
- Instrument the system under test with the same [production monitoring](25-production-monitoring.md)
  you run live, so the test surfaces the exact dashboards you will watch during launch.
- Automate a scaled-down load test in CI to catch gross throughput regressions between
  releases; run the full-scale test before major events.

## AI Review Checklist

- Does the test use an open/arrival-rate model, not a self-throttling closed model?
- Is the environment production-like (instance size, data volume, network, cache state)?
- Is there an explicit SLO pass/fail threshold, not just "it didn't crash"?
- Are results reported as a p99-vs-throughput curve with the knee identified?
- Was the load generator confirmed not to be the bottleneck?
- Is a soak test included before major launches to catch leaks and slow degradation?

## Related

- `knowledge/performance/20-capacity-planning.md`
- `knowledge/performance/21-scalability.md`
- `knowledge/performance/02-metrics.md`
- `knowledge/performance/19-benchmarking.md`
- `knowledge/performance/25-production-monitoring.md`
