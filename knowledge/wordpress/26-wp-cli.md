---
id: wordpress/26-wp-cli
topic: wordpress
slug: wp-cli
title: "WP-CLI"
type: doc
order: 26
status: ready
tags: [wordpress, wp-cli]
related: [wordpress/27-deployment, wordpress/22-cron-and-background-tasks, wordpress/19-database, wordpress/29-maintenance, wordpress/28-debugging]
when_to_use: "Read before automating WordPress from the command line — running maintenance, migrating URLs, scripting deploys, or writing a custom WP-CLI command."
---
# WP-CLI

## Purpose

This document defines how to operate WordPress from the command line: the commands that
matter for maintenance and deployment, why `search-replace` is the only safe way to change
URLs, and how to add project-specific commands.

Anything done repeatedly through the admin UI is a candidate for WP-CLI — it is scriptable,
reviewable, and runs without the execution limits of a web request.

---

## Core Principle

**WP-CLI runs inside a full WordPress bootstrap.** Hooks fire, plugins load, and the object
cache works. That is what separates it from raw SQL: a `wp post delete` triggers the same
cleanup hooks a UI deletion does, while a `DELETE` statement leaves orphaned meta and stale
caches behind.

It also means an error in a plugin can break unrelated CLI commands — and that
`--skip-plugins` and `--skip-themes` are the first diagnostic step when a command fails
mysteriously.

---

## Commands Worth Knowing

```bash
# Environment
wp core version --extra
wp plugin list --status=active --fields=name,version,update
wp theme list
wp cli info

# Content
wp post list --post_type=acme_event --format=count
wp post delete $(wp post list --post_type=revision --format=ids) --force
wp user create editor editor@example.com --role=editor --send-email=false

# Options
wp option get acme_settings --format=json
wp option update acme_settings '{"mode":"live"}' --format=json
wp option list --autoload=on --format=table | head   # find bloated autoloaded options

# Cache and cron
wp cache flush
wp transient delete --all
wp cron event list
wp cron event run --due-now

# Database
wp db export backup-$(date +%F).sql
wp db import backup-2026-07-14.sql
wp db size --tables --human-readable
wp db optimize
```

`wp option list --autoload=on` deserves particular attention during any performance
investigation: autoloaded options load on every single request, and a single oversized entry
left by an abandoned plugin is a common, invisible drag.

---

## `search-replace` and Serialized Data

Changing URLs with SQL corrupts serialized data. PHP serialization encodes string lengths, so
replacing `http://old.test` (15 chars) with `https://new.example` (19 chars) leaves length
prefixes that no longer match — and every affected option silently fails to unserialize.

```bash
# Always dry-run first: it reports what would change, table by table.
wp search-replace 'http://old.test' 'https://new.example' --dry-run --report-changed-only

# Then execute. --precise forces PHP-side replacement (slower, handles every case).
wp search-replace 'http://old.test' 'https://new.example' --precise --skip-columns=guid

# Network-wide.
wp search-replace 'old.test' 'new.example' --network --precise
```

Two flags matter every time:

- **`--skip-columns=guid`.** A post's GUID is a permanent identifier, not a URL. Rewriting it
  makes feed readers treat every existing post as new.
- **`--dry-run`.** Run it, read the table-by-table counts, and confirm they match expectations
  before touching data.

---

## Scripting

WP-CLI output is designed to be composed:

```bash
# Only the value, for use in a shell variable.
SITE_URL=$(wp option get siteurl)

# IDs as input to another command.
wp post delete $(wp post list --post_status=trash --format=ids) --force

# JSON for structured processing.
wp plugin list --format=json | jq -r '.[] | select(.update=="available") | .name'

# Exit codes are meaningful, so guard in scripts.
if ! wp core is-installed; then
	echo "WordPress is not installed here" >&2
	exit 1
fi
```

Useful global flags:

```bash
--url=https://site2.example   # target one site in a network
--path=/var/www/site          # run from outside the install
--skip-plugins --skip-themes  # isolate a failure
--quiet                       # suppress non-error output (good for cron)
```

Avoid `--allow-root`. It exists for containers where nothing else is possible; on a normal
server, running WP-CLI as root creates files the web user cannot manage and turns a compromise
into a root compromise.

---

## Custom Commands

Project-specific operations belong in a command, not a one-off `wp eval`.

```php
<?php
namespace Acme\Events\Cli;

defined( 'ABSPATH' ) || exit;

final class Signup_Command {

	/**
	 * Recalculates cached signup totals for events.
	 *
	 * ## OPTIONS
	 *
	 * [--event-id=<id>]
	 * : Limit to a single event. Defaults to all published events.
	 *
	 * [--dry-run]
	 * : Report what would change without writing.
	 *
	 * ## EXAMPLES
	 *
	 *     wp acme signups recount
	 *     wp acme signups recount --event-id=42 --dry-run
	 *
	 * @param array $args       Positional arguments.
	 * @param array $assoc_args Named arguments.
	 */
	public function recount( array $args, array $assoc_args ): void {
		$dry_run  = isset( $assoc_args['dry-run'] );
		$event_id = isset( $assoc_args['event-id'] ) ? absint( $assoc_args['event-id'] ) : 0;

		$ids = $event_id
			? array( $event_id )
			: get_posts( array( 'post_type' => 'acme_event', 'posts_per_page' => -1, 'fields' => 'ids' ) );

		$progress = \WP_CLI\Utils\make_progress_bar( 'Recounting', count( $ids ) );

		foreach ( $ids as $id ) {
			$total = acme_count_signups( $id );

			if ( ! $dry_run ) {
				update_post_meta( $id, '_acme_signup_total', $total );
			}

			$progress->tick();
		}

		$progress->finish();

		\WP_CLI::success(
			$dry_run
				? sprintf( 'Would update %d event(s).', count( $ids ) )
				: sprintf( 'Updated %d event(s).', count( $ids ) )
		);
	}
}

if ( defined( 'WP_CLI' ) && WP_CLI ) {
	\WP_CLI::add_command( 'acme signups', Signup_Command::class );
}
```

