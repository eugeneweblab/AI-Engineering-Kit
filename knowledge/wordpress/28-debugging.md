---
id: wordpress/28-debugging
topic: wordpress
slug: debugging
title: "WordPress Debugging"
type: doc
order: 28
status: ready
tags: [wordpress, debugging]
related: [wordpress/07-testing, wordpress/26-wp-cli, wordpress/08-hooks, wordpress/12-queries, wordpress/27-deployment, wordpress/29-maintenance, wordpress/19-database, wordpress/100-common-antipatterns]
when_to_use: "Read when diagnosing a WordPress problem — enabling debug output safely, finding the cause of a white screen, or tracing hooks, queries, and AJAX or REST failures."
---
# WordPress Debugging

## Purpose

This document defines how to diagnose problems in WordPress: the debug constants and what each
one does, how to read a white screen, how to trace hooks and queries, and how to debug
contexts — AJAX, REST, cron — where printing output is not an option.

WordPress hides errors by default in production, which is correct behavior and the reason
most reports arrive as "the page is blank".

---

## Core Principle

**Log, never display.** Printing errors breaks anything expecting structured output: REST
responses become invalid JSON, AJAX handlers return garbage, and redirects fail because
headers were already sent.

```php
// wp-config.php — development
define( 'WP_DEBUG', true );
define( 'WP_DEBUG_LOG', true );      // → wp-content/debug.log
define( 'WP_DEBUG_DISPLAY', false ); // ← the important one
define( 'SCRIPT_DEBUG', true );      // unminified core CSS/JS
define( 'SAVEQUERIES', true );       // record every query (heavy; development only)

@ini_set( 'display_errors', '0' );   // PHP's own setting; WP_DEBUG_DISPLAY does not cover it
```

Send the log somewhere outside the web root so it is never downloadable:

```php
define( 'WP_DEBUG_LOG', '/var/log/wordpress/debug.log' );
```

On production, `WP_DEBUG` stays off and errors go to the PHP error log. `WP_DEBUG_DISPLAY`
must never be true there — it leaks paths, queries, and sometimes credentials to visitors.

---

## The White Screen

A blank page is a fatal error with display disabled. In order:

```bash
# 1. Read the log — the fatal is in one of these.
tail -n 50 wp-content/debug.log
tail -n 50 /var/log/php-fpm/error.log

# 2. Is it a plugin or the theme?
wp plugin list --status=active --skip-plugins --skip-themes
wp eval 'echo "bootstrap ok\n";' --skip-plugins --skip-themes

# 3. Bisect.
wp plugin deactivate --all
wp plugin activate one-plugin   # repeat until the failure returns
```

Since WordPress 5.2, a fatal error in a plugin or theme triggers **recovery mode**: the site
emails the admin a link that loads the admin with the offending extension paused. If that email
never arrives, mail delivery is broken too — which is its own finding.

Common causes, in rough order of frequency: a PHP version mismatch after a host upgrade, a
plugin update requiring a newer core, memory exhaustion (`WP_MEMORY_LIMIT`), and a syntax error
in a file edited directly on the server.

---

## Query Monitor

For anything reproducible in a browser, Query Monitor answers most questions faster than
manual instrumentation: every query with its caller and duration, hooks fired in order, the
template chosen and its candidates, HTTP requests, REST responses, and PHP errors.

Install it on development and staging only:

```bash
wp plugin install query-monitor --activate
```

Its most useful views for the problems in this topic: **Queries by Component** (which plugin
is responsible for the slow page), **Hooks & Actions** (what is attached and in what order),
and **Template** (why that file rendered).

---

## Tracing Hooks

