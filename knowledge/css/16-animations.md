---
id: css/16-animations
topic: css
slug: animations
title: "CSS Animations"
type: doc
order: 16
status: ready
tags: [css, animations, "@keyframes", translateY, opacity, transform, transition, rotate]
related: [css/15-transitions, css/14-transforms, css/22-performance, css/23-accessibility]
when_to_use: "Read before building keyframe animations, loops, spinners, or multi-step motion."
---
# CSS Animations

## Purpose

This document defines how to build multi-step, self-running motion with `@keyframes` and
the `animation` property: keyframe stops, timing, iteration, direction, and fill mode. It
is written so an agent can author animations that are performant, accessible, and do not
block or distract users.

Use an animation when motion has more than two states, runs on its own, loops, or must
start without a user interaction. For a simple two-state change on hover or focus, a
[transition](15-transitions.md) is simpler and preferred.

## Why It Matters

Animations run continuously and often loop, so a wasteful one costs CPU/GPU for the entire
time it is visible — draining battery and dropping frames on low-end devices. They are
also the most likely CSS feature to harm users directly: flashing or large looping motion
can trigger vestibular disorders or seizures. And an animation applied to critical content
can hide it if the fill mode or initial state is wrong. Correct animation work is as much
about restraint and accessibility as about visual polish.

## Core Principles

- **Animate `transform` and `opacity`.** These composite without layout or repaint, so a
  loop stays cheap. Animating layout properties in a loop is the classic jank source.
- **`prefers-reduced-motion` is mandatory for looping/large motion,** not optional. Provide
  a reduced or removed variant; it is an accessibility requirement, not a nicety.
- **Fill mode controls the resting state.** Without `animation-fill-mode: forwards`, an
  element snaps back to its pre-animation styles when the animation ends.
- **Keyframe percentages are stops, not keyed to real time.** `duration` maps `0%`→`100%`
  onto elapsed time; the same keyframes can run fast or slow.
- **Infinite animations never idle.** An `infinite` spinner keeps the compositor busy even
  when off-screen unless you pause it; hide or pause what is not visible.

## Best Practices

- Define motion with `transform`/`opacity` keyframes so each frame composites instead of
  triggering layout.
- Always ship a `@media (prefers-reduced-motion: reduce)` block that disables or tones down
  non-essential animation.
- Never flash content more than 3 times per second (WCAG 2.3.1) — flashing above that
  threshold can induce seizures.
- Use `animation-fill-mode: forwards` when the element should stay at its final keyframe;
  use `both` when it also needs the `from` state applied during any delay.
- Pause off-screen or hidden loops (`animation-play-state: paused`, or toggle a class via
  `IntersectionObserver`) to stop burning cycles on invisible motion.
- Prefer the `animation` shorthand but keep the order memorable: name, duration, timing,
  delay, iteration-count, direction, fill-mode, play-state.

## Examples

**Good Example** — compositor-only spinner, correct fill, reduced-motion fallback

```css
@keyframes spin {
  to { transform: rotate(360deg); } /* only transform animates → composited */
}
.spinner {
  animation: spin 800ms linear infinite;
}
@keyframes fade-in-up {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
.toast {
  /* forwards keeps the toast at opacity:1 after the animation ends. */
  animation: fade-in-up 240ms ease-out forwards;
}
@media (prefers-reduced-motion: reduce) {
  .spinner { animation-duration: 1600ms; } /* slow, non-distracting */
  .toast   { animation: none; opacity: 1; } /* show instantly, no motion */
}
```

**Bad Example** — layout animation in a loop, no fill, no reduced-motion

```css
@keyframes pulse {
  /* Animating width/margin recalculates layout every frame, forever. */
  0%   { width: 40px; margin-left: 0; }
  50%  { width: 60px; margin-left: 10px; }
  100% { width: 40px; margin-left: 0; }
}
.dot {
  animation: pulse 1s infinite; /* infinite layout thrash, no reduced-motion opt-out */
}
```

## Common Mistakes

- Animating layout properties (`width`, `height`, `margin`, `top`) in a loop, guaranteeing
  continuous jank.
- Shipping animation with no `prefers-reduced-motion` fallback.
- Flashing content faster than 3Hz, risking seizures.
- Forgetting `animation-fill-mode`, so the element visibly snaps back at the end.
- Leaving `infinite` animations running off-screen, wasting battery.
- Reaching for `@keyframes` where a two-state `transition` would be simpler and cheaper.

## Production Tips

- For entrance animations tied to scroll, prefer the CSS `animation-timeline: view()` /
  scroll-driven animations where supported, so motion is driven by scroll position without
  a JS scroll handler.
- Name keyframes and animations semantically (`fade-in-up`, not `anim1`) so they are
  reusable and self-documenting across components.

## AI Review Checklist

- Do keyframes animate `transform`/`opacity` rather than layout properties?
- Is there a `prefers-reduced-motion: reduce` fallback for non-essential motion?
- Is no content flashing more than 3 times per second?
- Is `animation-fill-mode` set so the resting state is intentional?
- Are infinite/off-screen animations paused or hidden to save resources?
- Would a simpler `transition` achieve the same two-state effect?

## Related

- `knowledge/css/15-transitions.md`
- `knowledge/css/14-transforms.md`
- `knowledge/css/22-performance.md`
- `knowledge/css/23-accessibility.md`
