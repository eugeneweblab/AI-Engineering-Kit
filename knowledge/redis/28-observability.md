---
id: redis/28-observability
topic: redis
slug: observability
title: "Redis Observability"
type: doc
order: 28
status: ready
tags: [redis, observability]
related: [redis/22-monitoring, redis/23-performance, redis/25-debugging, redis/27-production, redis/29-tooling]
when_to_use: "Read when setting up metrics, dashboards, or alerts for a Redis deployment, or defining what to watch."
---
# Redis Observability

## Purpose

This document defines what to measure on a Redis deployment and how to expose it:
the handful of metrics that predict outages, where they come from (`INFO`,
`SLOWLOG`, `LATENCY`), and which alerts actually matter. It exists so an operator or
agent can tell *before* users do that Redis is running out of memory, evicting the
working set, or slowing down.

## Why It Matters

Redis fails predictably and the warning signs are all in `INFO` — but only if you
are scraping them. Memory creeps toward `maxmemory`, the eviction rate climbs, the
cache hit ratio drops, replica lag grows: each is visible minutes before the outage.
Without these metrics, the first signal is a user-facing timeout and a blind
incident. Observability turns Redis's internal counters into early warnings, and
distinguishes "Redis is slow" from "one command is slow" — a distinction that
decides where you look.

## Core Principles

- **Scrape `INFO` continuously.** It is the source of truth for memory, clients,
  persistence, replication, and keyspace stats. Everything else builds on it.
- **Track rates and ratios, not just absolutes.** `evicted_keys/sec` and hit ratio
  reveal trends; a single `used_memory` number does not tell you where it is heading.
- **Alert on leading indicators.** Memory nearing `maxmemory`, rising evictions,
  growing replica lag — these precede failure. Alert on them, not just on "down".
- **Keep latency history on.** Enable `latency-monitor` and a low `slowlog`
  threshold so evidence exists when a spike happens; you cannot capture it after.
- **Correlate Redis with the app.** A cache-hit drop should line up with backend
  load; alerts are actionable when tied to user impact.

## Best Practices

- Export metrics with a maintained Prometheus exporter (`redis_exporter`) rather than
  parsing `INFO` by hand, and dashboard them (Grafana / RedisInsight).
- Watch these core signals, each for a specific reason:
  - `used_memory` vs `maxmemory` — the OOM/eviction runway.
  - `evicted_keys` (rate) — non-zero and rising means the working set no longer fits.
  - `keyspace_hits` / `keyspace_misses` → hit ratio — cache effectiveness.
  - `instantaneous_ops_per_sec` and command latency — load and responsiveness.
  - `connected_clients` and `blocked_clients` — pool leaks and blocking-command pileups.
  - `master_link_status` / `master_repl_offset` lag — replication health.
  - `mem_fragmentation_ratio` — memory efficiency (>1.5 warrants attention).
  - `rejected_connections`, `rdb_last_bgsave_status`, `aof_last_write_status` — hard failures.
- Set `slowlog-log-slower-than` low (e.g. 10000 µs) and ship `SLOWLOG` entries so slow
  commands are named, not just counted.
- Define alerts with thresholds tied to consequences (memory > 85% of `maxmemory`,
  evictions > 0 sustained, replica lag > N seconds), not arbitrary numbers.

## Examples

**Good Example** — scrape the signals that predict failure

```bash
# Hit ratio and evictions from INFO — the two numbers that reveal a failing cache.
redis-cli INFO stats | grep -E 'keyspace_(hits|misses)|evicted_keys'
# keyspace_hits:9821004
# keyspace_misses:120553      # hits/(hits+misses) ~= 0.99 -> healthy
# evicted_keys:0              # rising above 0 = working set no longer fits

# Memory runway — alert when used_memory approaches maxmemory.
redis-cli INFO memory | grep -E 'used_memory:|maxmemory:|mem_fragmentation_ratio'

# Exporter turns all of this into Prometheus metrics for dashboards + alerts.
redis_exporter --redis.addr=rediss://10.0.0.5:6379   # scrape /metrics
```

**Bad Example** — no metrics, reactive-only

```bash
# "Monitoring" = a human runs PING and eyeballs it occasionally.
redis-cli PING            # only tells you up/down, nothing about memory/evictions/latency

# First real signal is a customer ticket, because used_memory, evicted_keys,
# hit ratio, and replica lag were never scraped or alerted on.
```

## Common Mistakes

- Alerting only on "is it up", missing the memory/eviction trend that precedes the outage.
- Not scraping `INFO`, so there is no history to investigate a past incident.
- Watching absolute `used_memory` but never comparing it to `maxmemory`.
- Ignoring the hit ratio, so a cache that has quietly stopped working goes unnoticed.
- `slowlog` and `latency-monitor` left at defaults, so spike evidence is missing.
- No replication-lag or `bgsave`/AOF-status alert, so silent data-durability failures accrue.
- Parsing `INFO` with brittle homemade scripts instead of a maintained exporter.

## Production Tips

- Dashboard the golden set (memory runway, eviction rate, hit ratio, ops/sec, p99
  latency, replica lag) on one screen so an incident is diagnosable at a glance.
- Alert on `rdb_last_bgsave_status:err` and `aof_last_write_status:err` — a failing
  snapshot means your backups are stale right when you will need them.
- Track per-command latency percentiles, not averages; Redis's tail latency (fork,
  eviction) is what users feel.

## AI Review Checklist

- Is `INFO` scraped continuously via a maintained exporter, with history retained?
- Are memory-vs-`maxmemory`, eviction rate, and hit ratio all monitored and alerted?
- Are alerts set on leading indicators (memory runway, evictions, replica lag), not just "down"?
- Are `slowlog` and `latency-monitor` enabled so spike evidence exists?
- Are persistence failures (`rdb_last_bgsave_status`, `aof_last_write_status`) alerted?
- Is latency tracked as percentiles rather than averages?

## Related

- `knowledge/redis/22-monitoring.md`
- `knowledge/redis/23-performance.md`
- `knowledge/redis/25-debugging.md`
- `knowledge/redis/27-production.md`
- `knowledge/redis/29-tooling.md`
