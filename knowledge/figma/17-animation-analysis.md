---
id: figma/17-animation-analysis
topic: figma
slug: animation-analysis
title: "Animation Analysis"
type: doc
order: 17
status: ready
tags: [figma, animation-analysis, prefers-reduced-motion, "@media", media, transform-origin, animation-iteration-count, animation-duration]
related: [figma/02-layout-analysis, css/16-animations, accessibility/14-motion-and-animation]
when_to_use: "Read before implementing animations or motion from a Figma design, to understand their intent and reuse patterns."
---
# Animation Analysis

## Purpose

This document defines the standard process for analyzing animations and motion behavior from Figma before implementation.

The objective is to understand the intent of motion, identify reusable animation patterns, and implement animations that improve usability without reducing performance or accessibility.

Animations should communicate state and improve the user experience.

They should never exist solely for decoration.

---

## Core Principle

Understand why an animation exists before deciding how to implement it.

Every animation should have a functional purpose.

---

## Animation Review Workflow

Analyze animations using the following sequence.

```
Identify Motion
        ↓
Determine Purpose
        ↓
Classify Animation
        ↓
Analyze Timing
        ↓
Analyze Trigger
        ↓
Review Responsive Behavior
        ↓
Review Accessibility
        ↓
Select Implementation Strategy
```

---

## Step 1 — Identify Motion

Review the complete design.

Identify:

- page transitions;
- section transitions;
- hover effects;
- focus effects;
- loading animations;
- scrolling animations;
- modal animations;
- menu animations;
- carousel transitions;
- accordion animations.

Document every animation before implementation.

---

## Step 2 — Determine Purpose

Every animation should have a reason.

Typical purposes include:

- drawing attention;
- indicating interaction;
- communicating system status;
- reinforcing hierarchy;
- providing feedback;
- improving orientation.

If no purpose exists, reconsider implementing the animation.

---

## Step 3 — Classify Animation

Classify each animation.

Examples:

- hover animation;
- page transition;
- fade;
- slide;
- scale;
- rotation;
- opacity;
- transform;
- loading indicator;
- progress animation.

Different animation types may require different implementation strategies.

---

## Step 4 — Analyze Trigger

Determine what starts the animation.

Examples:

- page load;
- hover;
- focus;
- click;
- scroll;
- viewport visibility;
- keyboard interaction;
- state change.

Every trigger should be intentional.

---

## Step 5 — Analyze Timing

Review:

- duration;
- delay;
- easing;
- sequence;
- repetition.

Animations should feel responsive without delaying user interaction.

---

## Step 6 — Analyze Relationships

Determine whether animations depend on one another.

Examples:

Navigation opens

↓

Overlay fades

↓

Menu slides

↓

Focus moves

Coordinated animations should remain synchronized.

---

## Step 7 — Responsive Behavior

Verify animation behavior across:

- Desktop;
- Laptop;
- Tablet;
- Mobile.

Large animations may require simplified behavior on smaller devices.

---

## Step 8 — Accessibility

Review:

- reduced motion support;
- keyboard interaction;
- focus visibility;
- flashing content;
- motion sensitivity.

Respect user preferences such as `prefers-reduced-motion`.

Accessibility takes priority over visual effects.

---

## Step 9 — Performance

Prefer animations that use:

- opacity;
- transform.

Avoid animating properties that trigger unnecessary layout recalculations.

Review:

- animation frequency;
- simultaneous animations;
- unnecessary JavaScript;
- repaint cost.

Performance should never be sacrificed for decorative effects.

---

## Step 10 — Implementation Strategy

Choose the simplest solution that satisfies the design.

Preferred order:

```
CSS Transition
        ↓
CSS Animation
        ↓
Native Browser APIs
        ↓
Project Animation Library
        ↓
Custom JavaScript
```

Avoid introducing additional dependencies unless justified.

---

## WordPress Considerations

For WordPress projects:

- avoid page-specific animation code;
- reuse shared animation utilities;
- avoid hardcoding animation values;
- ensure animations work inside reusable templates and blocks.

Animations should remain independent of page content.

---

## Divi Considerations

When using Divi:

- prefer existing animation capabilities when appropriate;
- avoid stacking multiple animation systems;
- avoid excessive scroll animations;
- use custom code only when native functionality cannot achieve the required behavior.

---

## AI Execution Checklist

## Investigation

☐ Every animation identified.

☐ Purpose documented.

☐ Trigger identified.

☐ Timing reviewed.

☐ Responsive behavior reviewed.

☐ Accessibility reviewed.

---

## Planning

☐ Appropriate implementation selected.

☐ Existing animation utilities reviewed.

☐ Performance considered.

☐ Reduced motion supported.

---

## Verification

☐ Animation matches design intent.

☐ Motion remains smooth.

☐ Keyboard interaction preserved.

☐ Accessibility requirements satisfied.

☐ Performance remains acceptable.

---

## Common Mistakes

Avoid:

Adding unnecessary animations.

Animating layout properties excessively.

Ignoring reduced motion preferences.

Using JavaScript when CSS is sufficient.

Creating inconsistent animation timing.

Combining multiple animation libraries.

Blocking user interaction with animations.

---

## Examples

**Good Example** — durations and easing recorded as tokens, motion made optional

```text
Smart Animate: Card / collapsed → Card / expanded
  Property   height 88 → 240
  Duration   240 ms
  Easing     Ease Out  → cubic-bezier(0, 0, 0.2, 1)
  Trigger    on click
  Purpose    reveals the detail; not decorative
```

```css
:root {
	--motion-fast: 120ms;
	--motion-base: 240ms;
	--motion-ease-out: cubic-bezier(0, 0, 0.2, 1);
}

.card__details {
	overflow: hidden;
	/* Animating a composited property; height would trigger layout on every frame. */
	transform-origin: top;
	transition: grid-template-rows var(--motion-base) var(--motion-ease-out);
}

/* Respect the operating-system setting. This is a correctness requirement,
   not a nicety: motion triggers nausea and migraines for some people. */
@media (prefers-reduced-motion: reduce) {
	*, *::before, *::after {
		animation-duration: 0.01ms !important;
		animation-iteration-count: 1 !important;
		transition-duration: 0.01ms !important;
	}
}
```

**Bad Example** — durations invented per component, layout animated, no opt-out

```css
.card__details {
	/* Animating height and top forces layout and paint on every frame; on a long
	   list this drops frames on mid-range hardware. */
	transition: height 0.35s ease-in-out, top 0.35s ease-in-out;
}

.banner {
	transition: all 500ms;      /* `all` animates properties nobody intended */
}

.modal {
	animation: bounce 800ms infinite;   /* runs forever, ignores the OS setting */
}
```

Three durations, three easings, none from the design, and no `prefers-reduced-motion` block
anywhere in the stylesheet.

---

## Completion Criteria

Animation analysis is complete when:

- every animation has been documented;
- implementation strategy has been selected;
- accessibility requirements have been considered;
- performance impact has been evaluated;
- reusable animation patterns have been identified.

---

## Summary

Effective animation enhances usability by communicating change, guiding attention, and providing feedback.

A disciplined analysis process ensures that motion remains purposeful, accessible, performant, and consistent throughout the project.

## Related

- `knowledge/figma/02-layout-analysis.md`
- `knowledge/css/16-animations.md`
- `knowledge/accessibility/14-motion-and-animation.md`
