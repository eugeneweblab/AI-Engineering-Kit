---
id: wordpress/19-database
topic: wordpress
slug: database
title: "Database and $wpdb"
type: doc
order: 19
status: ready
tags: [wordpress, database]
related: [wordpress/12-queries, wordpress/11-metadata, wordpress/06-security, wordpress/15-plugin-development, wordpress/05-performance, wordpress/25-multisite, security/13-sql-injection]
when_to_use: "Read before writing direct SQL in WordPress — using $wpdb, deciding whether a custom table is justified, or creating and migrating schema."
---
# Database and `$wpdb`

## Purpose

This document defines how to work with the database directly: preparing statements safely,
deciding when a custom table is justified over post meta, creating schema with `dbDelta()`,
and the multisite details that break code written on a single site.

Direct SQL is a last resort in WordPress, but a legitimate one. The API layer cannot express
every query, and forcing it to produces slower code than a well-written statement.

---

## Core Principle

**Use the API until it cannot answer the question.** `WP_Query`, `get_posts()`, and the meta
functions come with object caching, filters that plugins depend on, and multisite awareness.
A raw query has none of that, so it must earn its place.

Direct SQL is justified when:

- The query aggregates (`COUNT`, `SUM`, `GROUP BY`) — the API has no equivalent.
- The data lives in a custom table.
- A bulk operation would otherwise load thousands of objects into memory.
- An unavoidable join cannot be expressed as `meta_query` without becoming slower.

It is not justified for fetching posts, reading meta, or anything with a one-line API call.

---

## Preparing Statements

Every value interpolated into SQL goes through `$wpdb->prepare()`. There is no exception.

**Bad Example** — SQL injection

```php
global $wpdb;
$results = $wpdb->get_results( "SELECT * FROM {$wpdb->posts} WHERE post_title = '{$title}'" );
```

**Good Example**

```php
global $wpdb;

$results = $wpdb->get_results(
	$wpdb->prepare(
		"SELECT ID, post_title FROM {$wpdb->posts}
		 WHERE post_type = %s AND post_status = %s AND post_date > %s
		 LIMIT %d",
		'acme_event',
		'publish',
		$since,
		20
	)
);
```

Placeholders: `%s` string, `%d` integer, `%f` float, `%i` identifier (table or column name,
WordPress 6.2+). Table names from `$wpdb` properties are safe to interpolate; anything derived
from input is not.

Two details that bite:

```php
// LIKE requires esc_like() BEFORE prepare(), or user '%' becomes a wildcard.
$like = '%' . $wpdb->esc_like( $search ) . '%';
$wpdb->prepare( "SELECT ID FROM {$wpdb->posts} WHERE post_title LIKE %s", $like );

// IN () needs one placeholder per value — built, then prepared.
$ids          = array_map( 'absint', $ids );
$placeholders = implode( ',', array_fill( 0, count( $ids ), '%d' ) );
$wpdb->get_col(
	$wpdb->prepare( "SELECT ID FROM {$wpdb->posts} WHERE ID IN ({$placeholders})", $ids )
);
```

---

## Reading and Writing

```php
$count = $wpdb->get_var( $wpdb->prepare( "SELECT COUNT(*) FROM {$table} WHERE event_id = %d", $id ) );
$row   = $wpdb->get_row( $wpdb->prepare( "SELECT * FROM {$table} WHERE id = %d", $id ) );
$col   = $wpdb->get_col( "SELECT DISTINCT event_id FROM {$table}" );
$rows  = $wpdb->get_results( "SELECT * FROM {$table} LIMIT 100", ARRAY_A );
```

`insert()`, `update()`, and `delete()` escape automatically when given formats — no `prepare()`
needed, and safer than assembling SQL:

```php
$wpdb->insert(
	$table,
	array( 'event_id' => $event_id, 'user_id' => $user_id, 'created_at' => current_time( 'mysql' ) ),
	array( '%d', '%d', '%s' )      // formats: omitting these falls back to %s for everything
);
$new_id = $wpdb->insert_id;

$wpdb->update(
	$table,
	array( 'status' => 'confirmed' ),      // data
	array( 'id' => $row_id ),              // where
	array( '%s' ),                          // data formats
	array( '%d' )                           // where formats
);
```

Always check for failure — `$wpdb` does not throw:

```php
if ( false === $wpdb->insert( $table, $data, $formats ) ) {
	error_log( 'Signup insert failed: ' . $wpdb->last_error );
	return new WP_Error( 'acme_db_error', __( 'Could not save signup.', 'acme-events' ) );
}
```

---

## When a Custom Table Is Justified

Post meta is the default and handles most cases. A custom table is worth its cost when:

- The data is **not content** — logs, analytics, queue rows, relationships.
- Row counts run to **hundreds of thousands**, where `wp_postmeta` becomes a bottleneck.
- Queries need **real indexes** on values, which `meta_value` cannot provide.
- The rows have a **fixed shape** that a key-value store models badly.

The costs are real and permanent: no object caching, no REST or admin UI, no export or
migration tooling, and every backup and staging workflow must be taught about the table.

