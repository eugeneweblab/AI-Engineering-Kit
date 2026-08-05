---
id: frontend/17-animations
topic: frontend
slug: animations
title: "Frontend Animations"
type: doc
order: 17
status: ready
tags: [frontend, animations, will-change, translateY, scroll, box-shadow, width]
related: [frontend/15-styling, frontend/08-performance, frontend/09-accessibility, frontend/16-css-architecture, frontend/10-responsive-design]
when_to_use: "Read before adding transitions, motion, or animated feedback to a UI."
---
# Frontend Animations

## Purpose

This document defines how to add motion to a UI without hurting performance or
accessibility: what to animate, how to keep it on the compositor, how to respect user
motion preferences, and when animation helps versus distracts. It gives an agent concrete
rules for transitions, keyframes, and entrance/exit motion.

Animation is a communication tool, not decoration. Its job is to show relationships,
provide feedback, and guide attention. Motion that does not serve one of those purposes is
noise that costs performance and can literally make users sick.

## Why It Matters

Motion runs on the same main thread as your app logic, and the browser must hit ~16ms per
frame to stay smooth. Animating the wrong properties — `width`, `top`, `box-shadow` —
forces layout and paint on every frame and produces visible jank on exactly the devices
that can least afford it. Beyond performance, motion is an accessibility concern with
medical weight: for users with vestibular disorders, large parallax and zoom animations can
trigger nausea and dizziness. And gratuitous animation delays interaction — a user waiting
400ms for a menu to "elegantly" slide in is a user you slowed down. Getting animation right
means it is fast, purposeful, and skippable.

## Core Principles

- **Animate only `transform` and `opacity` on the hot path.** These run on the compositor
  without triggering layout or paint. Animating `width`, `height`, `top`, or `margin`
  forces reflow every frame and janks.
- **Respect `prefers-reduced-motion`.** Users who request reduced motion must get a
  near-instant or crossfade alternative, not the full animation. This is non-negotiable.
- **Motion must have a purpose.** Every animation should communicate state, spatial
  relationship, or feedback. If you cannot name its purpose, remove it.
- **Keep it short and interruptible.** UI transitions belong in the ~150–300ms range;
  never block or delay a user action behind a decorative animation.
- **Never animate away meaning.** An element that fades out must remain accessible until it
  is truly gone; motion must not hide focus or content from assistive tech.

## Best Practices

- Use CSS `transition`/`@keyframes` for state changes and a purpose-built library (e.g.
  the Web Animations API or Motion) for orchestrated sequences; reserve JS `requestAnimationFrame`
  loops for cases the compositor cannot express.
- Wrap non-essential motion in `@media (prefers-reduced-motion: reduce)` and collapse it to
  an instant transition or a small crossfade.
- Trigger heavy animations off `transform: translate/scale` rather than positional or size
  properties; promote long-running animated layers with `will-change` sparingly (it costs
  memory) and remove it when the animation ends.
- Keep durations short (150–300ms for most UI, up to ~500ms for large surfaces) and use
  ease-out for entrances, ease-in for exits so motion feels physically grounded.
- Ensure animated elements never trap or hide focus: exit animations should not remove an
  element from the accessibility tree before the transition completes visually.
- Avoid animating during scroll on the main thread; prefer CSS scroll-driven animations or
  `IntersectionObserver`-gated triggers over `scroll` event handlers.
- Debounce/limit simultaneous animations; dozens of concurrent transitions saturate the
  compositor as surely as one bad property.

## Examples

**Good Example** — compositor-friendly, motion-preference-aware

```css
.panel {
  /* animate transform + opacity only: no layout, no paint, runs on the GPU */
  transition: transform 200ms ease-out, opacity 200ms ease-out;
  transform: translateY(0);
  opacity: 1;
}
.panel[data-state="entering"] {
  transform: translateY(8px);
  opacity: 0;
}

/* users who ask for less motion get an instant, non-moving alternative */
@media (prefers-reduced-motion: reduce) {
  .panel {
    transition-duration: 0.01ms; /* effectively instant, still swaps state */
    transform: none;
  }
}
```

**Bad Example** — layout-thrashing, ignores preferences, blocks the user

```css
.panel {
  /* animating top + width forces reflow + repaint every single frame → jank */
  transition: top 600ms linear, width 600ms linear, box-shadow 600ms linear;
  top: 0;
  width: 400px;
}
.menu:hover .panel {
  top: 40px;   /* long, non-interruptible; user waits 600ms to interact */
  width: 420px;
}
/* no prefers-reduced-motion branch: nausea-inducing for vestibular-sensitive users */
```

## Common Mistakes

- Animating `width`, `height`, `top`, `left`, or `box-shadow`, forcing layout/paint per frame.
- Shipping no `prefers-reduced-motion` alternative, ignoring an accessibility requirement.
- Long durations (500ms+) on frequent UI transitions that make the app feel sluggish.
- Blocking or delaying a user interaction behind a decorative entrance animation.
- Leaving `will-change` on permanently, wasting GPU memory and sometimes causing blurriness.
- Driving scroll animations from `scroll` event handlers on the main thread, causing jank.
- Removing an element from the DOM/accessibility tree before its exit animation finishes,
  cutting off screen-reader users.

## Production Tips

- Profile animations with the browser's Performance panel and watch for "layout" and
  "paint" work inside animation frames — a green-only compositor track is the goal.
- Prefer CSS scroll-driven animations (`animation-timeline: scroll()/view()`) over JS scroll
  handlers where supported; they run off the main thread.
- Provide a global "reduce motion" honoring at the design-token level (a `--motion-scale`
  variable) so the whole app can dial motion down consistently.

## AI Review Checklist

- Do hot-path animations use only `transform` and `opacity` (no layout-triggering props)?
- Is there a `prefers-reduced-motion: reduce` branch that provides an instant/crossfade path?
- Does every animation serve a nameable purpose (feedback, relationship, attention)?
- Are UI transition durations short (~150–300ms) and non-blocking to interaction?
- Is `will-change` used sparingly and removed after the animation completes?
- Are scroll-linked effects driven off the main thread rather than `scroll` handlers?
- Do exit animations keep content accessible until the element is actually removed?

## Related

- `knowledge/frontend/15-styling.md`
- `knowledge/frontend/08-performance.md`
- `knowledge/frontend/09-accessibility.md`
- `knowledge/frontend/16-css-architecture.md`
- `knowledge/frontend/10-responsive-design.md`
