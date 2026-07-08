---
id: wordpress/07-testing
topic: wordpress
slug: testing
title: "WordPress Testing"
type: doc
order: 7
status: ready
tags: [wordpress, testing]
related: []
when_to_use: "Read before writing tests or defining a testing strategy for a WordPress project."
---
# WordPress Testing

## Purpose

This document defines the testing strategy for WordPress projects.

Testing is a continuous engineering activity performed throughout development rather than a final step before deployment.

The objective is to ensure that every feature behaves correctly, remains maintainable, and does not introduce regressions into the project.

---

## Core Principle

Every change should increase confidence in the system.

Testing is not about proving that code works.

Testing is about discovering where it does not.

---

## Testing Pyramid

Prefer the following balance:

```
           E2E Tests
         Integration Tests
          Unit Tests
```

Small tests should be numerous.

Large tests should be fewer.

---

## What Should Be Tested

Every feature should verify:

- expected behavior;
- unexpected behavior;
- edge cases;
- invalid input;
- authorization;
- permissions;
- error handling.

Testing should cover both successful and unsuccessful scenarios.

---

## Unit Testing

Unit tests should validate isolated business logic.

Examples:

- services;
- validators;
- helpers;
- calculations;
- formatting;
- utility classes.

Unit tests should not depend on WordPress whenever possible.

A pure function has no WordPress dependencies, so it can be tested with plain
PHPUnit without bootstrapping WordPress. These tests are fast and can run on
every save.

Good — a pure helper and a plain `PHPUnit\Framework\TestCase` that exercises it:

```php
// Function under test — no WordPress calls, so it needs no WP bootstrap.
function my_plugin_format_price( $amount, $currency = 'USD' ) {
	$amount = (float) $amount;

	return sprintf( '%s %.2f', $currency, $amount );
}
```

```php
use PHPUnit\Framework\TestCase;

final class My_Plugin_Format_Price_Test extends TestCase {

	public function test_formats_with_default_currency() {
		$this->assertSame( 'USD 9.90', my_plugin_format_price( 9.9 ) );
	}

	public function test_respects_explicit_currency() {
		$this->assertSame( 'EUR 12.00', my_plugin_format_price( 12, 'EUR' ) );
	}

	public function test_casts_numeric_strings() {
		$this->assertSame( 'USD 3.50', my_plugin_format_price( '3.5' ) );
	}
}
```

When logic must call WordPress functions, prefer refactoring the pure part out so
it can be unit tested in isolation, and cover the WordPress glue with an
integration test (below).

---

## Integration Testing

Integration tests verify interactions between components.

Examples:

- services with repositories;
- REST endpoints;
- WordPress hooks;
- custom post types;
- metadata;
- external APIs.

Integration tests ensure that independently tested components work together correctly.

Integration tests run against a real (throwaway) WordPress database using the
WordPress PHPUnit test suite. Provision it with `wp-env`, `wp scaffold plugin-tests`,
or the `wp-phpunit/wp-phpunit` package, then extend `WP_UnitTestCase`. That base
class wraps every test in a database transaction that is rolled back in
`tear_down()`, so tests stay isolated and never leak fixtures into each other.

Use the built-in factories (`$this->factory()->post`, `->user`, `->term`, …) to
create fixtures instead of writing to `$wpdb` by hand.

Good — verifying a custom post type is registered and that `WP_Query` filters it
correctly:

```php
function my_plugin_register_book_post_type() {
	register_post_type(
		'book',
		array(
			'label'        => 'Books',
			'public'       => true,
			'show_in_rest' => true,
			'supports'     => array( 'title', 'editor', 'custom-fields' ),
		)
	);
}
add_action( 'init', 'my_plugin_register_book_post_type' );
```

