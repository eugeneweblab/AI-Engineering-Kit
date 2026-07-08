---
id: wordpress/04-code-style
topic: wordpress
slug: code-style
title: "WordPress Code Style"
type: doc
order: 4
status: ready
tags: [wordpress, code-style]
related: []
when_to_use: "Read before writing or formatting WordPress code to match the project's coding style."
---
# WordPress Code Style

## Purpose

This document defines the coding style for WordPress projects.

The goal is to produce code that is easy to read, easy to review, and consistent across the entire codebase.

Code style is not about personal preference.

It is about reducing cognitive load for every engineer who works on the project.

---

## Core Principle

Optimize code for readability.

Code is read far more often than it is written.

Choose clarity over cleverness.

---

## General Rules

Every piece of code should be:

- readable;
- predictable;
- consistent;
- explicit;
- maintainable.

Avoid writing code that requires additional explanation.

---

## Follow Existing Conventions

Before writing code:

- review surrounding files;
- identify naming conventions;
- identify formatting conventions;
- identify architectural patterns.

Match the existing project instead of introducing a personal style.

---

## Naming

Names should describe intent.

The WordPress Coding Standards (WPCS, enforced by PHPCS) require `snake_case` for all variable names. Use lowercase words separated by underscores.

Good examples:

```php
$product_service

$user_repository

$newsletter_settings

$is_user_authorized

$should_display_banner
```

Bad examples:

```php
$data

$tmp

$obj

$helper

$newData

$value2
```

If a name needs a comment to explain it, choose a better name.

### Prefix Global Symbols

WordPress loads every active plugin and theme into one shared global namespace. Procedural functions, hook callbacks, option keys, and custom post type slugs must carry a unique prefix (or live inside a namespaced class) to avoid collisions with core, other plugins, or the theme.

Good:

```php
function acme_register_book_post_type() {
    // ...
}
add_action( 'init', 'acme_register_book_post_type' );

update_option( 'acme_newsletter_settings', $settings );
```

Bad:

```php
// `register` and `settings` will eventually collide with another plugin.
function register() {
    // ...
}
add_action( 'init', 'register' );

update_option( 'settings', $settings );
```

---

## Functions

Functions should:

- perform one responsibility;
- have descriptive names;
- minimize side effects;
- return predictable values.

The WordPress Coding Standards (WPCS, enforced by PHPCS) require `snake_case` for function names. Use lowercase words separated by underscores.

Prefer:

```php
get_user_profile()

update_product_price()

calculate_discount()

send_newsletter()
```

Avoid:

```php
process()

execute()

run()

handleEverything()
```

A well-named callback reads as a single responsibility even at the point where it is hooked. Prefer wiring a descriptive function to a hook over an anonymous closure that hides its intent and cannot be unhooked later.

Good:

```php
function acme_flush_product_cache( $post_id ) {
    delete_transient( 'acme_product_' . $post_id );
}
add_action( 'save_post_product', 'acme_flush_product_cache' );
```

Bad:

```php
add_action(
    'save_post_product',
    function ( $post_id ) {
        delete_transient( 'acme_product_' . $post_id );
    }
);
```

---

## Classes

Each class should have a single responsibility.

The following `PascalCase` names apply to namespaced, PSR-style OOP code (e.g. autoloaded plugin classes). Legacy procedural WordPress core still uses `Class_Name` (capitalized words joined by underscores) per WPCS. Procedural functions, template code, and variables remain `snake_case`.

Examples:

```text
ProductService

OrderRepository

UserValidator

ApiController

ImageUploader
```

Avoid classes that combine unrelated responsibilities.

---

## Methods

Methods should be:

- short;
- descriptive;
- cohesive;
- easy to test.

Large methods usually indicate missing abstractions.

---

## Conditionals

Prefer:

```php
if ( ! $user ) {
    return;
}
```

Over:

```php
if ( $user ) {
    // 100 lines of code
}
```

Use early returns to reduce nesting.

### Yoda Conditions

