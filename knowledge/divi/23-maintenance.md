---
id: divi/23-maintenance
topic: divi
slug: maintenance
title: "Maintenance"
type: doc
order: 23
status: ready
tags: [divi, maintenance]
related: [divi/22-deployment, divi/21-testing, divi/19-security, divi/10-performance, divi/20-debugging]
when_to_use: "Read before updating Divi, WordPress, or plugins, or when planning a site's ongoing upkeep."
---
# Maintenance

## Purpose

This document defines how to keep a live Divi site healthy over time: a safe update cadence
for Divi, WordPress core, and plugins; database and cache hygiene; backups; and planning the
Divi 4 → Divi 5 transition. It tells an agent how to update without breaking a production
site that non-developers depend on.

## Why It Matters

Divi sites rot in predictable ways: skipped updates accumulate into a risky big-bang upgrade,
an untested update breaks a layout site-wide, the database bloats with revisions and cache
rows, and one day the license lapses and security patches stop arriving. Because the same
site handles editing and public traffic, a botched update is an outage. Steady, tested,
reversible maintenance is what keeps a Divi site fast and secure instead of a fragile liability.

## Core Principles

- **Update on a cadence, on staging first, one axis at a time.** Update WordPress core, then
  Divi, then plugins — on a clone, testing between steps — so a break is attributable and
  reversible. See [testing](21-testing.md) and [deployment](22-deployment.md).
- **Back up before every change.** DB + `uploads`, verified restorable. An update without a
  fresh backup is an irreversible bet.
- **Keep the license active.** Divi security and feature updates flow only to a licensed,
  activated domain. A lapsed license is a silently aging, vulnerable site.
- **Prune what grows unbounded.** Post revisions, transients, and cache tables balloon and
  slow the site; cap and clean them on a schedule. See [performance](10-performance.md).

## Best Practices

- Run updates on staging with a production data copy; open key front-end pages **and** the
  Visual Builder, then promote. Never bulk-update everything on production at once.
- Limit revisions to bound `wp_posts` growth (Divi layouts create large revisions):
  `define('WP_POST_REVISIONS', 10);` in `wp-config.php`.
- Automate scheduled backups (daily DB, weekly full) stored **off-site**, and test a restore
  quarterly — an untested backup is a guess.
- Keep the child theme, custom modules, and config in version control so every change is
  tracked and reversible; never hot-fix on the live server. See [security](19-security.md).
- Monitor uptime, core web vitals, and PHP error rates; treat a spike as a signal to open the
  [debugging](20-debugging.md) process.
- Track PHP version compatibility: keep PHP within Divi's and WordPress's supported range so
  updates do not fatal.
- Plan the **Divi 4 → Divi 5** migration deliberately: test on staging, since the content
  model (shortcodes → JSON) and some custom-module APIs change; do not auto-upgrade production.

## Examples

**Good Example** — bounded, reversible update routine

```bash
# On STAGING (clone of production), before any production update:
wp db export backup-$(date +%F).sql        # fresh, restorable backup first
wp core update && wp core update-db         # 1) WordPress core
wp theme update divi                        # 2) Divi (test builder loads after)
wp plugin update --all                      # 3) plugins
wp cache flush && wp divi clear-cache       # regenerate static CSS
# Then: open key pages + Visual Builder, run smoke tests, and only then promote.
```

```php
// wp-config.php — cap revisions so Divi's large layouts don't bloat the DB.
define( 'WP_POST_REVISIONS', 10 );
```

**Bad Example** — big-bang update on production

```bash
# WRONG: on the LIVE site, no backup, everything at once.
wp core update; wp theme update divi; wp plugin update --all
# A markup change or plugin conflict now breaks every page and the builder,
# with no backup to roll back to and no way to tell which update caused it.
```

## Common Mistakes

- Updating directly on production with no backup and no staging test.
- Updating core, theme, and plugins in one shot, so a break is unattributable.
- Letting the Divi license lapse, so security updates silently stop.
- Never pruning revisions/transients, so the database bloats and queries slow down.
- Hot-fixing child-theme code on the live server, drifting from version control.
- Auto-upgrading Divi 4 → Divi 5 on production without testing the content-model change.

## Production Tips

- Keep a maintenance log of what was updated and when, so a regression can be bisected.
- Schedule updates in a low-traffic window and put the site in maintenance mode during them.
- Alert on failed backups and on lapsing licenses/SSL certs before they expire.

## AI Review Checklist

- Are updates applied on staging first, one axis (core/theme/plugins) at a time, then promoted?
- Was a fresh, restorable backup taken before the update?
- Is the Divi license active so security updates are delivered?
- Are post revisions bounded and cache/transients cleaned on a schedule?
- Is all custom code in version control, with no hot-fixes on the live server?
- Is the Divi 4 → 5 migration planned and tested on staging, not auto-applied to production?

## Related

- `knowledge/divi/22-deployment.md`
- `knowledge/divi/21-testing.md`
- `knowledge/divi/19-security.md`
- `knowledge/divi/10-performance.md`
- `knowledge/divi/20-debugging.md`
