---
id: ai/readme
topic: ai
slug: readme
title: "AI-Assisted Development Standards"
type: index
order: -1
status: ready
tags: [ai, readme]
related: []
when_to_use: "Read first when an AI agent is doing the coding — how to gather context, plan, generate, modify, fix, and self-verify."
---
# AI-Assisted Development Standards

## Purpose

This section defines how an AI coding assistant should approach engineering work so it
behaves like an experienced engineer, not an autocomplete.

It describes the reasoning process — gather context, plan, implement, verify — that
keeps AI-generated changes correct, consistent, and in scope.

These documents are written for AI agents first, but apply equally to any developer.

---

## Scope

This documentation covers:

- Engineering principles for AI-assisted work
- Gathering context before writing code
- Planning a task before implementing it
- Generating new code
- Modifying existing code safely
- Fixing bugs methodically
- Verifying your own work before finishing

---

## How to Use

Follow the documents in order. Together they form one loop:

- 00. AI Engineering Principles — the mindset and non-negotiables.
- 01. Context Gathering — understand the project before changing it.
- 02. Task Planning — decide the approach before writing code.
- 03. Code Generation — write new code that fits existing patterns.
- 04. Code Modification — change existing code without collateral damage.
- 05. Bug Fixing — diagnose the root cause, not the symptom.
- 06. Self-Verification — prove the change works before declaring done.

This section pairs with [`../workflows/`](../workflows/) (concrete task recipes) and
[`../engineering/`](../engineering/) (the underlying engineering discipline).

---

## Core Principles

- Understand before implementing. Read the relevant `ready` docs first.
- Reuse over recreate. Prefer existing components, patterns, and conventions.
- Stay in scope. Fix the task; do not make unrelated changes.
- Consistency over cleverness. Match the surrounding code.
- Verify with evidence. Do not claim done without checking.

---

## Intended Audience

- AI Coding Assistants
- Engineers pairing with AI tools
- Tech Leads defining AI usage standards
- Code Reviewers

---

## Summary

Applying these standards makes AI-assisted development predictable and safe: the agent
gathers context, plans, implements in scope, and verifies — every time.
