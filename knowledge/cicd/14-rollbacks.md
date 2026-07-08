---
id: cicd/14-rollbacks
topic: cicd
slug: rollbacks
title: "Rollbacks"
type: doc
order: 14
status: ready
tags: [cicd, rollbacks]
related: [cicd/10-deployment, cicd/11-blue-green-deployment, cicd/12-canary-deployment, cicd/13-feature-flags, cicd/08-versioning]
when_to_use: "Read before shipping any deployment, so a fast, tested reversal path exists before you need it."
---
# Rollbacks

## Purpose

This document defines how to revert a bad release quickly and safely. It is written so an
agent designs deployments that are *reversible by construction* — where returning to the
last known-good state is a fast, tested, low-risk operation, not an improvised scramble
during an outage.

A rollback is the ability to move production from a broken version back to the previous
good one with minimal downtime and no data loss. It is the safety net under every
[deployment strategy](10-deployment.md); a deploy you cannot cheaply undo is a bet, not a
release.

## Why It Matters

Every deployment can fail, and some failures only appear under real production load.
Mean time to recovery, not mean time between failures, is what users feel. A team that
can roll back in 60 seconds treats a bad deploy as a non-event; a team whose only option
is "roll forward with a hotfix" turns every regression into a 30-minute outage while they
write, review, and ship a fix under pressure. The cost of building for rollback is
discipline — backward-compatible changes and versioned artifacts — and it is far cheaper
than the cost of not having one when production is down.

## Core Principles

- **Make rollback the default recovery action.** When a deploy misbehaves, revert first,
  diagnose second. Do not debug in production while users are affected.
- **Deploy immutable, versioned artifacts.** Roll back by re-pointing to a previous
  known-good, immutable image/artifact — never by rebuilding from a moved tag.
- **Separate schema changes from code changes.** Databases do not roll back like code.
  Use expand/contract migrations so old and new code both work against the current schema.
- **Never write a destructive migration in the same release that depends on it.** Add
  columns/tables in one release; stop using the old ones in a later release; drop them in
  a third — so any single step is reversible.
- **Test the rollback path, not just the deploy path.** An untested rollback is an
  assumption, and assumptions fail during incidents.

## Best Practices

- Keep the last N known-good artifacts and their configuration retained and instantly
  re-deployable; tie every deploy to an immutable version (see [versioning](08-versioning.md)).
- Prefer strategies with built-in reversal: [blue-green](11-blue-green-deployment.md)
  (flip the router back) and [canary](12-canary-deployment.md) (shift weight back to 0).
- Gate migrations behind expand/contract: additive change → deploy code that tolerates
  both shapes → backfill → remove old shape in a later release.
- Version configuration and secrets alongside code so a rollback restores the matching
  config, not a mismatched pair.
- Use [feature flags](13-feature-flags.md) as the fastest partial rollback: disable one
  feature without reverting the whole deploy.
- Automate rollback triggers off health checks and SLO breaches so recovery does not wait
  on a human noticing.
- Practice rollbacks in a game day; measure the actual time-to-revert and shrink it.

## Examples

**Good Example** — expand/contract migration keeps every step reversible

```sql
-- Release 1 (expand): additive only. Old code ignores the column; rollback is trivial.
ALTER TABLE users ADD COLUMN email_verified boolean NOT NULL DEFAULT false;

-- Release 2: new code writes/reads email_verified. Old code still works (column is nullable-safe).
-- Backfill runs as data migration, independent of the deploy.

-- Release 3 (contract): only after Release 2 is proven, remove the legacy path.
ALTER TABLE users DROP COLUMN legacy_verified_flag;
-- Any single release can be rolled back to the prior one without data loss.
```

**Bad Example** — irreversible, destructive migration coupled to the deploy

```sql
-- Same release renames + drops the column the OLD code still reads.
ALTER TABLE users RENAME COLUMN verified TO email_verified; -- old code now 500s
ALTER TABLE users DROP COLUMN signup_source;                -- data gone, unrecoverable
-- Rolling back the app to the previous version cannot work: the schema it expects
-- no longer exists, and the dropped data is unrecoverable. There is no way back.
```

## Common Mistakes

- Treating "roll forward with a hotfix" as the only recovery, so every incident is a
  timed coding exercise under pressure.
- Coupling a destructive or renaming migration to the code release that needs it, making
  the deploy irreversible.
- Rolling back code but not the matching configuration or secrets, producing a broken
  mismatched state.
- Rebuilding from a mutable tag (`latest`) instead of re-deploying the exact prior
  artifact, so "rollback" ships something new.
- Never testing the rollback, so the first real attempt fails during an outage.
- No automated trigger, so rollback waits on a human watching dashboards.

## Production Tips

- Put the rollback command in the deploy runbook, next to the deploy command, with the
  exact previous version pinned or discoverable.
- Alert on and record every rollback; a frequent rollback rate is a signal that your
  pre-production gates are too weak.
- For stateful systems, snapshot/backup before risky migrations so data-level recovery is
  possible even when schema rollback is not.

## AI Review Checklist

- Can this deployment be reverted to the previous known-good artifact quickly?
- Is the artifact immutable and versioned, not rebuilt from a moving tag?
- Are schema changes expand/contract and decoupled from the code that depends on them?
- Does any migration in this release destroy or rename data the prior version reads?
- Does rollback restore the matching configuration and secrets, not just the code?
- Is the rollback path tested and documented, with an automated trigger on SLO breach?
- Are feature flags available as a fast partial-rollback lever?

## Related

- `knowledge/cicd/10-deployment.md`
- `knowledge/cicd/11-blue-green-deployment.md`
- `knowledge/cicd/12-canary-deployment.md`
- `knowledge/cicd/13-feature-flags.md`
- `knowledge/cicd/08-versioning.md`
