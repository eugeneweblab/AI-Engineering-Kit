---
id: linux/18-performance
topic: linux
slug: performance
title: "Linux Performance"
type: doc
order: 18
status: ready
tags: [linux, performance, cause, vmstat, perf, MemoryMax]
related: [linux/06-processes, linux/16-monitoring, linux/19-debugging, linux/11-storage, linux/27-troubleshooting]
when_to_use: "Read before diagnosing a slow or overloaded Linux host, or tuning one for higher throughput."
---
# Linux Performance

## Purpose

This document defines how to measure, reason about, and improve the performance of a
Linux host: CPU, memory, disk I/O, and network. It is written so an agent can find the
real bottleneck with data instead of guessing, and change one thing at a time.

Performance work answers "where is the time going, and why?". It is investigation, not
decoration. Every change must be justified by a measurement before it and validated by a
measurement after it.

## Why It Matters

A slow system is not just an annoyance — under load it drops requests, misses deadlines,
and cascades into outages. Worse, most performance "fixes" applied without measurement
are cargo-cult: they add complexity, hide the real problem, and sometimes make things
slower. The cost of a wrong guess is compounding technical debt. Because the bottleneck
is almost never where intuition says it is, the discipline of measuring first is what
separates a fix from a superstition.

## Core Principles

- **Measure before you change.** Get a baseline number first; without it you cannot tell
  whether a change helped, hurt, or did nothing.
- **Find the one bottleneck.** At any moment a system is limited by a single resource
  (CPU, memory, disk, or network). Tuning anything else is wasted effort.
- **Work top-down.** Start with a system-wide view (`top`, `vmstat`), then drill into the
  offending subsystem. Do not start by profiling a random function.
- **Change one variable at a time.** Two simultaneous changes make the result
  uninterpretable — you learn nothing about either.
- **Optimize the common case.** A 5% slice of runtime cannot yield a 30% speedup, no
  matter how clever the fix. Attack the largest cost first (Amdahl's law).

## Best Practices

- Take a baseline under representative load before tuning: throughput, latency
  percentiles (p50/p95/p99), and the saturating resource. Save it.
- Use the USE method per resource: check **U**tilization, **S**aturation, and **E**rrors.
  High utilization is fine; saturation (a growing queue) is the problem.
- Read load average relative to core count: a load of 8 on 8 cores is full, on 2 cores it
  is a 4x backlog. `nproc` gives the count.
- Distinguish waiting from working. High `%wa` (iowait) in `top` means the CPU is idle
  waiting on disk — adding CPU will not help; faster storage or fewer I/Os will.
- Watch for memory pressure via swap activity (`si`/`so` in `vmstat`), not just free
  memory. Linux uses free RAM for page cache on purpose — low "free" is normal.
- Profile hot code with `perf` (`perf top`, `perf record`/`perf report`) rather than
  adding print statements; it samples with near-zero overhead.
- Benchmark on hardware and data that resemble production. A laptop SSD result does not
  predict a network-attached volume.

## Examples

**Good Example** — measure, isolate the resource, then act

```bash
# 1. System-wide view: is the box CPU-bound, I/O-bound, or memory-bound?
vmstat 1 5          # watch 'r' (run queue), 'wa' (iowait), 'si/so' (swap)

# 2. iowait is high -> the bottleneck is disk, not CPU. Confirm which device.
iostat -xz 1 3      # look at %util near 100 and rising 'await' (latency)

# 3. Find the process doing the I/O before changing anything.
pidstat -d 1 3      # per-process kB read/write per second

# 4. Only now act on the real cause (e.g. a process fsync-ing per row),
#    then re-run the same commands to confirm the number moved.
```

**Bad Example** — guessing and tuning blind

```bash
# The app "feels slow", so we throw resources and knobs at it with no data.
sysctl -w vm.swappiness=0          # cargo-culted; may cause OOM kills under pressure
nice -n -20 ./app                  # raising priority does nothing if the box is I/O-bound
# No baseline was taken, so there is no way to know if any of this helped,
# and the actual cause (a missing index causing full-table disk scans) is untouched.
```

## Common Mistakes

- Optimizing without a baseline, so "improvements" cannot be proven and regressions slip
  through unnoticed.
- Reading load average without dividing by core count, then panicking at a healthy number.
- Treating low "free memory" as a problem when it is just page cache doing its job.
- Adding CPU or threads to an I/O-bound or lock-bound workload, which cannot help.
- Micro-optimizing a function that is 2% of runtime while ignoring a 60% hotspot.
- Benchmarking once and trusting it; noise and warm caches make single runs unreliable.

## Production Tips

- Keep lightweight always-on telemetry (see [monitoring](16-monitoring.md)) so you have
  history when an incident starts, not just a live snapshot.
- Record flame graphs from `perf` during incidents; they are the fastest way to see where
  CPU time actually goes.
- Set resource limits (cgroups / systemd `CPUQuota`, `MemoryMax`) so one runaway process
  cannot starve the whole host.
- Re-baseline after major dependency or kernel upgrades — performance characteristics
  shift silently.

## AI Review Checklist

- Is there a documented baseline (throughput and latency percentiles) before any tuning?
- Was the limiting resource identified with data (CPU vs I/O vs memory vs network)?
- Is load average interpreted relative to `nproc`?
- Does each proposed change target the measured bottleneck, not a guess?
- Is only one variable changed per experiment, with an after-measurement?
- Are sysctl / priority tweaks justified, or copied blindly from a blog?

## Related

- `knowledge/linux/06-processes.md`
- `knowledge/linux/16-monitoring.md`
- `knowledge/linux/19-debugging.md`
- `knowledge/linux/11-storage.md`
- `knowledge/linux/27-troubleshooting.md`
