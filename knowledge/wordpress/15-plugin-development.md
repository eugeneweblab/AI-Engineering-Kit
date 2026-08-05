---
id: wordpress/15-plugin-development
topic: wordpress
slug: plugin-development
title: "Plugin Development"
type: doc
order: 15
status: ready
tags: [wordpress, plugin-development]
related: [wordpress/02-project-structure, wordpress/08-hooks, wordpress/09-custom-post-types, wordpress/27-deployment, wordpress/06-security]
when_to_use: "Read before building a plugin — structuring the entry file, handling activation and uninstall, loading classes, or declaring dependencies."
---
# Plugin Development

## Purpose

This document defines how to structure a WordPress plugin: the entry file contract, class
loading, lifecycle hooks (activation, deactivation, uninstall), dependency checks, and schema
versioning.

A plugin is the correct home for anything that must survive a theme change: content types,
business logic, integrations, and admin functionality.

---

## Core Principle

The main plugin file **registers**; it does not **execute**. Everything expensive happens on
a hook, so that loading the plugin file is nearly free.

```php
<?php
/**
 * Plugin Name:       Acme Events
 * Description:       Event content type, listings, and registration.
 * Version:           1.4.0
 * Requires at least: 6.4
 * Requires PHP:      8.1
 * Author:            Acme
 * License:           GPL-2.0-or-later
 * Text Domain:       acme-events
 * Domain Path:       /languages
 */

// Never allow direct file access — the file is web-reachable.
defined( 'ABSPATH' ) || exit;

define( 'ACME_EVENTS_VERSION', '1.4.0' );
define( 'ACME_EVENTS_FILE', __FILE__ );
define( 'ACME_EVENTS_PATH', plugin_dir_path( __FILE__ ) );
define( 'ACME_EVENTS_URL', plugin_dir_url( __FILE__ ) );

require_once ACME_EVENTS_PATH . 'vendor/autoload.php';

// Registration only. No queries, no output, no side effects at file scope.
add_action( 'plugins_loaded', array( \Acme\Events\Plugin::class, 'boot' ) );
```

`defined( 'ABSPATH' ) || exit;` belongs at the top of **every** PHP file in the plugin. Files
under `wp-content/plugins/` are served by the web server, and without the guard they execute
outside WordPress.

---

## Directory Layout

```
acme-events/
├── acme-events.php          entry file: header, constants, bootstrap
├── uninstall.php            data removal on delete
├── composer.json            autoloading, dev tooling
├── src/
│   ├── Plugin.php           wiring: which hooks call which services
│   ├── PostTypes/Event.php
│   ├── Rest/EventsController.php
│   └── Services/Registration.php   ← testable, no WordPress functions where avoidable
├── templates/               overridable by the theme
├── assets/
└── languages/
```

Use Composer's PSR-4 autoloader rather than a hand-written `require` list — it loads classes
on demand instead of on every request:

```json
{
  "autoload": { "psr-4": { "Acme\\Events\\": "src/" } },
  "config": { "optimize-autoloader": true }
}
```

---

## Wiring

Keep hook registration in one place. It becomes the map of what the plugin does.

```php
<?php
namespace Acme\Events;

defined( 'ABSPATH' ) || exit;

final class Plugin {

	public static function boot(): void {
		$plugin = new self();
		$plugin->register_hooks();
	}

	private function register_hooks(): void {
		add_action( 'init', array( new PostTypes\Event(), 'register' ) );
		add_action( 'rest_api_init', array( new Rest\EventsController(), 'register_routes' ) );
		add_action( 'wp_enqueue_scripts', array( $this, 'enqueue_assets' ) );

		// Instance methods, not closures — so a site can remove them if needed.
	}

	public function enqueue_assets(): void {
		if ( ! is_singular( 'acme_event' ) ) {
			return;                       // load nothing on pages that do not need it
		}

		wp_enqueue_script(
			'acme-events',
			ACME_EVENTS_URL . 'assets/js/events.js',
			array(),
			ACME_EVENTS_VERSION,
			true
		);
	}
}
```

---

## Lifecycle Hooks

The three lifecycle hooks have different rules, and each is easy to get wrong.

```php
register_activation_hook( ACME_EVENTS_FILE, array( Installer::class, 'activate' ) );
register_deactivation_hook( ACME_EVENTS_FILE, array( Installer::class, 'deactivate' ) );
```

```php
final class Installer {

	public static function activate(): void {
		// Post types must be registered before flushing, or their rules are not written.
		( new PostTypes\Event() )->register();
		flush_rewrite_rules();

		self::maybe_upgrade_schema();

		// Schedule recurring work here, not on init.
		if ( ! wp_next_scheduled( 'acme_events_daily_cleanup' ) ) {
			wp_schedule_event( time() + HOUR_IN_SECONDS, 'daily', 'acme_events_daily_cleanup' );
		}
	}

	public static function deactivate(): void {
		wp_clear_scheduled_hook( 'acme_events_daily_cleanup' );
		flush_rewrite_rules();
		// Deactivation must NOT delete data — users deactivate to troubleshoot.
	}
}
```

