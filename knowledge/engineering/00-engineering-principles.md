---
id: engineering/00-engineering-principles
topic: engineering
slug: engineering-principles
title: "Engineering Principles"
type: doc
order: 0
status: ready
tags: [engineering, engineering-principles]
related: []
when_to_use: "Read before making any engineering decision to apply the kit's foundational principles."
---
# Engineering Principles

## Purpose

This document defines the engineering principles that guide every recommendation in the AI Engineering Kit.

These principles apply to every technology, framework, programming language, and AI coding agent.

When documentation appears to conflict, these principles take precedence.

---

## Principle 1 — Understand Before Changing

Never modify code before understanding its purpose.

Before making changes:

- identify the problem;
- understand the surrounding architecture;
- determine why the current implementation exists;
- identify potential side effects.

Making changes without understanding the existing system often introduces unnecessary complexity and regressions.

---

## Principle 2 — Solve the Root Cause

Do not optimize symptoms.

Do not patch consequences.

Identify and solve the underlying cause of the problem whenever practical.

Temporary workarounds should be explicitly documented.

---

## Principle 3 — Prefer Simplicity

Choose the simplest solution that fully satisfies the requirements.

Simple solutions are easier to:

- understand;
- review;
- test;
- maintain;
- extend.

Simplicity should never sacrifice correctness.

---

## Principle 4 — Preserve Consistency

Consistency is more valuable than personal preference.

Follow the conventions already established within the project unless there is a clear engineering reason to improve them.

Consistency reduces cognitive load and improves long-term maintainability.

---

## Principle 5 — Reuse Before Creating

Before introducing new code, determine whether an existing implementation can be reused.

Always:

- search for similar components;
- inspect existing utilities;
- evaluate extension points;
- compare responsibilities.

Create new abstractions only when reuse would increase complexity.

---

## Principle 6 — Minimize Change Surface

Modify as little code as necessary.

Smaller changes are:

- easier to review;
- easier to test;
- easier to revert;
- less likely to introduce regressions.

Avoid unrelated refactoring during feature implementation or bug fixes.

---

## Principle 7 — Make Intent Obvious

Code should communicate intent before implementation details.

Prioritize:

- meaningful names;
- clear structure;
- predictable behavior;
- explicit logic.

Future maintainers should understand *why* the code exists before reading *how* it works.

---

## Principle 8 — Optimize for Maintainability

Software is read significantly more often than it is written.

Favor solutions that improve long-term maintenance over short-term implementation speed.

Maintainability includes:

- readability;
- modularity;
- testability;
- consistency;
- documentation.

---

## Principle 9 — Verify Assumptions

Never assume.

Whenever possible:

- inspect existing code;
- inspect project configuration;
- inspect documentation;
- inspect APIs;
- inspect design assets.

Assumptions should be replaced with evidence.

---

## Principle 10 — Respect Existing Architecture

Every project has architectural decisions.

Understand them before introducing new ones.

Avoid creating competing patterns inside the same codebase.

When improvements are necessary, evolve the architecture incrementally instead of replacing it entirely.

---

## Principle 11 — Separate Problems

Solve one problem at a time.

Do not combine:

- feature development;
- refactoring;
- dependency upgrades;
- formatting changes;
- architectural redesign.

Independent changes produce clearer reviews and safer deployments.

---

## Principle 12 — Design for Future Readers

Write every line of code as if the next person maintaining it has no prior context.

Future readers may include:

- teammates;
- open-source contributors;
- future versions of yourself;
- AI coding agents.

Readable code reduces engineering cost.

---

## Principle 13 — Performance Requires Evidence

Do not optimize based on assumptions.

Measure first.

Optimize only after identifying a measurable bottleneck.

Avoid sacrificing readability for hypothetical performance improvements.

---

## Principle 14 — Security Is a Requirement

Security is never an optional enhancement.

Every implementation should consider:

- input validation;
- output escaping;
- authentication;
- authorization;
- secret management;
- dependency trust.

Secure defaults are preferable to configurable security.

---

## Principle 15 — Quality Before Speed

Fast delivery has value.

Reliable delivery has greater value.

Engineering decisions should balance:

- delivery speed;
- correctness;
- maintainability;
- operational risk.

Shipping quickly should never justify knowingly introducing avoidable technical debt.

---

## Summary

Every document in AI Engineering Kit builds upon these principles.

Technology-specific recommendations should never contradict them.

When uncertainty exists, these principles should guide the final engineering decision.