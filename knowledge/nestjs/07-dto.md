---
id: nestjs/07-dto
topic: nestjs
slug: dto
title: "NestJS Data Transfer Objects (DTO)"
type: doc
order: 7
status: ready
tags: [nestjs, dto]
related: []
when_to_use: ""
---
# NestJS Data Transfer Objects (DTO)

## Purpose

This document defines the engineering standards for designing and using Data Transfer Objects (DTOs) in NestJS applications.

The objective is to establish a clear contract between the API and its consumers while keeping transport models independent from domain models and persistence models.

DTOs define the API contract.

They are not business objects or database entities.

---

## Core Principle

Separate transport models from business models.

Never expose persistence models directly through the API.

---

## DTO Goals

Every DTO should provide:

- explicit API contracts;
- request validation;
- predictable serialization;
- version compatibility;
- type safety;
- documentation support.

DTOs should describe data—not behavior.

---

## Responsibilities

DTOs are responsible for:

- defining API input;
- defining API output;
- validation metadata;
- serialization rules;
- API documentation.

DTOs should never contain:

- business logic;
- persistence logic;
- authorization logic;
- database annotations.

---

## Request Flow

Typical flow:

```
HTTP Request

↓

Request DTO

↓

Validation

↓

Controller

↓

Service

↓

Repository

↓

Database

↓

Domain Model

↓

Response DTO

↓

HTTP Response
```

Every layer has a dedicated responsibility.

---

## DTO Categories

A feature typically contains:

```
dto/

    create-user.dto.ts

    update-user.dto.ts

    login.dto.ts

    user-response.dto.ts

    pagination.dto.ts
```

Separate DTOs by purpose.

---

## Request DTOs

Request DTOs describe incoming data.

Examples:

- CreateUserDto
- UpdateUserDto
- LoginDto
- ChangePasswordDto

Every public endpoint accepting a request body should use a dedicated Request DTO.

---

## Response DTOs

Response DTOs define outgoing data.

Examples:

- UserResponseDto
- ProductResponseDto
- OrderSummaryDto

Never return ORM entities directly.

---

## Why Entities Must Not Be Returned

Avoid:

```
Controller

↓

return prisma.user.findUnique(...)
```

Problems include:

- leaking internal fields;
- accidental password exposure;
- ORM coupling;
- unstable API contracts;
- serialization inconsistencies.

Always map entities to Response DTOs.

---

## Mapper Pattern

Use dedicated mappers.

Example:

```
UserEntity

↓

UserMapper

↓

UserResponseDto
```

Mapping should remain centralized.

Avoid performing mapping throughout controllers.

---

## Validation

Request DTOs should validate:

- required fields;
- formats;
- lengths;
- ranges;
- enums;
- nested objects.

Invalid input should never reach business logic.

---

## Nested DTOs

Nested objects should use dedicated DTOs.

Example:

```
CreateOrderDto

↓

CustomerDto

↓

AddressDto
```

Avoid anonymous nested object definitions.

---

## Partial Updates

Use dedicated update DTOs.

Typical pattern:

```
CreateUserDto

↓

UpdateUserDto
```

Update DTOs should clearly express optional fields.

---

## Serialization

Response DTOs should control serialization.

Typical responsibilities:

- hide internal fields;
- rename properties;
- transform values;
- expose computed values.

Serialization rules should remain predictable.

---

## Sensitive Data

Never expose:

- passwords;
- password hashes;
- API keys;
- refresh tokens;
- internal identifiers;
- security metadata.

Sensitive data should never leave the backend.

---

## Pagination DTOs

Collection endpoints should use dedicated DTOs.

Typical request:

```
page

limit

sort

filter
```

Typical response:

```
items

total

page

limit
```

Maintain a consistent pagination contract.

---

## Versioning

Public APIs should support DTO versioning when breaking changes occur.

Example:

```
UserResponseV1Dto

UserResponseV2Dto
```

Avoid modifying existing public contracts incompatibly.

---

## Reusability

Share DTOs only when semantics are identical.

Avoid creating generic DTOs that attempt to satisfy unrelated endpoints.

---

## Documentation

DTOs should serve as the source of truth for API documentation.

Every public property should be:

- named clearly;
- typed correctly;
- documented when necessary.

---

## Performance

Avoid unnecessary DTO nesting.

Avoid excessively large response objects.

Transfer only the data required by clients.

---

## Security

Review every Response DTO for:

- sensitive fields;
- internal metadata;
- authorization leaks.

Assume every exposed property becomes part of the public API.

---

## Testing

Verify:

- validation rules;
- serialization;
- mapping;
- excluded fields;
- transformed properties.

DTO contracts should remain stable.

---

## AI Execution Checklist

## Investigation

☐ Identify API contract.

☐ Separate input from output.

☐ Review validation requirements.

☐ Review serialization rules.

---

## Planning

☐ Create dedicated Request DTOs.

☐ Create dedicated Response DTOs.

☐ Implement mappers.

☐ Hide sensitive fields.

---

## Verification

☐ ORM entities not exposed.

☐ Validation complete.

☐ Serialization correct.

☐ Mapping centralized.

☐ API contract documented.

☐ DTOs independently testable.

---

## Common Mistakes

Avoid:

Returning Prisma models directly.

Returning TypeORM entities.

Sharing the same DTO for requests and responses.

Embedding business logic inside DTOs.

Skipping validation.

Duplicating mapping logic.

Leaking sensitive fields.

Treating DTOs as domain models.

---

## Completion Criteria

A DTO implementation is complete when:

- request and response models are separated;
- validation is comprehensive;
- ORM entities remain internal;
- mapping is centralized;
- serialization is predictable;
- the public API contract is stable and well documented.

---

## Summary

DTOs define the public language of a NestJS application.

By separating transport models from domain and persistence models, validating all incoming data, centralizing mapping, and carefully controlling serialization, applications become safer, easier to evolve, and more resilient to internal implementation changes.