```php
// What is attached to a hook, and at which priorities?
add_action( 'shutdown', function () {
	global $wp_filter;
	if ( isset( $wp_filter['the_content'] ) ) {
		foreach ( $wp_filter['the_content']->callbacks as $priority => $callbacks ) {
			error_log( "the_content @ {$priority}: " . implode( ', ', array_keys( $callbacks ) ) );
		}
	}
} );

// Did a hook fire at all, and how often?
add_action( 'shutdown', function () {
	error_log( 'save_post fired ' . did_action( 'save_post' ) . ' time(s)' );
} );

// Which callback is corrupting a value? Log around each priority.
foreach ( array( 1, 10, 20, 99 ) as $priority ) {
	add_filter( 'the_content', function ( $content ) use ( $priority ) {
		error_log( "the_content @ {$priority}: " . strlen( $content ) . ' bytes' );
		return $content;
	}, $priority );
}
```

The length trace is the fastest way to find the filter that empties a value: the priority where
the byte count drops to zero is the culprit. See [Hooks](08-hooks.md).

---

## Tracing Queries

```php
// Requires SAVEQUERIES. Log the slowest queries and where they came from.
add_action( 'shutdown', function () {
	global $wpdb;

	if ( ! defined( 'SAVEQUERIES' ) || ! SAVEQUERIES ) {
		return;
	}

	usort( $wpdb->queries, fn( $a, $b ) => $b[1] <=> $a[1] );

	foreach ( array_slice( $wpdb->queries, 0, 5 ) as [ $sql, $duration, $caller ] ) {
		error_log( sprintf( "%.4fs  %s\n    ← %s", $duration, $sql, $caller ) );
	}

	error_log( sprintf( 'Total: %d queries', count( $wpdb->queries ) ) );
} );
```

The `$caller` field is what makes this useful — it names the function chain that issued the
query, which usually identifies the responsible plugin immediately.

A query count in the hundreds on a single page almost always means a query inside a loop; see
[Queries](12-queries.md).

---

## Debugging AJAX, REST, and Cron

None of these contexts can tolerate printed output, and all three swallow errors differently.

```php
// AJAX and REST: log, then return a proper error object.
add_action( 'wp_ajax_acme_save', function () {
	error_log( '[acme] ajax_save: ' . wp_json_encode( $_POST ) );

	if ( ! check_ajax_referer( 'acme_save', 'nonce', false ) ) {
		wp_send_json_error( array( 'message' => 'Invalid nonce' ), 403 );
	}

	wp_send_json_success( array( 'saved' => true ) );
} );
```

```bash
# REST: call the endpoint directly and read the raw response.
curl -s -i https://site.test/wp-json/acme/v1/events/42

# Cron: run the event in the foreground, where errors surface.
wp cron event run acme_daily_cleanup --debug
```

`--debug` on any WP-CLI command prints internal notices and full stack traces, which is
usually the fastest path to a cron or CLI failure.

For "the form submits but nothing happens", check the browser's network tab first: a 500 with
an HTML error page inside a JSON response is a different problem from a 200 with
`success: false`.

---

## Instrumenting Code

```php
// A guarded logger — no output in production, structured data preserved.
function acme_log( string $message, array $context = array() ): void {
	if ( ! defined( 'WP_DEBUG' ) || ! WP_DEBUG ) {
		return;
	}

	error_log( sprintf(
		'[acme] %s %s',
		$message,
		$context ? wp_json_encode( $context, JSON_UNESCAPED_SLASHES ) : ''
	) );
}

acme_log( 'signup created', array( 'event' => $event_id, 'user' => $user_id ) );
```

Never leave `var_dump()`, `print_r()`, or `error_log( print_r( $x, true ) )` in committed code.
`wp_json_encode()` produces the same information in one line and cannot accidentally print.

For a stack trace without stopping execution:

```php
acme_log( 'unexpected state', array( 'trace' => wp_debug_backtrace_summary() ) );
```

---

## Isolating the Cause

The fastest general procedure, in order — each step eliminates a whole class of cause:

1. **Reproduce** with a specific URL, user role, and browser state. An intermittent bug is
   usually a caching or cron bug.
2. **Switch to a default theme** (`wp theme activate twentytwentyfive`) — separates theme from
   plugin.
