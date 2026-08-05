---
id: divi/17-rest-api
topic: divi
slug: rest-api
title: "Divi REST API"
type: doc
order: 17
status: ready
tags: [divi, rest-api]
related: [divi/18-headless, divi/16-wordpress-hooks, divi/19-security, divi/15-custom-fields, divi/07-dynamic-content]
when_to_use: "Read before exposing or consuming WordPress REST endpoints for a Divi site, headless or otherwise."
---
# Divi REST API

## Purpose

This document defines how to use the **WordPress REST API** with a **Divi** site: consuming its
data, registering custom endpoints, and doing so without exposing data or accepting writes you
should not. It covers both directions — a Divi module or block fetching data, and external clients
(a headless front end, a mobile app, an integration) reading and writing WordPress content.

The REST API is WordPress's HTTP interface under `/wp-json/`. Divi does not replace it; Divi builds
run on top of it, and headless Divi setups depend on it entirely (see [headless](18-headless.md)).
The core discipline is that every endpoint enforces **authentication**, **permission checks**, and
**input validation** — the API is a public door until you lock it.

## Why It Matters

The REST API is remotely reachable by anyone, so a mistake here is exploitable from the open
internet, not just from within the site. WordPress ships useful default endpoints, but some (like
the users endpoint) leak information such as usernames if left open, and a custom endpoint registered
without a `permission_callback` is world-readable *and* world-writable by default — a direct path to
data theft or content injection. Custom write endpoints that skip nonce/capability checks or input
validation invite CSRF and injection. Because these endpoints are the seam between WordPress and
everything outside it, they are held to the same bar as authentication code: assume every caller is
hostile. See [security](19-security.md).

## Core Principles

- **Every route has an explicit `permission_callback`.** Never register a route without one;
  omitting it (or returning `true`) exposes it to the world. Return a real capability check.
- **Authenticate writes properly.** Use application passwords, OAuth, or a nonce for
  cookie-authenticated requests. Never accept state-changing requests unauthenticated.
- **Validate and sanitize every argument.** Declare `args` with `validate_callback` and
  `sanitize_callback`; never trust `$request` params. Escape data on output.
- **Expose the minimum.** Return only the fields a client needs; do not dump full objects or
  private meta. Restrict or disable default endpoints that leak (e.g. user enumeration).
- **Consume defensively.** When Divi fetches an endpoint, handle failure, timeouts, and empty
  responses; never inject a remote response into the page as raw HTML.

## Best Practices

- Register custom endpoints on the `rest_api_init` hook with `register_rest_route`, a versioned
  namespace (`myplugin/v1`), and an explicit `permission_callback` and `args` schema.
- For reads that must stay public, still scope the data and rate-limit; for anything sensitive,
  gate on `current_user_can()`.
- Prefer the WordPress HTTP API (`wp_remote_get`/`wp_remote_post`) over raw cURL when consuming
  external or internal endpoints server-side — it respects timeouts and filters, and check
  `is_wp_error()` on the result.
- Cache expensive or high-traffic responses (transients or object cache) so the API is not a
  performance hole; set sane `Cache-Control` for public GETs.
- Expose custom fields to the API deliberately with `register_meta( ..., ['show_in_rest' => true] )`
  or `register_rest_field` — never rely on generic meta being silently public. See
  [custom-fields](15-custom-fields.md).
- Restrict user enumeration: require authentication on the `wp/v2/users` endpoint if usernames
  must stay private.
- When fetching from client-side JS in a Divi module, use the localized nonce
  (`wp_localize_script` with `wpApiSettings`) and send it as `X-WP-Nonce`.

## Examples

**Good Example** — permission-checked, validated custom route

```php
add_action( 'rest_api_init', function () {
    register_rest_route( 'myplugin/v1', '/subscriber', [
        'methods'  => 'POST',
        'permission_callback' => function () {
            return current_user_can( 'edit_posts' ); // real capability check, not true
        },
        'args' => [
            'email' => [
                'required'          => true,
                'validate_callback' => fn( $v ) => is_email( $v ) !== false,
                'sanitize_callback' => 'sanitize_email',
            ],
        ],
        'callback' => function ( WP_REST_Request $req ) {
            $email = $req->get_param( 'email' );      // already validated + sanitized
            // ...persist...
            return new WP_REST_Response( [ 'ok' => true ], 201 );
        },
    ] );
} );
```

**Bad Example** — open, unvalidated, world-writable route

```php
add_action( 'rest_api_init', function () {
    register_rest_route( 'myplugin/v1', '/subscriber', [
        'methods'  => 'POST',
        'permission_callback' => '__return_true', // anyone on the internet can call this
        'callback' => function ( $req ) {
            // Raw, unvalidated input written straight to the DB → injection + spam.
            save_subscriber( $req->get_param( 'email' ) );
            return 'ok';
        },
    ] );
} );
```

## Common Mistakes

- Registering a route without a `permission_callback`, or setting it to `__return_true`.
- Accepting write requests with no nonce/capability check, enabling CSRF and unauthorized writes.
- Using `$request` params without `validate_callback`/`sanitize_callback`.
- Returning full objects or private meta, leaking data the client never needed.
- Leaving the default users endpoint open, allowing username enumeration.
- Consuming remote endpoints without checking `is_wp_error()`/status, then rendering the response
  as raw HTML (XSS) or crashing on failure.
- Storing API secrets/tokens in client-side JS or committed code instead of server-side config.

## Production Tips

- Cache public GET responses and set `Cache-Control`; an uncached hot endpoint will dominate
  server load under traffic or a headless front end.
- Rate-limit and log write endpoints; alert on spikes, the same way you would for login endpoints.
- Version your namespace from day one (`/v1`) so you can evolve the contract without breaking
  existing clients.
- In headless setups, front the API with a CDN/edge cache and expose only the namespaces the
  front end needs. See [headless](18-headless.md).

## AI Review Checklist

- Does every registered route have an explicit, real `permission_callback` (never `__return_true`)?
- Are all write endpoints authenticated (nonce/app password/OAuth) and capability-checked?
- Does every argument have `validate_callback` and `sanitize_callback`?
- Is output limited to needed fields, with private meta excluded?
- Are default endpoints that enumerate users restricted where required?
- When consuming, is `is_wp_error()`/status checked and the response never injected as raw HTML?
- Are secrets kept server-side, and hot public responses cached?

## Related

- `knowledge/divi/18-headless.md`
- `knowledge/divi/16-wordpress-hooks.md`
- `knowledge/divi/19-security.md`
- `knowledge/divi/15-custom-fields.md`
- `knowledge/divi/07-dynamic-content.md`
