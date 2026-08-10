---
id: wordpress/06-security
topic: wordpress
slug: security
title: "WordPress Security"
type: doc
order: 6
status: ready
tags: [wordpress, security, current_user_can, wp_die, wp_unslash, esc_html__, update_post_meta, add_action, endpoints, authentication, input]
related: [wordpress/20-users-and-capabilities, wordpress/18-rest-api, wordpress/19-database, security/09-input-validation, security/11-xss]
when_to_use: "Read before handling input, endpoints, or authentication in a WordPress project."
---
# WordPress Security

## Purpose

This document defines the security principles for developing WordPress applications.

Security is a fundamental engineering responsibility rather than a final review step.

Every feature, endpoint, integration, and administrative interface should be designed with security in mind from the beginning.

---

## Core Principle

Never trust external input.

Every value originating from:

- users;
- browsers;
- APIs;
- databases;
- uploaded files;
- cookies;
- query parameters;
- request headers;

should be considered untrusted until validated.

---

## Security Mindset

Every implementation should answer the following questions:

- Who can access this feature?
- What data can they modify?
- What data can they read?
- How is the request verified?
- How is the input validated?
- How is the output protected?

Security begins before writing code.

---

## Authentication

Authentication verifies identity.

Always rely on the existing WordPress authentication system unless project requirements specify otherwise.

Examples:

- logged-in users;
- application passwords;
- JWT authentication;
- OAuth providers;
- SSO integrations.

Never implement custom authentication without a strong justification.

---

## Authorization

Authentication does not imply authorization.

Always verify permissions before allowing operations.

Use `current_user_can()` with the most specific capability available. For actions
that target a single object, pass the object ID so WordPress can apply meta
capabilities (for example `edit_post`, `delete_user`) rather than a broad
primitive capability.

```php
current_user_can( 'edit_posts' );

current_user_can( 'manage_options' );

current_user_can( 'edit_post', $post_id );
```

Every privileged action should perform an explicit capability check.

Bad — checks only that the user is logged in, so any subscriber can trash any post:

```php
function my_plugin_trash_post( $post_id ) {
	if ( is_user_logged_in() ) {
		wp_trash_post( $post_id );
	}
}
```

Good — checks the meta capability for this specific post:

```php
function my_plugin_trash_post( $post_id ) {
	$post_id = absint( $post_id );

	if ( ! current_user_can( 'delete_post', $post_id ) ) {
		wp_die( esc_html__( 'You are not allowed to delete this post.', 'my-plugin' ), 403 );
	}

	wp_trash_post( $post_id );
}
```

---

## Nonce Verification

Protect state-changing requests with nonces.

A nonce proves the request came from a page WordPress rendered for this user, not
from a forged cross-site request. Emit it with `wp_nonce_field()` and verify it on
submission. A nonce is never a substitute for a capability check — always do both.

Good — admin form protected by a nonce and a capability check:

```php
function my_plugin_settings_form() {
	?>
	<form method="post" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>">
		<input type="hidden" name="action" value="my_plugin_save_settings">
		<?php wp_nonce_field( 'my_plugin_save_settings', 'my_plugin_nonce' ); ?>
		<input type="text" name="api_endpoint" value="<?php echo esc_attr( get_option( 'my_plugin_api_endpoint', '' ) ); ?>">
		<?php submit_button(); ?>
	</form>
	<?php
}

add_action( 'admin_post_my_plugin_save_settings', 'my_plugin_save_settings' );

function my_plugin_save_settings() {
	if ( ! current_user_can( 'manage_options' ) ) {
		wp_die( esc_html__( 'Insufficient permissions.', 'my-plugin' ), 403 );
	}

	// Dies with a 403 if the nonce is missing or invalid.
	check_admin_referer( 'my_plugin_save_settings', 'my_plugin_nonce' );

	$endpoint = isset( $_POST['api_endpoint'] )
		? esc_url_raw( wp_unslash( $_POST['api_endpoint'] ) )
		: '';

	update_option( 'my_plugin_api_endpoint', $endpoint );

	wp_safe_redirect( add_query_arg( 'updated', 'true', wp_get_referer() ) );
	exit;
}
```

For AJAX handlers, use `check_ajax_referer()`, which reads the nonce from the
request and dies on failure:

```php
add_action( 'wp_ajax_my_plugin_action', 'my_plugin_ajax_handler' );

function my_plugin_ajax_handler() {
	// Verifies the 'my_plugin_action' nonce sent as the '_ajax_nonce' or 'nonce' field.
	check_ajax_referer( 'my_plugin_action' );

	if ( ! current_user_can( 'edit_posts' ) ) {
		wp_send_json_error( array( 'message' => 'Forbidden' ), 403 );
	}

	wp_send_json_success();
}
```

Never rely solely on hidden form fields. Always unslash superglobals with
`wp_unslash()` before sanitizing — WordPress adds slashes to `$_POST`, `$_GET`,
`$_REQUEST`, and `$_COOKIE`.

---

## Input Validation

Validate every input.

Examples:

- required fields;
- string length;
- numeric ranges;
- email format;
- URLs;
- UUIDs;
- enum values;
- dates.

Validation confirms a value is acceptable; sanitization coerces a value into a
safe shape. They are complementary, not interchangeable — validate the meaning,
then sanitize the format.

Bad — casts a status without checking it is one of the allowed values:

```php
$status = sanitize_text_field( wp_unslash( $_POST['status'] ) );
update_post_meta( $post_id, 'order_status', $status );
```

Good — rejects anything outside a known set before storing:

```php
$allowed_statuses = array( 'pending', 'processing', 'complete', 'cancelled' );
$status           = isset( $_POST['status'] )
	? sanitize_key( wp_unslash( $_POST['status'] ) )
	: '';

if ( ! in_array( $status, $allowed_statuses, true ) ) {
	wp_die( esc_html__( 'Invalid status.', 'my-plugin' ), 400 );
}

update_post_meta( $post_id, 'order_status', $status );
```

Reject invalid input as early as possible.

---

## Data Sanitization

Sanitize data before storing it.

Examples:

```php
sanitize_text_field()

sanitize_email()

sanitize_key()

sanitize_title()

sanitize_file_name()
```

Store clean data whenever possible.

---

## Output Escaping

Escape data immediately before rendering.

Examples:

```php
esc_html()

esc_attr()

esc_url()

wp_kses_post()
```

The escaping function depends on the output context. Escape as late as possible,
at the point of output, and match the function to the context.

Bad — trusts stored values and mixes contexts, allowing stored XSS:

```php
echo '<a href="' . get_post_meta( $post_id, 'homepage', true ) . '" title="'
	. get_post_meta( $post_id, 'bio', true ) . '">' . get_the_title() . '</a>';
```

Good — each value is escaped for its exact context:

```php
printf(
	'<a href="%1$s" title="%2$s">%3$s</a>',
	esc_url( get_post_meta( $post_id, 'homepage', true ) ),
	esc_attr( get_post_meta( $post_id, 'bio', true ) ),
	esc_html( get_the_title( $post_id ) )
);
```

When a value may contain a limited set of HTML tags (for example post content),
filter it with `wp_kses_post()` or a custom allowlist via `wp_kses()` rather than
echoing it raw.

Never escape data when storing it.

---

## SQL Safety

Prefer WordPress APIs.

When direct SQL is necessary:

- use `$wpdb->prepare()`;
- validate identifiers;
- avoid dynamic SQL generation;
- minimize privileges.

`$wpdb->prepare()` only placeholders values, not table or column names. Build
identifiers from a hardcoded allowlist and interpolate values exclusively through
`%s`, `%d`, `%f`, or the `%i` identifier placeholder (WordPress 6.2+).

Bad — untrusted input concatenated straight into the query:

```php
global $wpdb;

$email   = $_GET['email'];
$results = $wpdb->get_results( "SELECT * FROM {$wpdb->users} WHERE user_email = '$email'" );
```

Good — value passed through a placeholder in `prepare()`:

```php
global $wpdb;

$email = isset( $_GET['email'] )
	? sanitize_email( wp_unslash( $_GET['email'] ) )
	: '';

$results = $wpdb->get_results(
	$wpdb->prepare(
		"SELECT ID, user_login FROM {$wpdb->users} WHERE user_email = %s",
		$email
	)
);
```

Use `%i` for a dynamic column name that has been validated against an allowlist:

```php
global $wpdb;

$allowed_columns = array( 'user_login', 'user_email', 'user_registered' );
$order_by        = in_array( $requested_column, $allowed_columns, true )
	? $requested_column
	: 'user_login';

$results = $wpdb->get_results(
	$wpdb->prepare( "SELECT ID FROM {$wpdb->users} ORDER BY %i ASC", $order_by )
);
```

