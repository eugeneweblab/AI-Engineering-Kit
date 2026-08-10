---
id: divi/99-ai-review-checklist
topic: divi
slug: ai-review-checklist
title: "Divi AI Review Checklist"
type: checklist
order: 99
status: ready
tags: [divi, ai-review-checklist, wp_kses, post_content, esc_url, esc_attr, esc_html, merged, agent, another]
related: [divi/29-review, divi/24-best-practices, divi/30-engineering-principles, divi/04-custom-modules, divi/09-custom-css]
when_to_use: "Read when reviewing Divi work — your own or another agent's — before it is committed, merged, or handed off."
---
# Divi AI Review Checklist

## Purpose

This is the review gate an agent runs over Divi work before it is committed or handed off.
Where the [production-checklist](98-production-checklist.md) confirms a whole site is
ready to launch, this checklist reviews a *change* — a new module, a CSS edit, a template,
a PHP hook — for correctness and Divi-specific hazards. Each item is a yes/no an agent can
answer by inspecting the diff, the child theme, or the rendered page.

Use it as the last step of any Divi task. It encodes the failure modes from
[engineering-principles](30-engineering-principles.md) and [best-practices](24-best-practices.md)
as checkable questions.

## Why It Matters

Divi mistakes are quiet. Editing the parent theme, corrupting shortcode/JSON structure, or
leaking user input all pass a casual glance and break later — after an update, a hand-off,
or an attack. A structured review is how you catch them while they are cheap to fix,
instead of after they are live.

## Model & Structure

**Rules:** [Architecture](01-architecture.md) · [Layouts](05-layouts.md)

- [ ] Is the Divi version (4 shortcode vs 5 JSON) correct for the change, with the right
      content format and module API used?
- [ ] Is content edited through the builder model, not by hand-writing shortcodes/JSON or
      touching raw `post_content`?
- [ ] Is every layout a valid section → row → column → module tree with no broken nesting?
- [ ] Are reusable elements defined once (Theme Builder template, global module, preset)
      rather than duplicated?

## Styling

**Rules:** [Custom CSS](09-custom-css.md) · [Global Elements](06-global-elements.md)

- [ ] Are repeated styles driven by presets/globals instead of per-module inline CSS?
- [ ] Is custom CSS in the child theme or Divi's global Custom CSS box — not scattered
      across module Advanced tabs? See [custom-css](09-custom-css.md).
- [ ] Are `!important` overrides justified, not used to paper over specificity problems?
- [ ] Do styles use global colors/fonts/spacing tokens rather than hard-coded values?

## Code (Child Theme, PHP, JS)

**Rules:** [Custom Modules](04-custom-modules.md) · [WordPress Hooks](16-wordpress-hooks.md)

- [ ] Is all PHP/CSS/JS in a **child theme**, never the Divi parent?
- [ ] Are scripts/styles registered via `wp_enqueue_*` with declared dependencies — not
      pasted into a Code module? See [wordpress-hooks](16-wordpress-hooks.md).
- [ ] In custom modules, is user/dynamic input **sanitized on input and escaped on
      output** (`esc_html`, `esc_attr`, `esc_url`, `wp_kses`)? See
      [custom-modules](04-custom-modules.md).
- [ ] Are hooks/filters used instead of editing core or parent files, and removed cleanly
      if temporary?
- [ ] Are database and external calls avoided in render-hot paths, or cached?

## Performance & Accessibility

**Rules:** [Performance](10-performance.md) · [Accessibility](12-accessibility.md)

- [ ] Does the change avoid adding a plugin or font for something Divi already provides?
- [ ] Are new images sized, compressed, and lazy-loaded (except the LCP image)?
- [ ] Does the change preserve semantic headings, `alt` text, contrast, and keyboard focus?
      See [accessibility](12-accessibility.md).

## Verification

**Rules:** [Testing](21-testing.md) · [Debugging](20-debugging.md)

- [ ] Was the change confirmed on the **rendered front end**, not only in the Visual
      Builder, at every breakpoint?
- [ ] Was it tested on staging before production, given Divi updates can shift markup?
- [ ] Are Theme Builder templates and layouts exportable/committed so the change is
      reproducible? See [deployment](22-deployment.md).

## AI Review Checklist

- Have all items above been answered, with any "no" either fixed or explicitly justified?
- Are the two highest-impact hazards — parent-theme edits and unescaped output — both
  confirmed absent?
- Is the change reproducible from version control and verified on the front end?

## Related

- `knowledge/divi/29-review.md`
- `knowledge/divi/24-best-practices.md`
- `knowledge/divi/30-engineering-principles.md`
- `knowledge/divi/04-custom-modules.md`
- `knowledge/divi/09-custom-css.md`
