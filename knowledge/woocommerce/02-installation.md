---
id: woocommerce/02-installation
topic: woocommerce
slug: installation
title: "WooCommerce Installation"
type: doc
order: 2
status: ready
tags: [woocommerce, installation, WP_ENVIRONMENT_TYPE, wp-config.php, SITE_URL, production, staging, WooCommerce]
related: [woocommerce/00-overview, woocommerce/01-architecture, woocommerce/22-deployment, woocommerce/15-performance, woocommerce/16-security]
when_to_use: "Read before installing, upgrading, or provisioning an environment for a WooCommerce store."
---
# WooCommerce Installation

## Purpose

This document defines how to install and provision WooCommerce correctly: the runtime it
needs, how to install and pin it reproducibly, and how to set up separate environments.
The goal is an install that is deterministic, upgradeable, and identical from a developer's
laptop to production — not a one-off click-through that no one can reproduce.

## Why It Matters

WooCommerce is a stateful application handling money, so "it installed fine on my machine"
is not enough. Version drift between environments is a leading cause of checkout bugs that
only appear in production. An install with the wrong PHP version, a missing extension, or
an unpinned plugin set will pass a smoke test and then fail on a live payment. Because
upgrades touch the database schema (HPOS tables, product lookup tables), a botched or
untested upgrade can corrupt orders. Treat installation as code, not as a manual ritual.

## Core Principles

- **Meet the runtime requirements first.** As of 2026, target PHP 8.1+ (8.2/8.3
  preferred), MySQL 8.0+ or MariaDB 10.6+, and a current WordPress. Below the floor,
  WooCommerce refuses to run or degrades.
- **Pin every version.** WordPress core, WooCommerce, and every extension must have an
  exact, committed version so environments are reproducible.
- **Separate environments.** Local, staging, and production are distinct databases and
  configs. Never develop or test against live customer data.
- **Automate the install.** Use WP-CLI or a deploy script so the same steps run everywhere;
  manual admin clicks are not reproducible.
- **Back up before every upgrade.** Upgrades run database migrations; a verified backup is
  the only safe rollback.

## Best Practices

- Manage plugins and versions with Composer (via `wpackagist`) or a committed lockfile so
  installs are deterministic and auditable.
- Run the WooCommerce database update step explicitly after upgrades
  (`wp wc update`) rather than relying on a browser-triggered background update.
- Keep secrets (DB credentials, payment keys) in environment variables or a secrets
  manager, never in committed `wp-config.php`.
- Set `WP_ENVIRONMENT_TYPE` (`local`/`staging`/`production`) so code can branch on
  environment and disable test payment gateways in production.
- After install, confirm HPOS status and the checkout type (block vs. shortcode) match
  what your code targets; these defaults differ across versions.

## Examples

**Good Example** — reproducible, scripted install

```bash
# Pinned versions → identical result everywhere. Runs in CI, staging, and prod.
wp core install --url="$SITE_URL" --title="Shop" \
  --admin_user="$ADMIN_USER" --admin_email="$ADMIN_EMAIL" --skip-email
wp plugin install woocommerce --version=9.4.0 --activate
wp wc update                       # apply WooCommerce DB migrations explicitly
wp option update woocommerce_feature_custom_order_tables_enabled yes  # HPOS on
wp config set WP_ENVIRONMENT_TYPE staging --type=constant
```

**Bad Example** — manual, unpinned, live-data install

```bash
# "latest" makes every install different and un-rollbackable; no backup before
# migrations; developing straight against the production database.
wp plugin install woocommerce --activate           # whatever version is newest today
mysql -e "USE production_shop"                       # editing live customer data
# ...then clicking through the setup wizard by hand, unrecorded.
```

## Common Mistakes

- Installing "latest" instead of a pinned version, so environments silently diverge.
- Upgrading WooCommerce without a database backup, leaving no rollback path.
- Skipping the explicit DB update step and shipping code that queries not-yet-migrated
  tables.
- Committing payment API keys or DB passwords into `wp-config.php`.
- Testing against production data or a live payment gateway.
- Ignoring PHP/MySQL version floors, causing subtle failures under load.

## Production Tips

- Gate deploys on a staging run that mirrors production versions and a copy (sanitized) of
  production data.
- Put the store in maintenance mode during upgrades that run migrations.
- Keep an object cache (Redis) and a persistent OPcache configured; WooCommerce is
  query-heavy and these are effectively required at scale (see `15-performance.md`).
- Record the exact WooCommerce/WordPress/PHP versions of each environment in your deploy
  metadata for incident forensics.

## AI Review Checklist

- Are WordPress, WooCommerce, and all extensions pinned to exact versions?
- Is the install scripted (WP-CLI/Composer) rather than manual?
- Does the runtime meet the PHP/MySQL floors for the targeted WooCommerce version?
- Is `wp wc update` run explicitly after upgrades, with a backup taken first?
- Are secrets kept out of committed config?
- Is `WP_ENVIRONMENT_TYPE` set and used to keep test gateways out of production?

## Related

- `knowledge/woocommerce/00-overview.md`
- `knowledge/woocommerce/01-architecture.md`
- `knowledge/woocommerce/22-deployment.md`
- `knowledge/woocommerce/15-performance.md`
- `knowledge/woocommerce/16-security.md`
