---
id: nestjs/08-validation
topic: nestjs
slug: validation
title: "NestJS Validation"
type: doc
order: 8
status: ready
tags: [nestjs, validation]
related: []
when_to_use: ""
---
# NestJS Validation

## Purpose

This document defines the engineering standards for validating data in NestJS applications.

The objective is to ensure that all incoming data is validated consistently, securely, and predictably before reaching business logic.

Validation protects the application boundary.

Business rules remain inside services.

---

## Core Principle

Validate input immediately.

Reject invalid data before it enters the application.

---

## Validation Goals

Every validation strategy should provide:

- predictable behavior;
- fail-fast execution;
- clear error messages;
- consistent API responses;
- strong type safety;
- reusable validation rules.

Validation should reduce the number of invalid states the application can reach.

---

## Validation Layers

Validation exists at multiple layers.

```
HTTP Request

↓

Transport Validation

↓

Controller

↓

Business Validation

↓

Service

↓

Repository
```

Each layer validates different concerns.

---

## Transport Validation

Transport validation verifies:

- required fields;
- data types;
- formats;
- ranges;
- enums;
- array structure;
- nested objects.

Transport validation should not verify business rules.

---

## Business Validation

Business validation verifies rules such as:

- email uniqueness;
- account ownership;
- inventory availability;
- payment status;
- business constraints.

Business validation belongs inside services.

---

## ValidationPipe

Enable a global `ValidationPipe`.

Recommended production configuration:

- validate all DTOs;
- transform incoming values;
- reject unknown properties;
- forbid unexpected fields.

Validation should be centralized.

---

## DTO Validation

Every request DTO should define validation rules.

Typical examples:

- string length;
- numeric range;
- email format;
- UUID format;
- enum values;
- nested DTO validation.

Every public endpoint accepting request data should use DTO validation.

---

## Nested Validation

Validate nested objects explicitly.

Example hierarchy:

```
CreateOrderDto

↓

CustomerDto

↓

AddressDto
```

Every nested object should have its own DTO.

---

## Array Validation

Arrays should validate:

- item type;
- minimum length;
- maximum length;
- uniqueness when required.

Avoid accepting arbitrary arrays.

---

## Custom Validators

Create custom validators for reusable domain-independent rules.

Examples:

- password strength;
- phone number format;
- tax identifier format;
- country code validation.

Keep custom validators focused and reusable.

---

## Business Rules

Business rules should never be implemented as DTO validation.

Incorrect example:

```
Email must be unique
```

Correct location:

```
UsersService
```

Validation attributes cannot replace business logic.

---

## Fail-Fast

Reject invalid requests immediately.

Avoid allowing partially valid requests to continue through the application.

---

## Error Messages

Validation errors should be:

- consistent;
- human-readable;
- predictable;
- machine-consumable.

Do not expose internal implementation details.

---

## Sanitization

Normalize data before business processing when appropriate.

Examples:

- trimming whitespace;
- lowercasing email addresses;
- removing duplicate separators;
- converting numeric strings.

Sanitization should be deterministic.

---

## Transformation

Incoming values may be transformed into:

- numbers;
- booleans;
- dates;
- enums.

Transformation should occur before business logic executes.

---

## Unknown Fields

Unexpected request fields should be rejected.

Allowing arbitrary fields increases security risks and API ambiguity.

---

## Alternative Validators

Alternative validation libraries may be appropriate.

Examples:

- Zod;
- Joi;
- Yup.

When selected, validation strategy should remain consistent across the application.

---

## API Documentation

Validation rules should align with API documentation.

Consumers should understand:

- required fields;
- optional fields;
- constraints;
- formats.

Documentation and validation should never contradict each other.

---

## Performance

Validation should remain efficient.

Avoid:

- duplicate validation;
- unnecessary object transformations;
- repeated parsing.

Business logic should receive already validated data.

---

## Security

Validation helps prevent:

- malformed requests;
- injection attempts;
- oversized payloads;
- invalid identifiers;
- unexpected object structures.

Validation is part of the application's security model.

---

## Testing

Verify:

- valid input;
- invalid input;
- missing fields;
- nested validation;
- transformation;
- custom validators.

Validation should remain deterministic.

---

## AI Execution Checklist

## Investigation

☐ Identify request contract.

☐ Separate transport and business validation.

☐ Review nested objects.

☐ Review security requirements.

---

## Planning

☐ Validate DTOs.

☐ Reject unknown fields.

☐ Transform values.

☐ Centralize validation.

---

## Verification

☐ Validation complete.

☐ Business rules isolated.

☐ Error messages consistent.

☐ Unknown fields rejected.

☐ Transformation verified.

☐ Validation independently testable.

---

## Common Mistakes

Avoid:

Putting business validation inside DTOs.

Skipping validation on internal endpoints.

Accepting arbitrary JSON.

Duplicating validation in controllers.

Performing database lookups inside validators.

Returning inconsistent validation errors.

Trusting client-side validation.

---

## Completion Criteria

Validation is complete when:

- every public endpoint validates incoming data;
- transport validation is separated from business validation;
- unknown fields are rejected;
- data is normalized consistently;
- validation errors are predictable;
- business logic receives only validated input.

---

## Summary

Validation establishes the first line of defense for every NestJS application.

By validating all incoming requests, separating transport validation from business rules, rejecting unexpected input, and enforcing consistent validation behavior, applications become more secure, reliable, and easier to maintain.