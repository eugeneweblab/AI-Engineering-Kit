---
id: wordpress/24-internationalization
topic: wordpress
slug: internationalization
title: "Internationalization"
type: doc
order: 24
status: ready
tags: [wordpress, internationalization, esc_html__, esc_html, plugin_basename, add_action, init, load_theme_textdomain]
related: [wordpress/14-theme-development, wordpress/15-plugin-development, wordpress/16-block-editor, wordpress/04-code-style, wordpress/26-wp-cli]
when_to_use: "Read before writing user-facing strings — choosing a translation function, loading a text domain, or translating strings in JavaScript."
---
# Internationalization

## Purpose

This document defines how to make WordPress code translatable: which function to use for each
situation, how text domains are loaded, how to handle placeholders and plurals, and how to
translate strings in JavaScript.

Internationalization is cheap when done as you write and expensive to retrofit — every
hardcoded string has to be found, extracted, and re-tested.

---

## Core Principle

**Every user-facing string passes through a translation function with a literal text domain.**

```php
// Bad: untranslatable, and unescaped.
echo 'Read more';

// Bad: the text domain is a variable, so extraction tools cannot find this string.
echo esc_html__( 'Read more', $this->domain );

// Good: literal string, literal domain, escaped for context.
echo esc_html__( 'Read more', 'acme-events' );
```

The domain must be a literal because `wp i18n make-pot` parses source code statically. A
variable, constant, or concatenation produces a string that never reaches the `.pot` file and
therefore can never be translated.

---

## Choosing the Function

| Function | Behavior |
|---|---|
| `__()` | Returns the translation |
| `_e()` | Echoes it (unescaped — prefer the `esc_*` variants) |
| `esc_html__()` / `esc_html_e()` | Translate, then escape for HTML |
| `esc_attr__()` / `esc_attr_e()` | Translate, then escape for an attribute |
| `_n()` | Singular/plural by count |
| `_x()` | Translation with disambiguating context |
| `_nx()` | Plural with context |
| `_n_noop()` | Plural registered now, resolved later |

The rule: choose by **output context**, not by preference. A string going into an attribute
needs `esc_attr__()` even if it looks like plain text.

```php
printf(
	'<a href="%s" title="%s">%s</a>',
	esc_url( get_permalink() ),
	esc_attr__( 'Read the full article', 'acme-events' ),
	esc_html__( 'Read more', 'acme-events' )
);
```

---

## Placeholders

Never build a sentence by concatenation — word order differs between languages.

```php
// Bad: untranslatable in any language whose grammar reorders this.
echo esc_html__( 'Showing ', 'acme-events' ) . $count . esc_html__( ' events', 'acme-events' );

// Good: one string, with a placeholder.
printf(
	/* translators: %d: number of events. */
	esc_html__( 'Showing %d events', 'acme-events' ),
	(int) $count
);
```

With more than one placeholder, use **numbered** placeholders so translators can reorder them:

```php
printf(
	/* translators: 1: event title, 2: formatted date. */
	esc_html__( '%1$s starts on %2$s', 'acme-events' ),
	esc_html( $title ),
	esc_html( $date )
);
```

The `/* translators: */` comment must sit immediately above the call. It is the only context a
translator gets, and `%s` alone tells them nothing.

---

## Plurals

```php
printf(
	/* translators: %d: number of seats remaining. */
	esc_html( _n( '%d seat left', '%d seats left', $seats, 'acme-events' ) ),
	(int) $seats
);
```

`_n()` takes the count so the correct form is selected — and languages with three or more
plural forms are handled by the translation file, not by your code. An `if ( $n === 1 )`
branch around two `__()` calls is wrong for Russian, Polish, and Arabic, among others.

---

## Context

The same English word often needs different translations:

```php
_x( 'Post', 'noun: a blog post', 'acme-events' );
_x( 'Post', 'verb: to publish', 'acme-events' );
```

Without `_x()`, both share one entry in the translation file and one language ends up wrong.

---

## Loading the Text Domain

```php
// Theme
add_action( 'after_setup_theme', function () {
	load_theme_textdomain( 'acme', get_stylesheet_directory() . '/languages' );
} );

// Plugin distributed outside wordpress.org
add_action( 'init', function () {
	load_plugin_textdomain( 'acme-events', false, dirname( plugin_basename( ACME_EVENTS_FILE ) ) . '/languages' );
} );
```

Plugins hosted on wordpress.org do not need `load_plugin_textdomain()` — translations come
from translate.wordpress.org and load automatically.

**Timing matters.** Since WordPress 6.7, calling a translation function before the `init` hook
triggers a `_doing_it_wrong()` notice about `_load_textdomain_just_in_time`. In practice:
never translate at file scope or in a constructor that runs during plugin load. Translate
inside the callback that renders or returns the string.

```php
// Bad: runs while the plugin file loads, before translations are available.
const ACME_LABEL = __( 'Events', 'acme-events' );   // also invalid PHP for a const

class Acme_Admin {
	private $label;
	public function __construct() {
		$this->label = __( 'Events', 'acme-events' );   // too early if constructed on load
	}
}

// Good: translate at the point of use.
class Acme_Admin {
	public function label(): string {
		return __( 'Events', 'acme-events' );
	}
}
```

---

## JavaScript

```php
wp_enqueue_script( 'acme-app', $uri . '/assets/js/app.js', array( 'wp-i18n' ), $ver, true );

// Tells WordPress where to find the JSON translation files for this handle.
wp_set_script_translations( 'acme-app', 'acme-events', ACME_EVENTS_PATH . 'languages' );
```

