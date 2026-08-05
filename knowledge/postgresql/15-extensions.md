---
id: postgresql/15-extensions
topic: postgresql
slug: extensions
title: "PostgreSQL Extensions"
type: doc
order: 15
status: ready
tags: [postgresql, extensions]
related: [postgresql/04-indexes, postgresql/17-monitoring, postgresql/22-migrations, postgresql/18-security]
when_to_use: "Read before installing, upgrading, or reviewing a PostgreSQL extension such as pgvector, PostGIS, or pg_stat_statements."
---
# PostgreSQL Extensions

## Purpose

This document defines how to add functionality to PostgreSQL through extensions — packaged
bundles of C code, SQL objects, and types (pg_stat_statements, PostGIS, pgvector, and
others). It is written so an agent can choose, install, upgrade, and review an extension
without creating a security hole, a version trap, or an unremovable dependency.

Extensions are how you extend the database in-place instead of building the same logic in
the application. Used well they replace fragile app-side code with battle-tested native
features. Used carelessly they pin you to a version, widen the attack surface, or block a
major upgrade.

## Why It Matters

An extension runs *inside* the database process, often as compiled C with full backend
privileges. That is exactly why it is powerful and exactly why it is risky: a poorly
chosen or unmaintained extension can crash the backend, embed a security hole below the
SQL permission layer, or refuse to build against the next major PostgreSQL version — and
you cannot upgrade the cluster until every extension supports the target version. The
choice to adopt an extension is a long-lived operational commitment, so it is made
deliberately, from trusted sources, with an upgrade and removal path known in advance.

## Core Principles

- **`CREATE EXTENSION`, never manual SQL.** Extensions are managed objects. Installing
  their SQL by hand breaks version tracking, dump/restore, and clean upgrades. Use the
  extension mechanism so `pg_dump` records a single `CREATE EXTENSION`.
- **Provenance matters — it runs with backend privileges.** Prefer core `contrib`
  extensions and well-maintained, widely-used projects. A random extension is arbitrary C
  code inside your database.
- **Every extension is a major-upgrade constraint.** You cannot move to a new PostgreSQL
  major version until each installed extension has a build for it. Fewer, well-supported
  extensions upgrade more easily.
- **Version the extension in migrations.** Its version is part of your schema. Install and
  `ALTER EXTENSION ... UPDATE` through migrations, not ad-hoc in production shells.
- **Install into a schema you control, not blindly into `public`.** Placing extension
  objects in a dedicated schema keeps `public` clean and makes `search_path` and
  permissions auditable.

## Best Practices

- Check availability before use with `SELECT * FROM pg_available_extensions` and pin the
  version explicitly: `CREATE EXTENSION vector WITH VERSION '0.8.0'`.
- Enable **pg_stat_statements** on every production database — it is the single most
  useful extension for [performance](16-performance.md) and [monitoring](17-monitoring.md),
  and it is core contrib.
- Restrict who can install extensions; `CREATE EXTENSION` for untrusted extensions requires
  superuser. Do not hand out superuser to app roles just to install one.
- Keep extensions **updated in lockstep with migrations** using `ALTER EXTENSION ... UPDATE`;
  a mismatched extension version across environments causes "works here, breaks there" bugs.
- Before a major PostgreSQL upgrade, **inventory every extension** (`\dx`) and confirm each
  has a build for the target version — this is a common upgrade blocker.
- On managed platforms (RDS, Cloud SQL, etc.), use only the provider's allow-listed
  extensions; unlisted ones cannot be installed and will fail in production only.
- For a vector/search or geospatial workload, use the purpose-built extension (**pgvector**,
  **PostGIS**) rather than emulating it in application code — native indexes (HNSW, GiST)
  are far faster and correct.

## Examples

**Good Example** — declarative install, pinned, in a migration

```sql
-- migration 0042_enable_pgvector.sql
-- Idempotent, version-pinned, tracked as a managed object -> dump/restore reproduces it.
CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA extensions VERSION '0.8.0';

CREATE TABLE doc_embedding (
  id       bigint PRIMARY KEY,
  embedding vector(1536) NOT NULL
);
-- Use the extension's native index; do not do nearest-neighbor in the app.
CREATE INDEX ON doc_embedding USING hnsw (embedding vector_cosine_ops);
```

**Bad Example** — hand-installed, unpinned, unmanaged

```sql
-- Someone pasted the extension's SQL definitions straight into the DB.
CREATE FUNCTION cosine_distance(...) ...;   -- BAD: not tracked as an extension
CREATE OPERATOR <=> (...) ...;              -- pg_dump won't emit CREATE EXTENSION
-- Consequences:
--  * A dump/restore silently loses these objects -> restore produces a broken schema.
--  * No ALTER EXTENSION UPDATE path; upgrading means re-pasting SQL by hand.
--  * No version recorded, so staging and prod drift apart undetectably.
-- Fix: CREATE EXTENSION vector; and let the extension own its objects.
```

## Common Mistakes

- Installing an extension's SQL manually instead of `CREATE EXTENSION`, breaking
  dump/restore and upgrades.
- Adopting an unmaintained third-party extension that then blocks the next major-version
  upgrade.
- Not pinning the extension version, so environments drift and behavior differs.
- Dumping every extension object into `public`, polluting the namespace and complicating
  permissions.
- Trusting an extension from an unknown source — it runs as native code with backend
  privileges.
- Forgetting that the app role needs `USAGE` on the extension's schema and objects, so it
  works for the installer but fails for the app.
- Reimplementing vector search or geospatial math in application code when pgvector/PostGIS
  do it natively and faster.

## Production Tips

- Keep a checked-in inventory (`\dx` output) of installed extensions and versions per
  environment; diff it in CI so prod cannot drift from staging.
- When trialing an extension, do it in a disposable environment first — some extensions
  cannot be cleanly `DROP EXTENSION`-ed once dependent objects exist.
- Before scheduling a major upgrade, resolve extension compatibility first; it is usually
  the long pole, not the core upgrade itself.

## AI Review Checklist

- Is the extension enabled via `CREATE EXTENSION` (not hand-installed SQL)?
- Is its version pinned and installed/updated through a migration?
- Does the extension come from a trusted, maintained source (core contrib preferred)?
- Is `pg_stat_statements` enabled for performance visibility?
- Are extension objects in a controlled schema with correct `USAGE`/permissions for the
  app role?
- Has each installed extension been checked for compatibility with the next major version?
- On a managed platform, is every extension on the provider's allow-list?

## Related

- `knowledge/postgresql/04-indexes.md`
- `knowledge/postgresql/17-monitoring.md`
- `knowledge/postgresql/22-migrations.md`
- `knowledge/postgresql/18-security.md`
