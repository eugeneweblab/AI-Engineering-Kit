---
id: wordpress/17-block-themes
topic: wordpress
slug: block-themes
title: "Block Themes and theme.json"
type: doc
order: 17
status: ready
tags: [wordpress, block-themes, theme.json, rendered, style.css, index.html]
applies_to: [block-theme]
related: [wordpress/14-theme-development, wordpress/16-block-editor, wordpress/13-template-hierarchy, wordpress/05-performance, wordpress/24-internationalization]
when_to_use: "Read before building a block theme or writing theme.json — defining presets, styling blocks globally, or creating HTML templates and parts."
---
# Block Themes and theme.json

## Purpose

This document defines how block themes work: the role of `theme.json`, how presets become CSS
custom properties, how HTML templates replace PHP ones, and where the database copy of a
template overrides the file you deployed.

A block theme moves styling from a stylesheet into structured configuration. That trade is
worth understanding before committing: it buys editor integration and consistency, and it
costs direct control over the generated CSS.

---

## Core Principle

`theme.json` is the design system, and it flows in one direction: **settings** define what is
available in the editor; **styles** define what is applied by default.

```
theme.json
  ├── settings  → what the editor offers (palette, font sizes, spacing scale, toggles)
  └── styles    → what is rendered (defaults for the root and for individual blocks)
```

A value defined in `settings` becomes a CSS custom property automatically. Hardcoding the same
value in a stylesheet duplicates it and guarantees they will diverge.

---

## Minimal Theme Structure

```
acme-theme/
├── style.css          header only — theme metadata
├── theme.json         the design system
├── templates/
│   ├── index.html     required
│   ├── single.html
│   ├── archive.html
│   ├── page.html
│   └── 404.html
├── parts/
│   ├── header.html
│   └── footer.html
├── patterns/
│   └── hero.php
└── functions.php      optional: asset enqueuing, supports not covered by theme.json
```

The template hierarchy from [Template Hierarchy](13-template-hierarchy.md) still applies —
`single-acme_event.html` beats `single.html` — but the files are HTML containing block markup
instead of PHP.

---

## `theme.json` Essentials

```json
{
  "$schema": "https://schemas.wp.org/trunk/theme.json",
  "version": 3,
  "settings": {
    "appearanceTools": true,

    "color": {
      "defaultPalette": false,
      "custom": false,
      "palette": [
        { "slug": "base",    "color": "#FFFFFF", "name": "Base" },
        { "slug": "contrast","color": "#111827", "name": "Contrast" },
        { "slug": "primary", "color": "#2563EB", "name": "Primary" }
      ]
    },

    "typography": {
      "customFontSize": false,
      "fluid": true,
      "fontSizes": [
        { "slug": "small",  "size": "0.875rem", "name": "Small" },
        { "slug": "medium", "size": "1rem",     "name": "Medium" },
        { "slug": "large",  "size": "1.5rem",   "name": "Large" }
      ]
    },

    "spacing": {
      "units": [ "rem", "%", "vh" ],
      "spacingSizes": [
        { "slug": "30", "size": "1rem",   "name": "Small" },
        { "slug": "50", "size": "2rem",   "name": "Medium" },
        { "slug": "70", "size": "4rem",   "name": "Large" }
      ]
    },

    "layout": { "contentSize": "40rem", "wideSize": "72rem" }
  },

  "styles": {
    "color": { "background": "var(--wp--preset--color--base)", "text": "var(--wp--preset--color--contrast)" },
    "typography": { "lineHeight": "1.6" },
    "blocks": {
      "core/button": {
        "color": { "background": "var(--wp--preset--color--primary)", "text": "var(--wp--preset--color--base)" },
        "border": { "radius": "0.5rem" }
      }
    },
    "elements": {
      "link": { "color": { "text": "var(--wp--preset--color--primary)" } }
    }
  }
}
```

Three settings are worth calling out because they decide whether the design system holds:

- **`defaultPalette: false`** removes core's colors. Leaving them on means editors can pick
  from a palette the design never approved.
- **`custom: false`** removes the arbitrary color picker. Same argument, stronger effect.
- **`appearanceTools: true`** enables border, spacing, and typography controls in one flag
  instead of a dozen individual toggles.

---

## Presets Become CSS Variables

Every preset generates a custom property with a predictable name:

```css
--wp--preset--color--primary
--wp--preset--font-size--large
--wp--preset--spacing--50
```

Reference those instead of literals in any supplementary CSS:

```css
/* Good — one source of truth; changing theme.json changes this too. */
.acme-callout {
	background: var(--wp--preset--color--primary);
	padding: var(--wp--preset--spacing--50);
}

/* Bad — drifts the moment the palette changes. */
.acme-callout {
	background: #2563EB;
	padding: 2rem;
}
```

---

## Templates and Parts

```html
<!-- templates/single.html -->
<!-- wp:template-part {"slug":"header","tagName":"header"} /-->

<!-- wp:group {"tagName":"main","layout":{"type":"constrained"}} -->
<main class="wp-block-group">
	<!-- wp:post-title {"level":1} /-->
	<!-- wp:post-featured-image {"isLink":true} /-->
	<!-- wp:post-content {"layout":{"type":"constrained"}} /-->
</main>
<!-- /wp:group -->

<!-- wp:template-part {"slug":"footer","tagName":"footer"} /-->
```

Register custom templates and part areas in `theme.json` so they appear in the site editor:

