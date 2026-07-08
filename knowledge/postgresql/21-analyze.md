---
id: postgresql/21-analyze
topic: postgresql
slug: analyze
title: "Analyze"
type: doc
order: 21
status: ready
tags: [postgresql, analyze]
related: [postgresql/20-vacuum, postgresql/05-query-planner, postgresql/04-indexes, postgresql/16-performance, postgresql/27-tuning]
when_to_use: "Read before diagnosing a query that suddenly picked a bad plan, after a bulk load, or when tuning planner statistics on skewed or correlated columns."
---
# Analyze

## Purpose

This document defines how PostgreSQL collects the column statistics the planner uses to
choose query plans, via `ANALYZE`, autovacuum's analyze pass, and extended statistics. It is
written so an agent can keep statistics accurate, recognize when stale or insufficient stats
cause a bad plan, and fix it without blindly rewriting queries.

`ANALYZE` feeds the [query planner](05-query-planner.md): it estimates how many rows each
step returns, which drives index-vs-scan and join-order decisions. Reclaiming dead tuples is
the separate job of [VACUUM](20-vacuum.md); autovacuum runs both, but for different reasons.

## Why It Matters

The planner is a cost estimator, and its estimates are only as good as its statistics. After
a bulk load, a large delete, or a data-distribution shift, the stored stats describe a table
that no longer exists — so the planner picks a plan for the wrong data. The symptom is
brutal and familiar: a query that ran in milliseconds yesterday now does a sequential scan or
a nested loop over millions of rows, because the planner thinks the table has 1,000 rows when
it has 10 million. These regressions appear "out of nowhere" and are almost always a
statistics problem, not a query problem. Autovacuum keeps stats fresh automatically, but bulk
operations outrun it, and correlated columns defeat its single-column model entirely.

## Core Principles

- **The planner trusts statistics, not reality.** Wrong estimates → wrong plan, even if the
  query and indexes are perfect. Fix the stats before rewriting the SQL.
- **Autovacuum analyzes automatically, but on a threshold.** A bulk load can insert millions
  of rows and query them before the analyze pass fires — run `ANALYZE` explicitly after ETL.
- **`ANALYZE` samples, it does not scan the whole table.** Sample size is
  `default_statistics_target` (default 100). Skewed or high-cardinality columns often need a
  higher target to be estimated well.
- **Single-column stats assume independence.** When columns are correlated (e.g. `city` and
  `country`), the planner multiplies probabilities and massively under-estimates. Extended
  statistics (`CREATE STATISTICS`) fix this.
- **`ANALYZE` is cheap and online.** It takes a light lock and finishes fast; there is rarely
  a reason to avoid running it after a big data change.

## Best Practices

- Run `ANALYZE <table>;` explicitly at the end of any bulk load, restore, or large
  `INSERT`/`UPDATE`/`DELETE` — do not wait for autovacuum to notice.
- Diagnose bad plans with `EXPLAIN (ANALYZE, BUFFERS)` and compare *estimated* vs *actual*
  rows. A large gap points straight at a statistics problem.
- Raise `default_statistics_target` (or per-column via `ALTER TABLE … ALTER COLUMN … SET
  STATISTICS n`) for columns with skewed distributions or many distinct values, then
  re-`ANALYZE`. Higher target = more accurate estimates, at the cost of a bit more planning
  time and analyze time.
- Create extended statistics on correlated column groups used together in `WHERE`/`GROUP BY`:
  `CREATE STATISTICS s (dependencies, ndistinct) ON city, country FROM addresses;`
  then `ANALYZE addresses;`.
- Keep `autovacuum_analyze_scale_factor` low on large, frequently-queried tables so routine
  churn refreshes stats before plans drift.
- After a major version upgrade or `pg_restore`, run a database-wide `ANALYZE` before serving
  traffic — restored data has no statistics at all.

## Examples

**Good Example** — analyze after a load and fix a correlation misestimate

```sql
-- Bulk load leaves stale/absent stats. Analyze so the planner sees the real data.
COPY events FROM '/data/events.csv' CSV;
ANALYZE events;                        -- cheap, online; do this before querying

-- city and country are strongly correlated. Single-column stats under-count matches,
-- so the planner picks a nested loop. Extended stats teach it the dependency.
CREATE STATISTICS addr_geo (dependencies, ndistinct) ON city, country FROM addresses;
ANALYZE addresses;                     -- populate the new statistics object

-- Verify: estimated rows should now be close to actual rows.
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM addresses WHERE city = 'Paris' AND country = 'FR';
```

**Bad Example** — trust the plan after a bulk load and rewrite the query

```sql
-- Load 10M rows, then immediately query. Stats still say the table is tiny.
COPY events FROM '/data/events.csv' CSV;
SELECT count(*) FROM events WHERE tenant_id = 42;   -- planner estimates 1 row → seq scan

-- The query is fine. Instead of running ANALYZE, someone forces an index and adds hints,
-- masking the real issue. The next load reintroduces it. No ANALYZE anywhere.
SELECT /*+ IndexScan(events) */ count(*) FROM events WHERE tenant_id = 42;
```

## Common Mistakes

- Querying immediately after a bulk load or restore without running `ANALYZE`, so the planner
  optimizes for a table that no longer exists.
- Blaming the query or the index for a bad plan when the real cause is a stale/insufficient
  estimate — always check estimated vs actual rows first.
- Leaving `default_statistics_target` at 100 for a highly skewed column and getting poor
  estimates on its rare values.
- Ignoring correlated predicates; without extended statistics the planner under-estimates
  multi-column filters by orders of magnitude.
- Forgetting that a major-version upgrade or restore starts with no statistics at all.
- Confusing `ANALYZE` (statistics) with `VACUUM` (dead-tuple cleanup) and running the wrong one.

## Production Tips

- Bake `ANALYZE` into ETL/migration jobs as an explicit final step, not an afterthought.
- Track plan regressions with `pg_stat_statements` (mean time per query) so a stats-driven
  slowdown is visible before users report it.
- When a critical query's plan is unstable, raise the statistics target on its filter columns
  rather than pinning the plan.

## AI Review Checklist

- Does every bulk load / restore / large DML end with an explicit `ANALYZE`?
- When a plan is bad, was estimated-vs-actual row count checked with `EXPLAIN (ANALYZE)`?
- Is `default_statistics_target` raised for skewed or high-cardinality filter columns?
- Are correlated column groups covered by `CREATE STATISTICS` + `ANALYZE`?
- After a major upgrade or `pg_restore`, is a database-wide `ANALYZE` run before serving?
- Is a bad plan being fixed at the statistics level, not masked by query rewrites/hints?

## Related

- `knowledge/postgresql/20-vacuum.md`
- `knowledge/postgresql/05-query-planner.md`
- `knowledge/postgresql/04-indexes.md`
- `knowledge/postgresql/16-performance.md`
- `knowledge/postgresql/27-tuning.md`
