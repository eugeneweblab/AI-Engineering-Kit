---
id: wordpress/21-media-and-uploads
topic: wordpress
slug: media-and-uploads
title: "Media and Uploads"
type: doc
order: 21
status: ready
tags: [wordpress, media-and-uploads]
related: [wordpress/06-security, wordpress/05-performance, wordpress/14-theme-development, wordpress/27-deployment, wordpress/19-database]
when_to_use: "Read before handling uploads or rendering images — accepting files, registering image sizes, outputting responsive images, or offloading media."
---
# Media and Uploads

## Purpose

This document defines how to handle media in WordPress: accepting uploads safely, registering
and regenerating image sizes, emitting responsive markup, and the deployment concerns that
come with a growing uploads directory.

Uploads are the one place where a WordPress site accepts arbitrary binary data from users.
They are correspondingly the place where a permissive default becomes a remote code execution
vulnerability.

---

## Core Principle

**Never trust a filename, extension, or client-supplied MIME type.** All three are attacker
controlled. Verify content, restrict types to what the site needs, and let WordPress place the
file.

```php
// Bad: trusts $_FILES entirely and writes wherever it likes.
move_uploaded_file( $_FILES['file']['tmp_name'], WP_CONTENT_DIR . '/uploads/' . $_FILES['file']['name'] );
```

That single line permits `shell.php`, path traversal via the name, and a file the media
library does not know about.

---

## Accepting an Upload

`media_handle_upload()` runs the full pipeline: type verification, sanitized filename, correct
directory, attachment record, and generated sizes.

```php
function acme_handle_event_image( int $event_id ) {
	if ( ! current_user_can( 'upload_files' ) ) {
		return new WP_Error( 'acme_forbidden', __( 'Not allowed.', 'acme-events' ), array( 'status' => 403 ) );
	}

	check_admin_referer( 'acme_event_image_' . $event_id );

	if ( empty( $_FILES['event_image']['name'] ) ) {
		return new WP_Error( 'acme_no_file', __( 'No file was uploaded.', 'acme-events' ) );
	}

	// These includes are not loaded on the front end.
	require_once ABSPATH . 'wp-admin/includes/image.php';
	require_once ABSPATH . 'wp-admin/includes/file.php';
	require_once ABSPATH . 'wp-admin/includes/media.php';

	$attachment_id = media_handle_upload(
		'event_image',
		$event_id,
		array(),
		array( 'test_form' => false )
	);

	if ( is_wp_error( $attachment_id ) ) {
		return $attachment_id;
	}

	set_post_thumbnail( $event_id, $attachment_id );

	return $attachment_id;
}
```

For files fetched server-side rather than posted, the equivalents are `wp_handle_sideload()`
and `media_sideload_image()` — never `file_get_contents()` into the uploads directory.

---

## Restricting File Types

WordPress allows a broad default set. Narrow it to what the site actually needs:

```php
add_filter( 'upload_mimes', function ( array $mimes ) {
	if ( current_user_can( 'manage_options' ) ) {
		return $mimes;                      // administrators keep the full set
	}

	return array(
		'jpg|jpeg' => 'image/jpeg',
		'png'      => 'image/png',
		'webp'     => 'image/webp',
		'pdf'      => 'application/pdf',
	);
} );
```

Verification happens against file content, not the name — `wp_check_filetype_and_ext()` uses
`finfo` and, for images, `getimagesize()`. Keep that check; a file named `photo.jpg`
containing PHP is exactly what it is designed to catch.

**SVG deserves its own decision.** An SVG is an XML document that may contain `<script>` and
event handlers, so allowing uploads is granting stored XSS to anyone who can upload. If the
site needs SVG, sanitize it on upload with a dedicated library and restrict the capability to
trusted roles. "Just add it to `upload_mimes`" is not an acceptable answer.

---

## Hardening the Uploads Directory

Even with correct handling, the uploads directory should not execute code. At the web server:

```nginx
# nginx — deny execution anywhere under uploads
location ~* /wp-content/uploads/.*\.(php|phtml|php[0-9])$ {
	deny all;
}
```

```apache
# Apache — wp-content/uploads/.htaccess
<FilesMatch "\.(php|phtml|php[0-9])$">
	Require all denied
</FilesMatch>
```

This is defence in depth: it turns a successful upload bypass from a compromise into a
harmless file. See [Security](06-security.md).

---

## Image Sizes

```php
add_action( 'after_setup_theme', function () {
	add_theme_support( 'post-thumbnails' );

	add_image_size( 'acme-card', 640, 400, true );          // hard crop
	add_image_size( 'acme-hero', 1600, 900, true );

	// Expose sizes to the editor's size dropdown.
	add_filter( 'image_size_names_choose', function ( array $sizes ) {
		return array_merge( $sizes, array( 'acme-card' => __( 'Card', 'acme' ) ) );
	} );
} );
```

