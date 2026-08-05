---
id: wordpress/20-users-and-capabilities
topic: wordpress
slug: users-and-capabilities
title: "Users and Capabilities"
type: doc
order: 20
status: ready
tags: [wordpress, users-and-capabilities]
related: [wordpress/06-security, wordpress/18-rest-api, wordpress/09-custom-post-types, wordpress/25-multisite, wordpress/15-plugin-development, security/04-authorization]
when_to_use: "Read before implementing permission checks — choosing a capability, adding a custom role, or restricting access to a post type or admin screen."
---
# Users and Capabilities

## Purpose

This document defines how authorization works in WordPress: the difference between roles and
capabilities, how to check permission on a specific object, how to register custom
capabilities for a post type, and how to add roles without corrupting the database.

Authorization failures in WordPress are rarely subtle bugs — they are usually a missing check
or a check against the wrong thing.

---

## Core Principle

**Check capabilities, never roles.**

```php
// Bad: 'administrator' is a role name, not a capability. This happens to work only
// because roles and capabilities share a namespace, and it breaks the moment a site
// uses a custom role, a membership plugin, or multisite super admins.
if ( current_user_can( 'administrator' ) ) { /* … */ }

// Good: state what the user must be able to DO.
if ( current_user_can( 'manage_options' ) ) { /* … */ }
```

Roles are bundles of capabilities that site owners rearrange freely. Capabilities are the
contract your code should depend on.

---

## Primitive and Meta Capabilities

WordPress has two kinds, and mixing them up is the second most common authorization bug.

- **Primitive** — stored on the role: `edit_posts`, `publish_posts`, `manage_options`,
  `upload_files`.
- **Meta** — resolved per object at check time: `edit_post`, `delete_post`, `read_post`.
  They require an ID.

```php
// Primitive: "can this user edit posts at all?"
current_user_can( 'edit_posts' );

// Meta: "can this user edit THIS post?" — the only correct check before acting on a row.
current_user_can( 'edit_post', $post_id );
```

`map_meta_cap()` translates the meta capability into the primitive one the situation needs —
`edit_post` becomes `edit_others_posts` when the post belongs to someone else, or
`edit_published_posts` when it is already published. That is logic you should never
reimplement with ownership comparisons.

**Bad Example**

```php
// Misses published/private state, ignores editors, breaks with any membership plugin.
if ( get_current_user_id() === (int) $post->post_author ) {
	wp_update_post( $data );
}
```

**Good Example**

```php
if ( ! current_user_can( 'edit_post', $post->ID ) ) {
	wp_die( esc_html__( 'You are not allowed to edit this item.', 'acme-events' ), 403 );
}
wp_update_post( $data );
```

---

## Capability Plus Nonce

A capability answers "may this user do it". A nonce answers "did this user intend to do it,
here, now". State-changing requests need both.

```php
add_action( 'admin_post_acme_confirm_signup', 'acme_handle_confirm' );

function acme_handle_confirm(): void {
	$signup_id = isset( $_POST['signup_id'] ) ? absint( $_POST['signup_id'] ) : 0;

	// 1. Intent.
	check_admin_referer( 'acme_confirm_signup_' . $signup_id );

	// 2. Permission, on the specific object.
	if ( ! current_user_can( 'edit_post', $signup_id ) ) {
		wp_die( esc_html__( 'Not allowed.', 'acme-events' ), 403 );
	}

	// 3. Act.
	acme_confirm_signup( $signup_id );

	wp_safe_redirect( admin_url( 'admin.php?page=acme-signups&confirmed=1' ) );
	exit;
}
```

Note `wp_safe_redirect()` rather than `wp_redirect()` — it restricts the destination to the
site's own host, closing an open-redirect vector.

---

## Custom Capabilities for a Post Type

By default a custom post type reuses the `post` capabilities, so anyone who can edit posts can
edit it. For content that needs separate permissions, declare its own set:

```php
register_post_type(
	'acme_event',
	array(
		// Generates edit_event, edit_events, edit_others_events, publish_events,
		// read_private_events, delete_event, and so on.
		'capability_type' => array( 'event', 'events' ),
		'map_meta_cap'    => true,     // REQUIRED, or meta caps are never mapped
		// …
	)
);
```

Then grant them — **on activation**, not on every request:

```php
function acme_add_capabilities(): void {
	$editor = get_role( 'editor' );

	if ( ! $editor ) {
		return;
	}

	foreach ( array( 'edit_events', 'edit_others_events', 'publish_events', 'delete_events', 'read_private_events' ) as $cap ) {
		$editor->add_cap( $cap );
	}
}
register_activation_hook( ACME_EVENTS_FILE, 'acme_add_capabilities' );
```

