---
id: tailwind/12-dark-mode
topic: tailwind
slug: dark-mode
title: "Dark Mode"
type: doc
order: 12
status: ready
tags: [tailwind, dark-mode, "dark:", dark, data-theme, color-scheme, prefers-color-scheme, variant]
related: [tailwind/11-responsive-design, tailwind/13-state-variants, tailwind/16-theme, tailwind/10-colors, tailwind/22-accessibility]
when_to_use: "Read before adding a dark theme or a light/dark toggle to a Tailwind UI."
---
# Dark Mode

## Purpose

This document defines how to build dark mode in Tailwind CSS v4: how the `dark:`
variant works, how to switch between following the OS setting and an explicit
user toggle, and how to keep both themes correct without duplicating markup. It
is written so an agent can add a theme without producing a flash of the wrong
colors or a toggle that silently does nothing.

Dark mode is a *variant*, not a separate stylesheet. `dark:bg-slate-900` means
"apply `bg-slate-900` only when dark mode is active." How "active" is decided —
the OS preference or a class you control — is the one configuration decision that
governs everything else.

## Why It Matters

Dark mode is judged instantly: a single element that keeps its light background,
or a white flash on load, reads as broken. The failure modes are systematic, not
cosmetic. Choosing the wrong activation strategy means your toggle does nothing.
Rendering theme decisions in a client effect means every visitor sees a flash of
unstyled/wrong theme (FOUC) before hydration. And forgetting `dark:` on even one
surface leaves an unreadable low-contrast patch. Getting the strategy and the
initial-paint timing right up front avoids all three.

## Core Principles

- **Pick one activation strategy and commit.** Either follow the OS
  (`prefers-color-scheme`, the default) or toggle via a class/attribute you
  control. A user-facing toggle *requires* the class strategy.
- **The theme decision must be made before first paint.** Read the stored
  preference in a blocking inline script in `<head>`, not in a React effect.
  Anything later flashes.
- **Every color utility needs a `dark:` counterpart, or a token that already
  adapts.** A bare `bg-white` with no dark variant is a bug in dark mode.
- **Style light as the base, dark as the override.** `bg-white dark:bg-slate-900`,
  not the reverse. The unprefixed value is the default; `dark:` layers on top.
- **Contrast is per-theme.** A pair that passes WCAG in light mode can fail in
  dark mode. Verify both.

## Best Practices

- For a toggle, register the class variant in CSS (v4 has no JS `darkMode`
  option): `@custom-variant dark (&:where(.dark, .dark *));`. Then add/remove
  `.dark` on `<html>`.
- Prefer a `data-theme` attribute if you support a three-way choice (light / dark
  / system): `@custom-variant dark (&:where([data-theme=dark], [data-theme=dark] *));`.
- Persist the choice in `localStorage` and reconcile with `prefers-color-scheme`
  for the "system" option; update on the OS `change` event.
- Define semantic color tokens (`--color-surface`, `--color-text`) in
  [16-theme](16-theme.md) so most markup never needs `dark:` at all — the token
  swaps, the class stays.
- Set `color-scheme: light dark` (via the `scheme-light-dark` utilities or CSS)
  so native controls, scrollbars, and form widgets match the theme.
- Include `<meta name="theme-color">` updates so mobile browser chrome matches.

## Examples

**Good Example** — class strategy, no-flash init, paired colors

```html
<!-- In <head>, BEFORE the stylesheet: runs synchronously, no flash -->
<script>
  const t = localStorage.theme ??
    (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  document.documentElement.classList.toggle('dark', t === 'dark');
</script>
```

```css
/* app.css — register the class-based variant (v4 CSS-first config) */
@import "tailwindcss";
@custom-variant dark (&:where(.dark, .dark *));
```

```html
<!-- Light is the base; dark: overrides. Both surfaces AND text are paired. -->
<div class="bg-white text-slate-900 dark:bg-slate-900 dark:text-slate-100">
  Readable in both themes.
</div>
```

**Bad Example** — flash on load, half-themed, wrong default direction

```jsx
function App() {
  // BUG: decision runs after hydration → white flash every load (FOUC)
  useEffect(() => {
    if (localStorage.theme === "dark")
      document.documentElement.classList.add("dark");
  }, []);

  return (
    // BUG: bg has a dark variant but text does not → dark-on-dark, unreadable.
    // BUG: dark is written as the base, forcing a light: override everywhere.
    <div className="bg-slate-900 text-slate-900 light:bg-white">…</div>
  );
}
```

## Common Mistakes

- Deciding the theme in a client-side effect, causing a flash of the wrong theme
  on every load.
- Adding `dark:` to backgrounds but not to text, borders, shadows, or icons.
- Expecting a `dark:` toggle to work without registering the `dark` custom
  variant — by default `dark:` follows the OS, so the class does nothing.
- Hardcoding colors (`bg-white`) throughout instead of semantic tokens, so dark
  mode becomes a find-and-replace of hundreds of call sites.
- Assuming a color pair that passes contrast in light mode also passes in dark.
- Forgetting `color-scheme`, leaving native inputs and scrollbars light.

## Production Tips

- Test both themes in CI with a visual-regression tool; toggle `.dark` on the
  root and snapshot key pages.
- Audit contrast per theme with an automated checker (axe, Lighthouse) — run it
  twice, once per theme.
- Expose "system" as an option and listen for OS changes so the UI updates live
  without a reload.

## AI Review Checklist

- Is the theme decided in a blocking `<head>` script before first paint (no FOUC)?
- If there is a toggle, is the `dark` custom variant registered and does the
  toggle mutate `.dark`/`data-theme` on `<html>`?
- Does every color utility have a `dark:` counterpart, or use a token that adapts?
- Is light the base and `dark:` the override (not the reverse)?
- Does contrast pass WCAG in *both* themes?
- Is `color-scheme` set so native controls match?

## Related

- `knowledge/tailwind/11-responsive-design.md`
- `knowledge/tailwind/13-state-variants.md`
- `knowledge/tailwind/16-theme.md`
- `knowledge/tailwind/10-colors.md`
- `knowledge/tailwind/22-accessibility.md`