**Uninstall** is separate and runs in an isolated request where the plugin is not loaded.
Prefer `uninstall.php` over `register_uninstall_hook()`:

```php
<?php
// uninstall.php — runs only when the user deletes the plugin.
defined( 'WP_UNINSTALL_PLUGIN' ) || exit;

delete_option( 'acme_events_settings' );
delete_option( 'acme_events_db_version' );

// Multisite: options are per-site, so iterate.
if ( is_multisite() ) {
	foreach ( get_sites( array( 'fields' => 'ids' ) ) as $site_id ) {
		switch_to_blog( $site_id );
		delete_option( 'acme_events_settings' );
		restore_current_blog();
	}
}

// Deleting user content on uninstall should be opt-in, never automatic.
```

---

## Dependency Checks

A plugin that requires another must fail visibly rather than fatally:

```php
add_action( 'plugins_loaded', 'acme_events_check_dependencies', 5 );   // before boot

function acme_events_check_dependencies(): void {
	if ( class_exists( 'WooCommerce' ) ) {
		return;
	}

	remove_action( 'plugins_loaded', array( \Acme\Events\Plugin::class, 'boot' ) );

	add_action( 'admin_notices', function () {
		printf(
			'<div class="notice notice-error"><p>%s</p></div>',
			esc_html__( 'Acme Events requires WooCommerce to be active.', 'acme-events' )
		);
	} );
}
```

For PHP and WordPress versions, the `Requires PHP` and `Requires at least` headers let core
block activation entirely — cheaper and more reliable than a runtime check.

---

## Schema Versioning

Database changes need a version marker, checked on load rather than only on activation —
plugins are often updated by file replacement, which never fires the activation hook.

```php
add_action( 'plugins_loaded', 'acme_events_maybe_upgrade' );

function acme_events_maybe_upgrade(): void {
	$installed = get_option( 'acme_events_db_version', '0' );

	if ( version_compare( $installed, ACME_EVENTS_VERSION, '>=' ) ) {
		return;
	}

	require_once ABSPATH . 'wp-admin/includes/upgrade.php';

	global $wpdb;
	$table   = $wpdb->prefix . 'acme_event_signups';
	$charset = $wpdb->get_charset_collate();

	// dbDelta compares against the existing schema and applies the difference.
	// It is strict about formatting: two spaces after PRIMARY KEY, one field per line.
	dbDelta(
		"CREATE TABLE {$table} (
			id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
			event_id bigint(20) unsigned NOT NULL,
			user_id bigint(20) unsigned NOT NULL,
			created_at datetime NOT NULL,
			PRIMARY KEY  (id),
			KEY event_id (event_id)
		) {$charset};"
	);

	update_option( 'acme_events_db_version', ACME_EVENTS_VERSION );
}
```

See [Database](19-database.md) for when a custom table is justified at all.

---

## Must-Use Plugins

Code in `wp-content/mu-plugins/` loads before regular plugins, cannot be deactivated from the
admin, and is the right place for infrastructure that must always run — environment
configuration, security hardening, or a site-specific bootstrap. Note that only PHP files at
the top level of `mu-plugins/` load automatically; subdirectories need a loader file.

---

## Common Mistakes

- **Work at file scope** — queries, output, or registration outside a hook.
- **Missing `defined( 'ABSPATH' ) || exit;`**, leaving files directly executable.
- **Deleting data on deactivation** rather than on uninstall.
- **`flush_rewrite_rules()` on `init`** instead of on activation.
- **Unprefixed globals** — functions, classes, options, and post types share one namespace.
- **`register_uninstall_hook()` with a closure**, which cannot be serialized and silently
  never runs.
- **Schema upgrades only on activation**, skipped by file-replacement updates.
- **Assuming a dependency is active** and fataling when it is not.
- **Loading every asset on every page** instead of checking context first.
- **Business logic inside hook callbacks**, leaving nothing testable without WordPress.

---

## Verification Checklist

- Does the entry file only define constants and register hooks?
- Does every PHP file guard against direct access?
- Are classes autoloaded rather than unconditionally required?
- Are activation, deactivation, and uninstall each doing only what belongs to that phase?
- Is data removal opt-in and confined to `uninstall.php`?
- Are dependencies and version requirements declared and checked?
- Does the schema upgrade run on load, not only on activation?
- Is everything global prefixed?
- Are assets enqueued conditionally?

---

## Summary

A plugin's entry file registers and delegates; its lifecycle hooks each have one job;
its data is removed only on uninstall; and its logic lives in classes that can be tested
without loading WordPress.
