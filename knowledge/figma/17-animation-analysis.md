# Animation Analysis

## Purpose

This document defines the standard process for analyzing animations and motion behavior from Figma before implementation.

The objective is to understand the intent of motion, identify reusable animation patterns, and implement animations that improve usability without reducing performance or accessibility.

Animations should communicate state and improve the user experience.

They should never exist solely for decoration.

---

# Core Principle

Understand why an animation exists before deciding how to implement it.

Every animation should have a functional purpose.

---

# Animation Review Workflow

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

# Step 1 — Identify Motion

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

# Step 2 — Determine Purpose

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

# Step 3 — Classify Animation

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

# Step 4 — Analyze Trigger

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

# Step 5 — Analyze Timing

Review:

- duration;
- delay;
- easing;
- sequence;
- repetition.

Animations should feel responsive without delaying user interaction.

---

# Step 6 — Analyze Relationships

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

# Step 7 — Responsive Behavior

Verify animation behavior across:

- Desktop;
- Laptop;
- Tablet;
- Mobile.

Large animations may require simplified behavior on smaller devices.

---

# Step 8 — Accessibility

Review:

- reduced motion support;
- keyboard interaction;
- focus visibility;
- flashing content;
- motion sensitivity.

Respect user preferences such as `prefers-reduced-motion`.

Accessibility takes priority over visual effects.

---

# Step 9 — Performance

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

# Step 10 — Implementation Strategy

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

# WordPress Considerations

For WordPress projects:

- avoid page-specific animation code;
- reuse shared animation utilities;
- avoid hardcoding animation values;
- ensure animations work inside reusable templates and blocks.

Animations should remain independent of page content.

---

# Divi Considerations

When using Divi:

- prefer existing animation capabilities when appropriate;
- avoid stacking multiple animation systems;
- avoid excessive scroll animations;
- use custom code only when native functionality cannot achieve the required behavior.

---

# AI Execution Checklist

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

# Common Mistakes

Avoid:

Adding unnecessary animations.

Animating layout properties excessively.

Ignoring reduced motion preferences.

Using JavaScript when CSS is sufficient.

Creating inconsistent animation timing.

Combining multiple animation libraries.

Blocking user interaction with animations.

---

# Completion Criteria

Animation analysis is complete when:

- every animation has been documented;
- implementation strategy has been selected;
- accessibility requirements have been considered;
- performance impact has been evaluated;
- reusable animation patterns have been identified.

---

# Summary

Effective animation enhances usability by communicating change, guiding attention, and providing feedback.

A disciplined analysis process ensures that motion remains purposeful, accessible, performant, and consistent throughout the project.