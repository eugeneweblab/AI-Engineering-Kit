---
id: divi/07-dynamic-content
topic: divi
slug: dynamic-content
title: "Dynamic Content"
type: doc
order: 7
status: ready
tags: [divi, dynamic-content]
related: [divi/02-theme-builder, divi/15-custom-fields, divi/14-woocommerce, divi/19-security, divi/06-global-elements]
when_to_use: "Read before wiring a Divi module to post data, custom fields, or any value that must not be hard-coded."
---
# Dynamic Content

## Purpose

This document defines how to bind Divi modules to real data instead of typing values by
hand: **Dynamic Content** tokens for post fields (title, excerpt, featured image, author,
date), **custom fields** (native meta and ACF), and site/theme values. It is written so an
agent produces templates that render the *current* data for each post, not a frozen snapshot.

Dynamic Content is the mechanism that makes Theme Builder templates work: one template, many
posts. See [theme-builder](02-theme-builder.md) for where these tokens are consumed, and
[custom-fields](15-custom-fields.md) for defining the fields they read.

## Why It Matters

Hard-coding data into a builder that is meant to be a template defeats its purpose. If a post
template's H1 is literally typed as "My First Post", every post rendered through it says
"My First Post". Dynamic Content is what lets one blog-post template serve 500 posts, each with
its own title, image, and date. Getting this right also protects you: dynamic values pass through
Divi's escaping, whereas custom fields dumped into raw HTML or `Code` modules are a stored-XSS
vector. Dynamic Content is both a correctness feature (templates that actually template) and a
security boundary (values that are escaped by default). See [security](19-security.md).

## Core Principles

- **Template values must be dynamic, page values may be static.** Anything inside a Theme
  Builder template that varies per post — title, image, meta, custom fields — must be a Dynamic
  Content token. Static text there is a bug that surfaces as duplicated content.
- **Read fields through Dynamic Content, not raw meta echoes.** Selecting a custom field via the
  Dynamic Content picker escapes and formats it. Echoing `get_post_meta()` into a Code module
  bypasses escaping and invites XSS.
- **Provide fallbacks.** Dynamic tokens support a default value; supply one so a post missing an
  excerpt or image degrades gracefully instead of rendering an empty or broken element.
- **Match the field type to the module.** A URL field belongs in a link/button target, an image
  field in an Image module's dynamic source — not stuffed as text. Mismatches render raw markup
  or broken links.
- **Never trust user-supplied field values as HTML.** Treat custom fields written by editors or
  imported from elsewhere as untrusted; render them as text unless you have explicitly sanitized.

## Best Practices

- In every Theme Builder template, set the post title, featured image, author, date, and body via
  Dynamic Content tokens. Verify by previewing against two different posts.
- For ACF and native meta, use Divi's Dynamic Content field picker. If a field does not appear,
  register it (ACF exposes fields automatically; native meta may need `et_builder_...` filters or
  the ACF-style plugin bridge) rather than falling back to a raw echo.
- Always set a fallback/default on tokens that can be empty (excerpt, subtitle, secondary image).
- For repeating or relational data (galleries, related posts, product lists), use a purpose-built
  dynamic module (Blog, Portfolio, WooCommerce loop) or a custom module — Dynamic Content tokens
  are for single scalar values, not loops.
- When a value needs formatting Divi cannot do (currency, computed strings), compute it in a child
  theme via a Dynamic Content filter that returns an **escaped** string, and expose it as a token.
- Keep raw `Code` modules free of unescaped custom-field output; if you must, wrap in
  `esc_html()` / `wp_kses_post()` in PHP, never in the template UI.

## Examples

**Good Example** — a post template bound to dynamic fields with a fallback and safe custom field

```text
Theme Builder → "Blog Post Template"
  Text (H1)      → Dynamic Content: Post Title
  Image          → Dynamic Content: Featured Image (fallback: default-cover.jpg)
  Text (byline)  → Dynamic Content: Post Author • Post Date
  Text (subtitle)→ Dynamic Content: Custom Field "subtitle" (fallback: "")
```

```php
// child theme: expose a computed, ESCAPED value as a Dynamic Content option
add_filter( 'et_builder_resolve_dynamic_content', function ( $value, $name, $settings, $post_id ) {
    if ( $name === 'reading_time' ) {
        $words = str_word_count( wp_strip_all_tags( get_post_field( 'post_content', $post_id ) ) );
        return esc_html( max( 1, (int) ceil( $words / 200 ) ) . ' min read' ); // escaped before return
    }
    return $value;
}, 10, 4 );
```

Why: one template renders every post correctly; the featured image has a fallback so image-less
posts do not break; the custom value is computed server-side and escaped, so it is XSS-safe.

**Bad Example** — hard-coded template and unescaped field echo

```text
Theme Builder → "Blog Post Template"
  Text (H1)  → "How to Bake Bread"          // static: EVERY post now titled this
```

```php
// Code module / raw echo — untrusted meta injected into HTML with no escaping
echo '<div class="subtitle">' . get_post_meta( get_the_ID(), 'subtitle', true ) . '</div>';
// if an editor saved <script> in the field, it executes → stored XSS
```

Why this is wrong: the static H1 makes the template non-reusable, and the raw `get_post_meta`
echo bypasses escaping, turning a content field into a stored-XSS hole.

## Common Mistakes

- Typing per-post values as static text inside a Theme Builder template.
- Echoing `get_post_meta()` / ACF `the_field()` output into Code modules without escaping.
- No fallback on optional tokens, so empty fields render broken images or empty headings.
- Using a Dynamic Content token where a loop module is required (trying to list many items).
- Assuming a field is available in the picker without registering it, then hacking around it.
- Formatting values in the browser with JS when the value should be resolved and escaped server-side.

## Production Tips

- Preview every dynamic template against a post that has empty optional fields — that is where
  missing fallbacks show up.
- When importing content, verify custom fields survived the import before assuming tokens resolve.
- Cache-heavy sites: dynamic values are resolved at render; confirm your page cache varies by
  post, not by template, so each post caches its own resolved output.

## AI Review Checklist

- Are all per-post values in Theme Builder templates Dynamic Content tokens, not static text?
- Do custom fields render through the Dynamic Content picker (escaped), never raw `get_post_meta` echoes?
- Does every optional token have a sensible fallback/default?
- Are computed dynamic values escaped (`esc_html`/`wp_kses_post`) before being returned to Divi?
- Is repeating/relational data handled by a loop module, not a scalar token?

## Related

- `knowledge/divi/02-theme-builder.md`
- `knowledge/divi/15-custom-fields.md`
- `knowledge/divi/14-woocommerce.md`
- `knowledge/divi/19-security.md`
- `knowledge/divi/06-global-elements.md`
