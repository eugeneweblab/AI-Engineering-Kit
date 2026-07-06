# Code Generation

## Purpose

This document defines how AI coding agents should generate code inside an existing software project.

The primary objective is not to generate code quickly.

The primary objective is to generate code that is indistinguishable from code written by an experienced engineer already familiar with the project.

Code generation should preserve architecture, reduce maintenance cost, and integrate naturally with the existing codebase.

---

# Core Principle

Generate code that belongs to the project.

Not code that demonstrates knowledge.

The generated implementation should feel as though it has always been part of the repository.

---

# Generation Priorities

Always prioritize:

1. Correctness
2. Consistency
3. Maintainability
4. Readability
5. Reusability
6. Performance
7. Brevity

Shorter code is not necessarily better code.

---

# Repository-First Generation

Before generating any code, inspect the repository.

Determine:

- folder structure;
- architectural patterns;
- naming conventions;
- file organization;
- dependency injection patterns;
- error handling;
- logging strategy;
- testing strategy.

Generate code that follows the existing project.

Never generate code based only on generic framework examples.

---

# Reuse Before Creation

Before creating any new implementation, search for:

- components;
- services;
- utilities;
- hooks;
- helpers;
- validation logic;
- middleware;
- API clients;
- constants;
- types.

Creating duplicate logic should always be the last option.

---

# Match Existing Style

Generated code should match the repository.

Respect:

- naming conventions;
- import order;
- formatting;
- file structure;
- folder hierarchy;
- abstraction level;
- comment style;
- error handling patterns.

The generated code should not reveal which AI model produced it.

---

# Generate the Smallest Correct Change

Modify only what is required.

Avoid:

- unnecessary refactoring;
- unrelated formatting;
- dependency updates;
- architecture changes;
- renaming unrelated symbols.

The safest implementation is usually the smallest implementation.

---

# Respect Existing Boundaries

Do not move responsibilities between modules unless explicitly required.

Examples:

Business logic should remain in services.

Presentation logic should remain in UI.

Validation should remain in validation layers.

Database access should remain in repositories or data services.

Avoid mixing responsibilities.

---

# Prefer Extension Over Replacement

When existing code can be extended safely:

Prefer extension.

Do not replace an entire implementation simply because a different solution appears cleaner.

Respect the engineering history of the project.

---

# Error Handling

Generated code should follow existing error handling patterns.

Do not invent new approaches.

Verify:

- validation;
- null handling;
- exceptions;
- logging;
- retries;
- fallback behavior.

Every failure path should be intentional.

---

# Dependency Management

Before introducing a dependency, verify:

- an existing dependency already solves the problem;
- framework functionality is sufficient;
- a shared utility already exists.

New dependencies should require clear engineering justification.

---

# Comments

Comments should explain intent.

Do not comment obvious code.

Prefer:

Why

Instead of:

What

Bad:

```ts
// Increment counter
counter++;
```

Good:

```ts
// Prevent duplicate submission attempts
submissionCount++;
```

---

# Generated Code Should Be Predictable

Future engineers should be able to predict where new code will be located.

New implementations should follow existing project organization.

Avoid surprising file locations.

Avoid inconsistent naming.

Avoid unique patterns for common problems.

---

# Hallucination Prevention

Never invent:

- APIs;
- configuration values;
- environment variables;
- project utilities;
- framework capabilities;
- database tables;
- services;
- business rules.

When information cannot be verified, state the uncertainty.

---

# Large Tasks

Large implementations should be completed incrementally.

Preferred order:

Understand

↓

Plan

↓

Generate infrastructure

↓

Generate implementation

↓

Generate tests

↓

Verify

↓

Review

Avoid generating hundreds of lines of code before validation.

---

# AI Execution Checklist

## Before Generation

- Read every affected file completely.
- Search for similar implementations.
- Identify reusable code.
- Understand naming conventions.
- Understand architecture.
- Verify project configuration.
- Verify framework version.

---

## During Generation

- Modify the smallest possible area.
- Preserve architecture.
- Match repository style.
- Reuse existing abstractions.
- Avoid duplicate logic.
- Keep responsibilities separated.

---

## Before Completion

- Verify imports.
- Verify exports.
- Verify naming consistency.
- Remove temporary code.
- Remove debugging statements.
- Verify documentation.
- Verify tests.
- Review affected files.
- Review side effects.

---

# Anti-patterns

Avoid:

Generating code from memory.

Inventing project conventions.

Ignoring existing architecture.

Creating duplicate implementations.

Moving unrelated code.

Introducing unnecessary abstractions.

Using framework examples without adapting them.

Replacing working code unnecessarily.

Generating large changes without incremental verification.

---

# AI Responsibilities

AI should always explain:

What was changed.

Why it was changed.

Why this implementation was selected.

What existing code was reused.

What assumptions were made.

What risks remain.

What should be verified manually.

Transparency increases trust.

---

# Definition of Success

Generated code is successful when:

It follows project architecture.

It matches existing coding style.

It introduces no unnecessary complexity.

It minimizes regression risk.

It reuses existing implementations.

It is understandable without additional explanation.

It passes verification.

The best generated code is code that another engineer would naturally assume was written by a member of the project team.

---

# Summary

AI should not generate code that merely works.

AI should generate code that belongs.

Every generated line should respect the architecture, conventions, and engineering philosophy of the repository.

Successful AI-assisted development is measured not by the amount of generated code, but by how seamlessly that code integrates into the existing system.