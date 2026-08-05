---
id: postgresql/27-tuning
topic: postgresql
slug: tuning
title: "Tuning"
type: doc
order: 27
status: ready
tags: [postgresql, tuning, work_mem, shared_buffers, max_connections, autovacuum_vacuum_scale_factor, effective_cache_size, EXPLAIN]
related: [postgresql/02-configuration, postgresql/16-performance, postgresql/05-query-planner, postgresql/20-vacuum, postgresql/17-monitoring]
when_to_use: "Read before changing PostgreSQL memory, planner, or autovacuum settings to improve performance."
---
# Tuning

## Purpose

This document defines how to tune PostgreSQL memory, planner cost, and autovacuum
settings safely — from a measured baseline, toward a specific bottleneck, with each
change verified. It is written so an agent changes settings that matter and can prove
they helped.

Most "tuning" that matters is not config at all: it is a missing index or a bad query
plan. This document covers the server-level knobs, and where they help versus where a
schema or query fix is the real answer.

## Why It Matters

PostgreSQL ships with conservative defaults meant to start on almost any hardware, so a
production server is usually under-configured for its RAM. But the opposite failure —
copying "optimized" settings from a blog — is worse: `work_mem` set too high multiplies
across concurrent sorts and triggers the OOM killer, which crashes the whole cluster.
Tuning is a per-workload, per-hardware exercise. The cost of getting it wrong is not
slowness; it is instability under load, which appears only at peak.

## Core Principles

- **Baseline before you touch anything.** Record current throughput, latency, and the
  target metric. A change you cannot compare is not tuning.
- **Fix the query before the config.** An index or a rewrite usually beats any memory
  knob by an order of magnitude; config tuning has diminishing returns after that.
- **`work_mem` is per-operation, not per-connection.** One query can use several
  multiples of it; multiply by concurrency before you raise it.
- **Change one setting, measure, keep or revert.** Batched config changes make cause and
  effect impossible to attribute.
- **Autovacuum keeps performance stable; do not disable it.** Turning it off trades a
  small ongoing cost for catastrophic bloat and wraparound later.

## Best Practices

- Set `shared_buffers` to roughly 25% of RAM as a starting point; Postgres relies on the
  OS page cache too, so more is not always better. Measure the cache hit ratio.
- Set `effective_cache_size` to ~50–75% of RAM. It does not allocate memory — it tells the
  planner how much cache to expect, steering it toward index scans.
- Raise `work_mem` cautiously and per-workload. Compute a safe ceiling as roughly
  `RAM_budget / (max_connections × expected_sorts_per_query)`; set higher values per-session
  for known heavy analytics rather than globally.
- Set `random_page_cost` to `1.1` on SSD/NVMe (default `4.0` assumes spinning disks) so the
  planner stops over-penalizing index scans.
- Tune autovacuum to be *more* aggressive on large, high-churn tables — lower
  `autovacuum_vacuum_scale_factor` per-table so vacuum runs before bloat accumulates.
- Set `max_wal_size` high enough that checkpoints are time-driven, not forced by WAL
  volume; forced checkpoints cause I/O spikes.
- Use `pg_stat_statements` and `EXPLAIN (ANALYZE, BUFFERS)` to confirm a setting change
  actually moved the target query, not just the microbenchmark.

## Examples

**Good Example** — settings sized to hardware, verified against a metric

```ini
# 32 GB RAM server, OLTP workload, SSD storage.
shared_buffers = '8GB'            # ~25% RAM; OS cache holds the rest
effective_cache_size = '24GB'     # planner hint only, no allocation -> favors index scans
work_mem = '32MB'                 # per-op; 200 conns * a few sorts stays well under RAM
random_page_cost = 1.1            # SSD: index scans are cheap, stop over-penalizing them
max_wal_size = '4GB'              # checkpoints spread out, fewer I/O spikes
```

```sql
-- Heavy one-off analytics query: raise work_mem for THIS session only, not globally.
SET LOCAL work_mem = '256MB';                       -- avoids a temp-file sort on disk
EXPLAIN (ANALYZE, BUFFERS) SELECT ... GROUP BY ...; -- confirm the on-disk sort is gone
```

**Bad Example** — cargo-culted numbers that crash under load

```ini
# Copied from a "make Postgres fast" post, no relation to this server's RAM or workload.
shared_buffers = '24GB'           # 75% of 32GB starves the OS cache and other processes
work_mem = '1GB'                   # 200 connections * multiple sorts -> tens of GB -> OOM kill
autovacuum = off                   # "vacuum is slow" -> guaranteed bloat + wraparound halt
random_page_cost = 4.0             # left at spinning-disk default on an SSD -> avoids indexes
```

## Common Mistakes

- Setting `work_mem` globally high and hitting the OOM killer at peak concurrency.
- Setting `shared_buffers` to 60–80% of RAM and starving the OS cache Postgres also uses.
- Disabling autovacuum to "save I/O," then paying with bloat and a wraparound emergency.
- Tuning config before fixing a query that a single index would speed up 100×.
- Leaving `random_page_cost` at `4.0` on SSD, so the planner avoids good index scans.
- Changing several settings at once, unable to say which one helped or hurt.

## Production Tips

- Apply per-table autovacuum settings on your largest, hottest tables rather than global
  defaults sized for small tables.
- Use `ALTER SYSTEM` + `pg_reload_conf()` for reloadable settings; know which require a
  restart (`shared_buffers`, `max_connections`) and schedule those.
- Load-test config changes at production concurrency; a setting safe at 10 connections can
  OOM at 200.
- Keep config in version control so every change is reviewable and revertible.

## AI Review Checklist

- Was a baseline metric recorded before the change?
- Is `work_mem` justified against `max_connections` × sorts, not set globally high?
- Is `shared_buffers` ~25% of RAM, leaving room for the OS cache?
- Is `random_page_cost` lowered for SSD storage?
- Is autovacuum enabled and tuned per-table for high-churn tables (never disabled)?
- Was the change verified against the target query, one setting at a time?

## Related

- `knowledge/postgresql/02-configuration.md`
- `knowledge/postgresql/16-performance.md`
- `knowledge/postgresql/05-query-planner.md`
- `knowledge/postgresql/20-vacuum.md`
- `knowledge/postgresql/17-monitoring.md`
