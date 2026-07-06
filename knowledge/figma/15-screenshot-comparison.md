# Screenshot Comparison

## Purpose

This document defines the standard process for comparing implemented pages with approved Figma designs using screenshots.

The objective is to detect visual differences objectively and consistently before code review, QA, or production deployment.

Screenshot comparison should validate the final implementation rather than replace manual review.

---

# Core Principle

Compare the rendered result, not assumptions.

A page should be evaluated using identical conditions so that only implementation differences remain.

---

# Comparison Workflow

Every comparison should follow this sequence.

```
Open Approved Figma
        ↓
Open Implemented Page
        ↓
Match Viewport
        ↓
Match Zoom Level
        ↓
Capture Screenshots
        ↓
Compare Layout
        ↓
Compare Components
        ↓
Document Differences
        ↓
Fix Issues
        ↓
Repeat Verification
```

---

# Step 1 — Prepare the Environment

Verify:

- correct branch is running;
- latest implementation is loaded;
- browser cache is cleared if necessary;
- required fonts are loaded;
- correct theme is active;
- required content exists.

The implementation should be reviewed in its intended environment.

---

# Step 2 — Match Viewport

Use the same viewport dimensions as the design whenever possible.

Typical breakpoints:

- Desktop
- Laptop
- Tablet
- Mobile

A mismatch in viewport size may produce misleading differences.

---

# Step 3 — Match Zoom

Verify:

- browser zoom is 100%;
- operating system scaling is understood;
- Figma zoom is appropriate for inspection.

Do not compare screenshots captured at different scales.

---

# Step 4 — Compare Page Structure

Review:

- section order;
- page hierarchy;
- containers;
- alignment;
- whitespace.

Large structural differences should be investigated before reviewing smaller details.

---

# Step 5 — Compare Components

Review every reusable component.

Examples:

- buttons;
- cards;
- navigation;
- forms;
- accordions;
- tabs;
- sliders;
- pricing tables;
- testimonials.

Every instance should remain visually consistent.

---

# Step 6 — Compare Typography

Verify:

- font family;
- font size;
- font weight;
- line height;
- letter spacing;
- text alignment;
- heading hierarchy.

Typography differences often indicate incorrect design token usage.

---

# Step 7 — Compare Spacing

Review:

- section spacing;
- component spacing;
- margins;
- padding;
- grid gaps.

Spacing should follow the approved design system.

---

# Step 8 — Compare Colors

Verify:

- backgrounds;
- text colors;
- borders;
- buttons;
- icons;
- shadows.

Always compare against approved design tokens rather than subjective visual impressions.

---

# Step 9 — Compare Responsive Layouts

Repeat the comparison for:

- Desktop
- Laptop
- Tablet
- Mobile

Review:

- stacking behavior;
- navigation;
- spacing;
- typography;
- image scaling.

Every breakpoint should be verified independently.

---

# Step 10 — Compare Interactions

Review interactive elements.

Examples:

- hover;
- focus;
- active;
- disabled;
- expanded;
- collapsed;
- loading.

Static screenshots alone are not sufficient for interaction verification.

---

# Recording Differences

Every identified issue should include:

- location;
- description;
- expected result;
- actual result;
- severity;
- recommended fix.

Clear documentation reduces unnecessary review cycles.

---

# Severity Levels

## Critical

Examples:

- broken layout;
- inaccessible functionality;
- missing content;
- unusable navigation.

Must be fixed before approval.

---

## Major

Examples:

- incorrect responsive layout;
- missing section;
- incorrect typography;
- incorrect spacing affecting usability.

Should be fixed before approval.

---

## Minor

Examples:

- alignment differences;
- inconsistent padding;
- incorrect icon size;
- small border-radius differences.

Fix whenever practical.

---

## Cosmetic

Examples:

- insignificant visual differences;
- decorative inconsistencies.

May be deferred if they do not affect usability or design consistency.

---

# AI Execution Checklist

## Investigation

☐ Compare overall layout.

☐ Compare sections.

☐ Compare components.

☐ Compare typography.

☐ Compare spacing.

☐ Compare colors.

☐ Compare responsiveness.

☐ Compare interactions.

---

## Verification

☐ Every difference has been documented.

☐ Severity has been assigned.

☐ Recommended fixes are clear.

☐ Final comparison confirms design accuracy.

---

# Common Mistakes

Avoid:

Comparing different viewport sizes.

Comparing different zoom levels.

Ignoring typography.

Ignoring spacing.

Ignoring responsive layouts.

Ignoring interaction states.

Approving pages without side-by-side comparison.

---

# Completion Criteria

Screenshot comparison is complete when:

- every supported breakpoint has been reviewed;
- visual differences have been documented;
- significant issues have been resolved;
- the implementation accurately reflects the approved design.

---

# Summary

Screenshot comparison provides an objective method for validating frontend implementations against approved designs.

When performed consistently, it improves design accuracy, reduces review iterations, and increases confidence before production deployment.