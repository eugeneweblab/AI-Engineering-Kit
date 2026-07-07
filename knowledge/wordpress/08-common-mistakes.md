---
id: wordpress/08-common-mistakes
topic: wordpress
slug: common-mistakes
title: "Common WordPress Mistakes"
type: doc
order: 8
status: ready
tags: [wordpress, common-mistakes]
related: []
when_to_use: ""
---
# Common WordPress Mistakes

## Purpose

This document describes the most common engineering mistakes encountered in professional WordPress development.

The objective is to help engineers and AI coding agents recognize poor implementation patterns before they become technical debt.

Every mistake listed here has appeared repeatedly in real production projects.

Avoiding these mistakes improves maintainability, security, performance, and long-term project stability.

---

## Core Principle

Most problems are not caused by writing incorrect code.

They are caused by writing code that ignores the project's architecture.

Always understand the existing system before introducing new code.

---

## Mistake 1 — Creating Instead of Reusing

Before writing new code, search the project.

Look for existing:

- services;
- helper functions;
- React components;
- Gutenberg blocks;
- Divi modules;
- REST endpoints;
- template parts;
- hooks;
- utilities.

Duplicate functionality increases maintenance costs.

---

## Mistake 2 — Business Logic Inside Templates

Templates should display data.

They should not:

- query the database;
- calculate business rules;
- call external APIs;
- modify data;
- perform validation.

Preferred architecture:

```
Template
      ↓
Service
      ↓
Repository
      ↓
WordPress API
```

---

## Mistake 3 — Ignoring Existing Architecture

Projects already have conventions.

Do not introduce:

- new folder structures;
- new architectural patterns;
- alternative dependency systems;
- inconsistent naming;
- different coding styles.

Consistency is more valuable than personal preference.

---

## Mistake 4 — Using Direct SQL Unnecessarily

Prefer WordPress APIs.

Examples:

- WP_Query
- get_posts()
- get_terms()
- get_users()
- Metadata API
- Options API

Use direct SQL only when a measurable benefit exists.

Always use prepared statements.

---

## Mistake 5 — Missing Capability Checks

Never assume that hiding a button is sufficient.

Every privileged operation must verify permissions.

Examples:

- admin pages;
- AJAX handlers;
- REST endpoints;
- settings pages;
- file uploads.

Authorization must be enforced on the server.

---

## Mistake 6 — Skipping Validation

Every external input should be validated.

Examples:

- GET parameters;
- POST requests;
- REST requests;
- uploaded files;
- cookies;
- third-party APIs.

Reject invalid input immediately.

---

## Mistake 7 — Forgetting Sanitization and Escaping

Remember the lifecycle:

```
Input
      ↓
Validation
      ↓
Sanitization
      ↓
Storage
      ↓
Retrieval
      ↓
Escaping
      ↓
Output
```

Never confuse sanitization with escaping.

---

## Mistake 8 — Large Hook Callbacks

Hook callbacks should remain small.

Preferred flow:

```
Hook
    ↓
Validation
    ↓
Service
    ↓
Return
```

Avoid placing business logic directly inside hooks.

---

## Mistake 9 — Monolithic Classes

Large classes often violate the Single Responsibility Principle.

Examples of good classes:

- ProductService
- OrderRepository
- ApiController
- UserValidator

Avoid classes that manage unrelated concerns.

---

## Mistake 10 — Ignoring Existing Components

Before creating UI:

Search for:

- buttons;
- cards;
- forms;
- typography;
- layouts;
- icons;
- utility components.

Reuse existing UI whenever possible.

---

## Mistake 11 — Hardcoded Values

Avoid hardcoding:

- colors;
- spacing;
- breakpoints;
- URLs;
- IDs;
- option names;
- API endpoints.

Prefer centralized configuration and design tokens.

---

## Mistake 12 — Premature Optimization

Do not optimize code before identifying the bottleneck.

Measure first.

Optimize second.

Keep the implementation readable.

---

## Mistake 13 — Ignoring Performance

Review:

- repeated queries;
- duplicate API requests;
- unnecessary rendering;
- asset loading;
- image optimization;
- cache opportunities.

Performance should be considered throughout development.

---

## Mistake 14 — Weak Naming

Names should describe responsibility.

Good:

```
CustomerRepository

ProductPriceCalculator

NewsletterSubscriptionService
```

Poor:

```
Helper

Utils

Functions

Data

Process
```

Good names reduce documentation requirements.

---

## Mistake 15 — Mixing Responsibilities

Avoid files that:

- render UI;
- perform validation;
- access the database;
- call external APIs;
- implement business rules.

Separate concerns into dedicated layers.

---

## AI Self-Review Checklist

Before finishing implementation verify:

☐ Existing architecture was reviewed.

☐ Existing functionality was reused.

☐ Responsibilities remain separated.

☐ Security checks were implemented.

☐ Validation is complete.

☐ Output is escaped.

☐ Performance was considered.

☐ Naming is descriptive.

☐ Documentation was updated if necessary.

---

## Red Flags

Stop and review the implementation if you notice:

- duplicated code;
- large functions;
- large classes;
- deeply nested conditions;
- repeated database queries;
- business logic inside templates;
- direct SQL;
- hardcoded values;
- missing capability checks;
- inconsistent naming.

These usually indicate architectural issues.

---

## Completion Criteria

An implementation is considered free of common engineering mistakes when:

- existing architecture has been respected;
- duplication has been minimized;
- responsibilities remain clear;
- security has been verified;
- maintainability has been preserved;
- future extension is straightforward.

---

## Summary

Professional WordPress development is largely about avoiding predictable mistakes.

Most technical debt is created through small architectural shortcuts rather than large design failures.

Engineers and AI coding agents should continuously compare new code against these common mistakes before considering a task complete.