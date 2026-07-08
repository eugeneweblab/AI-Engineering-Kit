---
id: performance/20-capacity-planning
topic: performance
slug: capacity-planning
title: "Capacity Planning"
type: doc
order: 20
status: ready
tags: [performance, capacity-planning]
related: [performance/21-scalability, performance/22-load-testing, performance/02-metrics, performance/17-monitoring, performance/23-performance-budget]
when_to_use: "Read before sizing infrastructure, setting autoscaling limits, or preparing for a traffic event."
---
# Capacity Planning

## Purpose

This document defines how to decide *how much* infrastructure a system needs: measuring
per-unit capacity, applying headroom, and forecasting against expected demand. It exists
so an agent provisions for the load the system will actually face, without either paging
at 2am from saturation or burning budget on idle machines.

Capacity planning is the bridge between a [load test](22-load-testing.md) (what one
configuration can handle) and [scalability](21-scalability.md) (how to add more). It turns
measured capacity into a provisioning and autoscaling decision.

## Why It Matters

Systems do not degrade linearly — they fall off a cliff. Latency stays flat as utilization
climbs, then explodes near saturation as queues build (this is queuing theory, not a
metaphor). A service comfortable at 70% CPU can be timing out at 85%. Plan capacity by
guessing and you discover the cliff during your biggest traffic day. Plan it from measured
per-node capacity plus headroom, and the cliff never arrives. The cost of getting this
wrong is an outage at the worst possible moment or a cloud bill several times larger than
necessary.

## Core Principles

- **Capacity is measured, not assumed.** Derive max sustainable throughput per node from a
  [load test](22-load-testing.md), not from a spec sheet or intuition.
- **Never plan to 100% utilization.** Queues form long before saturation. Target a
  utilization ceiling (commonly 60–70% CPU for latency-sensitive services) so a spike or a
  failed node has somewhere to go.
- **Little's Law sizes concurrency.** `L = λ × W`: concurrent requests in flight equals
  arrival rate times average latency. It tells you thread-pool, connection-pool, and
  worker counts directly.
- **Plan for the peak, not the average.** Daily peaks are often 3–5x the mean; seasonal or
  launch peaks far more. Provisioning for average guarantees you are under-provisioned when
  it matters.
- **Include failure headroom.** N+1 (or N+2): the system must carry full load with one
  node (or one availability zone) down, or a routine failure becomes an outage.
- **Forecast, then re-measure.** Capacity plans decay as code and traffic change. Revisit
  on a schedule and after any major release.

## Best Practices

- Establish the unit of capacity: "one node serves X req/s at p99 < Y ms." Everything else
  is arithmetic from that number.
- Size pools with Little's Law: if you serve 500 req/s at 40ms average, you need ~20
  concurrent slots (`500 × 0.04`); provision pools and thread counts above that.
- Set autoscaling to trigger *before* the cliff — scale out at 60% utilization, not 90%,
  because new nodes take minutes to warm up while the spike is happening now.
- Add explicit headroom for the tail: plan for `peak × safety factor` (e.g. 1.5–2x the
  observed peak) plus N+1 redundancy.
- Track the leading indicators — saturation, queue depth, connection-pool wait — in
  [monitoring](17-monitoring.md), so you see the ceiling approaching weeks out.
- Re-run capacity math after any change to request cost, and before every known traffic
  event (launch, sale, campaign).

## Examples

**Good Example** — measured capacity, headroom, N+1

```text
Measured (from load test): 1 node = 800 req/s at p99 320ms; CPU saturates near 900 req/s.
Utilization ceiling:       70% → plan each node at 630 req/s (leaves headroom for spikes).
Expected peak:             8,000 req/s (Black Friday, 4x normal peak).
Nodes for load:            ceil(8000 / 630) = 13
Failure headroom (N+1):    13 + 1 = 14 nodes; survives one node loss at peak.
Autoscale trigger:         scale out at 60% CPU, cooldown tuned to warmup time.
# Every number traces to a measurement; the plan survives a spike AND a dead node.
```

**Bad Example** — guessed from averages, no headroom

```text
"Average traffic is 1,000 req/s and a node handles ~1,000, so run 1 node.
 Add a second for safety."
# Planned to average, not peak (peak is 4x). Planned to 100% of a spec-sheet number,
# not measured 70% capacity. No N+1 — one node restart during peak = full outage.
# Autoscaling reacts at 90% CPU, minutes too late; the queue has already collapsed.
```

## Common Mistakes

- Planning to average load when peaks are several times higher.
- Sizing to 100% of a node's theoretical capacity, ignoring the latency cliff before
  saturation.
- No N+1 headroom, so a single node or AZ failure cascades into an outage.
- Autoscaling on a threshold so high the new nodes arrive after the incident.
- Trusting vendor "up to X req/s" numbers instead of measuring your own workload.
- Treating the plan as permanent and never revisiting it as request cost drifts.

## Production Tips

- Watch saturation signals (run-queue length, connection-pool wait), not just CPU% —
  they predict the cliff earlier than utilization does.
- Keep a small permanent buffer of warm capacity for latency-sensitive paths; cold-start
  autoscaling cannot catch a sudden spike in time.
- Model cost alongside capacity so the plan is defensible both ways — headroom is
  insurance, not waste, but unbounded over-provisioning is a real bill.

## AI Review Checklist

- Is per-node capacity derived from a load test, not a spec or a guess?
- Does the plan target a utilization ceiling (e.g. 60–70%), not 100%?
- Is concurrency sized with Little's Law (`L = λ × W`)?
- Does provisioning cover the *peak*, with a safety factor, not the average?
- Is there N+1 (or N+2) failure headroom so a node/AZ loss is survivable?
- Does autoscaling trigger early enough to account for node warmup time?

## Related

- `knowledge/performance/21-scalability.md`
- `knowledge/performance/22-load-testing.md`
- `knowledge/performance/02-metrics.md`
- `knowledge/performance/17-monitoring.md`
- `knowledge/performance/23-performance-budget.md`
