---
id: woocommerce/17-customization
topic: woocommerce
slug: customization
title: "WooCommerce Customization"
type: doc
order: 17
status: ready
tags: [woocommerce, customization, functions.php, add_action, update_post_meta, sanitize_textarea_field, meta, get_meta]
related: [woocommerce/12-hooks, woocommerce/16-security, woocommerce/15-performance, woocommerce/02-installation, woocommerce/100-common-antipatterns]
when_to_use: "Read before overriding templates, adding custom fields, or changing WooCommerce UI/behavior."
---
# WooCommerce Customization

## Purpose

This document defines how to customize WooCommerce's appearance and behavior in a way
that survives updates: template overrides, custom product/checkout fields, custom
functionality, and where that code should live. It is written so an agent can tailor a
store without editing core, breaking on upgrade, or accumulating unmaintainable "just
paste it in `functions.php`" changes.

Customization in WooCommerce has a clear hierarchy: prefer a **hook** (see hooks); if the
markup itself must change, use a **template override** in a child theme; put logic in a
**site-specific plugin**. Editing core is never an option.

## Why It Matters

The tempting shortcuts — edit the core template, pile everything into a parent theme's
`functions.php`, hardcode a field into checkout — all fail the same way: the next
WooCommerce or theme update overwrites them, and the loss is silent until a customer hits
the broken flow. Template overrides carry a second trap: they are *copies* frozen at the
version you copied them, so a security or markup fix in core never reaches them. Doing
customization the supported way is what keeps a store both flexible and updatable.

## Core Principles

- **Hook first, template second.** If you can achieve it with an action/filter, do — it
  is far more update-resilient than copying a template. Override a template only when the
  HTML structure itself must change.
- **Override templates in a child theme, never core.** Copy the file to
  `your-child-theme/woocommerce/<same/path>` so WooCommerce's template loader picks yours
  over core's. Never edit `plugins/woocommerce/templates/`.
- **Keep logic in a site-specific plugin, presentation in the theme.** Business rules
  belong in a plugin so they survive theme switches; markup belongs in the theme.
- **Track the template version.** Each core template has an `@version` header; when core
  bumps it, re-diff and update your override or you drift from upstream fixes.
- **Store custom data as meta, saved through CRUD.** Persist custom fields with
  `update_post_meta`/`WC_Data::update_meta_data` and `->save()`, sanitized on the way in.

## Best Practices

- Reach for the right blocks/tools: for Checkout/Cart blocks use the Store API extension
  hooks and the block registration APIs, not by hacking the legacy shortcode template.
- Copy only the specific template you must change (e.g.
  `woocommerce/single-product/price.php`), keep it minimal, and keep the `@version`
  comment so drift is visible.
- Add custom product fields via `woocommerce_product_options_*` (admin) +
  `woocommerce_process_product_meta` (save) + a display hook (front end) rather than a
  template edit.
- Add checkout fields via the `woocommerce_checkout_fields` filter (or Checkout block
  integration), validate them, and persist to order meta on
  `woocommerce_checkout_update_order_meta`.
- Sanitize on save and escape on render for every custom field — customization is a
  common XSS entry point (see security).
- Enqueue custom CSS/JS with `wp_enqueue_scripts` and a version string; never inline
  `<script>` into templates.

## Examples

**Good Example** — hook-based custom field, sanitized in, escaped out

```php
// Add a "Gift message" field to checkout without touching any template.
add_filter( 'woocommerce_checkout_fields', function ( array $fields ): array {
    $fields['order']['acme_gift_message'] = [
        'type'  => 'textarea',
        'label' => __( 'Gift message', 'acme' ),
        'required' => false,
    ];
    return $fields; // A filter — return the modified value.
} );

// Persist it, sanitized, via order meta (CRUD), not raw SQL.
add_action( 'woocommerce_checkout_update_order_meta', function ( int $order_id ): void {
    $msg = sanitize_textarea_field( wp_unslash( $_POST['acme_gift_message'] ?? '' ) );
    if ( '' !== $msg ) {
        $order = wc_get_order( $order_id );
        $order->update_meta_data( '_acme_gift_message', $msg );
        $order->save();
    }
} );

// Render it on the order page, escaped for context.
add_action( 'woocommerce_order_details_after_order_table', function ( $order ): void {
    $msg = $order->get_meta( '_acme_gift_message' );
    if ( $msg ) {
        printf( '<p><strong>%s:</strong> %s</p>',
            esc_html__( 'Gift message', 'acme' ), esc_html( $msg ) ); // escaped output
    }
} );
```

**Bad Example** — edited core template, unsanitized field, logic in parent theme

```php
// BAD: this HTML was pasted into plugins/woocommerce/templates/checkout/form-checkout.php
// An update overwrites the file and the field vanishes with no error.
?>
<textarea name="acme_gift_message"></textarea>
<?php

// BAD: lives in the PARENT theme's functions.php — lost on theme update, and this
// business logic does not belong in the theme at all.
add_action( 'woocommerce_checkout_update_order_meta', function ( $order_id ) {
    // BAD: unsanitized input written straight to meta → stored XSS on the order screen.
    update_post_meta( $order_id, 'gift', $_POST['acme_gift_message'] );
} );
```

## Common Mistakes

- Editing a core WooCommerce template or the parent theme instead of overriding in a
  child theme / using a hook; lost on update.
- Template overrides with no version tracking, silently drifting from upstream security
  and markup fixes.
- Putting business logic in a theme's `functions.php` so it disappears when the theme
  changes.
- Saving custom field input without sanitizing (stored XSS) or rendering it without
  escaping.
- Overriding an entire large template to change one line, maximizing future merge pain.
- Hacking legacy checkout/cart shortcode templates on a store that uses the Cart/Checkout
  blocks, so the change never renders.

## Production Tips

- Keep a manifest of every template override and its `@version`; on each WooCommerce
  upgrade, re-diff overrides against the new core templates.
- Ship customizations as one versioned site-specific plugin plus a thin child theme, so
  changes are reviewable and reversible in a single deploy.
- Prefer official extension points (Store API, block hooks) over template surgery; they
  are contracts, whereas templates are implementation detail that shifts between releases.

## AI Review Checklist

- Could this be done with a hook instead of a template override? If a template is
  overridden, is it in a child theme (never core) and minimal?
- Does every overridden template carry an `@version` matching (or tracked against) core?
- Is business logic in a site-specific plugin rather than a theme's `functions.php`?
- Are custom fields sanitized on save and escaped on render?
- Is custom data stored as meta via CRUD (`->save()`), not raw SQL?
- On block-based stores, are Checkout/Cart changes made via block/Store API integration
  rather than legacy templates?

## Related

- `knowledge/woocommerce/12-hooks.md`
- `knowledge/woocommerce/16-security.md`
- `knowledge/woocommerce/15-performance.md`
- `knowledge/woocommerce/02-installation.md`
- `knowledge/woocommerce/100-common-antipatterns.md`
