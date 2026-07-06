# WordPress Best Practices

## Purpose

This document defines the engineering best practices for developing professional WordPress applications.

These principles apply to themes, plugins, headless WordPress projects, WooCommerce stores, Gutenberg blocks, Divi modules, REST APIs, and enterprise WordPress solutions.

The objective is to create maintainable, secure, scalable, and predictable software that integrates naturally with the WordPress ecosystem.

---

# Core Philosophy

Write code that another engineer can confidently modify two years from now.

Every implementation should optimize for:

- readability;
- maintainability;
- scalability;
- consistency;
- security;
- performance.

The best implementation is usually the simplest one that satisfies the requirements.

---

# Design Before Coding

Never begin implementation immediately.

Before writing code:

- understand the business requirements;
- review the existing architecture;
- search for reusable functionality;
- identify integration points;
- define an implementation plan.

Planning reduces bugs and unnecessary refactoring.

---

# Reuse Before Creating

Always search the project before creating:

- services;
- helper functions;
- components;
- hooks;
- REST endpoints;
- templates;
- block controls;
- Divi modules.

Duplicate code increases maintenance costs.

---

# Follow WordPress APIs

Prefer WordPress APIs over custom implementations.

Examples:

- REST API
- Settings API
- Options API
- Metadata API
- Transients API
- WP_Query
- WP_Filesystem
- WP_Cron

Using established APIs improves compatibility and future upgrades.

---

# Keep Business Logic Separate

Business logic should never be embedded inside:

- templates;
- block rendering files;
- shortcode callbacks;
- REST controllers;
- hook callbacks.

Business rules belong inside dedicated services.

---

# Write Small Functions

Functions should perform one responsibility.

Good characteristics:

- descriptive name;
- predictable behavior;
- minimal side effects;
- reusable;
- easy to test.

Large functions usually indicate multiple responsibilities.

---

# Keep Templates Simple

Templates should focus on presentation.

Templates may:

- display data;
- call helper methods;
- render components.

Templates should not:

- perform database queries;
- implement business rules;
- contain complex conditional logic.

---

# Respect Existing Architecture

Do not introduce new architectural patterns unless explicitly required.

Follow:

- existing folder structure;
- naming conventions;
- dependency direction;
- coding style;
- service organization.

Consistency is more valuable than personal preference.

---

# Validate, Sanitize, Escape

Every feature should follow three rules:

Validate input.

Sanitize stored data.

Escape rendered output.

Never assume external data is safe.

---

# Capability Checks

Administrative functionality should always verify user permissions.

Examples:

- current_user_can()
- capability mapping
- REST permission callbacks

Never rely solely on hidden UI elements.

---

# Prefer Dependency Injection

Dependencies should be explicit whenever practical.

Prefer:

```text
Service
    ↓
Repository
    ↓
API
```

Avoid hidden dependencies through global state.

---

# Keep Hooks Focused

Each action or filter should perform one clear responsibility.

Prefer:

```text
Register Hook
        ↓
Call Service
        ↓
Return Result
```

Avoid placing large amounts of business logic directly inside hook callbacks.

---

# Error Handling

Handle expected failures gracefully.

Examples:

- invalid input;
- missing resources;
- failed API requests;
- unavailable services.

Error messages should help developers while remaining safe for users.

---

# Logging

Log useful operational information.

Examples:

- API failures;
- external integrations;
- background jobs;
- unexpected exceptions.

Avoid excessive logging that obscures important events.

---

# Performance Awareness

Before adding new code consider:

- query count;
- caching opportunities;
- asset loading;
- image optimization;
- REST response size;
- unnecessary rendering.

Performance should be part of implementation—not an afterthought.

---

# Documentation

Document:

- public APIs;
- complex business rules;
- configuration;
- environment variables;
- unusual architectural decisions.

Code explains how.

Documentation explains why.

---

# AI Execution Checklist

## Investigation

☐ Understand the business goal.

☐ Review project architecture.

☐ Search existing implementations.

☐ Identify reusable code.

---

## Planning

☐ Define implementation strategy.

☐ Preserve architecture.

☐ Minimize complexity.

☐ Identify risks.

---

## Implementation

☐ Follow WordPress APIs.

☐ Separate responsibilities.

☐ Validate input.

☐ Sanitize data.

☐ Escape output.

☐ Reuse existing code.

---

## Verification

☐ Verify functionality.

☐ Verify security.

☐ Verify performance.

☐ Verify maintainability.

☐ Verify documentation.

---

# Common Mistakes

Avoid:

Creating duplicate functionality.

Ignoring WordPress APIs.

Writing business logic inside templates.

Hardcoding configuration values.

Skipping capability checks.

Skipping escaping.

Mixing unrelated responsibilities.

Overengineering simple solutions.

---

# Completion Criteria

A WordPress implementation follows best practices when:

- responsibilities are clearly separated;
- existing architecture is respected;
- WordPress APIs are used appropriately;
- security has been considered;
- performance has been reviewed;
- documentation is sufficient;
- future maintenance is straightforward.

---

# Summary

Professional WordPress development is built on consistency, reuse, and respect for the platform.

Following these practices results in software that is easier to maintain, safer to extend, and more resilient as projects grow.