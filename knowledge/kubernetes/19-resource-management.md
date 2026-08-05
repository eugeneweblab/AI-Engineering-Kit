---
id: kubernetes/19-resource-management
topic: kubernetes
slug: resource-management
title: "Resource Management"
type: doc
order: 19
status: ready
tags: [kubernetes, resource-management, LimitRange, requests, ResourceQuota, limits, Guaranteed]
related: [kubernetes/20-autoscaling, kubernetes/04-pods, kubernetes/23-monitoring, kubernetes/26-production]
when_to_use: "Read before setting CPU/memory requests and limits on any container, or when a pod is being OOM-killed, throttled, or evicted."
---
# Resource Management

## Purpose

This document defines how to declare a container's CPU and memory needs with
`requests` and `limits`, and how those values drive scheduling, throttling, and
eviction. It is written so an agent can size a workload correctly and avoid the two
failure modes — starved neighbors and OOM-killed pods.

`requests` are what the scheduler reserves; `limits` are the ceiling the kubelet
enforces. They are different knobs with different consequences. Getting them right is
the foundation for [autoscaling](20-autoscaling.md), which reads these values.

## Why It Matters

The scheduler places pods using `requests` alone — it never looks at limits or actual
usage. Set requests too low and nodes get overcommitted until real load causes cascading
evictions; too high and you pay for idle capacity and pods go Pending. Memory limits are
a hard wall: exceed it and the kernel OOM-kills the container instantly, mid-request,
with no graceful shutdown. CPU limits do not kill — they throttle — which shows up as
mysterious latency, not errors. These behaviors are non-obvious, so resource specs must
be reasoned about, not copied.

## Core Principles

- **Always set requests and memory limits.** A container with no request can be
  scheduled anywhere and starve neighbors; with no memory limit it can consume the whole
  node and trigger system-level OOM.
- **CPU is compressible; memory is not.** Over-CPU means throttling (slow); over-memory
  means the OOM killer (dead). Size memory with more headroom than CPU.
- **QoS class follows your numbers.** Requests == limits on every resource gives
  `Guaranteed` (evicted last); requests < limits gives `Burstable`; nothing set gives
  `BestEffort` (evicted first). Choose deliberately.
- **Request the steady state, not the peak.** Requests are a reservation held 24/7. Size
  them to typical usage and let limits (or autoscaling) absorb spikes.
- **Measure, then set.** Derive values from observed usage (p95/p99), not guesses.

## Best Practices

- Set memory `request == limit` for latency-sensitive services so they are `Guaranteed`
  and never evicted for memory pressure.
- Prefer setting a CPU `request` but **omitting the CPU limit** for most services: this
  lets a container burst into idle node capacity while still guaranteeing its request.
  Set a CPU limit only when you need hard, predictable isolation.
- Enforce baselines with a `LimitRange` (default request/limit per namespace) and caps
  with a `ResourceQuota` (total per namespace) so unspecified pods do not slip through.
- Use units precisely: CPU in millicores (`500m` = half a core), memory in binary units
  (`Mi`, `Gi`), never bare bytes you have to count.
- For the JVM, Go, and Node, align the runtime's heap/`GOMAXPROCS` to the container
  limit; otherwise the runtime sees the whole node and blows the memory limit.
- Review `kubectl top pods` and OOMKilled restart counts to correct sizing over time.

## Examples

**Good Example** — reasoned requests, memory guaranteed, CPU allowed to burst

```yaml
resources:
  requests:
    cpu: "250m"        # steady-state reservation the scheduler honors
    memory: "256Mi"    # request == limit below → Guaranteed for memory
  limits:
    # no CPU limit: burst into spare node capacity instead of being throttled
    memory: "256Mi"    # hard, non-compressible ceiling; sized from observed p99 + headroom
```

**Bad Example** — no requests, tiny memory limit, mismatched CPU

```yaml
resources:
  limits:
    cpu: "100m"        # aggressive throttle → tail-latency spikes under load
    memory: "64Mi"     # below real usage → container OOMKilled mid-request
  # no requests at all → BestEffort QoS, evicted first, scheduled onto full nodes
```

## Common Mistakes

- Omitting requests, producing `BestEffort` pods that are evicted first and scheduled
  onto already-full nodes.
- Setting a memory limit below real usage, causing repeated `OOMKilled` restarts.
- Copying CPU/memory numbers between services instead of measuring each one.
- Setting a low CPU limit and then debugging "slow" pods that are actually throttled.
- Letting the JVM/Node runtime detect the node's total memory, not the cgroup limit.
- No `LimitRange`/`ResourceQuota`, so a single namespace can exhaust the cluster.
- Assuming `limits` affect scheduling — the scheduler only reads `requests`.

## Production Tips

- Track container `memory working set` vs limit and CPU throttling metrics; alert before
  OOM, not after.
- Roll out a `LimitRange` in every namespace so new deployments inherit safe defaults.
- Re-derive requests quarterly from p95 usage — traffic and code both drift.

## AI Review Checklist

- Does every container set a CPU request and a memory request?
- Does every container set a memory limit sized above observed p99 usage?
- Is memory `request == limit` for latency-sensitive workloads (Guaranteed QoS)?
- Are CPU limits omitted for burst workloads, or justified where present?
- Are units correct (`m` for CPU, `Mi`/`Gi` for memory)?
- Is the container runtime's heap aligned to the memory limit, not the node?
- Does the namespace have a `LimitRange` and `ResourceQuota`?

## Related

- `knowledge/kubernetes/20-autoscaling.md`
- `knowledge/kubernetes/04-pods.md`
- `knowledge/kubernetes/23-monitoring.md`
- `knowledge/kubernetes/26-production.md`