WPCS requires Yoda conditions: when comparing a variable to a literal, put the literal on the left. If you accidentally type `=` instead of `==`, assigning to a literal is a fatal parse error, so the mistake is caught immediately instead of silently passing.

Good:

```php
if ( 'publish' === get_post_status( $post_id ) ) {
    acme_notify_subscribers( $post_id );
}

if ( true === $is_featured ) {
    // ...
}
```

Bad:

```php
if ( get_post_status( $post_id ) == 'publish' ) {
    acme_notify_subscribers( $post_id );
}

if ( $is_featured == true ) {
    // ...
}
```

Yoda conditions apply to equality checks. Do not force them onto `<`, `>`, or expressions that read unnaturally reversed.

---

## Nesting

Avoid deeply nested code.

Prefer:

```text
Validate

↓

Return early

↓

Continue
```

Instead of multiple nested `if` statements.

---

## Comments

Write comments only when they explain **why**, not **what**.

Good:

```php
// Required because the external API returns inconsistent IDs.
```

Poor:

```php
// Increment counter.
$counter++;
```

Well-written code should explain itself.

---

## Constants

Avoid magic values.

Prefer:

```php
const MAX_UPLOAD_SIZE = 10 * MB_IN_BYTES;
```

Instead of:

```php
10485760
```

Named constants improve readability.

---

## Arrays

Prefer meaningful keys.

Example:

```php
[
    'title' => 'Product',
    'price' => 100,
    'currency' => 'USD',
]
```

Avoid arrays whose meaning depends on element order.

WordPress passes configuration through associative arrays constantly (`WP_Query`, `register_post_type`, `wp_insert_post`). Use the short array syntax `[]`, one element per line for multi-line arrays, and align the `=>` operators for readability. Every element gets a trailing comma so future diffs touch only the line that changed.

Good:

```php
$query = new WP_Query(
    [
        'post_type'      => 'product',
        'post_status'    => 'publish',
        'posts_per_page' => 12,
        'orderby'        => 'date',
        'order'          => 'DESC',
    ]
);
```

Bad:

```php
$query = new WP_Query( array( 'product', 'publish', 12, 'date', 'DESC' ) );
```

---

## Hooks

Keep callbacks lightweight.

Preferred flow:

```text
Hook

↓

Validation

↓

Service

↓

Return
```

Business logic belongs in services.

Register callbacks against real core hooks and remember that `add_filter` callbacks must **return** the value they receive, while `add_action` callbacks return nothing. Declare the accepted-argument count (the fourth argument) whenever a callback needs more than one parameter.

Good:

```php
// A filter transforms and returns a value.
function acme_extend_excerpt_length( $length ) {
    return 40;
}
add_filter( 'excerpt_length', 'acme_extend_excerpt_length' );

// An action delegates to a service and returns nothing.
// transition_post_status passes ( $new_status, $old_status, $post ) in that order.
function acme_sync_order_on_status_change( $new_status, $old_status, $post ) {
    ( new Acme\Orders\Order_Sync() )->handle( $post->ID, $new_status );
}
add_action( 'transition_post_status', 'acme_sync_order_on_status_change', 10, 3 );
```

Bad:

```php
// Filter callback with no return silently blanks the excerpt.
function acme_extend_excerpt_length( $length ) {
    40;
}
add_filter( 'excerpt_length', 'acme_extend_excerpt_length' );

// Missing accepted-args count: $old_status and $post arrive as null.
add_action( 'transition_post_status', 'acme_sync_order_on_status_change' );
```

---

## Templates

Templates should:

- render data;
- include template parts;
- call helper methods.

Templates should not:

- query the database;
- implement business logic;
- contain complex calculations.

Escape every dynamic value at the point of output, and pick the escaping function that matches the context: `esc_html()` for text, `esc_attr()` for attribute values, `esc_url()` for links, and `wp_kses_post()` when a limited set of HTML is intentionally allowed. Translated strings use the `esc_html__()` / `esc_attr__()` family so the translation is escaped too.

