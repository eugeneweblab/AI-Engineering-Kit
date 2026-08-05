---
id: wordpress/02-project-structure
topic: wordpress
slug: project-structure
title: "WordPress Project Structure"
type: doc
order: 2
status: ready
tags: [wordpress, project-structure, register, add_action, wp_unslash, WP_REST_Response, sanitize_text_field, WP_Query]
related: [wordpress/01-wordpress-architecture, wordpress/14-theme-development, wordpress/15-plugin-development, wordpress/04-code-style, wordpress/27-deployment]
when_to_use: "Read before organizing files or deciding where new code belongs in a WordPress project."
---
# WordPress Project Structure

## Purpose

This document defines the recommended project structure for WordPress applications.

The objective is to organize code according to responsibilities rather than file types, making the project easier to understand, maintain, test, and extend.

The exact folder names may vary between projects, but the architectural principles should remain consistent.

---

## Core Principle

A directory should represent a responsibility, not a technology.

Good examples:

- API
- Services
- Modules
- Blocks
- Templates

Poor examples:

- Functions
- Misc
- Helpers2
- New
- Temp

Every folder should communicate its purpose immediately.

---

## High-Level Structure

A typical enterprise WordPress project may be organized as follows:

```text
project/
│
├── app/
├── config/
├── public/
├── storage/
├── vendor/
│
├── wp-content/
│   ├── plugins/
│   ├── mu-plugins/
│   ├── themes/
│   ├── uploads/
│   └── languages/
│
└── tools/
```

The exact layout depends on the project's deployment strategy.

---

## Theme Structure

A modern custom theme may contain:

```text
theme/
│
├── assets/
│   ├── css/
│   ├── js/
│   ├── fonts/
│   └── images/
│
├── blocks/
├── modules/
├── templates/
├── template-parts/
├── services/
├── api/
├── helpers/
├── hooks/
├── inc/
├── languages/
├── tests/
│
├── functions.php
└── style.css
```

Each directory should have a clearly defined responsibility.

---

## Plugin Structure

Large plugins should follow a modular architecture.

Example:

```text
plugin/
│
├── src/
│   ├── Admin/
│   ├── API/
│   ├── CLI/
│   ├── Commands/
│   ├── Controllers/
│   ├── DTO/
│   ├── Helpers/
│   ├── Hooks/
│   ├── Models/
│   ├── Repositories/
│   ├── Services/
│   ├── Validation/
│   └── Views/
│
├── assets/
├── languages/
├── tests/
│
└── plugin.php
```

Business logic should reside inside dedicated classes rather than the bootstrap file.

The root `plugin.php` should only hold the plugin header, guard direct access, load the autoloader, expose a path constant, and wire the container on `plugins_loaded`:

```php
<?php
/**
 * Plugin Name:       Acme Commerce
 * Description:       Product catalog and checkout for Acme.
 * Version:           1.4.0
 * Requires at least: 6.4
 * Requires PHP:      8.1
 * Text Domain:       acme-commerce
 *
 * @package Acme\Commerce
 */

defined( 'ABSPATH' ) || exit;

define( 'ACME_COMMERCE_FILE', __FILE__ );

require_once __DIR__ . '/vendor/autoload.php';

add_action(
	'plugins_loaded',
	static function () {
		( new Acme\Commerce\Plugin() )->register();
	}
);
```

The `Plugin` class then instantiates the hook, controller, and service objects and calls their own `register()` methods. Everything else lives under `src/`, keeping the bootstrap file free of business logic.

---

## Responsibility Guidelines

## Templates

Responsible for:

- markup;
- layout;
- presentation.

Templates should not contain business logic. A template receives already-prepared data and is responsible only for rendering it safely. Every dynamic value must be escaped at the point of output, and any form that mutates state must carry a nonce.

Good — a `Views/settings-form.php` template that only renders and escapes:

```php
<?php
/**
 * Admin settings form.
 *
 * @var string $tagline Current saved tagline, already loaded by the controller.
 */
defined( 'ABSPATH' ) || exit;
?>
<form method="post" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>">
	<input type="hidden" name="action" value="acme_save_settings">
	<?php wp_nonce_field( 'acme_save_settings', 'acme_settings_nonce' ); ?>

	<label for="acme-tagline"><?php esc_html_e( 'Tagline', 'acme-commerce' ); ?></label>
	<input
		id="acme-tagline"
		name="acme_tagline"
		type="text"
		value="<?php echo esc_attr( $tagline ); ?>"
	>

	<?php submit_button(); ?>
</form>
```

Bad — a template that queries the database, mutates state, and echoes raw input:

```php
<?php
// A template must never do this: no queries, no writes, no unescaped output.
if ( isset( $_POST['acme_tagline'] ) ) {
	update_option( 'acme_tagline', $_POST['acme_tagline'] ); // unsanitized, no nonce.
}
echo '<h2>' . get_option( 'acme_tagline' ) . '</h2>'; // unescaped output.
```

The write, the nonce check, and the sanitization belong in a controller (see the `API` and `Hooks` sections), not in the view.

---

## Services

Responsible for:

- business rules;
- workflows;
- integrations;
- reusable operations.

Services should be framework-independent whenever practical. A service owns a workflow and returns plain data; it should not read from `$_POST` or echo markup. A `Services/Product_Service.php` that wraps a `WP_Query`:

```php
<?php

namespace Acme\Commerce\Services;

use WP_Query;

class Product_Service {

	/**
	 * Return the IDs of featured, published products.
	 *
	 * @param int $limit Maximum number of products to return.
	 * @return int[]
	 */
	public function get_featured_ids( int $limit = 10 ): array {
		$query = new WP_Query(
			array(
				'post_type'      => 'product',
				'post_status'    => 'publish',
				'posts_per_page' => $limit,
				'no_found_rows'  => true,
				'fields'         => 'ids',
				'meta_query'     => array(
					array(
						'key'   => '_acme_featured',
						'value' => '1',
					),
				),
			)
		);

		return $query->posts;
	}
}
```

Note the deliberate performance flags: `'fields' => 'ids'` avoids hydrating full post objects, and `'no_found_rows' => true` skips the `SQL_CALC_FOUND_ROWS` count when pagination is not needed.

When a workflow needs a custom table rather than posts, keep the raw SQL in a `Repositories/` class and always parameterize with `$wpdb->prepare()`:

```php
<?php

namespace Acme\Commerce\Repositories;

class Subscriber_Repository {

	public function find_by_email( string $email ): ?object {
		global $wpdb;

		$table = $wpdb->prefix . 'acme_subscribers';

		// Good: %s placeholder is escaped by prepare(); the table name is a trusted constant.
		$row = $wpdb->get_row(
			$wpdb->prepare(
				"SELECT * FROM {$table} WHERE email = %s LIMIT 1",
				$email
			)
		);

		return $row ?: null;
	}
}
```

Never interpolate a variable directly into a query string (`"... WHERE email = '$email'"`) — that is a SQL injection. Placeholders (`%s`, `%d`, `%f`) go through `prepare()`.

---

## API

Responsible for:

- endpoint registration;
- request validation;
- response formatting.

Controllers should delegate work to services. Register routes on the `rest_api_init` hook, declare argument schemas so WordPress sanitizes and validates before your callback runs, and always supply a real `permission_callback`.

```php
<?php

namespace Acme\Commerce\API;

use WP_REST_Request;
use WP_REST_Response;
use Acme\Commerce\Services\Newsletter_Service;

class Newsletter_Controller {

	private Newsletter_Service $newsletter;

	public function __construct( Newsletter_Service $newsletter ) {
		$this->newsletter = $newsletter;
	}

	public function register(): void {
		add_action( 'rest_api_init', array( $this, 'register_routes' ) );
	}

	public function register_routes(): void {
		register_rest_route(
			'acme/v1',
			'/subscribers',
			array(
				'methods'             => 'POST',
				'callback'            => array( $this, 'create_subscriber' ),
				'permission_callback' => array( $this, 'can_subscribe' ),
				'args'                => array(
					'email' => array(
						'required'          => true,
						'type'              => 'string',
						'format'            => 'email',
						'sanitize_callback' => 'sanitize_email',
						'validate_callback' => static function ( $value ) {
							return false !== is_email( $value );
						},
					),
				),
			)
		);
	}

	public function can_subscribe(): bool {
		return current_user_can( 'edit_posts' );
	}

	public function create_subscriber( WP_REST_Request $request ): WP_REST_Response {
		$email = $request->get_param( 'email' );

		// The controller only orchestrates; the workflow lives in the service.
		$id = $this->newsletter->subscribe( $email );

		return new WP_REST_Response( array( 'id' => $id ), 201 );
	}
}
```

Bad — a route with `'permission_callback' => '__return_true'` and no `args` schema forces you to sanitize by hand inside the callback and, worse, ships an open write endpoint. Let the framework validate at the boundary.

Classic (non-REST) admin form submissions are handled the same way — a controller wired to the `admin_post_{action}` hook that checks the capability, verifies the nonce, sanitizes, then delegates. This is the handler for the `Views/settings-form.php` template shown earlier:

```php
public function register(): void {
	add_action( 'admin_post_acme_save_settings', array( $this, 'handle_save' ) );
}

public function handle_save(): void {
	if ( ! current_user_can( 'manage_options' ) ) {
		wp_die( esc_html__( 'Insufficient permissions.', 'acme-commerce' ) );
	}

	$nonce = isset( $_POST['acme_settings_nonce'] )
		? sanitize_text_field( wp_unslash( $_POST['acme_settings_nonce'] ) )
		: '';

	if ( ! wp_verify_nonce( $nonce, 'acme_save_settings' ) ) {
		wp_die( esc_html__( 'Security check failed.', 'acme-commerce' ) );
	}

	$tagline = sanitize_text_field( wp_unslash( $_POST['acme_tagline'] ?? '' ) );
	update_option( 'acme_tagline', $tagline );

	wp_safe_redirect( admin_url( 'options-general.php?page=acme-commerce' ) );
	exit;
}
```

Capability check, then nonce verification, then sanitization — in that order — is the standard WordPress write-path contract.

---

## Hooks

Responsible for:

- registering actions;
- registering filters;
- connecting WordPress events to application logic.

Avoid embedding business logic directly inside callbacks. A `Hooks/` class registers real WordPress hooks and immediately delegates to a service. This is also the correct home for registering a custom post type on `init` — never on `plugins_loaded`, which fires too early for post-type registration.

```php
<?php

namespace Acme\Commerce\Hooks;

use Acme\Commerce\Services\Product_Service;

class Product_Hooks {

	private Product_Service $products;

	public function __construct( Product_Service $products ) {
		$this->products = $products;
	}

	public function register(): void {
		add_action( 'init', array( $this, 'register_post_type' ) );
		// save_post_{post_type} passes ( $post_id, $post, $update ).
		add_action( 'save_post_product', array( $this, 'sync_price' ), 10, 3 );
	}

	public function register_post_type(): void {
		register_post_type(
			'product',
			array(
				'labels'       => array(
					'name'          => __( 'Products', 'acme-commerce' ),
					'singular_name' => __( 'Product', 'acme-commerce' ),
				),
				'public'       => true,
				'show_in_rest' => true,
				'menu_icon'    => 'dashicons-cart',
				'has_archive'  => true,
				'rewrite'      => array( 'slug' => 'products' ),
				'supports'     => array( 'title', 'editor', 'thumbnail', 'custom-fields' ),
			)
		);
	}

	public function sync_price( int $post_id, \WP_Post $post, bool $update ): void {
		// Guard clauses keep the callback thin; the real work is in the service.
		if ( wp_is_post_autosave( $post_id ) || wp_is_post_revision( $post_id ) ) {
			return;
		}

		$this->products->recalculate_price( $post_id );
	}
}
```

The callback stays small — guard, then delegate. Pricing rules live in `Product_Service`, not in the hook.

---

## Helpers

Responsible for:

- small reusable utility functions;
- formatting;
- conversions;
- lightweight abstractions.

Helpers should not become a second service layer. A helper is a small, pure-ish function — for example, normalizing untrusted input before it reaches a service. WordPress ships the correct primitives; use them rather than rolling your own escaping.

Good — sanitize on the way in, escape on the way out:

```php
<?php

namespace Acme\Commerce\Helpers;

class Request_Helper {

	/**
	 * Read a text field from a request array, unslashed and sanitized.
	 */
	public static function text( array $source, string $key ): string {
		if ( ! isset( $source[ $key ] ) ) {
			return '';
		}

		// wp_unslash() reverses WordPress's added slashes before sanitizing.
		return sanitize_text_field( wp_unslash( $source[ $key ] ) );
	}
}
```

```php
// At the point of output, escape for the context:
echo '<h2>' . esc_html( $title ) . '</h2>';               // HTML body
printf( '<a href="%s">', esc_url( $link ) );               // URL attribute
printf( '<input value="%s">', esc_attr( $value ) );        // HTML attribute
```

Bad — a helper that "cleans" input with `strip_tags()` or `trim()` alone, or that escapes with `htmlspecialchars()` instead of the context-aware `esc_*` functions. WordPress's `sanitize_*` and `esc_*` families handle encoding edge cases that ad-hoc string functions miss.

---

## Modules

A module groups related functionality.

Example:

```text
Pricing/

Testimonials/

Newsletter/

Products/

Checkout/
```

Each module should encapsulate one feature.

---

## Asset Organization

Separate assets by type.

Example:

```text
assets/

css/

js/

images/

fonts/

icons/
```

Avoid placing unrelated files together. Assets under `assets/` are never referenced with a hardcoded path — they are registered through the enqueue API so WordPress can handle dependencies, versioning (cache busting), and correct URLs across environments. A dedicated `Hooks/Asset_Hooks.php` keeps this out of templates:

```php
<?php

namespace Acme\Commerce\Hooks;

class Asset_Hooks {

	public function register(): void {
		add_action( 'wp_enqueue_scripts', array( $this, 'enqueue_front_assets' ) );
	}

	public function enqueue_front_assets(): void {
		$version = '1.4.0';

		wp_enqueue_style(
			'acme-commerce',
			plugins_url( 'assets/css/app.css', ACME_COMMERCE_FILE ),
			array(),
			$version
		);

		wp_enqueue_script(
			'acme-commerce',
			plugins_url( 'assets/js/app.js', ACME_COMMERCE_FILE ),
			array( 'wp-element' ),
			$version,
			true // Load in the footer.
		);

		// Pass server data to the script instead of inlining it into markup.
		wp_localize_script(
			'acme-commerce',
			'acmeSettings',
			array(
				'restUrl' => esc_url_raw( rest_url( 'acme/v1/subscribers' ) ),
				'nonce'   => wp_create_nonce( 'wp_rest' ),
			)
		);
	}
}
```

Bad — echoing `<script src="...">` or `<link>` tags directly in a template. That bypasses dependency resolution and versioning, and often loads the same asset twice.

---

## JavaScript Organization

Modern JavaScript should follow feature-based organization.

Example:

```text
components/

hooks/

services/

pages/

utils/

types/
```

Avoid placing hundreds of files in a single directory.

---

## PHP Organization

Prefer:

Small classes

Single responsibility

Dependency injection

Composition

Namespaces

Avoid:

God classes

Static utility containers

Deep inheritance

Large procedural files

---

## Naming Conventions

Prefer descriptive names.

Good

```text
ProductService.php

NewsletterController.php

ReviewRepository.php
```

Avoid

```text
Functions.php

Utils.php

Helpers.php

Stuff.php

New.php
```

Names should describe responsibilities.

---

## AI Execution Checklist

## Investigation

☐ Understand the existing project structure.

☐ Identify architectural patterns.

☐ Review naming conventions.

☐ Identify feature modules.

---

## Planning

☐ Place new code in the correct directory.

☐ Preserve project conventions.

☐ Avoid creating duplicate responsibilities.

☐ Minimize architectural changes.

---

## Implementation

☐ Respect folder responsibilities.

☐ Keep files cohesive.

☐ Reuse existing modules.

☐ Avoid unnecessary nesting.

---

## Verification

☐ Verify consistency.

☐ Verify discoverability.

☐ Verify maintainability.

☐ Verify documentation.

---

## Examples

**Good Example** — directories named after responsibilities

```text
wp-content/plugins/myplugin/
├── myplugin.php                  bootstrap: constants, autoloader, hook registration
├── inc/
│   ├── events/                   one feature, everything it owns
│   │   ├── class-event-post-type.php
│   │   ├── class-event-repository.php
│   │   └── class-event-rest-controller.php
│   ├── registrations/
│   │   ├── class-registration-service.php
│   │   └── class-registration-mailer.php
│   └── shared/
│       └── class-capability-map.php
├── blocks/
│   └── event-list/               block.json, index.js, render.php
├── templates/
│   └── single-myplugin_event.php
└── tests/
    └── events/EventRepositoryTest.php
```

A new engineer asked to change registration emails opens `inc/registrations/` and finds every
file involved. Deleting the feature means deleting one directory.

**Bad Example** — directories named after file types

```text
wp-content/plugins/myplugin/
├── myplugin.php
├── functions/
│   ├── functions.php             1,800 lines, everything
│   ├── functions-new.php         nobody remembers what "new" meant
│   └── helpers2.php
├── classes/
│   ├── class-event.php
│   ├── class-registration.php
│   └── class-misc.php
├── ajax/
└── temp/
```

Nothing here says what the plugin *does*. Changing registration emails means searching all of
`functions/`, and no directory can be deleted with confidence because responsibilities are
spread across every one of them.

---

## Common Mistakes

Avoid:

Creating folders without a clear responsibility.

Organizing files by technology instead of feature.

Large "helpers" directories.

Mixing presentation with business logic.

Deep directory nesting.

Duplicate modules.

Inconsistent naming.

---

## Completion Criteria

A project structure is considered successful when:

- every directory has a clear responsibility;
- similar functionality is grouped together;
- new developers can quickly locate code;
- architectural boundaries remain clear;
- future growth can be accommodated without major restructuring.

---

## Summary

A well-organized project structure reduces cognitive load, improves maintainability, and helps both engineers and AI coding agents navigate the codebase efficiently.

The goal is not to create the perfect folder hierarchy, but to create one that communicates architectural intent clearly.

## Related

- `knowledge/wordpress/01-wordpress-architecture.md`
- `knowledge/wordpress/14-theme-development.md`
- `knowledge/wordpress/15-plugin-development.md`
- `knowledge/wordpress/04-code-style.md`
- `knowledge/wordpress/27-deployment.md`
