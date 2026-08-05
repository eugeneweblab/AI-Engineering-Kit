---
id: divi/03-modules
topic: divi
slug: modules
title: "Divi Modules"
type: doc
order: 3
status: ready
tags: [divi, modules, module]
related: [divi/01-architecture, divi/04-custom-modules, divi/09-custom-css, divi/11-responsive-design, divi/10-performance]
when_to_use: "Read before adding or configuring built-in Divi modules on a page."
---
# Divi Modules

## Purpose

This document covers Divi's **built-in modules** — the leaf content units (Text, Image,
Blurb, Slider, Call To Action, Contact Form, and dozens more) that you place inside columns.
It explains how to configure them consistently and reuse styling so a site stays fast and
maintainable. For building your own module, see [custom-modules](04-custom-modules.md).

## Why It Matters

Modules are where 90% of Divi work happens, and where most Divi bloat is created. Every
module exposes hundreds of settings across Content, Design, and Advanced tabs. Configuring
each module by hand, with its own custom CSS and one-off spacing, produces pages that are
impossible to keep consistent and that ship redundant CSS. Disciplined module use — presets,
global defaults, the right module for the job — is what keeps a Divi site professional.

## Core Principles

- **Pick the semantically correct module.** Use the Blurb for icon+heading+text, the CTA for
  a call to action, the Contact Form for forms. The right module gives correct markup and
  accessibility for free; faking it with stacked Text modules does not.
- **Every module has three tabs: Content, Design, Advanced.** Content = data, Design =
  styling, Advanced = custom CSS/IDs/visibility/conditions. Keep concerns in the right tab.
- **Presets are the reuse unit.** A module preset captures Design settings so every instance
  of that module inherits one look; edit the preset and all instances update.
- **Responsive is per-setting.** Most settings can differ per breakpoint (desktop/tablet/
  phone). Set them intentionally rather than leaving desktop values to reflow badly.
- **Custom CSS is a last resort.** Prefer built-in Design controls; reach for the Advanced
  tab's custom CSS only when a control does not exist. See [custom-css](09-custom-css.md).

## Best Practices

- Define module **presets** early (e.g. a "Primary Button" preset) and apply them, instead of
  restyling each button. One edit then updates the whole site.
- Set global default styling for common modules so new instances start on-brand.
- Configure the tablet and phone breakpoints for any module with large text, wide spacing, or
  multi-column internals. See [responsive-design](11-responsive-design.md).
- Use the Advanced tab for accessibility: give interactive modules meaningful link text and
  ARIA-relevant settings; do not rely on color alone. See [accessibility](12-accessibility.md).
- Delete unused modules rather than hiding them; hidden modules still load assets.

## Examples

**Good Example** — reuse via a preset, responsive-aware

```text
Button module → apply preset "Primary Button"
  (preset holds: background, padding, font, hover — defined once, shared everywhere)
Content tab:  Button Text = "Get a Quote", Link = /contact
Design tab:   inherits preset; only breakpoint override = smaller font on phone
// Restyling all primary buttons later = edit the preset once.
```

**Bad Example** — one-off styling duplicated per instance

```text
Button module (no preset)
Design tab:  background #1a73e8, padding 16px 32px, radius 6px, font Poppins 18px
// Next button: retype every value by hand. 40 buttons = 40 places to update,
// 40 blocks of near-identical generated CSS shipped to the browser.
```

## Common Mistakes

- Stacking generic Text/Image modules to imitate a Blurb or CTA, losing correct markup and
  accessibility.
- Styling each module instance individually instead of using presets, causing visual drift
  and CSS bloat.
- Ignoring tablet/phone breakpoints, so desktop spacing and font sizes break on mobile.
- Putting layout hacks in per-module custom CSS when a Design control already exists.
- Leaving disabled/hidden modules on the page, which still enqueue their assets.

## Production Tips

- Audit a page's module count; dozens of modules per row usually signals a design that should
  be simplified or componentized into a reusable layout.
- Standardize presets in a starter template so every new site begins consistent.
- When performance matters, prefer a few well-configured modules over many nested ones — each
  module adds DOM and generated CSS. See [performance](10-performance.md).

## AI Review Checklist

- Is the semantically correct module used for each content type (Blurb, CTA, Form, etc.)?
- Are presets used for repeated elements instead of per-instance styling?
- Are tablet and phone breakpoints configured for spacing- and text-heavy modules?
- Is custom CSS avoided where a built-in Design control exists?
- Are unused or hidden modules removed rather than left loading assets?

## Related

- `knowledge/divi/01-architecture.md`
- `knowledge/divi/04-custom-modules.md`
- `knowledge/divi/09-custom-css.md`
- `knowledge/divi/11-responsive-design.md`
- `knowledge/divi/10-performance.md`