The docblock is not decoration — WP-CLI parses it to produce `wp help acme signups recount`
and to validate arguments.

Output through the WP-CLI API rather than `echo`, so `--quiet` and `--format` behave:

```php
\WP_CLI::log( 'Informational' );        // suppressed by --quiet
\WP_CLI::success( 'Done' );
\WP_CLI::warning( 'Skipped 3 rows' );
\WP_CLI::error( 'Cannot continue' );     // prints and exits with status 1
\WP_CLI\Utils\format_items( 'table', $rows, array( 'id', 'title' ) );
```

Guard registration with `defined( 'WP_CLI' )` — the class must not load on web requests.

---

## Bulk Work Belongs Here

CLI has no `max_execution_time` from the web server and no user waiting on a response, which
makes it the right place for migrations and backfills. It still has memory limits, so iterate
in batches:

```php
$paged = 1;

do {
	$ids = get_posts( array(
		'post_type'      => 'acme_event',
		'posts_per_page' => 200,
		'paged'          => $paged,
		'fields'         => 'ids',
		'no_found_rows'  => true,
	) );

	foreach ( $ids as $id ) {
		acme_migrate_event( $id );
	}

	// Object cache and query log grow unbounded across a long run.
	wp_cache_flush();

	$paged++;
} while ( ! empty( $ids ) );
```

---

## Examples

**Good Example** — a dry run first, then the real one, through WordPress

```bash
# search-replace understands serialized data; a SQL REPLACE() corrupts it.
# --dry-run reports the row count without writing anything.
wp search-replace 'https://staging.example.com' 'https://example.com' \
  --all-tables-with-prefix --precise --recurse-objects --dry-run

# Same command without --dry-run once the report looks right.
wp search-replace 'https://staging.example.com' 'https://example.com' \
  --all-tables-with-prefix --precise --recurse-objects

# Deleting through WP-CLI fires the same hooks the admin UI does, so meta,
# term relationships, and caches are cleaned up.
wp post delete $(wp post list --post_type=myplugin_event --post_status=trash --format=ids) --force

# Bulk work belongs here, not in an admin-page loop that dies on the PHP time limit.
wp eval-file scripts/backfill-event-slugs.php --quiet
```

**Bad Example** — raw SQL against the same data

```bash
# REPLACE() rewrites the bytes inside serialized strings without fixing their length
# prefixes, so every option holding a serialized array silently stops unserializing.
wp db query "UPDATE wp_options SET option_value =
  REPLACE(option_value, 'https://staging.example.com', 'https://example.com')"

# Deletes the rows and nothing else: postmeta, term relationships, and the object
# cache all keep pointing at posts that no longer exist.
wp db query "DELETE FROM wp_posts WHERE post_type = 'myplugin_event'"
```

---

## Common Mistakes

- **SQL `UPDATE` for URL changes**, corrupting serialized data.
- **`search-replace` without `--dry-run`**, or without `--skip-columns=guid`.
- **`--allow-root` as a habit.**
- **`wp eval` for anything repeated**, instead of a documented command.
- **`echo` in a command**, breaking `--quiet` and machine-readable output.
- **Registering a command without `defined( 'WP_CLI' )`**, loading it on web requests.
- **Unbatched bulk operations**, exhausting memory on large sites.
- **No `--dry-run` on destructive commands.**
- **Forgetting `--url`** on multisite, so the command silently targets the main site.

---

## Verification Checklist

- Is this operation scripted rather than performed by hand in the admin?
- Does any URL change go through `search-replace`, dry-run first, with `guid` skipped?
- Do custom commands carry a parsed docblock and use the WP-CLI output API?
- Is command registration guarded by `defined( 'WP_CLI' )`?
- Do destructive commands support `--dry-run`?
- Is bulk work batched with cache flushes between batches?
- On multisite, is `--url` passed explicitly?
- Is a database export taken before any migration command?

---

## Summary

WP-CLI runs real WordPress, so hooks and caches behave correctly. Use it for migrations,
maintenance, and deploys; change URLs only through `search-replace`; and package repeated
project operations as documented commands with dry-run support.

## Related

- `knowledge/wordpress/22-cron-and-background-tasks.md`
- `knowledge/wordpress/27-deployment.md`
- `knowledge/wordpress/29-maintenance.md`
- `knowledge/wordpress/28-debugging.md`
