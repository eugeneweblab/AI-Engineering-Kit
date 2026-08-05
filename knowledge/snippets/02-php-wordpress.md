---
id: snippets/02-php-wordpress
topic: snippets
slug: php-wordpress
title: "PHP and WordPress Snippets"
type: doc
order: 2
status: ready
tags: [snippets, php-wordpress]
related: [snippets/01-typescript-utilities, wordpress/06-security, wordpress/12-queries, wordpress/23-caching, php/13-security]
when_to_use: "Copy when writing WordPress PHP — escaping output, guarding a request, querying, or caching."
---
# PHP and WordPress Snippets

## Escaping at Output

The single most common WordPress vulnerability is unescaped output. The function depends on
where the value lands, not on what it contains.

```php
<article <?php post_class(); ?>>
	<h2><?php echo esc_html( get_the_title() ); ?></h2>

	<a href="<?php echo esc_url( get_permalink() ); ?>"
	   title="<?php echo esc_attr( get_the_title() ); ?>">
		<?php echo esc_html__( 'Read more', 'acme' ); ?>
	</a>

	<?php // the_content() is already filtered through wp_kses on save — do not double-escape. ?>
	<div class="entry"><?php the_content(); ?></div>

	<?php // Editor-supplied HTML that should keep its markup: filter, do not escape. ?>
	<div class="bio"><?php echo wp_kses_post( $author_bio ); ?></div>

	<script>
		// esc_js is for a JS string literal; wp_json_encode is for structured data.
		const settings = <?php echo wp_json_encode( $settings ); ?>;
	</script>
</article>
```

| Context | Function |
|---|---|
| HTML text | `esc_html()` |
| Attribute value | `esc_attr()` |
| URL (`href`, `src`) | `esc_url()` |
| Editor HTML that must survive | `wp_kses_post()` |
| Inside a JS string | `esc_js()` |
| Structured data into JS | `wp_json_encode()` |
| Translated string | `esc_html__()` / `esc_attr__()` |

---

## Guarding a State-Changing Request

Three checks, in order: intent, permission, then act.

```php
add_action( 'admin_post_acme_archive_order', 'acme_handle_archive_order' );

function acme_handle_archive_order(): void {
	$order_id = isset( $_POST['order_id'] ) ? absint( $_POST['order_id'] ) : 0;

	// 1. Intent — proves the request came from your form, not a forged one.
	check_admin_referer( 'acme_archive_order_' . $order_id );

	// 2. Permission — on the specific object, not just "is logged in".
	if ( ! current_user_can( 'edit_post', $order_id ) ) {
		wp_die( esc_html__( 'You are not allowed to archive this order.', 'acme' ), 403 );
	}

	// 3. Act.
	acme_archive_order( $order_id );

	// wp_safe_redirect restricts the destination to this host — closes open redirects.
	wp_safe_redirect( add_query_arg( 'archived', '1', admin_url( 'admin.php?page=acme-orders' ) ) );
	exit;
}
```

---

## Querying Without the N+1

```php
$events = new WP_Query(
	array(
		'post_type'      => 'acme_event',
		'post_status'    => 'publish',
		'posts_per_page' => 12,        // never -1 on anything that can grow
		'no_found_rows'  => true,      // skip the COUNT query when not paginating
		'meta_key'       => '_acme_event_start',
		'orderby'        => 'meta_value',
		'order'          => 'ASC',
	)
);

if ( $events->have_posts() ) {
	while ( $events->have_posts() ) {
		$events->the_post();

		// Meta and terms were primed for the whole result set by WP_Query —
		// these are cache reads, not queries.
		$start = get_post_meta( get_the_ID(), '_acme_event_start', true );
		$types = get_the_terms( get_the_ID(), 'acme_event_type' );

		echo esc_html( get_the_title() );
	}

	wp_reset_postdata(); // omitting this leaves $post pointing at the last event
}
```

Working from an ID list obtained elsewhere, prime the cache explicitly:

```php
$ids = get_posts( array( 'post_type' => 'acme_event', 'fields' => 'ids', 'posts_per_page' => 50 ) );

update_meta_cache( 'post', $ids );   // one query instead of one per post

foreach ( $ids as $id ) {
	$start = get_post_meta( $id, '_acme_event_start', true );
}
```

---

## Prepared Statements

