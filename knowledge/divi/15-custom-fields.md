---
id: divi/15-custom-fields
topic: divi
slug: custom-fields
title: "Custom Fields"
type: doc
order: 15
status: ready
tags: [divi, custom-fields, wp_kses_post, editor, get_the_ID, get_post_meta, esc_attr, esc_html]
related: [divi/07-dynamic-content, divi/02-theme-builder, divi/16-wordpress-hooks, divi/04-custom-modules, divi/19-security]
when_to_use: "Read before wiring ACF/meta-box data into Divi via dynamic content or custom modules."
---
# Custom Fields

## Purpose

This document defines how to connect **WordPress custom fields** (post meta — typically via
**ACF**, Meta Box, or Pods) to **Divi**, so structured data drives the design instead of
hard-coded text. It is written so an agent can wire a field into a Divi template safely, with
correct escaping and no data loss when content changes.

Custom fields are the bridge between *content* (managed by an editor) and *presentation*
(built in Divi). Divi reads them through its **Dynamic Content** feature and, for anything
beyond that, through PHP in a child theme or a custom module. The recurring failure is treating
field output as trusted HTML — an XSS hole — or hard-coding what should be dynamic.

## Why It Matters

Custom fields are where user- or editor-supplied data enters the page, which makes them a
security boundary and a maintenance pivot at once. Rendered without escaping, a field's value
becomes stored XSS that runs for every visitor; this is the single most common vulnerability in
custom WordPress/Divi work. On the maintenance side, hard-coding a value that belongs in a field
(a price, a phone number, a document link) means every change is a developer task and every
template drifts out of sync. Wiring fields correctly — dynamic, escaped, with sane fallbacks —
is what lets non-developers safely run the site the agent built. See [security](19-security.md).

## Core Principles

- **Escape on output, always, by context.** `esc_html()` for text, `esc_url()` for links,
  `esc_attr()` for attribute values. Never echo a field's raw value into HTML.
- **Prefer Divi Dynamic Content for display.** For showing a field in a module, use Divi's
  built-in [dynamic content](07-dynamic-content.md) picker — it handles the common cases without
  custom code. Drop to PHP only when the picker cannot express the need.
- **Read meta through the right API.** Use ACF's `get_field()` / `the_field()` (which honor
  field types and formatting) or core `get_post_meta()`. Do not query the meta table directly.
- **Design for empty.** A field may be blank on some posts. Provide a fallback or hide the
  element; never render "Price: " with nothing after it.
- **Content in fields, not in Divi.** Anything an editor may change is a field, so it updates
  everywhere the template renders — not a value typed into one module.

## Best Practices

- Register fields with ACF (or code) and bind them via Divi Dynamic Content in Theme Builder
  templates, so every post of a type inherits the layout and pulls its own data.
- For custom PHP output (shortcode, custom module, template), escape every value at the point of
  output with the context-appropriate function — even "trusted" admin-entered fields.
- Use `the_field()` cautiously: it echoes unescaped. Prefer `echo esc_html( get_field('key') )`
  unless the field is explicitly a rich-text/HTML field you have sanitized on save.
- Give ACF WYSIWYG/HTML fields a sanitization policy: sanitize on save (`wp_kses_post`) so the
  stored value is already safe, then escaping on output stays simple.
- Provide fallbacks in the query, not the markup: `$price = get_field('price') ?: 'Contact us';`.
- Expose a field to Divi Dynamic Content programmatically with the
  `et_builder_custom_fields` / dynamic-content filters when you need a computed value, rather
  than pasting raw meta into a Code module.
- Cache expensive lookups (e.g. related-object fields) where they run on every render.

## Examples

**Good Example** — dynamic, escaped, with a fallback

```php
// Custom module render or shortcode: value is escaped for its context and
// degrades gracefully when the field is empty.
$phone = get_field( 'contact_phone' );               // ACF returns the stored value
if ( $phone ) {
    printf(
        '<a href="tel:%s">%s</a>',
        esc_attr( preg_replace( '/\D+/', '', $phone ) ), // safe in href attribute
        esc_html( $phone )                                // safe in text node
    );
}
// No output at all when empty — never a dangling "Call: " label.
```

**Bad Example** — raw meta echoed into HTML

```php
// Stored XSS: if an editor (or an import) put <script> in the field,
// it runs for every visitor. And no fallback when the field is empty.
echo '<div>Phone: ' . get_post_meta( get_the_ID(), 'contact_phone', true ) . '</div>';
the_field( 'bio_html' ); // echoes unescaped rich text straight to the page
```

## Common Mistakes

- Echoing `get_post_meta()` / `the_field()` output without escaping — stored XSS.
- Hard-coding values in Divi modules that belong in fields, so they never update.
- Assuming a field is always populated, rendering empty labels or broken links.
- Querying the `wp_postmeta` table directly instead of using ACF/core APIs and their formatting.
- Storing raw HTML in a field and outputting it unsanitized, or sanitizing neither on save nor output.
- Pasting a computed value into a one-off Code module instead of exposing it to Dynamic Content.

## Production Tips

- Keep field definitions in code (ACF local JSON or PHP registration) under version control so
  staging and production stay in sync and fields survive a database refresh.
- When migrating content, re-sanitize imported meta — imports bypass the on-save sanitization
  that normally protects HTML fields.
- Audit every Code module and custom template for an unescaped meta value before launch; it is
  the highest-yield security check on a Divi build.

## AI Review Checklist

- Is every field value escaped on output with the correct function for its context?
- Is display done through Divi Dynamic Content where possible, PHP only when needed?
- Are fields read via ACF/core APIs, not direct meta-table queries?
- Does every field render have a fallback or hide cleanly when empty?
- Are HTML/WYSIWYG fields sanitized on save (`wp_kses_post`)?
- Are field definitions version-controlled and present on all environments?

## Related

- `knowledge/divi/07-dynamic-content.md`
- `knowledge/divi/02-theme-builder.md`
- `knowledge/divi/16-wordpress-hooks.md`
- `knowledge/divi/04-custom-modules.md`
- `knowledge/divi/19-security.md`
