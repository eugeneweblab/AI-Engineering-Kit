---
id: wordpress/01-wordpress-architecture
topic: wordpress
slug: wordpress-architecture
title: "WordPress Architecture"
type: doc
order: 1
status: ready
tags: [wordpress, wordpress-architecture]
related: [wordpress/02-project-structure, wordpress/08-hooks, wordpress/12-queries, wordpress/13-template-hierarchy, wordpress/19-database]
when_to_use: "Read before designing or extending the architecture of a WordPress application."
---
# WordPress Architecture

## Purpose

This document defines the engineering principles for designing, extending, and maintaining WordPress applications.

It applies to traditional WordPress websites, headless architectures, enterprise platforms, WooCommerce stores, multisite installations, and custom plugin ecosystems.

The objective is to ensure that every implementation remains maintainable, scalable, secure, and aligned with WordPress best practices.

---

## Core Philosophy

WordPress is an application framework—not simply a CMS.

Treat it as a platform composed of multiple independent systems:

- Content Management
- User Management
- Authentication
- REST API
- Media Library
- Hooks System
- Block Editor
- Theme System
- Plugin System
- Scheduled Tasks
- CLI Tools

Every feature should integrate with these systems instead of replacing them.

---

## Architectural Principles

## Respect Existing Architecture

Before implementing new functionality:

- understand the current architecture;
- identify existing abstractions;
- identify reusable services;
- understand coding conventions;
- understand deployment strategy.

Never introduce a second architecture into the project.

---

## Separate Responsibilities

Each layer should have a single responsibility.

Example:

```
Presentation
        ↓
Application Logic
        ↓
Business Logic
        ↓
Data Access
        ↓
Infrastructure
```

Avoid mixing these responsibilities.

---

## Prefer Composition

Build small reusable modules instead of large monolithic solutions.

Examples:

Good

```
Button
↓

Card
↓

Product Card
↓

Product Grid
↓

Landing Section
```

Instead of:

```
LandingPageComponent
```

---

## Reuse Before Creating

Before creating:

- helper functions;
- hooks;
- REST endpoints;
- custom fields;
- services;
- components;
- templates;

search the existing project.

Reuse is preferred over duplication.

---

## Recommended Project Structure

A typical enterprise project may contain:

```
theme/

plugin/

blocks/

modules/

api/

services/

helpers/

templates/

assets/

languages/

tests/
```

Folder names may vary, but responsibilities should remain clear.

---

## Theme Responsibilities

Themes should primarily handle:

- presentation;
- layouts;
- templates;
- frontend rendering;
- styling.

Avoid placing business logic inside templates.

---

## Plugin Responsibilities

Plugins should primarily contain:

- business logic;
- integrations;
- custom post types;
- REST endpoints;
- background jobs;
- reusable functionality.

Features that may outlive the active theme generally belong in plugins.

Custom post types are the clearest example: they represent structured content that must survive a theme switch, so they belong in a plugin and must be registered on the `init` hook.

Good — a custom post type registered in a plugin, on the correct hook:

```php
add_action( 'init', 'acme_register_review_cpt' );

function acme_register_review_cpt() {
	register_post_type(
		'acme_review',
		array(
			'labels'       => array(
				'name'          => __( 'Reviews', 'acme' ),
				'singular_name' => __( 'Review', 'acme' ),
			),
			'public'       => true,
			'has_archive'  => true,
			'show_in_rest' => true, // Required for the block editor and REST API.
			'menu_icon'    => 'dashicons-star-filled',
			'supports'     => array( 'title', 'editor', 'thumbnail', 'custom-fields' ),
			'rewrite'      => array( 'slug' => 'reviews' ),
		)
	);
}
```

Bad — registering content types from the theme's `functions.php`. The content becomes inaccessible the moment the theme is switched:

```php
// In theme functions.php — content disappears when the theme changes.
add_action( 'after_setup_theme', 'acme_register_review_cpt' ); // Wrong hook, wrong layer.
```

Use `after_setup_theme` for theme concerns (menus, image sizes, `add_theme_support()`), and `init` for content registration in plugins.

---

## Hooks First

Before modifying WordPress behavior, determine whether it can be achieved through:

Actions

Filters

