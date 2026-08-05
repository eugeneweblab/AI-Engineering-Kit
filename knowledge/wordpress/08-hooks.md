---
id: wordpress/08-hooks
topic: wordpress
slug: hooks
title: "Hooks — Actions and Filters"
type: doc
order: 8
status: ready
tags: [wordpress, hooks]
related: [wordpress/01-wordpress-architecture, wordpress/15-plugin-development, wordpress/12-queries, wordpress/03-best-practices, wordpress/100-common-antipatterns, wordpress/14-theme-development]
when_to_use: "Read before hooking into WordPress — registering actions or filters, choosing a hook and priority, or debugging a callback that does not fire."
---
# Hooks — Actions and Filters

## Purpose

This document defines how to extend WordPress through its hook system: which hook to choose,
what priority means, why a callback sometimes never fires, and how to write hooks that other
code can remove and test.

Hooks are the extension mechanism of WordPress. Code that changes behavior any other way —
editing core, editing a parent theme, editing a third-party plugin — is erased by the next
update.

---

## Core Principle

An **action** performs work at a moment. A **filter** transforms a value and must return it.

That single distinction causes more broken WordPress code than any other: a filter callback
that forgets to `return` replaces the value with `null`, and the symptom appears far from the
cause — an empty title, a missing excerpt, a blank template.

```php
// Action: side effect, return value ignored.
add_action( 'init', 'myplugin_register_types' );

// Filter: MUST return, or the value is destroyed.
add_filter( 'the_title', 'myplugin_decorate_title' );
```

Mechanically the two are the same system — `add_action()` is a thin wrapper over
`add_filter()` — but the contract is not, and the contract is what matters.

---

## Registering Callbacks

```php
add_action( string $hook, callable $callback, int $priority = 10, int $accepted_args = 1 );
add_filter( string $hook, callable $callback, int $priority = 10, int $accepted_args = 1 );
```

- **`$priority`** — lower runs earlier. Default `10`. It is an ordering hint, not a
  guarantee: another plugin may register at the same priority, and then registration order
  decides.
- **`$accepted_args`** — how many arguments the callback receives. Omitting it when the hook
  passes more than one is a silent bug: the extra arguments simply never arrive.

**Bad Example** — the filter destroys the value and ignores the second argument

```php
add_filter( 'excerpt_length', 'myplugin_excerpt_length' );

function myplugin_excerpt_length( $length ) {
	// No return: the excerpt length becomes null and WordPress falls back unpredictably.
	$length = 20;
}

add_filter( 'the_content', 'myplugin_append_notice' );

function myplugin_append_notice( $content, $post_id ) {
	// $post_id is never passed — $accepted_args defaults to 1, so this is a fatal
	// ArgumentCountError in PHP 8.
	return $content . myplugin_notice_for( $post_id );
}
```

**Good Example** — returns the value, declares the argument count

```php
add_filter( 'excerpt_length', 'myplugin_excerpt_length' );

function myplugin_excerpt_length( $length ) {
	return 20;
}

add_filter( 'render_block', 'myplugin_annotate_block', 10, 2 );

function myplugin_annotate_block( $block_content, $block ) {
	if ( 'core/quote' !== $block['blockName'] ) {
		return $block_content;   // always return the input unchanged when not applicable
	}

	return $block_content . '<p class="attribution">' . esc_html__( 'Quoted', 'myplugin' ) . '</p>';
}
```

The early return matters as much as the final one: a filter that only sometimes returns a
value is a filter that sometimes erases it.

---

## Choosing the Right Hook

Registering at the wrong moment is the most common reason a callback "does nothing". The
request runs in a fixed order, and a hook that has already fired will never fire again for
that request.

| Hook | Fires | Use it for |
|---|---|---|
| `plugins_loaded` | All plugins loaded, theme not yet | Cross-plugin integration, early bootstrapping |
| `after_setup_theme` | Theme loading | `add_theme_support()`, image sizes, menus |
| `init` | Core fully loaded, user resolved | Post types, taxonomies, shortcodes, rewrite rules |
| `wp_loaded` | Everything loaded, before any query | Work needing the full environment |
| `pre_get_posts` | Before the main query runs | Altering what the page queries |
| `template_redirect` | Query done, template not chosen | Redirects, custom responses, access gates |
| `wp_enqueue_scripts` | Front-end asset stage | `wp_enqueue_script()` / `wp_enqueue_style()` |
| `admin_enqueue_scripts` | Admin asset stage | Admin-only assets |
| `wp_head` / `wp_footer` | Template output | Markup injection (rarely the right answer) |
| `save_post` / `wp_insert_post` | After a post is written | Derived data, cache invalidation, notifications |
| `shutdown` | End of request | Deferred logging; never user-visible output |

Two rules follow from the ordering:

- **`init` is not "early".** By `init`, plugins and the theme have already loaded. Code that
  must run before the theme belongs on `plugins_loaded` or in an mu-plugin.
- **A hook registered after it fired is dead code.** Registering `add_action( 'init', … )`
  from inside a `template_redirect` callback does nothing at all, silently.

```php
// Verify before assuming a hook is still ahead of you.
if ( did_action( 'init' ) ) {
	// 'init' has already run — registering for it now would never fire.
}
```

---

## Modifying the Main Query

`pre_get_posts` is the correct place to change what a page lists — not a second `WP_Query`
inside the template, which runs the query twice and breaks pagination.

