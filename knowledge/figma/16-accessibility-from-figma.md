---
id: figma/16-accessibility-from-figma
topic: figma
slug: accessibility-from-figma
title: "Accessibility from Figma"
type: doc
order: 16
status: ready
tags: [figma, accessibility-from-figma, parseInt, background, inset, toFixed, white-space, row-reverse]
related:
  - figma/06-component-detection
  - accessibility/10-color-and-contrast
  - accessibility/05-focus-management
  - figma/01-figma-analysis
  - figma/14-figma-inspection-checklist
  - figma/10-design-qa
  - figma/19-design-handoff
  - accessibility/03-semantic-html
  - accessibility/04-keyboard-navigation
  - accessibility/07-aria
  - accessibility/08-forms
  - accessibility/23-wcag
  - html/02-semantic-html
when_to_use: "Read while inspecting a Figma design, to identify accessibility requirements before implementation begins."
---
# Accessibility from Figma

## Purpose

This document defines the standard process for identifying accessibility requirements during Figma analysis before implementation begins.

Accessibility should be planned while inspecting the design—not added after development.

The goal is to produce interfaces that are usable by all users while remaining faithful to the approved design.

---

## Core Principle

Accessibility starts in the design phase.

Every UI element should be evaluated for accessibility before writing code.

Do not treat accessibility as a separate task.

---

## Accessibility Review Workflow

Follow this sequence during design analysis.

```
Analyze Layout
        ↓
Identify Semantic Structure
        ↓
Review Interactive Elements
        ↓
Review Forms
        ↓
Review Images
        ↓
Review Typography
        ↓
Review Color Contrast
        ↓
Review Keyboard Navigation
        ↓
Review Responsive Behavior
        ↓
Prepare Implementation
```

---

## Step 1 — Semantic Structure

Identify the document structure.

Verify:

- page landmarks;
- sections;
- articles;
- navigation;
- footer;
- sidebar;
- heading hierarchy.

Every visible section should have a semantic purpose.

---

## Step 2 — Heading Hierarchy

Review the complete heading structure.

Verify:

- exactly one H1 per page where appropriate;
- logical heading order;
- no skipped heading levels without justification;
- headings describe content rather than appearance.

Headings create the document outline for assistive technologies.

---

## Step 3 — Interactive Elements

Identify every interactive component.

Examples:

- buttons;
- links;
- navigation;
- menus;
- accordions;
- tabs;
- sliders;
- dialogs;
- dropdowns.

Every interactive element must be operable using both a mouse and a keyboard.

---

## Step 4 — Forms

Review every form.

Verify:

- labels;
- placeholders;
- required indicators;
- validation messages;
- error messages;
- success messages;
- helper text.

Placeholders must never replace labels.

A designer showing grey text inside an input is showing a **label**, not a placeholder — a
placeholder disappears the moment typing starts, taking the field's meaning with it.

**Bad Example** — the label exists only until the user types

```html
<input type="email" placeholder="Email address" class="input" />
<span class="error">Invalid</span>
```

Nothing associates the error with the field, the control has no accessible name once filled,
and "Invalid" tells the user nothing actionable.

**Good Example** — persistent label, associated help and error text

```html
<div class="field">
  <label for="email">Email address</label>

  <input
    id="email"
    name="email"
    type="email"
    autocomplete="email"
    required
    aria-describedby="email-help email-error"
    aria-invalid="true"
  />

  <p id="email-help" class="help">We use this only for your receipt.</p>

  <!-- role="alert" announces the message when it appears, without moving focus. -->
  <p id="email-error" class="error" role="alert">
    Enter an email address in the format name@example.com.
  </p>
</div>
```

When the design genuinely has no room for a visible label, the label still exists — it is
visually hidden, never absent:

```css
/* Available to assistive technology, invisible on screen. Never use display:none. */
.visually-hidden {
  position: absolute;
  width: 1px; height: 1px;
  padding: 0; margin: -1px;
  overflow: hidden;
  clip-path: inset(50%);
  white-space: nowrap;
}
```

See [Accessibility — Forms](../accessibility/08-forms.md) and
[Accessibility — Error Messages](../accessibility/18-error-messages.md).

---

## Step 5 — Images

Classify every image.

Possible categories:

- informative;
- decorative;
- functional;
- branding.

Determine whether meaningful alternative text is required.

Decorative images should not create unnecessary noise for assistive technologies.

---

## Step 6 — Icons

Determine whether icons:

- communicate information;
- trigger actions;
- are decorative.

Icons used as controls require accessible names.

Decorative icons should not be announced unnecessarily.

**Bad Example** — an icon-only control with no name

```html
<button class="icon-btn">
  <svg viewBox="0 0 24 24"><path d="…" /></svg>
</button>
<!-- Screen reader announces: "button". Announcing what, exactly? -->
```

