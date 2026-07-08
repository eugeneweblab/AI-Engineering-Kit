---
id: engineering/01-decision-framework
topic: engineering
slug: decision-framework
title: "Engineering Decision Framework"
type: doc
order: 1
status: ready
tags: [engineering, decision-framework]
related: []
when_to_use: "Read before writing or modifying code to work through engineering decisions systematically."
---
# Engineering Decision Framework

## Purpose

This document defines a universal decision-making process for engineers and AI coding agents.

Before writing, modifying, or reviewing code, every engineering task should follow the same sequence of decisions.

The framework is intentionally technology-independent and can be applied to any programming language, framework, or codebase.

---

## Step 1 — Understand the Request

Do not start implementing immediately.

Identify:

- the requested outcome;
- the actual problem;
- the expected behavior;
- the scope of the change;
- any explicit constraints.

If the request is ambiguous, resolve the ambiguity before implementation.

---

## Step 2 — Understand the Existing System

Never assume the current implementation is incorrect.

Inspect:

- project architecture;
- existing patterns;
- related components;
- similar implementations;
- documentation;
- configuration;
- tests.

The goal is to understand why the current solution exists before replacing it.

---

## Step 3 — Define the Real Problem

Many requests describe symptoms instead of root causes.

Examples:

**Request**

> Make this API faster.

Possible root causes:

- unnecessary database queries;
- inefficient caching;
- network latency;
- oversized payloads;
- client-side rendering issues.

Never optimize before identifying the actual bottleneck.

---

## Step 4 — Evaluate Existing Solutions

Before introducing new code, determine whether the project already contains an appropriate solution.

Search for:

- reusable components;
- shared utilities;
- helper functions;
- existing services;
- design patterns;
- abstractions.

Reuse should always be considered before creating something new.

---

## Step 5 — Evaluate Impact

Every change has consequences.

Consider:

- affected modules;
- public APIs;
- backward compatibility;
- performance;
- accessibility;
- security;
- testing;
- documentation.

The best implementation is not always the smallest one.

---

## Step 6 — Choose the Simplest Correct Solution

Prefer solutions that are:

- understandable;
- maintainable;
- testable;
- consistent with the existing architecture.

Avoid introducing unnecessary abstractions.

Avoid solving future problems that do not yet exist.

---

## Step 7 — Verify Before Completing

Before considering the task complete, verify:

- requirements are satisfied;
- existing behavior remains unchanged where expected;
- no unrelated code was modified;
- naming remains consistent;
- documentation remains accurate;
- tests still pass.

Implementation is not complete until verification is complete.

---

## Decision Checklist

Before writing code:

- Do I understand the problem?
- Do I understand the existing implementation?
- Am I solving the root cause?
- Can existing code be reused?
- Is this solution consistent with the project?
- Have I considered side effects?
- Is there a simpler solution?

If any answer is **No**, continue investigating before implementing.

---

## Decision Tree

```
Receive request
        │
        ▼
Understand the problem
        │
        ▼
Inspect existing implementation
        │
        ▼
Identify root cause
        │
        ▼
Search for reusable solution
        │
        ▼
Choose the simplest correct implementation
        │
        ▼
Evaluate impact
        │
        ▼
Implement
        │
        ▼
Verify
        │
        ▼
Complete
```

---

## Summary

Good engineering decisions are rarely the result of writing code quickly.

They are the result of understanding the problem deeply, respecting the existing system, and making deliberate, verifiable changes.