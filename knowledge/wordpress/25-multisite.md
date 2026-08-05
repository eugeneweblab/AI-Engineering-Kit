---
id: wordpress/25-multisite
topic: wordpress
slug: multisite
title: "WordPress Multisite"
type: doc
order: 25
status: ready
tags: [wordpress, multisite, switch_to_blog, restore_current_blog, get_sites, update_option, get_option, current_user_can]
related: [wordpress/19-database, wordpress/20-users-and-capabilities, wordpress/15-plugin-development, wordpress/27-deployment, wordpress/21-media-and-uploads, wordpress/26-wp-cli]
when_to_use: "Read before building for or deciding on a WordPress network — writing multisite-aware code, switching between sites, or evaluating whether multisite fits."
---
# WordPress Multisite

## Purpose

This document defines how WordPress multisite differs from a single site: which data is shared
and which is per-site, how to write code that works on both, and when a network is the wrong
answer.

Most multisite bugs come from code written on a single install where `$wpdb->prefix`,
`get_option()`, and capability checks all behaved as if there were only one site.

---

## Core Principle

**A network is many sites sharing one codebase, one users table, and one database.**
Everything else is per-site.

| Shared across the network | Per-site |
|---|---|
| Users and user meta | Posts, pages, all content |
| Plugin and theme **files** | Which plugins and themes are **active** |
| Network options (`wp_sitemeta`) | Options (`wp_2_options`) |
| The PHP process and its constants | Uploads (`uploads/sites/2/`) |

A user therefore exists once but has a different role on each site — which is why permission
state must never be cached across a site switch.

---

## When Multisite Is the Wrong Answer

Multisite is genuinely useful for many sites under one administration with one codebase:
university departments, franchise locations, a network of publications.

It is the wrong tool when:

- Sites need **different plugin sets or versions** — the files are shared, so they cannot.
- Sites have **different owners or clients** — a network admin can reach everything, and a
  plugin vulnerability on one site compromises all of them.
- Sites will be **sold, migrated, or spun out** — extracting one site from a network is
  painful, unlike copying a standalone install.
- The requirement is really **one site with sections**, which categories or a CPT solve.

The decision is difficult to reverse. Make it deliberately.

---

## Switching Between Sites

`switch_to_blog()` changes `$wpdb->prefix` and the option context. Every switch must be
restored, on every path.

**Good Example** — `try`/`finally` guarantees restoration even on an exception or early return

```php
foreach ( get_sites( array( 'fields' => 'ids', 'number' => 0 ) ) as $site_id ) {
	switch_to_blog( $site_id );

	try {
		$count = wp_count_posts( 'acme_event' )->publish;
		acme_record_site_total( $site_id, $count );
	} finally {
		restore_current_blog();
	}
}
```

**Bad Example** — an exception or `continue` leaves the whole request pointed at the wrong
site, so everything after it reads and writes the wrong data

```php
foreach ( $site_ids as $site_id ) {
	switch_to_blog( $site_id );
	if ( ! acme_site_is_active( $site_id ) ) {
		continue;                       // never restored
	}
	do_expensive_thing();
	restore_current_blog();
}
```

Two further cautions:

- `switch_to_blog()` does **not** reset every cache or global. Plugins that cached data in a
  static property before the switch keep serving the previous site's values.
- Switching is not free. Iterating hundreds of sites on a web request will time out; do it
  from WP-CLI or a scheduled job instead — see [WP-CLI](26-wp-cli.md).

---

## Options: Site or Network

```php
// Per-site: stored in wp_{id}_options.
get_option( 'acme_settings' );
update_option( 'acme_settings', $value );

// Network-wide: stored in wp_sitemeta. On a single site these fall back to
// get_option()/update_option(), so they are safe to use unconditionally.
get_network_option( null, 'acme_license_key' );
update_network_option( null, 'acme_license_key', $key );
```

Decide per setting: a license key or API credential is usually network-level, while display
preferences are per-site. Writing a network setting with `update_option()` silently stores it
on whichever site happened to be active.

---

## Plugin Activation

A network-activated plugin runs on every site, and its activation hook fires **once** with a
flag rather than once per site.

