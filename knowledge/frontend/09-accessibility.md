---
id: frontend/09-accessibility
topic: frontend
slug: accessibility
title: "Frontend Accessibility"
type: doc
order: 9
status: ready
tags: [frontend, accessibility, DeleteButton, aria-label, focus, useEffect, prefers-reduced-motion]
related: [accessibility/01-accessibility-fundamentals, frontend/12-forms, frontend/02-component-driven-development, frontend/10-responsive-design, frontend/07-rendering, frontend/28-ui-patterns]
defers_to: accessibility/01-accessibility-fundamentals
when_to_use: "Read before building any interactive component, form, modal, or custom control."
---
# Frontend Accessibility

## Purpose

This document defines how to build interfaces usable by everyone, including people who
navigate with a keyboard, a screen reader, voice control, or a magnifier. It is written
so an agent can ship a component that is accessible by construction, not one that has to
be retrofitted after an audit fails.

The target is **WCAG 2.2 AA**. Accessibility is not a separate feature bolted onto the UI;
it is a property of correct HTML, correct focus management, and correct labeling. Most of
it is free if you use the right element from the start.

## Why It Matters

Roughly one in six people has a disability, and accessibility barriers exclude them from
using — or buying from — your product. In many jurisdictions AA conformance is also a legal
requirement, and inaccessible sites draw lawsuits. The trap is that a mouse-using developer
never notices the problem: the app looks perfect while being completely unusable with a
keyboard or screen reader. Because the failure is invisible to the person building it,
accessibility must be a deliberate discipline, checked, not assumed.

## Core Principles

- **Use the native element.** A real `<button>`, `<a>`, `<input>`, or `<label>` comes with
  keyboard support, focus, and screen-reader semantics for free. Rebuilding them with `<div>`
  means re-implementing all of that — and you will miss cases.
- **Everything operable by mouse must be operable by keyboard.** Every interactive element
  must be reachable with Tab, activatable with Enter/Space, and dismissible with Escape.
- **Semantics convey meaning, not just appearance.** Headings, landmarks, lists, and labels
  tell assistive tech what things *are*. Styling a `<div>` to look like a heading tells it nothing.
- **Never trap or lose focus.** Focus must be visible, move logically, be sent into dialogs
  when they open, and return to the trigger when they close.
- **Do not rely on color alone.** Color-blind and low-vision users need a second signal (text,
  icon, underline) and sufficient contrast (4.5:1 for body text).

## Best Practices

- Give every form control a programmatic label (`<label htmlFor>` or `aria-label`); placeholder
  text is not a label and disappears on input (see [forms](12-forms.md)).
- Provide meaningful `alt` text for informative images and `alt=""` for decorative ones, so
  screen readers describe the first and skip the second.
- Reach for **ARIA only to fill gaps** native HTML cannot. Wrong ARIA is worse than none —
  it actively lies to assistive tech. First rule of ARIA: don't use ARIA if a native element works.
- Manage focus for dynamic UI: move focus into a modal on open, trap it inside while open,
  restore it to the trigger on close, and announce async updates via a live region.
- Ensure a **visible focus indicator** on every interactive element; never `outline: none`
  without an equally clear replacement.
- Meet contrast minimums (4.5:1 text, 3:1 large text and UI components) and support 200% zoom
  and 320px reflow without loss of content (overlaps with [responsive design](10-responsive-design.md)).
- Structure the page with one `<h1>` and a correct heading hierarchy, plus landmarks
  (`<header>`, `<nav>`, `<main>`, `<footer>`) so users can jump directly to sections.
- Respect `prefers-reduced-motion` and never convey meaning through motion or color alone.

## Examples

**Good Example** — native semantics, labeled control, keyboard-free by default

```tsx
function DeleteDialog({ onConfirm, onClose }: Props) {
  const ref = useRef<HTMLButtonElement>(null);
  useEffect(() => ref.current?.focus(), []); // move focus into the dialog on open

  return (
    // role + aria-modal + labelledby tell screen readers this is a modal dialog.
    <div role="dialog" aria-modal="true" aria-labelledby="dlg-title" onKeyDown={escapeCloses}>
      <h2 id="dlg-title">Delete file?</h2>
      {/* Real <button>: Tab-reachable, Enter/Space activate, focusable — all for free */}
      <button ref={ref} onClick={onConfirm}>Delete</button>
      <button onClick={onClose}>Cancel</button>
    </div>
  );
}

// A visible icon-only control still needs an accessible name:
<button aria-label="Close"><XIcon aria-hidden="true" /></button>
```

**Bad Example** — clickable div, color-only state, no keyboard support

```tsx
function DeleteButton({ onConfirm }: { onConfirm: () => void }) {
  // A div is not focusable, not Tab-reachable, and Enter/Space do nothing.
  // Screen readers announce nothing — this control is invisible to them.
  return (
    <div className="btn" onClick={onConfirm} style={{ color: "red" }}>
      Delete {/* meaning carried only by color → invisible to color-blind users */}
    </div>
  );
}
// Icon button with no label → screen reader says "button", not what it does:
<button onClick={close}>✕</button>
```

## Common Mistakes

- Building buttons and links from `<div>`/`<span>`, losing keyboard and screen-reader support.
- Icon-only controls with no `aria-label`, announced as an unnamed "button".
- Removing focus outlines for looks without providing a visible replacement.
- Conveying state (error, selected, required) through color alone.
- Placeholder text used as the only label, disappearing the moment the user types.
- Opening a modal without moving focus into it or trapping focus, stranding keyboard users.
- Sprinkling ARIA roles onto native elements, overriding correct built-in semantics.

## Production Tips

- Add automated checks (axe, Lighthouse) to CI — they catch ~30-50% of issues cheaply — but
  never treat a green automated score as "accessible"; the rest needs manual testing.
- Test the primary flows with keyboard only and with a real screen reader (VoiceOver, NVDA).
- Include focus and contrast checks in design review (see [design review](29-design-review.md)).

## AI Review Checklist

- Are interactive elements native (`<button>`, `<a>`, `<input>`) rather than clickable `<div>`s?
- Is every control reachable by Tab, activatable by keyboard, and dialogs dismissible by Escape?
- Does every form control have a programmatic label, and every image appropriate `alt`?
- Is there a visible focus indicator, and is focus managed for modals and dynamic content?
- Does text meet 4.5:1 contrast, and is no meaning carried by color alone?
- Is ARIA used only where native HTML falls short, and is it correct?
- Does the page have one `<h1>`, ordered headings, and landmark regions?

## Related

- `knowledge/accessibility/01-accessibility-fundamentals.md`
- `knowledge/frontend/12-forms.md`
- `knowledge/frontend/02-component-driven-development.md`
- `knowledge/frontend/10-responsive-design.md`
- `knowledge/frontend/07-rendering.md`
- `knowledge/frontend/28-ui-patterns.md`