Never concatenate untrusted input into SQL queries.

---

## REST API Security

Every endpoint should verify:

- authentication;
- authorization;
- request validation;
- response filtering.

Permission callbacks are mandatory.

Bad — `permission_callback` returns `true`, exposing the route to everyone:

```php
register_rest_route(
	'my-plugin/v1',
	'/orders/(?P<id>\d+)',
	array(
		'methods'             => 'POST',
		'callback'            => 'my_plugin_update_order',
		'permission_callback' => '__return_true',
	)
);
```

Good — the route validates its arguments and enforces a capability. WordPress
verifies the REST nonce automatically for cookie-authenticated requests, so a
capability check is the correct authorization gate here:

```php
add_action( 'rest_api_init', 'my_plugin_register_routes' );

function my_plugin_register_routes() {
	register_rest_route(
		'my-plugin/v1',
		'/orders/(?P<id>\d+)',
		array(
			'methods'             => WP_REST_Server::EDITABLE,
			'callback'            => 'my_plugin_update_order',
			'permission_callback' => function () {
				return current_user_can( 'edit_others_posts' );
			},
			'args'                => array(
				'id'     => array(
					'required'          => true,
					'validate_callback' => function ( $value ) {
						return is_numeric( $value ) && (int) $value > 0;
					},
					'sanitize_callback' => 'absint',
				),
				'status' => array(
					'required'          => true,
					'type'              => 'string',
					'enum'              => array( 'pending', 'processing', 'complete' ),
					'sanitize_callback' => 'sanitize_key',
				),
			),
		)
	);
}

function my_plugin_update_order( WP_REST_Request $request ) {
	$order_id = $request['id'];     // Already sanitized by absint.
	$status   = $request['status']; // Already validated against the enum.

	update_post_meta( $order_id, 'order_status', $status );

	return rest_ensure_response( array( 'id' => $order_id, 'status' => $status ) );
}
```

Sensitive fields should never be returned unless explicitly required.

---

## File Upload Security

Before accepting uploads verify:

- file type;
- MIME type;
- file size;
- upload permissions;
- destination directory.

Route uploads through `wp_handle_upload()`, which moves the file safely and
returns an error for disallowed types. Restrict the accepted MIME types explicitly
and check the capability first.

Good — capability check, nonce, MIME allowlist, and core upload handling:

```php
function my_plugin_handle_upload() {
	if ( ! current_user_can( 'upload_files' ) ) {
		wp_die( esc_html__( 'Insufficient permissions.', 'my-plugin' ), 403 );
	}

	check_admin_referer( 'my_plugin_upload' );

	if ( ! function_exists( 'wp_handle_upload' ) ) {
		require_once ABSPATH . 'wp-admin/includes/file.php';
	}

	$allowed_mimes = array(
		'jpg|jpeg' => 'image/jpeg',
		'png'      => 'image/png',
		'pdf'      => 'application/pdf',
	);

	$result = wp_handle_upload(
		$_FILES['my_plugin_file'],
		array(
			'test_form' => false,
			'mimes'     => $allowed_mimes,
		)
	);

	if ( isset( $result['error'] ) ) {
		wp_die( esc_html( $result['error'] ), 400 );
	}

	// $result['file'], $result['url'], and $result['type'] are now safe to use.
	return $result;
}
```

Never trust the client-provided filename or extension. `wp_handle_upload()`
verifies the real file type with `wp_check_filetype_and_ext()`, which inspects the
file contents rather than relying on the submitted name.

---

## Cross-Site Scripting (XSS)

Prevent XSS by:

- validating input;
- sanitizing stored content;
- escaping rendered output;
- limiting allowed HTML.

Output context determines the correct escaping strategy.

---

## Cross-Site Request Forgery (CSRF)

Protect state-changing actions with:

- nonces;
- capability checks;
- request validation.

Do not rely on HTTP method alone.

---

## Sensitive Data

Never expose:

- passwords;
- API keys;
- tokens;
- private configuration;
- internal identifiers when unnecessary.

Store secrets outside the repository whenever possible.

---

## Logging

Log security-relevant events.

Examples:

- failed authentication;
- permission failures;
- suspicious requests;
- repeated validation failures;
- external API failures.

Logs should support investigation without exposing sensitive information.

---

## Dependencies

Regularly review:

- plugins;
- themes;
- Composer packages;
- npm packages;
- external services.

