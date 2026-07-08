---
id: wordpress/03-best-practices
topic: wordpress
slug: best-practices
title: "WordPress Best Practices"
type: doc
order: 3
status: ready
tags: [wordpress, best-practices]
related: []
when_to_use: "Read before writing WordPress code to follow professional engineering best practices."
---
# WordPress Best Practices

## Purpose

This document defines the engineering best practices for developing professional WordPress applications.

These principles apply to themes, plugins, headless WordPress projects, WooCommerce stores, Gutenberg blocks, Divi modules, REST APIs, and enterprise WordPress solutions.

The objective is to create maintainable, secure, scalable, and predictable software that integrates naturally with the WordPress ecosystem.

---

## Core Philosophy

Write code that another engineer can confidently modify two years from now.

Every implementation should optimize for:

- readability;
- maintainability;
- scalability;
- consistency;
- security;
- performance.

The best implementation is usually the simplest one that satisfies the requirements.

---

## Design Before Coding

Never begin implementation immediately.

Before writing code:

- understand the business requirements;
- review the existing architecture;
- search for reusable functionality;
- identify integration points;
- define an implementation plan.

Planning reduces bugs and unnecessary refactoring.

---

## Reuse Before Creating

Always search the project before creating:

- services;
- helper functions;
- components;
- hooks;
- REST endpoints;
- templates;
- block controls;
- Divi modules.

Duplicate code increases maintenance costs.

---

## Follow WordPress APIs

Prefer WordPress APIs over custom implementations.

Examples:

- REST API
- Settings API
- Options API
- Metadata API
- Transients API
- WP_Query
- WP_Filesystem
- WP_Cron

Using established APIs improves compatibility and future upgrades.

Register content with the core APIs instead of writing to the database directly. A custom post type belongs on the `init` hook so it is available for every request:

```php
add_action( 'init', 'acme_register_book_post_type' );

function acme_register_book_post_type() {
	register_post_type(
		'acme_book',
		array(
			'labels'       => array(
				'name'          => __( 'Books', 'acme' ),
				'singular_name' => __( 'Book', 'acme' ),
			),
			'public'       => true,
			'has_archive'  => true,
			'show_in_rest' => true, // Required for the block editor and REST API.
			'supports'     => array( 'title', 'editor', 'thumbnail', 'custom-fields' ),
			'rewrite'      => array( 'slug' => 'books' ),
		)
	);
}
```

Query content with `WP_Query` rather than raw SQL. Always reset global post state after a custom loop:

```php
function acme_get_recent_books( $limit = 5 ) {
	$query = new WP_Query(
		array(
			'post_type'              => 'acme_book',
			'post_status'            => 'publish',
			'posts_per_page'         => $limit,
			'no_found_rows'          => true,  // Skip the SQL_CALC_FOUND_ROWS pagination count.
			'update_post_meta_cache' => false, // Skip meta cache when meta is not used.
		)
	);

	return $query->posts;
}
```

When you must query the database directly, always use `$wpdb->prepare` to parameterize values. Never concatenate variables into SQL.

```php
// Bad: variable interpolated straight into the query (SQL injection risk).
global $wpdb;
$results = $wpdb->get_results( "SELECT * FROM {$wpdb->posts} WHERE post_author = $author_id" );

// Good: %d placeholder bound through prepare().
global $wpdb;
$results = $wpdb->get_results(
	$wpdb->prepare(
		"SELECT ID, post_title FROM {$wpdb->posts} WHERE post_author = %d AND post_status = %s",
		$author_id,
		'publish'
	)
);
```

---

## Keep Business Logic Separate

Business logic should never be embedded inside:

- templates;
- block rendering files;
- shortcode callbacks;
- REST controllers;
- hook callbacks.

Business rules belong inside dedicated services.

The hook callback should stay thin: parse the request, delegate to a service, shape the response.

```php
// Bad: business logic, persistence, and formatting crammed into the callback.
add_action( 'save_post_acme_book', 'acme_on_save_book' );

function acme_on_save_book( $post_id ) {
	$isbn = $_POST['isbn'];
	if ( strlen( $isbn ) === 13 && ctype_digit( $isbn ) ) {
		update_post_meta( $post_id, 'isbn', $isbn );
		wp_remote_post( 'https://api.example.com/index', array( 'body' => array( 'isbn' => $isbn ) ) );
	}
}
```

```php
// Good: the callback validates and delegates; the service owns the rules.
add_action( 'save_post_acme_book', 'acme_on_save_book', 10, 2 );

function acme_on_save_book( $post_id, $post ) {
	if ( wp_is_post_autosave( $post_id ) || wp_is_post_revision( $post_id ) ) {
		return;
	}

	if ( ! isset( $_POST['acme_book_nonce'] )
		|| ! wp_verify_nonce( sanitize_key( $_POST['acme_book_nonce'] ), 'acme_save_book' ) ) {
		return;
	}

	if ( ! current_user_can( 'edit_post', $post_id ) ) {
		return;
	}

	$isbn = isset( $_POST['isbn'] ) ? sanitize_text_field( wp_unslash( $_POST['isbn'] ) ) : '';

	( new Acme_Book_Service() )->update_isbn( $post_id, $isbn );
}
```