REST API

Block APIs

Template hierarchy

Core APIs

Prefer extension over modification.

Actions let you run side effects at a defined point; filters let you transform a value that core is about to use. Both require a real, existing hook name and the correct number of accepted arguments.

Good — extend behavior through documented hooks:

```php
// Action: enqueue front-end assets at the standard point.
add_action( 'wp_enqueue_scripts', 'acme_enqueue_assets' );

function acme_enqueue_assets() {
	wp_enqueue_style(
		'acme-main',
		plugins_url( 'assets/main.css', __FILE__ ),
		array(),
		'1.2.0'
	);
}

// Filter: append content only on the single view of our post type.
add_filter( 'the_content', 'acme_append_disclaimer' );

function acme_append_disclaimer( $content ) {
	if ( is_singular( 'acme_review' ) && in_the_loop() && is_main_query() ) {
		$content .= '<p class="acme-disclaimer">' . esc_html__( 'Sponsored review.', 'acme' ) . '</p>';
	}

	return $content; // A filter callback must always return the value.
}
```

Bad — editing core or theme output directly, or a filter that forgets to return:

```php
add_filter( 'the_content', 'acme_append_disclaimer' );

function acme_append_disclaimer( $content ) {
	echo '<p>Sponsored review.</p>'; // Echoing inside a filter, and no return — breaks the content.
}
```

---

## REST API

REST endpoints should:

- follow consistent naming;
- validate input;
- sanitize input;
- escape output;
- return predictable responses;
- implement permission checks.

Controllers should remain thin.

Business logic belongs in services.

Register endpoints with `register_rest_route` on the `rest_api_init` hook. A `permission_callback` is mandatory — omitting it triggers a `_doing_it_wrong()` notice and, on WordPress 5.5+, blocks the route.

Good — a thin controller that validates arguments, checks capability, and delegates to a service:

```php
add_action( 'rest_api_init', 'acme_register_review_routes' );

function acme_register_review_routes() {
	register_rest_route(
		'acme/v1',
		'/reviews',
		array(
			'methods'             => WP_REST_Server::CREATABLE, // POST
			'callback'            => 'acme_create_review',
			'permission_callback' => function () {
				return current_user_can( 'edit_posts' );
			},
			'args'                => array(
				'title'  => array(
					'required'          => true,
					'type'              => 'string',
					'sanitize_callback' => 'sanitize_text_field',
				),
				'rating' => array(
					'required'          => true,
					'type'              => 'integer',
					'validate_callback' => function ( $value ) {
						return is_numeric( $value ) && $value >= 1 && $value <= 5;
					},
				),
			),
		)
	);
}

function acme_create_review( WP_REST_Request $request ) {
	// Input is already sanitized/validated by the args schema above.
	$post_id = acme_reviews_service()->create(
		$request->get_param( 'title' ),
		(int) $request->get_param( 'rating' )
	);

	if ( is_wp_error( $post_id ) ) {
		return $post_id; // WP_Error is serialized to a proper HTTP error response.
	}

	return new WP_REST_Response( array( 'id' => $post_id ), 201 );
}
```

Bad — no permission callback, business logic and raw SQL inlined in the controller:

```php
register_rest_route(
	'acme/v1',
	'/reviews',
	array(
		'methods'  => 'POST',
		'callback' => function ( $request ) {
			global $wpdb;
			// Public write access + unsanitized input + string-built SQL.
			$wpdb->query( "INSERT INTO wp_reviews (title) VALUES ('" . $request['title'] . "')" );
			return 'ok';
		},
		// permission_callback omitted — route is rejected on modern WordPress.
	)
);
```

---

## Database Strategy

Prefer:

- WordPress APIs;
- post meta;
- term meta;
- user meta;
- options API;
- transients;
- object cache.

Avoid direct SQL unless necessary.

Retrieve content through `WP_Query` (or `get_posts`) rather than querying `wp_posts` yourself — it applies the correct joins, statuses, caching, and hooks. Store singleton settings in the Options API and expensive computed results in transients.

Good — query posts and cache a derived result:

```php
$reviews = new WP_Query(
	array(
		'post_type'      => 'acme_review',
		'post_status'    => 'publish',
		'posts_per_page' => 10,
		'meta_key'       => 'acme_rating',
		'orderby'        => 'meta_value_num',
		'order'          => 'DESC',
		'no_found_rows'  => true, // Skip the SQL_CALC_FOUND_ROWS count when pagination is not needed.
	)
);

if ( $reviews->have_posts() ) {
	while ( $reviews->have_posts() ) {
		$reviews->the_post();
		the_title( '<h2>', '</h2>' );
	}
	wp_reset_postdata(); // Always restore the global $post after a custom loop.
}
```

```php
// Settings: read once, write with autoload control.
$settings = get_option( 'acme_settings', array() );
update_option( 'acme_settings', $settings, false ); // false = do not autoload large/rarely used options.

// Expensive aggregate cached for one hour.
function acme_get_average_rating() {
	$average = get_transient( 'acme_average_rating' );

	if ( false === $average ) {
		$average = acme_reviews_service()->calculate_average(); // Expensive computation.
		set_transient( 'acme_average_rating', $average, HOUR_IN_SECONDS );
	}

	return $average;
}
```

When SQL is required:

- prepare queries;
- minimize complexity;
- document assumptions.

Good — a prepared statement using `$wpdb->prepare`, with the correct table prefix:

```php
global $wpdb;

$rating = 4;

$post_ids = $wpdb->get_col(
	$wpdb->prepare(
		"SELECT post_id FROM {$wpdb->postmeta} WHERE meta_key = %s AND meta_value >= %d",
		'acme_rating',
		$rating
	)
);
```

Bad — a hardcoded prefix and interpolated input (SQL injection):

```php
$rating   = $_GET['rating']; // Untrusted, unsanitized.
$post_ids = $wpdb->get_col( "SELECT post_id FROM wp_postmeta WHERE meta_value >= $rating" );
```

---

## Configuration

Configuration should be centralized.

Examples:

Environment variables

Constants

Configuration classes

Service providers

Avoid scattered configuration values.

---

## Security Principles

Every feature should include:

- capability checks;
- nonce verification;
- validation;
- sanitization;
- escaping;
- permission checks;
- secure file handling.

Security is an architectural concern.

A state-changing admin form demonstrates the full flow: emit a nonce on render, then verify the nonce, verify the capability, sanitize on input, and escape on output.

Good — the complete round trip:

```php
// Render: output the nonce field inside the form.
function acme_render_settings_form() {
	?>
	<form method="post" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>">
		<input type="hidden" name="action" value="acme_save_settings">
		<?php wp_nonce_field( 'acme_save_settings', 'acme_settings_nonce' ); ?>
		<input type="text" name="acme_label" value="<?php echo esc_attr( get_option( 'acme_label', '' ) ); ?>">
		<?php submit_button( __( 'Save', 'acme' ) ); ?>
	</form>
	<?php
}

// Handle: verify, authorize, sanitize, store.
add_action( 'admin_post_acme_save_settings', 'acme_handle_settings' );

function acme_handle_settings() {
	if ( ! isset( $_POST['acme_settings_nonce'] )
		|| ! wp_verify_nonce( sanitize_key( $_POST['acme_settings_nonce'] ), 'acme_save_settings' )
	) {
		wp_die( esc_html__( 'Invalid request.', 'acme' ), 403 );
	}

	if ( ! current_user_can( 'manage_options' ) ) {
		wp_die( esc_html__( 'Insufficient permissions.', 'acme' ), 403 );
	}

	$label = isset( $_POST['acme_label'] ) ? sanitize_text_field( wp_unslash( $_POST['acme_label'] ) ) : '';
	update_option( 'acme_label', $label );

	wp_safe_redirect( admin_url( 'admin.php?page=acme-settings&updated=1' ) );
	exit;
}
```

Bad — trusting the request and storing raw input:

```php
add_action( 'admin_post_acme_save_settings', 'acme_handle_settings' );

function acme_handle_settings() {
	// No nonce check, no capability check, no sanitization, no wp_unslash.
	update_option( 'acme_label', $_POST['acme_label'] );
	wp_redirect( $_SERVER['HTTP_REFERER'] ); // Unvalidated redirect.
}
```

