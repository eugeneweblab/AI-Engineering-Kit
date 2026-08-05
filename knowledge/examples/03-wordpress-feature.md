---
id: examples/03-wordpress-feature
topic: examples
slug: wordpress-feature
title: "Example — WordPress Feature"
type: doc
order: 3
status: ready
tags: [examples, wordpress-feature]
related: [examples/01-rest-endpoint, workflows/09-build-wordpress-feature, wordpress/09-custom-post-types, wordpress/11-metadata, wordpress/06-security]
when_to_use: "Read when building a WordPress feature end to end — post type, metadata, admin UI, front end, and security."
---
# Example — WordPress Feature

## The Feature

An events plugin: a custom post type with a start date and capacity, an editor UI for both,
and a front-end listing of upcoming events. The same domain as the other examples, on the
WordPress side.

The process is [Workflow — Build a WordPress Feature](../workflows/09-build-wordpress-feature.md).

---

## 1. Plugin Entry Point

```php
<?php
/**
 * Plugin Name:       Acme Events
 * Description:       Event content type with dates, capacity, and a listing block.
 * Version:           1.0.0
 * Requires at least: 6.4
 * Requires PHP:      8.1
 * Text Domain:       acme-events
 */

defined( 'ABSPATH' ) || exit;   // the file is web-reachable; without this it runs standalone

define( 'ACME_EVENTS_FILE', __FILE__ );
define( 'ACME_EVENTS_PATH', plugin_dir_path( __FILE__ ) );

require_once ACME_EVENTS_PATH . 'includes/post-type.php';
require_once ACME_EVENTS_PATH . 'includes/meta.php';
require_once ACME_EVENTS_PATH . 'includes/admin.php';
require_once ACME_EVENTS_PATH . 'includes/query.php';
```

Content lives in a **plugin**, not the theme: a post type registered in `functions.php`
disappears on a theme switch, leaving rows no query can reach.

---

## 2. The Post Type

```php
<?php
// includes/post-type.php
defined( 'ABSPATH' ) || exit;

add_action( 'init', 'acme_register_event_post_type' );

function acme_register_event_post_type(): void {
	register_post_type(
		'acme_event',   // prefixed: the slug is a global namespace, and it is permanent
		array(
			'labels'       => array(
				'name'          => _x( 'Events', 'post type general name', 'acme-events' ),
				'singular_name' => _x( 'Event', 'post type singular name', 'acme-events' ),
				'add_new_item'  => __( 'Add New Event', 'acme-events' ),
			),
			'public'       => true,
			'has_archive'  => 'events',
			'rewrite'      => array( 'slug' => 'events', 'with_front' => false ),
			'menu_icon'    => 'dashicons-calendar-alt',

			// `supports` replaces the defaults rather than extending them —
			// anything omitted is off, including revisions and thumbnails.
			'supports'     => array( 'title', 'editor', 'excerpt', 'thumbnail', 'revisions', 'custom-fields' ),

			// Required for the block editor and for any REST client.
			'show_in_rest' => true,
			'rest_base'    => 'events',
		)
	);
}

// Rewrite rules are cached in the database. Flush once, on activation —
// never on `init`, which rewrites the whole option on every request.
register_activation_hook( ACME_EVENTS_FILE, function (): void {
	acme_register_event_post_type();
	flush_rewrite_rules();
} );

register_deactivation_hook( ACME_EVENTS_FILE, 'flush_rewrite_rules' );
```

---

## 3. Metadata

```php
<?php
// includes/meta.php
defined( 'ABSPATH' ) || exit;

add_action( 'init', 'acme_register_event_meta' );

function acme_register_event_meta(): void {
	register_post_meta( 'acme_event', '_acme_event_start', array(
		'type'              => 'string',
		'single'            => true,
		'show_in_rest'      => true,                        // editor + REST visibility
		'sanitize_callback' => 'acme_sanitize_date',        // runs on every write path
		'auth_callback'     => function ( $allowed, $meta_key, $post_id ) {
			return current_user_can( 'edit_post', $post_id );
		},
	) );

	register_post_meta( 'acme_event', '_acme_event_capacity', array(
		'type'              => 'integer',
		'single'            => true,
		'default'           => 0,
		'show_in_rest'      => true,
		'sanitize_callback' => 'absint',
		'auth_callback'     => function ( $allowed, $meta_key, $post_id ) {
			return current_user_can( 'edit_post', $post_id );
		},
	) );
}

function acme_sanitize_date( $value ): string {
	$date = DateTimeImmutable::createFromFormat( 'Y-m-d', (string) $value );
	return $date ? $date->format( 'Y-m-d' ) : '';
}
```

Both keys are underscore-prefixed — protected meta, hidden from the generic Custom Fields
box because the plugin owns them. The `auth_callback` is what stops any authenticated user
writing them through the REST API.

---

## 4. The Editor UI

