---
id: postgresql/20-vacuum
topic: postgresql
slug: vacuum
title: "Vacuum"
type: doc
order: 20
status: ready
tags: [postgresql, vacuum, VACUUM, pg_repack, pg_stat_user_tables, autovacuum_vacuum_scale_factor, autovacuum_freeze_max_age, idle_in_transaction_session_timeout]
related: [postgresql/21-analyze, postgresql/06-transactions, postgresql/16-performance, postgresql/17-monitoring, postgresql/27-tuning]
when_to_use: "Read before tuning autovacuum, diagnosing table/index bloat or transaction-ID wraparound warnings, or running a manual VACUUM on a large table."
---
# Vacuum

## Purpose

This document defines how PostgreSQL reclaims dead row versions and prevents transaction-ID
wraparound via `VACUUM` and, primarily, the autovacuum daemon. It is written so an agent can
tune autovacuum correctly, recognize bloat and wraparound risk, and choose the right
`VACUUM` variant without freezing a production table.

Vacuuming updates the visibility and free-space bookkeeping that keeps a table healthy;
keeping the *planner's* statistics fresh is the related but separate job of
[ANALYZE](21-analyze.md). Autovacuum does both, but they solve different problems.

## Why It Matters

PostgreSQL uses MVCC: an `UPDATE` or `DELETE` does not overwrite a row, it writes a new
version and leaves the old one as a "dead tuple". Without vacuuming, dead tuples accumulate
forever — tables and indexes bloat, disk fills, and every scan wades through corpses, so
query latency climbs even though row counts look flat. Worse, PostgreSQL's 32-bit
transaction IDs wrap around; if vacuum never freezes old rows, the database will *shut down
to protect data* at ~2 billion transactions. Both failure modes are slow-building and then
sudden. Autovacuum exists to prevent them, but its defaults are tuned for small databases
and routinely under-service large, write-heavy tables.

## Core Principles

- **Autovacuum is not optional.** Leave it on. Manual `VACUUM` supplements it; it does not
  replace it. Disabling autovacuum guarantees eventual bloat or wraparound.
- **Bloat comes from dead tuples the daemon cannot keep up with**, usually because the
  per-table threshold scales too slowly for the table's write rate.
- **A long-running transaction holds back the "vacuum horizon".** Vacuum cannot remove a
  dead tuple that some open snapshot might still see, so idle-in-transaction sessions cause
  bloat cluster-wide, not just in their own tables.
- **`VACUUM` is online; `VACUUM FULL` is not.** Plain `VACUUM` reclaims space for reuse
  without an exclusive lock. `VACUUM FULL` rewrites the table, takes an `ACCESS EXCLUSIVE`
  lock, and blocks all reads and writes — never run it casually on a live table.
- **Freezing prevents wraparound.** Aggressive "anti-wraparound" autovacuums are mandatory
  and cannot be skipped; plan for their I/O rather than being surprised by it.

## Best Practices

- Keep autovacuum enabled globally. Do not set `autovacuum = off`, ever, on a real database.
- Lower `autovacuum_vacuum_scale_factor` for large, high-churn tables. The default `0.2`
  means "wait until 20% of the table is dead" — on a 100M-row table that is 20M dead tuples.
  Set it per-table: `ALTER TABLE t SET (autovacuum_vacuum_scale_factor = 0.02);`
- Raise `autovacuum_max_workers` and, on modern hardware, increase
  `autovacuum_vacuum_cost_limit` (or lower `autovacuum_vacuum_cost_delay`) so the daemon is
  not artificially throttled and falls behind.
- Monitor dead tuples and last-vacuum time via `pg_stat_user_tables`
  (`n_dead_tup`, `last_autovacuum`). Alert when dead tuples grow unbounded.
- Watch wraparound headroom with `age(datfrozenxid)` per database and `age(relfrozenxid)`
  per table; investigate long before `autovacuum_freeze_max_age` (default 200M).
- Hunt down long-running and `idle in transaction` sessions — they pin the vacuum horizon.
  Set `idle_in_transaction_session_timeout` to bound them.
- Use plain `VACUUM (VERBOSE)` to reclaim space online. Reserve `VACUUM FULL` for a
  maintenance window, or use `pg_repack` to rebuild a bloated table without the long lock.

## Examples

**Good Example** — tune a hot table and vacuum it online

```sql
-- A high-churn table: make autovacuum trigger at ~2% dead instead of 20%,
-- and analyze more eagerly too. Per-table settings override the global defaults.
ALTER TABLE events SET (
  autovacuum_vacuum_scale_factor  = 0.02,   -- trigger vacuum sooner → less bloat
  autovacuum_analyze_scale_factor = 0.02,   -- keep planner stats fresh on churn
  autovacuum_vacuum_cost_limit    = 2000    -- let it work faster on this table
);

-- Reclaim space online; VERBOSE reports what was removed. No exclusive lock,
-- so reads and writes continue throughout.
VACUUM (VERBOSE, ANALYZE) events;
```

**Bad Example** — disable autovacuum and reach for VACUUM FULL

```sql
-- "Autovacuum causes I/O spikes, let's turn it off and vacuum nightly."
ALTER TABLE events SET (autovacuum_enabled = false);  -- bloat + wraparound risk builds

-- Later, the table is bloated, so someone runs this during business hours:
VACUUM FULL events;
-- ACCESS EXCLUSIVE lock: every SELECT/INSERT/UPDATE on events blocks until it
-- finishes rewriting the whole table. On a large table that is a multi-minute outage.
```

## Common Mistakes

- Turning autovacuum off (globally or per-table) to "reduce load", then hitting bloat or an
  emergency wraparound shutdown.
- Leaving `scale_factor` at the default on huge tables, so vacuum waits for tens of millions
  of dead tuples before running.
- Running `VACUUM FULL` on a live table and taking an unplanned outage from the exclusive
  lock — reach for `pg_repack` instead.
- Ignoring `idle in transaction` sessions and long transactions that freeze the vacuum
  horizon, causing bloat that per-table tuning cannot fix.
- Treating rising `n_dead_tup` as harmless until latency and disk usage force a crisis.
- Assuming `VACUUM` returns disk to the OS — plain `VACUUM` marks space reusable but does not
  shrink the file; only `VACUUM FULL`/`pg_repack` does.

## Production Tips

- Add `autovacuum` timing to monitoring: alert on tables whose `last_autovacuum` is stale
  relative to their write rate, and on wraparound age crossing ~50% of the freeze threshold.
- Schedule `pg_repack` in maintenance windows for chronically bloated tables instead of
  ad-hoc `VACUUM FULL`.
- Log autovacuum activity with `log_autovacuum_min_duration = 0` to see what the daemon is
  actually doing and where it is falling behind.

## AI Review Checklist

- Is autovacuum enabled globally and on every large/high-churn table?
- Are `autovacuum_vacuum_scale_factor`/`analyze_scale_factor` tuned per-table for big tables?
- Is dead-tuple growth and `last_autovacuum` monitored via `pg_stat_user_tables`?
- Is transaction-ID wraparound age monitored well below `autovacuum_freeze_max_age`?
- Are long-running / idle-in-transaction sessions bounded and alerted on?
- Is `VACUUM FULL` avoided on live tables in favor of online `VACUUM` or `pg_repack`?

## Related

- `knowledge/postgresql/21-analyze.md`
- `knowledge/postgresql/06-transactions.md`
- `knowledge/postgresql/16-performance.md`
- `knowledge/postgresql/17-monitoring.md`
- `knowledge/postgresql/27-tuning.md`
