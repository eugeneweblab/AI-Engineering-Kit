---
id: woocommerce/27-production
topic: woocommerce
slug: production
title: "Production"
type: doc
order: 27
status: ready
tags: [woocommerce, production]
related: [woocommerce/22-deployment, woocommerce/23-monitoring, woocommerce/16-security, woocommerce/24-scaling, woocommerce/26-debugging]
when_to_use: "Read before taking a WooCommerce store live or reviewing whether an existing one is production-ready."
---
# Production

## Purpose

This document defines what "production-ready" means for a WooCommerce store: correct
environment configuration, caching that does not corrupt carts, backups that actually
restore, and the security and compliance baseline for handling real money and customer
data. It is the gate a store passes through before it takes an order from a stranger.

## Why It Matters

A production WooCommerce store handles payments, personal data, and inventory that maps to
real fulfilment. A cache misconfiguration can serve one customer's cart to another; a debug
flag left on can leak database paths; a broken backup turns a routine failure into permanent
data loss. Unlike a content site, a store outage is lost revenue by the minute and a
mishandled card detail is a compliance breach. The cost of getting this wrong is measured in
money and trust, so the checklist is not optional.

## Core Principles

- **Separate environments; promote, don't edit.** Development, staging, and production are
  distinct. Changes flow forward through [deployment](22-deployment.md) — never hand-edit
  production.
- **Config by environment, secrets out of code.** URLs, keys, and gateway modes come from
  environment variables or `wp-config` per environment, not from tracked files.
- **Cache aggressively, but never the dynamic pages.** Cart, checkout, and My Account must
  bypass full-page cache, or you leak sessions between shoppers.
- **Assume things fail.** Tested backups, monitoring, and a rollback path are prerequisites,
  not follow-ups.
- **Payments are PCI scope.** Card data goes to the gateway (tokenized/hosted fields); it
  never touches your server, logs, or database.

## Best Practices

- Set `WP_DEBUG=false`, `WP_DEBUG_DISPLAY=false`, and `SCRIPT_DEBUG=false` in production;
  log errors to a file, never the screen.
- Force **HTTPS everywhere** and set `FORCE_SSL_ADMIN`; checkout over HTTP is disqualifying.
- Enable a **persistent object cache** and a **full-page cache**, with `cart`, `checkout`,
  `my-account`, and `wc-ajax` requests excluded from page cache.
- Use the payment gateway's **hosted fields or tokenization** so raw PAN never reaches your
  app — keeping you in the smallest PCI-DSS scope (SAQ A).
- Run **automated, tested, off-site backups** of database and uploads; rehearse a restore.
  A backup you have never restored is a hope, not a backup.
- Pin versions and deploy from **version control** with a staging soak; keep a one-command
  rollback.
- Run a **real system cron** (`wp-cron` disabled) so scheduled emails, subscriptions, and
  Action Scheduler jobs fire on time.
- Lock down admin: strong/2FA logins, least-privilege roles, disabled file editor
  (`DISALLOW_FILE_EDIT`), and a WAF/rate limit in front.

## Examples

**Good Example** — production `wp-config` posture

```php
// Secrets and mode come from the environment, debug is off but logged,
// SSL is forced, and in-dashboard file editing is disabled.
define( 'WP_ENVIRONMENT_TYPE', 'production' );
define( 'WP_DEBUG', false );
define( 'WP_DEBUG_LOG', true );          // log to file for post-mortems
define( 'WP_DEBUG_DISPLAY', false );     // never render errors to shoppers
define( 'FORCE_SSL_ADMIN', true );
define( 'DISALLOW_FILE_EDIT', true );    // no plugin/theme editor in prod
define( 'DISABLE_WP_CRON', true );       // real cron runs wp-cron.php every minute

define( 'STRIPE_SECRET_KEY', getenv( 'STRIPE_SECRET_KEY' ) ); // from env, not tracked
```

**Bad Example** — a store that will leak and lose data

```php
define( 'WP_DEBUG', true );
define( 'WP_DEBUG_DISPLAY', true );   // stack traces + DB paths shown to visitors
// Live secret key committed to the repo and shared across environments:
define( 'STRIPE_SECRET_KEY', 'sk_live_51H...hardcoded' );
// No object cache, no page-cache exclusions → carts get cached and cross-served,
// and pseudo-cron means order emails fire late or not at all.
```

## Common Mistakes

- Leaving `WP_DEBUG_DISPLAY` on, exposing paths, queries, and notices to customers.
- Full-page caching cart/checkout/My Account, cross-serving sessions between shoppers.
- Committing live gateway keys, or reusing production keys in staging.
- Backups that are untested, on the same server, or exclude the database or uploads.
- Storing or logging raw card numbers, pulling the whole app into PCI scope.
- Relying on `wp-cron` under load, so subscription renewals and emails run late.
- Editing plugins/theme directly on production with no version control or rollback.

## Production Tips

- Add a **health endpoint / uptime check** on the storefront *and* checkout, plus the
  order-rate and error alerts from [monitoring](23-monitoring.md) — a store can be "up"
  while checkout is broken.
- Keep a **maintenance/read-only mode** switch so you can freeze new orders during an
  incident without a full outage.
- Verify **PCI and privacy** posture (SAQ A gateway integration, data-retention/erasure for
  GDPR/CCPA) before launch, not after the first data request.

## AI Review Checklist

- Are debug/display flags off, with errors logged to a file only?
- Is HTTPS forced site-wide, including admin and checkout?
- Are object cache and page cache enabled, with cart/checkout/My Account excluded?
- Do payments use hosted fields/tokenization so raw card data never hits the server?
- Are backups automated, off-site, inclusive of the database, and restore-tested?
- Is a real system cron configured with `wp-cron` disabled?
- Are secrets loaded from the environment and distinct per environment?

## Related

- `knowledge/woocommerce/22-deployment.md`
- `knowledge/woocommerce/23-monitoring.md`
- `knowledge/woocommerce/16-security.md`
- `knowledge/woocommerce/24-scaling.md`
- `knowledge/woocommerce/26-debugging.md`
