---
id: wordpress/100-common-antipatterns
topic: wordpress
slug: common-antipatterns
title: "Common WordPress Antipatterns"
type: doc
order: 100
status: ready
tags: [wordpress, common-antipatterns]
related: [wordpress/03-best-practices, wordpress/06-security, wordpress/05-performance, wordpress/99-ai-review-checklist]
when_to_use: "Read before writing WordPress code to avoid common implementation mistakes."
---
# Common WordPress Antipatterns

## Purpose

This document describes the most common engineering mistakes encountered in professional WordPress development.

The objective is to help engineers and AI coding agents recognize poor implementation patterns before they become technical debt.

Every mistake listed here has appeared repeatedly in real production projects.

Avoiding these mistakes improves maintainability, security, performance, and long-term project stability.

---

## Core Principle

Most problems are not caused by writing incorrect code.

They are caused by writing code that ignores the project's architecture.

Always understand the existing system before introducing new code.

---

## Mistake 1 — Creating Instead of Reusing

Before writing new code, search the project.

Look for existing:

- services;
- helper functions;
- React components;
- Gutenberg blocks;
- Divi modules;
- REST endpoints;
- template parts;
- hooks;
- utilities.

Duplicate functionality increases maintenance costs.

---

## Mistake 2 — Business Logic Inside Templates

Templates should display data.

They should not:

- query the database;
- calculate business rules;
- call external APIs;
- modify data;
- perform validation.

Preferred architecture:

```
Template
      ↓
Service
      ↓
Repository
      ↓
WordPress API
```

---

## Mistake 3 — Ignoring Existing Architecture

Projects already have conventions.

Do not introduce:

- new folder structures;
- new architectural patterns;
- alternative dependency systems;
- inconsistent naming;
- different coding styles.

Consistency is more valuable than personal preference.

---

## Mistake 4 — Using Direct SQL Unnecessarily

Prefer WordPress APIs.

Examples:

- WP_Query
- get_posts()
- get_terms()
- get_users()
- Metadata API
- Options API

Use direct SQL only when a measurable benefit exists.

Bad — hand-rolled SQL that also concatenates input, opening an injection hole:

```php
function my_plugin_get_featured_products( $term_id ) {
	global $wpdb;

	// Unnecessary raw SQL AND an unescaped identifier interpolated into the query.
	$results = $wpdb->get_results(
		"SELECT ID FROM {$wpdb->posts} p
		 INNER JOIN {$wpdb->term_relationships} tr ON p.ID = tr.object_id
		 WHERE tr.term_taxonomy_id = " . $term_id . "
		 AND p.post_type = 'product' AND p.post_status = 'publish'"
	);

	return $results;
}
```

Good — the same intent expressed with `WP_Query`, which handles joins, caching, and escaping:

```php
function my_plugin_get_featured_products( $term_id ) {
	$query = new WP_Query(
		array(
			'post_type'      => 'product',
			'post_status'    => 'publish',
			'posts_per_page' => 12,
			'no_found_rows'  => true, // Skip the SQL_CALC_FOUND_ROWS pass when paging is not needed.
			'tax_query'      => array(
				array(
					'taxonomy' => 'product_cat',
					'field'    => 'term_id',
					'terms'    => absint( $term_id ),
				),
			),
		)
	);

	return $query->posts;
}
```

When direct SQL is genuinely required, always pass values through `$wpdb->prepare()`.

Good — a prepared statement with typed placeholders:

```php
function my_plugin_count_recent_orders( $customer_id, $since_gmt ) {
	global $wpdb;

	return (int) $wpdb->get_var(
		$wpdb->prepare(
			"SELECT COUNT(*) FROM {$wpdb->posts}
			 WHERE post_author = %d
			 AND post_type = 'shop_order'
			 AND post_date_gmt >= %s",
			$customer_id,
			$since_gmt
		)
	);
}
```

Table names come from `$wpdb` properties, never from user input. Placeholders are
`%d` (integer), `%f` (float), and `%s` (string) — do not wrap `%s` in your own quotes.

---

## Mistake 5 — Missing Capability Checks

Never assume that hiding a button is sufficient.

Every privileged operation must verify permissions.

Examples:

- admin pages;
- AJAX handlers;
- REST endpoints;
- settings pages;
- file uploads.

Authorization must be enforced on the server.

A frequent mistake is registering a REST route with `'permission_callback' => '__return_true'`
"to make it work," which exposes the endpoint to the entire internet.

Bad — a public, unauthorized write endpoint:

```php
add_action( 'rest_api_init', 'my_plugin_register_routes' );

function my_plugin_register_routes() {
	register_rest_route(
		'my-plugin/v1',
		'/settings',
		array(
			'methods'             => WP_REST_Server::EDITABLE,
			'callback'            => 'my_plugin_update_settings',
			'permission_callback' => '__return_true', // Anyone can POST here.
		)
	);
}
```

