---
id: databases/04-normalization
topic: databases
slug: normalization
title: "Normalization"
type: doc
order: 4
status: ready
tags: [databases, normalization, city, customer, total]
related: [databases/05-denormalization, databases/03-data-modeling, databases/06-schema-design, databases/23-data-integrity, databases/01-database-fundamentals]
when_to_use: "Read while designing a transactional (write-heavy) schema, to eliminate redundancy that would otherwise let data drift out of sync."
---
# Normalization

## Purpose

This document defines normalization: organizing a relational schema so that each
fact is stored in exactly one place, eliminating the redundancy that causes update,
insert, and delete anomalies. It is the discipline that turns a working
[data model](03-data-modeling.md) into a correct one, and it is the default for any
schema that takes writes. Its counterpart is [Denormalization](05-denormalization.md),
a deliberate, measured reversal for read performance.

The practical goal, through third normal form (3NF), is simple to state:
**every non-key column depends on the key, the whole key, and nothing but the key.**

## Why It Matters

Redundant data is data that can disagree with itself. If a customer's address is
copied onto every order, updating the address means updating N rows; miss one and the
database now holds two "true" addresses with no way to know which is right. These are
called anomalies, and they are silent — the schema keeps accepting writes while the
data quietly rots. Normalization removes the redundancy so the contradiction cannot
arise in the first place. It is prevention built into the structure, not a check you
have to remember to run.

## Core Principles

- **First Normal Form (1NF): atomic values.** Each column holds one indivisible
  value; no arrays, no comma-separated lists, no repeating groups of columns
  (`phone1`, `phone2`, `phone3`). Repeating data becomes rows in another table.
- **Second Normal Form (2NF): full dependency on the key.** No non-key column
  depends on only part of a composite key. Attributes of one part move to their own
  table.
- **Third Normal Form (3NF): no transitive dependency.** No non-key column depends on
  another non-key column. If `zip` determines `city`, `city` does not belong in a
  table keyed by order.
- **One fact, one place.** Each piece of information is stored once. Everything else
  references it by foreign key.
- **3NF is the default target.** It removes the anomalies that matter for most
  systems. Higher forms (BCNF, 4NF) are occasionally needed; going below 3NF is a
  deliberate denormalization decision, not an accident.

## Best Practices

- Split any column that holds a list into its own table with one row per value.
- Move any group of attributes that describes a different entity (customer details on
  an order row) into that entity's table, referenced by foreign key.
- Store derived or dependent values (`city` from `zip`, `total` from line items) once
  at their source, or compute them — do not copy them onto dependent rows.
- Add foreign keys and `UNIQUE`/`CHECK` constraints as you normalize; the split only
  pays off if referential integrity is enforced.
- Normalize first, then measure. Only denormalize a proven read hotspot, and document
  why (see [Denormalization](05-denormalization.md)).

## Examples

**Good Example** — normalized to 3NF, each fact stored once

```sql
CREATE TABLE customer (
  id      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name    TEXT NOT NULL,
  email   TEXT NOT NULL UNIQUE,
  city    TEXT NOT NULL        -- the customer's city lives with the customer, once
);

CREATE TABLE "order" (
  id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  customer_id BIGINT NOT NULL REFERENCES customer(id),  -- reference, do not copy
  placed_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- Updating a customer's city touches exactly one row. No order can disagree with it.
```

**Bad Example** — customer facts duplicated onto every order

```sql
CREATE TABLE "order" (
  id             BIGINT PRIMARY KEY,
  placed_at      TIMESTAMPTZ,
  customer_name  TEXT,   -- copied per order → update anomaly: change name = rewrite N rows
  customer_email TEXT,   -- two orders can now hold two different emails for one customer
  customer_city  TEXT,   -- transitive dependency on the customer, not the order
  item_names     TEXT    -- "Pen, Pad" → violates 1NF, cannot join to a products table
);
-- A new customer with no orders yet cannot be recorded at all (insert anomaly).
-- Deleting a customer's last order erases the customer entirely (delete anomaly).
```

## Common Mistakes

- Leaving list-valued columns (`tags`, `roles` as CSV) in place, violating 1NF and
  making the values unqueryable and un-joinable.
- Repeating groups of columns (`item1`, `item2`, `item3`) instead of a child table.
- Copying attributes of a related entity onto a row "to avoid a join," creating the
  exact update anomaly normalization exists to prevent.
- Storing a computed total or count on a parent row and letting it drift from the
  children it summarizes, without a mechanism to keep it correct.
- Confusing normalization with slowness and denormalizing preemptively, before any
  measurement shows a read problem.

## Production Tips

- Anomalies you can grep for: the same string value appearing in many rows that
  should reference one row, and columns whose name embeds another entity
  (`customer_*` on an `order` table). Both are normalization smells.
- When you must keep a derived value for speed, enforce it with a trigger,
  materialized view, or transactional update — never trust it to be maintained by
  every writer by hand.

## AI Review Checklist

- Are all columns atomic (no CSV lists, arrays-as-strings, or repeating groups)? (1NF)
- Does every non-key column depend on the whole primary key? (2NF)
- Are there transitive dependencies where one non-key column determines another? (3NF)
- Is each fact stored exactly once, referenced elsewhere by foreign key?
- Are derived/duplicated values either removed or kept correct by an enforced mechanism?
- Was any denormalization deliberate and documented, not accidental?

## Related

- `knowledge/databases/05-denormalization.md`
- `knowledge/databases/03-data-modeling.md`
- `knowledge/databases/06-schema-design.md`
- `knowledge/databases/23-data-integrity.md`
- `knowledge/databases/01-database-fundamentals.md`
