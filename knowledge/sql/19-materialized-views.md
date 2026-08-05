---
id: sql/19-materialized-views
topic: sql
slug: materialized-views
title: "Materialized Views"
type: doc
order: 19
status: ready
tags: [sql, materialized-views, UNIQUE, CONCURRENTLY]
related: [sql/18-views, sql/15-indexes, sql/23-performance, sql/17-query-optimization, sql/14-transactions]
when_to_use: "Read before caching an expensive aggregation or join in the database, or when a plain view is too slow for a read-heavy dashboard or report."
---
# Materialized Views

## Purpose

This document defines when and how to use materialized views: precomputed query
results stored on disk as a physical table that must be explicitly refreshed. It
is written so an agent can trade freshness for speed deliberately, without serving
stale data by accident.

A materialized view stores the *result* of a query. A plain
[view](18-views.md) stores only the query text and recomputes on every read. That
one difference — cached result vs. re-run query — drives every decision here.

## Why It Matters

Some queries are genuinely expensive: a nightly report aggregating millions of
rows, a dashboard rolling up a year of events, a search index built from several
joined tables. Running them on every page load is wasteful and slow. A
materialized view computes the answer once and serves it instantly. The catch is
that the stored answer is a snapshot in time. The moment you materialize a result,
you own a new obligation: keeping it fresh. Forgetting that obligation is how a
"fast dashboard" ends up quietly reporting last week's numbers.

## Core Principles

- **You are trading freshness for speed.** A materialized view is only correct if
  its staleness is acceptable to the consumer. State the tolerable lag explicitly.
- **Refresh is not automatic.** Standard SQL materialized views do not update when
  base tables change. You must schedule or trigger a `REFRESH`; nothing does it
  for you.
- **Refresh has a cost.** A full refresh re-runs the whole query. Schedule it for
  off-peak windows and size it against how often the data actually changes.
- **A materialized view is a real table.** You can and should index it, analyze it,
  and grant on it like any other table.
- **Stale-but-fast beats fresh-but-timed-out — only when the business agrees.**
  Never assume the tolerance; confirm it and encode it in the refresh cadence.

## Best Practices

- Use a materialized view when the query is expensive, read far more often than the
  underlying data changes, and a bounded staleness is acceptable.
- In PostgreSQL, refresh with `REFRESH MATERIALIZED VIEW CONCURRENTLY` so readers
  are not blocked during the rebuild. This requires a `UNIQUE` index on the view.
- Create indexes on the materialized view's filter and join columns; it is queried
  like a table and benefits from indexes exactly like one.
- Schedule refreshes on a fixed cadence (cron, `pg_cron`, an external job) tied to
  the data's change rate, and record `last_refreshed_at` so consumers can display
  or reason about freshness.
- Expose the freshness timestamp to the application so the UI can label data as
  "as of HH:MM" rather than implying it is live.
- For very large views that change incrementally, prefer engine-native incremental
  refresh (e.g. Oracle fast refresh, or a rollup table maintained by triggers /
  batch upserts) over full recomputation.
- Wrap refresh-then-swap logic so a failed refresh leaves the previous good result
  in place rather than an empty or half-built view.

## Examples

**Good Example** — indexed, concurrently refreshable, freshness tracked

```sql
-- Expensive rollup: one row per seller per day. Read on every dashboard load,
-- recomputed once an hour — an hour of staleness is acceptable here.
CREATE MATERIALIZED VIEW daily_sales AS
SELECT
    seller_id,
    order_date::date            AS day,
    count(*)                    AS orders,
    sum(total_cents)            AS revenue_cents,
    now()                       AS refreshed_at
FROM orders
GROUP BY seller_id, order_date::date;

-- Required for CONCURRENTLY, and speeds up point lookups on the view.
CREATE UNIQUE INDEX daily_sales_pk ON daily_sales (seller_id, day);

-- Scheduled hourly: readers keep querying the old snapshot during rebuild.
REFRESH MATERIALIZED VIEW CONCURRENTLY daily_sales;
```

**Bad Example** — created once, never refreshed, no freshness signal

```sql
-- Computed at deploy time and then forgotten. Base data changes constantly;
-- the view silently serves the numbers from the day it was created.
CREATE MATERIALIZED VIEW daily_sales AS
SELECT seller_id, sum(total_cents) AS revenue_cents
FROM orders
GROUP BY seller_id;
-- No index, so CONCURRENTLY is impossible and every refresh locks readers.
-- No refreshed_at column, so nobody can tell the data is stale.
-- No scheduled REFRESH anywhere -> permanently frozen results.
```

## Common Mistakes

- Assuming the view updates itself; it never does without an explicit `REFRESH`.
- Omitting the `UNIQUE` index, which blocks `REFRESH ... CONCURRENTLY` and forces
  reader-blocking full refreshes.
- Refreshing during peak traffic, so the rebuild competes with the queries it was
  meant to speed up.
- Not exposing a freshness timestamp, leaving consumers unable to detect staleness.
- Full-refreshing a giant view when only a small slice changed, instead of an
  incremental rollup.
- Using a materialized view where a plain [view](18-views.md) plus a good index
  would already be fast enough — adding staleness for no benefit.

## Production Tips

- Alert if `now() - refreshed_at` exceeds the agreed staleness budget; a stuck
  refresh job is otherwise invisible.
- Make refresh idempotent and safe to retry; log start/finish and duration so you
  can catch a refresh that is creeping toward the next refresh window.
- Size disk for it: a materialized view is stored data and can rival its base
  tables in size, plus extra during a `CONCURRENTLY` rebuild.

## AI Review Checklist

- Is the staleness introduced by materialization explicitly acceptable to consumers?
- Is there a scheduled/triggered `REFRESH` — not a one-time creation?
- Does the view have a `UNIQUE` index enabling `REFRESH ... CONCURRENTLY`?
- Are filter/join columns on the view indexed for fast reads?
- Is a freshness timestamp stored and surfaced to consumers?
- Is refresh scheduled off-peak and monitored for staleness/failure?
- Would a plain [view](18-views.md) with proper indexes suffice instead?

## Related

- `knowledge/sql/18-views.md`
- `knowledge/sql/15-indexes.md`
- `knowledge/sql/23-performance.md`
- `knowledge/sql/17-query-optimization.md`
- `knowledge/sql/14-transactions.md`