```php
require_once ABSPATH . 'wp-admin/includes/upgrade.php';

global $wpdb;
$table   = $wpdb->prefix . 'acme_event_signups';
$charset = $wpdb->get_charset_collate();

// dbDelta is strict: two spaces after PRIMARY KEY, one definition per line,
// lowercase types, and KEY (not INDEX).
dbDelta(
	"CREATE TABLE {$table} (
		id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
		event_id bigint(20) unsigned NOT NULL,
		user_id bigint(20) unsigned NOT NULL,
		status varchar(20) NOT NULL DEFAULT 'pending',
		created_at datetime NOT NULL,
		PRIMARY KEY  (id),
		KEY event_id (event_id),
		KEY user_event (user_id,event_id)
	) {$charset};"
);
```

`dbDelta()` compares the definition against the live schema and applies the difference, which
makes it safe to run on every upgrade — see the schema-versioning pattern in
[Plugin Development](15-plugin-development.md). It does not drop columns or indexes you
remove, so cleanup is manual.

---

## Multisite

`$wpdb->prefix` changes per site; `$wpdb->base_prefix` does not.

```php
$wpdb->prefix         // wp_2_  on site 2 — per-site tables
$wpdb->base_prefix    // wp_    — network-wide tables (users, usermeta)
```

Decide deliberately which one a custom table uses. A per-site table gives each site its own
data; a network table shares it. Getting this wrong is discovered only when the plugin is
activated on a second site — often long after launch.

```php
// Iterate every site correctly.
foreach ( get_sites( array( 'fields' => 'ids' ) ) as $site_id ) {
	switch_to_blog( $site_id );
	// $wpdb->prefix now points at this site
	restore_current_blog();      // always restore, even on early return
}
```

---

## Transactions

WordPress has no transaction API, but InnoDB supports them through raw queries:

```php
$wpdb->query( 'START TRANSACTION' );

try {
	$wpdb->insert( $signups, $signup_data, $signup_formats );
	$wpdb->update( $events, array( 'seats_taken' => $taken + 1 ), array( 'id' => $event_id ), array( '%d' ), array( '%d' ) );

	if ( $wpdb->last_error ) {
		throw new RuntimeException( $wpdb->last_error );
	}

	$wpdb->query( 'COMMIT' );
} catch ( Throwable $e ) {
	$wpdb->query( 'ROLLBACK' );
	error_log( 'Signup transaction failed: ' . $e->getMessage() );
}
```

Two caveats: core tables are InnoDB on modern installs but this is not guaranteed on old
hosts, and DDL statements cause an implicit commit — never mix schema changes into a
transaction.

---

## Performance

- **Index what you filter and sort on.** A custom table without indexes performs worse than
  post meta, which at least indexes the key.
- **Never `SELECT *`** when you need two columns; row size drives memory and network cost.
- **Batch bulk operations.** A `DELETE` over a million rows locks the table; loop in chunks of
  a few thousand with a `LIMIT`.
- **Cache aggregates.** `COUNT(*)` over a large table on every page load is a self-inflicted
  outage; cache it — see [Caching](23-caching.md).
- **Profile with `SAVEQUERIES`** in development, or Query Monitor, to see the real query list.

---

## Common Mistakes

- **String interpolation instead of `prepare()`** — the primary SQL-injection vector in
  WordPress plugins.
- **`LIKE` without `esc_like()`**, letting user input act as a wildcard.
- **Ignoring `$wpdb` return values**, which are `false` on error rather than exceptions.
- **A custom table where post meta would do**, forfeiting caching and tooling.
- **A custom table with no indexes.**
- **`$wpdb->prefix` where `base_prefix` was meant** (or vice versa) on multisite.
- **`switch_to_blog()` without `restore_current_blog()`** on every path.
- **Malformed `dbDelta()` SQL**, which fails silently and leaves the schema unchanged.
- **Direct SQL for posts and meta** that the API already caches.
- **Unbounded `DELETE` / `UPDATE`** on large tables.

---

## Verification Checklist

- Is the API genuinely insufficient here?
- Is every interpolated value passed through `prepare()` with the right placeholder?
- Is `esc_like()` applied before any `LIKE` value?
- Are `$wpdb` return values checked and errors logged?
- If a custom table exists: is it justified, indexed, versioned, and multisite-aware?
- Does `dbDelta()` SQL follow its formatting rules exactly?
- Are bulk operations batched and aggregates cached?

---

## Summary

Prefer the API; when it cannot answer the question, prepare every statement, check every
return value, index what you query, and treat a custom table as a permanent commitment that
gives up WordPress's caching and tooling in exchange for a real schema.

## Related

- `knowledge/wordpress/12-queries.md`
- `knowledge/wordpress/11-metadata.md`
- `knowledge/wordpress/06-security.md`
- `knowledge/wordpress/15-plugin-development.md`
- `knowledge/wordpress/05-performance.md`
- `knowledge/wordpress/25-multisite.md`
- `knowledge/security/13-sql-injection.md`