```json
{
  "customTemplates": [
    { "name": "page-full-width", "title": "Full Width", "postTypes": [ "page" ] }
  ],
  "templateParts": [
    { "name": "header", "title": "Header", "area": "header" },
    { "name": "footer", "title": "Footer", "area": "footer" }
  ]
}
```

---

## The Database Overrides the File

This is the operational surprise of block themes. When a user edits a template in the site
editor, WordPress saves a copy as a `wp_template` post. From then on, **the database copy
wins** and your deployed file is ignored.

```bash
# What has been customized (and is therefore no longer tracked by your repo)?
wp post list --post_type=wp_template --fields=post_name,post_status
wp post list --post_type=wp_template_part --fields=post_name,post_status
```

Consequences for a real project:

- A deploy that changes `templates/single.html` may have no visible effect.
- "Clear customizations" in the site editor deletes the database copy and restores the file.
- Decide per project whether site-editor changes are allowed at all; if not, restrict the
  `edit_theme_options` capability — see [Users and Capabilities](20-users-and-capabilities.md).

---

## Style Variations

Alternate palettes and type scales live under `styles/` and are selectable in the editor:

```
acme-theme/styles/dark.json
acme-theme/styles/high-contrast.json
```

```json
{
  "$schema": "https://schemas.wp.org/trunk/theme.json",
  "version": 3,
  "title": "Dark",
  "settings": { "color": { "palette": [ { "slug": "base", "color": "#111827", "name": "Base" } ] } }
}
```

A variation is the correct way to ship a dark mode or a campaign look — it reuses the same
templates rather than duplicating them.

---

## Classic Theme or Block Theme

Do not mix the models in one project. A half-migrated theme has styling in `theme.json`, in
`style.css`, and in the database, and no one can predict which wins.

| Choose a block theme when | Choose a classic theme when |
|---|---|
| Editors should control layout | Layout must stay fixed |
| The design maps to core blocks | The design needs bespoke PHP templates |
| A design system is already token-based | Heavy integration with page-builder plugins |

Note that a page builder such as Divi assumes a classic theme — see
[Divi — Architecture](../divi/01-architecture.md).

---

## Examples

**Good Example** — one source of truth, consumed as generated custom properties

```json
{
  "$schema": "https://schemas.wp.org/trunk/theme.json",
  "version": 3,
  "settings": {
    "appearanceTools": true,
    "color": {
      "custom": false,
      "palette": [
        { "slug": "surface", "color": "#ffffff", "name": "Surface" },
        { "slug": "ink", "color": "#111827", "name": "Ink" },
        { "slug": "accent", "color": "#2563eb", "name": "Accent" }
      ]
    },
    "spacing": {
      "spacingScale": { "steps": 7 }
    }
  },
  "styles": {
    "color": { "background": "var(--wp--preset--color--surface)", "text": "var(--wp--preset--color--ink)" },
    "blocks": {
      "core/button": {
        "color": { "background": "var(--wp--preset--color--accent)" },
        "spacing": { "padding": { "top": "var(--wp--preset--spacing--30)" } }
      }
    }
  }
}
```

```css
/* Any additional CSS consumes the same generated variables. */
.acme-event-card {
	background: var(--wp--preset--color--surface);
	color: var(--wp--preset--color--ink);
	padding: var(--wp--preset--spacing--40);
}
```

Changing the accent colour is one edit in `theme.json`; the editor, the front end, and this
stylesheet all follow.

**Bad Example** — the palette declared twice, then forced with `!important`

```css
/* style.css — the same values retyped, now free to drift from theme.json */
:root {
	--brand-blue: #2563EB;
}

.wp-block-button__link {
	background: #2563eb !important;   /* overrides whatever the editor shows */
	padding: 9px 15px !important;     /* off the spacing scale entirely */
}
```

The editor preview and the front end now disagree, and every future override needs another
`!important` to win.

---

## Common Mistakes

- **Hardcoding colors and spacing in CSS** that `theme.json` already defines.
- **Leaving `defaultPalette` and `custom` enabled**, so editors can select off-brand values.
- **Deploying template changes** without realizing the database copy overrides them.
- **Mixing classic and block theme approaches** in one theme.
- **Fighting generated CSS with `!important`** instead of setting the value in `theme.json`.
- **Duplicating templates** for a color change that a style variation handles.
- **Forgetting `index.html`**, which every block theme must provide.
- **Untranslated strings in `patterns/*.php`**, which are PHP and can use translation
  functions — unlike HTML templates, which cannot.

---

## Verification Checklist

- Is every design token defined once, in `theme.json`?
- Does supplementary CSS reference `--wp--preset--*` variables rather than literals?
- Are `defaultPalette` and `custom` set deliberately?
- Are custom templates and part areas registered in `theme.json`?
- Is it understood which templates have database copies, and is that acceptable?
- Are alternate looks style variations rather than duplicated templates?
- Is the theme consistently a block theme, with no classic-theme leftovers?

---

## Summary

`theme.json` is the design system: settings decide what editors may choose, styles decide the
defaults, and presets become CSS variables you should reference everywhere. Templates are HTML
following the same hierarchy — and once a user edits one, the database copy, not your file, is
what renders.

## Related

- `knowledge/wordpress/14-theme-development.md`
- `knowledge/wordpress/16-block-editor.md`
- `knowledge/wordpress/13-template-hierarchy.md`
- `knowledge/wordpress/05-performance.md`
- `knowledge/wordpress/24-internationalization.md`