```php
final class My_Plugin_Book_CPT_Test extends WP_UnitTestCase {

	public function test_book_post_type_is_registered() {
		$this->assertTrue( post_type_exists( 'book' ) );
	}

	public function test_query_returns_only_published_books() {
		$published = $this->factory()->post->create(
			array(
				'post_type'   => 'book',
				'post_status' => 'publish',
			)
		);

		// A draft that must be excluded.
		$this->factory()->post->create(
			array(
				'post_type'   => 'book',
				'post_status' => 'draft',
			)
		);

		$query = new WP_Query(
			array(
				'post_type'      => 'book',
				'post_status'    => 'publish',
				'fields'         => 'ids',
				'posts_per_page' => -1,
			)
		);

		$this->assertSame( array( $published ), $query->posts );
	}
}
```

Because `WP_UnitTestCase` registers post types through the `init` hook during
bootstrap, `post_type_exists( 'book' )` is already true inside the test — there is
no need to call the registration function again.

---

## End-to-End Testing

End-to-end tests simulate real user behavior.

Examples:

- login;
- checkout;
- publishing content;
- editing posts;
- uploading media;
- administrator workflows.

E2E tests validate complete user journeys.

---

## Manual Testing

Some scenarios require manual verification.

Examples:

- responsive layouts;
- browser compatibility;
- accessibility;
- editor experience;
- Visual Builder behavior;
- Gutenberg editing.

Manual testing complements automated testing.

---

## WordPress-Specific Testing

Verify:

- actions;
- filters;
- REST endpoints;
- cron jobs;
- shortcodes;
- widgets;
- Gutenberg blocks;
- Divi modules;
- WooCommerce integrations.

Every integration point should be tested.

### Testing hooks

Verify that callbacks are attached with `has_action()` / `has_filter()` (which
return the registered priority, or `false`), and verify their effect by firing the
hook.

Good — asserting a filter is registered and that it transforms content:

```php
function my_plugin_append_notice( $content ) {
	return $content . '<p class="notice">Subscribe to our newsletter.</p>';
}
add_filter( 'the_content', 'my_plugin_append_notice' );
```

```php
final class My_Plugin_Content_Filter_Test extends WP_UnitTestCase {

	public function test_filter_is_registered_at_default_priority() {
		$this->assertSame( 10, has_filter( 'the_content', 'my_plugin_append_notice' ) );
	}

	public function test_filter_appends_notice_to_content() {
		$output = apply_filters( 'the_content', 'Body copy.' );

		$this->assertStringContainsString( 'Subscribe to our newsletter.', $output );
	}
}
```

### Testing REST endpoints

Dispatch a real `WP_REST_Request` through the server. Rebuild the server in
`set_up()` so `rest_api_init` runs with a clean route table for each test.

Good — a registered route exercised through the dispatcher:

```php
add_action( 'rest_api_init', 'my_plugin_register_routes' );

function my_plugin_register_routes() {
	register_rest_route(
		'my-plugin/v1',
		'/books',
		array(
			'methods'             => WP_REST_Server::READABLE,
			'callback'            => 'my_plugin_rest_get_books',
			'permission_callback' => '__return_true',
		)
	);
}

function my_plugin_rest_get_books( WP_REST_Request $request ) {
	$books = get_posts(
		array(
			'post_type'      => 'book',
			'post_status'    => 'publish',
			'posts_per_page' => (int) $request->get_param( 'per_page' ) ?: 10,
		)
	);

	return rest_ensure_response( wp_list_pluck( $books, 'ID' ) );
}
```

