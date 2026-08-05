---
id: wordpress/18-rest-api
topic: wordpress
slug: rest-api
title: "WordPress REST API"
type: doc
order: 18
status: ready
tags: [wordpress, rest-api]
related: [wordpress/06-security, wordpress/20-users-and-capabilities, wordpress/11-metadata, wordpress/16-block-editor, wordpress/23-caching, wordpress/09-custom-post-types, rest-api/24-security]
when_to_use: "Read before exposing or consuming WordPress REST endpoints — registering a route, adding fields to core responses, or securing an API used by a headless front end."
---
# WordPress REST API

## Purpose

This document defines how to register and secure WordPress REST endpoints: permission
callbacks, argument validation, response shaping, and the authentication options available to
different kinds of client.

The REST API is not an add-on. The block editor, the site editor, and most modern admin
screens are REST clients, so its conventions are core conventions.

---

## Core Principle

**Every route needs an explicit `permission_callback`.** Since WordPress 5.5, omitting it
raises a `_doing_it_wrong()` notice — because a missing callback historically meant a public
endpoint by accident.

```php
// Public by intent — say so explicitly.
'permission_callback' => '__return_true',

// Restricted — check a capability, never a role.
'permission_callback' => function () {
	return current_user_can( 'edit_posts' );
},
```

There is no third option. A route without a permission callback is a defect regardless of
what it returns.

---

## Registering a Route

```php
add_action( 'rest_api_init', 'acme_register_routes' );

function acme_register_routes(): void {
	register_rest_route(
		'acme/v1',                          // vendor/version — never reuse 'wp/v2'
		'/events/(?P<id>\d+)',
		array(
			'methods'             => WP_REST_Server::READABLE,   // 'GET'
			'callback'            => 'acme_get_event',
			'permission_callback' => '__return_true',
			'args'                => array(
				'id' => array(
					'required'          => true,
					'type'              => 'integer',
					'sanitize_callback' => 'absint',
					'validate_callback' => function ( $value ) {
						return $value > 0;
					},
				),
			),
		)
	);

	register_rest_route(
		'acme/v1',
		'/events',
		array(
			'methods'             => WP_REST_Server::CREATABLE,  // 'POST'
			'callback'            => 'acme_create_event',
			'permission_callback' => function () {
				return current_user_can( 'publish_posts' );
			},
			'args'                => array(
				'title' => array(
					'required'          => true,
					'type'              => 'string',
					'sanitize_callback' => 'sanitize_text_field',
				),
				'start' => array(
					'required'          => true,
					'type'              => 'string',
					'format'            => 'date',
					'validate_callback' => 'rest_validate_request_arg',
				),
				'status' => array(
					'type'    => 'string',
					'default' => 'draft',
					'enum'    => array( 'draft', 'publish' ),
				),
			),
		)
	);
}
```

Declaring `args` is what makes the endpoint self-validating: WordPress runs
`validate_callback` and `sanitize_callback` before the handler executes, so the callback
receives values it can trust.

---

## Responses and Errors

```php
function acme_get_event( WP_REST_Request $request ) {
	$event = get_post( $request->get_param( 'id' ) );

	if ( ! $event || 'acme_event' !== $event->post_type || 'publish' !== $event->post_status ) {
		// Status in the data array is what sets the HTTP status code.
		return new WP_Error(
			'acme_event_not_found',
			__( 'Event not found.', 'acme-events' ),
			array( 'status' => 404 )
		);
	}

	return rest_ensure_response(
		array(
			'id'    => $event->ID,
			'title' => get_the_title( $event ),
			'start' => get_post_meta( $event->ID, '_acme_event_start', true ),
			'link'  => get_permalink( $event ),
		)
	);
}
```

Return a `WP_Error`, never a response with `success: false`. `WP_Error` produces the correct
status code, and every REST client — including the block editor — understands it.

Add headers for paginated collections so clients can paginate without a second request:

```php
$response = rest_ensure_response( $items );
$response->header( 'X-WP-Total', (int) $query->found_posts );
$response->header( 'X-WP-TotalPages', (int) $query->max_num_pages );
return $response;
```