```php
global $wpdb;

$rows = $wpdb->get_results(
	$wpdb->prepare(
		"SELECT id, status FROM {$wpdb->prefix}acme_signups
		 WHERE event_id = %d AND created_at > %s
		 LIMIT %d",
		$event_id,
		$since,
		50
	)
);

// LIKE needs esc_like() *before* prepare(), or a user's % becomes a wildcard.
$like = '%' . $wpdb->esc_like( $search ) . '%';
$hits = $wpdb->get_col(
	$wpdb->prepare( "SELECT ID FROM {$wpdb->posts} WHERE post_title LIKE %s", $like )
);

// IN () needs one placeholder per value.
$ids          = array_map( 'absint', $ids );
$placeholders = implode( ',', array_fill( 0, count( $ids ), '%d' ) );
$titles = $wpdb->get_col(
	$wpdb->prepare( "SELECT post_title FROM {$wpdb->posts} WHERE ID IN ({$placeholders})", $ids )
);

// $wpdb never throws — check the return value.
if ( false === $wpdb->insert( $table, $data, array( '%d', '%s' ) ) ) {
	error_log( 'acme: insert failed — ' . $wpdb->last_error );
}
```

---

## Caching an Expensive Result

```php
function acme_get_upcoming_event_ids(): array {
	$ids = get_transient( 'acme_upcoming_events' );

	// Compare against false explicitly: an empty array is a valid cached value,
	// and `if ( ! $ids )` would recompute it on every request.
	if ( false !== $ids ) {
		return $ids;
	}

	$ids = get_posts(
		array(
			'post_type'      => 'acme_event',
			'posts_per_page' => 10,
			'fields'         => 'ids',
			'no_found_rows'  => true,
		)
	);

	// Always pass an expiry — without one this becomes a permanently autoloaded option.
	set_transient( 'acme_upcoming_events', $ids, HOUR_IN_SECONDS );

	return $ids;
}

// Expiry is not invalidation: clear it where the data changes.
add_action( 'save_post_acme_event', 'acme_flush_event_cache' );
add_action( 'deleted_post', 'acme_flush_event_cache' );

function acme_flush_event_cache( int $post_id ): void {
	if ( wp_is_post_revision( $post_id ) || wp_is_post_autosave( $post_id ) ) {
		return;
	}

	delete_transient( 'acme_upcoming_events' );
}
```

---

## Enqueuing Assets

```php
add_action( 'wp_enqueue_scripts', 'acme_enqueue_assets' );

function acme_enqueue_assets(): void {
	// Load only where it is needed — not on every page.
	if ( ! is_singular( 'acme_event' ) ) {
		return;
	}

	$dir = get_stylesheet_directory();
	$uri = get_stylesheet_directory_uri();

	wp_enqueue_script(
		'acme-event',
		$uri . '/assets/js/event.js',
		array(),
		filemtime( $dir . '/assets/js/event.js' ),  // cache-busts on change, unlike a literal
		true
	);

	wp_localize_script(
		'acme-event',
		'acmeEvent',
		array(
			'restUrl' => esc_url_raw( rest_url( 'acme/v1/' ) ),
			'nonce'   => wp_create_nonce( 'wp_rest' ),
		)
	);
}
```

---

## Examples

**Good Example** — prefixed, hooked, escaped, and capability-checked

```php
// Prefixed so it cannot collide with another plugin, registered on a hook,
// and every value escaped for the context it lands in.
add_action( 'wp_enqueue_scripts', 'acme_enqueue_assets' );

function acme_enqueue_assets() {
	// Version from filemtime: the cache busts when the file actually changes.
	$path = get_stylesheet_directory() . '/build/app.css';

	wp_enqueue_style(
		'acme-app',
		get_stylesheet_directory_uri() . '/build/app.css',
		array(),
		file_exists( $path ) ? (string) filemtime( $path ) : null
	);
}

add_action( 'admin_post_acme_save', 'acme_handle_save' );

function acme_handle_save() {
	$post_id = isset( $_POST['post_id'] ) ? absint( $_POST['post_id'] ) : 0;

	if ( ! $post_id || ! current_user_can( 'edit_post', $post_id ) ) {
		wp_die( esc_html__( 'Not allowed.', 'acme' ), 403 );
	}
	check_admin_referer( 'acme_save_' . $post_id );

	update_post_meta( $post_id, '_acme_note', sanitize_textarea_field( wp_unslash( $_POST['note'] ?? '' ) ) );

	wp_safe_redirect( wp_get_referer() );
	exit;
}
```

**Bad Example** — the snippet pasted into `functions.php` unchanged

```php
// Unprefixed: collides with any other plugin defining the same name, and the
// site white-screens with "Cannot redeclare function".
function enqueue_assets() {
	// Hardcoded version: the browser serves last month's CSS after every deploy.
	wp_enqueue_style( 'app', get_template_directory_uri() . '/build/app.css', array(), '1.0' );
}
enqueue_assets();   // called directly, before WordPress is ready for it

function handle_save() {
	global $wpdb;
	// No capability check, no nonce, unescaped interpolation into SQL.
	$wpdb->query( "UPDATE {$wpdb->posts} SET post_title='{$_POST['title']}' WHERE ID={$_POST['id']}" );
}
```

---

## Related

- `knowledge/wordpress/06-security.md`
- `knowledge/wordpress/12-queries.md`
- `knowledge/wordpress/23-caching.md`
- `knowledge/php/13-security.md`
