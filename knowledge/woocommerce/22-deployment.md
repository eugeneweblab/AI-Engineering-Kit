---
id: woocommerce/22-deployment
topic: woocommerce
slug: deployment
title: "WooCommerce Deployment"
type: doc
order: 22
status: ready
tags: [woocommerce, deployment, composer.json, WooCommerce, deployed, store, changing]
related: [woocommerce/21-testing, woocommerce/23-monitoring, woocommerce/15-performance, woocommerce/16-security]
when_to_use: "Read before releasing WooCommerce code to production or changing how a store is deployed and updated."
---
# WooCommerce Deployment

## Purpose

This document defines how to deploy WooCommerce safely: releasing plugin/theme changes,
running database migrations, updating WooCommerce and WordPress core, and rolling back when
a release goes wrong. It is written so an agent can ship a change to a live store without
dropping orders, corrupting data, or taking checkout offline.

WooCommerce deployment is unusual because the application state (orders, stock, sessions)
lives in the same database you are migrating, and the store is often taking money during
the deploy. A safe process treats the database as production data that must survive the
release, uses a real staging environment, and never edits code on the live server.

## Why It Matters

A WooCommerce store is a live financial system. Deploying by editing files over SFTP, or
running an unreviewed migration against the orders table, can drop in-flight checkouts,
double-charge customers via a half-applied change, or corrupt order history that is legally
required for accounting. Unlike a stateless app you can redeploy freely, a store's database
carries irreplaceable transactional data — there is no "just redeploy" once orders are
mangled. Downtime is also directly measurable in lost revenue. Because the blast radius is
money and customer trust, WooCommerce releases need the same discipline as a database
change in any transactional system: tested, reversible, and observable.

## Core Principles

- **Never edit code on production.** Deploy immutable, version-controlled artifacts built
  and tested in CI — see [testing](21-testing.md). Files changed by hand are lost on the
  next deploy and untraceable.
- **The database is production state.** Back it up before every release and treat schema
  changes as forward-and-backward compatible migrations, not one-shot SQL.
- **Stage on a copy of production.** Run the release against real (sanitized) order data
  before touching the live store; store bugs hide in real data, not fixtures.
- **Make releases reversible.** Have a rollback for both code and database before you
  deploy. "We'll fix forward" is not a plan for corrupted orders.
- **Deploy without interrupting checkout.** Use atomic swaps and drain in-flight requests;
  a store mid-checkout must not see a partial deploy.

## Best Practices

- Manage code with Composer and version control; deploy a built artifact via an atomic
  symlink swap (Deployer, Bedrock-style) so the switch is instant and reversible.
- Keep WooCommerce and WordPress out of the "edit in admin" workflow: pin versions in
  `composer.json`, update via PR, and test the update in staging first.
- Run WooCommerce's database update (`wp wc update`) as an explicit, monitored step after
  deploying new code — never let it auto-run mid-request on a busy store.
- Put schema/data migrations behind Action Scheduler or WP-CLI so long migrations run in
  the background and are idempotent and resumable.
- Back up the database immediately before deploy and verify the backup restores; snapshot
  uploads too. Confirm rollback works in staging.
- Run a post-deploy smoke test: place a test order end-to-end, confirm email and payment
  capture, before declaring success — see [monitoring](23-monitoring.md).
- Deploy during low-traffic windows and behind a maintenance-mode fallback that still shows
  a branded page, not a fatal error.

## Examples

**Good Example** — atomic, tested, migrated deliberately

```bash
# CI has already run the test matrix (PHP × WooCommerce × HPOS) and built the artifact.
wp db export backup-$(date +%F-%H%M).sql          # reversible: full DB snapshot first

# Atomic swap: build the new release beside the old, then flip a symlink.
ln -sfn /var/www/releases/2026-07-07 /var/www/current   # instant, no partial state

wp wc update --yes                                 # run WC DB update as an explicit step
wp action-scheduler run --group=my_migration       # long data migration, resumable

# Post-deploy smoke test — prove checkout works before walking away.
wp eval-file scripts/smoke-place-test-order.php || {
    ln -sfn /var/www/releases/2026-07-01 /var/www/current  # roll back code instantly
    echo "smoke test failed, rolled back"; exit 1;
}
```

**Bad Example** — edit-on-prod, blind migration, no rollback

```bash
# Editing live files over SFTP: untracked, lost on next deploy, and the store
# serves a half-updated codebase while the upload is in flight.
scp checkout-fix.php prod:/var/www/current/wp-content/plugins/my-plugin/

# Destructive, non-idempotent SQL run straight at production with no backup.
# A typo here corrupts every order's status; there is no way back.
wp db query "UPDATE wp_posts SET post_status='wc-completed' WHERE post_type='shop_order'"

# No smoke test, no rollback, no monitoring — success is assumed, not verified.
```

## Common Mistakes

- Editing plugin/theme files directly on the production server.
- Deploying without a fresh, verified database backup and a rollback plan.
- Running destructive or non-idempotent SQL against live order data.
- Letting WooCommerce's DB update auto-run mid-request instead of as a controlled step.
- Skipping staging, so bugs that only appear in real order data reach production.
- No post-deploy smoke test, so a broken checkout is discovered by customers.
- Updating WooCommerce/WordPress from the admin on the live store with no rollback.

## Production Tips

- Automate the pipeline: CI runs tests, builds the artifact, deploys atomically, runs the
  smoke test, and auto-rolls-back on failure.
- Keep the last few releases on disk so rollback is a symlink flip, not a rebuild.
- Sanitize customer PII when cloning production to staging so real emails/cards never leak.
- Announce and monitor releases; watch error rate and checkout success for 15 minutes
  post-deploy — see [monitoring](23-monitoring.md).

## AI Review Checklist

- Is the release a versioned, CI-tested artifact rather than hand-edited production files?
- Is there a verified database backup and a tested rollback for both code and schema?
- Are migrations idempotent, resumable, and run as an explicit step (not mid-request)?
- Is the change validated on staging against realistic order data first?
- Does the deploy swap atomically without serving a partial codebase?
- Is there a post-deploy smoke test that places a real test order?
- Are WooCommerce/WordPress versions pinned and updated through the pipeline, not the admin?

## Related

- `knowledge/woocommerce/21-testing.md`
- `knowledge/woocommerce/23-monitoring.md`
- `knowledge/woocommerce/15-performance.md`
- `knowledge/woocommerce/16-security.md`
