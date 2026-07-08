---
id: php/readme
topic: php
slug: readme
title: "PHP Engineering Standards"
type: index
order: -1
status: ready
tags: [php]
related: []
when_to_use: "Read first when starting any PHP work, to see how this section's docs fit together."
---
# PHP Engineering Standards

## Purpose

This section defines the engineering standards, idioms, and best practices for writing
modern PHP. PHP in 2026 means PHP 8.3+ (8.4 current, 8.1 the practical floor): a
strictly-typed, object-oriented language with a mature ecosystem of Composer, PSR
standards, static analysis (PHPStan/Psalm), and Pest/PHPUnit. Pre-8.0 patterns — untyped
code, manual `require` chains, `mysql_*` — are legacy to be replaced, not copied.

The objective is idiomatic, safe, testable PHP: every file under `declare(strict_types=1)`,
every dependency wired through Composer and PSR-4, every module analyzed and formatted in
CI. From language fundamentals and OOP through security, performance, architecture, and
production operations, these docs point to the version-appropriate feature for each concern
and the sibling doc that governs it.

These standards are written for both human engineers and AI coding assistants, so that
neither writes PHP as if it were 2012.

---

## Scope

This documentation covers:

- Language fundamentals, types, functions, and OOP
- Namespaces, autoloading, and Composer
- Error handling and exceptions
- Files, HTTP, database access, and CLI
- Modern features: attributes, generators, enums
- Dependency injection, design patterns, and clean code
- PSR standards, modern PHP, and architecture
- Security, performance, testing, and debugging
- Tooling, production, and engineering principles

---

## Learning Path

Study the documents in the following order.

### Language Core
- [00. Overview](00-overview.md)
- [01. Language Fundamentals](01-language-fundamentals.md)
- [02. Types](02-types.md)
- [03. Functions](03-functions.md)
- [04. OOP](04-oop.md)
- [05. Namespaces](05-namespaces.md)

### Structure & Tooling
- [06. Autoloading](06-autoloading.md)
- [07. Composer](07-composer.md)
- [24. PSR Standards](24-psr-standards.md)
- [28. Tooling](28-tooling.md)

### Modern Features
- [17. Attributes](17-attributes.md)
- [18. Generators](18-generators.md)
- [19. Enums](19-enums.md)
- [23. Modern PHP](23-modern-php.md)

### Errors, I/O & Platform
- [08. Error Handling](08-error-handling.md)
- [09. Exceptions](09-exceptions.md)
- [10. Files](10-files.md)
- [11. HTTP](11-http.md)
- [12. Database](12-database.md)
- [16. CLI](16-cli.md)

### Design
- [20. Dependency Injection](20-dependency-injection.md)
- [21. Design Patterns](21-design-patterns.md)
- [22. Clean Code](22-clean-code.md)
- [29. Architecture](29-architecture.md)
- [30. Engineering Principles](30-engineering-principles.md)

### Quality & Delivery
- [13. Security](13-security.md)
- [14. Performance](14-performance.md)
- [15. Testing](15-testing.md)
- [25. Debugging](25-debugging.md)
- [26. Best Practices](26-best-practices.md)
- [27. Production](27-production.md)

### Verification
- [98. Production Checklist](98-production-checklist.md)
- [99. AI Review Checklist](99-ai-review-checklist.md)
- [100. Common Anti-Patterns](100-common-antipatterns.md)

---

## Engineering Principles

Every PHP change should satisfy the following principles:

- Target only a supported version (8.3/8.4); never rely on end-of-life APIs.
- Begin every file with `declare(strict_types=1)` and type every parameter, return, and property.
- Manage dependencies and autoloading through Composer and PSR-4, never manual includes.
- Follow the PSRs; deviating from shared conventions costs interoperability.
- Inject dependencies instead of constructing them or reaching for global state.
- Make failure explicit with typed exceptions, not silent error codes.
- Separate concerns — keep HTML out of logic and logic out of templates.
- Treat all input as untrusted; escape on output and use parameterized queries.
- Run PHPStan/Psalm at a high level and a formatter in CI so style and type errors never reach review.
- Prefer the newest stable syntax the target version supports for explicit, analyzable code.

---

## Intended Audience

These standards are intended for:

- Backend Engineers
- Fullstack Engineers
- Tech Leads
- Software Architects
- AI Coding Assistants
- Code Reviewers

---

## Summary

Following these standards keeps PHP code strictly typed, PSR-compliant, and secure,
using modern language features rather than legacy idioms.
