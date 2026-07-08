---
id: nextjs/25-accessibility
topic: nextjs
slug: accessibility
title: "Accessibility"
type: doc
order: 25
status: ready
tags: [nextjs, accessibility]
related: [nextjs/07-client-components, nextjs/05-layouts, nextjs/16-images, nextjs/17-fonts, nextjs/22-testing]
when_to_use: "Read before building any UI, form, navigation, or interactive component in a Next.js app."
---
# Accessibility

## Purpose

This document defines how to build Next.js interfaces that work for everyone, including people
using keyboards, screen readers, and assistive technology. It targets WCAG 2.2 AA and focuses
on the accessibility concerns specific to the App Router: client navigation, focus management,
and the framework's `next/link`, `next/image`, and `next/font` primitives.

## Why It Matters

Accessibility is a correctness and legal requirement, not a nice-to-have — inaccessible flows
lock out real users and expose the organization to litigation. Single-page navigation makes it
worse: when Next.js swaps content client-side without a full page load, screen readers are not
automatically told the page changed and keyboard focus can be stranded on a stale element.
These failures are invisible to a sighted mouse user, so they survive code review unless the
rules below are applied deliberately.

## Core Principles

- **Semantic HTML first.** Use `<button>`, `<a>`, `<nav>`, `<main>`, `<h1>`–`<h6>` for their
  meaning. Native elements come with focus, keyboard, and role behavior that a `<div>` plus
  ARIA cannot fully recreate. ARIA supplements semantics; it does not replace them.
- **Everything works from the keyboard.** Every interactive element must be reachable and
  operable by Tab/Enter/Space/arrows, with a visible focus indicator. Never remove `outline`
  without replacing it.
- **Announce and manage focus on navigation.** After a route change or dialog open, move focus
  deliberately so keyboard and screen-reader users are not lost.
- **Perceivable by default.** Meaningful images need real `alt`; text needs sufficient contrast
  (4.5:1 for body text); information is never conveyed by color alone.

## Best Practices

- Set `lang` on `<html>` in the root layout (`app/layout.tsx`) so screen readers pronounce
  content correctly.
- Use `next/link` for navigation (renders a real `<a>`); use `<button>` for actions. Never make
  a clickable `<div>` — it loses keyboard and role semantics.
- Provide a "skip to content" link and one `<main id="content">` per page so keyboard users can
  bypass repeated navigation.
- Give every `next/image` a descriptive `alt`, or `alt=""` if purely decorative — an empty
  string is a deliberate signal, a missing attribute is a bug.
- Label every form control with a `<label htmlFor>`; associate errors via `aria-describedby` and
  mark the field `aria-invalid`. Do not rely on placeholder text as a label.
- Load fonts with `next/font` and set `display: 'swap'` so text stays visible while fonts load
  (avoids invisible-text flashes that hurt low-vision users).
- Manage focus in client components with `useRef` + `useEffect` when opening dialogs or after
  async updates; return focus to the trigger on close.

## Examples

**Good Example** — semantic, labeled, focus-managed

```tsx
'use client';
import { useEffect, useRef } from 'react';

export function EditDialog({ open, onClose, title }: Props) {
  const closeRef = useRef<HTMLButtonElement>(null);
  useEffect(() => { if (open) closeRef.current?.focus(); }, [open]); // focus enters dialog

  if (!open) return null;
  return (
    <div role="dialog" aria-modal="true" aria-labelledby="dlg-title">
      <h2 id="dlg-title">{title}</h2>       {/* labels the dialog for screen readers */}
      <label htmlFor="name">Name</label>
      <input id="name" name="name" aria-describedby="name-err" />
      <button ref={closeRef} onClick={onClose}>Close</button> {/* real button: keyboard-operable */}
    </div>
  );
}
```

**Bad Example** — div-buttons, no labels, color-only state

```tsx
// Not focusable, no keyboard, no role — screen readers announce nothing actionable.
<div className="btn" onClick={save}>Save</div>

// Placeholder is not a label; it vanishes on input and screen readers may skip it.
<input placeholder="Email" />

// Error signaled only by red border → invisible to color-blind and screen-reader users.
<input style={{ borderColor: error ? 'red' : 'gray' }} />
```

## Common Mistakes

- Clickable `<div>`/`<span>` instead of `<button>`/`<a>`, losing keyboard and role behavior.
- Missing or wrong `alt` on `next/image`; using `alt` to stuff keywords instead of describing.
- Removing focus outlines for aesthetics, leaving keyboard users unable to see where they are.
- Placeholder-as-label; unlabeled icon-only buttons (add `aria-label`).
- Skipping heading levels (`h1` → `h4`), breaking screen-reader document structure.
- Not moving focus after opening a modal or navigating, stranding keyboard users.

## Production Tips

- Add `eslint-plugin-jsx-a11y` (recommended config) to catch missing `alt`, labels, and roles
  at lint time — cheap, fast feedback before review.
- Run axe (via `@axe-core/react` in dev or Playwright + axe in CI) so regressions fail the build.
- Test the real thing: navigate a key flow with keyboard only, then with a screen reader
  (VoiceOver/NVDA). Automated tools catch ~40% of issues; the rest need manual checks.

## AI Review Checklist

- Are interactive elements native (`<button>`, `<a>`, `<label>`) rather than `<div>` + handlers?
- Does the root layout set `lang`, and does each page have one `<main>` and a skip link?
- Do all meaningful images have descriptive `alt` (and decorative ones `alt=""`)?
- Are form controls labeled and errors linked via `aria-describedby` / `aria-invalid`?
- Is focus moved intentionally on dialog open and route change, with visible focus indicators?
- Is information conveyed by more than color, and does text meet 4.5:1 contrast?

## Related

- `knowledge/nextjs/07-client-components.md`
- `knowledge/nextjs/05-layouts.md`
- `knowledge/nextjs/16-images.md`
- `knowledge/nextjs/17-fonts.md`
- `knowledge/nextjs/22-testing.md`