```js
import { __, _n, sprintf } from '@wordpress/i18n';

const label = __( 'Add event', 'acme-events' );

const message = sprintf(
	/* translators: %d: number of events. */
	_n( '%d event selected', '%d events selected', count, 'acme-events' ),
	count
);
```

JavaScript translations need a JSON file per script handle, generated from the `.po`:

```bash
wp i18n make-json languages/ --no-purge
```

Skipping this step is why JS strings often remain untranslated on a site where PHP strings
work fine.

---

## Generating the Template

```bash
# Scan the codebase and produce languages/acme-events.pot
wp i18n make-pot . languages/acme-events.pot --domain=acme-events

# Compile .po → .mo after translating
wp i18n make-mo languages/
```

Run `make-pot` in CI and fail the build when the `.pot` changes without being committed —
that catches strings added without translation functions, which is the failure this whole
document exists to prevent.

---

## Dates, Numbers, and RTL

```php
// Localized date in the site's timezone — the correct default.
echo esc_html( wp_date( get_option( 'date_format' ), $timestamp ) );

// number_format_i18n respects the locale's separators.
echo esc_html( number_format_i18n( $count ) );
```

Avoid `date()` (server timezone, English) and `date_i18n()` (superseded by `wp_date()`).

For right-to-left languages, WordPress loads `style-rtl.css` automatically when present:

```bash
npx rtlcss assets/css/style.css assets/css/style-rtl.css
```

Layouts should use logical CSS properties (`margin-inline-start`, `padding-inline-end`) so
most of the RTL work disappears.

---

## Examples

**Good Example** — literal strings, literal domain, escaped for the output context

```php
add_action( 'init', 'myplugin_load_textdomain' );

function myplugin_load_textdomain() {
	// Not needed for plugins hosted on WordPress.org since 4.6, but required for
	// plugins distributed elsewhere.
	load_plugin_textdomain( 'myplugin', false, dirname( plugin_basename( __FILE__ ) ) . '/languages' );
}

function myplugin_render_seat_notice( int $event_id ): string {
	$remaining = myplugin_seats_remaining( $event_id );

	return sprintf(
		/* translators: %s: number of seats still available. */
		esc_html(
			_n( '%s seat left.', '%s seats left.', $remaining, 'myplugin' )
		),
		esc_html( number_format_i18n( $remaining ) )
	);
}
```

```php
// Attribute context needs esc_attr, and the string still carries a translator note.
printf(
	'<button aria-label="%s">%s</button>',
	esc_attr(
		sprintf(
			/* translators: %s: event title. */
			__( 'Register for %s', 'myplugin' ),
			get_the_title( $event_id )
		)
	),
	esc_html__( 'Register', 'myplugin' )
);
```

**Bad Example** — concatenation, a variable domain, and translation at load time

```php
// The text domain is a variable, so the string extractor cannot find this string
// and it never appears in the .pot file.
$domain = 'myplugin';
echo __( 'Register', $domain );

// Concatenation splits one sentence into fragments. Any language that reorders the
// clause is untranslatable, and the number cannot be pluralized.
echo __( 'There are ', 'myplugin' ) . $remaining . __( ' seats left.', 'myplugin' );

// Runs while the plugin file loads, before the text domain is available, so it
// returns the untranslated original and caches it in a constant forever.
define( 'MYPLUGIN_LABEL', __( 'Events', 'myplugin' ) );

// Unescaped: a translation is untrusted input like any other.
echo __( 'Register for the event', 'myplugin' );
```

---

## Common Mistakes

- **Hardcoded strings** in templates, admin notices, and error messages.
- **A variable or constant as the text domain**, making the string invisible to extraction.
- **A domain that does not match the plugin or theme slug.**
- **Concatenation instead of placeholders.**
- **Unnumbered placeholders** in multi-placeholder strings, so translators cannot reorder.
- **Missing `/* translators: */` comments** on strings with placeholders.
- **`if ( $count === 1 )`** instead of `_n()`.
- **Translating before `init`**, triggering the 6.7 just-in-time notice.
- **Escaping before translating** (`__( esc_html( … ) )`), which escapes the source string
  rather than the translated one.
- **JS translations without `wp_set_script_translations()` and JSON files.**
- **`date()` instead of `wp_date()`**, producing English dates in the server's timezone.

---

## Verification Checklist

- Is every user-facing string wrapped, with a literal domain matching the slug?
- Is the escaping variant correct for the output context?
- Do all dynamic values use numbered placeholders with translator comments?
- Are plurals handled by `_n()`, and ambiguous terms by `_x()`?
- Is the text domain loaded at the right time, with no translation before `init`?
- Are JS strings covered by `wp_set_script_translations()` and generated JSON?
- Do dates and numbers use `wp_date()` and `number_format_i18n()`?
- Is a `.pot` file generated and kept current in CI?

---

## Summary

Wrap every user-facing string with a literal text domain, escape for the output context, use
numbered placeholders with translator comments, delegate plurals to `_n()`, and translate at
the point of use rather than at load time.

## Related

- `knowledge/wordpress/14-theme-development.md`
- `knowledge/wordpress/15-plugin-development.md`
- `knowledge/wordpress/16-block-editor.md`
- `knowledge/wordpress/04-code-style.md`
- `knowledge/wordpress/26-wp-cli.md`