**Good Example** — narrow the guard so only the intended query changes

```php
add_action( 'pre_get_posts', 'myplugin_events_archive_query' );

function myplugin_events_archive_query( WP_Query $query ) {
	// Three guards, all required:
	//   is_admin()      — otherwise this also rewrites the admin list table
	//   is_main_query() — otherwise every widget and secondary loop is affected
	//   the context     — otherwise it applies site-wide
	if ( is_admin() || ! $query->is_main_query() ) {
		return;
	}

	if ( ! $query->is_post_type_archive( 'event' ) ) {
		return;
	}

	$query->set( 'posts_per_page', 12 );
	$query->set( 'meta_key', '_event_start' );
	$query->set( 'orderby', 'meta_value' );
	$query->set( 'order', 'ASC' );
}
```

**Bad Example** — unguarded, so it corrupts every query on the site

```php
add_action( 'pre_get_posts', function ( $query ) {
	$query->set( 'posts_per_page', 12 );   // admin lists, widgets, feeds, search — all of it
} );
```

---

## Providing Hooks in Your Own Code

Code meant to be extended should expose its own hooks. Two conventions make them usable:
namespace the name, and pass enough context for a consumer to decide.

```php
/**
 * Filters the plans shown on the pricing page.
 *
 * @param array  $plans   Plan definitions.
 * @param string $context Where the list is rendered ('page' | 'widget').
 */
$plans = apply_filters( 'myplugin_pricing_plans', $plans, $context );

/**
 * Fires after a booking is confirmed.
 *
 * @param int      $booking_id Booking post ID.
 * @param WP_User  $user       User who booked.
 */
do_action( 'myplugin_booking_confirmed', $booking_id, $user );
```

Document each hook where it is defined. An undocumented filter is an accidental API: someone
will depend on it, and its signature then cannot change without breaking them.

---

## Removing Callbacks

`remove_action()` / `remove_filter()` need the **identical** callback reference *and* the
identical priority. Two cases break in practice:

```php
// Works: same function name, same priority.
remove_action( 'wp_head', 'wp_generator' );

// Works: same object instance.
remove_action( 'init', array( $plugin_instance, 'register' ), 20 );

// Impossible: a closure has no stable reference to pass here.
add_action( 'init', function () { /* … */ } );
```

That is the practical argument against closures for hooks in shipped code: they cannot be
removed, replaced, or unit-tested in isolation. Use a named function or a method on an
instance the site can reach.

Timing matters too — removing a callback registered by a plugin requires running *after* that
plugin registered it:

```php
add_action( 'wp_loaded', 'myplugin_unhook_other_plugin' );

function myplugin_unhook_other_plugin() {
	remove_filter( 'the_content', 'other_plugin_inject_banner', 20 );
}
```

---

## Common Mistakes

- **A filter that does not return.** Every path through the callback must return a value.
- **Wrong `$accepted_args`.** Under PHP 8 an unmatched signature is a fatal error, not a
  warning.
- **Unguarded `pre_get_posts`** affecting admin screens, widgets, and feeds.
- **Priority games.** `PHP_INT_MAX` to win an ordering fight is a symptom of a design
  problem, and the next plugin will do the same.
- **Business logic in the callback.** The callback should be a thin adapter that calls a
  service — that service is what you can test without WordPress loaded.
- **Registering too late**, after the hook has already fired.
- **Closures for anything a site might need to remove.**
- **Unprefixed hook names**, colliding with another plugin in the shared namespace.
- **Expensive work on `init`**, which runs on every single request including AJAX and REST.

---

## Debugging a Hook

```php
// Is anything attached, and at what priority?
var_dump( has_filter( 'the_content' ) );          // false, or the priority of the first callback
var_dump( has_action( 'save_post', 'myplugin_sync' ) );

// Which hook is executing right now, and at which priority?
add_filter( 'the_content', function ( $content ) {
	$hook = current_filter();
	$priority = $GLOBALS['wp_filter'][ $hook ]->current_priority();   // WP_Hook method
	error_log( "{$hook} running at priority {$priority}" );
	return $content;
}, 1 );

// Has it already run, and how many times?
error_log( 'init ran ' . did_action( 'init' ) . ' time(s)' );
```

For a full picture of what is attached to a hook, inspect `$GLOBALS['wp_filter']['hook_name']`
in a debugger, or use the Query Monitor plugin — see [Debugging](28-debugging.md).

---

## Verification Checklist

- Does every filter callback return a value on every code path?
- Does `$accepted_args` match the callback signature?
- Is the hook chosen the earliest one that has the data the callback needs?
- Is `pre_get_posts` guarded with `is_admin()`, `is_main_query()`, and a context check?
- Are callbacks named functions or instance methods, so they can be removed and tested?
- Are hook names prefixed, and are custom hooks documented where they are defined?
- Is the callback thin, delegating real work to a testable service?

---

## Summary

Hooks are the contract between your code and everything else on the site. Choose the hook by
what data exists at that moment, keep filters honest by always returning, guard callbacks
that touch shared state, and keep the callback itself thin enough to be obviously correct.

## Related

- `knowledge/wordpress/01-wordpress-architecture.md`
- `knowledge/wordpress/15-plugin-development.md`
- `knowledge/wordpress/12-queries.md`
- `knowledge/wordpress/03-best-practices.md`
- `knowledge/wordpress/100-common-antipatterns.md`
- `knowledge/wordpress/14-theme-development.md`
