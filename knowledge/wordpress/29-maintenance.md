---
id: wordpress/29-maintenance
topic: wordpress
slug: maintenance
title: "Maintenance"
type: doc
order: 29
status: ready
tags: [wordpress, maintenance]
related: [wordpress/27-deployment, wordpress/26-wp-cli, wordpress/06-security, wordpress/23-caching, wordpress/98-production-checklist, wordpress/22-cron-and-background-tasks]
when_to_use: "Read when planning ongoing care of a WordPress site — update strategy, backups, plugin audits, database hygiene, and monitoring."
---
# Maintenance

## Purpose

This document defines what keeping a WordPress site healthy actually requires: how to apply
updates without breaking the site, what to back up and how to verify it, how to audit an
accumulating plugin list, and which database growth needs periodic attention.

A WordPress site is not finished at launch. It runs on software that updates roughly monthly,
with plugins that update weekly, on a platform where an unpatched vulnerability is found and
exploited within days.

---

## Core Principle

**Update on a schedule you control, or be updated on one you do not.**

Sites break during updates because updates were deferred until a dozen accumulated and one of
them was a major version. Frequent small updates are individually reversible; a six-month
backlog applied at once is not diagnosable.

---

## Updates

Core, plugins, and themes carry different risk profiles and deserve different policies:

| What | Policy |
|---|---|
| Core minor/security (6.7.1 → 6.7.2) | Automatic — enabled by default, leave it on |
| Core major (6.7 → 6.8) | Staging first, scheduled, after plugin compatibility check |
| Plugins | Staging first; security releases expedited |
| Themes (parent) | Staging first; verify child-theme overrides still apply |
| PHP version | Staging first; check every plugin's `Requires PHP` |

```php
// wp-config.php — automatic core updates for minor releases only (the default).
define( 'WP_AUTO_UPDATE_CORE', 'minor' );
```

For individual plugins where automatic updates are acceptable — small, well-maintained, and
non-critical — enable them per plugin rather than globally:

```php
add_filter( 'auto_update_plugin', function ( $update, $item ) {
	$always = array( 'wordpress-seo', 'query-monitor' );
	return in_array( $item->slug, $always, true ) ? true : $update;
}, 10, 2 );
```

A repeatable update run:

```bash
wp db export pre-update-$(date +%F).sql          # 1. backup first, always
wp plugin list --update=available --fields=name,version,update_version
wp plugin update --all --dry-run                 # 2. see what would change
wp plugin update --all                           # 3. on staging
wp core update-db                                # 4. schema migrations
wp cache flush
# 5. smoke-test: home page, a post, checkout or the primary conversion path, wp-admin
```

Do this on staging, verify, then repeat on production. "Update all" clicked directly on
production is how sites go down at 4pm on a Friday.

---

## Backups

A backup is two things — database *and* uploads — and it is worthless until a restore has been
tested.

```bash
# Database
wp db export /backups/db-$(date +%F-%H%M).sql
gzip /backups/db-*.sql

# Uploads (incremental)
rsync -a --delete wp-content/uploads/ /backups/uploads/

# Code lives in git and needs no separate backup — if it does, that is the finding.
```

What a backup policy has to specify, beyond "we take backups":

- **Frequency**, matched to how much data loss is acceptable. A store taking orders hourly
  cannot restore from a nightly dump without losing orders.
- **Retention** — daily for a week, weekly for a month, monthly for a year is a common shape.
- **Off-site storage.** A backup on the same server is not a backup; it dies with the server.
- **A tested restore.** Schedule one quarterly, into staging, timed. An untested backup is a
  hypothesis.

---

## Plugin Audit

Plugin count is the strongest predictor of a site's fragility. Audit quarterly:

```bash
wp plugin list --fields=name,status,version,update
```

For each plugin, four questions:

1. **Is it used?** Deactivated plugins still receive vulnerability reports and are still
   present on disk. Delete rather than deactivate.
2. **Is it maintained?** Check the last update date and tested-up-to version on
   wordpress.org. Abandoned plugins are unpatched plugins.
3. **Does it duplicate another?** Two SEO plugins, three caching plugins, and overlapping
   security plugins conflict rather than compound.
4. **Could this be twenty lines in the site's own plugin?** A plugin that adds one filter is
   a dependency, an update obligation, and an attack surface.

```bash
# Known vulnerabilities in what is installed.
wp plugin list --format=json > plugins.json   # check against a vulnerability database
```

---

## Database Hygiene

WordPress accumulates data that nothing ever removes:

```bash
# Post revisions — unbounded by default.
wp post delete $(wp post list --post_type=revision --format=ids) --force

# Expired transients.
wp transient delete --expired

# Spam and trashed comments.
wp comment delete $(wp comment list --status=spam --format=ids) --force

# Autoloaded options — the highest-impact check on this list.
wp option list --autoload=on --format=table --fields=option_name,size_bytes \
  | sort -k2 -rn | head -20

wp db optimize
```

Autoloaded options load on **every single request**. A few hundred kilobytes left behind by a
removed plugin is a permanent tax on every page view, and it is invisible until someone looks.

