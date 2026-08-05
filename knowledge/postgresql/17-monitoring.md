---
id: postgresql/17-monitoring
topic: postgresql
slug: monitoring
title: "PostgreSQL Monitoring"
type: doc
order: 17
status: ready
tags: [postgresql, monitoring, pg_stat_activity, pg_stat_statements, pg_stat_replication, wait_event_type, pg_stat_user_tables, autovacuum_freeze_max_age]
related: [postgresql/16-performance, postgresql/12-replication, postgresql/20-vacuum, postgresql/26-production]
when_to_use: "Read before setting up PostgreSQL metrics, alerts, or dashboards, or when diagnosing a live database incident."
---
# PostgreSQL Monitoring

## Purpose

This document defines what to observe in a running PostgreSQL cluster and how to alert on
it: the built-in statistics views, the metrics that predict outages, and the wait events
that explain a live incident. It is written so an agent can instrument a database that
warns *before* it fails and gives a first responder the signal they need during an
incident.

Monitoring is the sensing layer under [performance](16-performance.md),
[replication](12-replication.md), and [high availability](13-high-availability.md). Those
docs tell you what can go wrong; this one tells you how to see it coming.

## Why It Matters

An unmonitored database fails silently until it fails catastrophically: transaction IDs
approach wraparound and the server is minutes from forced shutdown; a replica has been
disconnected for an hour; connections are exhausted and every request errors. Each of
these gives clear, cheap warning signs hours in advance — and PostgreSQL exposes all of
them in system views — but only if something is watching and alerting. Monitoring is what
converts a 3am outage into a business-hours ticket. Because the worst failures are the
predictable ones, the goal is not dashboards to admire but a small set of alerts on
leading indicators that fire early enough to act.

## Core Principles

- **Alert on leading indicators, not just symptoms.** Transaction-ID age, replication lag,
  and connection saturation warn *before* the outage. Alerting only on "database down" is
  alerting too late.
- **The database already knows — read its views.** `pg_stat_activity`, `pg_stat_database`,
  `pg_stat_replication`, `pg_stat_user_tables`, and `pg_stat_statements` expose almost
  everything. Prefer these to guessing from the outside.
- **Wait events explain *why* it is slow.** During an incident, aggregating
  `wait_event_type` in `pg_stat_activity` tells you whether the bottleneck is locks, IO,
  or CPU — which points to entirely different fixes.
- **Every alert must be actionable.** An alert with no clear response is noise that trains
  responders to ignore the page. Tie each alert to a runbook step.
- **Track trends, not just thresholds.** A metric creeping up (bloat, XID age, connection
  count) predicts the incident days out; only historical data reveals the slope.

## Best Practices

- Export metrics with a standard exporter (**postgres_exporter** to Prometheus, or your
  cloud provider's native metrics) rather than scraping views ad hoc, so history is
  retained for trend alerts.
- **Alert on transaction-ID wraparound risk**: watch `age(datfrozenxid)` /
  `age(relfrozenxid)` and page well before `autovacuum_freeze_max_age` (default 200M) —
  wraparound forces a read-only shutdown and is a top-severity, avoidable outage.
- **Alert on replication lag** in bytes and on any standby that disappears from
  `pg_stat_replication` (see [replication](12-replication.md)).
- **Alert on connection saturation**: percent of `max_connections` used, and on rising
  counts of `idle in transaction` sessions, which hold locks and block vacuum.
- Track **cache hit ratio** from `pg_stat_database` and **table/index bloat** trends; a
  falling hit ratio or growing bloat is a slow-burn slowdown (see [vacuum](20-vacuum.md)).
- Enable **`pg_stat_statements`** and surface the top queries by total time so regressions
  are visible before users report them.
- Log slow queries with `log_min_duration_statement`, and centralize logs so an incident
  responder can search them, not SSH to a box.
- Monitor the **checkpoint** picture (`pg_stat_checkpointer` on PostgreSQL 17+, or
  `pg_stat_bgwriter` on older versions) and disk space on the WAL and data volumes.

## Examples

**Good Example** — a leading-indicator query wired to an alert

```sql
-- Transaction-ID age per database. Alert BEFORE wraparound forces a shutdown.
SELECT datname,
       age(datfrozenxid) AS xid_age,
       age(datfrozenxid)::float / 2000000000 AS fraction_to_wraparound
FROM pg_database
ORDER BY xid_age DESC;
-- Page at ~50% (1e9) so autovacuum-to-prevent-wraparound has time; the failure is
-- predictable days ahead, so this alert should never be a surprise.

-- Live-incident triage: what is the database WAITING on right now?
SELECT wait_event_type, wait_event, count(*)
FROM pg_stat_activity
WHERE state = 'active'
GROUP BY 1, 2 ORDER BY 3 DESC;   -- Lock -> contention, IO -> cache miss, tells you the fix class
```

**Bad Example** — a check that only notices total failure

```yaml
# The entire monitoring strategy: is the port open?
- alert: PostgresDown
  expr: up{job="postgres"} == 0     # only fires AFTER the database is already down
  for: 5m
# What this never catches, until it is a full outage:
#  * XID age at 190M -> forced read-only shutdown is imminent
#  * a standby offline for an hour -> failover would lose an hour of data
#  * connections at 100% -> every app request already erroring
# Fix: alert on the leading indicators above, hours before "down".
```

## Common Mistakes

- Only alerting on "database is down", missing every warning that preceded it.
- Not monitoring transaction-ID age, then hitting a forced read-only shutdown from
  wraparound.
- Ignoring replication lag until a failover reveals the standby was hours behind.
- No alert on `idle in transaction`, so a leaked transaction quietly blocks vacuum and
  holds locks.
- Dashboards full of metrics but no alerts, so nobody is actually watching.
- Alerts with no runbook, producing pages that responders learn to dismiss.
- Only threshold alerts and no history, so slow-burn trends (bloat, XID age) are invisible
  until they are urgent.
- Storing logs only on the DB host, so an incident responder cannot search them under
  load.

## Production Tips

- Keep a one-screen "golden signals" dashboard: connections, XID age, replication lag,
  cache hit ratio, slow-query rate, disk free. If it is red, someone acts.
- Snapshot `pg_stat_statements` and reset it on a schedule so you can attribute load to a
  time window rather than all-time totals.
- Practice reading `pg_stat_activity` during a game day so responders know the triage
  query cold before a real incident.
- Alert on **absence** too: if the metrics exporter itself stops reporting, treat that as
  a potential incident, not silence.

## AI Review Checklist

- Are there alerts on transaction-ID age well before wraparound?
- Is replication lag alerted in bytes, and is a missing standby detected?
- Is connection saturation (and `idle in transaction`) alerted?
- Is `pg_stat_statements` enabled and top-by-total-time queries visible?
- Are metrics retained as history so trends (bloat, XID age) are alertable?
- Does every alert map to a concrete runbook action?
- Can a responder search centralized logs and read `pg_stat_activity` wait events during
  an incident?

## Related

- `knowledge/postgresql/16-performance.md`
- `knowledge/postgresql/12-replication.md`
- `knowledge/postgresql/20-vacuum.md`
- `knowledge/postgresql/26-production.md`
