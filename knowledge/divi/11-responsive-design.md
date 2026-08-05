---
id: divi/11-responsive-design
topic: divi
slug: responsive-design
title: "Divi Responsive Design"
type: doc
order: 11
status: ready
tags: [divi, responsive-design]
related: [divi/09-custom-css, divi/10-performance, divi/12-accessibility, divi/08-templates, divi/03-modules]
when_to_use: "Read before adjusting any layout for phone/tablet or when a Divi page looks broken on mobile."
---
# Divi Responsive Design

## Purpose

This document defines how to make Divi layouts work across screen sizes using Divi's native
responsive system: the three breakpoint tabs (Desktop, Tablet, Phone) on almost every design
control, responsive visibility, and Divi 5's custom breakpoints. It is written so an agent
produces layouts that adapt correctly rather than ones that only look right on the machine they
were built on.

Divi's model is **mobile-inherits-from-desktop**: a value set on Desktop applies to Tablet and
Phone unless you override it on those tabs. Understanding that inheritance is the whole game.

## Why It Matters

Most traffic is mobile, and Google indexes mobile-first — so the phone layout is the *primary*
layout, not an afterthought. Divi makes it easy to build a beautiful desktop page whose fixed
pixel paddings, four-column rows, and oversized headings collapse into an unusable mess on a
360px screen, and because the builder opens on Desktop by default, the author never sees it. Every
responsive override you skip is a bug that only mobile users experience. Responsive correctness is
also tied to performance (CLS from reflow) and accessibility (tap targets, readable text). See
[performance](10-performance.md) and [accessibility](12-accessibility.md).

## Core Principles

- **Design is mobile-first even in a desktop-first tool.** Values cascade Desktop → Tablet →
  Phone. Set sensible desktop defaults, then override only what must change downward. Always review
  the Phone tab before considering a section done.
- **Prefer fluid units and Divi's layout controls to fixed pixels.** Percentages, `rem`/`em`, and
  Divi's column stacking adapt; hard-coded `px` paddings and heights do not.
- **Override on the right tab, not with new CSS.** Use the Tablet/Phone tabs on the existing
  control instead of writing a separate media query — it stays in the builder model and remains
  editable. See [custom-css](09-custom-css.md).
- **Rows stack; plan the stack order.** Multi-column rows collapse to one column on phone in source
  order. If the visual order must differ, use Divi's column reversal, not absolute positioning.
- **Responsive visibility hides, it does not delete.** "Disable on Phone" still loads the module's
  markup/assets; use it for layout, not to ship a lighter page. For weight, remove the module.
- **Test real breakpoints and real content.** Long titles, long menus, and empty fields break at
  edges that lorem ipsum hides.

## Best Practices

- Build on Desktop, then walk the Tablet and Phone tabs of every section, overriding font sizes,
  paddings, and column behavior that do not translate. Divi shows a colored dot on controls that
  have a responsive override — use it to audit.
- Use `rem`/`em` or Divi's built-in responsive font scaling for typography so text stays readable
  without per-breakpoint hand-tuning.
- Reduce section/row vertical padding on Phone; desktop whitespace is usually far too large on a
  small screen.
- Ensure interactive targets (buttons, menu items) are at least ~44px tall on phone and not
  crammed edge-to-edge. See [accessibility](12-accessibility.md).
- Configure the mobile menu explicitly and test it; the hamburger breakpoint and full-screen/nested
  menu behavior are easy to leave in a broken default.
- Preview Theme Builder templates (header/footer) responsively too, not just page content — headers
  are the most common mobile break. See [templates](08-templates.md).

## Examples

**Good Example** — responsive overrides on the built-in control, fluid type, phone padding

```text
Section → Spacing (padding top/bottom)
  Desktop: 120px    Tablet: 80px    Phone: 48px      // overridden per tab, not one fixed value

Heading → Text Size
  Desktop: 3rem     Tablet: 2.25rem  Phone: 1.75rem   // rem scales; readable on 360px

Row: 4 columns on Desktop → stacks to 1 column on Phone (Divi default)
  Column order verified so the CTA lands first after stacking
Button: min height ~48px on Phone, full-width               // easy tap target
```

Why: each control adapts on its own tab within the builder, typography scales with `rem`, phone
padding is sane, and the stacked order is deliberate — the page works on a real phone.

**Bad Example** — desktop-only fixed values and misuse of visibility

```text
Section → padding: 120px  (Desktop only, no Tablet/Phone override)  // 120px on a 360px screen
Heading → Text Size: 48px (fixed px, all breakpoints)               // overflows on phone
4-column row, no stacking check                                     // squished to slivers
Mobile fix: "Disable on Phone" the whole section                    // content just vanishes on mobile
Custom CSS: position: absolute; left: 600px                         // shatters below 600px viewport
```

Why this is wrong: fixed desktop paddings and font sizes overflow small screens, the columns are
unusable when squeezed, hiding the section makes content disappear for mobile users, and absolute
positioning has no responsive fallback.

## Common Mistakes

- Reviewing only the Desktop tab and never opening Tablet/Phone before shipping.
- Fixed `px` paddings/heights and font sizes that overflow or dwarf small screens.
- Using "Disable on Phone" to fix layout, hiding content from the majority of users.
- Absolute positioning / negative margins that have no small-screen fallback.
- Ignoring stack order, so columns reflow into a confusing sequence on phone.
- Leaving the mobile menu at an untested default.
- Assuming "Disable on X" reduces page weight — it still loads the assets.

## Production Tips

- Test on real devices or accurate device emulation at 360px, 768px, and a large desktop width,
  with real (long) content, before launch.
- If Divi 5 custom breakpoints are enabled, document them; a value that looks wrong may be an
  override at a non-standard breakpoint.
- Re-check mobile after content edits — editors routinely add desktop-only paddings that regress phone.

## AI Review Checklist

- Has every section been reviewed and overridden on the Tablet and Phone tabs, not just Desktop?
- Are paddings and font sizes fluid (`rem`/%/responsive controls), not fixed desktop `px`?
- Is column stack order deliberate and correct on phone?
- Are tap targets ~44px+ and not crammed on mobile?
- Is content adapted rather than hidden with "Disable on Phone"?
- Have Theme Builder header/footer templates been tested responsively?

## Related

- `knowledge/divi/09-custom-css.md`
- `knowledge/divi/10-performance.md`
- `knowledge/divi/12-accessibility.md`
- `knowledge/divi/08-templates.md`
- `knowledge/divi/03-modules.md`