Every registered size multiplies storage for every upload — a site with twelve sizes stores
thirteen files per image. Register what templates use, and remove sizes that nothing renders.

New sizes apply only to future uploads; existing media needs regeneration:

```bash
wp media regenerate --image_size=acme-card --yes
```

WordPress also scales down very large uploads by default (`big_image_size_threshold`, 2560px)
and keeps the original as `-scaled`. Raise or disable it deliberately, not by accident:

```php
add_filter( 'big_image_size_threshold', fn() => 3840 );
```

---

## Rendering Responsive Images

Use the attachment helpers; they emit `srcset`, `sizes`, dimensions, and lazy loading:

**Good Example** — responsive, dimensioned, lazy where appropriate

```php
echo wp_get_attachment_image(
	$attachment_id,
	'acme-card',
	false,
	array(
		'class'    => 'card__image',
		'sizes'    => '(max-width: 640px) 100vw, 640px',
		'loading'  => 'lazy',
		'decoding' => 'async',
		'alt'      => esc_attr( get_post_meta( $attachment_id, '_wp_attachment_image_alt', true ) ),
	)
);

// The featured image, with the same benefits.
the_post_thumbnail( 'acme-hero', array( 'loading' => 'eager', 'fetchpriority' => 'high' ) );
```

**Bad Example** — no srcset, no dimensions (so the page shifts as it loads), no alt

```php
echo '<img src="' . wp_get_attachment_url( $attachment_id ) . '">';
```

The above-the-fold image should be `eager` with `fetchpriority="high"`; lazy-loading the LCP
image delays it by a full round trip — see [Performance](05-performance.md).

Alt text lives in `_wp_attachment_image_alt`, and `wp_get_attachment_image()` reads it
automatically. Passing an empty `alt` for a decorative image is correct; omitting the concept
entirely is not — see [Accessibility — Images](../accessibility/09-images.md).

---

## Attachment Metadata

```php
$meta = wp_get_attachment_metadata( $attachment_id );
// array( 'width' => 1600, 'height' => 900, 'file' => '2026/07/hero.jpg', 'sizes' => array( … ) )

$src = wp_get_attachment_image_src( $attachment_id, 'acme-card' );
// array( url, width, height, is_intermediate )
```

Attachments are posts (`post_type = attachment`), so they carry meta, terms, and permissions
like any other content — including in queries, where they are excluded unless asked for.

---

## Operations

The uploads directory is the largest and least reproducible part of a WordPress site:

- **Do not commit it.** Exclude `wp-content/uploads` from version control.
- **Sync it separately** for staging (`wp media` and `rsync`, or an offload plugin).
- **Back it up separately** from the database; a database backup alone cannot restore a site.
- **Offloading to S3 or a CDN** removes it from the application server — verify that image
  sizes, regeneration, and deletion still work end to end afterwards.

---

## Common Mistakes

- **`move_uploaded_file()` on `$_FILES`** instead of the media API.
- **Trusting the extension or the client MIME type.**
- **Allowing SVG uploads unsanitized.**
- **No capability check or nonce** before handling an upload.
- **Uploads directory able to execute PHP.**
- **Registering many image sizes** and never removing unused ones.
- **Raw `<img>` tags** without `srcset`, dimensions, or alt.
- **Lazy-loading the hero image**, delaying LCP.
- **New image sizes without regeneration**, so old media renders at the wrong dimensions.
- **Committing `uploads/` to the repository.**

---

## Verification Checklist

- Does every upload path check a capability and a nonce, and go through the media API?
- Are allowed MIME types restricted to what the site needs?
- If SVG is allowed, is it sanitized and limited to trusted roles?
- Is PHP execution blocked in the uploads directory at the web server?
- Are registered image sizes actually used, and has media been regenerated after changes?
- Does image output use `wp_get_attachment_image()` with real alt text and dimensions?
- Is the LCP image eager with high fetch priority, and everything else lazy?
- Is `uploads/` excluded from version control and backed up separately?

---

## Summary

Let WordPress handle uploads: it verifies content, sanitizes names, and files everything
correctly. Restrict types, block execution in the uploads directory, register only the image
sizes you render, and emit responsive markup with real alt text.

## Related

- `knowledge/wordpress/05-performance.md`
- `knowledge/wordpress/06-security.md`
- `knowledge/wordpress/16-block-editor.md`
- `knowledge/security/15-file-upload-security.md`
