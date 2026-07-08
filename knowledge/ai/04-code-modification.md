---
id: ai/04-code-modification
topic: ai
slug: code-modification
title: "Code Modification"
type: doc
order: 4
status: ready
tags: [ai, code-modification]
related: []
when_to_use: "Read before modifying existing code to make the smallest safe change without breaking behavior."
---
# Code Modification

## Purpose

This document defines how AI coding agents should modify existing code safely.

Most engineering work is not creating new software.

It is modifying existing software without breaking existing behavior.

The objective is to make the smallest correct change while preserving the integrity of the project.

---

## Core Principle

Respect the existing codebase.

Every line of existing code exists for a reason.

Before changing it, understand:

- why it exists;
- what depends on it;
- what assumptions it makes;
- what problems it solves.

Changing code without understanding its role increases technical debt.

---

## Modification Strategy

Always follow this sequence.

```
Understand
      ↓
Inspect
      ↓
Analyze Impact
      ↓
Plan
      ↓
Modify
      ↓
Verify
      ↓
Self Review
```

Never begin editing immediately.

---

## Rule 1 — Read Before Editing

Read the entire file.

Do not edit after reading only the relevant function.

Review:

- imports;
- exports;
- interfaces;
- helper functions;
- surrounding logic;
- comments;
- TODOs.

Local changes often have file-level implications.

---

## Rule 2 — Understand Why

Before changing existing logic determine:

- why it was written;
- whether it solves multiple problems;
- whether other modules depend on it;
- whether it exists for backward compatibility.

Never assume existing code is incorrect simply because it looks unfamiliar.

---

## Rule 3 — Minimize the Change Surface

Modify only what is necessary.

Prefer:

- changing one function;
- extending one class;
- adding one condition;
- updating one interface.

Avoid rewriting entire modules unless explicitly required.

Small changes reduce risk.

---

## Rule 4 — Preserve Public Contracts

When modifying:

- APIs;
- public functions;
- exported types;
- reusable components;
- services;

assume external code depends on them.

Changing public behavior requires careful verification.

Backward compatibility should be preserved whenever practical.

---

## Rule 5 — Preserve Existing Patterns

Match:

- naming;
- architecture;
- folder organization;
- abstraction level;
- dependency flow;
- testing style.

Avoid introducing a new pattern inside an established project.

---

## Rule 6 — Avoid Hidden Side Effects

Before modifying code determine:

What calls this?

What imports this?

Who depends on this?

What assumptions may change?

Every modification should consider downstream consumers.

---

## Rule 7 — Separate Refactoring From Functional Changes

Do not combine:

- formatting;
- renaming;
- optimization;
- feature development;
- dependency upgrades.

One pull request should solve one engineering problem.

Mixed changes increase review complexity.

---

## Rule 8 — Preserve Existing Behavior

If behavior is not intentionally changing:

It should remain identical.

Regression prevention is a primary engineering responsibility.

---

## Rule 9 — Extend Before Replacing

If existing code can safely support the new requirement:

Extend it.

Avoid replacing mature implementations simply because a new approach appears cleaner.

Engineering history has value.

---

## Rule 10 — Remove Temporary Changes

Before completion remove:

- console logs;
- debug output;
- temporary variables;
- commented-out code;
- experimental logic;
- unused imports.

Only intentional code should remain.

---

## Safe Modification Checklist

Before editing verify:

- I understand the file.
- I understand the module.
- I understand the architecture.
- I understand why this implementation exists.

---

Before saving verify:

- Only required code changed.
- Existing behavior is preserved.
- Public interfaces remain compatible.
- Existing conventions were followed.
- No duplicate logic was introduced.

---

Before completing verify:

- Imports are correct.
- Types are correct.
- Documentation remains valid.
- Tests still pass.
- No debugging code remains.
- Side effects were reviewed.

---

## Modification Risk Assessment

Before modifying code estimate the risk.

## Low Risk

- UI text
- Styling
- Documentation
- Small isolated utility

---

## Medium Risk

- Component logic
- Business rules
- API validation
- Shared utilities

---

## High Risk

- Authentication
- Authorization
- Database schema
- Payment logic
- Framework configuration
- Public APIs
- Shared infrastructure

Higher-risk changes require more investigation and verification.

---

## AI Execution Checklist

## Investigation

☐ Read the complete file.

☐ Read related files.

☐ Search similar implementations.

☐ Identify reusable code.

☐ Understand dependencies.

☐ Understand architecture.

---

## Modification

☐ Modify the smallest possible area.

☐ Preserve existing naming.

☐ Preserve architecture.

☐ Preserve public contracts.

☐ Avoid duplicate logic.

☐ Avoid unnecessary refactoring.

---

## Verification

☐ Review changed files.

☐ Review imports.

☐ Review exports.

☐ Review side effects.

☐ Review edge cases.

☐ Remove temporary code.

☐ Verify documentation.

☐ Verify tests.

---

## Common Anti-patterns

## Rewrite Instead of Extend

Replacing large sections of code when a small extension would solve the problem.

---

## Cascade Editing

Changing multiple unrelated files because they appear similar.

---

## Architecture Drift

Introducing a new pattern into a project that already has an established architecture.

---

## Silent Breaking Change

Changing public behavior without updating documentation or dependent code.

---

## Accidental Cleanup

Removing code simply because its purpose is unclear.

Unclear code should be investigated—not deleted.

---

## AI Responsibilities

Before proposing modifications AI should explain:

- what will change;
- why the change is necessary;
- what existing code will remain unchanged;
- possible side effects;
- rollback strategy if the change fails.

Transparency improves engineering confidence.

---

## Definition of Success

A successful modification:

- solves the intended problem;
- preserves existing behavior where expected;
- introduces the smallest reasonable change;
- follows repository conventions;
- minimizes regression risk;
- improves maintainability rather than reducing it.

The best modification is often the one that future engineers barely notice because it integrates naturally into the existing codebase.

---

## Summary

Professional software engineering is primarily the discipline of changing existing systems safely.

AI coding agents should optimize for confidence, predictability, and maintainability—not for the amount of generated code.

Safe modifications build trust.

Trust enables effective AI-assisted engineering.