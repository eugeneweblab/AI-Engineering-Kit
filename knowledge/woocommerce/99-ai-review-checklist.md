---
id: woocommerce/99-ai-review-checklist
topic: woocommerce
slug: ai-review-checklist
title: "WooCommerce AI Review Checklist"
type: doc
order: 99
status: ready
tags: [woocommerce, ai-review-checklist]
related: [woocommerce/29-ai-review, woocommerce/16-security, woocommerce/12-hooks, woocommerce/98-production-checklist, woocommerce/100-common-antipatterns]
when_to_use: "Read when reviewing or generating any WooCommerce code change, before it is merged."
---
# WooCommerce AI Review Checklist

## Purpose

This is the review gate for WooCommerce *code* — a customization, extension, template
override, or REST/Store API integration. Every item is a verifiable yes/no an agent can
confirm by reading the diff, not vague advice. It complements the
[production checklist](98-production-checklist.md), which reviews the running store; this
one reviews the change before it ships. Reject a change on any "no" unless the risk is
recorded and accepted.

## Why It Matters

Most WooCommerce defects are not exotic — they are the same handful of mistakes repeated:
a raw meta read that breaks under HPOS, a trusted client price, a missing nonce, a
non-idempotent webhook, a core edit an update will erase. Each passes a quick manual test
in a clean store and fails in production beside real data and other plugins. A concrete
checklist catches these at review, while the fix is one line, instead of after a customer
is double-charged.

## Data Access & Correctness

- [ ] Products and orders are read/written through **CRUD objects** (`wc_get_product()`,
  `wc_get_order()`, `->save()`), not `get_post_meta()`/`update_post_meta()`/`$wpdb`.
- [ ] Order code is **HPOS-compatible** — no assumption that orders live in
  `wp_posts`/`wp_postmeta` (see [architecture](01-architecture.md)).
- [ ] Stock, totals, and status changes use WooCommerce's own methods, not read-modify-write
  on meta that can race.
- [ ] Any direct `$wpdb` query is justified by profiling, parameterized with `$wpdb->prepare()`,
  and isolated behind a clearly named function.

## Trust & Money

- [ ] Prices, line totals, quantities, and coupon values are **recomputed server-side**;
  nothing money-related is trusted from `$_POST`/request.
- [ ] Payment and webhook handlers are **idempotent** — a duplicate delivery or retry does
  not capture, fulfill, or refund twice (see [payments](08-payments.md)).
- [ ] Order status transitions go through the API (`$order->update_status()` /
  `payment_complete()`), so hooks and stock reduction fire correctly.

## Extension Hygiene

- [ ] Customization is delivered via **hooks** (actions/filters), not by editing core or
  parent-theme files that an update reverts (see [hooks](12-hooks.md)).
- [ ] Any template override matches the plugin's current template version and is noted for
  re-check on WooCommerce upgrades.
- [ ] Customizations target the checkout path in use — **block (Store API)** as well as
  legacy shortcode where relevant (see [checkout](07-checkout.md)).
- [ ] Hook callbacks are cheap; expensive/external work is deferred to **Action Scheduler**,
  not run inline on page load or checkout.

## WordPress Security

- [ ] Every state-changing request verifies a **nonce** and a **capability**
  (`current_user_can()`); nothing relies on obscurity (see [security](16-security.md)).
- [ ] Input is **sanitized** on the way in (`sanitize_text_field`, `wc_clean`, etc.) and
  **escaped** on output (`esc_html`, `esc_attr`, `wp_kses`).
- [ ] REST and Store API routes declare a real `permission_callback`; none is left as
  `__return_true` on a route that reads or writes store data.
- [ ] No secrets, card data, or full PII are logged or echoed.

## Compatibility & Versions

- [ ] Only non-deprecated APIs are used, appropriate to the **targeted WooCommerce/WordPress/PHP
  versions**, and those targets are stated.
- [ ] Text is internationalized (`__()`, `esc_html__()` with the correct text domain) rather
  than hard-coded.
- [ ] Currency and decimals use `wc_price()`, `wc_get_price_decimals()`, and related helpers,
  not hand-rolled formatting.

## Tests

- [ ] The change has automated coverage for the money path (order total, tax, stock, coupon)
  and for the negative cases (invalid input, unauthorized user) (see [testing](21-testing.md)).
- [ ] Behavior was verified under HPOS and, for checkout changes, on the block checkout.

## AI Review Checklist

- Does the diff avoid raw meta/SQL for products and orders, and work under HPOS?
- Is every money value recomputed server-side, and every payment handler idempotent?
- Is each customization a hook rather than a core/template edit an update would revert?
- Does every state change verify a nonce and capability, sanitize input, and escape output?
- Do REST/Store API routes have real permission callbacks and no leaked secrets?
- Are only non-deprecated APIs used against stated version targets, with tests on the money
  and negative paths?

## Related

- `knowledge/woocommerce/29-ai-review.md`
- `knowledge/woocommerce/16-security.md`
- `knowledge/woocommerce/12-hooks.md`
- `knowledge/woocommerce/98-production-checklist.md`
- `knowledge/woocommerce/100-common-antipatterns.md`
