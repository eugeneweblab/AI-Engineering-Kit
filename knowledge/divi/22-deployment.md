---
id: divi/22-deployment
topic: divi
slug: deployment
title: "Deployment"
type: doc
order: 22
status: ready
tags: [divi, deployment]
related: [divi/21-testing, divi/23-maintenance, divi/10-performance, divi/19-security, divi/98-production-checklist]
when_to_use: "Read before pushing a Divi site live or migrating it between staging, production, or hosts."
---
# Deployment

## Purpose

This document defines how to move a Divi site safely between environments: staging →
production, host → host, and how to release child-theme code changes. Its core concern is
the thing that breaks Divi migrations — **serialized content with hard-coded URLs** — and
how to change domains without corrupting layouts.

## Why It Matters

Divi content is stored as serialized shortcode/JSON in the database, and it embeds
**absolute URLs** (images, links, background settings). A plain SQL find-and-replace of the
domain corrupts PHP serialized strings, because it changes string bytes without updating
their length prefixes, and the Visual Builder then fails to parse the layout. Meanwhile
Divi licensing is per-site, and production serves cached static CSS. A deploy that ignores
any of these ships a broken or unstyled site. Getting deployment right is mostly about
respecting serialization and cache state.

## Core Principles

- **Search-replace with a serialization-aware tool, never raw SQL.** Use
  `wp search-replace` (WP-CLI) or WP Migrate, which fix serialized-string lengths. A raw
  `UPDATE ... REPLACE()` corrupts Divi layouts.
- **Code deploys through version control; content stays in the database.** Child theme,
  custom modules, and config are Git-tracked and deployed. Page content is authored in the
  builder and migrated as data, not committed as code.
- **Regenerate static CSS on the target.** After a migration or deploy, clear Divi's cache
  and regenerate static CSS so production serves current output. See [performance](10-performance.md).
- **Never edit the live site directly.** Author and update on staging, test, then promote —
  editing production is how layouts get corrupted with no rollback.

## Best Practices

- Migrate the database and `wp-content/uploads` together, then run
  `wp search-replace 'https://staging.example' 'https://example.com' --all-tables` to fix
  every embedded URL, including inside serialized Divi content.
- Activate the Divi license on the production domain (Elegant Themes account / Divi
  Updates) so it receives security updates — an unlicensed site silently stops updating.
- Keep the **child theme in Git**; deploy it via CI/rsync. Never edit the parent theme or
  child theme files on the live server. See [maintenance](23-maintenance.md).
- After deploy: clear Divi cache + static CSS, clear any page/object cache and CDN, then run
  the post-launch smoke checks from the [production checklist](98-production-checklist.md).
- Take a full backup (DB + uploads) immediately before every production deploy so rollback
  is one restore away.
- Confirm environment config (HTTPS, `WP_ENV`, debug off, correct SMTP/API keys) differs
  correctly between staging and production.

## Examples

**Good Example** — serialization-safe domain migration

```bash
# Import the DB dump, then rewrite URLs with WP-CLI (repairs serialized string lengths).
wp db import production-clone.sql
wp search-replace 'https://staging.example.com' 'https://example.com' \
  --all-tables --precise --report-changed-only
# Sync media, then flush caches so production serves fresh output.
rsync -a staging:wp-content/uploads/ ./wp-content/uploads/
wp cache flush
wp divi clear-cache        # regenerate static CSS on the target
```

**Bad Example** — raw SQL replace corrupts Divi layouts

```sql
-- WRONG: byte-replaces the domain but NOT the serialized string length prefixes.
-- Divi shortcodes/JSON become unparseable; the Visual Builder fails to load.
UPDATE wp_posts
SET post_content = REPLACE(post_content,
    'https://staging.example.com', 'https://example.com');
```

## Common Mistakes

- Using SQL `REPLACE()` (or a text editor on a dump) to change domains, corrupting serialized
  Divi content.
- Forgetting `wp-content/uploads`, so migrated pages reference missing images.
- Not activating the Divi license on production, so it never gets security updates.
- Skipping cache/static-CSS regeneration, so production serves stale or unstyled pages.
- Editing content or code directly on the live site with no backup and no rollback path.
- Committing page content as code, or trying to Git-manage the database.

## Production Tips

- Automate deploys: Git push → CI runs [tests](21-testing.md) → deploy child theme → run
  `wp search-replace`/cache flush on the target.
- Keep environment differences in config, not in content, so the same layout works on both.
- Snapshot the DB before and after deploy; retain enough history to roll back a bad release.

## AI Review Checklist

- Is domain migration done with `wp search-replace` / a serialization-aware tool, never raw SQL?
- Were the database and `uploads` migrated together?
- Is the Divi license activated on the production domain for updates?
- Was Divi's static CSS regenerated and all caches/CDN flushed after deploy?
- Is child-theme code deployed from version control, with the parent theme untouched?
- Was a full backup taken immediately before the production deploy?

## Related

- `knowledge/divi/21-testing.md`
- `knowledge/divi/23-maintenance.md`
- `knowledge/divi/10-performance.md`
- `knowledge/divi/19-security.md`
- `knowledge/divi/98-production-checklist.md`
