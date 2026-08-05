---
id: woocommerce/16-security
topic: woocommerce
slug: security
title: "WooCommerce Security"
type: doc
order: 16
status: ready
tags: [woocommerce, security]
related: [woocommerce/13-rest-api, woocommerce/08-payments, woocommerce/07-checkout, woocommerce/12-hooks, woocommerce/100-common-antipatterns]
when_to_use: "Read before handling any user input, form, AJAX handler, or database query in a WooCommerce store."
---
# WooCommerce Security

## Purpose

This document defines how to write WooCommerce code that resists the attacks a public
store attracts: SQL injection, cross-site scripting (XSS), cross-site request forgery
(CSRF), broken access control, and payment/PII exposure. It is written so an agent can
add forms, AJAX handlers, endpoints, and queries without opening a hole in a
money-handling, PII-holding application.

WordPress and WooCommerce give you the right primitives — nonces, capability checks,
`$wpdb->prepare()`, escaping and sanitizing functions. Security failures are almost
always a *missing* call to one of them, not a missing library.

## Why It Matters

A WooCommerce store holds names, addresses, order history, and a live payment path. A
single unescaped output or unprepared query can dump the customer table or let an
attacker place orders as someone else — and it stays exploitable silently while the store
runs normally. Commerce sites are actively scanned; "it's a small shop" is not
protection. The bar here matches authentication: assume every request parameter, header,
and cookie is hostile until validated.

## Core Principles

- **Sanitize on input, escape on output.** Clean incoming data with the right
  `sanitize_*` function when you receive it; escape with the right `esc_*` function at
  the point you print it. These are two separate duties — do both.
- **Every state-changing request needs a nonce.** Forms and AJAX that write data must
  verify a nonce (`check_admin_referer` / `wp_verify_nonce`) to stop CSRF.
- **Every privileged action needs a capability check.** Gate writes behind
  `current_user_can('edit_shop_orders')` (or the specific cap) — never on role name
  strings or on the mere presence of a logged-in user.
- **Never build SQL by string concatenation.** Use `$wpdb->prepare()` with placeholders,
  or a CRUD query API, for every dynamic query.
- **Keep secrets and PII out of logs and the client.** No API keys, card data, or
  customer records in `error_log`, JS, or committed code.

## Best Practices

- Match the sanitizer to the type: `sanitize_text_field`, `sanitize_email`,
  `absint`, `sanitize_key`, `wc_clean` for WooCommerce input. Validate the *shape*, not
  just the type (e.g. a known set of order statuses).
- Match the escaper to the context: `esc_html` in body text, `esc_attr` in attributes,
  `esc_url` in URLs, `wp_kses_post` where limited HTML is allowed.
- Pair `wp_nonce_field()` in the form with `check_admin_referer()` in the handler; for
  AJAX use `check_ajax_referer()`. A nonce without a matching verification is decoration.
- Enforce authorization on the server for every action, including AJAX and REST — the UI
  hiding a button is not access control.
- Use `$wpdb->prepare( "... WHERE id = %d", $id )` (or `wc_get_orders()` filters) for all
  dynamic queries; never interpolate `$_GET`/`$_POST` into SQL.
- Handle PCI scope by delegating card data to the gateway (tokenization) — never store or
  log PAN/CVV; see payments.
- Force HTTPS site-wide, keep WooCommerce and PHP patched, and log security events with
  `wc_get_logger()` without the sensitive payload.

## Examples

**Good Example** — nonce + capability + sanitize in, prepare, escape out

```php
add_action( 'admin_post_acme_note', 'acme_save_note' );
function acme_save_note(): void {
    // CSRF: reject any request without a valid, matching nonce.
    check_admin_referer( 'acme_note' );
    // AuthZ: server-side capability check, not a role string or "is logged in".
    if ( ! current_user_can( 'edit_shop_orders' ) ) {
        wp_die( 'Forbidden', 403 );
    }

    $order_id = absint( $_POST['order_id'] ?? 0 );          // sanitize input by type
    $note     = sanitize_text_field( wp_unslash( $_POST['note'] ?? '' ) );

    global $wpdb;
    $wpdb->query( $wpdb->prepare(                            // parameterized query
        "UPDATE {$wpdb->prefix}acme_notes SET note = %s WHERE order_id = %d",
        $note, $order_id
    ) );

    printf( '<p>%s</p>', esc_html( $note ) );                // escape at output
}
```

**Bad Example** — no nonce, no cap check, string-built SQL, raw echo

```php
function acme_save_note(): void {
    // BAD: no nonce → any site can forge this request on a logged-in admin's behalf.
    // BAD: no capability check → any authenticated user (even a customer) can call it.

    $order_id = $_POST['order_id'];   // BAD: unsanitized
    $note     = $_POST['note'];

    global $wpdb;
    // BAD: values interpolated straight into SQL → trivial SQL injection.
    $wpdb->query( "UPDATE wp_acme_notes SET note = '$note' WHERE order_id = $order_id" );

    echo $note; // BAD: reflected XSS — attacker's <script> runs in the admin's browser.
}
```

## Common Mistakes

- A form/AJAX write handler with no nonce (CSRF) or no `current_user_can` check (broken
  access control).
- Echoing user or DB data without `esc_html`/`esc_attr`/`esc_url` (XSS).
- Building SQL with string interpolation instead of `$wpdb->prepare()` (SQL injection).
- Trusting the client: hiding a button in JS and assuming the action is protected.
- Logging or storing card data, API keys, or customer PII.
- Relying on role name comparisons instead of capabilities, which breaks with custom
  roles.

## Production Tips

- Run a WAF/edge rules and keep automatic security updates on for WooCommerce and PHP;
  most exploits target known, patched CVEs.
- Audit third-party plugins — they run with full privileges and are the common breach
  vector; remove what you do not use.
- Alert on failed-login and admin-action spikes; keep an off-site, tested backup so a
  compromise is recoverable.

## AI Review Checklist

- Does every state-changing form/AJAX/REST handler verify a nonce?
- Is every privileged action gated by a specific `current_user_can` capability check,
  server-side?
- Is all input sanitized with a type-appropriate `sanitize_*`/`wc_clean` on receipt?
- Is all output escaped with a context-appropriate `esc_*`/`wp_kses_*` at print time?
- Are all dynamic queries built with `$wpdb->prepare()` or a CRUD API, never
  concatenation?
- Is card data, PII, and secret material kept out of logs, client code, and the repo?

## Related

- `knowledge/woocommerce/13-rest-api.md`
- `knowledge/woocommerce/08-payments.md`
- `knowledge/woocommerce/07-checkout.md`
- `knowledge/woocommerce/12-hooks.md`
- `knowledge/woocommerce/100-common-antipatterns.md`