Bound revisions rather than deleting them repeatedly:

```php
define( 'WP_POST_REVISIONS', 10 );          // per post
define( 'EMPTY_TRASH_DAYS', 14 );
```

---

## Monitoring

Know the site is broken before a client tells you:

- **Uptime**, checking a real page rather than the server's root.
- **Errors** — PHP fatals and JavaScript exceptions, aggregated somewhere you will actually
  see them.
- **Performance** — Core Web Vitals from real users, not just a lab score.
- **SSL expiry** — automated renewal fails silently more often than it should.
- **Backup success** — a backup job that stopped running three weeks ago is the classic
  discovery during an incident.
- **Disk space** — uploads and logs grow monotonically.
- **Cron health** — `wp cron event list` showing overdue events means scheduled work stopped.

WordPress's own Site Health screen (`/wp-admin/site-health.php`) catches a useful subset:
outdated PHP, missing modules, failing REST or loopback requests. Check it during every
maintenance pass.

---

## Security Hygiene

Ongoing, not one-time:

- Remove unused plugins, themes, and user accounts — especially administrators from departed
  staff.
- Enforce strong passwords and two-factor authentication for anyone with `edit_posts` or
  above.
- Keep `DISALLOW_FILE_EDIT` and `DISALLOW_FILE_MODS` on — see [Deployment](27-deployment.md).
- Review file integrity after any suspected compromise: `wp core verify-checksums` and
  `wp plugin verify-checksums --all`.
- Rotate database credentials and salts when staff with access leave.

---

## A Maintenance Cadence

| Frequency | Work |
|---|---|
| Continuous | Uptime, error, and backup monitoring |
| Weekly | Apply plugin and core minor updates on staging, then production; check Site Health |
| Monthly | Review error logs and slow pages; check disk and database growth |
| Quarterly | Plugin audit; tested restore; review users and access; check PHP version support |
| Annually | Dependency and architecture review; renew or retire what is no longer justified |

---

## Examples

**Good Example** — updates rehearsed on a copy, backups proven by restoring

```bash
#!/usr/bin/env bash
set -euo pipefail

# 1. Refresh staging from production so the rehearsal is realistic.
wp @production db export - | wp @staging db import -

# 2. Apply updates there first, one layer at a time.
wp @staging plugin update --all --dry-run     # report what would change
wp @staging plugin update --all
wp @staging core update

# 3. Prove the site still works before touching production.
wp @staging cron event run --due-now
npx playwright test --config=tests/smoke.config.ts

# 4. Only now, and with a restorable backup taken first.
wp @production db export "backups/pre-update-$(date -u +%Y%m%dT%H%M%SZ).sql"
wp @production plugin update --all
```

```bash
# A backup is not a backup until it has been restored. Verify on a schedule.
wp @scratch db import "backups/pre-update-20260801T030000Z.sql"
wp @scratch post list --post_type=post --format=count   # non-zero = the dump is real
```

**Bad Example** — deferred updates, unverified backups

```bash
# "We will update after the release." Six months later this is one command that
# crosses two major versions, and nothing here is individually reversible.
wp plugin update --all && wp core update && wp theme update --all

# Backup written to the same disk as the site: a disk failure loses both.
mysqldump wordpress > /var/www/app/backup.sql

# Nobody has ever restored it, so nobody knows the dump is truncated.
```

Auto-updates for security releases plus a scheduled window for everything else beats both
extremes: unattended major updates, and updates deferred until they cannot be reasoned about.

---

## Common Mistakes

- **Deferring updates** until the backlog is too large to diagnose.
- **Updating production first**, with no staging verification.
- **Backups that have never been restored.**
- **Backups stored on the same server** they protect.
- **Database backed up, uploads not** — or the reverse.
- **Deactivating plugins instead of deleting them.**
- **Ignoring autoloaded option growth.**
- **Unbounded revisions** on a content-heavy site.
- **No monitoring**, so the client reports the outage.
- **Administrator accounts** for people who left the project.

---

## Verification Checklist

- Are core minor updates automatic, and are majors and plugins scheduled through staging?
- Is a database export taken before every update run?
- Do backups cover database and uploads, stored off-site, with retention defined?
- Has a restore been performed and timed within the last quarter?
- Has the plugin list been audited, with unused plugins deleted rather than deactivated?
- Are revisions, transients, and autoloaded options within sane bounds?
- Is uptime, error, backup, SSL, and cron health monitored?
- Are administrator accounts current, with file editing disabled?

---

## Summary

Maintenance is a schedule, not a reaction: frequent small updates verified on staging, backups
of both database and uploads proven by a tested restore, a plugin list kept short
deliberately, and monitoring that tells you about failures before a client does.

## Related


- `knowledge/wordpress/27-deployment.md`
- `knowledge/wordpress/26-wp-cli.md`
- `knowledge/wordpress/06-security.md`
- `knowledge/wordpress/23-caching.md`
- `knowledge/wordpress/98-production-checklist.md`
- `knowledge/wordpress/22-cron-and-background-tasks.md`
