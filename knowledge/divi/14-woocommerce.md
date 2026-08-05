---
id: divi/14-woocommerce
topic: divi
slug: woocommerce
title: "WooCommerce"
type: doc
order: 14
status: ready
tags: [divi, woocommerce, WooCommerce, woocommerce_checkout_fields, add_filter]
related: [divi/02-theme-builder, divi/07-dynamic-content, divi/03-modules, divi/10-performance, divi/19-security]
when_to_use: "Read before building or reviewing a Divi store: product, shop, cart, or checkout templates."
---
# WooCommerce

## Purpose

This document defines how to build a **WooCommerce** store inside **Divi** correctly: using
Divi's WooCommerce modules and the Theme Builder to template product, shop, cart, and
checkout pages without breaking WooCommerce's own logic. It is written so an agent can build
or review a store without introducing the two classic Divi-commerce failures — duplicated or
missing WooCommerce hooks, and a customized checkout that no longer converts.

Divi ships **WooCommerce modules** (Product Title, Price, Add to Cart, Tabs, Related Products,
etc.) and lets you template store pages in the Theme Builder. These modules are wrappers
around WooCommerce template functions and hooks. Respecting that boundary is the whole job:
Divi controls layout; WooCommerce controls commerce.

## Why It Matters

Checkout and cart are the revenue-critical path, and they are the easiest thing to break in a
visual builder. WooCommerce renders those pages through a chain of hooks (`woocommerce_checkout_*`,
`woocommerce_after_cart`, etc.); when you rebuild a checkout with generic Divi modules instead of
the WooCommerce checkout module, you can drop the fields, notices, or payment hooks that WooCommerce
depends on — producing a checkout that looks polished but silently fails validation or payment. Divi
templating a store also multiplies performance and PCI concerns: every extra module on a product page
is weight on a page a shopper must load before buying, and any tampering with the checkout form is a
compliance risk. Getting the architecture right protects both conversions and legal standing.

## Core Principles

- **WooCommerce owns commerce logic; Divi owns layout.** Never replace the cart/checkout form
  with hand-built inputs — use the WooCommerce Cart/Checkout modules so all hooks fire.
- **Template with the Theme Builder, per template type.** Assign a template to *All Product
  Pages*, *Shop*, *Cart*, *Checkout* — not by editing individual product posts.
- **Keep the hook chain intact.** WooCommerce fires ordered actions on store pages; do not
  remove default modules that stand in for required hooks, and do not double-render them.
- **Dynamic data, never hard-coded.** Price, stock, SKU, and gallery come from the product via
  [dynamic content](07-dynamic-content.md), so they stay correct as inventory changes.
- **Test the money path.** A store is not done until a real end-to-end test order — add to cart,
  checkout, pay, order-received — succeeds in a sandbox.

## Best Practices

- Build store pages as Theme Builder templates. For a product template, place the Divi
  WooCommerce modules (Title, Images, Price, Add to Cart, Description Tabs) that map to the
  standard product layout; do not scatter generic Text modules with pasted prices.
- Bind product data dynamically. Use the WooCommerce modules or dynamic content so `Product
  Price` reflects sales, tax, and currency logic — never type a price into a Text module.
- Leave the Checkout and Cart modules doing their own rendering. Restyle with the Design tab
  and CSS; do not remove or reorder the underlying WooCommerce form fields.
- Add custom checkout behavior through WooCommerce hooks in a child theme (`woocommerce_checkout_fields`,
  `woocommerce_after_order_notes`), not by injecting inputs via a Code module.
- Load only the product-relevant modules; keep product templates lean for LCP, since these
  are the highest-traffic conversion pages. See [performance](10-performance.md).
- Keep WooCommerce, Divi, and payment gateway plugins updated together and test after each
  update — a Divi update can shift WooCommerce module output.

## Examples

**Good Example** — extend checkout via the WooCommerce hook, form stays intact

```php
// child theme functions.php — add a field through WooCommerce's own API so
// validation, order meta, and the payment flow keep working.
add_filter( 'woocommerce_checkout_fields', function ( $fields ) {
    $fields['billing']['billing_vat'] = [
        'label'    => 'VAT number',
        'required' => false,
        'class'    => [ 'form-row-wide' ],
    ];
    return $fields; // WooCommerce renders and persists it in the real checkout form
} );
```

**Bad Example** — hand-built checkout that bypasses WooCommerce

```html
<!-- Divi Code/Contact Form module faking a checkout: none of WooCommerce's
     validation, tax, shipping, or payment hooks run. Orders never complete. -->
<form action="/thank-you" method="post">
  <input name="card" placeholder="Card number">   <!-- raw PCI data, no gateway -->
  <input name="total" value="49.00">              <!-- price hard-coded, editable -->
  <button>Pay</button>
</form>
```

## Common Mistakes

- Rebuilding cart/checkout with generic modules, dropping WooCommerce's required hooks/fields.
- Hard-coding prices or stock in Text modules, so they drift from actual product data.
- Adding checkout fields via a Code module instead of `woocommerce_checkout_fields`, so the
  data is never validated or saved to the order.
- Collecting payment details in a custom form instead of the gateway's checkout, a PCI breach.
- Overloading product templates with heavy modules, hurting LCP on the pages that must convert.
- Editing WooCommerce template files in the Divi parent theme instead of overriding correctly.
- Shipping without a real sandbox test order, so a broken payment path reaches production.

## Production Tips

- Run a full sandbox order after every Divi/Woo/gateway update; automate a smoke test of
  add-to-cart → checkout → order-received if possible.
- Keep tax, shipping, and currency logic in WooCommerce settings, not in Divi — Divi should
  only display the computed values.
- Monitor checkout errors and abandoned carts; a sudden spike usually means a template or
  plugin update broke a hook.

## AI Review Checklist

- Are cart and checkout rendered by the WooCommerce modules, with all fields/hooks intact?
- Are store pages templated in the Theme Builder by template type, not per product post?
- Do price, stock, and SKU come from dynamic product data, never hard-coded?
- Are checkout customizations done via WooCommerce hooks in a child theme?
- Is payment handled only by the gateway, with no card data in custom forms (PCI)?
- Are product templates lean enough to pass Core Web Vitals?
- Has a real end-to-end sandbox order been tested after the latest updates?

## Related

- `knowledge/divi/02-theme-builder.md`
- `knowledge/divi/07-dynamic-content.md`
- `knowledge/divi/03-modules.md`
- `knowledge/divi/10-performance.md`
- `knowledge/divi/19-security.md`
