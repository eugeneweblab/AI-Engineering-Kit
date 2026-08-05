---
id: accessibility/14-motion-and-animation
topic: accessibility
slug: motion-and-animation
title: "Motion And Animation"
type: doc
order: 14
status: ready
tags: [accessibility, motion-and-animation, translateX, prefers-reduced-motion, "@keyframes", translateY, "@media", media]
related: [accessibility/13-responsive-accessibility, accessibility/15-media, accessibility/05-focus-management, accessibility/19-live-regions, accessibility/16-dialogs]
when_to_use: "Read before adding any animation, transition, auto-scroll, parallax, carousel, or auto-playing motion."
---
# Motion And Animation

## Purpose

This document defines how to add motion without harming users who are sensitive to it.
Animation can cause real physical harm — nausea, dizziness, migraine, and in the worst
case seizures — and it can obstruct users who need to read at their own pace. The goal
is motion that is **optional, brief, and safe by default**.

It maps to WCAG **2.3.1 Three Flashes**, **2.2.2 Pause, Stop, Hide**, and **2.3.3
Animation from Interactions**, and is written so an agent honoring
`prefers-reduced-motion` can add transitions without triggering any of them.

## Why It Matters

Motion is not a cosmetic concern. Content that flashes more than three times per second
can trigger seizures in people with photosensitive epilepsy — this is a documented
harm, not a preference. Large parallax and full-screen transitions provoke vestibular
disorders: the same motion sickness you feel on a boat, induced by a scroll. Auto-playing
carousels and marquees move content out from under users who read slowly or use a screen
magnifier, so they can never finish a sentence.

Unlike most accessibility issues, the fix is cheap and the operating system already
tells you the user's preference — you only have to listen for it.

## Core Principles

- **Respect `prefers-reduced-motion`.** The OS-level setting is an explicit request.
  Reduce or remove non-essential animation when it is set — this is the single most
  important rule in this document.
- **Nothing flashes more than three times per second.** No exceptions; this prevents
  seizures (WCAG 2.3.1).
- **Anything that moves, blinks, or scrolls automatically for more than 5 seconds must
  be pausable, stoppable, or hideable** by the user (WCAG 2.2.2).
- **Motion is decoration, not information.** Never convey state (loading, success,
  error) through animation alone; pair it with text or an accessible status.
- **Default to still.** Prefer opt-in motion. If motion is essential (e.g., a progress
  indicator), keep it small and non-flashing.

## Best Practices

- Wrap non-essential animation in `@media (prefers-reduced-motion: reduce)` and disable
  or shorten it there. Provide the reduced path explicitly; do not rely on the animation
  being subtle.
- Keep transitions short (typically under ~200ms) and confined to small elements; avoid
  large translate/scale moves across the viewport.
- Give carousels, marquees, and auto-advancing content a visible pause/stop control, and
  do not restart on hover/focus alone.
- Never auto-play video or animated backgrounds with sound; see [media](15-media.md).
- Avoid parallax and full-viewport scroll-jacking; if used, disable them under reduced
  motion.
- Announce state changes with text or a [live region](19-live-regions.md), so a spinner
  is not the only signal that something is happening.
- Set the reduced-motion default at the top of your CSS so every new animation inherits
  it unless explicitly overridden.

## Examples

**Good Example** — motion honors the user's OS preference

```css
.card {
  transition: transform 150ms ease; /* small, brief motion by default */
}
.card:hover { transform: translateY(-4px); }

/* When the user asks for reduced motion, remove transitions and animations
   globally. This is a single, robust guard that catches every animation,
   including ones added later, instead of relying on each author to remember. */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

**Bad Example** — infinite motion, no preference check, no pause control

```css
/* Auto-scrolls forever, ignores prefers-reduced-motion, and offers no way
   to stop it. This can induce nausea and moves content out from under
   slow readers — a WCAG 2.2.2 failure. */
.ticker {
  animation: scroll 8s linear infinite;
}
@keyframes scroll { from { transform: translateX(0); } to { transform: translateX(-100%); } }
```

## Common Mistakes

- Adding animations with no `prefers-reduced-motion` fallback.
- Auto-playing carousels or marquees with no pause/stop/hide control.
- Content that flashes or strobes faster than three times per second.
- Using a spinner or animated checkmark as the *only* signal of loading or success.
- Parallax or scroll-jacking that hijacks the user's scroll and induces motion sickness.
- Restarting or speeding up motion on hover/focus, defeating the user's attempt to read.

## Production Tips

- Emulate reduced motion in DevTools (Rendering panel) and verify no essential motion
  remains before shipping.
- In `matchMedia('(prefers-reduced-motion: reduce)')`, gate JavaScript-driven animation
  (e.g., scroll libraries, confetti) — CSS media queries do not cover JS animation.

## AI Review Checklist

- Is every non-essential animation disabled or reduced under `prefers-reduced-motion`?
- Does any content flash more than three times per second? (Must be no.)
- Do auto-moving elements longer than 5s have a pause, stop, or hide control?
- Is state (loading/success/error) conveyed by text or a live region, not motion alone?
- Is JS-driven motion also gated on the reduced-motion media query?
- Are large viewport-scale movements (parallax, full-screen transitions) avoided or
  disabled under reduced motion?

## Related

- `knowledge/accessibility/13-responsive-accessibility.md`
- `knowledge/accessibility/15-media.md`
- `knowledge/accessibility/05-focus-management.md`
- `knowledge/accessibility/19-live-regions.md`
- `knowledge/accessibility/16-dialogs.md`
