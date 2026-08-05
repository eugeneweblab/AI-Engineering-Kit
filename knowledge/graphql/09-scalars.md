---
id: graphql/09-scalars
topic: graphql
slug: scalars
title: "Scalars"
type: doc
order: 9
status: ready
tags: [graphql, scalars, GraphQLError, parseValue, DateTime, serialize, Float, isNaN]
related: [graphql/03-types, graphql/10-input-types, graphql/02-schema, graphql/17-security, graphql/20-error-handling]
when_to_use: "Read before adding a custom scalar or handling dates, money, IDs, or other leaf values in a GraphQL schema."
---
# Scalars

## Purpose

This document defines how to use and author GraphQL **scalars**: the leaf types that hold
actual values (`Int`, `Float`, `String`, `Boolean`, `ID`, and custom ones like `DateTime`).
It is written so an agent picks correct scalar types, validates input at the type boundary,
and writes custom scalars whose `serialize`/`parseValue`/`parseLiteral` behave consistently.

Every field in a GraphQL response ultimately bottoms out in a scalar. Scalars are where the
schema's promises about data shape are actually enforced.

## Why It Matters

Scalars are the type system's first line of defence and its most common shortcut. Reaching
for `String` to represent a date, a money amount, or a URL throws away validation the schema
could have guaranteed and pushes the burden onto every client and resolver. The `Float`
scalar is IEEE-754 and silently loses precision on money — a real correctness bug. And a
custom scalar with asymmetric parse/serialize logic corrupts data on the way in or out in
ways that are extremely hard to trace, because the value looks plausible. Choosing the right
scalar is a cheap decision that prevents an expensive class of bugs.

## Core Principles

- **A scalar's job is to validate and normalize at the boundary.** `parseValue`/`parseLiteral`
  reject bad input before any resolver runs; `serialize` guarantees output shape. Use them.
- **Never use `Float` for money.** Represent currency as integer minor units (cents) or a
  string-backed decimal scalar. Binary floats cannot hold `0.10` exactly.
- **Prefer a well-known scalar library over hand-rolling.** `graphql-scalars` provides
  vetted `DateTime`, `EmailAddress`, `URL`, `UUID`, `JSON`, etc. Custom scalars are easy to
  get subtly wrong.
- **Keep serialize and parse symmetric.** What `serialize` emits must be re-parseable by
  `parseValue`. Asymmetry silently corrupts round-trips.
- **`ID` is an opaque string, not a number.** Never do arithmetic on it or assume it is an
  integer; treat it as a token.

## Best Practices

- Use `DateTime` (ISO-8601 / RFC-3339) rather than `String` or a Unix `Int`; it validates
  format and makes timezone handling explicit.
- Model money as `Int` cents (or a `Decimal`/`BigInt` scalar), never `Float`; document the
  currency and unit in the schema description.
- Adopt `graphql-scalars` for `EmailAddress`, `URL`, `UUID`, `PositiveInt`, etc., so
  validation lives in the type, not scattered across resolvers or [input types](10-input-types.md).
- In custom scalars, throw `GraphQLError` on invalid input from `parseValue`/`parseLiteral`
  so the client gets a clear boundary error, and handle both variable (`parseValue`) and
  inline-literal (`parseLiteral`) paths — forgetting the latter breaks hardcoded arguments.
- Constrain the `JSON` scalar tightly; it is an escape hatch that opts a field out of the
  type system and out of [security](17-security.md) validation. Prefer a real type.
- Make `serialize` defensive: it receives internal values and must reject or coerce
  unexpected shapes rather than emit malformed output.

## Examples

**Good Example** — a symmetric, validating custom scalar

```ts
import { GraphQLScalarType, Kind, GraphQLError } from "graphql";

export const DateTime = new GraphQLScalarType({
  name: "DateTime",
  description: "RFC-3339 date-time string, e.g. 2026-07-07T14:00:00Z",

  // Internal Date -> wire string. Symmetric with the parsers below.
  serialize(value: unknown): string {
    if (!(value instanceof Date) || isNaN(value.getTime())) {
      throw new GraphQLError("DateTime must serialize a valid Date");
    }
    return value.toISOString();
  },

  // Value from a query variable -> internal Date, validated at the boundary.
  parseValue(value: unknown): Date {
    if (typeof value !== "string") throw new GraphQLError("DateTime must be a string");
    const d = new Date(value);
    if (isNaN(d.getTime())) throw new GraphQLError("Invalid DateTime");
    return d;
  },

  // Value hardcoded inline in the query -> internal Date. Do NOT forget this path.
  parseLiteral(ast): Date {
    if (ast.kind !== Kind.STRING) throw new GraphQLError("DateTime must be a string literal");
    const d = new Date(ast.value);
    if (isNaN(d.getTime())) throw new GraphQLError("Invalid DateTime");
    return d;
  },
});
```

**Bad Example** — Float money and a stringly-typed date

```graphql
type Product {
  # Float is IEEE-754: 19.99 + 0.01 != 20.00. Currency corruption over time.
  price: Float!
  # String defers all validation to clients; every consumer re-parses and re-validates.
  createdAt: String!
}
```

## Common Mistakes

- Using `Float` for money, accumulating rounding error on every calculation.
- Using `String` for dates, emails, URLs, or UUIDs, discarding schema-level validation.
- Writing a custom scalar that implements `parseValue` but forgets `parseLiteral` (or
  vice-versa), so inline literals or variables silently fail or bypass validation.
- Asymmetric serialize/parse, corrupting values on round-trip.
- Treating `ID` as a number or doing arithmetic on it.
- Leaning on a permissive `JSON` scalar to dodge modelling the real type.

## AI Review Checklist

- Is money represented as integer minor units or a decimal scalar, never `Float`?
- Are dates/emails/URLs/UUIDs modelled with proper scalars, not `String`?
- Does each custom scalar implement `serialize`, `parseValue`, *and* `parseLiteral`?
- Are `serialize` output and `parseValue` input symmetric and re-parseable?
- Do parsers throw `GraphQLError` on invalid input rather than returning `null`?
- Is `ID` treated as an opaque string?
- Is any `JSON` scalar justified, or could a real type replace it?

## Related

- `knowledge/graphql/03-types.md`
- `knowledge/graphql/10-input-types.md`
- `knowledge/graphql/02-schema.md`
- `knowledge/graphql/17-security.md`
- `knowledge/graphql/20-error-handling.md`
