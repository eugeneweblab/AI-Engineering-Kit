# Implementation Definition of Done

## Purpose

This document defines the mandatory Definition of Done (DoD) for implementing Figma designs.

The objective is to establish a consistent completion standard for all frontend implementations, regardless of framework, CMS, or AI coding assistant.

An implementation is considered complete only when every requirement in this document has been satisfied.

---

# Core Principle

Code completion is not task completion.

A feature is complete only after implementation, verification, review, testing, and documentation have been finished.

---

# Definition of Done Workflow

Every implementation must complete the following stages.

```
Requirements
        ↓
Implementation
        ↓
Self Review
        ↓
Design Verification
        ↓
Accessibility Review
        ↓
Responsive Review
        ↓
Performance Review
        ↓
Code Review
        ↓
Testing
        ↓
Ready for Production
```

No stage may be skipped.

---

# Stage 1 — Requirements

Verify:

☐ Requirements are fully understood.

☐ Business objectives are satisfied.

☐ Acceptance criteria are complete.

☐ Design has been reviewed.

☐ Open questions have been resolved.

Implementation should never begin with unresolved requirements.

---

# Stage 2 — Implementation

Verify:

☐ Existing components reused.

☐ Project architecture respected.

☐ Semantic HTML used.

☐ Dynamic content implemented correctly.

☐ Design system followed.

☐ No unnecessary code introduced.

---

# Stage 3 — Design Verification

Compare implementation with the approved Figma design.

Verify:

☐ Layout.

☐ Typography.

☐ Colors.

☐ Spacing.

☐ Components.

☐ Icons.

☐ Images.

☐ Responsive behavior.

No significant visual differences should remain.

---

# Stage 4 — Accessibility

Verify:

☐ Semantic HTML.

☐ Heading hierarchy.

☐ Image accessibility.

☐ Form accessibility.

☐ Keyboard navigation.

☐ Focus indicators.

☐ Color contrast.

Accessibility issues must be resolved before completion.

---

# Stage 5 — Responsive Verification

Review:

☐ Desktop.

☐ Laptop.

☐ Tablet.

☐ Mobile.

Verify:

☐ Layout.

☐ Navigation.

☐ Typography.

☐ Images.

☐ Forms.

☐ Interactive components.

Every supported breakpoint must be verified.

---

# Stage 6 — Performance

Verify:

☐ Images optimized.

☐ Assets minimized.

☐ Lazy loading applied where appropriate.

☐ Unused code removed.

☐ Duplicate code avoided.

☐ Performance remains acceptable.

Implementation quality includes runtime performance.

---

# Stage 7 — Code Quality

Verify:

☐ Naming conventions followed.

☐ Consistent formatting.

☐ No dead code.

☐ No duplicated logic.

☐ Readable implementation.

☐ Maintainable architecture.

Code should be understandable without additional explanation.

---

# Stage 8 — Testing

Verify:

☐ Manual testing completed.

☐ Existing functionality unaffected.

☐ Interactive behavior verified.

☐ Error scenarios reviewed.

☐ Browser compatibility reviewed.

☐ Regression testing completed.

Testing confirms that implementation works as intended.

---

# Stage 9 — Documentation

Verify:

☐ Required documentation updated.

☐ Comments added only when necessary.

☐ New reusable components documented.

☐ Configuration changes documented.

Documentation should remain synchronized with implementation.

---

# Stage 10 — Final Review

Before marking the task complete, confirm:

☐ Requirements satisfied.

☐ Design accurately implemented.

☐ Accessibility verified.

☐ Responsive behavior verified.

☐ Performance acceptable.

☐ Testing completed.

☐ Documentation updated.

☐ Ready for production.

---

# AI Completion Report

Before finishing a task, AI should summarize:

## Work Completed

Describe:

- implemented sections;
- modified files;
- reused components;
- new components.

---

## Verification Summary

Confirm:

- design accuracy;
- responsive review;
- accessibility review;
- performance review;
- testing status.

---

## Known Limitations

Document any remaining issues.

Examples:

- pending backend API;
- missing design assets;
- blocked dependencies.

Do not hide known limitations.

---

# AI Execution Checklist

## Investigation

☐ Requirements reviewed.

☐ Existing implementation reviewed.

☐ Reusable components identified.

---

## Verification

☐ Design matches Figma.

☐ Accessibility verified.

☐ Responsive verified.

☐ Performance reviewed.

☐ Code reviewed.

☐ Testing completed.

☐ Documentation updated.

---

# Common Mistakes

Avoid:

Considering coding the end of the task.

Skipping responsive testing.

Skipping accessibility review.

Ignoring existing reusable components.

Leaving TODO comments without explanation.

Ignoring performance regressions.

Marking incomplete work as finished.

---

# Completion Criteria

Implementation is complete only when:

- all functional requirements have been met;
- the design has been accurately reproduced;
- responsive behavior has been verified;
- accessibility requirements have been satisfied;
- performance remains acceptable;
- testing has been completed;
- documentation has been updated;
- the feature is ready for production deployment.

---

# Summary

A consistent Definition of Done creates predictable engineering quality.

By requiring implementation, verification, testing, documentation, and review, every completed feature reaches the same production-ready standard regardless of who—or what—implemented it.