---

## Write Small Functions

Functions should perform one responsibility.

Good characteristics:

- descriptive name;
- predictable behavior;
- minimal side effects;
- reusable;
- easy to test.

Large functions usually indicate multiple responsibilities.

---

## Keep Templates Simple

Templates should focus on presentation.

Templates may:

- display data;
- call helper methods;
- render components.

Templates should not:

- perform database queries;
- implement business rules;
- contain complex conditional logic.

---

## Respect Existing Architecture

Do not introduce new architectural patterns unless explicitly required.

Follow:

- existing folder structure;
- naming conventions;
- dependency direction;
- coding style;
- service organization.

Consistency is more valuable than personal preference.

---

## Validate, Sanitize, Escape

Every feature should follow three rules:

Validate input.

Sanitize stored data.

Escape rendered output.

Never assume external data is safe.

Sanitize on the way in with the `sanitize_*` family; escape on the way out with the `esc_*` family. Unslash superglobals first, because WordPress adds slashes to `$_POST`, `$_GET`, and `$_REQUEST`.

```php
// Bad: raw request data stored and echoed without sanitization or escaping.
update_option( 'acme_contact_email', $_POST['contact_email'] );
echo '<a href="' . get_option( 'acme_contact_email' ) . '">Email us</a>';
```

```php
// Good: sanitize before storing, escape at the point of output.
$email = sanitize_email( wp_unslash( $_POST['contact_email'] ) );

if ( is_email( $email ) ) {
	update_option( 'acme_contact_email', $email );
}

printf(
	'<a href="%s">%s</a>',
	esc_url( 'mailto:' . get_option( 'acme_contact_email' ) ),
	esc_html__( 'Email us', 'acme' )
);
```

Match the escaping function to the output context: `esc_html()` inside element text, `esc_attr()` inside HTML attributes, `esc_url()` for URLs, and `wp_kses_post()` when a limited set of HTML must survive.

```php
$classes = 'card card--' . sanitize_html_class( $variant );

printf(
	'<div class="%s"><h2>%s</h2>%s</div>',
	esc_attr( $classes ),
	esc_html( $title ),
	wp_kses_post( $rich_text )
);
```

---

## Capability Checks

Administrative functionality should always verify user permissions.

Examples:

- current_user_can()
- capability mapping
- REST permission callbacks

Never rely solely on hidden UI elements.

Every custom REST route needs a `permission_callback`. Registering a route without one is a hard error in WordPress 5.5+ and leaves the endpoint open. Combine capability checks with argument validation and sanitization.

```php
add_action( 'rest_api_init', 'acme_register_book_routes' );

function acme_register_book_routes() {
	register_rest_route(
		'acme/v1',
		'/books/(?P<id>\d+)',
		array(
			'methods'             => WP_REST_Server::EDITABLE, // POST, PUT, PATCH.
			'callback'            => 'acme_update_book_rating',
			'permission_callback' => function ( WP_REST_Request $request ) {
				return current_user_can( 'edit_post', (int) $request['id'] );
			},
			'args'                => array(
				'id'     => array(
					'required'          => true,
					'validate_callback' => static function ( $value ) {
						return is_numeric( $value );
					},
				),
				'rating' => array(
					'required'          => true,
					'type'              => 'integer',
					'sanitize_callback' => 'absint',
					'validate_callback' => static function ( $value ) {
						return $value >= 1 && $value <= 5;
					},
				),
			),
		)
	);
}

function acme_update_book_rating( WP_REST_Request $request ) {
	$post_id = (int) $request['id'];
	$rating  = (int) $request['rating'];

	if ( 'acme_book' !== get_post_type( $post_id ) ) {
		return new WP_Error( 'acme_not_found', __( 'Book not found.', 'acme' ), array( 'status' => 404 ) );
	}

	update_post_meta( $post_id, 'rating', $rating );

	return rest_ensure_response( array( 'id' => $post_id, 'rating' => $rating ) );
}
```

For admin form submissions, pair a capability check with a nonce. The nonce proves intent; the capability check proves authorization. Both are required.

```php
// In the form:
wp_nonce_field( 'acme_save_settings', 'acme_settings_nonce' );

// In the handler:
function acme_handle_settings_submit() {
	if ( ! current_user_can( 'manage_options' ) ) {
		wp_die( esc_html__( 'You are not allowed to do this.', 'acme' ), 403 );
	}

	if ( ! isset( $_POST['acme_settings_nonce'] )
		|| ! wp_verify_nonce( sanitize_key( $_POST['acme_settings_nonce'] ), 'acme_save_settings' ) ) {
		wp_die( esc_html__( 'Security check failed.', 'acme' ), 403 );
	}

	// Safe to process the request.
}
```

