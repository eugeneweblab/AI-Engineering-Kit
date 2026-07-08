---
id: divi/09-custom-css
topic: divi
slug: custom-css
title: "Custom CSS"
type: doc
order: 9
status: ready
tags: [divi, custom-css]
related: [divi/10-performance, divi/06-global-elements, divi/11-responsive-design, divi/03-modules, divi/24-best-practices]
when_to_use: "Read before writing any custom CSS in Divi — a module CSS box, the Theme Options field, or a child theme stylesheet."
---
# Custom CSS

## Purpose

This document defines *where* and *how* to write custom CSS in Divi so styling stays
maintainable and does not fight the builder. Divi offers several CSS entry points — the
per-module Custom CSS tab, the Theme Options / Theme Builder CSS field, page-level CSS, and
the child theme stylesheet — each with different scope, specificity, and performance cost.
Choosing the wrong one is the root of most "my CSS won't apply" and "the site is bloated"
problems.

Custom CSS is a last resort, not a first move: Divi's built-in design controls already emit
optimized, per-module CSS. Reach for hand-written CSS only when a control does not exist.

## Why It Matters

Divi generates CSS per unique module configuration and can inline critical CSS. Scattering
hand-written rules across dozens of individual modules multiplies the CSS payload and makes
every rule invisible to global change — the exact bloat Divi is criticized for. Worse, the
per-module CSS box is high-specificity and page-scoped, so a rule you put there works on one
page and mysteriously fails elsewhere, and later overrides require `!important` wars. Deciding
the *right location* for a rule up front is what keeps a Divi site's CSS small, cascadable, and
debuggable. See [performance](10-performance.md).

## Core Principles

- **Prefer built-in design controls to custom CSS.** If Divi has a control for it (spacing,
  border, shadow, filter), use the control — it is responsive-aware and centrally editable.
- **Site-wide rules go in the child theme stylesheet.** Reusable styling belongs in
  `style.css` of a child theme (or the Theme Options CSS field), scoped by a class — one place,
  cascadable, no per-page duplication.
- **Per-module CSS is for genuinely one-off tweaks only.** The module Custom CSS tab is
  high-specificity and local; use it sparingly and never for anything that repeats.
- **Target a stable selector, add your own class.** Give modules a CSS Class in the Advanced tab
  and target that, instead of relying on Divi's generated `.et_pb_*` IDs which change.
- **Avoid `!important` and deep nesting.** They signal you are in the wrong layer. Fix specificity
  by choosing the right location, not by escalating.
- **Never edit the parent theme's CSS.** Updates overwrite it. All CSS lives in a child theme or
  Divi's own fields. See [best-practices](24-best-practices.md).

## Best Practices

- Add a semantic **CSS Class** to modules (Advanced → CSS ID & Classes), e.g. `feature-card`, and
  write rules against `.feature-card` in the child theme — reusable and low-specificity.
- Put anything used on more than one page in the child theme `style.css` (enqueued after the
  parent), not in a module box. Reserve the module box for true one-offs.
- Use Divi's responsive controls or standard media queries; do not hard-code desktop-only pixel
  values that break on mobile. See [responsive-design](11-responsive-design.md).
- Keep selectors shallow and class-based. If you need `!important`, first check whether the rule
  belongs in a lower-specificity location.
- Comment non-obvious rules with the *why*, since the next editor sees CSS with no builder context.
- Consolidate: if the same rule appears in five module boxes, delete them and write it once against
  a shared class.

## Examples

**Good Example** — reusable rule in the child theme, targeting a semantic class

```css
/* child-theme/style.css — one place, cascadable, applies everywhere the class is used */
.feature-card {
  transition: transform 0.2s ease;      /* uses a low-specificity class, no !important */
}
.feature-card:hover {
  transform: translateY(-4px);          /* one definition drives every feature card */
}

@media (max-width: 767px) {
  .feature-card { transition: none; }   /* explicit mobile behaviour, not a desktop-only guess */
}
```

Assign the class once per module (Advanced → CSS Class: `feature-card`). Why: one source of
truth, editable in a single file, no specificity escalation, responsive-aware.

**Bad Example** — the same tweak pasted into many module CSS boxes with `!important`

```css
/* pasted into Module → Custom CSS → Main Element, repeated on 12 modules */
transform: translateY(-4px) !important;   /* !important to beat Divi's generated CSS */
transition: transform 0.2s ease !important;
/* high-specificity, page-scoped, duplicated 12× — a rebrand means editing 12 boxes,
   and the next override needs an even bigger !important hammer */
```

Why this is wrong: twelve duplicated, page-scoped, `!important`-laden copies. There is no single
place to change it, it bloats the CSS, and it starts a specificity war for any future override.

## Common Mistakes

- Using the per-module Custom CSS box for styling that repeats, instead of a shared class.
- Reaching for custom CSS when a built-in design control already exists.
- Targeting Divi's generated `.et_pb_module_N` selectors, which change and break silently.
- Sprinkling `!important` to win specificity instead of moving the rule to the right layer.
- Editing the Divi parent theme's stylesheet, which the next update overwrites.
- Desktop-only pixel values with no media query, breaking mobile layout.

## Production Tips

- Before launch, grep the exported layout / child theme for `!important` — each occurrence is a
  candidate for relocation to a lower-specificity layer.
- Keep a single, commented child-theme `style.css` as the canonical home for custom rules; treat
  module CSS boxes as exceptions that must be justified.
- If a rule "won't apply", check location and specificity before adding force — it is almost always
  a page-scope or cascade issue, not a missing `!important`.

## AI Review Checklist

- Is custom CSS only used where no built-in Divi control exists?
- Do reusable rules live in the child theme / Theme Options field, not in per-module boxes?
- Do selectors target author-added semantic classes, not Divi's generated `.et_pb_*` IDs?
- Is the code free of `!important` and deep nesting, or is each use justified?
- Are custom rules responsive (controls or media queries), not desktop-only pixels?
- Is all CSS in a child theme, never the parent?

## Related

- `knowledge/divi/10-performance.md`
- `knowledge/divi/06-global-elements.md`
- `knowledge/divi/11-responsive-design.md`
- `knowledge/divi/03-modules.md`
- `knowledge/divi/24-best-practices.md`
