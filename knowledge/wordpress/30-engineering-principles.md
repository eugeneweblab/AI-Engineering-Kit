---
id: wordpress/30-engineering-principles
topic: wordpress
slug: engineering-principles
title: "WordPress Engineering Principles"
type: doc
order: 30
status: ready
tags: [wordpress, engineering-principles, WP_Query, wp_reset_postdata, flush_rewrite_rules, the_post, have_posts, get_the_ID, regardless, satisfy, plugin]
related: [wordpress/01-wordpress-architecture, wordpress/06-security, wordpress/08-hooks, wordpress/99-ai-review-checklist, wordpress/100-common-antipatterns]
when_to_use: "Read before writing or reviewing any WordPress code, as the baseline every file must satisfy regardless of whether it is a theme, plugin, or block."
---
# WordPress Engineering Principles

## Purpose

This document defines the non-negotiable principles for WordPress code: the baseline an agent
applies to every file it authors or reviews, whether the work is a theme, a plugin, a block,
or a one-line filter. Topic-specific detail lives in the sibling documents; this one covers
the reasoning that holds across all of them.

## Why It Matters

WordPress is unusually permissive. It will run a plugin that queries inside a loop, echoes
unescaped user input, edits core files, and stores a megabyte of autoloaded options — and the
site will appear to work. Nothing in the platform stops any of it. The consequences arrive
later and elsewhere: a page that took 200ms now takes 4s, an update erases a customization
nobody documented, a form field becomes stored XSS.

That permissiveness is why WordPress needs an explicit baseline more than a framework with
opinions does. The principles below are the ones whose violation is invisible at the time and
expensive afterwards.

## Core Principles

- **Never modify what you do not own.** Core, parent themes, and third-party plugins are
  replaced on update. Extend through hooks, child themes, and template overrides. An edit
  outside your own code is a defect regardless of how well it works today.
- **Escape at output, sanitize at input, validate before use.** The three are distinct
  operations at distinct moments, and doing one does not cover the others. The output context
  determines the function — `esc_html()`, `esc_attr()`, `esc_url()`, `wp_kses_post()`.
- **Check the capability, verify the nonce.** A capability answers "may this user"; a nonce
  answers "did they intend this, now". Every state-changing request needs both, and the
  capability check must name the object when there is one.
- **Prefix everything global.** Functions, classes, hooks, post types, taxonomies, meta keys,
  and options share one namespace with every other plugin on the site. An unprefixed name is
  a collision waiting for the right combination of plugins.
- **Never query inside a loop.** Batch, prime the cache, or restructure the query. This single
  rule accounts for most of the difference between a fast and a slow WordPress site.
- **Content belongs in plugins, presentation in themes.** If switching the theme should not
  delete it, it is not theme code.
- **Register on the right hook, and only register.** File scope declares; hooks execute. Work
  at file scope runs on every request, including AJAX, REST, and cron.
- **Bound every result set.** `posts_per_page => -1`, unbounded `meta_query`, and unpaginated
  REST collections all work fine until the data grows.
- **Make it translatable as you write.** Retrofitting internationalization means finding every
  string that was never wrapped.
- **Assume the code runs on multisite.** `$wpdb->prefix`, `get_option()`, and capability
  checks all behave differently there, and the discovery usually comes long after launch.

## Best Practices

- Keep hook callbacks thin: a callback should adapt WordPress to a service, and the service
  should be testable without WordPress loaded.
- Use named functions or instance methods for hooks, not closures — a closure cannot be
  removed, replaced, or tested in isolation.
- Prefer the API (`WP_Query`, meta functions) over `$wpdb`, and `$wpdb->prepare()` without
  exception when raw SQL is genuinely required.
- Return `WP_Error` for failure, and check `is_wp_error()` on everything that can return one.
- Register post types, taxonomies, and meta with explicit arguments — `show_in_rest`,
  `supports`, `sanitize_callback`, `auth_callback` — rather than relying on defaults.
- Flush rewrite rules on activation only, never on `init`.
- Enqueue assets through the queue, conditionally, with versions derived from file mtime.
- Treat block attributes and saved markup as a content contract; ship deprecations when it
  changes.
