---
id: engineering/05-context-first-development
topic: engineering
slug: context-first-development
title: "Context-First Development"
type: doc
order: 5
status: ready
tags: [engineering, context-first-development]
related: []
when_to_use: ""
---
# Context-First Development

## Purpose

This document defines one of the most important engineering principles in AI-assisted software development:

> Every implementation should begin with understanding the surrounding context before modifying code.

The quality of engineering decisions depends directly on the quality of the available context.

Adding more code without understanding the existing system usually increases technical debt.

---

## Core Principle

Context always comes before implementation.

Never begin writing code simply because a file has been identified.

Instead, understand:

- why the file exists;
- how it interacts with the rest of the system;
- what assumptions it makes;
- which architectural decisions it follows.

Implementation without context produces inconsistent software.

---

## What Is Context?

Context is every piece of information that influences an engineering decision.

Examples include:

- project architecture;
- business requirements;
- existing design patterns;
- coding conventions;
- folder structure;
- naming conventions;
- dependencies;
- APIs;
- database schema;
- user experience;
- accessibility requirements;
- security requirements;
- performance requirements.

Context extends beyond the current file.

---

## Levels of Context

Engineering decisions should be made using multiple levels of context.

## Level 1 — Business Context

Understand:

- What problem is being solved?
- Who benefits from this change?
- What is the expected outcome?
- What are the business constraints?

Without business context it is impossible to determine whether a solution is actually correct.

---

## Level 2 — Project Context

Understand the project itself.

Review:

- architecture;
- technology stack;
- coding standards;
- project structure;
- existing conventions.

Every project has its own engineering language.

Learn it before contributing.

---

## Level 3 — Module Context

Inspect the module that will be modified.

Questions:

- What is its responsibility?
- Which modules depend on it?
- Which modules does it depend on?
- Does it expose public APIs?

Understanding module boundaries prevents accidental regressions.

---

## Level 4 — File Context

Read the entire file before modifying it.

Determine:

- overall responsibility;
- public interface;
- internal structure;
- existing comments;
- TODO items;
- technical debt.

Never modify code after reading only a few lines.

---

## Level 5 — Local Context

Only after understanding the larger system should individual functions be modified.

Understand:

- inputs;
- outputs;
- side effects;
- assumptions;
- error handling.

Local optimizations should never violate higher-level architecture.

---

## Context Investigation Checklist

Before writing code, inspect:

- similar implementations;
- existing utilities;
- related components;
- project configuration;
- documentation;
- tests;
- previous implementations.

Engineering is often about discovering existing solutions rather than creating new ones.

---

## Context Before Creation

Before creating a new...

## Component

Search for:

- similar UI;
- shared layouts;
- reusable patterns.

---

## Utility

Search for:

- helper functions;
- existing abstractions;
- framework capabilities.

---

## API Endpoint

Search for:

- existing endpoints;
- reusable services;
- shared validation;
- authentication logic.

---

## Database Model

Review:

- existing relationships;
- naming conventions;
- migration strategy.

---

## Service

Determine whether the responsibility already exists elsewhere.

Prefer extending an existing service over introducing competing abstractions.

---

## Warning Signs

The following often indicate insufficient context.

Examples:

- duplicate components;
- duplicate utilities;
- inconsistent naming;
- multiple architectural patterns;
- unnecessary abstractions;
- excessive refactoring;
- repeated business logic.

Most of these problems originate from implementing before investigating.

---

## AI Guidance

Before generating code, AI coding agents should explicitly determine:

- the architectural pattern being used;
- the conventions followed by the project;
- existing reusable implementations;
- expected coding style;
- likely integration points.

If important context is missing, AI should explain what information is required instead of making assumptions.

---

## Self Review

Before implementation ask:

- Do I understand the business problem?
- Do I understand the architecture?
- Have I inspected similar code?
- Have I searched for reusable solutions?
- Do I understand why the current implementation exists?
- Am I modifying the correct location?
- Have I considered downstream effects?

If any answer is **No**, continue investigating.

---

## Anti-patterns

Avoid:

Reading only the current function.

Making assumptions based on filenames.

Creating new abstractions without searching the repository.

Copying code from unrelated projects.

Ignoring project conventions.

Treating every task as an isolated problem.

---

## Summary

Strong engineers spend significant time building context before writing code.

The larger the system becomes, the more valuable context becomes.

Understanding the system first consistently produces simpler, safer, and more maintainable solutions than implementation driven by assumptions.