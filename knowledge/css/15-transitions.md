---
id: css/15-transitions
topic: css
slug: transitions
title: "Transitions"
type: doc
order: 15
status: ready
tags: [css, transitions]
related: [css/14-transforms, css/16-animations, css/22-performance, css/23-accessibility]
when_to_use: "Read before adding hover, focus, or state-change transitions that animate CSS property changes."
---
# Transitions

## Purpose

This document defines how to animate a change *between two states* with the `transition`
property: which properties animate, over what duration, with what timing curve, and after
what delay. It is written so an agent can add smooth state changes without hurting
performance or accessibility.

A transition interpolates a property from its old value to its new value when the value
changes (on hover, focus, class toggle, etc.). For continuous or multi-step motion that
runs on its own, use [animations](16-animations.md) instead.

## Why It Matters

Transitions are the most common animation on the web — every hover, focus ring, and
accordion uses them — so their defaults set the perceived quality and performance of the
whole UI. Two mistakes recur: transitioning `all` (which animates unintended, expensive
properties) and transitioning layout properties (which janks). Both are cheap to write
and expensive at runtime. Because transitions fire constantly, a bad default is felt on
every interaction.

## Core Principles

- **Only animatable properties transition.** Properties like `display` historically could
  not be interpolated; use `transition-behavior: allow-discrete` (or `@starting-style`)
  when animating to/from `display: none`.
- **Name the properties; never transition `all`.** `all` sweeps in properties you did not
  intend to animate, some of which force layout, and makes intent unclear.
- **Prefer transitioning `transform` and `opacity`** — they stay on the compositor.
  Transitioning `height`, `width`, `top`, or `margin` triggers layout each frame.
- **A transition needs a starting value in the base rule.** If the property is only set in
  the `:hover` state, there is nothing to interpolate from on the way out.
- **Duration is perception, not decoration.** 150–300ms feels responsive; over ~400ms
  feels sluggish for UI feedback.

## Best Practices

- List explicit properties: `transition: transform 200ms ease, opacity 200ms ease;` so
  only those animate and reviewers can see the intent.
- Use `ease-out` for elements entering/responding to input (fast start, gentle settle)
  and `ease-in` for elements leaving; linear feels mechanical for UI.
- Keep durations in the ~150–300ms range for hovers and toggles; reserve longer times for
  larger, deliberate movements.
- Put the `transition` declaration on the *base* state, not the `:hover` state, so it
  applies both entering and leaving the state.
- Honor `prefers-reduced-motion: reduce` by shortening or removing transitions, because
  motion can cause discomfort or nausea for some users.
- To collapse/expand height smoothly, animate `transform: scaleY()` or `grid-template-rows`
  (`0fr`→`1fr`), not `height: auto`, which cannot be interpolated directly.

## Examples

**Good Example** — explicit properties, base-state transition, reduced-motion aware

```css
.button {
  /* Declared on the base state so it applies on hover-in AND hover-out. Only
     compositor-friendly properties are named. */
  transition: transform 150ms ease-out, background-color 150ms ease-out;
  transform: scale(1);
  background-color: #2563eb;
}
.button:hover {
  transform: scale(1.03);   /* compositor-only: no layout */
  background-color: #1d4ed8;
}
@media (prefers-reduced-motion: reduce) {
  .button { transition-duration: 0.01ms; } /* effectively instant, no motion */
}
```

**Bad Example** — `all`, layout property, transition on the wrong state

```css
.button {
  width: 120px;
}
.button:hover {
  /* Declared only on :hover, so there is no smooth transition back out.
     `all` animates every changed property, and `width` forces layout each
     frame — jank plus unintended animations. */
  transition: all 150ms ease;
  width: 140px;
}
```

## Common Mistakes

- Using `transition: all`, which animates unexpected and expensive properties.
- Transitioning layout properties (`width`, `height`, `top`, `margin`) instead of
  `transform`, causing per-frame layout.
- Declaring the transition only in the `:hover` rule, so the exit is instant.
- Setting durations so long the UI feels laggy, or so short the change is not perceived.
- Trying to transition `height: auto` and getting no animation.
- Ignoring `prefers-reduced-motion`.

## Production Tips

- To reveal an element from `display: none`, pair the transition with
  `transition-behavior: allow-discrete` and `@starting-style` so the entry animates from
  a defined initial value.
- When many elements share a transition, define it once in a utility class rather than
  repeating (and risking divergent durations) across components.

## AI Review Checklist

- Are transitioned properties named explicitly instead of `all`?
- Is the transition declared on the base state so it applies both directions?
- Are `transform`/`opacity` used instead of layout properties where possible?
- Are durations in a responsive range (~150–300ms) for UI feedback?
- Is `prefers-reduced-motion` handled?
- For height/reveal animations, is a compositor- or grid-based technique used instead of
  `height: auto`?

## Related

- `knowledge/css/14-transforms.md`
- `knowledge/css/16-animations.md`
- `knowledge/css/22-performance.md`
- `knowledge/css/23-accessibility.md`
