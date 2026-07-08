---
id: testing/16-load-testing
topic: testing
slug: load-testing
title: "Load Testing"
type: doc
order: 16
status: ready
tags: [testing, load-testing]
related: [testing/15-performance-testing, testing/12-api-testing, testing/26-observability, testing/25-production-testing, testing/04-e2e-testing]
when_to_use: "Read before designing a test that drives a system with concurrent traffic to find its capacity or breaking point."
---
# Load Testing

## Purpose

This document defines how to test a system under *concurrent* traffic: many users,
sustained duration, and realistic request mixes. Where [performance testing](15-performance-testing.md)
measures one operation in isolation, load testing measures the whole system under
pressure — to find its capacity, its failure mode, and whether it degrades gracefully.

A load test drives a running system with a modeled workload and answers: how many users
can it serve within its latency budget, what breaks first, and what happens past the
limit.

## Why It Matters

Systems fail differently under load than in isolation. A query that is instant with one
user melts a connection pool at a thousand; a cache that hides a slow path evaporates on
a cold start; retries that are harmless alone become a self-amplifying storm at scale.
None of this appears in unit, integration, or single-request performance tests. Load
testing is the only way to learn a system's ceiling and its failure mode *before* real
traffic teaches you both at once, during an outage, with users watching.

## Core Principles

- **Model the real workload, not a single endpoint.** Users hit a mix of routes with
  think-time and realistic payloads. Hammering one URL flat-out measures a fiction.
- **Name the load pattern on purpose.** *Baseline* (expected traffic), *stress* (past the
  limit to find the break), *soak* (hours, to find leaks), *spike* (sudden surge). Each
  answers a different question — pick the one your risk demands.
- **Define pass/fail before you run.** Set SLOs up front: p95 latency, error rate,
  throughput. A load test without a threshold is a demo, not a test.
- **The load generator must not be the bottleneck.** If the client is CPU- or
  network-bound, you are measuring the client. Verify headroom or distribute the load.
- **Watch the system, not just the client.** Capacity is found by correlating client
  latency with server CPU, memory, connections, and queue depth — the client alone cannot
  tell you *why* it broke.

## Best Practices

- Use a purpose-built tool (`k6`, Gatling, Locust, JMeter) that models virtual users,
  ramp-up, think-time, and thresholds. Do not script raw request loops.
- Ramp up gradually and hold a steady state; measure during the plateau, not during
  ramp-up, so numbers reflect a stable system.
- Set thresholds in the tool so the run fails automatically when an SLO is breached, and
  wire that into CI/CD for release-gating.
- Test against a production-like environment with production-shaped data volume. Results
  from a laptop or an empty database are meaningless for capacity planning.
- Correlate the run with server-side [observability](26-observability.md): dashboards for
  CPU, memory, DB connections, GC, and queue depth, aligned to the load timeline.
- Parameterize requests with varied data (different user IDs, search terms) so you exercise
  cache misses and real distribution, not one hot cached row.
- Isolate the target and announce the run. A stress test against shared infrastructure can
  page an unrelated team; run soak tests in a dedicated environment.

## Examples

**Good Example** — modeled users, ramp, think-time, threshold gate

```js
import http from "k6/http";
import { sleep, check } from "k6";

export const options = {
  stages: [                                   // ramp up, hold steady, ramp down
    { duration: "2m", target: 200 },
    { duration: "5m", target: 200 },          // measure during this steady plateau
    { duration: "2m", target: 0 },
  ],
  thresholds: {                               // pass/fail defined before the run
    http_req_duration: ["p(95)<500"],         // p95 latency SLO
    http_req_failed: ["rate<0.01"],           // under 1% errors
  },
};

export default function () {
  const id = Math.floor(Math.random() * 10000); // varied data → real cache-miss mix
  const res = http.get(`https://staging.example.com/products/${id}`);
  check(res, { "status is 200": (r) => r.status === 200 });
  sleep(Math.random() * 3); // think-time so virtual users behave like people
}
```

**Bad Example** — one URL, no ramp, no think-time, no threshold

```js
export const options = { vus: 5000, duration: "30s" }; // instant 5k VUs, no ramp

export default function () {
  // Same cached URL, zero think-time: measures one hot row and likely saturates the
  // load generator itself. No threshold, so the run cannot pass or fail — only "finish".
  http.get("https://staging.example.com/products/1");
}
```

## Common Mistakes

- Blasting a single endpoint with no think-time, which models no real user and hits one
  cached path.
- Starting at full concurrency with no ramp, so you measure a thundering-herd artifact
  instead of steady-state capacity.
- Running without SLO thresholds, leaving the result subjective.
- Load-testing a laptop or an empty database and treating the number as production capacity.
- Ignoring server metrics, so you see *that* it slowed but never *why*.
- Saturating the load generator and reporting the client's limit as the server's.
- Running a stress test against shared infra without warning, causing collateral incidents.

## Production Tips

- Include a stress run to find the breaking point and confirm the system degrades
  gracefully (sheds load, returns `429`/`503`) rather than crashing or corrupting data.
- Run periodic soak tests (hours) to surface slow memory leaks and connection exhaustion
  that short runs never reach.
- Keep the baseline load profile in version control next to the code, and re-run it before
  major releases so capacity is a tracked, comparable number over time.

## AI Review Checklist

- Does the test model a realistic mix of routes with think-time and varied data?
- Is the load pattern (baseline/stress/soak/spike) chosen deliberately for the question asked?
- Are pass/fail thresholds (p95, error rate, throughput) defined before the run and enforced?
- Does the run measure during a steady plateau after a gradual ramp?
- Is it run against production-like infra and data, with server metrics correlated?
- Is the load generator confirmed to have headroom so it is not the bottleneck?

## Related

- `knowledge/testing/15-performance-testing.md`
- `knowledge/testing/12-api-testing.md`
- `knowledge/testing/26-observability.md`
- `knowledge/testing/25-production-testing.md`
- `knowledge/testing/04-e2e-testing.md`