Good — the permission callback enforces the capability, and arguments are validated
and sanitized declaratively:

```php
add_action( 'rest_api_init', 'my_plugin_register_routes' );

function my_plugin_register_routes() {
	register_rest_route(
		'my-plugin/v1',
		'/settings',
		array(
			'methods'             => WP_REST_Server::EDITABLE,
			'callback'            => 'my_plugin_update_settings',
			'permission_callback' => function () {
				return current_user_can( 'manage_options' );
			},
			'args'                => array(
				'items_per_page' => array(
					'type'     => 'integer',
					'required' => true,
					'minimum'  => 1,
					'maximum'  => 100,
				),
			),
		)
	);
}

function my_plugin_update_settings( WP_REST_Request $request ) {
	update_option( 'my_plugin_items_per_page', $request['items_per_page'] );

	return rest_ensure_response( array( 'saved' => true ) );
}
```

Declaring `type`, `minimum`, and `maximum` in the schema lets WordPress validate and
sanitize the argument for you before the callback runs — the request is rejected with
a `rest_invalid_param` error if the value is out of range, so `$request['items_per_page']`
is already a bounded integer. Supplying a custom `validate_callback` here would *replace*
this schema check rather than add to it, so prefer schema keywords when they suffice.

---

## Mistake 6 — Skipping Validation

Every external input should be validated.

Examples:

- GET parameters;
- POST requests;
- REST requests;
- uploaded files;
- cookies;
- third-party APIs.

Reject invalid input immediately.

---

## Mistake 7 — Forgetting Sanitization and Escaping

Remember the lifecycle:

```
Input
      ↓
Validation
      ↓
Sanitization
      ↓
Storage
      ↓
Retrieval
      ↓
Escaping
      ↓
Output
```

Never confuse sanitization with escaping. Sanitization cleans data on the way *in*
(before storage); escaping neutralizes data on the way *out*, for the specific
context it is rendered into.

Bad — sanitizing at output time and never escaping, so stored HTML executes in the browser:

```php
function my_plugin_render_greeting() {
	$name = get_option( 'my_plugin_display_name' );

	// Wrong tool, wrong place: this does not make output safe for HTML context.
	echo '<h2>Hello, ' . sanitize_text_field( $name ) . '</h2>';
}
```

Good — sanitize once when saving, then escape for the exact context when printing:

```php
function my_plugin_save_display_name( $raw_name ) {
	update_option( 'my_plugin_display_name', sanitize_text_field( wp_unslash( $raw_name ) ) );
}

function my_plugin_render_greeting() {
	$name = get_option( 'my_plugin_display_name', '' );

	// esc_html() for text nodes, esc_attr() for attributes, esc_url() for URLs.
	printf( '<h2>%s</h2>', esc_html( $name ) );
}
```

Escape at the point of output every time, even for data you sanitized on input —
the two steps defend different boundaries.

---

## Mistake 8 — Large Hook Callbacks

Hook callbacks should remain small.

Preferred flow:

```
Hook
    ↓
Validation
    ↓
Service
    ↓
Return
```

Avoid placing business logic directly inside hooks.

Bad — a monolithic callback wired to `save_post` that runs on every save, revision,
and autosave, mixing guard clauses with business logic:

```php
add_action( 'save_post', 'my_plugin_on_save' );

function my_plugin_on_save( $post_id ) {
	// Recalculates, calls an API, writes meta — all inline, and fires far too often.
	$price   = get_post_meta( $post_id, 'base_price', true );
	$tax     = $price * 0.2;
	$total   = $price + $tax;
	$rate    = wp_remote_get( 'https://api.example.com/fx' );
	// ...dozens more lines...
	update_post_meta( $post_id, 'total_price', $total );
}
```

Good — a thin callback that guards against irrelevant invocations, then delegates.
Note the correct signature for the `save_post_{$post_type}` hook, which passes the
post object:

```php
add_action( 'save_post_product', 'my_plugin_on_product_save', 10, 3 );

function my_plugin_on_product_save( $post_id, $post, $update ) {
	// Skip autosaves and revisions; capability is still required.
	if ( wp_is_post_autosave( $post_id ) || wp_is_post_revision( $post_id ) ) {
		return;
	}

	if ( ! current_user_can( 'edit_post', $post_id ) ) {
		return;
	}

	// Delegate the actual work to a dedicated service.
	( new My_Plugin_Product_Pricing() )->recalculate( $post_id );
}
```

The same discipline applies to filters: a `the_content` or `wp_nav_menu_items`
callback should transform its input and `return` it, not perform side effects.