- Cache what is expensive and stable, key it by everything that changes the result, and
  invalidate it where the data is written.
- Delete data on uninstall, never on deactivation.

## Examples

**Bad Example** — plausible code that violates six principles at once

```php
// functions.php
add_action( 'init', function () {
	register_post_type( 'event', array( 'public' => true ) );   // unprefixed, in the theme,
	flush_rewrite_rules();                                       // flushing on every request
} );

function show_events() {
	$events = new WP_Query( array( 'post_type' => 'event', 'posts_per_page' => -1 ) );

	while ( $events->have_posts() ) {
		$events->the_post();
		$venue = get_posts( array( 'meta_key' => 'event', 'meta_value' => get_the_ID() ) );  // query in loop
		echo '<h3>' . get_the_title() . '</h3>';                                              // unescaped
		echo '<p>Venue: ' . $venue[0]->post_title . '</p>';                                   // unescaped, unchecked
	}
	// no wp_reset_postdata()
}
```

**Good Example** — the same feature, corrected

```php
// plugin: content model lives where it survives a theme change
add_action( 'init', 'acme_register_event_type' );

function acme_register_event_type(): void {
	register_post_type( 'acme_event', array(
		'public'       => true,
		'has_archive'  => 'events',
		'show_in_rest' => true,
		'supports'     => array( 'title', 'editor', 'thumbnail', 'revisions' ),
	) );
}

register_activation_hook( ACME_FILE, function () {
	acme_register_event_type();
	flush_rewrite_rules();              // once, on activation
} );

function acme_render_events(): void {
	$events = new WP_Query( array(
		'post_type'      => 'acme_event',
		'posts_per_page' => 12,          // bounded
		'no_found_rows'  => true,
	) );

	// One query for every venue, outside the loop.
	$venues = acme_venues_for( wp_list_pluck( $events->posts, 'ID' ) );

	while ( $events->have_posts() ) {
		$events->the_post();
		$venue = $venues[ get_the_ID() ] ?? null;

		printf( '<h3>%s</h3>', esc_html( get_the_title() ) );

		if ( $venue ) {
			printf(
				/* translators: %s: venue name. */
				'<p>' . esc_html__( 'Venue: %s', 'acme' ) . '</p>',
				esc_html( $venue->post_title )
			);
		}
	}

	wp_reset_postdata();
}
```

## Common Mistakes

- Editing core, a parent theme, or a third-party plugin instead of hooking.
- Escaping at input and outputting raw, or escaping once and assuming it holds everywhere.
- A nonce without a capability check, or a capability check without a nonce.
- Checking a role name rather than a capability.
- Unprefixed global names.
- Queries inside loops, and unbounded result sets.
- Content modelling in `functions.php`.
- Work at file scope rather than on a hook.
- Strings never wrapped for translation.
- Data deleted on deactivation rather than uninstall.

## Production Tips

- Run PHPCS with the WordPress standard in CI; it catches escaping, prefixing, and style
  violations before review does.
- Keep `WP_DEBUG` on in development and `WP_DEBUG_DISPLAY` off everywhere — deprecation
  notices are early warning of the next breaking release.
- Watch autoloaded options and query counts as standing metrics; both grow silently.
- Test on multisite before claiming multisite compatibility.
- Treat every plugin added as a permanent maintenance obligation, not a free feature.

## AI Review Checklist

- Is anything modified that the project does not own?
- Is every dynamic value escaped for its exact output context?
- Does every state-changing path verify both capability and nonce?
- Is every global name prefixed?
- Are there queries inside loops, or unbounded result sets?
- Is content modelling in a plugin rather than the theme?
- Does file scope only declare, with all work on hooks?
- Are user-facing strings translatable with a literal text domain?
- Would this code behave correctly on multisite?
- Is data removal confined to uninstall?

## Related

- `knowledge/wordpress/01-wordpress-architecture.md`
- `knowledge/wordpress/06-security.md`
- `knowledge/wordpress/08-hooks.md`
- `knowledge/wordpress/99-ai-review-checklist.md`
- `knowledge/wordpress/100-common-antipatterns.md`
