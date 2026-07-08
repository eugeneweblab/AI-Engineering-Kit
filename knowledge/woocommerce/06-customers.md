---
id: woocommerce/06-customers
topic: woocommerce
slug: customers
title: "Customers"
type: doc
order: 6
status: ready
tags: [woocommerce, customers]
related: [woocommerce/05-orders, woocommerce/07-checkout, woocommerce/13-rest-api, woocommerce/16-security]
when_to_use: "Read before creating, updating, or reading customer records, addresses, or account data in WooCommerce."
---
# Customers

## Purpose

This document defines how to read and write customer data in WooCommerce: the
`WC_Customer` object, registered accounts versus guests, billing and shipping
addresses, and the meta that ties a customer to their orders. It is written so an
agent can manipulate customer records without corrupting data or leaking personal
information.

A WooCommerce "customer" is a WordPress user with the `customer` role plus a layer
of commerce meta (addresses, currency, order history). Guests place orders too, so
"customer" and "user account" are not the same thing — code must handle both.

## Why It Matters

Customer records hold personally identifiable information (PII): names, emails,
physical addresses, and the full purchase history that links them together. Writing
this data with raw `update_user_meta()` or direct SQL bypasses WooCommerce's
validation, caching, and HPOS-aware order lookups, producing addresses that render
on the account page but never reach the order. Reading it carelessly leaks PII into
logs, exports, or REST responses. Because a store's legal exposure (GDPR, CCPA) lives
in exactly this data, customer code is held to a higher bar than ordinary CRUD.

## Core Principles

- **Use the CRUD object, never touch meta directly.** Load `new WC_Customer( $id )`,
  call setters, then `save()`. Direct `update_user_meta()` skips validation and
  invalidates nothing.
- **A guest is a first-class case.** Orders carry their own billing/shipping copy, so
  never assume `get_current_user_id()` is non-zero at checkout.
- **Snapshot address onto the order.** The customer's saved address can change later;
  the order must keep the address as it was at purchase time.
- **PII is need-to-know.** Do not log emails or addresses, and expose customer fields
  through the REST API only with an authenticated, authorized request.
- **Email is the identity key for guests.** Match and merge guest history by email,
  not by user id.

## Best Practices

- Create accounts with `wc_create_new_customer( $email, $username, $password )`, which
  fires the correct hooks and sends the account email. Do not call `wp_insert_user()`
  directly for customers.
- Read and write addresses with `WC_Customer::get_billing()` / `set_billing_*()` and
  `save()`; the setters validate and normalize (e.g. country codes).
- Query customer orders with `wc_get_orders( [ 'customer_id' => $id ] )`, which is
  HPOS-aware. Never `SELECT` from `wp_posts`/`wp_postmeta` — those tables may be empty
  when HPOS is the authoritative store.
- Distinguish account addresses (editable, reusable) from order addresses (immutable
  historical record) in your data model and UI.
- Honor erasure and export: register handlers on the personal-data hooks
  (`woocommerce_privacy_erase_personal_data_*`) rather than deleting rows by hand.
- Deduplicate on normalized, lowercased email before creating a new account.

## Examples

**Good Example** — CRUD object, validated, saved once

```php
$customer = new WC_Customer( $user_id ); // 0 is fine — represents the session guest

$customer->set_billing_first_name( $first );
$customer->set_billing_email( $email );      // setter validates + normalizes
$customer->set_billing_country( 'DE' );      // ISO-2, checked against known list
$customer->set_billing_postcode( $postcode );

$customer->save(); // one write; caches and hooks handled for you

// HPOS-safe history lookup — works whether orders live in posts or the orders table.
$orders = wc_get_orders( [ 'customer_id' => $user_id, 'limit' => 10 ] );
```

**Bad Example** — raw meta and direct SQL

```php
// Skips validation and cache invalidation; the account page and the order disagree.
update_user_meta( $user_id, 'billing_country', $raw ); // unvalidated country string

// Breaks under HPOS: postmeta is not the source of truth for orders.
global $wpdb;
$orders = $wpdb->get_results(
    "SELECT post_id FROM {$wpdb->postmeta}
     WHERE meta_key = '_customer_user' AND meta_value = $user_id" // also SQL-injectable
);
```

## Common Mistakes

- Reading orders from `wp_posts`/`wp_postmeta`, which returns nothing on HPOS stores.
- Assuming a logged-in user at checkout — guest orders have `customer_id = 0`.
- Editing a saved account address and expecting past orders to change (or vice versa).
- Writing `billing_*` with `update_user_meta()`, bypassing country/email validation.
- Creating customers with `wp_insert_user()`, so account emails and hooks never fire.
- Logging or exporting full customer emails and addresses without redaction.
- Deduplicating by exact string instead of normalized, lowercased email.

## Production Tips

- Wrap bulk customer imports in batches and call `save()` per record; a single giant
  transaction blocks other checkouts.
- Add an index-friendly lookup (email) before import loops to avoid O(n²) dedup scans.
- Test both roles in CI: a registered customer and a pure guest going through the same
  code path.

## AI Review Checklist

- Is customer data read/written through `WC_Customer` CRUD, not raw user meta?
- Are order lookups done with `wc_get_orders()` (HPOS-safe), never direct SQL on posts?
- Does the code handle `customer_id = 0` (guest) without erroring?
- Are order addresses treated as immutable snapshots, separate from account addresses?
- Are personal-data erase/export hooks used instead of manual deletes?
- Is PII kept out of logs and gated behind auth on the REST API?

## Related

- `knowledge/woocommerce/05-orders.md`
- `knowledge/woocommerce/07-checkout.md`
- `knowledge/woocommerce/13-rest-api.md`
- `knowledge/woocommerce/16-security.md`