Remove unused dependencies.

Update supported dependencies promptly after reviewing compatibility.

---

## AI Execution Checklist

## Investigation

☐ Identify protected resources.

☐ Review authentication.

☐ Review authorization.

☐ Review data flow.

☐ Review external integrations.

---

## Implementation

☐ Validate every input.

☐ Sanitize stored data.

☐ Escape rendered output.

☐ Verify capabilities.

☐ Verify nonces.

☐ Protect SQL queries.

☐ Secure file uploads.

---

## Verification

☐ Verify unauthorized access.

☐ Verify permission checks.

☐ Verify validation.

☐ Verify escaping.

☐ Review logs.

☐ Review exposed data.

---

## Examples

**Good Example** — capability, nonce, sanitize on input, escape on output

```php
add_action( 'admin_post_myplugin_save_event', 'myplugin_handle_save_event' );

function myplugin_handle_save_event() {
	$event_id = isset( $_POST['event_id'] ) ? absint( $_POST['event_id'] ) : 0;

	// 1. Authorisation: can THIS user edit THIS object?
	if ( ! $event_id || ! current_user_can( 'edit_post', $event_id ) ) {
		wp_die( esc_html__( 'You are not allowed to edit this event.', 'myplugin' ), 403 );
	}

	// 2. Intent: did the request come from our form? check_admin_referer dies on failure.
	check_admin_referer( 'myplugin_save_event_' . $event_id );

	// 3. Sanitize on the way in — never trust the shape or the type.
	$title = sanitize_text_field( wp_unslash( $_POST['title'] ?? '' ) );
	$notes = wp_kses_post( wp_unslash( $_POST['notes'] ?? '' ) );

	wp_update_post(
		array(
			'ID'         => $event_id,
			'post_title' => $title,
		)
	);
	update_post_meta( $event_id, '_event_notes', $notes );

	wp_safe_redirect( add_query_arg( 'updated', '1', wp_get_referer() ) );
	exit;
}
```

```php
<?php // Escape on the way out, with the function that matches the context. ?>
<h2><?php echo esc_html( get_the_title( $event_id ) ); ?></h2>
<a href="<?php echo esc_url( get_permalink( $event_id ) ); ?>"
   data-id="<?php echo esc_attr( $event_id ); ?>">
	<?php esc_html_e( 'View event', 'myplugin' ); ?>
</a>
```

**Bad Example** — trusted input, no checks, escaping in the wrong place

```php
add_action( 'admin_post_myplugin_save_event', 'myplugin_handle_save_event' );
add_action( 'admin_post_nopriv_myplugin_save_event', 'myplugin_handle_save_event' ); // public!

function myplugin_handle_save_event() {
	global $wpdb;

	// No capability check, no nonce: any visitor can post this form from anywhere.
	$id = $_POST['event_id'];

	// String interpolation into SQL — the classic injection point.
	$wpdb->query( "UPDATE {$wpdb->posts} SET post_title = '{$_POST['title']}' WHERE ID = {$id}" );

	// Escaping on write corrupts the stored value and still does not make output safe:
	// the same data rendered in an attribute or a URL needs a different escaper.
	update_post_meta( $id, '_event_notes', esc_html( $_POST['notes'] ) );
}
```

Escape late, at the point of output, using the escaper that matches the context — `esc_html()`
in body text, `esc_attr()` in an attribute, `esc_url()` in `href`. Escaping once on write
cannot satisfy all three.

---

## Common Mistakes

Avoid:

Trusting client input.

Skipping capability checks.

Skipping nonce verification.

Escaping data before storage.

Returning excessive API data.

Hardcoding secrets.

Using direct SQL without prepared statements.

Ignoring uploaded file validation.

---

## Completion Criteria

A feature is considered secure when:

- authentication is correct;
- authorization is enforced;
- every input is validated;
- stored data is sanitized;
- rendered output is escaped;
- sensitive information is protected;
- common attack vectors have been considered.

---

## Summary

Security is achieved through multiple layers of protection rather than a single defensive mechanism.

Well-designed WordPress applications validate every request, authorize every action, protect every output, and minimize the impact of potential failures.

## Related

- `knowledge/wordpress/20-users-and-capabilities.md`
- `knowledge/wordpress/18-rest-api.md`
- `knowledge/wordpress/19-database.md`
- `knowledge/security/09-input-validation.md`
- `knowledge/security/11-xss.md`
