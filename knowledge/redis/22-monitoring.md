---
id: redis/22-monitoring
topic: redis
slug: monitoring
title: "Monitoring"
type: doc
order: 22
status: ready
tags: [redis, monitoring]
related: [redis/23-performance, redis/28-observability, redis/20-persistence, redis/18-replication]
when_to_use: "Read before shipping Redis to production or when diagnosing latency, memory, or eviction issues."
---
# Monitoring

## Purpose

This document defines what to measure on a Redis instance and how to read it:
`INFO` sections, latency, memory and eviction, keyspace hits, replication health,
and slow commands. The aim is that an agent can instrument Redis so that problems
are visible *before* an outage, and can diagnose one when metrics point the way.
For deeper tracing and app-level telemetry see [observability](28-observability.md).

Monitoring answers "is this instance healthy right now, and what changed when it
was not?".

## Why It Matters

Redis is single-threaded for command execution, so **one slow command blocks every
other client**. A `KEYS *` on a big keyspace, an unbounded `LRANGE`, or a heavy Lua
script raises latency for the whole system at once — and without metrics you see
only "the app got slow", not the cause. The signals that predict Redis incidents —
rising memory toward `maxmemory`, growing evictions, replication lag, a filling
slowlog — are all cheap to collect and are invisible unless you deliberately watch
them. Instrumenting after the outage is too late.

## Core Principles

- **Watch memory against `maxmemory`, not in isolation.** Approaching the limit
  triggers evictions or OOM errors; the trend is the warning.
- **Latency is a first-class metric because Redis is single-threaded.** Track it at
  the server (`INFO commandstats`, `LATENCY`) and the client. Tail latency (p99)
  matters more than average.
- **The slowlog names your blocking commands.** Any command over your threshold is
  a candidate to hurt every other client; treat it as an alert, not a curiosity.
- **Cache health is the hit rate.** `keyspace_hits` vs `keyspace_misses` tells you
  whether the cache is doing its job or thrashing.
- **Instrument before you need it.** The data that explains an incident must
  already be flowing when the incident starts.

## Best Practices

- Scrape `INFO` regularly and track: `used_memory` / `maxmemory`,
  `mem_fragmentation_ratio`, `evicted_keys`, `keyspace_hits`/`keyspace_misses`,
  `connected_clients`, `blocked_clients`, `instantaneous_ops_per_sec`, and
  `rejected_connections`.
- Set the **slowlog** threshold (`slowlog-log-slower-than`, e.g. 10000 µs) and pull
  `SLOWLOG GET` into your monitoring; alert on new entries.
- Use `LATENCY LATEST` / `LATENCY DOCTOR` and enable latency monitoring
  (`latency-monitor-threshold`) to catch fork stalls, slow `fsync`, and expiry
  spikes.
- Monitor **replication**: `master_link_status`, and lag as `master_repl_offset`
  minus each replica's offset (see [replication](18-replication.md)).
- Monitor **persistence**: `rdb_last_bgsave_status`, `aof_last_write_status` — a
  failing backup is a silent, high-severity condition.
- Export metrics with a dedicated exporter (e.g. `redis_exporter`) into your
  metrics stack; alert on thresholds, not on dashboards nobody watches.
- Track hit rate and eviction *rate of change*, not just point values — a sudden
  eviction spike signals a hot/oversized workload.

## Examples

**Good Example** — computed, actionable signals

```python
info = r.info()

# Cache hit ratio: is the cache actually saving backend load, or thrashing?
hits, misses = info["keyspace_hits"], info["keyspace_misses"]
hit_ratio = hits / (hits + misses) if (hits + misses) else 1.0
gauge("redis.hit_ratio", hit_ratio)            # alert if this drops sharply

# Memory pressure relative to the limit, not an absolute byte count.
used, limit = info["used_memory"], info.get("maxmemory", 0)
if limit:
    gauge("redis.mem_used_ratio", used / limit)  # alert well before it hits 1.0

# Evictions are a rate: rising = workload exceeds capacity.
gauge("redis.evicted_keys", info["evicted_keys"])
```

**Bad Example** — diagnosing blind and blocking the server to do it

```python
# "Let me see what's slow." KEYS scans the ENTIRE keyspace, single-threaded,
# blocking every other client for the duration. The monitoring itself causes
# the latency spike it was meant to find.
big = redis_client.keys("*")            # O(N) over all keys, blocks the server
print(f"{len(big)} keys")

# No metrics pipeline: the only signal is a human running commands by hand,
# after users already complained. Nothing was watched, so nothing was caught.
```

## Common Mistakes

- Running `KEYS *`, `SMEMBERS` on huge sets, or `DEBUG SLEEP` in production —
  each blocks the single command thread. Use `SCAN` and its cursor variants.
- Watching `used_memory` without `maxmemory`, so eviction/OOM arrives unannounced.
- Ignoring the slowlog, so blocking commands are only found post-incident.
- Alerting on averages; a healthy average hides a bad p99.
- Not monitoring replication lag or backup status until failover/restore fails.
- Building dashboards but no alerts — nobody is watching at 3am.

## Production Tips

- Baseline p50/p99 latency and ops/sec in normal traffic so anomalies are obvious.
- Alert on: memory ratio > 80%, sustained evictions, `master_link_status:down`,
  failed bgsave/AOF, `rejected_connections` > 0, and new slowlog entries.
- Keep `latency-monitor-threshold` on in production; it is cheap and explains stalls.
- Pull `INFO everything` into your metrics store rather than sampling one field by
  hand; the correlations across sections are what diagnose incidents.

## AI Review Checklist

- Is memory tracked as a ratio to `maxmemory`, with an alert before the limit?
- Is the slowlog enabled with a threshold, and are entries alerted on?
- Is cache hit ratio computed from `keyspace_hits`/`keyspace_misses`?
- Are replication lag and persistence status monitored?
- Is diagnostic code free of blocking commands (`KEYS *`, big `SMEMBERS`)?
- Are there alerts, not just dashboards, for the key thresholds?

## Related

- `knowledge/redis/23-performance.md`
- `knowledge/redis/28-observability.md`
- `knowledge/redis/20-persistence.md`
- `knowledge/redis/18-replication.md`
