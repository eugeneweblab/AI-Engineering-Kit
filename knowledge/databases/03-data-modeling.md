---
id: databases/03-data-modeling
topic: databases
slug: data-modeling
title: "Data Modeling"
type: doc
order: 3
status: ready
tags: [databases, data-modeling, author, CHECK]
related: [databases/04-normalization, databases/05-denormalization, databases/06-schema-design, databases/01-database-fundamentals, databases/23-data-integrity]
when_to_use: "Read before designing the tables and relationships for a new feature or service, before writing any DDL."
---
# Data Modeling

## Purpose

This document defines how to turn a domain into a database model: identifying
entities, their attributes, the relationships between them, and the keys that tie
them together. It is the step that comes before [Normalization](04-normalization.md)
(refining the model) and [Schema Design](06-schema-design.md) (expressing it in DDL).

A data model is a set of decisions about what facts the system records and how they
connect. Made well, it makes correct code easy and incorrect code hard to write.
Made poorly, it forces every feature afterward to work around it.

## Why It Matters

The model is the most durable and most shared artifact in the system. Screens change
weekly; the tables behind them last for years and are read by every service, job,
and report. A modeling mistake — the wrong cardinality, a missing entity, an
attribute in the wrong place — cannot be hidden behind an abstraction. It surfaces as
awkward queries, duplicated data that drifts out of sync, and migrations over live
data. Time spent modeling before writing DDL is the highest-leverage time in the
whole build.

## Core Principles

- **Model the domain, then the queries.** First capture the real entities and rules
  ("a customer places many orders; an order has many line items"). Then confirm the
  model answers every query the application must run.
- **One entity, one table; one fact, one place.** Each concept becomes its own
  table. Each fact is stored once, so it can only ever have one value.
- **Relationships are foreign keys.** A relationship between entities is expressed by
  a foreign key, with cardinality (one-to-many, many-to-many) made explicit.
- **A many-to-many relationship is a table.** Join two entities that relate M:N
  through an explicit junction table — never a comma-separated list in a column.
- **Keys are chosen, not accidental.** Every entity has a primary key you selected
  deliberately, and every reference to it goes through a foreign key.

## Best Practices

- Name tables for the entity (singular or plural, but consistently) and columns for
  the fact they hold. `order.placed_at`, not `order.date2`.
- Prefer surrogate primary keys (identity/UUID) for entities whose natural
  identifier could change (people, products). A key must be immutable.
- Model optional relationships with a nullable foreign key or a separate table — not
  with a magic sentinel value like `customer_id = 0`.
- Give status/state fields a small, explicit set of values enforced by an `enum` or
  `CHECK` constraint, so illegal states are unrepresentable.
- Represent a value that recurs and has its own attributes (an address, a currency,
  a category) as its own table, referenced by foreign key, so it is defined once.
- Validate the model against the top ten queries and top five writes the app will
  perform. If a common query needs a five-table gymnastics join, revisit the model.

## Examples

**Good Example** — entities, a junction table, explicit keys and cardinality

```sql
CREATE TABLE author (
  id   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE book (
  id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  title        TEXT NOT NULL,
  published_on DATE
);

-- Many-to-many (a book has many authors, an author writes many books)
-- is its own table. This lets a co-authored book exist without duplicating rows.
CREATE TABLE book_author (
  book_id   BIGINT NOT NULL REFERENCES book(id)   ON DELETE CASCADE,
  author_id BIGINT NOT NULL REFERENCES author(id) ON DELETE RESTRICT,
  PRIMARY KEY (book_id, author_id)   -- composite key: each pair appears once
);
```

**Bad Example** — relationships crammed into columns

```sql
CREATE TABLE book (
  id          BIGINT PRIMARY KEY,
  title       TEXT,
  authors     TEXT,   -- "Ada Lovelace, Alan Turing" — cannot query, join, or dedupe by author
  author_ids  TEXT,   -- "1,2" — a foreign key relationship pretending to be a string
  status      TEXT    -- free text: "pub", "Published", "done" all coexist and mean the same
);
-- Finding every book by author 2 now requires string matching.
-- Renaming an author must edit every book row. Referential integrity is impossible.
```

## Common Mistakes

- Storing a list of related IDs (or names) in a single column instead of a junction
  table, making joins and integrity impossible.
- Modeling a many-to-many relationship as two nullable foreign keys, silently losing
  the ability to record more than one relationship.
- Using natural keys that change (email, username) as primary keys, forcing cascading
  updates when they do.
- Sentinel values (`0`, `-1`, `"N/A"`) standing in for "no relationship," which every
  query must remember to exclude.
- Free-text status fields that accumulate synonyms and typos, defeating filtering.
- Modeling for the current screen instead of the domain, so the next feature needs a
  migration the model should have anticipated.

## Production Tips

- Draw the model (an ER diagram) and check cardinality with a domain expert before
  writing DDL. Cardinality errors are the costliest to fix later.
- Keep a source-of-truth model in migrations; generate ER diagrams from the live
  schema so documentation cannot drift from reality.

## AI Review Checklist

- Does each entity have its own table and a deliberately chosen, immutable primary key?
- Is every relationship a foreign key with explicit cardinality?
- Are many-to-many relationships expressed as junction tables, not delimited columns?
- Are status/type fields constrained to an explicit set of legal values?
- Are optional relationships modeled with nullability or a separate table, not sentinels?
- Does the model answer the application's real queries without contorted joins?

## Related

- `knowledge/databases/04-normalization.md`
- `knowledge/databases/05-denormalization.md`
- `knowledge/databases/06-schema-design.md`
- `knowledge/databases/01-database-fundamentals.md`
- `knowledge/databases/23-data-integrity.md`