`'map_meta_cap' => true` is the line people forget. Without it, `current_user_can(
'edit_post', $id )` on that post type never resolves correctly, and access checks silently
fail open or closed depending on the caller.

---

## Roles Are Stored in the Database

`add_role()`, `add_cap()`, and `remove_cap()` write to the `wp_user_roles` option. They are
persistent, not runtime configuration.

```php
// Bad: rewrites the option on EVERY request, on every page load, forever.
add_action( 'init', function () {
	$role = get_role( 'editor' );
	$role->add_cap( 'edit_events' );
} );

// Good: once, on activation.
register_activation_hook( ACME_EVENTS_FILE, 'acme_add_capabilities' );
```

Because the change persists, it also survives deactivation — clean up on uninstall so the site
is not left with orphaned capabilities:

```php
// uninstall.php
foreach ( array( 'editor', 'administrator' ) as $role_name ) {
	$role = get_role( $role_name );
	if ( $role ) {
		$role->remove_cap( 'edit_events' );
	}
}
remove_role( 'acme_event_manager' );
```

For a runtime decision that should not be stored, filter instead:

```php
add_filter( 'user_has_cap', function ( array $allcaps, array $caps, array $args, WP_User $user ) {
	if ( in_array( 'edit_events', $caps, true ) && acme_user_has_active_subscription( $user->ID ) ) {
		$allcaps['edit_events'] = true;
	}
	return $allcaps;
}, 10, 4 );
```

---

## Working With User Data

```php
$user = wp_get_current_user();          // WP_User; ID 0 when logged out
if ( ! is_user_logged_in() ) { /* … */ }

$user = get_user_by( 'email', $email ); // false when not found — always check

update_user_meta( $user_id, 'acme_newsletter_optin', '1' );
$optin = get_user_meta( $user_id, 'acme_newsletter_optin', true );
```

Never accept a user ID from the request and act on it without a check:

```php
// Bad: any logged-in user can operate on any other user's data.
$user_id = absint( $_POST['user_id'] );
update_user_meta( $user_id, 'acme_plan', $plan );

// Good.
$user_id = absint( $_POST['user_id'] );
if ( get_current_user_id() !== $user_id && ! current_user_can( 'edit_user', $user_id ) ) {
	wp_die( esc_html__( 'Not allowed.', 'acme-events' ), 403 );
}
```

Never implement password handling yourself: `wp_hash_password()`, `wp_check_password()`,
`wp_set_password()`, and `retrieve_password()` exist and are audited. See
[Security](06-security.md).

---

## Multisite

On a network, `is_super_admin()` sits above every role, and capabilities are per-site:

```php
// A super admin passes almost every capability check on every site.
if ( is_super_admin( $user_id ) ) { /* … */ }

// Network-level administration is its own capability.
if ( current_user_can( 'manage_network_options' ) ) { /* … */ }
```

A user may be an administrator on one site and a subscriber on another, so cache nothing about
permissions across `switch_to_blog()` — see [Multisite](25-multisite.md).

---

## Common Mistakes

- **Checking a role name** instead of a capability.
- **Comparing `post_author` manually** instead of using the `edit_post` meta capability.
- **`'map_meta_cap' => true` omitted** on a post type with custom capabilities.
- **A capability check without a nonce** on a state-changing request (or the reverse).
- **`add_cap()` on `init`**, writing to the options table on every request.
- **Capabilities never removed on uninstall.**
- **Trusting a user ID from the request.**
- **`wp_redirect()` with a user-supplied destination** instead of `wp_safe_redirect()`.
- **Assuming `get_user_by()` returns an object** without checking for `false`.
- **Custom password hashing.**

---

## Verification Checklist

- Does every check use a capability, and a meta capability where an object is involved?
- Does every state-changing request verify both a nonce and a capability?
- Does any custom post type needing separate permissions set `capability_type` and
  `map_meta_cap`?
- Are role and capability changes applied on activation, and reversed on uninstall?
- Are runtime permission decisions expressed through `user_has_cap` rather than stored?
- Is every user ID from a request authorized before use?
- Are redirects using `wp_safe_redirect()`?

---

## Summary

Authorization in WordPress means asking what a user may *do*, on *which object*, at the moment
of the action — with a nonce to prove intent. Roles are site configuration stored in the
database; capabilities are the contract your code depends on.

## Related


- `knowledge/wordpress/06-security.md`
- `knowledge/wordpress/18-rest-api.md`
- `knowledge/wordpress/09-custom-post-types.md`
- `knowledge/wordpress/25-multisite.md`
- `knowledge/wordpress/15-plugin-development.md`
- `knowledge/security/04-authorization.md`
