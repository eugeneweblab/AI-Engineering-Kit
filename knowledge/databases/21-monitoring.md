---
id: databases/21-monitoring
topic: databases
slug: monitoring
title: "Monitoring"
type: doc
order: 21
status: ready
tags: [databases, monitoring]
related: [databases/20-performance, databases/08-query-optimization, databases/22-high-availability, databases/18-backup-and-recovery, databases/14-replication]
when_to_use: "Read before shipping a database to production, setting alerts, or diagnosing an incident where you need to know what the database was doing."
---
# Monitoring

## Purpose

This document defines what to observe about a running database and how to turn those
signals into alerts that fire before users notice. It covers the golden signals, the
metrics that predict outages (connections, replication lag, disk, locks), query-level
visibility, and the difference between a metric worth waking someone for and noise.

You cannot operate what you cannot see. Monitoring is how a database stops being a black
box and becomes a system you can reason about during the three-in-the-morning incident.

## Why It Matters

Database failures are usually slow-motion: disk fills over days, replication lag creeps up
over hours, a connection leak saturates the pool over minutes. Each of these is trivially
survivable if you see it coming and fatal if you do not. Without monitoring, the first
signal you get is a total outage — the worst possible time to start gathering information.
Good monitoring converts a page-at-3am catastrophe into a routine daytime fix, and gives
you the historical baseline that makes "is this slow?" an answerable question instead of a
guess. It is also how you know your [backups](18-backup-and-recovery.md) and
[replicas](14-replication.md) are actually healthy rather than silently broken.

## Core Principles

- **Alert on symptoms users feel, monitor everything else.** Page on high latency, error
  rate, and saturation; keep the deep internal metrics as dashboards for diagnosis, not
  pages. Alerting on every metric trains people to ignore alerts.
- **Watch the leading indicators, not just the outcome.** Disk-free trend, connection
  pool usage, and replication lag predict an outage; downtime reports it after the fact.
- **Every alert must be actionable.** If a human cannot do anything about it, it is a
  dashboard, not a page. Non-actionable pages cause alert fatigue and missed real ones.
- **Establish baselines.** "500 queries/sec" means nothing without knowing normal. Retain
  history so anomalies are visible against a trend.
- **Instrument at the query level.** Aggregate CPU tells you *something* is slow; query
  stats tell you *which statement* to fix. See [performance](20-performance.md).

## Best Practices

- Track the **four golden signals** for the database: latency (query time), traffic
  (QPS/TPS), errors (failed queries, deadlocks), and saturation (CPU, memory, I/O,
  connections). Alert primarily on these.
- Monitor **connections** as a percentage of the server limit; a climbing count is a
  leaking pool and a coming `too many connections` outage.
- Monitor **replication lag** in seconds/bytes and alert when it exceeds your tolerance —
  lag means stale reads and, during failover, data loss. See [replication](14-replication.md).
- Monitor **disk free and growth rate**, and alert on *time-to-full*, not just a static
  threshold — a database that hits 100% disk stops accepting writes.
- Enable **`pg_stat_statements`** (or the engine equivalent) and review top queries by
  total time and by mean time; the two lists surface different problems.
- Watch **cache/buffer hit ratio, lock waits, deadlocks, and long-running transactions** —
  each is an early warning of a performance cliff.
- Verify **backup success and age** and **replica health** as monitored metrics, not
  assumptions; a job that silently stopped is the classic disaster.
- Emit metrics to a **time-series system** (Prometheus, CloudWatch) with dashboards and
  defined SLOs; ad-hoc `SELECT`s during an incident are too late.

## Examples

**Good Example** — actionable, symptom-based, trend-aware alerts

```yaml
# Prometheus rules: page on things users feel or that predict imminent failure.
groups:
  - name: database
    rules:
      - alert: DBConnectionsSaturating
        # Leading indicator: pool nearing the server limit BEFORE it errors.
        expr: pg_stat_activity_count / pg_settings_max_connections > 0.85
        for: 5m
        labels: { severity: page }

      - alert: DBDiskWillFillIn6h
        # Alert on time-to-full (trend), not a static "90%" that gives no lead time.
        expr: predict_linear(node_filesystem_free_bytes[1h], 6*3600) < 0
        for: 15m
        labels: { severity: page }

      - alert: DBReplicationLagHigh
        expr: pg_replication_lag_seconds > 30   # stale reads + failover data-loss risk
        for: 2m
        labels: { severity: page }
```

**Bad Example** — noisy, non-actionable, blind to trends

```yaml
groups:
  - name: database
    rules:
      - alert: DBAnyQuerySlow
        # Fires on a single 501ms query. Pages constantly → everyone mutes the channel →
        # the real outage is missed. Not actionable, not a symptom.
        expr: pg_query_duration_ms > 500
        labels: { severity: page }

      - alert: DBDiskAt90
        # Static threshold with no trend: on a fast-filling disk 90%→100% is minutes away,
        # giving no time to act; on a slow one it pages for weeks of harmless headroom.
        expr: disk_used_percent > 90
        labels: { severity: page }
# Missing entirely: replication lag, connection saturation, backup age, deadlocks.
```

## Common Mistakes

- Alerting on internal metrics no human can act on, causing fatigue that masks real pages.
- Static disk thresholds instead of time-to-full, giving no lead time on a fast-filling disk.
- Not monitoring connection count, so a pool leak becomes a surprise `too many connections`.
- Ignoring replication lag until a failover silently loses the un-replicated writes.
- No query-level stats, so you know the DB is slow but not which statement to fix.
- Assuming backups and replicas are healthy instead of monitoring their status and age.
- No retained history, so there is no baseline to judge "is this normal?" during an incident.

## Production Tips

- Route pages by **severity and ownership**; a page should reach someone who can act now.
- Build a **first-response dashboard** (golden signals + top queries + lag + disk) that
  answers "what is the database doing?" in one screen during an incident.
- Correlate database metrics with application metrics on the same timeline — the cause and
  the symptom often live in different services.
- Review alert precision monthly: any alert that mostly fires without action gets fixed or
  deleted.

## AI Review Checklist

- Are the four golden signals (latency, traffic, errors, saturation) monitored and alerted?
- Do alerts fire on user-facing symptoms and predictive leading indicators, not raw internals?
- Is every alert actionable, and is disk alerted on time-to-full rather than a fixed percent?
- Are connections, replication lag, deadlocks, and long transactions all tracked?
- Are query-level statistics (`pg_stat_statements` or equivalent) enabled and reviewed?
- Are backup success/age and replica health monitored, not assumed?
- Is metric history retained so baselines and anomalies are visible?

## Related

- `knowledge/databases/20-performance.md`
- `knowledge/databases/08-query-optimization.md`
- `knowledge/databases/22-high-availability.md`
- `knowledge/databases/18-backup-and-recovery.md`
- `knowledge/databases/14-replication.md`
