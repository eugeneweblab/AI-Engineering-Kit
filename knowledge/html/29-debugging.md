---
id: html/29-debugging
topic: html
slug: debugging
title: "Debugging"
type: doc
order: 29
status: ready
tags: [html, debugging]
related: [html/22-validation, html/11-accessibility, html/20-browser-rendering, html/18-performance, html/99-ai-review-checklist]
when_to_use: "Read before diagnosing why a page renders, reflows, or behaves incorrectly."
---
# Debugging

## Purpose

This document defines a systematic method for finding the cause of HTML rendering and
behavior bugs: unexpected layout, elements the browser silently "fixed", accessibility
failures, and content that appears in the source but not on screen. The goal is to move
from "it looks wrong" to a specific, verified root cause using the browser's own tools —
the DevTools Elements panel, the validator, the accessibility tree — rather than guessing
and reshuffling markup.

## Why It Matters

HTML fails quietly. There is no compiler and no runtime error for a misnested tag; the
browser silently repairs invalid markup, often not the way you intended, and the bug
surfaces later as a mysterious layout shift or a node that "won't style." The gap between
the HTML you wrote and the DOM the browser built is where most of these bugs live. A
debugging method that inspects the *live DOM and computed styles* — not the source you
typed — is the difference between a two-minute fix and an afternoon of thrashing.

## Core Principles

- **Debug the DOM, not the source.** The Elements panel shows what the browser actually
  built after error-correction; compare it against your source to spot silent repairs.
- **Validate first.** Run the [validator](22-validation.md) before deep debugging —
  misnested or duplicated-`id` markup produces bizarre downstream symptoms.
- **Isolate before you theorize.** Reproduce the bug in a minimal snippet; removing
  unrelated markup usually reveals the offending element quickly.
- **Read computed styles, not authored ones.** "Why is this invisible/misaligned?" is
  answered by the Computed tab and the box model, which show what actually won.
- **Check the accessibility tree, not just the pixels.** A page can look correct and be
  broken for assistive tech; the a11y inspector shows the semantic reality.

## Best Practices

- Open DevTools Elements and confirm the DOM matches your intent — look for tags the
  parser moved (a `<div>` inside a `<table>` gets hoisted out) or auto-closed.
- Use the Computed styles tab and box-model diagram to trace which rule set a property and
  whether margins/padding/`box-sizing` explain the geometry.
- Toggle element states (`:hover`, `:focus`) and force them in DevTools to debug
  interactive styling without chasing the pointer.
- Use the "Rendering" panel to visualize layout shifts, paint flashing, and
  `content-visibility` to diagnose reflow and jank.
- Inspect the accessibility pane to verify roles, names, and the tab order; run axe or
  Lighthouse for a labeled report of failures.
- For "content missing" bugs, check whether it is `display:none`, clipped by
  `overflow`, off-screen positioned, or simply never in the DOM (failed JS/template).
- Search for duplicate `id`s (`document.querySelectorAll` count) — duplicates break
  label association, `getElementById`, and anchor links.

## Examples

**Good Example** — verifying the real DOM and finding the silent repair

```js
// Symptom: styles on a <td> "don't apply." Check what the browser actually built.
const cell = document.querySelector("td.total");
console.log(cell?.parentElement.tagName); // expect "TR"; if it's "BODY", the row was hoisted

// Duplicate ids silently break getElementById and label[for] — count them:
const ids = [...document.querySelectorAll("[id]")].map(el => el.id);
const dupes = ids.filter((id, i) => ids.indexOf(id) !== i);
console.log("duplicate ids:", [...new Set(dupes)]); // fix these first
```

```html
<!-- Root cause the DOM revealed: a <td> with no wrapping <tr>; the parser
     moved it out of the table, so table styles never reached it. Fix the nesting. -->
<table>
  <tr><td class="total">$0</td></tr>
</table>
```

**Bad Example** — guessing from the source and papering over the symptom

```css
/* Symptom: element not visible. Instead of inspecting the DOM/computed styles,
   pile on overrides and hope one sticks — this hides the real cause. */
.total {
  display: block !important;   /* was the element even in the DOM? unknown */
  visibility: visible !important;
  z-index: 99999 !important;   /* cargo-culting; no evidence z-index was the issue */
  margin-top: -9999px;         /* now it's off-screen for a different reason */
}
```

## Common Mistakes

- Debugging the HTML source instead of the live DOM, missing the parser's silent repairs.
- Skipping validation, so a misnested tag or duplicate `id` sends you chasing symptoms.
- Adding `!important` and higher `z-index` by trial and error instead of reading computed
  styles to find which rule actually won.
- Assuming "not visible" means a CSS problem when the node was never rendered (JS/template
  failure) — check existence in the DOM first.
- Ignoring the accessibility tree, shipping a page that looks right but is unusable with a
  screen reader or keyboard.
- Testing in one browser; parser and rendering quirks differ across engines.

## Production Tips

- Keep HTML validation and an automated a11y scan (axe/Lighthouse) in CI so structural
  regressions fail the build instead of reaching users.
- Reproduce user-reported layout bugs at the reported viewport and device pixel ratio —
  many "bugs" are responsive breakpoints, not defects.
- When a bug only appears in production, diff the server-rendered HTML against local; a
  sanitizer or template escaping difference is a common culprit.
- Save minimal reproductions; they document the fix and become regression tests.

## AI Review Checklist

- Was the diagnosis based on the live DOM and computed styles, not just the source?
- Has the markup been run through the validator, with misnesting and duplicate `id`s ruled out?
- For "missing content," was DOM existence checked before assuming a CSS cause?
- Were fixes made at the root cause rather than layered `!important`/`z-index` overrides?
- Was the accessibility tree and keyboard order verified, not only the visual result?
- Was the bug confirmed fixed across the relevant browsers/viewports?

## Related

- `knowledge/html/22-validation.md`
- `knowledge/html/11-accessibility.md`
- `knowledge/html/20-browser-rendering.md`
- `knowledge/html/18-performance.md`
- `knowledge/html/99-ai-review-checklist.md`
