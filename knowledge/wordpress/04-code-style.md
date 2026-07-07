---
id: wordpress/04-code-style
topic: wordpress
slug: code-style
title: "WordPress Code Style"
type: doc
order: 4
status: ready
tags: [wordpress, code-style]
related: []
when_to_use: ""
---
# WordPress Code Style

## Purpose

This document defines the coding style for WordPress projects.

The goal is to produce code that is easy to read, easy to review, and consistent across the entire codebase.

Code style is not about personal preference.

It is about reducing cognitive load for every engineer who works on the project.

---

## Core Principle

Optimize code for readability.

Code is read far more often than it is written.

Choose clarity over cleverness.

---

## General Rules

Every piece of code should be:

- readable;
- predictable;
- consistent;
- explicit;
- maintainable.

Avoid writing code that requires additional explanation.

---

## Follow Existing Conventions

Before writing code:

- review surrounding files;
- identify naming conventions;
- identify formatting conventions;
- identify architectural patterns.

Match the existing project instead of introducing a personal style.

---

## Naming

Names should describe intent.

Good examples:

```php
$productService

$userRepository

$newsletterSettings

$isUserAuthorized

$shouldDisplayBanner
```

Bad examples:

```php
$data

$tmp

$obj

$helper

$newData

$value2
```

If a name needs a comment to explain it, choose a better name.

---

## Functions

Functions should:

- perform one responsibility;
- have descriptive names;
- minimize side effects;
- return predictable values.

Prefer:

```php
getUserProfile()

updateProductPrice()

calculateDiscount()

sendNewsletter()
```

Avoid:

```php
process()

execute()

run()

handleEverything()
```

---

## Classes

Each class should have a single responsibility.

Examples:

```text
ProductService

OrderRepository

UserValidator

ApiController

ImageUploader
```

Avoid classes that combine unrelated responsibilities.

---

## Methods

Methods should be:

- short;
- descriptive;
- cohesive;
- easy to test.

Large methods usually indicate missing abstractions.

---

## Conditionals

Prefer:

```php
if ( ! $user ) {
    return;
}
```

Over:

```php
if ( $user ) {
    // 100 lines of code
}
```

Use early returns to reduce nesting.

---

## Nesting

Avoid deeply nested code.

Prefer:

```text
Validate

↓

Return early

↓

Continue
```

Instead of multiple nested `if` statements.

---

## Comments

Write comments only when they explain **why**, not **what**.

Good:

```php
// Required because the external API returns inconsistent IDs.
```

Poor:

```php
// Increment counter.
$counter++;
```

Well-written code should explain itself.

---

## Constants

Avoid magic values.

Prefer:

```php
const MAX_UPLOAD_SIZE = 10 * MB_IN_BYTES;
```

Instead of:

```php
10485760
```

Named constants improve readability.

---

## Arrays

Prefer meaningful keys.

Example:

```php
[
    'title' => 'Product',
    'price' => 100,
    'currency' => 'USD',
]
```

Avoid arrays whose meaning depends on element order.

---

## Hooks

Keep callbacks lightweight.

Preferred flow:

```text
Hook

↓

Validation

↓

Service

↓

Return
```

Business logic belongs in services.

---

## Templates

Templates should:

- render data;
- include template parts;
- call helper methods.

Templates should not:

- query the database;
- implement business logic;
- contain complex calculations.

---

## REST Controllers

Controllers should:

- validate requests;
- authorize users;
- call services;
- format responses.

Avoid embedding business logic inside controllers.

---

## Error Handling

Handle expected failures explicitly.

Prefer:

- early validation;
- meaningful exceptions;
- descriptive error messages;
- predictable return values.

Avoid silent failures.

---

## Formatting

Maintain consistency.

Examples:

- consistent indentation;
- consistent spacing;
- consistent import ordering;
- consistent file organization.

Formatting should never distract from the code.

---

## AI Execution Checklist

## Investigation

☐ Review nearby files.

☐ Identify naming conventions.

☐ Review project formatting.

☐ Review architecture.

---

## Implementation

☐ Use descriptive names.

☐ Keep functions small.

☐ Use early returns.

☐ Minimize nesting.

☐ Avoid duplicate logic.

☐ Separate responsibilities.

---

## Verification

☐ Review readability.

☐ Review consistency.

☐ Review maintainability.

☐ Review naming.

☐ Remove unnecessary comments.

---

## Common Mistakes

Avoid:

Generic variable names.

Large methods.

Large classes.

Deep nesting.

Magic numbers.

Business logic inside templates.

Business logic inside hooks.

Inconsistent formatting.

Excessive comments.

---

## Completion Criteria

Code style is considered successful when:

- another engineer can understand the code without explanation;
- naming is descriptive;
- responsibilities are clear;
- formatting is consistent;
- architecture is respected;
- maintenance is straightforward.

---

## Summary

Good code style is invisible.

It allows engineers to focus on solving business problems instead of decoding implementation details.

Consistency across the project is more valuable than individual coding preferences.