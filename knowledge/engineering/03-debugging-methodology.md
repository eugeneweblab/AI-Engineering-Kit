# Debugging Methodology

## Purpose

This document defines a structured approach to debugging software systems.

Debugging is an investigation process, not a guessing process.

The goal is to identify and eliminate the root cause of a problem with the smallest possible change while preserving existing behavior.

This methodology applies to all technologies, programming languages, and AI coding agents.

---

# Core Principle

Never fix a bug you do not understand.

Every bug has a cause.

Until that cause is identified, every code change is a hypothesis.

---

# The Debugging Process

Always follow the same sequence.

```
Observe
    ↓
Reproduce
    ↓
Understand
    ↓
Locate
    ↓
Verify
    ↓
Fix
    ↓
Validate
```

Never skip steps.

---

# Step 1 — Observe

Understand what actually happened.

Collect evidence before writing code.

Examples:

- error messages;
- stack traces;
- logs;
- screenshots;
- recordings;
- browser console output;
- network requests;
- API responses.

Facts are more valuable than assumptions.

---

# Step 2 — Reproduce

A bug that cannot be reproduced cannot be reliably fixed.

Determine:

- exact steps;
- environment;
- browser;
- operating system;
- device;
- user permissions;
- application state;
- feature flags.

Document the shortest possible reproduction.

---

# Step 3 — Define Expected Behavior

Before fixing the issue, define what should happen.

Questions:

- What is the correct behavior?
- Where is it documented?
- Does another feature behave correctly?
- Is the current behavior actually incorrect?

Do not assume the report is accurate.

---

# Step 4 — Isolate the Problem

Reduce the problem to the smallest possible scope.

Identify:

- affected component;
- affected service;
- affected API;
- affected database query;
- affected configuration;
- affected dependency.

The smaller the investigation area, the faster the solution.

---

# Step 5 — Collect Evidence

Avoid changing code during investigation.

Instead:

- inspect variables;
- inspect network traffic;
- inspect logs;
- inspect database records;
- inspect request payloads;
- inspect configuration.

Evidence should explain the behavior.

---

# Step 6 — Identify the Root Cause

Ask repeatedly:

Why did this happen?

Continue until the underlying cause becomes clear.

Examples:

Bad diagnosis

"The button doesn't work."

Better diagnosis

"The click handler never executes."

Root cause

"The component is conditionally rendered and the condition is always false."

Fix the root cause—not the symptom.

---

# Step 7 — Design the Fix

Before modifying code, determine:

- smallest safe change;
- affected modules;
- possible regressions;
- existing patterns to follow;
- existing utilities to reuse.

Avoid rewriting working code.

---

# Step 8 — Verify the Fix

Confirm that:

- the bug no longer exists;
- no new issues were introduced;
- related functionality still works;
- edge cases behave correctly.

Verification is mandatory.

---

# Step 9 — Prevent Regression

Whenever practical:

- add a test;
- improve validation;
- improve logging;
- improve documentation;
- simplify the implementation.

A good fix reduces the chance of the same issue returning.

---

# Debugging Rules

Always:

- understand before changing;
- reproduce before fixing;
- isolate before modifying;
- verify before closing.

Never:

- guess;
- rewrite unrelated code;
- ignore warnings;
- suppress errors without understanding them.

---

# Debugging Checklist

## Investigation

- Can the issue be reproduced?
- Is the expected behavior known?
- Has the affected area been isolated?
- Was sufficient evidence collected?

---

## Solution

- Was the root cause identified?
- Is the solution minimal?
- Does it follow existing architecture?
- Were existing utilities reused?

---

## Verification

- Is the original issue fixed?
- Were edge cases tested?
- Was regression risk evaluated?
- Were tests updated if needed?

---

# Common Anti-patterns

## Guess-Driven Development

Changing random code until something appears to work.

---

## Symptom Fixing

Masking the visible issue while leaving the underlying cause unchanged.

---

## Rewrite Instead of Investigate

Replacing large parts of the implementation without understanding the defect.

---

## Multiple Changes at Once

Making several unrelated modifications during debugging.

This makes root cause verification difficult.

---

## Ignoring Existing Patterns

Implementing a completely new solution instead of following existing architecture.

---

# AI Guidance

When debugging, AI coding agents should:

1. Gather evidence before proposing fixes.
2. Inspect existing implementations.
3. Explain the suspected root cause.
4. Clearly distinguish facts from assumptions.
5. Propose the smallest safe change.
6. Explain possible side effects.
7. Suggest verification steps after implementation.

AI should never present hypotheses as facts.

---

# Summary

Effective debugging is a disciplined engineering process.

The fastest fix is rarely the best fix.

Understanding the problem thoroughly almost always leads to a simpler, safer, and more maintainable solution.