```php
<?php
// includes/admin.php
defined( 'ABSPATH' ) || exit;

add_action( 'add_meta_boxes', function (): void {
	add_meta_box(
		'acme-event-details',
		__( 'Event Details', 'acme-events' ),
		'acme_render_event_meta_box',
		'acme_event',
		'side'
	);
} );

function acme_render_event_meta_box( WP_Post $post ): void {
	wp_nonce_field( 'acme_save_event_' . $post->ID, 'acme_event_nonce' );

	$start    = get_post_meta( $post->ID, '_acme_event_start', true );
	$capacity = (int) get_post_meta( $post->ID, '_acme_event_capacity', true );
	?>
	<p>
		<label for="acme-event-start"><?php esc_html_e( 'Start date', 'acme-events' ); ?></label>
		<input type="date" id="acme-event-start" name="acme_event_start"
		       value="<?php echo esc_attr( $start ); ?>" class="widefat" />
	</p>
	<p>
		<label for="acme-event-capacity"><?php esc_html_e( 'Capacity', 'acme-events' ); ?></label>
		<input type="number" id="acme-event-capacity" name="acme_event_capacity" min="0"
		       value="<?php echo esc_attr( (string) $capacity ); ?>" class="widefat" />
	</p>
	<?php
}

add_action( 'save_post_acme_event', 'acme_save_event_meta', 10, 2 );

function acme_save_event_meta( int $post_id, WP_Post $post ): void {
	// save_post fires for autosaves and revisions too — bail before doing work.
	if ( wp_is_post_autosave( $post_id ) || wp_is_post_revision( $post_id ) ) {
		return;
	}

	// Intent: the nonce proves this came from the form above.
	if ( ! isset( $_POST['acme_event_nonce'] )
		|| ! wp_verify_nonce( sanitize_key( $_POST['acme_event_nonce'] ), 'acme_save_event_' . $post_id ) ) {
		return;
	}

	// Permission: on this specific post, not just "can edit posts".
	if ( ! current_user_can( 'edit_post', $post_id ) ) {
		return;
	}

	if ( isset( $_POST['acme_event_start'] ) ) {
		update_post_meta( $post_id, '_acme_event_start',
			acme_sanitize_date( wp_unslash( $_POST['acme_event_start'] ) ) );
	}

	if ( isset( $_POST['acme_event_capacity'] ) ) {
		update_post_meta( $post_id, '_acme_event_capacity',
			absint( wp_unslash( $_POST['acme_event_capacity'] ) ) );
	}
}
```

The three guards — autosave, nonce, capability — are the pattern every `save_post` handler
needs. Omitting the first causes data loss on autosave; omitting either of the others is a
vulnerability.

---

## 5. The Front-End Query

```php
<?php
// includes/query.php
defined( 'ABSPATH' ) || exit;

// Alter the archive rather than running a second query in the template:
// a second query breaks pagination and pays for the work twice.
add_action( 'pre_get_posts', 'acme_order_event_archive' );

function acme_order_event_archive( WP_Query $query ): void {
	// Three guards: admin screens, secondary queries, and other contexts must be untouched.
	if ( is_admin() || ! $query->is_main_query() || ! $query->is_post_type_archive( 'acme_event' ) ) {
		return;
	}

	$query->set( 'meta_key', '_acme_event_start' );
	$query->set( 'orderby', 'meta_value' );
	$query->set( 'order', 'ASC' );
	$query->set( 'posts_per_page', 12 );

	// Upcoming only.
	$query->set( 'meta_query', array(
		array(
			'key'     => '_acme_event_start',
			'value'   => current_time( 'Y-m-d' ),
			'compare' => '>=',
			'type'    => 'DATE',   // without this, the comparison is a string comparison
		),
	) );
}
```

---

## 6. The Template

```php
<?php
// archive-acme_event.php — in the theme, since this is presentation
get_header();
?>

<main class="events">
	<h1><?php esc_html_e( 'Upcoming events', 'acme-events' ); ?></h1>

	<?php if ( have_posts() ) : ?>
		<ul class="events__list">
			<?php while ( have_posts() ) : the_post(); ?>
				<?php
				// Cache reads, not queries: WP_Query primed meta for the whole page.
				$start    = get_post_meta( get_the_ID(), '_acme_event_start', true );
				$capacity = (int) get_post_meta( get_the_ID(), '_acme_event_capacity', true );
				?>
				<li class="events__item">
					<h2>
						<a href="<?php echo esc_url( get_permalink() ); ?>">
							<?php echo esc_html( get_the_title() ); ?>
						</a>
					</h2>

					<?php if ( $start ) : ?>
						<time datetime="<?php echo esc_attr( $start ); ?>">
							<?php echo esc_html( wp_date( get_option( 'date_format' ), strtotime( $start ) ) ); ?>
						</time>
					<?php endif; ?>

					<?php if ( $capacity > 0 ) : ?>
						<p class="events__capacity">
							<?php
							printf(
								/* translators: %d: number of places available. */
								esc_html( _n( '%d place available', '%d places available', $capacity, 'acme-events' ) ),
								$capacity
							);
							?>
						</p>
					<?php endif; ?>
				</li>
			<?php endwhile; ?>
		</ul>

		<?php the_posts_pagination(); ?>
	<?php else : ?>
		<p><?php esc_html_e( 'No upcoming events.', 'acme-events' ); ?></p>
	<?php endif; ?>
</main>

<?php get_footer(); ?>
```

Every dynamic value is escaped for its context, and the plural uses `_n()` rather than an
`if ( $n === 1 )` branch — languages with three plural forms need the translation file to
decide, not the template.

---

## What a Real Implementation Adds

- **Uninstall cleanup** — `uninstall.php` removing options; content deletion opt-in.
- **A block** for the listing, rather than relying on the archive template.
- **Signups**, which is where capacity stops being decorative — the concurrency problem in
  [Example — REST Endpoint](01-rest-endpoint.md) applies here too.
- **Caching** the archive query, invalidated on `save_post_acme_event`.
- **Tests** — see [WordPress — Testing](../wordpress/07-testing.md).

---

## Related

- `knowledge/workflows/09-build-wordpress-feature.md`
- `knowledge/wordpress/09-custom-post-types.md`
- `knowledge/wordpress/11-metadata.md`
- `knowledge/wordpress/06-security.md`
