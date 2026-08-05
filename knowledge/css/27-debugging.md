---
id: css/27-debugging
topic: css
slug: debugging
title: "CSS Debugging"
type: doc
order: 27
status: ready
tags: [css, debugging]
related: [css/03-specificity, css/04-box-model, css/22-performance, css/26-browser-compatibility]
when_to_use: "Read when a style is not applying, an element is the wrong size or position, or the layout overflows and you cannot see why."
---
# CSS Debugging

## Purpose

This document defines a systematic method for diagnosing CSS problems: a rule that will
not apply, an element that is the wrong size, an unexpected scrollbar, a layout that
collapses. CSS has no stack trace, so debugging is about *observing the computed reality*
in devtools rather than guessing at source. The aim is to replace trial-and-error edits
with a repeatable diagnostic sequence.

## Why It Matters

The instinct when a style does not work is to pile on more CSS — another selector, an
`!important`, a magic pixel offset — until something moves. That "fixes" the symptom while
adding specificity debt and hiding the real cause, so the next change reopens the bug.
Every guess-and-check edit also risks breaking two other layouts. Debugging from the
computed state instead tells you *why* — which rule won, what the box actually measures,
what created that scrollbar — so one precise change fixes it. Speed and correctness both
come from looking before editing.

## Core Principles

- **Read the computed value, not the source.** The Styles/Computed panel shows which
  declaration actually won and which were struck through. That is ground truth; your source
  file is a hypothesis.
- **A rule that "doesn't work" is almost always overridden, misselected, or invalid.**
  Struck-through in devtools means a more specific rule won; no rule at all means the
  selector does not match; a yellow warning means invalid syntax.
- **Size and position problems are box-model problems.** Inspect `box-sizing`, padding,
  border, and margin in the box diagram before touching `width`.
- **Change one thing, then reobserve.** Toggle a single declaration in devtools and watch
  the result; do not batch guesses.
- **Isolate to bisect.** When the cause is unclear, remove halves of the CSS (or the DOM)
  until the problem disappears, then add back to find the trigger.

## Best Practices

- Use the **Styles panel** to see the winning rule and the strike-through losers; use the
  **Computed panel** to see the final value and click "arrow" to jump to its source.
- Turn on **element outlines** (`* { outline: 1px solid red; }` temporarily, or devtools'
  layout overlays) to reveal box boundaries and spot the element causing overflow.
- Diagnose horizontal overflow by finding the widest child: in the console,
  `document.querySelectorAll('*').forEach(e => { if (e.scrollWidth > document.documentElement.clientWidth) console.log(e); })`.
- For **specificity** conflicts, read the selector's weight in devtools rather than adding
  `!important`; fix by lowering the winner or matching it. See [specificity](03-specificity.md).
- For **flex/grid**, use the devtools grid and flex overlays to see tracks, gaps, and
  alignment — invisible in source, obvious in the overlay.
- Toggle **`:hover`/`:focus`/`:active`** states in devtools ("force element state") to debug
  interactive styles you cannot otherwise freeze.
- When a value is unexpectedly inherited, check the **Computed** panel's "inherited from"
  chain rather than assuming the local rule.

## Examples

**Good Example** — diagnose before editing

```css
/* Symptom: `.btn` text stays black though you wrote `color: white`.
   Devtools Styles panel shows your rule STRUCK THROUGH — a more specific
   selector won. The fix is to match that specificity, not to escalate. */

.card .btn { color: black; }   /* specificity 0,2,0 — this was winning */

/* Correct fix: raise the intended rule to the same weight, deliberately. */
.card .btn.btn--primary { color: white; }  /* 0,3,0, and the intent is explicit */
```

**Bad Example** — escalate blindly

```css
/* Same symptom, but instead of inspecting, you slap on !important.
   It "works" today but now nothing can override .btn without another !important,
   and you never learned that `.card .btn` was the real culprit. */
.btn { color: white !important; } /* specificity nuke — debt, not a fix */
```

## Common Mistakes

- Editing source and reloading repeatedly instead of toggling declarations live in devtools.
- Adding `!important` to force a style instead of finding which selector is winning and why.
- Blaming `width` for a sizing bug that is actually `box-sizing: content-box` adding padding.
- Ignoring the yellow "invalid property value" warning in the Styles panel, which means the
  declaration was dropped entirely.
- Debugging overflow by hiding it (`overflow: hidden`) instead of finding the too-wide child.
- Assuming a rule does not exist when the selector simply does not match the element (typo,
  wrong nesting, dynamic class not applied).
- Testing the fix only in the one browser where the bug appeared — some CSS bugs are
  engine-specific. See [browser compatibility](26-browser-compatibility.md).

## Production Tips

- Reproduce the bug in the specific engine and at the specific viewport where it occurs;
  responsive and engine-specific bugs vanish under the wrong conditions.
- For CSS that appears "randomly" broken, suspect the cascade order changed (a layer, an
  import order, a build that reordered rules) rather than the rule itself.
- Keep a scratch `outline`/background-tint debugging snippet handy but never commit it;
  temporary diagnostic CSS shipped to production is its own class of bug.

## AI Review Checklist

- Was the winning rule identified in the Styles panel before any edit was made?
- Is the fix a targeted specificity/selector change rather than an added `!important`?
- For a sizing bug, were `box-sizing`, padding, and border checked before `width`?
- For overflow, was the actual too-wide element located?
- Were invalid-value warnings in devtools checked and resolved?
- Was the fix verified in the same browser/viewport where the bug appeared?

## Related

- `knowledge/css/03-specificity.md`
- `knowledge/css/04-box-model.md`
- `knowledge/css/22-performance.md`
- `knowledge/css/26-browser-compatibility.md`