---

## Mistake 9 — Monolithic Classes

Large classes often violate the Single Responsibility Principle.

Examples of good classes:

- ProductService
- OrderRepository
- ApiController
- UserValidator

Avoid classes that manage unrelated concerns.

---

## Mistake 10 — Ignoring Existing Components

Before creating UI:

Search for:

- buttons;
- cards;
- forms;
- typography;
- layouts;
- icons;
- utility components.

Reuse existing UI whenever possible.

---

## Mistake 11 — Hardcoded Values

Avoid hardcoding:

- colors;
- spacing;
- breakpoints;
- URLs;
- IDs;
- option names;
- API endpoints.

Prefer centralized configuration and design tokens.

Option keys repeated as string literals drift apart over time; a single typo silently
reads a different (empty) option. Define them once.

Bad — an option name typed by hand in several places, and a script enqueued with a
hardcoded version that never busts the browser cache after a deploy:

```php
function my_plugin_enqueue_assets() {
	wp_enqueue_script(
		'my-plugin-app',
		plugins_url( 'assets/app.js', __FILE__ ),
		array( 'wp-element' ),
		'1.0.0', // Stale forever unless a human remembers to bump it.
		true
	);
}
add_action( 'wp_enqueue_scripts', 'my_plugin_enqueue_assets' );
```

Good — the option key is a constant, and the asset version is derived from the file's
modification time so it changes automatically on every build:

```php
const MY_PLUGIN_LAYOUT_OPTION = 'my_plugin_layout';

function my_plugin_enqueue_assets() {
	$path = plugin_dir_path( __FILE__ ) . 'assets/app.js';

	wp_enqueue_script(
		'my-plugin-app',
		plugins_url( 'assets/app.js', __FILE__ ),
		array( 'wp-element' ),
		file_exists( $path ) ? (string) filemtime( $path ) : false,
		array( 'in_footer' => true )
	);

	wp_localize_script(
		'my-plugin-app',
		'myPluginData',
		array( 'layout' => get_option( MY_PLUGIN_LAYOUT_OPTION, 'grid' ) )
	);
}
add_action( 'wp_enqueue_scripts', 'my_plugin_enqueue_assets' );
```

Passing the last argument to `wp_enqueue_script()` as `array( 'in_footer' => true )`
uses the WordPress 6.3+ signature; the older boolean `true` still works. `filemtime()`
is a cheap, reliable cache-busting version during active development.

---

## Mistake 12 — Premature Optimization

Do not optimize code before identifying the bottleneck.

Measure first.

Optimize second.

Keep the implementation readable.

---

## Mistake 13 — Ignoring Performance

Review:

- repeated queries;
- duplicate API requests;
- unnecessary rendering;
- asset loading;
- image optimization;
- cache opportunities.

Performance should be considered throughout development.

---

## Mistake 14 — Weak Naming

Names should describe responsibility.

Good:

```
CustomerRepository

ProductPriceCalculator

NewsletterSubscriptionService
```

Poor:

```
Helper

Utils

Functions

Data

Process
```

Good names reduce documentation requirements.

---

## Mistake 15 — Mixing Responsibilities

Avoid files that:

- render UI;
- perform validation;
- access the database;
- call external APIs;
- implement business rules.

Separate concerns into dedicated layers.

---

## AI Self-Review Checklist

Before finishing implementation verify:

☐ Existing architecture was reviewed.

☐ Existing functionality was reused.

☐ Responsibilities remain separated.

☐ Security checks were implemented.

☐ Validation is complete.

☐ Output is escaped.

☐ Performance was considered.

☐ Naming is descriptive.

☐ Documentation was updated if necessary.

---

## Red Flags

Stop and review the implementation if you notice:

- duplicated code;
- large functions;
- large classes;
- deeply nested conditions;
- repeated database queries;
- business logic inside templates;
- direct SQL;
- hardcoded values;
- missing capability checks;
- inconsistent naming.

These usually indicate architectural issues.

---

## Completion Criteria

An implementation is considered free of common engineering mistakes when:

- existing architecture has been respected;
- duplication has been minimized;
- responsibilities remain clear;
- security has been verified;
- maintainability has been preserved;
- future extension is straightforward.

---

## Summary

Professional WordPress development is largely about avoiding predictable mistakes.

Most technical debt is created through small architectural shortcuts rather than large design failures.

Engineers and AI coding agents should continuously compare new code against these common mistakes before considering a task complete.

## Related

- `knowledge/wordpress/03-best-practices.md`
- `knowledge/wordpress/06-security.md`
- `knowledge/wordpress/05-performance.md`
- `knowledge/wordpress/99-ai-review-checklist.md`
