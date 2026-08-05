---
id: wordpress/98-production-checklist
topic: wordpress
slug: production-checklist
title: "WordPress Production Checklist"
type: doc
order: 98
status: ready
tags: [wordpress, production-checklist]
related: []
when_to_use: "Read before considering a WordPress task complete to verify all mandatory checks."
---
# WordPress Production Checklist

## Purpose

This document defines the mandatory checklist that every AI coding agent must complete before considering a WordPress task finished.

The checklist is intentionally independent of any specific AI model and applies equally to Cursor, Claude Code, Codex, Copilot, Gemini, Cline, and future coding assistants.

Completing this checklist reduces regressions, architectural inconsistencies, duplicated code, and incomplete implementations.

---

## Core Principle

A task is not complete when the code compiles.

A task is complete when it integrates correctly into the existing project, satisfies the requirements, and does not introduce unnecessary technical debt.

---

## Phase 1 — Understand the Task

Before writing code verify:

☐ Business requirements are understood.

☐ Expected user behavior is understood.

☐ Expected administrator behavior is understood.

☐ Acceptance criteria are clear.

☐ Missing information has been identified.

Never implement features based on assumptions.

---

## Phase 2 — Understand the Existing Project

Before creating anything verify:

☐ Existing architecture has been reviewed.

☐ Similar implementations have been located.

☐ Existing services have been reviewed.

☐ Existing helpers have been reviewed.

☐ Existing templates have been reviewed.

☐ Existing components have been reviewed.

☐ Existing REST endpoints have been reviewed.

Always search before creating.

---

## Phase 3 — Architecture

Verify:

☐ The implementation follows the project's architecture.

☐ Responsibilities remain separated.

☐ Business logic is not placed inside templates.

☐ Business logic is not placed inside hook callbacks.

☐ Business logic is reusable.

☐ New files are placed in the correct directories.

Architecture should become stronger after every task.

---

## Phase 4 — WordPress Standards

Verify:

☐ WordPress APIs are used where appropriate.

☐ Existing hooks are reused.

☐ Core functionality is not duplicated.

☐ Naming follows project conventions.

☐ Internationalization has been considered.

☐ Coding style matches the project.

---

## Phase 5 — Security

Verify:

☐ Input validation has been implemented.

☐ Data sanitization has been implemented.

☐ Output escaping has been implemented.

☐ Capability checks are present.

☐ Nonces are verified when required.

☐ REST permission callbacks are implemented.

☐ Sensitive information is protected.

Security is never optional.

---

## Phase 6 — Performance

Verify:

☐ Duplicate queries were avoided.

☐ Existing data is reused.

☐ Caching opportunities were considered.

☐ Unnecessary assets were not added.

☐ Images are optimized.

☐ API responses contain only required data.

Performance should improve or remain unchanged.

---

## Phase 7 — Frontend

Verify:

☐ Responsive behavior is correct.

☐ Semantic HTML is used.

☐ Accessibility has been considered.

☐ Existing design system is respected.

☐ Existing components were reused.

☐ UI matches the design.

---

## Phase 8 — Backend

Verify:

☐ Business logic is isolated.

☐ Services remain cohesive.

☐ Error handling is implemented.

☐ Logging is appropriate.

☐ Configuration is centralized.

☐ Dependencies are explicit.

---

## Phase 9 — Code Quality

Verify:

☐ No duplicate functionality was created.

☐ Functions have a single responsibility.

☐ Classes have a single responsibility.

☐ Variable names are descriptive.

☐ Methods are easy to understand.

☐ Nesting is minimal.

☐ Magic values have been avoided.

Readable code is preferred over clever code.

---

## Phase 10 — Testing

Verify:

☐ Happy path was tested.

☐ Invalid input was tested.

☐ Permission failures were tested.

☐ Edge cases were considered.

☐ Existing functionality still works.

☐ Regression risks were reviewed.

---

## Phase 11 — Documentation

Verify:

☐ Public APIs are documented.

☐ Complex business logic is documented.

☐ Configuration changes are documented.

☐ README was updated if required.

☐ Comments explain "why", not "what".

---

## Final Self-Review

Before marking the task as complete ask:

- Would another engineer understand this implementation without explanation?
- Does the solution match the existing architecture?
- Is any duplicated code introduced?
- Can this feature be extended easily?
- Is every security concern addressed?
- Is performance acceptable?
- Would I confidently approve this in a code review?

If the answer to any question is "No", continue improving the implementation.

---

## Mandatory AI Output

Before completing the task, every AI agent should summarize:

## Requirements

- What was requested?

## Investigation

- Which files were reviewed?
- Which existing functionality was reused?

## Implementation

- Which files were modified?
- Which architectural decisions were made?

## Verification

- Which checks were performed?
- Which edge cases were considered?

## Remaining Work

- Are there known limitations?
- Are there recommended future improvements?

This summary should accompany every non-trivial implementation.

---

## Completion Criteria

A WordPress task is complete only if:

- all applicable checklist items have been verified;
- project architecture has been respected;
- WordPress standards have been followed;
- security has been reviewed;
- performance has been considered;
- documentation has been updated when necessary;
- the implementation is ready for production.

---

## Summary

This checklist is the minimum quality standard for all WordPress development.

It should be used before every commit, pull request, or AI-generated implementation to ensure consistency, maintainability, and production readiness.