Good:

```php
<article class="acme-card">
    <a href="<?php echo esc_url( get_permalink() ); ?>">
        <h2><?php echo esc_html( get_the_title() ); ?></h2>
    </a>
    <div class="acme-card__body">
        <?php echo wp_kses_post( get_the_content() ); ?>
    </div>
</article>
```

Bad:

```php
<article class="acme-card">
    <a href="<?php echo get_permalink(); ?>">
        <h2><?php echo get_the_title(); ?></h2>
    </a>
    <div class="acme-card__body">
        <?php echo get_the_content(); ?>
    </div>
</article>
```

When a template accepts user-submitted input via a form, print a nonce field on output and verify it before acting on the submission.

Good:

```php
<form method="post" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>">
    <input type="hidden" name="action" value="acme_save_profile">
    <?php wp_nonce_field( 'acme_save_profile', 'acme_profile_nonce' ); ?>
    <input type="text" name="display_name" value="<?php echo esc_attr( $display_name ); ?>">
    <button type="submit"><?php esc_html_e( 'Save', 'acme' ); ?></button>
</form>
```

```php
function acme_handle_save_profile() {
    if ( ! isset( $_POST['acme_profile_nonce'] )
        || ! wp_verify_nonce( sanitize_key( $_POST['acme_profile_nonce'] ), 'acme_save_profile' )
    ) {
        wp_die( esc_html__( 'Invalid request.', 'acme' ) );
    }

    $display_name = sanitize_text_field( wp_unslash( $_POST['display_name'] ?? '' ) );
    update_user_meta( get_current_user_id(), 'acme_display_name', $display_name );
}
add_action( 'admin_post_acme_save_profile', 'acme_handle_save_profile' );
```

---

## REST Controllers

Controllers should:

- validate requests;
- authorize users;
- call services;
- format responses.

Avoid embedding business logic inside controllers.

Register routes on the `rest_api_init` hook. Always supply a `permission_callback` (returning `true` is an explicit, reviewable decision; omitting it is a hard error in WordPress 6.x), and declare an `args` schema so the framework sanitizes and validates input before your callback runs.

Good:

```php
function acme_register_rest_routes() {
    register_rest_route(
        'acme/v1',
        '/products/(?P<id>\d+)',
        [
            'methods'             => WP_REST_Server::READABLE,
            'callback'            => 'acme_get_product',
            'permission_callback' => function () {
                return current_user_can( 'read' );
            },
            'args'                => [
                'id' => [
                    'required'          => true,
                    'validate_callback' => static function ( $value ) {
                        return is_numeric( $value );
                    },
                    'sanitize_callback' => 'absint',
                ],
            ],
        ]
    );
}
add_action( 'rest_api_init', 'acme_register_rest_routes' );

function acme_get_product( WP_REST_Request $request ) {
    $product = get_post( $request['id'] );

    if ( null === $product || 'product' !== $product->post_type ) {
        return new WP_Error( 'acme_not_found', 'Product not found.', [ 'status' => 404 ] );
    }

    return rest_ensure_response(
        [
            'id'    => $product->ID,
            'title' => get_the_title( $product ),
        ]
    );
}
```

Bad:

```php
// No permission_callback (fatal in 6.x), raw $_GET, no sanitization.
register_rest_route(
    'acme/v1',
    '/products',
    [
        'methods'  => 'GET',
        'callback' => function () {
            return get_post( $_GET['id'] );
        },
    ]
);
```

---

## Database Access

Prefer the high-level APIs (`WP_Query`, `get_posts`, `get_option`, `get_user_meta`) over raw SQL. When a custom query is genuinely required, go through `$wpdb` and **always** build the statement with `$wpdb->prepare()`. Never interpolate variables straight into SQL. Reference table names through `$wpdb` properties (`$wpdb->posts`, `$wpdb->prefix`) rather than hard-coded strings so the code respects custom table prefixes.

Good:

