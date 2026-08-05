---
id: mysql/15-monitoring
topic: mysql
slug: monitoring
title: "MySQL Monitoring"
type: doc
order: 15
status: ready
tags: [mysql, monitoring, Seconds_Behind_Source, NOW, sys.statements_with_full_table_scans, performance_schema.events_statements_summary_by_digest, sys.schema_unused_indexes, pt-query-digest]
related: [mysql/14-performance, mysql/05-query-optimization, mysql/09-replication, mysql/20-production]
when_to_use: "Read before shipping a MySQL server to production, setting up alerting, or diagnosing a live performance or availability incident."
---
# MySQL Monitoring

## Purpose

This document defines what to observe on a running MySQL server and how: the
signals that predict trouble, where to read them, and what to alert on. It is
written so an agent can instrument a database that surfaces problems before users
do, and gives an on-call engineer the data to diagnose an incident quickly.

Monitoring is the feedback loop for [performance](14-performance.md) and the
early-warning system for [replication](09-replication.md) and availability. Tuning
without monitoring is guessing; this document makes the guessing unnecessary.

## Why It Matters

A database fails gradually, then suddenly. Replication lag creeps up, the buffer
pool hit rate slips, connections climb, and disk fills — each invisible until the
site is down. By then the useful diagnostic history is gone. Monitoring turns
these silent trends into signals you can alert on and trend lines you can read
during an incident. The cost of not monitoring is measured in outage minutes spent
blind; the cost of monitoring is a metrics exporter and a handful of alert rules.

## Core Principles

- **Instrument before you need it.** The data must already be flowing when an
  incident starts; you cannot retroactively observe a spike that already passed.
- **Alert on symptoms, page on user impact.** Page for things that hurt users
  (replica down, disk full, connections exhausted); ticket for slow-burning trends.
- **Golden signals for a database.** Watch throughput (QPS), latency (slow queries),
  errors (aborted connects, deadlocks), and saturation (connections, buffer pool,
  disk, replication lag).
- **Prefer the performance schema to guesswork.** MySQL exposes precise, low-overhead
  instrumentation; read it rather than sampling `SHOW PROCESSLIST` by eye.
- **Baselines make anomalies visible.** A number is meaningless without its normal
  range; keep history so "500 connections" reads as normal or alarming.

## Best Practices

- Export metrics with a standard exporter (e.g. `mysqld_exporter` to Prometheus) and
  keep dashboards for QPS, latency, connections, buffer pool hit rate, InnoDB row
  operations, and replication lag.
- Enable the slow query log with a low `long_query_time` (e.g. 0.5s) and aggregate it
  with `pt-query-digest` or `performance_schema.events_statements_summary_by_digest`
  to rank queries by total time consumed, not per-call time.
- Alert on replication lag (`Seconds_Behind_Source` or, better,
  `performance_schema.replication_applier_status_by_worker`) — lag means stale reads
  and a failover that loses data.
- Alert on saturation: connection usage approaching `max_connections`, buffer pool hit
  rate dropping, disk free space, and long-running/idle-in-transaction sessions.
- Track errors: aborted connections (`Aborted_connects`), deadlocks
  (`SHOW ENGINE INNODB STATUS`), and lock wait timeouts — rising counts precede outages.
- Use `sys` schema views (`sys.statements_with_full_table_scans`,
  `sys.schema_unused_indexes`, `sys.innodb_lock_waits`) for fast human diagnosis.
- Monitor backups and their restores, not just their success exit code — an unrestorable
  backup is not a backup. See [backups](11-backups.md).

## Examples

**Good Example** — rank real load with the performance schema

```sql
-- Top statements by total latency: this is where server time actually goes.
-- Aggregated by normalized digest, so parameter variants collapse into one row.
SELECT digest_text,
       count_star            AS calls,
       sum_timer_wait/1e12   AS total_seconds,
       (sum_timer_wait/count_star)/1e9 AS avg_ms
FROM performance_schema.events_statements_summary_by_digest
ORDER BY sum_timer_wait DESC       -- total time, not per-call: what to optimize first
LIMIT 10;

-- Applied replication lag per worker (more reliable than Seconds_Behind_Source).
SELECT worker_id,
       TIMEDIFF(NOW(6), last_applied_transaction_original_commit_timestamp) AS lag
FROM performance_schema.replication_applier_status_by_worker;
```

**Bad Example** — eyeballing processlist, no history, no alerts

```sql
-- Runs once, by hand, only after someone reports the site is slow. Shows a single
-- instant with no baseline, no aggregation, and nothing to alert on. The spike that
-- caused the incident is already gone by the time this is typed.
SHOW FULL PROCESSLIST;
```

## Common Mistakes

- No instrumentation until an outage, then no history to diagnose it.
- Alerting on per-call query time, missing a fast query run millions of times.
- Ignoring replication lag until a failover promotes a stale replica.
- Paging on noisy, non-actionable metrics until the team mutes all alerts.
- Trusting a backup's exit code without ever testing a restore.
- Watching CPU only, while the real saturation is buffer pool misses or disk I/O.
- Sampling `SHOW PROCESSLIST` by hand instead of reading the performance schema.

## Production Tips

- Retain metrics long enough to see weekly and seasonal patterns; capacity trends
  need weeks, not hours.
- Wire alerts to on-call with clear severities: page vs ticket, mapped to user impact.
- Add a synthetic canary query per connection path so you detect "can't reach the DB"
  independently of host metrics.
- Record `EXPLAIN` and the digest for the top slow queries in incident runbooks so
  responders start from data, not a cold search.

## AI Review Checklist

- Are QPS, latency, connections, buffer pool hit rate, and replication lag exported
  and dashboarded?
- Is the slow query log enabled and aggregated by digest / total time?
- Do alerts cover saturation (connections, disk, buffer pool) and replication lag?
- Do alerts page on user-impacting failures and ticket on slow trends?
- Is metric history retained long enough to establish baselines?
- Are backups monitored by test restore, not just success status?
- Can an on-call engineer find the top slow queries from the performance schema quickly?

## Related

- `knowledge/mysql/14-performance.md`
- `knowledge/mysql/05-query-optimization.md`
- `knowledge/mysql/09-replication.md`
- `knowledge/mysql/20-production.md`
