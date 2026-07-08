---
id: docker/17-resource-limits
topic: docker
slug: resource-limits
title: "Resource Limits"
type: doc
order: 17
status: ready
tags: [docker, resource-limits]
related: [docker/15-healthchecks, docker/16-logging, docker/22-production, docker/23-orchestration, docker/25-performance]
when_to_use: "Read before running containers on a shared host or reviewing memory/CPU limits in a compose file."
---
# Resource Limits

## Purpose

This document defines how to bound a container's memory, CPU, and process usage so a
single container cannot starve its neighbors or take down the host. It is written so
an agent can set correct limits and reservations and understand how the kernel
enforces them.

By default a container can consume all of the host's memory and CPU. On a shared host
— which is nearly every production host — one misbehaving container will then degrade
or kill every other container on the box. Resource limits turn a container into a good
neighbor with a fixed, predictable footprint.

## Why It Matters

Without limits, resource exhaustion is a host-wide, cascading failure. A memory leak
in one service consumes all RAM; the kernel's OOM killer then reaps *some* process on
the host — often not the offender — and unrelated services die. An unbounded CPU
loop starves every container's scheduling. These failures are hard to diagnose
precisely because the victim is rarely the culprit. Limits contain the blast radius:
a leaking container hits its own ceiling and is killed in isolation, leaving the rest
of the host healthy. The trade-off is that a too-tight limit kills a legitimately
busy container, so limits must be sized from real usage, not guessed.

## Core Principles

- **Every production container gets a memory limit.** Memory is the dangerous
  resource: exceeding the host's RAM invokes the OOM killer, which can kill innocent
  processes. A memory limit makes the offender the victim.
- **Set reservations *and* limits.** A reservation is the guaranteed floor for
  scheduling; a limit is the hard ceiling. Together they give predictable behavior
  under contention.
- **CPU limits throttle; memory limits kill.** Exceeding a CPU limit slows the
  container; exceeding a memory limit terminates it. Size each accordingly.
- **Size from measured usage, not guesses.** Observe real memory/CPU under load, then
  set the limit above the peak with headroom. Too low = OOM kills; too high = no
  protection.
- **Limit process/file descriptors too.** A fork bomb or descriptor leak exhausts the
  host as surely as memory; cap `pids` and `ulimits`.

## Best Practices

- Set a memory hard limit (`mem_limit` / `--memory`) on every long-running container,
  sized above observed peak plus headroom for spikes and garbage collection.
- Set a memory reservation (`--memory-reservation`) as the soft guaranteed floor so
  the scheduler can place the container sensibly under pressure.
- Constrain CPU with `--cpus` (fractional cores, e.g. `1.5`) rather than raw `--cpu-shares`;
  it is absolute and readable, whereas shares are only relative weights.
- Cap process count with `--pids-limit` to contain fork bombs and runaway thread
  creation.
- In compose on a single host, use `mem_limit`/`cpus` (or `deploy.resources` when
  running under Swarm); know which one your runtime actually honors.
- Make the app aware of its limit: for the JVM, Node, or Go, ensure the runtime reads
  cgroup limits so heap/GC sizing matches the container, not the host's total RAM.
- Load-test to find the real ceiling before setting limits; never ship a guessed
  number to production.

## Examples

**Good Example** — memory limit + reservation, bounded CPU and PIDs

```yaml
# compose.yaml — container has a hard ceiling and a guaranteed floor
services:
  app:
    image: myorg/app:1.4.2
    mem_limit: 512m            # hard ceiling: exceed it → this container is OOM-killed
    mem_reservation: 256m      # soft floor: guaranteed for scheduling under pressure
    cpus: 1.5                  # throttled to 1.5 cores; cannot monopolize the host
    pids_limit: 200            # contains fork bombs / thread leaks
```

```bash
# Equivalent for `docker run`
docker run --memory=512m --memory-reservation=256m \
           --cpus=1.5 --pids-limit=200 myorg/app:1.4.2
```

**Bad Example** — no limits; one leak takes down the host

```yaml
services:
  app:
    image: myorg/app:1.4.2
    # No mem_limit → a memory leak consumes all host RAM. The kernel OOM killer
    # then reaps SOME process — possibly the database, not this app — and unrelated
    # containers die. No cpus/pids_limit → a runaway loop or fork bomb starves
    # every other container on the box.
```

## Common Mistakes

- Running production containers with no memory limit, so a leak triggers a host-wide
  OOM event that kills unrelated processes.
- Setting the limit far too low from a guess, causing legitimate load to be OOM-killed
  and mistaken for an app bug.
- Setting a limit but no reservation, so the scheduler has no floor to plan around.
- Assuming a runtime auto-detects the limit — an unaware JVM/Node sizes its heap to
  the host's total RAM and gets OOM-killed at a fraction of it.
- Ignoring `pids`/file-descriptor limits, leaving fork bombs and descriptor leaks
  unbounded.
- Using relative `--cpu-shares` and expecting an absolute cap; shares only matter
  under contention.

## Production Tips

- Alert on containers approaching their memory limit and on OOM-kill events; a rising
  memory curve is a leak signal before it becomes an outage.
- Right-size continuously: review real utilization against limits and adjust, rather
  than setting once and forgetting.
- Leave host headroom — do not sum every container's limit up to 100% of host RAM;
  the kernel, log drivers, and bursts need room too.
- In orchestrators, requests/limits (Kubernetes) or `deploy.resources` (Swarm) drive
  scheduling and eviction; keep them consistent with the single-host values.

## AI Review Checklist

- Does every production container have a memory hard limit sized above measured peak?
- Is a memory reservation set alongside the limit to give the scheduler a floor?
- Is CPU bounded with an absolute `--cpus` value rather than only relative shares?
- Is `pids_limit` (and relevant `ulimits`) set to contain fork/descriptor exhaustion?
- Were the limits derived from load-tested real usage, not guessed?
- Is the language runtime configured to read cgroup limits (heap/GC sized to the
  container, not the host)?

## Related

- `knowledge/docker/15-healthchecks.md`
- `knowledge/docker/16-logging.md`
- `knowledge/docker/22-production.md`
- `knowledge/docker/23-orchestration.md`
- `knowledge/docker/25-performance.md`
