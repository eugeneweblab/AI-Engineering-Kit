---
id: wordpress/99-ai-review-checklist
topic: wordpress
slug: ai-review-checklist
title: "WordPress AI Review Checklist"
type: doc
order: 99
status: ready
tags: [wordpress, ai-review-checklist]
related: [wordpress/98-production-checklist, wordpress/100-common-antipatterns, wordpress/03-best-practices]
when_to_use: "Read before reviewing or merging WordPress code changes."
---
# WordPress AI Review Checklist

## Purpose

This document defines the standard code review checklist for WordPress projects.

It is intended for both human reviewers and AI coding assistants to ensure that every implementation meets the project's engineering standards before it is merged.

A code review should evaluate far more than whether the code works.

It should verify that the implementation is maintainable, secure, scalable, and aligned with the project's architecture.

---

## Core Principle

Review the solution, not only the code.

A technically correct implementation may still introduce technical debt if it ignores existing architecture or duplicates functionality.

The objective of a review is to improve the overall quality of the project.

---

## Phase 1 — Requirements Review

Verify:

☐ The implementation satisfies the original requirements.

☐ Acceptance criteria have been met.

☐ No requested functionality is missing.

☐ No unnecessary functionality has been introduced.

☐ Edge cases have been considered.

---

## Phase 2 — Architecture Review

**Rules:** [Architecture](01-wordpress-architecture.md) · [Project Structure](02-project-structure.md)

Verify:

☐ Existing architecture has been respected.

☐ No duplicate functionality has been introduced.

☐ Responsibilities remain clearly separated.

☐ Business logic is isolated from presentation.

☐ Existing services and utilities have been reused.

☐ New files are located in the appropriate directories.

Architecture should become cleaner after every change.

---

## Phase 3 — WordPress Review

**Rules:** [Hooks — Actions and Filters](08-hooks.md) · [Best Practices](03-best-practices.md)

Verify:

☐ WordPress APIs are used where appropriate.

☐ Existing hooks have been reused.

☐ Core functionality has not been duplicated.

☐ Internationalization has been considered.

☐ Coding standards are consistent with the project.

☐ Theme and plugin responsibilities remain separated.

---

## Phase 4 — Security Review

**Rules:** [Security](06-security.md) · [Users and Capabilities](20-users-and-capabilities.md)

Verify:

☐ Input validation is implemented.

☐ Stored data is sanitized.

☐ Rendered output is escaped.

☐ Capability checks are present.

☐ Nonce verification is implemented where required.

☐ REST permission callbacks are correct.

☐ Sensitive information is protected.

Security issues block approval.

---

## Phase 5 — Performance Review

**Rules:** [Performance](05-performance.md) · [Queries and The Loop](12-queries.md)

Verify:

☐ Database queries are efficient.

☐ Duplicate queries have been avoided.

☐ Existing cached data is reused where appropriate.

☐ Asset loading is optimized.

☐ Images are appropriately optimized.

☐ API responses contain only necessary data.

Avoid accepting performance regressions without justification.

---

## Phase 6 — Frontend Review

**Rules:** [Template Hierarchy](13-template-hierarchy.md) · [Block Editor](16-block-editor.md)

Verify:

☐ The implementation matches the design.

☐ Responsive behavior has been verified.

☐ Semantic HTML is used.

☐ Accessibility requirements have been considered.

☐ Existing UI components have been reused.

☐ Styling follows the design system.

---

## Phase 7 — Backend Review

**Rules:** [Plugin Development](15-plugin-development.md) · [Database and $wpdb](19-database.md)

Verify:

☐ Business logic is encapsulated.

☐ Services remain cohesive.

☐ Dependencies are explicit.

☐ Error handling is appropriate.

☐ Logging is meaningful.

☐ Configuration remains centralized.

---

## Phase 8 — Code Quality Review

**Rules:** [Code Style](04-code-style.md)

Verify:

☐ Functions have a single responsibility.

☐ Classes have a single responsibility.

☐ Variable names are descriptive.

☐ Method names are descriptive.

☐ Nesting is minimal.

☐ Magic values have been avoided.

☐ Dead code has been removed.

☐ Comments explain intent rather than implementation.

Readable code should require minimal explanation.

---

## Phase 9 — Testing Review

**Rules:** [Testing](07-testing.md)

Verify:

☐ Primary functionality has been tested.

☐ Validation failures have been tested.

☐ Permission checks have been tested.

☐ Edge cases have been considered.

☐ Regression risks have been evaluated.

☐ Existing functionality remains unaffected.

Testing should provide confidence rather than merely increase coverage.

---

## Phase 10 — Documentation Review

**Rules:** [Maintenance](29-maintenance.md)

Verify:

☐ Public APIs are documented.

☐ Configuration changes are documented.

☐ Complex architectural decisions are documented.

☐ README files have been updated where appropriate.

☐ New workflows are documented if necessary.

Documentation should explain why the implementation exists.

---

## Review Questions

Before approving a change, ask:

- Is this implementation simpler than the alternatives?
- Does it follow the existing architecture?
- Is any duplicated functionality introduced?
- Can another engineer maintain it easily?
- Is security handled correctly?
- Is performance acceptable?
- Would this implementation still make sense in one year?

If the answer to any question is uncertain, request clarification or improvements.

---

## Approval Criteria

Approve only if:

☐ Requirements are fully satisfied.

☐ Architecture has been respected.

☐ Security concerns have been addressed.

☐ Performance is acceptable.

☐ Existing conventions have been followed.

☐ Testing has been completed.

☐ Documentation is sufficient.

Every approval increases the long-term quality of the project.

---

## AI Review Summary

When an AI assistant performs a review, it should provide a structured summary containing:

## Overall Assessment

- Ready for approval / Changes requested.

## Strengths

- What was implemented well?
- Which project conventions were followed?

## Findings

Categorize issues as:

- Critical
- Major
- Minor
- Suggestions

Each finding should include:

- Description
- Impact
- Recommended improvement

## Files Reviewed

List all reviewed files.

## Final Recommendation

One of:

- Approve
- Approve with minor comments
- Request changes
- Reject

The recommendation should be based on engineering quality rather than personal preference.

---

## Completion Criteria

A review is complete only when:

- all checklist items have been evaluated;
- findings are documented;
- recommendations are actionable;
- approval status is clearly stated;
- the implementation is considered production-ready.

---

## Summary

A high-quality code review protects the project's architecture, prevents technical debt, and improves the overall engineering culture.

The goal is not to criticize the author but to ensure that every merged change leaves the codebase in a better state than before.

## Related

- `knowledge/wordpress/98-production-checklist.md`
- `knowledge/wordpress/100-common-antipatterns.md`
- `knowledge/wordpress/03-best-practices.md`
