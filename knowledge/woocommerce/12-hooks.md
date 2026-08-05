---
id: woocommerce/12-hooks
topic: woocommerce
slug: hooks
title: "WooCommerce Hooks"
type: doc
order: 12
status: ready
tags: [woocommerce, hooks]
related: [woocommerce/01-architecture, woocommerce/17-customization, woocommerce/15-performance, woocommerce/16-security, woocommerce/100-common-antipatterns]
when_to_use: "Read before adding, filtering, or overriding any WooCommerce behavior with actions or filters."
---
# WooCommerce Hooks

## Purpose

This document defines how to extend WooCommerce through its hook system — **actions**
(do something at a point in time) and **filters** (transform a value and return it).
Hooks are the *only* supported extension point that survives a core or theme update.
It is written so an agent can add behavior without editing core files, breaking on
upgrade, or silently corrupting data.

WooCommerce is built on the WordPress Plugin API. You register a callback against a
named hook; core fires the hook and your callback runs. If you find yourself editing a
file under `wp-content/plugins/woocommerce/`, stop — that is not extension, it is a fork.

## Why It Matters

WooCommerce updates monthly, often with security patches. Any change made by editing
core, a parent theme, or a template in place is erased on the next update — and the
regression is invisible until an order fails or a price renders wrong in production.
Hooks decouple your code from core internals so both can evolve independently. A wrong
hook choice is equally damaging: a filter that forgets to return its value blanks out a
price; an action on the wrong priority runs before the cart exists and reads `null`.

## Core Principles

- **Never edit core or a parent theme.** Register a hook from a child theme's
  `functions.php` or, better, a small site-specific plugin. Only a plugin survives a
  theme switch.
- **A filter must always return a value.** It receives data and must return data —
  ideally the same type. Returning nothing (`null`) destroys the value for every later
  callback.
- **An action returns nothing.** Its job is a side effect (send mail, write a row).
  Do not `echo` from an action that runs during order processing.
- **Priority and argument count are load-bearing.** `add_action($hook, $cb, $priority,
  $args)` — the 4th argument must match how many parameters your callback reads, or
  WordPress passes it fewer than you expect.
- **Prefer WooCommerce hooks over WordPress hooks for commerce data.** Use
  `woocommerce_thankyou`, not a generic `wp_footer`, so you run with the order in scope.

## Best Practices

- Put custom logic in a **site-specific plugin**, not `functions.php`, so it is portable
  across themes and can be version-controlled independently.
- Namespace or prefix every callback function (`acme_recalculate_fee`) to avoid
  collisions; anonymous closures cannot be unhooked, so name callbacks you may remove.
- Always mirror the hook's documented signature. Read `apply_filters()` /
  `do_action()` in core to confirm the exact arguments and their order.
- Remove a core callback with `remove_action`/`remove_filter` using the *same*
  priority it was added with, or the removal silently no-ops.
- Guard against missing context: check `is_admin()`, `wp_doing_ajax()`, or that
  `WC()->cart` exists before touching it.
- Return early and cheaply — hooks like `woocommerce_before_calculate_totals` fire on
  every cart change; expensive work there compounds (see performance).

## Examples

**Good Example** — a filter that transforms and returns, correctly hooked

```php
// In a site-specific plugin. Add a 2% handling fee to the cart.
add_action( 'woocommerce_cart_calculate_fees', 'acme_handling_fee', 20, 1 );
function acme_handling_fee( WC_Cart $cart ): void {
    if ( is_admin() && ! wp_doing_ajax() ) {
        return; // Do not run in admin screens; the cart is not the shopper's cart there.
    }
    $fee = $cart->get_subtotal() * 0.02;
    $cart->add_fee( __( 'Handling', 'acme' ), $fee, true ); // taxable = true
}

// A filter MUST return the (possibly modified) value.
add_filter( 'woocommerce_product_get_price', 'acme_round_price', 10, 2 );
function acme_round_price( $price, WC_Product $product ) {
    if ( '' === $price ) {
        return $price; // Preserve empty prices; do not coerce to 0.
    }
    return round( (float) $price, 2 ); // Always return — later filters depend on it.
}
```

**Bad Example** — edited template, filter with no return, wrong priority

```php
// BAD: this lives in a copied core template file that an update will overwrite.
add_filter( 'woocommerce_product_get_price', function ( $price ) {
    $rounded = round( $price, 2 );
    // BAD: no `return`. The callback returns null, so every product price becomes empty.
} );

// BAD: priority 1 runs before the cart is populated; get_subtotal() reads 0.
add_action( 'woocommerce_cart_calculate_fees', 'acme_fee', 1 );
function acme_fee() {                       // BAD: no $cart arg; reads global state.
    WC()->cart->add_fee( 'Fee', 5 );        // Fires in admin too → corrupts order edits.
}
```

## Common Mistakes

- Editing a core file or parent-theme template instead of hooking; lost on next update.
- A filter callback that does not `return`, wiping the value for all later callbacks.
- Declaring fewer callback parameters than the `$accepted_args` you passed, so expected
  arguments arrive as `null`.
- `remove_action` with a different priority than the original `add_action`, so it does
  nothing.
- Running cart/order logic in `is_admin()` context without guarding, corrupting
  admin-side order edits.
- Using anonymous closures for callbacks you later need to `remove_*` — they have no
  handle to reference.

## Production Tips

- Keep all customizations in one versioned site-specific plugin so a rollback is a
  single deploy, not a scatter of theme edits.
- Log unexpected states inside hooks with `wc_get_logger()` (source-tagged), never
  `error_log` of order data — see security.
- When overriding, prefer the narrowest hook available; broad hooks like
  `template_redirect` invite side effects across unrelated pages.

## AI Review Checklist

- Is the change made via a hook in a plugin/child theme, not by editing core or a parent
  theme?
- Does every filter callback return a value of the expected type on all paths?
- Do `add_action`/`add_filter` priority and `$accepted_args` match the callback's
  signature and the documented hook?
- Does any `remove_*` call use the same priority the callback was added with?
- Is cart/order logic guarded against admin and AJAX contexts where appropriate?
- Are callbacks named and prefixed so they can be unhooked and do not collide?

## Related

- `knowledge/woocommerce/01-architecture.md`
- `knowledge/woocommerce/17-customization.md`
- `knowledge/woocommerce/15-performance.md`
- `knowledge/woocommerce/16-security.md`
- `knowledge/woocommerce/100-common-antipatterns.md`
