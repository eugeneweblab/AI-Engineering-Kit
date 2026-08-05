---
id: divi/20-debugging
topic: divi
slug: debugging
title: "Divi Debugging"
type: doc
order: 20
status: ready
tags: [divi, debugging]
related: [divi/09-custom-css, divi/04-custom-modules, divi/10-performance, divi/21-testing, divi/19-security]
when_to_use: "Read when the Visual Builder fails to load, styles don't apply, or custom code misbehaves."
---
# Divi Debugging

## Purpose

This document defines a disciplined method for diagnosing Divi problems: a Visual Builder
that will not load, styles that do not apply, broken layouts, and misbehaving
[custom modules](04-custom-modules.md) or hooks. It gives an agent an ordered process so it
isolates the real cause instead of guessing.

## Why It Matters

Divi failures are usually **integration failures**, not Divi bugs: a PHP error in a child
theme, a JavaScript conflict from another plugin, or a stale static-CSS cache. The symptom
(a blank Visual Builder, an unstyled front-end) rarely names the cause, and editing
shortcodes blindly to "fix" it corrupts the content model. A repeatable isolation process —
enable logging, reproduce, bisect plugins, clear caches — turns a vague "Divi is broken"
into a specific, fixable line of code.

## Core Principles

- **Read the actual error before changing anything.** Enable `WP_DEBUG` + `WP_DEBUG_LOG`
  and open the browser console. A blank builder almost always logged a PHP fatal or a JS
  exception that names the file.
- **Bisect to isolate.** Use Divi's **Safe Mode** (Support Center) to disable third-party
  plugins/custom code in one click; if the problem vanishes, re-enable one at a time.
- **Suspect the cache before the code.** Stale static CSS or a page cache produces
  "my change didn't apply" and unstyled pages. Clear Divi's cache and regenerate static
  CSS before deeper debugging. See [performance](10-performance.md).
- **Never hand-edit shortcodes to fix rendering.** A malformed attribute is a common cause;
  fix it in the builder or by restoring a revision, not by guessing at raw shortcode text.

## Best Practices

- Turn on debugging in `wp-config.php`: `WP_DEBUG`, `WP_DEBUG_LOG` (write to a file), and
  `WP_DEBUG_DISPLAY = false` so errors go to the log, not to visitors.
- Use Divi **Support Center → Safe Mode** to rule out plugin/theme conflicts and to
  temporarily disable custom CSS/JS.
- Install **Query Monitor** to see PHP notices, slow queries, hook timing, and REST calls
  behind a failing page.
- After any CSS or theme change, **clear Divi's cache** (Divi → Theme Options → Builder →
  Advanced → *Static CSS File Generation* toggle/clear) so you test fresh output.
- Reproduce with the default theme / no plugins to confirm whether the bug is Divi-specific
  before filing or fixing.
- Check the console for JS errors when the builder hangs — a single third-party script that
  throws will stop React from mounting the builder.

## Examples

**Good Example** — capture the error, then bisect

```php
// wp-config.php — log errors instead of guessing at a blank screen
define( 'WP_DEBUG', true );
define( 'WP_DEBUG_LOG', true );      // -> wp-content/debug.log
define( 'WP_DEBUG_DISPLAY', false ); // never show errors to visitors
```

```
# Process, in order:
# 1. Reproduce, then tail the log for the fatal line.
tail -f wp-content/debug.log
# 2. If nothing in PHP, open DevTools console for a JS exception.
# 3. Still unclear? Divi Support Center -> Safe Mode (disables plugins/custom code).
# 4. Problem gone in Safe Mode? Re-enable plugins one-by-one to find the conflict.
# 5. Style change not applying? Clear Divi cache + regenerate static CSS, retest.
```

**Bad Example** — guessing and corrupting content

```php
// WRONG: "the builder is blank, maybe this shortcode is off" — hand-edited in the DB
$content = str_replace( 'et_pb_section', 'et_pb_section fb_built="1"', $post_content );
// Silences nothing, corrupts the serialized layout, and hides the real PHP fatal
// that WP_DEBUG_LOG would have named in one line.
```

## Common Mistakes

- Debugging with caching on, so you keep testing stale static CSS and "nothing changes".
- Editing raw shortcodes/JSON in the database to fix a render instead of finding the cause.
- Ignoring the browser console when the Visual Builder hangs (usually a JS conflict).
- Leaving `WP_DEBUG_DISPLAY` on in production, leaking paths and errors to visitors.
- Changing many things at once, so you cannot tell which change fixed or broke it.
- Blaming Divi before ruling out plugin conflicts via Safe Mode.

## Production Tips

- Never enable `WP_DEBUG_DISPLAY` on production; log to a file and inspect it out of band.
- Reproduce and fix on staging with a copy of production data — see [testing](21-testing.md).
- Keep post revisions enabled so a corrupted layout can be rolled back to a known-good state.

## AI Review Checklist

- Was the actual PHP/JS error captured (log + console) before any code changed?
- Was caching/static CSS cleared before concluding a change "didn't work"?
- Was a plugin/theme conflict ruled out with Safe Mode?
- Is `WP_DEBUG_DISPLAY` off (log only) so errors never reach visitors?
- Was the fix made in the builder/child theme, not by hand-editing serialized content?
- Was only one variable changed at a time while isolating the cause?

## Related

- `knowledge/divi/09-custom-css.md`
- `knowledge/divi/04-custom-modules.md`
- `knowledge/divi/10-performance.md`
- `knowledge/divi/21-testing.md`
- `knowledge/divi/19-security.md`
