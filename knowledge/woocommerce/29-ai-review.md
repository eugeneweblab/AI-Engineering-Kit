---
id: woocommerce/29-ai-review
topic: woocommerce
slug: ai-review
title: "AI Review"
type: doc
order: 29
status: ready
tags: [woocommerce, ai-review, WP_Query, get_posts, wc_get_orders, tables, wc_get_product, update_post_meta]
related: [woocommerce/25-best-practices, woocommerce/16-security, woocommerce/05-orders, woocommerce/15-performance, woocommerce/100-common-antipatterns]
when_to_use: "Read before reviewing, or asking an AI agent to review, any WooCommerce plugin, theme, or store customization."
---
# AI Review

## Purpose

This document defines how an AI agent should review WooCommerce code: what to look for, in
what order, and where the platform-specific traps are. WooCommerce reviews fail differently
from generic PHP reviews — the risks are HPOS compatibility, money/inventory correctness,
and data leaks through caching and output. This is the lens to apply before approving a change.

## Why It Matters

An AI reviewer that treats WooCommerce as "just PHP" misses the failures that actually hurt:
a `WP_Query` on orders that silently bypasses HPOS, a checkout hook that blocks on an API,
a missing capability check that lets any user edit any order, an unescaped product attribute
that ships stored XSS. These pass a syntax check and a unit test, then break stores in
production. A review calibrated to WooCommerce catches them before they merge.

## Core Principles

- **Verify HPOS-safety first.** Any order read/write must use CRUD (`wc_get_order`,
  `wc_get_orders`), never `WP_Query`, `get_posts`, or raw SQL on `shop_order`.
- **Check money and inventory for correctness, not just style.** Totals, tax, coupons, and
  stock changes must use WooCommerce APIs; float math and manual stock writes are red flags.
- **Confirm auth on every state change.** Each admin/AJAX/REST write needs a nonce/permission
  check *and* a capability check — see [security](16-security.md).
- **Trace data in and out.** Input sanitized, output escaped, secrets from the environment.
- **Question the request boundary.** Slow or external work in checkout hooks belongs in
  Action Scheduler; flag anything that can make a shopper wait on a third party.

## Best Practices

- Start the review by asking **"is this HPOS-compatible?"** — grep for `WP_Query`,
  `get_posts`, `wp_postmeta`, and `post_type => 'shop_order'` in changed files.
- Check that **compatibility is declared** for `custom_order_tables` and `cart_checkout_blocks`
  when the change is a plugin.
- Verify **CRUD discipline**: no mixing of `update_post_meta()` and order CRUD on the same
  object, and a single `save()`.
- Confirm **escaping and sanitization** on every template output and every request read; flag
  any `echo` of order/customer/product data without `esc_*`.
- Look for **N+1 queries** in loops over products/orders and missing pagination in
  `wc_get_orders()` — link findings to [performance](15-performance.md).
- Ensure **external calls and heavy work are async** and idempotent, not inline in checkout.
- Reject **direct edits** to core, parent themes, or committed secrets.

## Examples

**Good Example** — a review comment that names the platform risk and the fix

```text
BLOCKING — HPOS + auth
File: includes/class-acme-orders.php:42
Issue: `new WP_Query( [ 'post_type' => 'shop_order' ] )` bypasses HPOS and returns
       nothing on stores using custom order tables (the 2026 default). The AJAX
       handler also has no capability check.
Fix:   Use `wc_get_orders( [ 'status' => 'processing', 'limit' => 50, 'paginate' => true ] )`
       and gate the handler with `current_user_can( 'edit_shop_orders' )` + a nonce.
Why:   Order queries must be storage-agnostic, and every write must prove permission.
```

**Bad Example** — a review that only checks generic style

```text
LGTM — code is clean, variables well named, follows PSR-12.
# Misses that the changed loop calls wc_get_product() per line item (N+1),
# writes stock with update_post_meta() (bypasses WC stock + HPOS), and echoes
# $product->get_description() unescaped. Style-only reviews approve broken stores.
```

## Common Mistakes

- Approving order code that uses `WP_Query`/`get_posts`, which returns nothing under HPOS.
- Missing manual stock or total math done outside WooCommerce APIs (drift and race conditions).
- Not flagging a missing capability/nonce check because the code "looks like an internal call".
- Overlooking unescaped output of product, order, or customer fields.
- Ignoring synchronous external calls in checkout hooks that block or lose orders.
- Reviewing only the diff's syntax and style, not its effect on money, stock, and data.
- Passing a plugin that never declares HPOS/block compatibility.

## AI Review Checklist

- Are all order operations CRUD-based and HPOS-safe (no `WP_Query`/`get_posts`/raw SQL)?
- Does the plugin declare HPOS and Cart/Checkout block compatibility?
- Do totals, tax, coupons, and stock changes go through WooCommerce APIs (no float/manual math)?
- Does every state-changing action verify a nonce and a capability?
- Is request input sanitized and all output escaped with the correct functions?
- Are external/slow operations async (Action Scheduler) and idempotent, not inline at checkout?
- Are there N+1 queries or unpaginated order/product loops to flag?
- Are secrets loaded from the environment, with no edits to core or parent themes?

## Related

- `knowledge/woocommerce/25-best-practices.md`
- `knowledge/woocommerce/16-security.md`
- `knowledge/woocommerce/05-orders.md`
- `knowledge/woocommerce/15-performance.md`
- `knowledge/woocommerce/100-common-antipatterns.md`
