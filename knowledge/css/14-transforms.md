---
id: css/14-transforms
topic: css
slug: transforms
title: "Transforms"
type: doc
order: 14
status: ready
tags: [css, transforms, transform, transform-origin, rotate, left, translate, translateX]
related: [css/15-transitions, css/16-animations, css/22-performance, css/05-positioning]
when_to_use: "Read before translating, scaling, rotating, or 3D-transforming elements, or animating position."
---
# Transforms

## Purpose

This document defines how to move, scale, rotate, and skew elements with the `transform`
property (and the individual `translate`/`rotate`/`scale` properties), including 2D and
3D transforms and the stacking they create. It is written so an agent can transform
elements without triggering layout thrash or breaking accessibility.

Transforms change how an element is *painted*, not the layout box it occupies. The
element still reserves its original space; neighbors do not move. That single fact is why
transforms are the correct tool for animating motion — see
[transitions](15-transitions.md) and [animations](16-animations.md).

## Why It Matters

`transform` and `opacity` are the only two properties the browser can animate on the
compositor thread — without recalculating layout or repainting. Animating `left`, `top`,
`width`, or `margin` instead forces layout on every frame, which janks on any non-trivial
page. Choosing `transform` over layout properties is often the single biggest performance
decision in an animation. Transforms also create stacking contexts and containing blocks,
which can quietly change how `position: fixed` children and `z-index` behave.

## Core Principles

- **Transforms do not affect layout.** The element's reserved space is unchanged;
  surrounding content does not reflow. Use this to animate motion cheaply.
- **Animate `transform` and `opacity`, not layout properties.** They stay on the
  compositor; `width`/`left`/`margin` trigger layout and repaint every frame.
- **Order matters and is right-to-left in effect.** `translate(x) rotate(45deg)` moves
  then rotates; swapping them gives a different result.
- **Any non-`none` transform creates a stacking context and a containing block.** A
  `position: fixed` descendant becomes fixed relative to the transformed ancestor, not
  the viewport — a frequent surprise.
- **3D transforms need a `perspective`** on the parent (or in the function) to look 3D;
  without it, rotations look flat.

## Best Practices

- Use `transform: translate()` to move things during animation instead of `top`/`left`,
  because translate is compositor-only and does not trigger layout.
- Prefer the individual `translate`, `rotate`, and `scale` properties (widely supported
  since 2022) when you need to animate one axis independently without clobbering the
  others in a single `transform` string.
- Set `transform-origin` explicitly when rotating or scaling; the default is the element
  center, which is often not the pivot you want.
- Add `will-change: transform` only right before a known animation and remove it after —
  leaving it on permanently wastes memory by keeping layers alive.
- Respect `prefers-reduced-motion`: gate large translate/scale animations behind a media
  query so motion-sensitive users are not affected.
- Avoid non-integer scale factors on text where crispness matters; scaling can blur
  rasterized content.

## Examples

**Good Example** — compositor-friendly motion, explicit origin, reduced-motion aware

```css
.panel {
  /* translate/opacity animate on the compositor: no layout, no repaint per frame */
  transition: transform 200ms ease-out, opacity 200ms ease-out;
  transform: translateX(0);
}
.panel.is-hidden {
  transform: translateX(100%); /* slides out without reflowing siblings */
  opacity: 0;
}
.badge {
  transform-origin: top right; /* pivot from the corner, not the center */
  transform: rotate(12deg);
}
@media (prefers-reduced-motion: reduce) {
  .panel { transition: none; } /* honor users who opt out of motion */
}
```

**Bad Example** — animating layout properties, layout thrash every frame

```css
.panel {
  position: relative;
  /* Animating `left` recalculates layout on every frame → jank, especially
     on mobile or with many elements. */
  transition: left 200ms ease-out;
  left: 0;
}
.panel.is-hidden {
  left: 100%; /* moves the box, forcing reflow of the document each frame */
}
```

## Common Mistakes

- Animating `top`/`left`/`width`/`margin` for motion instead of `transform`, causing
  per-frame layout and dropped frames.
- Being surprised that a `position: fixed` child stops tracking the viewport because an
  ancestor has a `transform` (which made it the containing block).
- Forgetting `transform-origin`, so a rotation pivots from the center unexpectedly.
- Leaving `will-change: transform` on many elements permanently, bloating GPU memory.
- Omitting `perspective`, so 3D rotations render flat.
- Ignoring `prefers-reduced-motion`, causing discomfort for motion-sensitive users.

## Production Tips

- If a transformed element looks blurry, check for a fractional `translate` (e.g.
  `translateX(0.5px)`); round to whole pixels or use `translateZ(0)` to promote a layer.
- Combine multiple animated transforms into one `transform` value rather than nesting
  transformed wrappers, which multiplies stacking contexts.

## AI Review Checklist

- Are motion animations using `transform`/`opacity` rather than layout properties?
- Is `transform-origin` set explicitly wherever rotation or scaling is used?
- Is `will-change` scoped to the animation and removed afterward, not global?
- Are `position: fixed` descendants checked against transformed ancestors?
- Do 3D transforms declare a `perspective`?
- Is `prefers-reduced-motion` honored for non-trivial motion?

## Related

- `knowledge/css/15-transitions.md`
- `knowledge/css/16-animations.md`
- `knowledge/css/22-performance.md`
- `knowledge/css/05-positioning.md`