```php
final class My_Plugin_Books_REST_Test extends WP_UnitTestCase {

	private WP_REST_Server $server;

	public function set_up() {
		parent::set_up();

		global $wp_rest_server;
		$this->server   = new WP_REST_Server();
		$wp_rest_server = $this->server;
		do_action( 'rest_api_init' );
	}

	public function tear_down() {
		global $wp_rest_server;
		$wp_rest_server = null;

		parent::tear_down();
	}

	public function test_route_is_registered() {
		$this->assertArrayHasKey( '/my-plugin/v1/books', $this->server->get_routes() );
	}

	public function test_get_books_returns_published_ids() {
		$book_id = $this->factory()->post->create(
			array(
				'post_type'   => 'book',
				'post_status' => 'publish',
			)
		);

		$request  = new WP_REST_Request( 'GET', '/my-plugin/v1/books' );
		$response = $this->server->dispatch( $request );

		$this->assertSame( 200, $response->get_status() );
		$this->assertContains( $book_id, $response->get_data() );
	}
}
```

---

## Security Testing

Verify:

- authentication;
- authorization;
- nonce validation;
- input validation;
- sanitization;
- escaping;
- permission callbacks.

Security should be verified as part of normal testing.

Switch the current user with `wp_set_current_user()` and assert on capabilities,
nonces, and REST permission callbacks. Every privileged path deserves a negative
test that proves an unauthorized user is rejected.

Good — a capability check tested from both sides:

```php
final class My_Plugin_Capability_Test extends WP_UnitTestCase {

	public function test_editor_can_delete_any_post() {
		$post_id   = $this->factory()->post->create();
		$editor_id = $this->factory()->user->create( array( 'role' => 'editor' ) );
		wp_set_current_user( $editor_id );

		$this->assertTrue( current_user_can( 'delete_post', $post_id ) );
	}

	public function test_subscriber_cannot_delete_post() {
		$post_id       = $this->factory()->post->create();
		$subscriber_id = $this->factory()->user->create( array( 'role' => 'subscriber' ) );
		wp_set_current_user( $subscriber_id );

		$this->assertFalse( current_user_can( 'delete_post', $post_id ) );
	}
}
```

Good — a nonce round-trips, and a forged value is rejected:

```php
public function test_nonce_verification() {
	$user_id = $this->factory()->user->create();
	wp_set_current_user( $user_id );

	$nonce = wp_create_nonce( 'my_plugin_action' );

	$this->assertNotFalse( wp_verify_nonce( $nonce, 'my_plugin_action' ) );
	$this->assertFalse( wp_verify_nonce( 'forged-value', 'my_plugin_action' ) );
}
```

Good — a REST permission callback denies an anonymous request. `rest_do_request()`
runs the same permission pipeline as a live HTTP request. When the callback denies
access, the REST API returns `401` for logged-out users and `403` for logged-in
users without the capability:

```php
add_action( 'rest_api_init', 'my_plugin_register_write_route' );

function my_plugin_register_write_route() {
	register_rest_route(
		'my-plugin/v1',
		'/books',
		array(
			'methods'             => WP_REST_Server::CREATABLE,
			'callback'            => 'my_plugin_rest_create_book',
			'permission_callback' => function () {
				return current_user_can( 'edit_posts' );
			},
		)
	);
}
```

```php
public function test_rest_write_requires_authentication() {
	wp_set_current_user( 0 );

	global $wp_rest_server;
	$wp_rest_server = new WP_REST_Server();
	do_action( 'rest_api_init' );

	$request  = new WP_REST_Request( 'POST', '/my-plugin/v1/books' );
	$response = rest_do_request( $request );

	$this->assertSame( 401, $response->get_status() );
}
```

---

## Performance Testing

Review:

- query count;
- page generation time;
- API response time;
- asset loading;
- cache usage.

Performance regressions should be detected early.

Query count is the cheapest performance regression to catch in an automated test.
`get_num_queries()` returns the running total of database queries, so you can bound
the queries a code path is allowed to make. This is how you catch an N+1 loop
before it reaches production.

Good — asserting a bounded query count around a code path:

