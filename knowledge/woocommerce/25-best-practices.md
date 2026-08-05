---
id: woocommerce/25-best-practices
topic: woocommerce
slug: best-practices
title: "WooCommerce Best Practices"
type: doc
order: 25
status: ready
tags: [woocommerce, best-practices]
related: [woocommerce/12-hooks, woocommerce/16-security, woocommerce/17-customization, woocommerce/15-performance, woocommerce/29-ai-review]
when_to_use: "Read before writing or reviewing any custom WooCommerce plugin, theme, or extension code."
---
# WooCommerce Best Practices

## Purpose

This document defines how to extend WooCommerce so your code survives core and extension
updates, stays secure, and does not corrupt store data. It is the baseline every custom
plugin, theme override, and snippet is held to. Follow these and an upgrade is routine;
ignore them and every `wp plugin update` is a gamble.

## Why It Matters

WooCommerce is a shared, frequently-updated platform: WordPress core, WooCommerce, and
dozens of extensions all run in one PHP process against one database. Code that edits core
files, writes order data with raw SQL, or trusts request input does not just break itself —
it breaks checkout, leaks customer data, or gets silently overwritten on the next update.
The discipline here is what separates a store that ships features from one that firefights
regressions after every release.

## Core Principles

- **Extend through hooks, never edit core.** Every change goes through actions, filters,
  or template overrides in a child theme — never a modified WooCommerce or WordPress file.
- **Use CRUD objects, not the database.** Read and write products, orders, and customers
  through `wc_get_product()`, `wc_get_order()`, and their setters — never direct SQL on
  `wp_posts`/`wp_postmeta`. CRUD is what makes your code HPOS-safe.
- **Never trust input; always escape output.** Sanitize on the way in, escape on the way
  out, verify a nonce and capability on every state change.
- **Declare compatibility explicitly.** Announce HPOS and Cart/Checkout block support so
  the store knows your extension is safe to run.
- **Prefix and namespace everything.** Global functions, hooks, options, and CSS classes
  collide in a shared runtime unless uniquely prefixed.

## Best Practices

- Put customizations in a **plugin or child theme**, not `functions.php` of a parent theme
  that updates. Template changes go in `yourtheme/woocommerce/` overrides.
- Access data via **CRUD getters/setters** and call `$object->save()` once — do not mix
  `update_post_meta()` with CRUD on the same order, which desyncs HPOS tables.
- Guard admin/AJAX actions with `check_admin_referer()` / `wp_verify_nonce()` **and**
  `current_user_can()`. A nonce proves intent; a capability proves permission.
- Sanitize input with the right function (`sanitize_text_field`, `absint`, `wc_clean`) and
  escape output with `esc_html`, `esc_attr`, `esc_url`, or `wp_kses`.
- Load text domains and wrap user-facing strings in `__()`/`esc_html_e()` for i18n.
- Declare feature compatibility in a `before_woocommerce_init` hook so the store does not
  disable your plugin or warn admins.
- Enqueue scripts/styles with `wp_enqueue_*` and a version string; never hardcode `<script>`.
- Version-control the whole site config and pin plugin versions — see
  [deployment](22-deployment.md).

## Examples

**Good Example** — HPOS-safe write, prefixed, capability + nonce checked

```php
// Declare compatibility so the store trusts this plugin under HPOS + block checkout.
add_action( 'before_woocommerce_init', function () {
    if ( class_exists( \Automattic\WooCommerce\Utilities\FeaturesUtil::class ) ) {
        \Automattic\WooCommerce\Utilities\FeaturesUtil::declare_compatibility(
            'custom_order_tables', __FILE__, true
        );
    }
} );

add_action( 'wp_ajax_acme_flag_order', function () {
    check_admin_referer( 'acme_flag_order' );          // proves intent
    if ( ! current_user_can( 'edit_shop_orders' ) ) {  // proves permission
        wp_send_json_error( 'forbidden', 403 );
    }
    $order = wc_get_order( absint( $_POST['order_id'] ?? 0 ) ); // CRUD + sanitized input
    if ( $order ) {
        $order->update_meta_data( '_acme_flagged', 'yes' );
        $order->save();                                 // single save writes HPOS tables
    }
    wp_send_json_success();
} );
```

**Bad Example** — raw SQL, no auth, HPOS-blind

```php
add_action( 'wp_ajax_flag_order', function () {
    global $wpdb;
    // No nonce, no capability check → any logged-in user can flag any order.
    // Raw postmeta write is invisible to HPOS order tables and unsanitized input
    // is a SQL-injection vector.
    $wpdb->query( "UPDATE wp_postmeta SET meta_value='yes'
                   WHERE post_id={$_POST['order_id']} AND meta_key='_flagged'" );
    echo 'ok';
} );
```

## Common Mistakes

- Editing WooCommerce core or parent-theme files; the next update wipes the change.
- Writing order/product data with `update_post_meta()` or raw SQL, breaking HPOS.
- Skipping the nonce *or* the capability check — you need both, for different reasons.
- Unprefixed function/hook/option names that collide with another extension.
- Echoing unescaped data into templates, opening stored XSS.
- Hardcoding `WP_DEBUG`, secret keys, or API tokens in tracked files.
- Not declaring HPOS/block compatibility, so the store disables your plugin.

## Production Tips

- Run PHP_CodeSniffer with the **WordPress + WooCommerce coding standards** in CI to catch
  unescaped output and missing sanitization mechanically.
- Test every custom plugin with **HPOS enabled and a block-based checkout**, since both are
  the default on new stores in 2026.

## AI Review Checklist

- Are all customizations in a plugin/child theme, with zero edits to core files?
- Is order/product/customer data accessed through CRUD objects, not raw SQL or post meta?
- Does every state-changing action verify both a nonce and a capability?
- Is input sanitized and output escaped with the correct WordPress functions?
- Are functions, hooks, and options uniquely prefixed?
- Does the plugin declare HPOS and Cart/Checkout block compatibility?
- Are user-facing strings translatable via a loaded text domain?

## Related

- `knowledge/woocommerce/12-hooks.md`
- `knowledge/woocommerce/16-security.md`
- `knowledge/woocommerce/17-customization.md`
- `knowledge/woocommerce/15-performance.md`
- `knowledge/woocommerce/29-ai-review.md`
