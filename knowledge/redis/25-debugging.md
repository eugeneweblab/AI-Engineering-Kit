---
id: redis/25-debugging
topic: redis
slug: debugging
title: "Redis Debugging"
type: doc
order: 25
status: ready
tags: [redis, debugging, SLOWLOG, MONITOR, LATENCY, latency-monitor-threshold, WRONGTYPE, mem_fragmentation_ratio]
related: [redis/22-monitoring, redis/23-performance, redis/24-testing, redis/28-observability, redis/100-common-antipatterns]
when_to_use: "Read when a Redis-backed system is slow, returning wrong data, using too much memory, or timing out."
---
# Redis Debugging

## Purpose

This document defines how to diagnose Redis problems — latency spikes, wrong
results, memory growth, connection errors — using Redis's own introspection
commands instead of guessing. It shows which tool answers which question so an
agent can go from symptom to root cause quickly and without making things worse.

## Why It Matters

Redis is single-threaded for command execution: one slow command blocks every
other client. So a single `KEYS *` or a large `SMEMBERS` on a hot path can freeze
the whole server, and the symptom ("random timeouts everywhere") looks nothing like
the cause. The right introspection command turns an invisible, system-wide stall
into a specific line of code. Guessing — or worse, running `MONITOR` on a busy
production node — wastes time and can add load to an already struggling server.

## Core Principles

- **Reproduce before you fix.** Confirm the symptom against a specific command,
  key, or client. A fix you cannot reproduce is a guess.
- **Ask the server, don't speculate.** `SLOWLOG`, `LATENCY`, `INFO`, and
  `CLIENT LIST` expose exactly what Redis is doing. Read them first.
- **Never run blocking or firehose commands on production.** `KEYS`, `MONITOR`,
  and `DEBUG SLEEP` block or flood the single thread. Use `SCAN` and `SLOWLOG`.
- **Suspect the big key and the O(N) command.** Most latency mysteries are one
  large collection or one unbounded-range command run on a hot path.
- **Change one thing at a time.** Redis state is global; simultaneous changes make
  the result unattributable.

## Best Practices

- Start with `SLOWLOG GET 20` to see the slowest recent commands with their exact
  arguments and microsecond timing — this usually names the culprit immediately.
- Use `LATENCY LATEST` and `LATENCY DOCTOR` to correlate spikes with fork, AOF
  rewrite, or eviction events, which the command log alone will not show.
- Find oversized keys with `redis-cli --bigkeys` (samples) or `MEMORY USAGE key`
  (exact). A single multi-MB value explains most memory and latency surprises.
- Check `OBJECT ENCODING key` — a hash/zset that has fallen out of its compact
  encoding (`listpack` → `hashtable`/`skiplist`) uses far more memory.
- Inspect connections with `CLIENT LIST`; look for many idle clients (a pool leak)
  or one client with a huge output buffer (a slow consumer).
- Enable keyspace notifications only temporarily when debugging expiry/eviction,
  and turn them off after — they add overhead.

## Examples

**Good Example** — find and confirm the slow command

```bash
# 1. What has been slow? Shows args + duration in microseconds.
redis-cli SLOWLOG GET 5
# 1) 1) (integer) 14        # entry id
#    2) (integer) 1720000000
#    3) (integer) 8213      # 8.2 ms — huge for Redis
#    4) 1) "KEYS"           # the culprit: O(N) scan on a hot path
#       2) "session:*"

# 2. Confirm the key it hit is the size we suspect.
redis-cli DEBUG OBJECT session:index   # or: MEMORY USAGE session:index

# 3. Fix: replace KEYS with a cursor scan that never blocks the server.
redis-cli SCAN 0 MATCH 'session:*' COUNT 100
```

**Bad Example** — debugging by flooding production

```bash
# MONITOR streams EVERY command from EVERY client through the single thread.
# On a busy server this alone can add latency and hide the real problem.
redis-cli MONITOR | grep session      # firehose; makes the incident worse

# KEYS blocks the server for the full scan — the exact command you are hunting.
redis-cli KEYS '*'                     # never do this to diagnose latency
```

## Common Mistakes

- Running `MONITOR` or `KEYS` on production to "see what's happening" and adding load.
- Blaming the network for latency that `SLOWLOG` would have pinned to one command.
- Ignoring `INFO memory` — high `mem_fragmentation_ratio` or hitting `maxmemory`
  causes eviction stalls that look like random slowness.
- Not checking `OBJECT ENCODING`, so a silently de-optimized collection is missed.
- Reading a value that returns `WRONGTYPE` and assuming Redis is broken, when the
  key simply holds a different type than the code expects.
- Leaving keyspace notifications or a high `slowlog` sampling rate on after debugging.

## Production Tips

- Set `slowlog-log-slower-than` to a low threshold (e.g. 10000 µs) so slow commands
  are captured continuously, and scrape `SLOWLOG` into your logs.
- Keep `latency-monitor-threshold` enabled so `LATENCY HISTORY` has data when an
  incident happens — you cannot enable it retroactively for a past spike.
- When memory is the issue, run `MEMORY DOCTOR` and `MEMORY STATS` before restarting;
  a restart erases the evidence.

## AI Review Checklist

- Is the diagnosis backed by `SLOWLOG`/`LATENCY`/`INFO` output, not a guess?
- Does any debugging step run `KEYS`, `MONITOR`, or `DEBUG SLEEP` on production? (It must not.)
- Was the problem reproduced against a specific command or key before changing code?
- Were big keys and `OBJECT ENCODING` checked when memory or latency is the symptom?
- Are temporary debug settings (notifications, verbose slowlog) reverted afterward?

## Related

- `knowledge/redis/22-monitoring.md`
- `knowledge/redis/23-performance.md`
- `knowledge/redis/24-testing.md`
- `knowledge/redis/28-observability.md`
- `knowledge/redis/100-common-antipatterns.md`
