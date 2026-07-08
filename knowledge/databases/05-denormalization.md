---
id: databases/05-denormalization
topic: databases
slug: denormalization
title: "Denormalization"
type: doc
order: 5
status: ready
tags: [databases, denormalization]
related: [databases/04-normalization, databases/03-data-modeling, databases/07-indexing, databases/08-query-optimization, databases/23-data-integrity]
when_to_use: "Read when a measured read hotspot needs speeding up and you are considering trading redundancy for query performance."
---
# Denormalization

## Purpose

This document defines denormalization: deliberately introducing controlled
redundancy into a [normalized](04-normalization.md) schema to make specific reads
faster. It covers when the trade is worth making, how to keep the redundant data
correct, and the traps to avoid. Denormalization is a performance optimization, not
a design starting point — it is normalization spent on purpose, with eyes open.

The governing rule: **normalize by default; denormalize only a proven hotspot, and
own the consistency cost you just took on.**

## Why It Matters

Reads and writes pull in opposite directions. A fully normalized schema makes writes
safe (one fact, one place) but can make hot reads expensive (many joins, repeated
aggregation). Denormalization buys read speed by storing a copy or a precomputed
value — but every copy is now a fact that can go stale, and the responsibility for
keeping it correct shifts from the database engine to you. Done blindly, it
reintroduces exactly the anomalies normalization removed. Done deliberately and
measured, it turns an unacceptable query into a fast one. The difference is whether
you paid the consistency cost knowingly.

## Core Principles

- **Normalize first; denormalize as a targeted fix.** You cannot know the hotspot
  before you have one. Start correct, measure, then optimize the specific query that
  is too slow.
- **Every denormalized value needs an owner and a mechanism.** Redundant data must be
  kept in sync by something explicit — a trigger, a transaction that writes both
  places, a materialized view, or a scheduled rebuild. Never "the app will remember."
- **Keep the source of truth normalized.** The denormalized copy is a cache derived
  from authoritative data. If they disagree, the normalized source wins and the copy
  is rebuildable from it.
- **Prefer reversible, rebuildable forms.** A materialized view or cache can be
  regenerated from the source. A value hand-copied into rows cannot easily be
  audited or repaired.
- **Denormalization is a write cost.** You are moving work from read time to write
  time (and adding a staleness risk). Confirm the workload is read-heavy enough to
  justify it.

## Best Practices

- Reach for cheaper options first: an [index](07-indexing.md), a better query, or a
  covering index often removes the need to denormalize at all.
- For expensive aggregates read far more often than they change, use a **materialized
  view** with a defined refresh strategy — the engine owns correctness and rebuilds.
- When storing a rollup (order total, comment count) on a parent row, update it in
  the **same transaction** as the child change, or via a trigger, so it can never
  drift within a committed state.
- Document every denormalization at the schema: what it duplicates, why, and how it
  stays correct. Undocumented redundancy is indistinguishable from a bug.
- Add a reconciliation check (a periodic job that recomputes and compares) for any
  denormalized value that matters, so drift is detected, not discovered by a customer.
- Accept eventual consistency explicitly where you use async refresh, and make sure
  the product tolerates the staleness window (see [Eventual Consistency](13-eventual-consistency.md)).

## Examples

**Good Example** — rollup kept correct inside the write transaction

```sql
-- Denormalized comment_count on post, justified: read on every feed render,
-- written only when a comment is added. Kept correct atomically.
BEGIN;
  INSERT INTO comment (post_id, body) VALUES ($1, $2);
  UPDATE post
     SET comment_count = comment_count + 1   -- same transaction: count can never
   WHERE id = $1;                            -- diverge from the committed comments
COMMIT;
-- The source of truth is still the comment table; comment_count is a rebuildable cache:
--   UPDATE post p SET comment_count =
--     (SELECT count(*) FROM comment c WHERE c.post_id = p.id);
```

**Bad Example** — copied data with no mechanism to keep it correct

```sql
-- Product price copied onto each order line "to avoid a join", updated nowhere.
CREATE TABLE order_line (
  id         BIGINT PRIMARY KEY,
  product_id BIGINT REFERENCES product(id),
  price      NUMERIC   -- copy of product.price at write time, but treated as live
);

-- Later, price is changed only in one place, and the two silently disagree:
UPDATE product SET price = 12.00 WHERE id = 42;
-- order_line.price for product 42 still says 9.00. Which is correct? Nobody knows.
-- No owner, no refresh, no reconciliation → a permanent, invisible inconsistency.
```

Note: capturing the price *as of the sale* is a legitimate, different design — but
then it is a historical fact, named `price_at_purchase`, and must never be "kept in
sync" with the current price. The bug above is treating a snapshot as a live copy.

## Common Mistakes

- Denormalizing before measuring, optimizing a query that was never slow and taking
  on consistency risk for nothing.
- Introducing a redundant column with no trigger, transaction, or job to maintain it,
  guaranteeing eventual drift.
- Updating the source but forgetting the copy (or vice versa), because two writers
  must now agree by convention instead of by constraint.
- Confusing a point-in-time snapshot (a legitimate historical fact) with a live copy
  that must track its source — they look identical but have opposite maintenance rules.
- Denormalizing a write-heavy workload, so every write now updates several places and
  contends on the same rows.
- Leaving denormalization undocumented, so the next engineer "fixes" the redundancy
  and breaks the read path, or trusts the stale copy.

## Production Tips

- Schedule a reconciliation job for critical denormalized values and alert on any
  mismatch; treat a mismatch as a defect, not noise.
- For materialized views, monitor refresh duration and lag; a view that takes longer
  to refresh than its refresh interval is silently always stale.
- When removing a denormalization, keep it until the replacement (index, query) is
  proven faster in production — do not swap on assumption.

## AI Review Checklist

- Was this denormalization driven by a measured, real read hotspot?
- Was a cheaper fix (index, query rewrite, covering index) ruled out first?
- Does every redundant value have an explicit owner and sync mechanism (trigger,
  same-transaction write, materialized view, or job)?
- Is the normalized source still authoritative and the copy rebuildable from it?
- Is there a reconciliation check to detect drift on values that matter?
- Is a point-in-time snapshot clearly distinguished from a live copy, and named so?
- Is the redundancy documented at the schema with its justification?

## Related

- `knowledge/databases/04-normalization.md`
- `knowledge/databases/03-data-modeling.md`
- `knowledge/databases/07-indexing.md`
- `knowledge/databases/08-query-optimization.md`
- `knowledge/databases/23-data-integrity.md`