---

## Prefer Dependency Injection

Dependencies should be explicit whenever practical.

Prefer:

```text
Service
    ↓
Repository
    ↓
API
```

Avoid hidden dependencies through global state.

---

## Keep Hooks Focused

Each action or filter should perform one clear responsibility.

Prefer:

```text
Register Hook
        ↓
Call Service
        ↓
Return Result
```

Avoid placing large amounts of business logic directly inside hook callbacks.

Register assets on the correct hook using the enqueue API. Never hardcode `<script>` or `<link>` tags into templates, and always version assets so caches invalidate on deploy.

```php
add_action( 'wp_enqueue_scripts', 'acme_enqueue_frontend_assets' );

function acme_enqueue_frontend_assets() {
	$version = wp_get_theme()->get( 'Version' );

	wp_enqueue_style(
		'acme-main',
		get_theme_file_uri( 'assets/css/main.css' ),
		array(),
		$version
	);

	wp_enqueue_script(
		'acme-app',
		get_theme_file_uri( 'assets/js/app.js' ),
		array( 'wp-element' ),
		$version,
		array( 'in_footer' => true ) // WP 6.3+ signature; an array here also enables 'strategy'.
	);

	// Pass server data to JS safely instead of inlining unescaped values.
	wp_localize_script(
		'acme-app',
		'acmeSettings',
		array(
			'restUrl' => esc_url_raw( rest_url( 'acme/v1/books' ) ),
			'nonce'   => wp_create_nonce( 'wp_rest' ),
		)
	);
}
```

---

## Error Handling

Handle expected failures gracefully.

Examples:

- invalid input;
- missing resources;
- failed API requests;
- unavailable services.

Error messages should help developers while remaining safe for users.

---

## Logging

Log useful operational information.

Examples:

- API failures;
- external integrations;
- background jobs;
- unexpected exceptions.

Avoid excessive logging that obscures important events.

---

## Performance Awareness

Before adding new code consider:

- query count;
- caching opportunities;
- asset loading;
- image optimization;
- REST response size;
- unnecessary rendering.

Performance should be part of implementation—not an afterthought.

Cache the results of expensive work with the Transients API. A transient stores a value with an expiry and is backed by a persistent object cache when one is available.

```php
function acme_get_bestseller_ids() {
	$cache_key = 'acme_bestseller_ids';
	$ids       = get_transient( $cache_key );

	if ( false !== $ids ) {
		return $ids; // Cache hit.
	}

	$query = new WP_Query(
		array(
			'post_type'      => 'acme_book',
			'posts_per_page' => 10,
			'meta_key'       => 'sales_count',
			'orderby'        => 'meta_value_num',
			'order'          => 'DESC',
			'fields'         => 'ids',    // Return IDs only; skips hydrating full post objects.
			'no_found_rows'  => true,
		)
	);

	$ids = $query->posts;

	set_transient( $cache_key, $ids, HOUR_IN_SECONDS );

	return $ids;
}
```

Invalidate the cache when the underlying data changes rather than relying only on the expiry:

```php
add_action( 'save_post_acme_book', 'acme_flush_bestseller_cache' );

function acme_flush_bestseller_cache() {
	delete_transient( 'acme_bestseller_ids' );
}
```

---

## Documentation

Document:

- public APIs;
- complex business rules;
- configuration;
- environment variables;
- unusual architectural decisions.

Code explains how.

Documentation explains why.

---

## AI Execution Checklist

## Investigation

☐ Understand the business goal.

☐ Review project architecture.

☐ Search existing implementations.

☐ Identify reusable code.

---

## Planning

☐ Define implementation strategy.

☐ Preserve architecture.

☐ Minimize complexity.

☐ Identify risks.

---

## Implementation

☐ Follow WordPress APIs.

☐ Separate responsibilities.

☐ Validate input.

☐ Sanitize data.

☐ Escape output.

☐ Reuse existing code.

---

## Verification

☐ Verify functionality.

☐ Verify security.

☐ Verify performance.

☐ Verify maintainability.

☐ Verify documentation.

---

## Common Mistakes

Avoid:

Creating duplicate functionality.

Ignoring WordPress APIs.

Writing business logic inside templates.

Hardcoding configuration values.

Skipping capability checks.

Skipping escaping.

Mixing unrelated responsibilities.

Overengineering simple solutions.

---

## Completion Criteria

A WordPress implementation follows best practices when:

- responsibilities are clearly separated;
- existing architecture is respected;
- WordPress APIs are used appropriately;
- security has been considered;
- performance has been reviewed;
- documentation is sufficient;
- future maintenance is straightforward.

---

## Summary

Professional WordPress development is built on consistency, reuse, and respect for the platform.

Following these practices results in software that is easier to maintain, safer to extend, and more resilient as projects grow.