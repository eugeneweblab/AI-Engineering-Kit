# Engineering Code Review

## Purpose

This document defines how software engineers and AI coding agents should review code before considering a task complete.

Code review is not the final step of development.

It is an essential part of engineering that ensures code is correct, maintainable, understandable, and consistent with the project.

This document should be used both for reviewing pull requests and for performing self-review before submitting changes.

---

# Review Mindset

The purpose of a review is to improve the software—not to criticize the author.

A good review focuses on:

- correctness;
- maintainability;
- consistency;
- readability;
- long-term engineering quality.

Every review should assume good intentions.

---

# Review Order

Always review code in the following order.

Do not start by reviewing formatting or naming.

## 1. Requirements

Verify that the implementation satisfies the original requirements.

Ask:

- Does it solve the requested problem?
- Does it solve the correct problem?
- Is any requirement missing?
- Was unnecessary functionality introduced?

---

## 2. Scope

Verify that only the required parts of the project were modified.

Look for:

- unrelated refactoring;
- formatting-only changes;
- accidental file modifications;
- unnecessary dependency updates.

Small pull requests are easier to understand and safer to deploy.

---

## 3. Architecture

Check whether the implementation follows the existing architecture.

Questions:

- Does this fit the project?
- Is a new pattern being introduced?
- Is there an existing solution that should have been reused?
- Does this increase architectural complexity?

Architecture should evolve intentionally.

---

## 4. Simplicity

Prefer the simplest solution that fully satisfies the requirements.

Review for:

- unnecessary abstractions;
- deeply nested logic;
- duplicated responsibilities;
- premature optimization;
- over-engineering.

Simple code is easier to maintain.

---

## 5. Readability

Code should explain itself.

Review:

- names;
- function size;
- class responsibilities;
- file organization;
- logical flow.

Future maintainers should understand the implementation without additional explanation.

---

## 6. Reusability

Determine whether existing code could have been reused.

Look for:

- duplicated utilities;
- duplicated components;
- repeated business logic;
- similar API implementations.

Avoid introducing duplicate solutions.

---

## 7. Error Handling

Verify that failures are handled intentionally.

Check:

- invalid input;
- API failures;
- database failures;
- empty states;
- timeout handling;
- fallback behavior.

Happy-path code is not sufficient.

---

## 8. Security

Every review should include a basic security assessment.

Verify:

- input validation;
- output escaping;
- authentication;
- authorization;
- secrets handling;
- dependency usage.

Security is a requirement, not an enhancement.

---

## 9. Performance

Performance should be reviewed using evidence.

Look for:

- unnecessary rendering;
- duplicate requests;
- repeated calculations;
- excessive database queries;
- unnecessary allocations.

Do not optimize hypothetical bottlenecks.

---

## 10. Accessibility

For user interfaces verify:

- keyboard navigation;
- semantic HTML;
- focus management;
- labels;
- color contrast;
- screen reader support.

Accessibility is part of product quality.

---

## 11. Testing

Review whether the implementation is sufficiently verified.

Questions:

- Are existing tests still valid?
- Should new tests exist?
- Are edge cases covered?
- Is manual verification documented when automated testing is unavailable?

---

## 12. Documentation

Determine whether documentation needs updating.

Examples:

- README
- API documentation
- Architecture documentation
- Configuration
- Environment variables
- Migration instructions

Code and documentation should evolve together.

---

# Self Review

Before submitting changes, every engineer should perform a complete self-review.

Self-review should answer the following questions.

## Understanding

- Did I fully understand the problem?
- Did I verify my assumptions?
- Did I inspect similar implementations?

---

## Correctness

- Does the implementation satisfy every requirement?
- Did I verify edge cases?
- Could this introduce regressions?

---

## Consistency

- Does the implementation match project conventions?
- Did I introduce a competing pattern?
- Are naming conventions consistent?

---

## Maintainability

- Can another engineer understand this quickly?
- Can this implementation be extended safely?
- Did I remove unnecessary complexity?

---

## Safety

- Did I accidentally modify unrelated files?
- Did I leave debugging code?
- Did I remove temporary workarounds?
- Did I remove commented-out code?

---

## Final Checklist

Before considering the task complete, verify:

- Requirements are fully satisfied.
- No unrelated code was modified.
- Existing architecture was respected.
- Code is readable.
- Code is maintainable.
- Existing solutions were reused whenever possible.
- Error handling is appropriate.
- Security considerations were reviewed.
- Performance implications were evaluated.
- Accessibility was considered where applicable.
- Tests were updated or verified.
- Documentation remains accurate.

---

# Review Anti-patterns

Avoid reviews that focus primarily on:

- formatting preferences;
- personal coding style;
- unnecessary micro-optimizations;
- subjective opinions without engineering justification.

Every review comment should answer at least one of the following questions:

- Does this improve correctness?
- Does this improve maintainability?
- Does this reduce risk?
- Does this improve consistency?
- Does this improve developer understanding?

If the answer is **no**, the comment may not be valuable.

---

# Summary

Excellent engineering reviews improve software quality, reduce long-term maintenance costs, and encourage consistent decision-making.

The goal of a review is not to find fault.

The goal is to leave the codebase in a better state than before.