```php
global $wpdb;

$product_id = absint( $product_id );

$row = $wpdb->get_row(
    $wpdb->prepare(
        "SELECT * FROM {$wpdb->posts} WHERE ID = %d AND post_type = %s",
        $product_id,
        'product'
    )
);
```

Bad:

```php
global $wpdb;

// String interpolation is a SQL injection vector.
$row = $wpdb->get_row(
    "SELECT * FROM wp_posts WHERE ID = $product_id AND post_type = 'product'"
);
```

Store and read settings through the options API instead of ad-hoc queries. Cast on the way in and provide a sensible default on the way out.

Good:

```php
update_option( 'acme_items_per_page', absint( $items_per_page ) );

$items_per_page = (int) get_option( 'acme_items_per_page', 12 );
```

---

## Error Handling

Handle expected failures explicitly.

Prefer:

- early validation;
- meaningful exceptions;
- descriptive error messages;
- predictable return values.

Avoid silent failures.

Many core functions signal failure by returning `WP_Error` (or `false`/`0`). Check the return value with `is_wp_error()` before using it, and return `WP_Error` from your own functions when a caller needs to distinguish failure modes.

Good:

```php
$post_id = wp_insert_post( $postarr, true );

if ( is_wp_error( $post_id ) ) {
    return $post_id;
}

update_post_meta( $post_id, 'acme_source', 'import' );
```

Bad:

```php
// wp_insert_post can return 0 or a WP_Error; this treats it as a valid ID.
$post_id = wp_insert_post( $postarr );
update_post_meta( $post_id, 'acme_source', 'import' );
```

---

## Formatting

Maintain consistency.

Examples:

- consistent indentation;
- consistent spacing;
- consistent import ordering;
- consistent file organization.

Formatting should never distract from the code.

WPCS formats function calls with a space just inside the parentheses and after each comma. Named arguments like the dependency array and version keep asset registration self-documenting. Enqueue assets on the appropriate hook (`wp_enqueue_scripts` for the front end, `admin_enqueue_scripts` for the admin) rather than printing tags directly.

Good:

```php
function acme_enqueue_assets() {
    wp_enqueue_style(
        'acme-app',
        get_theme_file_uri( 'assets/css/app.css' ),
        [],
        '1.4.0'
    );

    wp_enqueue_script(
        'acme-app',
        get_theme_file_uri( 'assets/js/app.js' ),
        [ 'wp-element' ],
        '1.4.0',
        true
    );
}
add_action( 'wp_enqueue_scripts', 'acme_enqueue_assets' );
```

Bad:

```php
// Hard-coded tag, no dependency/version handling, wrong place.
function acme_enqueue_assets() {
    echo '<script src="/wp-content/themes/acme/assets/js/app.js"></script>';
}
add_action( 'wp_head', 'acme_enqueue_assets' );
```

---

## AI Execution Checklist

## Investigation

☐ Review nearby files.

☐ Identify naming conventions.

☐ Review project formatting.

☐ Review architecture.

---

## Implementation

☐ Use descriptive names.

☐ Keep functions small.

☐ Use early returns.

☐ Minimize nesting.

☐ Avoid duplicate logic.

☐ Separate responsibilities.

---

## Verification

☐ Review readability.

☐ Review consistency.

☐ Review maintainability.

☐ Review naming.

☐ Remove unnecessary comments.

---

## Common Mistakes

Avoid:

Generic variable names.

Large methods.

Large classes.

Deep nesting.

Magic numbers.

Business logic inside templates.

Business logic inside hooks.

Inconsistent formatting.

Excessive comments.

---

## Completion Criteria

Code style is considered successful when:

- another engineer can understand the code without explanation;
- naming is descriptive;
- responsibilities are clear;
- formatting is consistent;
- architecture is respected;
- maintenance is straightforward.

---

## Summary

Good code style is invisible.

It allows engineers to focus on solving business problems instead of decoding implementation details.

Consistency across the project is more valuable than individual coding preferences.