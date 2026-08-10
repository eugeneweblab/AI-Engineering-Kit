---
id: woocommerce/98-production-checklist
topic: woocommerce
slug: production-checklist
title: "WooCommerce Production Checklist"
type: checklist
order: 98
status: ready
tags: [woocommerce, production-checklist, wp_options, WP_DEBUG, significant, launching, live]
related: [woocommerce/27-production, woocommerce/22-deployment, woocommerce/15-performance, woocommerce/16-security, woocommerce/99-ai-review-checklist]
when_to_use: "Read before launching a WooCommerce store or promoting a significant change to a live store."
---
# WooCommerce Production Checklist

## Purpose

This is the go/no-go checklist for putting a WooCommerce store — or a change to one — into
production. Every item is a verifiable yes/no an agent or reviewer can confirm against the
running site, its config, or a test order, not general advice. If an item is "no", the
honest answer is fix it or accept the risk in writing. Use it alongside the
[AI review checklist](99-ai-review-checklist.md), which reviews the code; this one reviews
that the store is ready to take real money.

## Why It Matters

WooCommerce stores fail in production for boringly repetitive reasons: a payment webhook
that was never reachable, HPOS half-migrated, a checkout that only worked with the test
gateway, taxes off by a rounding rule, no way to roll back a bad plugin update. Each is
trivially preventable and each has cost a real store real revenue and real customer trust.
A checklist turns "we probably tested checkout" into "we placed a live-mode order and
verified the receipt", and moves the cost of a gap from a lost sale to five minutes of
review.

## Payments & Checkout

**Rules:** [Payments](08-payments.md) · [Checkout](07-checkout.md)

- [ ] A real order has been placed in **live mode** (not just the test gateway) and
  refunded, confirming capture, order status, and receipt end to end.
- [ ] Every payment gateway's **webhook/IPN endpoint** is reachable from the internet and
  its handler is **idempotent** — a duplicate delivery does not double-fulfill.
- [ ] Orders do not get stuck in "pending payment": webhook failures are alerted, and there
  is a documented way to reconcile a paid-but-unmarked order.
- [ ] Both the **block (Store API)** and any legacy shortcode checkout paths in use have
  been tested; customizations apply on the path customers actually see.
- [ ] Cart totals, prices, and coupon amounts are recomputed server-side and cannot be
  overridden by the client (see [checkout](07-checkout.md), [payments](08-payments.md)).

## Data & Storage

**Rules:** [Orders](05-orders.md) · [Customers](06-customers.md)

- [ ] **HPOS** status is intentional and consistent: either fully enabled and migrated, or
  fully off — never mid-migration on launch (see [architecture](01-architecture.md)).
- [ ] A tested **backup** and a tested **restore** of the database and uploads exist — an
  untested backup is not a backup.
- [ ] Inventory/stock reduction uses WooCommerce's methods and has been checked under
  concurrent orders so oversell cannot occur.
- [ ] Customer PII and order retention meet the applicable privacy/compliance rules; test
  and abandoned orders are cleaned up (see [security](16-security.md)).

## Tax, Shipping & Pricing

**Rules:** [Taxes](10-taxes.md) · [Shipping](09-shipping.md)

- [ ] Tax rates, rounding, and inclusive/exclusive display are configured and verified
  against a known-correct order total (see [taxes](10-taxes.md)).
- [ ] Shipping zones, methods, and rates produce the expected cost for a real address in
  each region you sell to (see [shipping](09-shipping.md)).
- [ ] Currency, decimal, and price-format settings match the store's market and payment
  gateway expectations.

## Performance & Scale

**Rules:** [Performance](15-performance.md) · [Scaling](24-scaling.md)

- [ ] A persistent **object cache** (Redis/Memcached) is running, and page/full-page
  caching **excludes** cart, checkout, my-account, and any session-bearing page.
- [ ] Bulk product/order operations run through **Action Scheduler** batches, not in a
  single request that can time out (see [performance](15-performance.md)).
- [ ] Autoloaded options are bounded (no runaway `wp_options` autoload); slow queries on
  orders/products have been profiled under production-like data volume.
- [ ] The store has been load-tested on the launch traffic profile, including the checkout
  path (see [scaling](24-scaling.md)).

## Security & Access

**Rules:** [Security](16-security.md)

- [ ] Site is served over **HTTPS** end to end; mixed content and insecure gateway
  callbacks are eliminated.
- [ ] WooCommerce, WordPress, PHP, and every plugin/theme are on **supported, patched**
  versions; no abandoned plugins in the payment or checkout path.
- [ ] Admin, REST API, and Store API access enforce authentication and capability checks;
  no debug endpoints or `WP_DEBUG` display left on in production.
- [ ] Secrets (gateway API keys, webhook signing secrets) live in environment config, not
  in the database export or the repo.

## Deployment & Operations

**Rules:** [Deployment](22-deployment.md) · [Monitoring](23-monitoring.md)

- [ ] Deploys are repeatable and support a **rollback** of code, plugins, and (where safe)
  schema, tested on staging that mirrors production versions (see [deployment](22-deployment.md)).
- [ ] Transactional **emails** (new order, processing, completed, password reset) actually
  deliver via a real SMTP/transactional provider, not the PHP mailer (see [emails](18-emails.md)).
- [ ] Monitoring covers uptime, checkout success rate, payment errors, and stuck orders,
  with actionable alerts (see [monitoring](23-monitoring.md)).
- [ ] A **runbook** documents how to deploy, roll back, reconcile payments, and put the
  store in maintenance mode; ownership and on-call are assigned.

## AI Review Checklist

- Has a real live-mode order been placed, fulfilled, and refunded before launch?
- Is every gateway webhook reachable and its handler idempotent against duplicates?
- Is HPOS state consistent, and are database and uploads backed up *and* restore-tested?
- Do caching rules exclude cart/checkout/account, and is a persistent object cache present?
- Are all components on patched versions with secrets kept out of the repo and DB export?
- Do transactional emails deliver, and is there a runbook and named owner before launch?

## Related

- `knowledge/woocommerce/27-production.md`
- `knowledge/woocommerce/22-deployment.md`
- `knowledge/woocommerce/15-performance.md`
- `knowledge/woocommerce/16-security.md`
- `knowledge/woocommerce/99-ai-review-checklist.md`