**Good Example** — named control, silent decoration

```html
<!-- Icon-only control: the name lives on the control, the SVG is hidden. -->
<button class="icon-btn" aria-label="Close dialog">
  <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="…" /></svg>
</button>

<!-- Icon beside visible text: the text is already the name, so the icon adds nothing. -->
<button class="btn">
  <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="…" /></svg>
  Download invoice
</button>

<!-- Icon carrying meaning on its own: give it a text equivalent. -->
<span class="status">
  <svg viewBox="0 0 24 24" role="img" aria-labelledby="paid-label"><path d="…" /></svg>
  <span id="paid-label">Paid</span>
</span>
```

Note the status example: the design may communicate "paid" with a green check alone, but color
and shape are not available to every user — WCAG 1.4.1 requires the meaning to survive without
them. Flag this during inspection and request a text equivalent from design.

---

## Step 7 — Color Contrast

Review:

- text;
- buttons;
- links;
- form controls;
- icons;
- status indicators.

Do not rely on color alone to communicate meaning.

Check the palette against the WCAG formula while still in the design file — a failing token
found here costs a conversation, and found after implementation costs a redesign:

```js
// scripts/contrast.mjs — WCAG 2.x relative luminance and contrast ratio
const channel = (v) => {
  const c = v / 255;
  return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
};

const luminance = ([r, g, b]) =>
  0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b);

const hexToRgb = (hex) =>
  hex.replace("#", "").match(/../g).map((h) => parseInt(h, 16));

export function contrast(fg, bg) {
  const [a, b] = [luminance(hexToRgb(fg)), luminance(hexToRgb(bg))].sort((x, y) => y - x);
  return (a + 0.05) / (b + 0.05);
}

const PAIRS = [
  { name: "body on surface",       fg: "#4B5563", bg: "#FFFFFF", size: "normal" },
  { name: "muted caption",         fg: "#9CA3AF", bg: "#FFFFFF", size: "normal" },
  { name: "primary button label",  fg: "#FFFFFF", bg: "#2563EB", size: "normal" },
  { name: "focus ring on surface", fg: "#2563EB", bg: "#FFFFFF", size: "ui" },
];

for (const p of PAIRS) {
  // AA: 4.5:1 normal text · 3:1 large text (>=24px, or >=18.66px bold)
  //     3:1 for UI components and graphical objects (SC 1.4.11)
  const required = p.size === "normal" ? 4.5 : 3;
  const ratio = contrast(p.fg, p.bg);
  console.log(
    `${ratio >= required ? "PASS" : "FAIL"}  ${ratio.toFixed(2)}:1  (needs ${required}:1)  ${p.name}`
  );
}
```

```
PASS  7.56:1  (needs 4.5:1)  body on surface
FAIL  2.54:1  (needs 4.5:1)  muted caption
PASS  5.17:1  (needs 4.5:1)  primary button label
PASS  5.17:1  (needs 3:1)    focus ring on surface
```

The failing caption is a design decision to raise before implementation, not something to
silently darken in CSS — the token has to change everywhere it is used. Disabled controls are
exempt from the contrast requirement; placeholder text is not.
See [Accessibility — Color and Contrast](../accessibility/10-color-and-contrast.md) and
[Accessibility — WCAG](../accessibility/23-wcag.md).

---

## Step 8 — Typography

Verify:

- readable font sizes;
- sufficient line height;
- adequate spacing;
- text alignment;
- paragraph width.

Typography directly affects readability.

---

## Step 9 — Focus Management

Review every interactive flow.

Verify:

- logical tab order;
- visible focus indicators;
- dialog focus management;
- keyboard accessibility.

Users should never lose track of keyboard focus.

Designs rarely include a focus state — that omission is a finding, not permission to skip it.
Implement a visible indicator and record it as a deviation to confirm:

```css
/* Never `outline: none` without a replacement — it removes the only cue
   keyboard users have for their position on the page. */
:focus-visible {
  outline: 2px solid var(--color-focus, #2563EB);
  outline-offset: 2px;
  border-radius: inherit;
}

/* :focus-visible applies to keyboard focus only, so a mouse click on a button
   does not show a ring while a Tab press does. */
:focus:not(:focus-visible) {
  outline: none;
}

/* The indicator must survive a dark surface too — 3:1 against its background (SC 1.4.11). */
.surface-dark :focus-visible {
  outline-color: #93C5FD;
}
```

Tab order follows DOM order, so a design that visually reorders columns at a breakpoint
creates a mismatch when implemented with `order` or `row-reverse`: the visual sequence and the
keyboard sequence diverge. Reorder the markup instead. See
[Accessibility — Focus Management](../accessibility/05-focus-management.md) and
[Accessibility — Keyboard Navigation](../accessibility/04-keyboard-navigation.md).

---

## Step 10 — Responsive Accessibility

