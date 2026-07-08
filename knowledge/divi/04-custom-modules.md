---
id: divi/04-custom-modules
topic: divi
slug: custom-modules
title: "Custom Modules"
type: doc
order: 4
status: ready
tags: [divi, custom-modules]
related: [divi/03-modules, divi/01-architecture, divi/16-wordpress-hooks, divi/19-security, divi/10-performance]
when_to_use: "Read before writing a custom Divi module in PHP/React when no built-in module fits."
---
# Custom Modules

## Purpose

This document covers building a **custom Divi module** — your own module that appears in the
builder with its own settings and render output. Build one only when no built-in
[module](03-modules.md) and no combination of them can express the requirement. A custom
module is real code and carries real security and maintenance responsibility.

## Why It Matters

Custom modules are the correct way to add bespoke functionality, but they run inside the
builder and on every page that uses them. A module that echoes user input without escaping
opens an XSS hole; one that queries the database on render without caching slows every page.
Because a module is authored once and reused everywhere, its bugs multiply. Custom modules
must meet the same bar as plugin code, not "theme tweak" code.

## Core Principles

- **Package it as a plugin (or child-theme include), never in the parent theme.** Register the
  module on Divi's initialization hook so it survives theme updates.
- **Version awareness is mandatory.** Divi 4 uses the PHP `ET_Builder_Module` class API
  (`get_fields()` + `render()`). Divi 5 introduces a new React/PHP module API with separated
  content and style layers. Target the version the site runs; do not assume one works on the
  other.
- **Declare fields; do not hand-parse attributes.** `get_fields()` (Divi 4) defines the
  settings UI and sanitization. Divi generates the builder controls from it.
- **Escape on output, sanitize on input.** Every dynamic value in `render()` must be escaped
  with the correct WordPress function. See [security](19-security.md).
- **Render must be cheap and idempotent.** It runs on the front end and in the builder. Keep
  queries cached and side-effect free.

## Best Practices

- Register on `et_builder_ready` so the module class loads only when Divi is active.
- Give the module a unique `slug` prefixed to your project (e.g. `acme_pricing`) to avoid
  collisions with Divi and other plugins.
- Escape output by type: `esc_html()` for text, `esc_url()` for links, `esc_attr()` for
  attributes, `wp_kses_post()` for rich text. Never `echo` raw props.
- Whitelist and sanitize any field that becomes HTML; never trust builder input as safe.
- Cache expensive work (queries, remote calls) with transients; a module renders on every
  page load. See [performance](10-performance.md).
- Enqueue module CSS/JS conditionally, only when the module is present, not globally.

## Examples

**Good Example** — declared fields, escaped output (Divi 4 API)

```php
class ACME_Pricing_Module extends ET_Builder_Module {
    public $slug       = 'acme_pricing';
    public $vb_support = 'on';

    public function init() {
        $this->name = esc_html__( 'ACME Pricing', 'acme' );
    }

    public function get_fields() {
        return array(
            'plan_name' => array(
                'label'   => esc_html__( 'Plan Name', 'acme' ),
                'type'    => 'text',                 // Divi builds + sanitizes the control
                'toggle_slug' => 'main_content',
            ),
            'plan_url' => array(
                'label' => esc_html__( 'Sign-up URL', 'acme' ),
                'type'  => 'text',
            ),
        );
    }

    public function render( $attrs, $content, $render_slug ) {
        // Escape every dynamic value by its output context.
        $name = esc_html( $this->props['plan_name'] );
        $url  = esc_url( $this->props['plan_url'] );
        return sprintf(
            '<div class="acme-pricing"><h3>%s</h3><a href="%s">Choose</a></div>',
            $name, $url
        );
    }
}
new ACME_Pricing_Module(); // registered on et_builder_ready
```

**Bad Example** — raw echo, no escaping, uncached query

```php
public function render( $attrs, $content, $render_slug ) {
    // XSS: plan_name is echoed unescaped straight from builder input.
    echo '<h3>' . $this->props['plan_name'] . '</h3>';
    // Runs an uncached query on EVERY page render — slow and repeated.
    $rows = $GLOBALS['wpdb']->get_results( "SELECT * FROM wp_acme_plans" );
    foreach ( $rows as $r ) {
        echo '<a href=' . $r->url . '>' . $r->title . '</a>'; // unquoted, unescaped
    }
}
```

## Common Mistakes

- Echoing `$this->props` values without escaping, creating stored XSS in the builder.
- Writing the module into the parent theme, so a Divi update deletes it.
- Reusing a slug that collides with Divi core or another module.
- Running database or remote calls in `render()` with no caching, slowing every page.
- Targeting the Divi 4 API on a Divi 5 site (or vice versa) and getting a module that does not
  load in the Visual Builder.

## Production Tips

- Set `vb_support = 'on'` and test the module renders correctly inside the Visual Builder, not
  just on the front end — builder rendering is a separate code path.
- Enqueue assets on `wp_enqueue_scripts` guarded by whether the module is on the page.
- Add the module to your CI: PHP lint, and a smoke test that the builder loads with the module
  active. See [testing](21-testing.md).

## AI Review Checklist

- Is the module packaged in a plugin or child theme, never the parent theme?
- Does it target the correct module API for the site's Divi version?
- Is every dynamic value in `render()` escaped with the context-correct function?
- Are expensive queries/remote calls cached rather than run on every render?
- Is the slug uniquely prefixed to avoid collisions?
- Does the module render correctly inside the Visual Builder, not only the front end?

## Related

- `knowledge/divi/03-modules.md`
- `knowledge/divi/01-architecture.md`
- `knowledge/divi/16-wordpress-hooks.md`
- `knowledge/divi/19-security.md`
- `knowledge/divi/10-performance.md`