Note the ordering rule reinforced across this project: sanitize when data enters the system, and escape (`esc_html`, `esc_attr`, `esc_url`) at the moment of output — never the reverse.

---

## Performance Principles

Review:

- database queries;
- caching;
- image optimization;
- asset loading;
- REST responses;
- lazy loading;
- background processing.

Optimize architecture before micro-optimizing code.

---

## AI Execution Checklist

## Investigation

☐ Understand the project architecture.

☐ Identify active plugins.

☐ Identify theme structure.

☐ Review coding conventions.

☐ Review existing services.

☐ Review reusable modules.

---

## Planning

☐ Select the correct integration point.

☐ Define responsibilities.

☐ Identify reusable code.

☐ Estimate architectural impact.

---

## Implementation

☐ Preserve architecture.

☐ Separate responsibilities.

☐ Reuse existing code.

☐ Follow WordPress APIs.

☐ Avoid duplication.

---

## Verification

☐ Verify maintainability.

☐ Verify security.

☐ Verify performance.

☐ Verify compatibility.

☐ Verify documentation.

---

## Examples

**Good Example** — the template renders; a service decides

```php
// inc/class-myplugin-event-service.php — business rules live here, testable in isolation.
class MyPlugin_Event_Service {

	public function upcoming( int $limit = 5 ): array {
		$cached = wp_cache_get( "upcoming_{$limit}", 'myplugin_events' );
		if ( false !== $cached ) {
			return $cached;
		}

		$query = new WP_Query(
			array(
				'post_type'      => 'myplugin_event',
				'posts_per_page' => $limit,
				'no_found_rows'  => true,   // skip SQL_CALC_FOUND_ROWS; no pagination needed
			)
		);

		wp_cache_set( "upcoming_{$limit}", $query->posts, 'myplugin_events', 5 * MINUTE_IN_SECONDS );

		return $query->posts;
	}
}
```

```php
<?php
// template-parts/upcoming-events.php — presentation only.
$events = ( new MyPlugin_Event_Service() )->upcoming();
?>
<ul class="upcoming-events">
	<?php foreach ( $events as $event ) : ?>
		<li><?php echo esc_html( get_the_title( $event ) ); ?></li>
	<?php endforeach; ?>
</ul>
```

Swapping the data source, adding a test, or reusing the list in a REST endpoint touches one
class. The template never changes.

**Bad Example** — the template is the application

```php
<?php
// template-parts/upcoming-events.php
global $wpdb;

// Direct SQL bypasses the object cache, the post-status rules, and every filter another
// plugin registered. It cannot be unit-tested, and it cannot be reused by the REST layer.
$rows = $wpdb->get_results(
	"SELECT ID, post_title FROM {$wpdb->posts}
	 WHERE post_type = 'myplugin_event' AND post_status = 'publish' LIMIT 5"
);

foreach ( $rows as $row ) {
	// A business rule buried in markup, and unescaped output on top of it.
	if ( get_post_meta( $row->ID, 'featured', true ) ) {
		echo '<li class="featured">' . $row->post_title . '</li>';
	}
}
```

The rule "featured events render differently" now exists only inside one template file. The
next place that needs it will reimplement it, and the two will drift.

---

## Common Mistakes

Avoid:

Placing business logic inside templates.

Creating duplicate APIs.

Ignoring existing hooks.

Writing direct SQL without necessity.

Hardcoding configuration.

Mixing responsibilities.

Ignoring scalability.

Ignoring future maintainability.

---

## Completion Criteria

A WordPress implementation is considered architecturally correct when:

- responsibilities are clearly separated;
- existing architecture is respected;
- WordPress APIs are used appropriately;
- duplication is minimized;
- security has been considered;
- performance has been reviewed;
- future maintenance remains straightforward.

---

## Summary

Well-designed WordPress architecture is based on clear responsibilities, reuse, and integration with the WordPress ecosystem.

Every new feature should strengthen the architecture rather than increase its complexity.

## Related

- `knowledge/wordpress/02-project-structure.md`
- `knowledge/wordpress/08-hooks.md`
- `knowledge/wordpress/12-queries.md`
- `knowledge/wordpress/13-template-hierarchy.md`
- `knowledge/wordpress/19-database.md`