---

## Extending Core Endpoints

Prefer extending `wp/v2` over building a parallel API when the data belongs to a post type.

```php
add_action( 'rest_api_init', function () {
	register_rest_field(
		'acme_event',
		'event_start',
		array(
			'get_callback' => function ( array $post ) {
				return get_post_meta( $post['id'], '_acme_event_start', true );
			},
			'update_callback' => function ( $value, WP_Post $post ) {
				if ( ! current_user_can( 'edit_post', $post->ID ) ) {
					return new WP_Error( 'acme_forbidden', __( 'Not allowed.', 'acme-events' ), array( 'status' => 403 ) );
				}
				return update_post_meta( $post->ID, '_acme_event_start', sanitize_text_field( $value ) );
			},
			'schema' => array(
				'description' => __( 'Event start date (Y-m-d).', 'acme-events' ),
				'type'        => 'string',
				'context'     => array( 'view', 'edit' ),
			),
		)
	);
} );
```

Registering meta with `show_in_rest` (see [Metadata](11-metadata.md)) is simpler still when
the value maps one-to-one onto a meta key.

---

## Authentication

| Client | Mechanism |
|---|---|
| Same-origin JS (editor, admin, theme) | Cookies + `X-WP-Nonce` |
| External service, server-to-server | Application Passwords (WP 5.6+) over HTTPS |
| Third-party app | OAuth or JWT via a plugin |

For same-origin requests, the nonce is what proves the request came from your page:

```php
wp_localize_script( 'acme-app', 'acmeApi', array(
	'root'  => esc_url_raw( rest_url( 'acme/v1/' ) ),
	'nonce' => wp_create_nonce( 'wp_rest' ),   // the action name is always 'wp_rest'
) );
```

```js
await fetch( `${ acmeApi.root }events`, {
	method: 'POST',
	headers: { 'Content-Type': 'application/json', 'X-WP-Nonce': acmeApi.nonce },
	credentials: 'same-origin',     // without this the cookie is not sent
	body: JSON.stringify( { title, start } ),
} );
```

A REST nonce expires (by default within 24 hours) while a page may stay open longer. A `403`
with code `rest_cookie_invalid_nonce` after a long idle period is an expired nonce, not a
permission bug — refresh it rather than widening the permission callback.

---

## Hardening a Public API

The default `wp/v2` surface exposes more than most sites intend — including
`/wp/v2/users`, which enumerates author accounts.

```php
// Require authentication for user enumeration on a site with no public author pages.
add_filter( 'rest_endpoints', function ( array $endpoints ) {
	if ( ! is_user_logged_in() ) {
		unset( $endpoints['/wp/v2/users'], $endpoints['/wp/v2/users/(?P<id>[\d]+)'] );
	}
	return $endpoints;
} );
```

Other measures worth taking on any public deployment:

- **Rate-limit** write endpoints at the edge — WordPress has no built-in throttling, and a
  REST request boots the whole application.
- **Cap `per_page`.** Core allows up to 100; an unbounded custom endpoint is a denial-of-service
  vector.
- **Never return unfiltered post content** for non-public statuses; check `post_status` and
  capabilities explicitly, as in the example above.

---

## Caching REST Responses

Every REST request loads all of WordPress. For read-heavy public endpoints, cache
deliberately:

```php
function acme_get_upcoming( WP_REST_Request $request ) {
	$cache_key = 'acme_upcoming_' . absint( $request->get_param( 'page' ) );
	$data      = get_transient( $cache_key );

	if ( false === $data ) {
		$data = acme_build_upcoming_payload( $request );
		set_transient( $cache_key, $data, 5 * MINUTE_IN_SECONDS );
	}

	$response = rest_ensure_response( $data );
	$response->header( 'Cache-Control', 'public, max-age=300' );
	return $response;
}
```

Note that WordPress sends `Cache-Control: no-cache` on REST responses by default, so a CDN
will not cache them unless you override the header. See [Caching](23-caching.md).

---

## Examples

**Good Example** — explicit permission, declared arguments, shaped response

