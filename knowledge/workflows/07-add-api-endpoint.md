---
id: workflows/07-add-api-endpoint
topic: workflows
slug: add-api-endpoint
title: "Workflow — Add an API Endpoint"
type: doc
order: 7
status: ready
tags: [workflows, add-api-endpoint]
related: []
when_to_use: "Follow this workflow when adding a new API endpoint to an existing project."
---
# Workflow — Add an API Endpoint

## Purpose

This workflow defines the standard process for implementing a new API endpoint in an existing project.

The objective is to create a predictable, secure, maintainable, and well-documented API that follows the project's existing architecture and conventions.

An API endpoint is part of a contract with its consumers.

Changes should be deliberate and backward compatible whenever possible.

---

## Goal

Implement an endpoint that:

- satisfies business requirements;
- follows existing API conventions;
- validates all input;
- returns consistent responses;
- handles errors correctly;
- is secure;
- is testable.

---

## Workflow Overview

```
Understand Requirements
        ↓
Analyze Existing API
        ↓
Design Contract
        ↓
Validate Inputs
        ↓
Implement Business Logic
        ↓
Implement Endpoint
        ↓
Handle Errors
        ↓
Test
        ↓
Document
        ↓
Complete
```

---

## Step 1 — Understand the Requirements

Determine:

- business objective;
- endpoint purpose;
- request flow;
- response expectations;
- authentication requirements;
- authorization requirements;
- validation rules.

Do not implement an endpoint based on assumptions.

---

## Step 2 — Analyze Existing APIs

Inspect similar endpoints.

Review:

- routing conventions;
- controller structure;
- services;
- DTOs;
- validation;
- error handling;
- response format;
- authentication middleware;
- logging.

New endpoints should look like existing endpoints.

---

## Step 3 — Design the API Contract

Define the endpoint before writing code.

Specify:

Method

Path

Request body

Query parameters

Path parameters

Headers

Authentication

Authorization

Success response

Error responses

HTTP status codes

The contract should remain stable.

---

## Step 4 — Validate Input

Validate every external input.

Examples:

- required fields;
- string length;
- numeric ranges;
- enum values;
- dates;
- UUIDs;
- email addresses;
- file uploads.

Never trust client input.

---

## Step 5 — Implement Business Logic

Business rules belong in the business layer.

Avoid placing business logic inside:

- controllers;
- route handlers;
- middleware.

Controllers should coordinate work, not perform it.

---

## Step 6 — Implement the Endpoint

The endpoint should:

- receive the request;
- validate input;
- call the appropriate service;
- return the response;
- handle errors consistently.

Keep controllers small.

---

## Step 7 — Handle Errors

Return predictable error responses.

Verify:

- validation failures;
- unauthorized access;
- forbidden actions;
- missing resources;
- conflicts;
- unexpected failures.

Never expose internal implementation details.

---

## Step 8 — Test the Endpoint

Verify:

- valid requests;
- invalid requests;
- missing fields;
- unauthorized access;
- forbidden access;
- unexpected errors;
- edge cases.

Every public endpoint should be tested.

---

## Step 9 — Update Documentation

Update documentation when required.

Examples:

- OpenAPI / Swagger;
- API reference;
- README;
- Postman collection;
- environment variables;
- authentication guide.

Documentation is part of the API.

---

## API Design Principles

Prefer:

Resource-oriented endpoints

Consistent naming

Standard HTTP methods

Predictable responses

Consistent error format

Idempotent operations when appropriate

Avoid:

RPC-style naming

Inconsistent status codes

Multiple response formats

Hidden side effects

Breaking existing consumers

---

## AI Execution Checklist

## Investigation

☐ Read the requirements.

☐ Review similar endpoints.

☐ Review routing conventions.

☐ Review authentication.

☐ Review response format.

---

## Planning

☐ Define API contract.

☐ Define validation rules.

☐ Define error responses.

☐ Identify reusable services.

---

## Implementation

☐ Reuse existing architecture.

☐ Keep controllers thin.

☐ Validate all input.

☐ Preserve response consistency.

☐ Avoid duplicate business logic.

---

## Verification

☐ Test successful requests.

☐ Test validation failures.

☐ Test authentication.

☐ Test authorization.

☐ Test error responses.

☐ Update documentation.

---

## Security Checklist

Before completion verify:

☐ Authentication is enforced.

☐ Authorization is enforced.

☐ Input is validated.

☐ Sensitive information is not exposed.

☐ Error messages are safe.

☐ Logging contains useful information.

☐ Secrets are never returned.

---

## Common Mistakes

Avoid:

Embedding business logic in controllers.

Skipping validation.

Returning inconsistent response formats.

Using incorrect HTTP status codes.

Creating duplicate services.

Ignoring authorization.

Breaking existing API contracts.

Forgetting documentation.

---

## Completion Criteria

The workflow is complete only if:

- requirements are satisfied;
- API contract is implemented;
- validation is complete;
- authentication and authorization are correct;
- responses follow project standards;
- tests pass;
- documentation is updated.

---

## Expected AI Output

After completing this workflow, the AI should explain:

- endpoint purpose;
- request structure;
- response structure;
- validation strategy;
- reused services;
- modified files;
- testing performed;
- remaining considerations.

---

## Summary

A well-designed API endpoint is predictable, secure, and easy to maintain.

The endpoint should integrate seamlessly into the existing API, follow established conventions, and provide a stable contract for all consumers.