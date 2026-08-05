---
id: woocommerce/13-rest-api
topic: woocommerce
slug: rest-api
title: "Rest API"
type: doc
order: 13
status: ready
tags: [woocommerce, rest-api, register_rest_route, WP_Error, permission_callback, WooCommerce, file_get_contents, update_meta_data]
related: [woocommerce/14-headless, woocommerce/16-security, woocommerce/15-performance, woocommerce/05-orders, woocommerce/12-hooks]
when_to_use: "Read before consuming, authenticating to, or extending the WooCommerce REST API."
---
# Rest API

## Purpose

This document defines how to use and extend the WooCommerce REST API — the HTTP
interface (`/wp-json/wc/v3/`) for reading and writing products, orders, customers, and
coupons. It is written so an agent can integrate a client or add a custom endpoint
without leaking credentials, over-fetching, or bypassing WooCommerce's own data layer.

The API is versioned (`wc/v3` is current in 2026). Prefer it over touching the database
directly: it enforces WooCommerce's validation, hooks, and object model. A raw
`INSERT` into `wp_posts` creates an order WooCommerce does not fully recognize.

## Why It Matters

The REST API is a write path into money-moving data. A leaked consumer key with
read/write scope lets an attacker read every customer's address and rewrite order
totals. Meanwhile naive clients page one record at a time or fetch full product objects
to read a single field, hammering a store into timeouts on catalog size that "worked in
dev." Getting authentication, scope, and pagination right is what separates a durable
integration from a support incident.

## Core Principles

- **Authenticate over HTTPS only.** WooCommerce API keys (consumer key/secret) are
  sent as Basic Auth or query params; over plain HTTP they are captured in transit.
- **Grant the least scope.** Create a key with **read** scope for reporting, **write**
  only when the integration must mutate data. Scope is per-key and cannot be widened
  without a new key.
- **Never embed credentials in client-side code.** Browser or mobile apps must call
  your backend, which holds the key — see headless. Keys in a bundle are public.
- **Go through the API or CRUD classes, not raw SQL.** `wc_get_orders()`,
  `WC_Product`, and the REST controllers fire hooks and enforce invariants that direct
  `$wpdb` writes skip.
- **Paginate and select fields.** Every collection endpoint is paginated; treat an
  unbounded fetch as a bug.

## Best Practices

- Generate keys under *WooCommerce → Settings → Advanced → REST API*, tied to a
  dedicated integration user with the minimum WordPress role needed.
- Send keys as Basic Auth (`Authorization` header) over HTTPS; avoid the
  `?consumer_key=&consumer_secret=` form, which lands in access logs.
- Use `per_page` (max 100) with the `X-WP-TotalPages` response header to loop pages;
  never assume the default page size returns everything.
- Request only needed fields with `_fields=id,total,status` to cut payload and DB load.
- Filter server-side (`status`, `after`, `modified_after`) instead of downloading all
  records and filtering in the client.
- Extend with `register_rest_route()` under a **custom namespace** (`acme/v1`), and set a
  real `permission_callback` — never `'__return_true'` on a write route.
- Handle rate limiting and transient 5xx with idempotent retries and backoff; use
  `orders` idempotency by checking an external order key before re-creating.

## Examples

**Good Example** — scoped read, paginated, field-limited; custom route with a permission check

```bash
# Read-only key, HTTPS, only the fields we need, explicit pagination.
curl -s https://shop.example.com/wp-json/wc/v3/orders \
  -u "$CK:$CS" \
  --get \
  --data-urlencode "status=processing" \
  --data-urlencode "after=2026-07-01T00:00:00" \
  --data-urlencode "per_page=100" \
  --data-urlencode "_fields=id,total,status" # small payload, filtered server-side
```

```php
// A custom endpoint that guards writes and delegates to WooCommerce CRUD.
add_action( 'rest_api_init', function () {
    register_rest_route( 'acme/v1', '/orders/(?P<id>\d+)/flag', [
        'methods'             => 'POST',
        'permission_callback' => fn() => current_user_can( 'edit_shop_orders' ), // real check
        'callback'            => function ( WP_REST_Request $req ) {
            $order = wc_get_order( (int) $req['id'] );        // CRUD, not raw SQL
            if ( ! $order ) {
                return new WP_Error( 'not_found', 'No such order', [ 'status' => 404 ] );
            }
            $order->update_meta_data( '_acme_flagged', 'yes' );
            $order->save();                                    // fires hooks, stays consistent
            return rest_ensure_response( [ 'flagged' => true ] );
        },
    ] );
} );
```

**Bad Example** — secrets in the URL, unbounded fetch, open write route

```php
// BAD: consumer secret in the query string is written to every access log.
$all = file_get_contents(
  "https://shop.example.com/wp-json/wc/v3/products?consumer_key=$ck&consumer_secret=$cs"
);
// BAD: no per_page/paging → only the first 10 products; the rest are silently dropped.

register_rest_route( 'acme/v1', '/orders', [
    'methods'             => 'POST',
    'permission_callback' => '__return_true',   // BAD: anyone can create orders
    'callback'            => function ( $req ) {
        global $wpdb;
        $wpdb->insert( 'wp_posts', [ 'post_type' => 'shop_order' ] ); // BAD: raw SQL,
        // no line items, no totals, no hooks → a broken order WooCommerce cannot process.
    },
] );
```

## Common Mistakes

- Passing consumer key/secret as query parameters, leaking them into server logs and
  browser history.
- Creating a read/write key when read would do, widening blast radius on leak.
- Assuming one request returns the whole collection; forgetting pagination truncates
  data silently.
- `permission_callback => '__return_true'` (or omitting it) on a state-changing route.
- Writing orders/products with raw `$wpdb` instead of CRUD, producing objects missing
  line items, taxes, or status transitions.
- Fetching full objects to read one field instead of using `_fields`.

## Production Tips

- Store integration keys in a secrets manager and rotate on staff offboarding; each key
  is independently revocable in the admin.
- Log API errors with correlation IDs; watch for 401 spikes (rotated/leaked key) and
  429s (needing backoff).
- Cache read responses that tolerate staleness (catalog listings) rather than re-hitting
  the API per request — see performance.

## AI Review Checklist

- Are credentials sent via HTTPS and Basic Auth header, never in the query string or
  client bundle?
- Is the API key scoped to the minimum (read vs write) the integration needs?
- Does every collection call paginate and, where possible, use `_fields` and
  server-side filters?
- Does every custom write route set a real `permission_callback`?
- Do custom endpoints use `wc_get_order()`/CRUD classes rather than raw `$wpdb`?
- Are transient failures retried idempotently so orders are not duplicated?

## Related

- `knowledge/woocommerce/14-headless.md`
- `knowledge/woocommerce/16-security.md`
- `knowledge/woocommerce/15-performance.md`
- `knowledge/woocommerce/05-orders.md`
- `knowledge/woocommerce/12-hooks.md`