```php
final class My_Plugin_Query_Budget_Test extends WP_UnitTestCase {

	public function test_book_list_avoids_n_plus_one() {
		$this->factory()->post->create_many(
			20,
			array(
				'post_type'   => 'book',
				'post_status' => 'publish',
			)
		);

		$before = get_num_queries();

		$request  = new WP_REST_Request( 'GET', '/my-plugin/v1/books' );
		rest_do_request( $request );

		// A single WP_Query should not scale with the number of books.
		$this->assertLessThan( 15, get_num_queries() - $before );
	}
}
```

---

## Regression Testing

Before merging changes verify that existing functionality still works.

Focus on:

- shared components;
- reusable services;
- API compatibility;
- templates;
- editor experience.

Every bug fix should reduce the chance of future regressions.

---

## Test Data

Use predictable and reusable test data.

Avoid relying on:

- production databases;
- random values;
- manually prepared environments.

Tests should produce consistent results.

Build fixtures with the WordPress factories rather than inserting rows directly.
Factories create real objects through the same code paths WordPress uses at
runtime, and `WP_UnitTestCase` rolls them back after each test.

Bad — writing to the database directly and reading from live production data:

```php
public function test_reads_a_post() {
	global $wpdb;

	// Bypasses hooks and object cache, and is not rolled back cleanly.
	$wpdb->insert( $wpdb->posts, array( 'post_title' => 'Hardcoded' ) );

	// Assumes a specific post exists in the live database.
	$post = get_post( 42 );

	$this->assertSame( 'Expected Title', $post->post_title );
}
```

Good — deterministic fixtures created through factories:

```php
public function test_reads_a_post() {
	$author_id = $this->factory()->user->create( array( 'role' => 'editor' ) );

	$post_id = $this->factory()->post->create(
		array(
			'post_title'  => 'Test Post',
			'post_status' => 'publish',
			'post_author' => $author_id,
		)
	);

	$category_id = $this->factory()->term->create( array( 'taxonomy' => 'category' ) );
	wp_set_post_terms( $post_id, array( $category_id ), 'category' );

	$post = get_post( $post_id );

	$this->assertSame( 'Test Post', $post->post_title );
	$this->assertSame( 'publish', $post->post_status );
}
```

---

## AI Execution Checklist

## Investigation

☐ Understand the feature.

☐ Identify affected components.

☐ Identify integration points.

☐ Review existing tests.

---

## Planning

☐ Define test scenarios.

☐ Define edge cases.

☐ Define negative cases.

☐ Define regression scope.

---

## Verification

☐ Verify successful behavior.

☐ Verify validation.

☐ Verify permissions.

☐ Verify error handling.

☐ Verify responsive behavior.

☐ Verify accessibility.

☐ Verify performance.

---

## Common Mistakes

Avoid:

Testing only successful scenarios.

Ignoring edge cases.

Skipping authorization tests.

Skipping editor testing.

Testing implementation instead of behavior.

Depending on production data.

Ignoring regression testing.

Bad — asserts on an internal implementation detail (which private cache key is
used), so the test breaks on harmless refactors and proves nothing about behavior:

```php
public function test_caches_result() {
	my_plugin_get_report( 5 );

	$this->assertNotFalse( wp_cache_get( 'my_plugin_report_v3_5', 'my_plugin' ) );
}
```

Good — asserts on observable behavior (correct output, and that a repeated call
adds no queries), which stays valid regardless of how caching is implemented:

```php
public function test_result_is_cached() {
	$first = my_plugin_get_report( 5 );

	$queries_before = get_num_queries();
	$second         = my_plugin_get_report( 5 );

	$this->assertSame( $first, $second );
	$this->assertSame( 0, get_num_queries() - $queries_before );
}
```

---

## Completion Criteria

Testing is considered complete when:

- expected behavior has been verified;
- invalid scenarios have been tested;
- integration points have been reviewed;
- regressions have been checked;
- security has been validated;
- performance has been reviewed where appropriate.

---

## Summary

Testing provides confidence that software behaves correctly today and continues to behave correctly as the project evolves.

A professional engineering workflow treats testing as part of development rather than a separate activity performed at the end.