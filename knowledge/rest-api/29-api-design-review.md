---
id: rest-api/29-api-design-review
topic: rest-api
slug: api-design-review
title: "API Design Review"
type: doc
order: 29
status: ready
tags: [rest-api, api-design-review]
related: [rest-api/03-resource-design, rest-api/07-status-codes, rest-api/14-versioning, rest-api/27-best-practices, rest-api/21-openapi]
when_to_use: "Read before approving a new or changed REST endpoint, whether reviewing a PR or a design proposal."
---
# API Design Review

## Purpose

This document defines how to review a REST API design *before* it ships and its contract
freezes. It is a process doc: what to check, in what order, and where to push back. The
goal is to catch breaking, inconsistent, or unsafe design while it is still cheap to
change — a comment in a review, not a versioned migration a year later. It draws the
concrete rules from [best practices](27-best-practices.md) and applies them as review gates.

## Why It Matters

The single cheapest moment to fix an API design flaw is before the first client integrates.
After that, the contract is load-bearing: a renamed field, a changed status code, or a new
required parameter breaks live consumers, and the only remedies are a slow deprecation or a
new version. Design review is the last gate before that lock-in. A ten-minute review that
catches a plural-vs-singular inconsistency or a missing pagination cap saves months of
compatibility debt. Reviewers are the guardians of consistency — the property that lets the
whole API feel like one coherent surface.

## Core Principles

- **Review the contract, not just the code.** The request/response shape, status codes,
  and error format are what clients depend on. Correct code behind a bad contract is still
  a bad API.
- **Breaking changes are the highest-priority finding.** Removing or renaming a field,
  tightening validation, or changing a status code breaks clients. Flag these first and
  require a version bump. See [versioning](14-versioning.md).
- **Consistency is a review gate, not a preference.** A new endpoint must match the API's
  existing conventions for naming, pagination, errors, and dates — even if the author
  prefers otherwise.
- **Check the spec and the implementation together.** The OpenAPI definition must match
  what the code actually does; a drifted spec is a lie clients will trust. See [OpenAPI](21-openapi.md).
- **Verify the unhappy paths.** Most design gaps are in errors, edge cases, and auth, not
  the happy path. Review what happens on bad input, missing objects, and unauthorized callers.

## Best Practices

- Confirm resources are nouns and actions use HTTP methods; reject verbs in paths.
- Check that every status code is semantically correct, especially `201`+`Location` on
  create, `4xx` vs `5xx`, and `409` on conflict. See [status codes](07-status-codes.md).
- Verify collections are paginated with the API's standard strategy and a capped page size.
- Confirm the error response uses the shared envelope with a stable machine code.
- Diff the change against the current contract for breaking changes: removed/renamed
  fields, new required params, narrowed enums, changed types.
- Check that input is validated and the caller is authorized on every new route — including
  object-level ownership. See [security](24-security.md).
- Ensure the OpenAPI spec is updated in the same change and that examples are accurate.
- Look for consistency drift: casing, date format, id format, and naming versus siblings.

## Examples

**Good Example** — a review comment that catches a breaking change

```diff
# PR changes GET /v1/users response:
- "role": "admin"            # was a single string clients already parse
+ "roles": ["admin"]         # renamed + retyped

# Review comment:
# BLOCKING: renaming `role` -> `roles` and changing string -> array is a breaking
# change; existing clients read `role` as a string. Either keep `role` and ADD
# `roles` (additive, non-breaking), or ship this under /v2. Also update the OpenAPI
# schema and the pagination example, which still shows `role`.
```

**Bad Example** — an approval that misses the contract problems

```diff
# PR adds POST /v1/user  (singular) that returns 200 with { "ID": 5 }
# Review comment:
# "LGTM, tests pass. 👍"

# Missed: `/user` is singular while the rest of the API uses plural `/users`;
# a create should return 201 + Location, not 200; `ID` is PascalCase while every
# other field is snake_case; no OpenAPI update. All are now frozen in the contract.
```

## Common Mistakes

- Approving on "tests pass" without reviewing the request/response contract.
- Missing a breaking change (renamed field, changed type/status) that needs a version bump.
- Letting a new endpoint diverge from existing naming, pagination, or error conventions.
- Not checking that the OpenAPI spec was updated to match the change.
- Reviewing only the happy path and skipping error, auth, and edge-case behavior.
- Treating consistency feedback as optional style nitpicks rather than review gates.

## Production Tips

- Automate the mechanical checks: run an API linter (Spectral) and a contract/spec test in
  CI so reviewers spend their attention on design judgment, not casing typos.
- Keep a short design-review checklist in the PR template so nothing is skipped.
- For significant new APIs, review a written design proposal before implementation, not
  just the finished PR — it is far cheaper to change a doc than shipped code.

## AI Review Checklist

- Are resources nouns, with actions expressed as HTTP methods?
- Are all status codes semantically correct (esp. `201`+`Location`, `4xx` vs `5xx`)?
- Does the change introduce any breaking change without a version bump?
- Is the new endpoint consistent with siblings in naming, casing, dates, and pagination?
- Does the response use the shared error envelope with a stable code?
- Is input validated and the caller authorized, including object-level ownership?
- Was the OpenAPI spec updated to match, with accurate examples?
- Were error and edge-case behaviors reviewed, not just the happy path?

## Related

- `knowledge/rest-api/03-resource-design.md`
- `knowledge/rest-api/07-status-codes.md`
- `knowledge/rest-api/14-versioning.md`
- `knowledge/rest-api/27-best-practices.md`
- `knowledge/rest-api/21-openapi.md`