Review every breakpoint.

Verify:

- touch target size;
- navigation usability;
- readable typography;
- spacing;
- scrolling behavior.

Accessibility must be preserved across all supported devices.

Measure the touch targets in the mobile frame rather than trusting how they look. WCAG 2.2
SC 2.5.8 sets a 24×24 CSS px minimum (AA); SC 2.5.5 asks for 44×44 (AAA), which is the
practical target for primary actions:

```css
/* A 16px icon in a 24px box is a 24px target — below comfortable, and easy to miss. */
.icon-btn {
  min-inline-size: 44px;
  min-block-size: 44px;
  display: inline-grid;
  place-items: center;
}

/* When the design demands a visually small control, keep the hit area large. */
.compact-toggle {
  position: relative;
}
.compact-toggle::after {
  content: "";
  position: absolute;
  inset: -12px;          /* extends the target without changing the visual size */
}
```

Also confirm the layout survives zoom: WCAG 1.4.10 requires content to reflow at 320px
equivalent width (400% zoom on a 1280px viewport) without horizontal scrolling. A fixed-width
container in the design will fail this. See
[Accessibility — Responsive Accessibility](../accessibility/13-responsive-accessibility.md).

---

## Accessibility Questions

Before implementation ask:

- Can this page be understood without visual styling?
- Can every interactive element be reached using a keyboard?
- Does every control have an accessible name?
- Does the heading hierarchy describe the content?
- Can users understand errors without relying only on color?

If any answer is "No", improve the implementation plan.

---

## AI Execution Checklist

## Investigation

☐ Semantic structure identified.

☐ Heading hierarchy reviewed.

☐ Interactive elements identified.

☐ Forms reviewed.

☐ Images classified.

☐ Icons reviewed.

☐ Color contrast considered.

☐ Responsive accessibility reviewed.

---

## Verification

☐ Accessibility requirements documented.

☐ Keyboard interaction planned.

☐ Semantic HTML planned.

☐ Form accessibility planned.

☐ Image accessibility planned.

---

## Common Mistakes

Avoid:

Replacing semantic HTML with generic containers.

Using placeholders instead of labels.

Skipping heading levels.

Relying only on color.

Removing focus indicators.

Ignoring keyboard navigation.

Using icons without accessible names.

Adding accessibility only after implementation.

---

## Completion Criteria

Accessibility planning is complete when:

- semantic structure has been defined;
- interactive elements have been reviewed;
- form accessibility has been planned;
- image accessibility has been evaluated;
- responsive accessibility has been considered;
- implementation requirements have been documented.

---

## Recording the Findings

Accessibility decisions made during inspection must reach implementation. Annotate the design
analysis rather than keeping them in your head:

```yaml
# design/a11y/pricing.yml
landmarks:
  header: <header> with <nav aria-label="Main">
  main: <main> — one per page
  footer: <footer>

headings:
  h1: "Simple, transparent pricing"
  h2: [Plans, Compare features, FAQ]
  note: "Plan names render as h3 inside each card — visual size is not the heading level."

interactive:
  - element: PlanCard
    role: "link wrapping the card is wrong — use a button/link inside, or the whole card
           becomes one unreadable link label"
    keyboard: "Tab reaches the CTA; the card itself is not focusable."
  - element: FAQ accordion
    pattern: "button[aria-expanded] controlling a region — no role=tablist"

images:
  hero-photo: decorative → alt=""
  logo-acme:  informative → alt="Acme"
  icon-check: decorative beside text → aria-hidden="true"

deviations_from_design:
  - "Focus ring not specified in the file — using --color-focus at 2px/2px offset."
  - "Muted caption #9CA3AF fails AA at 2.54:1 — requested a darker token from design."
```

The `deviations_from_design` list is what a designer reviews. An accessibility fix applied
silently tends to be reverted at the next design update.

---

## Related Knowledge

- [Figma Inspection Checklist](14-figma-inspection-checklist.md) — where these checks sit in the inspection order.
- [Design QA](10-design-qa.md) — verifying the implementation against what was planned here.
- [Design Handoff](19-design-handoff.md) — what to request when the file omits states, labels, or contrast-safe tokens.
- [Accessibility — Semantic HTML](../accessibility/03-semantic-html.md), [ARIA](../accessibility/07-aria.md), [Forms](../accessibility/08-forms.md), [Color and Contrast](../accessibility/10-color-and-contrast.md) — the implementation detail behind each step.
- [Accessibility — WCAG](../accessibility/23-wcag.md) — the success criteria referenced throughout.
- [Testing — Accessibility Testing](../testing/18-accessibility-testing.md) — verifying the result automatically.

---

## Summary

Accessibility begins during design analysis.

Identifying accessibility requirements before implementation results in cleaner code, fewer revisions, and interfaces that are usable by a broader range of people.