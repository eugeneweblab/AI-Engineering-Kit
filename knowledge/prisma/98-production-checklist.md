---
id: prisma/98-production-checklist
topic: prisma
slug: production-checklist
title: "Prisma Production Checklist"
type: doc
order: 98
status: ready
tags: [prisma, production-checklist, P2024, P2028, offset, maxWait, connection_limit, P2034]
related: [prisma/25-production, prisma/05-migrations, prisma/15-performance, prisma/26-observability, prisma/21-security]
when_to_use: "Read before deploying a Prisma-backed service to production or promoting a database change."
---
# Prisma Production Checklist

## Purpose

A verifiable, pre-deployment checklist for any service that uses Prisma against a
production database. Every item is a yes/no an agent or reviewer can confirm from the
code, config, or CI pipeline. If an item cannot be confirmed, treat it as failed.

## Why It Matters

Prisma failures in production are almost always operational, not logical: the code
worked in dev with ten rows and one connection, then fell over under real traffic,
real data volume, and real concurrency. Connection pools exhaust, unbounded queries
time out, and an unreviewed migration locks a table or drops a column. This checklist
catches the failures that only appear at scale, before users do.

## Client and Connections

**Rules:** [Client](06-client.md) · [Production](25-production.md)

- [ ] Exactly one `PrismaClient` is instantiated per process, exported from a shared module.
- [ ] In development, the client is cached on `globalThis` so hot-reload does not spawn new pools.
- [ ] `connection_limit` is set explicitly, and total connections across all instances stay under the database max.
- [ ] A connection pooler (PgBouncer, Prisma Accelerate, or Data Proxy) is used for serverless/edge deployments.
- [ ] The client is disconnected on graceful shutdown (`SIGTERM` → `$disconnect()`).

## Schema and Migrations

**Rules:** [Schema](02-schema.md) · [Migrations](05-migrations.md)

- [ ] Migrations are applied with `prisma migrate deploy` in CI/CD, never at app boot.
- [ ] `prisma migrate status` reports no pending or failed migrations against production.
- [ ] `db push` is not used anywhere in the production path.
- [ ] Every migration has been tested against a copy of production-scale data.
- [ ] Destructive changes (drop column, narrow type) use an expand/contract sequence, not a single breaking step.
- [ ] The generated client (`prisma generate`) runs in the build so the deployed client matches the schema.

## Queries and Performance

**Rules:** [Performance](15-performance.md) · [Indexes](16-indexes.md)

- [ ] Every `findMany` on a growing table has a `take` limit and a deterministic `orderBy`.
- [ ] Large lists use cursor-based pagination, not `skip`/`offset` for deep pages.
- [ ] Relations are loaded with `include`/`select`, and no N+1 loops remain in hot paths.
- [ ] Queries `select` only needed columns rather than returning full rows.
- [ ] Every column filtered or sorted in a hot path is backed by a `@@index`, verified with `EXPLAIN`.
- [ ] Long or heavy queries have a statement/query timeout configured.

## Transactions and Consistency

**Rules:** [Transactions](08-transactions.md)

- [ ] Multi-step dependent writes are wrapped in `$transaction`.
- [ ] Interactive transactions have a bounded `timeout` and `maxWait`.
- [ ] Transaction callbacks contain no external I/O (HTTP, queue) that could hold locks open.
- [ ] Isolation level is set explicitly where write-skew or lost-update is possible.

## Security

**Rules:** [Security](21-security.md)

- [ ] No user input is interpolated into `$queryRawUnsafe`; all raw SQL uses tagged templates.
- [ ] The `DATABASE_URL` comes from a secrets manager, not source control.
- [ ] The database user has least-privilege grants (no superuser for the app).
- [ ] Multi-tenant queries always scope by tenant id; no cross-tenant reads are possible.
- [ ] Error responses to clients do not leak SQL, table names, or raw Prisma error text.

## Observability

**Rules:** [Observability](26-observability.md) · [Debugging](20-debugging.md)

- [ ] Slow-query and error logging is enabled (sampled in production, not full query logs).
- [ ] Connection pool saturation and query latency are monitored with alerts.
- [ ] Known error codes (`P2002`, `P2024`, `P2025`, `P2028`) are handled and surfaced in metrics.
- [ ] A dashboard tracks migration status and replication lag if read replicas are used.

## Resilience

**Rules:** [Error Handling](18-error-handling.md) · [Production](25-production.md)

- [ ] Transient failures (deadlock `P2034`, timeout `P2024`) are retried with backoff and a cap.
- [ ] The app degrades gracefully (returns a clear error) when the database is unreachable, not a stack trace.
- [ ] Health checks verify database connectivity, not just process liveness.
- [ ] A tested rollback plan exists for the pending migration.

## AI Review Checklist

- [ ] Every item above is confirmed from code, config, or CI — not assumed.
- [ ] The single-client and bounded-query rules are verified by grep, not by trust.
- [ ] The pending migration is reviewed for locks and reversibility before deploy.
- [ ] Secrets and least-privilege grants are confirmed in the deploy environment.

## Related

- `knowledge/prisma/25-production.md`
- `knowledge/prisma/05-migrations.md`
- `knowledge/prisma/15-performance.md`
- `knowledge/prisma/26-observability.md`
- `knowledge/prisma/21-security.md`
