---
id: backend/26-deployment
topic: backend
slug: deployment
title: "Deployment"
type: doc
order: 26
status: ready
tags: [backend, deployment]
related: [backend/27-production, backend/22-observability, backend/17-transactions, backend/98-production-checklist]
when_to_use: "Read before setting up a release pipeline, a database migration, or a rollback strategy for a backend service."
---
# Deployment

## Purpose

This document defines how to move backend code from a merged commit to running in
production safely and reversibly. It covers build artifacts, configuration, database
migrations, release strategies (rolling, blue-green, canary), health checks, and
rollback. The goal: any change can be released without downtime and undone in minutes if
it misbehaves. Deployment is where correct code still breaks production — this document
is about not letting it.

## Why It Matters

Most production incidents are triggered by a deploy, not by organic traffic. The moment of
change is the moment of risk. A deployment process that cannot roll back turns a small bug
into a long outage. A migration coupled to a code release makes rollback impossible without
data loss. Manual, undocumented deploys fail differently every time and cannot be trusted at
2 a.m. A disciplined pipeline makes releases boring — and boring is the goal, because boring
means recoverable.

## Core Principles

- **Build once, promote the same artifact.** The image tested in staging is the exact image
  that runs in production. Rebuilding per environment reintroduces the bug you thought you
  tested away.
- **Config comes from the environment, not the artifact.** Same binary, different config per
  environment. Secrets never live in the image or the repo.
- **Every deploy must be reversible.** If you cannot roll back in one command, you cannot
  deploy safely. Rollback is a feature, not an afterthought.
- **Decouple schema changes from code changes.** Migrate in backward-compatible steps so old
  and new code can run at the same time during a rollout.
- **A deploy is not done when it starts; it is done when it is healthy.** Gate rollout on
  health checks and error rates, not on "the pod started".

## Best Practices

- Produce an **immutable, versioned artifact** (container image tagged by commit SHA) in CI;
  promote that same tag through staging to production.
- Use **rolling or canary** releases behind health checks; route a small slice of traffic
  first, watch error rate and latency, then widen. Automate rollback on regression.
- Run migrations as **expand/contract**: add the new column/table (backward compatible),
  deploy code that writes both, backfill, then remove the old shape in a later release.
  Never drop or rename in the same deploy that stops using it.
- Make migrations forward-only and idempotent; never edit a migration that has run in
  production — add a new one.
- Give every service **liveness** and **readiness** probes; readiness must fail while the
  service is warming up or a dependency is down, so it receives no traffic prematurely.
- Drain connections on shutdown (handle `SIGTERM`, stop accepting new work, finish in-flight
  requests) so rollout does not sever live requests.
- Keep the pipeline fully automated and audited: no manual SSH-and-edit deploys.

## Examples

**Good Example** — backward-compatible migration, safe to roll back

```sql
-- Release 1: additive only. Old code ignores the column; new code can write it.
ALTER TABLE orders ADD COLUMN currency VARCHAR(3) NULL;   -- nullable, no default lock

-- Release 2 (after code writing `currency` is fully deployed and backfilled):
-- enforce the constraint. Rolling back Release 2 does not lose data.
UPDATE orders SET currency = 'USD' WHERE currency IS NULL; -- backfill
ALTER TABLE orders ALTER COLUMN currency SET NOT NULL;
```

**Bad Example** — schema and code coupled, rollback loses data

```sql
-- Single release, run in the same deploy that ships the new code:
ALTER TABLE orders RENAME COLUMN total TO total_cents;  -- old code now crashes
ALTER TABLE orders DROP COLUMN legacy_total;            -- data gone, unrecoverable
-- If the new code has a bug, rolling back the code leaves the schema broken:
-- old code reads `total`, which no longer exists. There is no safe rollback.
```

## Common Mistakes

- Rebuilding the artifact per environment, so production runs code that was never tested.
- Baking secrets or environment-specific config into the image.
- Coupling a destructive migration (drop/rename) to the release that stops using the column,
  making rollback impossible.
- Editing an already-applied migration instead of adding a new one.
- No readiness probe, so traffic hits pods before they can serve it.
- Ignoring `SIGTERM`, killing in-flight requests on every rollout.
- Treating "the deploy finished" as success without checking error rate and latency after.

## Production Tips

- Keep the previous known-good artifact one command away; rehearse rollback so it is muscle
  memory, not improvisation.
- Deploy small and often. Small diffs make the cause of a regression obvious; big-bang
  releases hide it.
- Automate canary analysis: promote or roll back on metrics, not on someone watching a graph.

## AI Review Checklist

- Is a single immutable artifact built once and promoted across environments?
- Is configuration injected from the environment, with secrets outside the image and repo?
- Are migrations backward-compatible (expand/contract) and forward-only?
- Can the release be rolled back in one command without data loss?
- Do liveness and readiness probes exist, and does readiness gate traffic correctly?
- Does the service drain in-flight work on `SIGTERM`?
- Is rollout gated on post-deploy health/error metrics, not just process start?

## Related

- `knowledge/backend/27-production.md`
- `knowledge/backend/22-observability.md`
- `knowledge/backend/17-transactions.md`
- `knowledge/backend/98-production-checklist.md`
