---
id: rest-api/21-openapi
topic: rest-api
slug: openapi
title: "OpenAPI"
type: doc
order: 21
status: ready
tags: [rest-api, openapi]
related: [rest-api/22-swagger, rest-api/08-validation, rest-api/14-versioning, rest-api/23-testing, rest-api/27-best-practices]
when_to_use: "Read before writing or reviewing an API contract, generating clients/servers, or wiring request validation from a spec."
---
# OpenAPI

## Purpose

This document defines how to describe a REST API with the OpenAPI Specification (OAS
3.1, the current version). An OpenAPI document is a machine-readable contract: it lists
every path, method, parameter, request body, response, and schema. This guide covers
how to structure that contract so it can drive validation, code generation, and docs
from one source of truth.

OpenAPI answers "what exactly does this API accept and return?" — in a form both humans
and tools can consume without reading the implementation.

## Why It Matters

Without a formal contract, an API's behavior lives only in code and in tribal memory.
Clients guess field names, integrations break silently on a rename, and documentation
drifts out of date the moment it is written. An OpenAPI spec makes the contract
explicit and executable: you can generate typed clients and server stubs, validate live
requests against it, run contract tests, and render always-accurate docs. The spec
becomes the interface both sides agree on, so breaking changes are caught in review
rather than in production. The alternative — a contract that exists only implicitly — is
how integrations rot.

## Core Principles

- **The spec is the source of truth, not a byproduct.** Either write the spec first and
  generate/validate code from it (design-first), or generate it from annotated code —
  but pick one direction and keep them in sync in CI. A hand-maintained spec that
  duplicates the code will diverge.
- **OAS 3.1 aligns with JSON Schema.** Use full JSON Schema (`type`, `format`,
  `required`, `enum`, `oneOf`, `nullable` via `type: [..., "null"]`) so one schema can
  both document and validate a payload.
- **Model reuse with `components`.** Define shared schemas, parameters, responses, and
  security schemes once under `components` and `$ref` them. Duplication in a spec drifts
  exactly like duplication in code.
- **Every operation declares all its outcomes.** List each success and error status an
  endpoint can return, each with a schema. An undocumented `4xx` is a contract gap a
  client cannot handle.
- **Describe security in the spec.** Declare `securitySchemes` and apply them per
  operation so the contract states what auth each endpoint requires.

## Best Practices

- Give every operation a stable, unique `operationId` — code generators use it to name
  client methods; renaming it is a breaking change to generated SDKs.
- Define reusable error responses (e.g. a `Problem` schema per RFC 9457) under
  `components/responses` and reference them everywhere, so errors are shaped uniformly.
- Validate the spec itself in CI (lint with a tool like Spectral) to catch missing
  descriptions, undefined `$ref`s, and inconsistent naming before merge.
- Wire runtime request/response validation from the spec (e.g. `express-openapi-validator`)
  so drift between contract and code fails a test, not a customer call.
- Version the spec alongside the API and record breaking changes; see
  [versioning](14-versioning.md).
- Keep examples in the spec realistic and valid against their schema — they render in
  docs and seed contract tests.

## Examples

**Good Example** — a reusable, fully specified operation (OAS 3.1)

```yaml
paths:
  /users/{id}:
    get:
      operationId: getUser          # stable name → stable generated client method
      security: [{ bearerAuth: [] }] # this endpoint requires a bearer token
      parameters:
        - { name: id, in: path, required: true, schema: { type: string, format: uuid } }
      responses:
        "200":
          description: The user
          content:
            application/json:
              schema: { $ref: "#/components/schemas/User" } # reused, single definition
        "404": { $ref: "#/components/responses/NotFound" }   # shared error shape
components:
  schemas:
    User:
      type: object
      required: [id, email]
      properties:
        id:    { type: string, format: uuid }
        email: { type: string, format: email }
        name:  { type: [string, "null"] }   # explicitly nullable, JSON-Schema style
```

**Bad Example** — vague, unreusable, incomplete

```yaml
paths:
  /users/{id}:
    get:
      # No operationId → generators invent unstable names that churn every build.
      responses:
        "200":
          description: ok            # inlined, duplicated schema; no error responses
          content:
            application/json:
              schema:
                type: object         # untyped bag: no required fields, no formats.
                # Clients cannot tell what is guaranteed; validation is impossible.
```

## Common Mistakes

- Maintaining the spec by hand separately from the code, so the two silently diverge.
- Inlining and duplicating schemas instead of `$ref`-ing shared `components`.
- Documenting only the happy-path `200` and omitting the `4xx`/`5xx` a client must
  handle.
- Using loose `type: object` with no `properties`/`required`, giving tools nothing to
  validate.
- Omitting or renaming `operationId`, breaking every generated SDK downstream.
- Writing OAS 2.0 (Swagger) for a new API instead of current OAS 3.1.

## Production Tips

- Publish the spec at a stable URL (e.g. `/openapi.json`) and gate merges on it
  matching the running app via contract tests.
- Generate typed clients for internal consumers from the same spec so a contract change
  produces compile errors in dependents, not runtime surprises.
- Diff the spec between releases in CI to flag breaking changes automatically.

## AI Review Checklist

- Is there a single source of truth, kept in sync with code in CI?
- Does every operation have a stable `operationId` and declared `security`?
- Are shared schemas, parameters, and error responses defined once under `components`?
- Does each operation document all realistic success and error responses with schemas?
- Are schemas precise (types, formats, `required`, enums), not open `object` bags?
- Is the spec linted and used to validate live requests?

## Related

- `knowledge/rest-api/22-swagger.md`
- `knowledge/rest-api/08-validation.md`
- `knowledge/rest-api/14-versioning.md`
- `knowledge/rest-api/23-testing.md`
- `knowledge/rest-api/27-best-practices.md`
