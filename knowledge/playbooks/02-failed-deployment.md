---
id: playbooks/02-failed-deployment
topic: playbooks
slug: failed-deployment
title: "Playbook — Failed Deployment"
type: doc
order: 2
status: ready
tags: [playbooks, failed-deployment]
related: [playbooks/01-site-down, templates/03-incident-report, tools/28-release-tools, wordpress/27-deployment, databases/17-migrations]
when_to_use: "Follow when a release broke production, a deploy will not complete, or a migration failed partway."
---
# Playbook — Failed Deployment

## Purpose

Get back to a known-good state. A failed deploy is the most recoverable kind of incident —
you know exactly what changed and you have the previous version — provided you roll back
before trying to fix forward.

---

## Step 1 — Roll back first

**Do not debug a broken release in production.** Restore the previous version, then
investigate at your own pace with the pressure off.

```bash
# Symlink-based deploy: repoint and clear the bytecode cache
PREVIOUS=$(ls -1dt /var/www/app/releases/* | sed -n 2p)   # the release before the current one
ln -sfn "$PREVIOUS" /var/www/app/current
sudo systemctl reload php8.3-fpm

# Container platforms
kubectl rollout undo deployment/web
docker service update --rollback web

# Managed platforms usually expose a one-command revert
```

If the previous version is not obviously identifiable, that is the first finding for the
report — a deploy you cannot reverse is not a deploy, it is a migration.

Confirm recovery from outside, the same way as in [Site Down](01-site-down.md):

```bash
curl -sS -o /dev/null -w '%{http_code} %{time_total}s\n' https://example.com/
```

---

## Step 2 — Check whether the rollback was enough

Code rolls back cleanly. Four things do not:

| Thing | Why it survives the rollback | What to do |
|---|---|---|
| **Database migrations** | Already applied; old code may not understand the new schema | See Step 3 |
| **Bytecode / opcode cache** | Serves the previous path's compiled code | Reload the runtime, always |
| **CDN and page cache** | Still serving the broken assets or HTML | Purge, then verify with a cache-busting request |
| **Queued jobs** | Enqueued by the new code, consumed by the old | Pause the queue; drain or discard deliberately |

```bash
# Purge and verify
curl -sS -o /dev/null -w '%{http_code}\n' 'https://example.com/?cachebust=1'
```

---

## Step 3 — Handle the migration

This is where a rollback becomes genuinely hard, and it depends on what the migration did:

**Additive** (new column, new table, new index) — usually safe to leave. Old code ignores it.
Roll back the code and stop.

**Destructive** (dropped column, renamed column, changed type) — old code will error. Two
options, in order of preference:

1. **Fix forward.** Ship a corrected version rather than reversing the schema. Almost always
   faster and safer than an untested down-migration.
2. **Restore from backup.** Only when data is actually corrupted, and only with a known
   restore point. You will lose everything written since it — quantify that before you start.

```bash
# Where did it stop?
npx prisma migrate status
wp db query "SELECT * FROM migrations ORDER BY id DESC LIMIT 5"
```

**A migration that failed partway is the worst case:** the schema is in a state no version of
the code expects. Do not run it again hoping it completes. Determine what applied, finish or
reverse it by hand under a transaction, and record every statement you run.

The prevention for all of this is additive migrations — add, backfill, deploy code that
writes both, migrate, and only then remove. See [Databases — Migrations](../databases/17-migrations.md).

---

## Step 4 — Diagnose, with the pressure off

Now that production is stable:

```bash
# What actually shipped? Set these to the two release SHAs first.
GOOD=a1b2c3d   # last known-good release
BAD=e4f5a6b    # the release that broke

git log --oneline "$GOOD".."$BAD"
git diff "$GOOD".."$BAD" -- package.json composer.json   # dependency changes first
```

The usual causes, in rough order of frequency:

- **An environment variable** present locally and in staging, missing in production.
- **A dependency** that resolved differently because the lockfile was not used.
- **A migration** that assumed data the production table does not have.
- **A build artifact** that was stale, or built against the wrong environment.
- **An external service** whose credentials or quota differ in production.
- **Cache state** — the new code assumed a cache shape the old cache does not have.

If nothing in the diff explains it, question whether the deploy is the cause at all. Deploys
attract blame because they are visible; a certificate expiring at the same time does not
announce itself.

---

## Step 5 — Close the gap

A failed deploy that reaches production means a gate was missing. Before re-deploying, name
the one that would have caught it:

☐ Did CI run the full verify suite on the merge commit?

☐ Was this exercised on staging with production-like data?

☐ Would a smoke test against the deployed environment have caught it?

☐ Was a migration reviewed for reversibility, not just correctness?

☐ Should this ship behind a feature flag next time?

Add the missing check as an action item — see [Incident Report](../templates/03-incident-report.md).

---

## Step 6 — Re-deploy deliberately

- Fix the cause, not the symptom.
- Re-run the full pipeline; do not reuse the artifact that failed.
- Deploy at a time when people are available, not at the end of the day.
- Watch error rates for at least one full traffic cycle before calling it done.
- If the platform supports it, use a canary or a percentage rollout so the next failure
  affects a fraction of users.

---

## Common Mistakes

- **Debugging in production** instead of rolling back first.
- **Rolling back code but not the bytecode cache**, so nothing appears to change.
- **Assuming the rollback covered the migration.**
- **Re-running a partially failed migration** and compounding the schema damage.
- **Restoring from backup** when fixing forward was available — silently discarding writes.
- **Re-deploying the same artifact** after a "quick fix" that was not rebuilt.
- **Blaming the deploy** without confirming it correlates with the start time.
- **No action item**, so the same gap ships the same failure next quarter.

---

## Examples

**Good Example** — roll back on a clock, then investigate the artifact

```bash
# Decide the rollback deadline BEFORE debugging: "if not healthy by 14:25, revert".
kubectl rollout status deployment/api --timeout=120s || kubectl rollout undo deployment/api

# For a symlink-based deploy, the previous release is still on disk.
PREVIOUS=$(ls -1dt /var/www/app/releases/* | sed -n 2p)
ln -sfn "$PREVIOUS" /var/www/app/current
sudo systemctl reload php8.3-fpm

# Confirm the rollback actually took effect — do not assume.
curl -sS https://example.com/api/version
```

```bash
# Then investigate off production, against the exact artifact that failed.
GOOD=a1b2c3d   # last known-good release
BAD=e4f5a6b    # the release that broke
git log --oneline "$GOOD".."$BAD"
docker run --rm -it "registry.example.com/api:$BAD" node -e 'require("./dist/main.js")'
```

The rollback is boring because it was rehearsed: the previous release is on disk, the database
migration was backward-compatible, and the decision had a deadline instead of an argument.

**Bad Example** — fix forward under pressure

```bash
# 15 minutes into a broken deploy, with no rollback path because the release
# directory was overwritten in place.
cd /var/www/app && git pull && composer install     # on the live server

# The migration already ran and dropped a column, so the previous release
# cannot start even if it were available.
php artisan migrate                                  # irreversible, unreviewed

# Each attempt is untested, unlogged, and applied straight to production.
```

Fixing forward is a decision, not a default. It is only available when the change is small,
understood, and reversible — none of which is true fifteen minutes into an outage.

---

## Related

- `knowledge/playbooks/01-site-down.md`
- `knowledge/templates/03-incident-report.md`
- `knowledge/tools/28-release-tools.md`
- `knowledge/wordpress/27-deployment.md`
- `knowledge/databases/17-migrations.md`
