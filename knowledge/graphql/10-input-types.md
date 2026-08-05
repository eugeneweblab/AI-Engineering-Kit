---
id: graphql/10-input-types
topic: graphql
slug: input-types
title: "Input Types"
type: doc
order: 10
status: ready
tags: [graphql, input-types, GraphQLError, input, createUser, CreateUserInput, EmailAddress, BAD_USER_INPUT]
related: [graphql/05-mutations, graphql/09-scalars, graphql/03-types, graphql/17-security, graphql/29-schema-evolution]
when_to_use: "Read before defining arguments for a mutation or query, especially any operation that takes structured or optional input."
---
# Input Types

## Purpose

This document defines how to design GraphQL **input types**: the `input` objects used as
arguments to [mutations](05-mutations.md) and complex queries. It is written so an agent
shapes arguments that are evolvable, validated, and unambiguous — avoiding the giant
optional-everything blobs that make mutations impossible to reason about.

Input types are distinct from output object types: they may only contain scalars, enums,
and other input types (no interfaces, unions, or fields with resolvers). They exist so
GraphQL can validate structured arguments against the schema.

## Why It Matters

Input types are the public contract for *writing* to your system, and that contract is
hard to change once clients depend on it. Two problems dominate. First, **evolvability**:
passing many positional-feeling arguments, or reusing the output type as input, paints you
into a corner where you cannot add a field without breaking clients. Second, **validation
gaps**: the schema validates *shape* (is `email` a string?) but not *semantics* (is it a
valid email, under 320 chars, not already taken?). Agents routinely assume the schema
validated everything and skip the semantic checks, letting bad data through the front door.

## Core Principles

- **Wrap arguments in a single `input` object per mutation.** One `createUser(input: CreateUserInput!)`
  argument is additive-friendly; a list of loose scalar arguments is not. New fields can be
  added to an input without touching existing call sites.
- **Separate input types from output types.** Never reuse an output object as an argument;
  they evolve differently and inputs cannot hold resolver fields. See [types](03-types.md).
- **Non-null means required, and it is a breaking change to add later.** Only mark a field
  non-null if it is truly always required; adding a required field breaks existing clients.
- **Schema validation is shape-only; add semantic validation in the resolver.** Length,
  format, ranges, uniqueness, and cross-field rules are yours to enforce.
- **Use enums for closed sets, not free strings.** An enum makes invalid values
  unrepresentable and self-documents the allowed options.

## Best Practices

- Give each mutation its own tailored input type (`UpdateUserInput`, `CreateUserInput`);
  do not share one `UserInput` across create and update — their required fields differ.
- Use custom [scalars](09-scalars.md) (`EmailAddress`, `URL`, `PositiveInt`) so common
  validation lives in the type and never reaches the resolver malformed.
- For partial updates, prefer explicitly optional fields and treat "absent" and "null"
  distinctly: absent = leave unchanged, `null` = clear the value. Document this convention.
- Validate semantics in the resolver (or a validation layer) and return structured field
  errors, so clients can map a violation back to the offending input field.
- Provide sensible defaults via `= value` in the schema for optional fields to reduce
  client burden and make behaviour explicit.
- Keep input nesting shallow; deeply nested inputs are hard to validate and to evolve.
  Where nesting is needed, define named nested input types, not anonymous structures.
- Never accept an unvalidated `JSON` scalar as a stand-in for a real input type — it
  bypasses the whole point of input validation and [security](17-security.md).

## Examples

**Good Example** — single input object, enum, semantic validation

```graphql
enum AccountTier { FREE PRO ENTERPRISE }

input CreateUserInput {
  email: EmailAddress!        # custom scalar validates format at the boundary
  displayName: String!
  tier: AccountTier = FREE    # enum + default: invalid tiers are unrepresentable
}

type Mutation {
  # One input arg => adding fields later is additive, not breaking.
  createUser(input: CreateUserInput!): CreateUserPayload!
}
```

```ts
async function createUser(_p, { input }, ctx) {
  // Schema guaranteed shape; resolver enforces SEMANTICS the schema cannot.
  if (input.displayName.length > 80) {
    throw new GraphQLError("displayName too long", {
      extensions: { code: "BAD_USER_INPUT", field: "displayName" },
    });
  }
  if (await ctx.services.users.emailTaken(input.email)) {
    throw new GraphQLError("Email already registered", {
      extensions: { code: "BAD_USER_INPUT", field: "email" },
    });
  }
  return ctx.services.users.create(input);
}
```

**Bad Example** — loose args, output type as input, string enum, no validation

```graphql
type Mutation {
  # Loose positional-feeling args: adding one means editing every client call.
  # `tier: String` accepts "gold", "banana", anything. `User` is an OUTPUT type reused as input.
  createUser(email: String!, displayName: String!, tier: String!, profile: User): User
}
```

## Common Mistakes

- Spraying many scalar arguments across a mutation instead of one `input` object.
- Reusing an output object type as an input argument.
- Marking fields non-null that are not always required, then being unable to relax them.
- Adding a required (non-null, no-default) field to an existing input — a breaking change.
- Assuming schema validation covers semantics (length, format, uniqueness) and skipping resolver checks.
- Using `String` where a closed set of values calls for an enum.
- Conflating "field absent" with "field null" in update inputs, silently clearing data.

## Production Tips

- Track which clients send which input fields (via operation logging) before deprecating or
  tightening any input field; inputs are a contract you cannot break unilaterally.
- Centralize semantic validation in a schema-adjacent layer (e.g. zod/valibot) so the same
  rules apply across mutations and are unit-testable independent of GraphQL.

## AI Review Checklist

- Does each mutation take a single, dedicated `input` object rather than loose scalars?
- Are input types distinct from output types (no output object reused as input)?
- Are only genuinely-required fields non-null (and no new required field added to an existing input)?
- Is semantic validation (length, format, ranges, uniqueness) done in the resolver?
- Are closed value sets modelled as enums, not `String`?
- Do update inputs define absent-vs-null behaviour explicitly?
- Are custom scalars used for emails/URLs/ids instead of raw `String`?

## Related

- `knowledge/graphql/05-mutations.md`
- `knowledge/graphql/09-scalars.md`
- `knowledge/graphql/03-types.md`
- `knowledge/graphql/17-security.md`
- `knowledge/graphql/29-schema-evolution.md`
