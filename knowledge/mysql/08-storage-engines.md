---
id: mysql/08-storage-engines
topic: mysql
slug: storage-engines
title: "Storage Engines"
type: doc
order: 8
status: ready
tags: [mysql, storage-engines, MyISAM, MEMORY, CURRENT_TIMESTAMP, AUTO_INCREMENT, InnoDB, DATETIME, engine, legacy, migrating]
related: [mysql/06-transactions, mysql/07-locking, mysql/04-indexes, mysql/09-replication]
when_to_use: "Read before creating a table, migrating a legacy MyISAM table, or choosing an engine for a workload."
---
# Storage Engines

## Purpose

This document defines how to choose and configure a MySQL storage engine. The engine
decides whether a table is transactional, how it locks, how it stores rows on disk, and
how it survives a crash. It is written so an agent picks the right engine — almost always
**InnoDB** — and does not inherit a broken legacy default.

The storage engine is a per-table property, so a single database can mix engines. But the
choice has consequences that ripple into [transactions](06-transactions.md),
[locking](07-locking.md), and [replication](09-replication.md). Get it wrong and features
you assume are present silently do nothing.

## Why It Matters

The engine determines whether your data is safe. Choose `MyISAM` and your `BEGIN`/`COMMIT`
are ignored, a crash mid-write corrupts the table, and one writer locks the whole table.
Choose `MEMORY` and everything vanishes on restart. These are not tuning knobs — they are
correctness guarantees. The trap is that MyISAM tables still exist in old schemas and
tutorials, and MySQL will happily let you create one; the table works in testing and
loses data in production. Picking InnoDB deliberately is the single highest-leverage
schema decision.

## Core Principles

- **Use InnoDB unless you have a proven, specific reason not to.** It is the default since
  MySQL 5.5, is ACID-compliant, crash-safe, row-locking, and supports foreign keys.
- **Only InnoDB is transactional.** Transactions, `FOR UPDATE`, foreign keys, and
  savepoints are engine features — non-InnoDB tables ignore or reject them.
- **Crash safety comes from the redo log.** InnoDB's write-ahead log lets it recover to a
  consistent state after a crash; MyISAM has no such guarantee and needs `REPAIR TABLE`.
- **Locking granularity is an engine property.** InnoDB locks rows; MyISAM locks the whole
  table on every write — a throughput ceiling under concurrency.
- **The engine is not a runtime switch.** Changing it rewrites the entire table (`ALTER
  TABLE ... ENGINE=InnoDB`), which locks and copies data; plan it as a migration.

## Best Practices

- Create every table with InnoDB (the default). Set `default_storage_engine=InnoDB`
  explicitly in config so nothing can create a MyISAM table by accident.
- Migrate legacy MyISAM tables to InnoDB to gain transactions, row locking, and crash
  safety; do it with a low-lock tool (`gh-ost`, `pt-online-schema-change`) on large tables.
- Give every InnoDB table an explicit, monotonic **primary key** (usually a `BIGINT`
  auto-increment or a sortable UUIDv7). InnoDB clusters the table on the PK; a poor PK
  hurts every read and write.
- Reach for `MEMORY` only for genuinely ephemeral scratch data you can afford to lose on
  restart, and never for anything a user depends on.
- Do not use `MyISAM` for full-text search anymore — InnoDB has supported `FULLTEXT`
  indexes since 5.6; there is no remaining functional reason to choose MyISAM.
- Keep `innodb_file_per_table=ON` (the default) so each table has its own tablespace file,
  making per-table backup, reclaim, and `OPTIMIZE TABLE` possible.
- Verify engine choices in review: `SELECT table_name, engine FROM
  information_schema.tables WHERE table_schema = DATABASE()`.

## Examples

**Good Example** — explicit InnoDB with a clustered primary key

```sql
-- InnoDB gives ACID transactions, row-level locking, crash recovery, and FKs.
-- The BIGINT auto-increment PK clusters rows in insert order for fast range scans.
CREATE TABLE orders (
  id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  customer_id BIGINT UNSIGNED NOT NULL,
  total_cents INT NOT NULL,
  created_at  DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  KEY idx_customer (customer_id),
  CONSTRAINT fk_customer FOREIGN KEY (customer_id) REFERENCES customers(id)
) ENGINE=InnoDB;
```

**Bad Example** — MyISAM: no transactions, no crash safety, table locks

```sql
-- MyISAM ignores transactions, so a crash between two writes corrupts state and
-- needs REPAIR TABLE. Every INSERT/UPDATE takes a full table lock, serializing
-- writers. Foreign keys are silently dropped. Never choose this for real data.
CREATE TABLE orders (
  id          INT NOT NULL AUTO_INCREMENT,
  customer_id INT NOT NULL,
  total_cents INT NOT NULL,
  PRIMARY KEY (id)
) ENGINE=MyISAM;
```

## Common Mistakes

- Copying a `CREATE TABLE` from an old schema or tutorial that specifies `ENGINE=MyISAM`.
- Assuming transactions work on a table without checking its engine — they silently no-op
  on MyISAM.
- Using `MEMORY` tables for session or cache data and losing everything on the next restart.
- Omitting a primary key on an InnoDB table; InnoDB then generates a hidden 6-byte clustered
  key you cannot use, and secondary indexes and replication both suffer.
- Running `ALTER TABLE ... ENGINE=InnoDB` on a huge table during peak hours, blocking writes
  while the whole table is rebuilt.
- Disabling `innodb_file_per_table`, dumping everything into the shared system tablespace,
  which can never shrink.

## Production Tips

- Size `innodb_buffer_pool_size` to hold the working set — typically 50–75% of RAM on a
  dedicated database host. This is the single most important InnoDB tuning parameter.
- After migrating off MyISAM, audit for remaining `MyISAM`/`MEMORY` tables in
  `information_schema.tables` and add a CI check that fails on new non-InnoDB tables.
- The MySQL system tables (in the `mysql` schema) use InnoDB in modern versions; do not
  "optimize" them by changing engines.

## AI Review Checklist

- Is every application table `ENGINE=InnoDB` (verified via `information_schema.tables`)?
- Is `default_storage_engine=InnoDB` set so accidental MyISAM tables cannot be created?
- Does every InnoDB table have an explicit, sortable primary key?
- Are transactional guarantees only relied upon on InnoDB tables?
- Is `innodb_file_per_table` enabled for per-table space management and backup?
- If a MyISAM/MEMORY table exists, is there a documented, justified reason?

## Related

- `knowledge/mysql/06-transactions.md`
- `knowledge/mysql/07-locking.md`
- `knowledge/mysql/04-indexes.md`
- `knowledge/mysql/09-replication.md`
