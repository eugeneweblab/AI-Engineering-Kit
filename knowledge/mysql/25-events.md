---
id: mysql/25-events
topic: mysql
slug: events
title: "MySQL Events"
type: doc
order: 25
status: ready
tags: [mysql, events, NOW, ROW_COUNT, LIMIT, my.cnf]
related: [mysql/27-procedures, mysql/26-triggers, mysql/15-monitoring, mysql/09-replication]
when_to_use: "Read before scheduling recurring work (purges, rollups, refreshes) inside MySQL with the Event Scheduler."
---
# MySQL Events

## Purpose

This document defines when and how to use the MySQL **Event Scheduler** — named,
time-scheduled blocks of SQL that the server runs on an interval or at a timestamp. It
covers enabling the scheduler, writing idempotent event bodies, and the failure modes
that make in-database cron a liability.

Events are MySQL's built-in cron. They are convenient for self-contained maintenance
(purging expired rows, refreshing a summary table) but they are invisible to your
application deployment, hard to observe, and tied to one server. Treat them as a
deliberate trade-off, not a default.

## Why It Matters

An event runs silently inside the database with no application log, no alert on failure,
and no code-review trail unless you build one. When it throws, the row is simply not
purged and no one notices until the table is huge. Events also interact badly with
replication and failover: a `CREATE EVENT` on the primary replicates, but the scheduler
runs events only where it is enabled, so a botched failover can run the same purge twice
or not at all. Because the logic lives in the database rather than in version-controlled
application code, it drifts out of sync with what engineers believe is running.

## Core Principles

- **The scheduler is off until you turn it on.** Nothing runs unless
  `event_scheduler = ON`. Set it in the config file, not just at runtime, or it resets on
  restart.
- **Event bodies must be idempotent and bounded.** An event can run late, twice, or after
  a failover. Re-running it must be safe, and each run must limit its own work.
- **Events do not run on replicas by default.** The scheduler is enabled per server;
  enabling it on a replica double-runs the work. Run events only on the primary.
- **Failures are silent.** MySQL logs an error and moves on. You get zero signal unless
  you record success/failure yourself.
- **Version-control the definition.** An event that exists only in production is
  undocumented infrastructure. Keep the `CREATE EVENT` in migrations.

## Best Practices

- Enable the scheduler in `my.cnf` (`event_scheduler=ON`) so it survives restarts, and
  enable it **only on the primary**; leave it `OFF` on replicas so failover controls it.
- Make every event idempotent: purge by absolute condition (`WHERE expires_at < NOW()`),
  never by "delete the oldest N since last run" that assumes exactly-once execution.
- Bound the work per run with `LIMIT` and let the interval catch up, so a backlog cannot
  produce one giant locking `DELETE`. See [locking](07-locking.md).
- Write results to an audit/log table (rows affected, timestamp, error) so failures are
  observable. See [monitoring](15-monitoring.md).
- Use `ON COMPLETION PRESERVE` for recurring events so a one-shot definition is not
  dropped after firing; drop stale events explicitly.
- Define events through migrations with `CREATE EVENT IF NOT EXISTS`, and keep the
  interval and body in code review — not typed live into production.

## Examples

**Good Example** — bounded, idempotent, observable purge

```sql
SET GLOBAL event_scheduler = ON; -- also set event_scheduler=ON in my.cnf

CREATE EVENT IF NOT EXISTS purge_expired_sessions
  ON SCHEDULE EVERY 5 MINUTE
  ON COMPLETION PRESERVE               -- keep the definition after it fires
  DO
    BEGIN
      -- Absolute condition: safe to run late or twice. LIMIT caps the work so
      -- one run cannot take a huge lock on the table.
      DELETE FROM sessions WHERE expires_at < NOW() LIMIT 5000;
      -- Record the run so a silent failure becomes visible in the log table.
      INSERT INTO maintenance_log (job, rows_affected, ran_at)
        VALUES ('purge_expired_sessions', ROW_COUNT(), NOW());
    END;
```

**Bad Example** — assumes exactly-once, unbounded, invisible

```sql
CREATE EVENT purge_sessions
  ON SCHEDULE EVERY 1 DAY
  DO
    -- Deletes everything in one statement: on a large table this takes a long
    -- lock and can stall the server. No LIMIT, no batching.
    DELETE FROM sessions
    -- "Since yesterday" assumes the event ran exactly once yesterday. After a
    -- missed run or a failover it deletes the wrong window -- silently.
    WHERE created_at < NOW() - INTERVAL 1 DAY;
    -- No log row: if this errors, nobody ever finds out.
```

## Common Mistakes

- Assuming the scheduler is on — it defaults to `OFF`, so the event never fires.
- Setting `event_scheduler=ON` at runtime only, so it reverts to `OFF` on restart.
- Leaving the scheduler enabled on replicas, double-running purges after failover.
- Writing event bodies that assume exactly-once execution instead of idempotence.
- Unbounded `DELETE`/`UPDATE` in an event, taking a huge lock and blocking traffic.
- No logging, so failures are invisible until the table has grown out of control.
- Defining events by hand in production instead of via reviewed migrations.

## Production Tips

- Prefer an external scheduler (application cron, Kubernetes CronJob, Airflow) for
  anything non-trivial: it gives you logs, alerting, retries, and one place to reason
  about failover. Reserve DB events for simple, self-contained data hygiene.
- Query `information_schema.EVENTS` to audit what is actually scheduled and when each last
  ran (`LAST_EXECUTED`).
- Alert if `maintenance_log` shows no successful run within the expected window — absence
  of a run is the failure you will otherwise miss.

## AI Review Checklist

- Is `event_scheduler=ON` set in the config file (not just at runtime), and only on the
  primary?
- Is the event body idempotent and safe to run late or twice?
- Is per-run work bounded (`LIMIT`/batching) so it cannot take a long, blocking lock?
- Does the event record success/failure somewhere observable?
- Is the event defined in a version-controlled migration with `IF NOT EXISTS`?
- Would an external scheduler be a better fit than in-database cron here?

## Related

- `knowledge/mysql/27-procedures.md`
- `knowledge/mysql/26-triggers.md`
- `knowledge/mysql/15-monitoring.md`
- `knowledge/mysql/09-replication.md`