```php
register_activation_hook( ACME_EVENTS_FILE, 'acme_activate' );

function acme_activate( bool $network_wide ): void {
	if ( is_multisite() && $network_wide ) {
		foreach ( get_sites( array( 'fields' => 'ids', 'number' => 0 ) ) as $site_id ) {
			switch_to_blog( $site_id );
			try {
				acme_activate_single_site();
			} finally {
				restore_current_blog();
			}
		}
		return;
	}

	acme_activate_single_site();
}
```

Sites created *after* network activation never run that code, so handle them too:

```php
add_action( 'wp_initialize_site', function ( WP_Site $site ) {
	if ( ! is_plugin_active_for_network( plugin_basename( ACME_EVENTS_FILE ) ) ) {
		return;
	}

	switch_to_blog( $site->blog_id );
	try {
		acme_activate_single_site();   // create tables, set defaults, flush rules
	} finally {
		restore_current_blog();
	}
}, 10, 1 );
```

---

## Database Tables

```php
$wpdb->prefix        // wp_2_ on site 2 — per-site tables
$wpdb->base_prefix   // wp_   — network tables (users, usermeta, blogs, sitemeta)
```

A custom table must choose one. Per-site tables mean `$wpdb->prefix` and one table per site;
a shared table means `$wpdb->base_prefix` and a `blog_id` column. Both are valid; picking by
accident is not.

```php
// Shared table: always filter by site.
$table = $wpdb->base_prefix . 'acme_events_log';
$wpdb->get_results(
	$wpdb->prepare( "SELECT * FROM {$table} WHERE blog_id = %d", get_current_blog_id() )
);
```

---

## Capabilities on a Network

```php
is_super_admin( $user_id );                    // above every role, on every site
current_user_can( 'manage_network_options' );  // network administration
current_user_can( 'manage_options' );          // administration of the current site
```

Because roles are per-site, a check made before a switch does not hold after it. Re-check
after switching rather than caching the result — see
[Users and Capabilities](20-users-and-capabilities.md).

---

## Uploads and URLs

Each site has its own uploads path (`wp-content/uploads/sites/2/`) and its own domain or path.
Never build these by hand:

```php
$upload_dir = wp_upload_dir();      // correct for the current site after any switch
$home       = home_url( '/' );      // site
$network    = network_home_url();   // network
$admin      = admin_url();          // site admin
$net_admin  = network_admin_url();  // network admin
```

Hardcoded paths and URLs are the single most common reason a plugin "works on the main site
only".

---

## Common Mistakes

- **`switch_to_blog()` without a guaranteed `restore_current_blog()`.**
- **`update_option()` for a value that should be network-wide.**
- **Activation code that runs once**, leaving other sites — and future sites — uninitialized.
- **`$wpdb->prefix` where `base_prefix` was meant**, or the reverse.
- **Caching capabilities or user state across a switch.**
- **Hardcoded upload paths and URLs.**
- **Iterating every site on a web request**, timing out as the network grows.
- **Assuming plugin files can differ per site** — they cannot.
- **Choosing multisite for unrelated client sites**, coupling their security and uptime.

---

## Verification Checklist

- Does the code work unchanged on both a single site and a network?
- Is every `switch_to_blog()` restored on every path, ideally with `try`/`finally`?
- Is each setting deliberately per-site or network-wide?
- Does activation cover existing sites, and does `wp_initialize_site` cover new ones?
- Do custom tables use the right prefix, with `blog_id` if shared?
- Are capabilities re-checked after switching rather than cached?
- Are all paths and URLs derived from WordPress functions?
- Is bulk cross-site work run from CLI or cron rather than a web request?

---

## Summary

A network shares code and users but separates content, options, and uploads. Write code that
asks WordPress for the current context instead of assuming it, restore every switch, and treat
the choice to run multisite as an architectural commitment that is hard to undo.

## Related

- `knowledge/wordpress/19-database.md`
- `knowledge/wordpress/20-users-and-capabilities.md`
- `knowledge/wordpress/15-plugin-development.md`
- `knowledge/wordpress/27-deployment.md`
- `knowledge/wordpress/21-media-and-uploads.md`
- `knowledge/wordpress/26-wp-cli.md`