3. **Deactivate plugins**, then reactivate in halves rather than one at a time.
4. **Compare environments.** Works locally but not on production usually means PHP version,
   object cache, a page cache, or a filesystem permission difference.
5. **Check the constants.** `WP_DEBUG` off, an aggressive page cache, or `DISABLE_WP_CRON`
   explain a large share of "impossible" behavior.

---

## Examples

**Good Example** — log with context, isolate by bisection

```php
// Never echo. Write structured context to the log and keep the response valid.
function myplugin_log( string $event, array $context = array() ): void {
	if ( ! defined( 'WP_DEBUG' ) || ! WP_DEBUG ) {
		return;
	}
	error_log( sprintf( '[myplugin] %s %s', $event, wp_json_encode( $context ) ) );
}

add_action( 'myplugin_signup_failed', function ( int $event_id, WP_Error $error ) {
	myplugin_log(
		'signup_failed',
		array(
			'event_id' => $event_id,
			'code'     => $error->get_error_code(),
			'user'     => get_current_user_id(),
			'request'  => defined( 'REST_REQUEST' ) ? 'rest' : 'web',
		)
	);
}, 10, 2 );
```

```bash
# Bisect the cause instead of guessing: does it survive with no plugins and a core theme?
wp --skip-plugins --skip-themes eval 'echo (int) is_user_logged_in();'

# Re-enable in halves until the failure returns; the last one added is the cause.
wp plugin deactivate --all
wp plugin activate acme-events woocommerce
```

**Bad Example** — printing into the response and guessing

```php
function myplugin_create_signup( WP_REST_Request $request ) {
	// Output before the JSON body: the response is no longer valid JSON, so the
	// client reports a parse error and the real failure is never seen.
	var_dump( $request->get_params() );
	print_r( $GLOBALS['wpdb']->last_query );

	// Silences the error that explains the bug, then returns a value that hides it.
	$result = @myplugin_register( $request['id'] );

	// Displaying errors on a production site leaks paths, versions, and query text.
	ini_set( 'display_errors', '1' );

	return $result ?: array( 'ok' => false );
}
```

---

## Common Mistakes

- **`WP_DEBUG_DISPLAY` enabled**, breaking REST, AJAX, and redirects — and leaking paths.
- **`debug.log` inside the web root**, publicly downloadable.
- **`SAVEQUERIES` left on in production**, consuming memory on every request.
- **`var_dump()` in committed code**, corrupting JSON responses.
- **Debugging AJAX by echoing.**
- **Bisecting one plugin at a time** instead of halving.
- **Ignoring the browser network tab** for front-end failures.
- **Assuming the code is wrong** when a page cache is serving a stale response.
- **Editing files on production to debug**, leaving changes the next deploy silently reverts.

---

## Verification Checklist

- Is `WP_DEBUG_DISPLAY` off everywhere, with logging to a path outside the web root?
- Has the log actually been read before forming a hypothesis?
- Has the problem been isolated to theme, plugin, or core by switching and bisecting?
- For a slow page, has the query list been inspected with `SAVEQUERIES` or Query Monitor?
- For a wrong value, has the hook chain been traced by priority?
- For AJAX or REST, has the raw HTTP response been examined?
- Is all temporary instrumentation removed before committing?

---

## Summary

Turn logging on and display off, read the log before theorizing, and isolate by switching
themes and bisecting plugins. For values, trace the hook chain by priority; for slowness, read
the query list with its callers; and for AJAX, REST, and cron, inspect the raw response rather
than printing into it.

## Related


- `knowledge/wordpress/07-testing.md`
- `knowledge/wordpress/26-wp-cli.md`
- `knowledge/wordpress/08-hooks.md`
- `knowledge/wordpress/12-queries.md`
- `knowledge/wordpress/27-deployment.md`
- `knowledge/wordpress/29-maintenance.md`
- `knowledge/wordpress/19-database.md`
- `knowledge/wordpress/100-common-antipatterns.md`
