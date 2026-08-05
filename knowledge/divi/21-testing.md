---
id: divi/21-testing
topic: divi
slug: testing
title: "Divi Testing"
type: doc
order: 21
status: ready
tags: [divi, testing]
related: [divi/20-debugging, divi/04-custom-modules, divi/11-responsive-design, divi/12-accessibility, divi/22-deployment]
when_to_use: "Read before shipping a Divi change, custom module, or theme update to verify nothing regressed."
---
# Divi Testing

## Purpose

This document defines how to verify a Divi site before it ships: confirming the Visual
Builder still loads, that layouts render correctly across breakpoints, that
[custom modules](04-custom-modules.md) and hooks behave, and that a Divi/plugin update did
not break anything. It tells an agent what to test and how, so "it looked fine on my page"
is replaced by a repeatable check.

## Why It Matters

Divi's output is emergent: content lives in shortcodes/JSON, styling comes from global
presets, the Theme Builder, and static CSS, and a single update can shift markup site-wide.
There is no compiler to catch a broken layout, so untested changes reach visitors as
collapsed sections, unstyled pages, or a builder that will not open. Because so much
behavior is visual and cross-cutting, testing must combine automated code tests for custom
PHP with visual and functional checks of the rendered site.

## Core Principles

- **Test on staging, never in production.** Divi and plugin updates must be validated on a
  clone with real content before they touch the live site. See [deployment](22-deployment.md).
- **Custom PHP gets automated tests.** Custom modules, shortcodes, and hooks are code —
  cover them with PHPUnit (WordPress test suite), not just a glance in the builder.
- **The rendered site gets functional + visual tests.** Automate "does the page load,
  does the builder open, does the form submit" with Playwright/Cypress against the front-end.
- **Verify the two states that matter: front-end and Visual Builder.** A change can render
  fine for visitors yet break the builder (or vice versa). Check both.

## Best Practices

- After any Divi/theme/plugin update on staging: open key pages on the front-end **and**
  open each key page in the Visual Builder to confirm it still loads and saves.
- Write PHPUnit tests for custom module output and hook logic using the WP test harness;
  assert on the rendered HTML and on capability/nonce behavior (see [security](19-security.md)).
- Add end-to-end tests (Playwright) for critical flows: navigation, contact/WooCommerce
  forms, and that no console errors appear on load.
- Test [responsive](11-responsive-design.md) breakpoints (desktop/tablet/phone) and run an
  [accessibility](12-accessibility.md) check (axe) on templated pages, not just one page.
- Regenerate static CSS on staging and test the *cached* output, since that is what
  production serves.
- Seed staging with a production data copy so tests exercise real layouts, not a toy page.

## Examples

**Good Example** — automated test for a custom module's output

```php
// tests/test-cta-module.php — WordPress PHPUnit test harness
class CtaModuleTest extends WP_UnitTestCase {
    public function test_renders_escaped_label() {
        // Malicious label must be escaped, not echoed raw (guards against XSS regressions).
        $html = do_shortcode( '[my_cta label="<script>x</script>"]' );

        $this->assertStringContainsString( '&lt;script&gt;', $html ); // escaped
        $this->assertStringNotContainsString( '<script>x</script>', $html );
    }
}
```

**Bad Example** — "tested" by eyeballing one page

```text
Manual "test":
1. Update Divi on the live site.
2. Load the homepage in a browser. Looks fine.
3. Ship.

Why it fails: the homepage is one of 40 templated pages; the Theme Builder header,
the Visual Builder, mobile breakpoints, and the checkout flow were never opened.
A markup change from the update silently broke them for every visitor.
```

## Common Mistakes

- Testing only the front-end and never opening the Visual Builder after an update.
- Checking a single page instead of each Theme Builder template and layout type.
- Skipping responsive and accessibility checks because "it looks fine on desktop".
- No automated tests for custom modules/hooks, so refactors regress silently.
- Testing uncached output while production serves stale static CSS.
- Running the update straight on production because "it's just a minor version".

## Production Tips

- Gate deploys on a CI job that runs PHPUnit for custom code and Playwright smoke tests.
- Keep a short manual checklist of "must-open" pages/templates for post-update verification.
- Capture baseline screenshots for visual-regression diffing on key templates.

## AI Review Checklist

- Was the change validated on staging with a production data copy, not on production?
- Do custom modules/hooks have PHPUnit coverage, including escaping and capability checks?
- Are critical front-end flows covered by end-to-end tests with no console errors?
- Was each affected Theme Builder template and layout opened in the Visual Builder?
- Were responsive breakpoints and accessibility checked, not just one desktop page?
- Was cached/static-CSS output tested, matching what production serves?

## Related

- `knowledge/divi/20-debugging.md`
- `knowledge/divi/04-custom-modules.md`
- `knowledge/divi/11-responsive-design.md`
- `knowledge/divi/12-accessibility.md`
- `knowledge/divi/22-deployment.md`
