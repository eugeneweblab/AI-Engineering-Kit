---
id: css/100-common-antipatterns
topic: css
slug: common-antipatterns
title: "CSS Common Antipatterns"
type: doc
order: 100
status: ready
tags: [css, common-antipatterns]
related: [css/03-specificity, css/20-css-variables, css/30-engineering-principles, css/22-performance, css/23-accessibility]
when_to_use: "Read when writing new CSS or reviewing a diff, to recognize and reject the failure patterns below."
---
# CSS Common Antipatterns

## Purpose

This document catalogs the CSS patterns that reliably cause pain, each with *why it is
wrong* and *the fix*. An agent should treat these as reject-on-sight during review and
avoid them when authoring. They are the concrete failures that violate the
[engineering principles](30-engineering-principles.md).

## Why It Matters

CSS antipatterns rarely fail immediately — they work in the diff that introduces them and
break something else weeks later. Because the cost is deferred and non-local, they slip
through review unless a reviewer knows the pattern by name. Naming them makes them
rejectable.

## Core Principles

- **Specificity is a ceiling you cannot lower.** Every over-specific selector forces the
  next author to go higher. Keep it flat.
- **Repetition is drift waiting to happen.** A value duplicated will eventually diverge.
- **The layout must survive real content.** Fixed dimensions assume content you do not control.

## The Antipatterns

### 1. `!important` to win a cascade fight

**Why it is wrong:** `!important` overrides the normal cascade, so the only way to beat it
is another `!important`. It escalates until the stylesheet is unmaintainable and nothing
can be reliably overridden. See [specificity](03-specificity.md).
**The fix:** Lower the specificity of the *competing* rule instead of raising this one.
Style with a single class and let source order decide. Reserve `!important` for isolated
utility classes whose whole job is to win (`.u-hidden { display: none !important }`).

### 2. Over-qualified descendant selectors

**Why it is wrong:** `.homepage .content .sidebar ul li a` is tied to a specific DOM shape
and a high specificity. It breaks when markup moves and forces escalation to override.
**The fix:** Give the element one class describing what it is (`.nav-link`) and style that.
Specificity stays `0,1,0` and the style survives markup changes.

```css
/* Bad: brittle and specificity 0,4,1 */
.homepage .content .sidebar ul li a { color: blue; }

/* Good: portable and specificity 0,1,0 */
.nav-link { color: blue; }
```

### 3. Magic numbers instead of tokens

**Why it is wrong:** Hard-coding `#3b82f6` or `16px` in many rules means a redesign is a
fragile find-and-replace that misses occurrences and cannot be themed.
**The fix:** Define the decision once as a [custom property](20-css-variables.md) and
reference it. One edit updates every use, and theming becomes a variable swap.

```css
/* Bad */
.btn { background: #3b82f6; padding: 16px; }

/* Good */
:root { --brand: #3b82f6; --space-4: 1rem; }
.btn { background: var(--brand); padding: var(--space-4); }
```

### 4. Fixed heights on content containers

**Why it is wrong:** `height: 400px` on a container that holds text or dynamic content
clips overflow or leaves dead space the moment the content differs from the mock-up.
**The fix:** Let content size the box. Use `min-height` for a floor, and `padding` for
breathing room, so the container grows with its content.

### 5. Desktop-first with `max-width` overrides

**Why it is wrong:** Writing the large-screen layout first and stripping it back with
`max-width` queries produces more rules, more overrides, and more edge cases than the
reverse. The mobile experience becomes the exception path, which is where bugs hide.
**The fix:** Write mobile-first: simple base styles, then add complexity at `min-width`
breakpoints. The base is the simplest case and each query only adds.

### 6. Animating layout properties

**Why it is wrong:** Transitioning `width`, `height`, `top`, `left`, or `margin` forces
layout and paint on every frame, causing jank on low-end devices. See [performance](22-performance.md).
**The fix:** Animate only `transform` and `opacity`, which the compositor handles off the
main thread.

```css
/* Bad: triggers layout every frame */
.panel { transition: left 0.3s; left: 0; }
.panel.open { left: 300px; }

/* Good: compositor-only */
.panel { transition: transform 0.3s; transform: translateX(0); }
.panel.open { transform: translateX(300px); }
```

### 7. Removing focus outlines

**Why it is wrong:** `outline: none` (or `:focus { outline: 0 }`) leaves keyboard users
with no visible indication of where they are, an accessibility failure. See [accessibility](23-accessibility.md).
**The fix:** Style `:focus-visible` with a clear, high-contrast indicator. Never remove the
outline without providing a replacement.

### 8. Deeply nested preprocessor selectors

**Why it is wrong:** Nesting `&` four levels deep in Sass (or native CSS nesting) compiles
to a long, high-specificity descendant selector — the same problem as #2, hidden by the
source looking tidy.
**The fix:** Keep nesting to one level for state/modifiers only. Flatten structural styles
into their own single-class rules.

### 9. Layout logic in JavaScript

**Why it is wrong:** Measuring elements and setting `style.top`/`style.width` in JS
duplicates what CSS does natively, fights reflow, and breaks on resize and zoom.
**The fix:** Use Grid, Flexbox, `clamp()`, and [container queries](19-container-queries.md).
Declarative layout survives reflow without JS bookkeeping.

### 10. Append-only stylesheets

**Why it is wrong:** Never deleting old CSS — only adding overrides on top — makes the
bundle grow without bound and accumulates dead rules nobody dares remove.
**The fix:** Replace, don't stack. When changing a component, edit its rules and delete
what they supersede. Use coverage tooling to find and remove dead CSS.

## Common Mistakes

- Treating `!important` as a quick fix instead of a smell that points to a specificity problem.
- Copying a color or spacing value "just this once" and letting it become the sixth copy.
- Assuming the mock-up's content length is the only content length.
- Disabling a Stylelint rule inline rather than fixing the flagged pattern.

## AI Review Checklist

- Does the diff introduce any `!important` outside a documented utility layer?
- Are any selectors over-qualified or nested past one level, raising specificity?
- Are there magic numbers that should be tokens?
- Do any transitions animate layout properties instead of `transform`/`opacity`?
- Is any focus outline removed without a `:focus-visible` replacement?
- Does the change add overrides where it should have replaced the original rule?

## Related

- `knowledge/css/03-specificity.md`
- `knowledge/css/20-css-variables.md`
- `knowledge/css/30-engineering-principles.md`
- `knowledge/css/22-performance.md`
- `knowledge/css/23-accessibility.md`
