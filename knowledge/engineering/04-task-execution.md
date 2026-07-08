---
id: engineering/04-task-execution
topic: engineering
slug: task-execution
title: "Task Execution Workflow"
type: doc
order: 4
status: ready
tags: [engineering, task-execution]
related: []
when_to_use: "Read before starting any engineering task to follow the standard execution process."
---
# Task Execution Workflow

## Purpose

This document defines the standard workflow for completing engineering tasks.

Every software engineer and AI coding agent should follow the same execution process regardless of technology, framework, or project size.

The objective is to produce predictable, maintainable, and verifiable changes while minimizing unnecessary risk.

---

## Core Principle

Never begin implementation immediately.

Engineering starts with understanding, not coding.

The quality of the solution depends far more on understanding the problem than on writing code quickly.

---

## Standard Workflow

Every task should follow this sequence.

```
Receive Task
      ↓
Understand
      ↓
Investigate
      ↓
Plan
      ↓
Implement
      ↓
Verify
      ↓
Self Review
      ↓
Complete
```

Each phase has a specific purpose.

Skipping phases increases the likelihood of defects.

---

## Phase 1 — Receive the Task

Identify exactly what is being requested.

Determine:

- the expected outcome;
- the business goal;
- constraints;
- assumptions;
- unknowns.

If requirements are unclear, clarification should be requested before implementation.

Never invent missing requirements.

---

## Phase 2 — Understand the Existing System

Before changing code, inspect the surrounding context.

Review:

- project architecture;
- existing implementation;
- related modules;
- coding conventions;
- documentation;
- similar solutions.

The objective is to understand why the current implementation exists.

---

## Phase 3 — Investigate

Collect evidence before making decisions.

Examples include:

- reading source code;
- examining configuration;
- reviewing logs;
- inspecting API responses;
- checking database queries;
- reviewing design files;
- reading documentation.

Engineering decisions should be evidence-based.

---

## Phase 4 — Create an Implementation Plan

Think before writing code.

A good implementation plan should answer:

- What will change?
- Why is the change necessary?
- Which files are affected?
- What are the risks?
- Can existing code be reused?
- What should not be modified?

Planning reduces unnecessary changes.

---

## Phase 5 — Implement

Implementation should follow the established architecture.

Guidelines:

- modify the smallest possible amount of code;
- preserve existing conventions;
- reuse existing abstractions;
- avoid unrelated refactoring;
- keep commits focused.

Every change should have a clear purpose.

---

## Phase 6 — Verify

Before considering the task complete, verify the implementation.

Check:

- requirements are satisfied;
- no regressions were introduced;
- existing behavior is preserved;
- edge cases behave correctly;
- performance remains acceptable;
- security has not been weakened.

Verification is part of implementation.

---

## Phase 7 — Perform Self Review

Review your own work before asking others to review it.

Ask:

- Would another engineer understand this?
- Is every change necessary?
- Can anything be simplified?
- Did I introduce duplication?
- Did I accidentally modify unrelated code?

Self-review should identify obvious issues before they reach code review.

---

## Phase 8 — Complete the Task

A task is complete only when:

- implementation is correct;
- verification is complete;
- documentation is updated if necessary;
- tests pass or have been updated;
- temporary code has been removed.

Completion is determined by quality, not by the last edited file.

---

## Decision Rules

During implementation always prefer:

Understanding over assumptions.

Evidence over guesses.

Reuse over duplication.

Consistency over personal preference.

Simplicity over cleverness.

Maintainability over speed.

Small changes over large rewrites.

Root-cause fixes over symptom fixes.

---

## Task Checklist

Before beginning:

- Do I understand the request?
- Do I understand the existing implementation?
- Do I understand the expected behavior?

---

Before implementing:

- Have I investigated similar code?
- Can existing code be reused?
- Have I identified the smallest possible change?

---

Before finishing:

- Are all requirements satisfied?
- Were only necessary files modified?
- Does the implementation follow project conventions?
- Is the code readable?
- Is the solution maintainable?
- Were edge cases considered?
- Were tests verified?
- Does documentation remain accurate?

---

## Common Mistakes

Avoid the following:

Starting implementation before understanding the problem.

Making assumptions without verification.

Changing unrelated code.

Introducing new patterns unnecessarily.

Creating duplicate functionality.

Combining refactoring with feature development.

Leaving temporary debugging code.

Ignoring existing project conventions.

Marking tasks complete without verification.

---

## AI Guidance

AI coding agents should always explain:

- what was investigated;
- why the selected approach was chosen;
- what alternatives were considered;
- what risks exist;
- how the solution was verified.

AI should distinguish clearly between:

- facts;
- assumptions;
- recommendations;
- uncertainty.

When uncertainty exists, AI should state it explicitly instead of presenting speculation as fact.

---

## Definition of Done

A task is considered complete only if:

- The requested outcome has been achieved.
- The implementation follows the existing architecture.
- The smallest reasonable change was made.
- Existing functionality remains intact.
- Documentation is still accurate.
- Tests were verified or updated.
- The implementation passed self-review.

Completion means the codebase is in a better state than before the task began.

---

## Summary

Professional engineering is not defined by writing code quickly.

It is defined by consistently making correct decisions throughout the entire lifecycle of a task.

Following a structured workflow reduces defects, improves maintainability, and produces predictable engineering outcomes for both humans and AI coding agents.