```php
add_action( 'rest_api_init', 'myplugin_register_routes' );

function myplugin_register_routes() {
	register_rest_route(
		'myplugin/v1',
		'/events/(?P<id>\d+)/signups',
		array(
			'methods'             => WP_REST_Server::CREATABLE,
			'callback'            => 'myplugin_create_signup',
			'permission_callback' => static function ( WP_REST_Request $request ) {
				return is_user_logged_in() && current_user_can( 'read_post', (int) $request['id'] );
			},
			'args'                => array(
				'id'    => array(
					'required'          => true,
					'validate_callback' => static fn( $value ) => is_numeric( $value ) && (int) $value > 0,
					'sanitize_callback' => 'absint',
				),
				'notes' => array(
					'type'              => 'string',
					'default'           => '',
					'sanitize_callback' => 'sanitize_textarea_field',
				),
			),
		)
	);
}

function myplugin_create_signup( WP_REST_Request $request ) {
	$result = ( new MyPlugin_Registration_Service() )->register(
		(int) $request['id'],
		get_current_user_id(),
		$request['notes']
	);

	if ( is_wp_error( $result ) ) {
		// A WP_Error with a status becomes a correct HTTP response automatically.
		$result->add_data( array( 'status' => 409 ), $result->get_error_code() );
		return $result;
	}

	// Return only what the client needs — not the whole post object.
	return new WP_REST_Response(
		array(
			'id'     => $result,
			'status' => 'confirmed',
		),
		201
	);
}
```

**Bad Example** — implicitly public, unvalidated input, oversharing

```php
add_action( 'rest_api_init', function () {
	register_rest_route(
		'myplugin/v1',
		'/events/signups',
		array(
			'methods'  => 'POST',
			'callback' => 'myplugin_create_signup',
			// No permission_callback: _doing_it_wrong() since 5.5, and historically
			// this meant "public" by accident.
		)
	);
} );

function myplugin_create_signup() {
	// Reads the superglobal directly, so nothing declared or sanitized it.
	$event_id = $_POST['event_id'];

	add_post_meta( $event_id, '_signup', get_current_user_id() );

	// Returns the entire post row: author email, unpublished content, private meta.
	return get_post( $event_id );
}
```

---

## Common Mistakes

- **Missing or `__return_true` permission callbacks** on endpoints that expose private data.
- **Checking a role instead of a capability** (`current_user_can( 'administrator' )`).
- **Validating inside the callback** rather than declaring `args`.
- **Returning `array( 'success' => false )`** instead of `WP_Error`, so clients see HTTP 200.
- **Registering routes under `wp/v2`**, colliding with core.
- **No version in the namespace**, leaving no way to change the contract later.
- **Unbounded `per_page`** on custom collection endpoints.
- **Forgetting `credentials: 'same-origin'`**, so the request arrives unauthenticated.
- **Treating an expired nonce as an authorization failure** and loosening permissions.
- **Leaving `/wp/v2/users` open** on a site that does not need public author data.

---

## Verification Checklist

- Does every route declare a `permission_callback` that reflects real intent?
- Are permissions capability checks, including object-level checks such as `edit_post`?
- Is every argument declared with type, sanitization, and validation?
- Do errors return `WP_Error` with an accurate HTTP status?
- Is the namespace vendor-prefixed and versioned?
- Are collection endpoints bounded and paginated with the standard headers?
- Is authentication appropriate to the client, and is the API HTTPS-only?
- Are expensive read endpoints cached, with headers a CDN can act on?

---

## Summary

Register versioned, namespaced routes with an explicit permission callback and declared
arguments; return `WP_Error` for failures; extend core endpoints rather than duplicating them;
and remember that every REST call boots the entire application, so bound and cache what is
public.

## Related


- `knowledge/wordpress/06-security.md`
- `knowledge/wordpress/20-users-and-capabilities.md`
- `knowledge/wordpress/11-metadata.md`
- `knowledge/wordpress/16-block-editor.md`
- `knowledge/wordpress/23-caching.md`
- `knowledge/wordpress/09-custom-post-types.md`
- `knowledge/rest-api/24-security.md`
