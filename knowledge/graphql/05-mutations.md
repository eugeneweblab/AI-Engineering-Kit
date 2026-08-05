---
id: graphql/05-mutations
topic: graphql
slug: mutations
title: "Mutations"
type: doc
order: 5
status: ready
tags: [graphql, mutations, publishPost, publish, UserError, PublishPostPayload, PublishPostInput, byId]
related: [graphql/04-queries, graphql/10-input-types, graphql/20-error-handling, graphql/19-authorization, graphql/02-schema]
when_to_use: "Read before designing or reviewing any write operation — create, update, delete, or state change."
---
# Mutations

## Purpose

This document defines how to design write operations in GraphQL: the `Mutation`
root, input types, payload types, error modeling, and execution semantics.
Mutations change server state, so correctness, validation, and predictable error
handling matter more here than anywhere else in the schema.

## Why It Matters

Mutations are where data integrity is won or lost. A mutation that trusts its
input, throws raw exceptions for expected failures, or returns nothing useful
forces clients to guess what happened and leaves the system in undefined states.
Unlike queries, mutations have side effects that cannot be retried blindly.
Designing them with explicit inputs, explicit payloads, and explicit error types
is what makes writes safe to build clients against.

## Core Principles

- **Top-level mutation fields run serially, in order.** The runtime executes
  root mutation fields one after another; nested fields within each still resolve
  like a query. Never rely on parallel ordering for writes.
- **One input type per mutation.** Take a single `input:` argument of a dedicated
  [input type](10-input-types.md), not a list of positional arguments. It is
  self-documenting and safe to extend.
- **Return a payload, not the bare entity.** Return a `...Payload` object so you
  can include the affected entity plus metadata, warnings, and typed errors
  without a breaking change later.
- **Model expected failures as data.** Validation failures, not-found, and
  conflicts are normal outcomes — return them in the payload (see
  [Error Handling](20-error-handling.md)), not as thrown 500s.
- **Validate and authorize inside the resolver.** The type system checks shape,
  never business rules or permissions. Every mutation re-checks both.

## Best Practices

- Name mutations `verbNoun` (`publishPost`, `archiveUser`) so the action is
  explicit; avoid generic `updatePost` that hides what changed.
- Make writes idempotent where possible, or accept a client-supplied idempotency
  key, so a retried request does not double-apply.
- Return the mutated entity in the payload so the client can update its cache
  without a follow-up query.
- Put user-facing, recoverable errors in a typed `errors` field on the payload;
  reserve thrown GraphQL errors for truly exceptional/unexpected failures.
- Authorize the action against the actor in [context](08-context.md) before
  touching data (see [Authorization](19-authorization.md)).
- Keep the resolver thin: validate, authorize, delegate to a service, map the
  result to the payload.

## Examples

**Good Example** — input type, typed payload, errors as data

```graphql
input PublishPostInput { postId: ID!, notify: Boolean = true }

type PublishPostPayload {
  post: Post                       # null when it failed
  userErrors: [UserError!]!        # expected, recoverable failures as data
}

type UserError { field: String, message: String! }

type Mutation {
  publishPost(input: PublishPostInput!): PublishPostPayload!
}
```

```ts
// Resolver: authorize, validate, delegate, map to payload — never trust input.
async function publishPost(_p, { input }, ctx) {
  const post = await ctx.posts.byId(input.postId);
  if (!post) return { post: null, userErrors: [{ message: "Post not found." }] };
  if (post.authorId !== ctx.actor.id)          // business rule, not a type rule
    return { post: null, userErrors: [{ message: "Not your post." }] };
  const published = await ctx.posts.publish(post.id, input.notify);
  return { post: published, userErrors: [] };
}
```

**Bad Example** — loose args, bare return, exceptions for expected cases

```graphql
type Mutation {
  # positional args are hard to evolve; returning Post loses error/metadata room
  publishPost(postId: ID!, notify: Boolean): Post
}
```

```ts
async function publishPost(_p, { postId }) {
  const post = await db.posts.find(postId);
  if (!post) throw new Error("not found");   // expected case thrown as 500-ish
  // no authorization check → any caller publishes anyone's post
  return db.posts.publish(postId);           // no way to report a warning
}
```

## Common Mistakes

- Using many positional arguments instead of one input type, making the mutation
  hard to extend and read.
- Returning the bare entity, leaving no room for typed errors, warnings, or
  metadata without a breaking change.
- Throwing generic errors for expected outcomes (not-found, validation, conflict)
  so clients cannot distinguish them from real failures.
- Skipping authorization because the field is "internal" — every mutation must
  check the actor.
- Assuming mutations retry safely; non-idempotent writes double-apply on retry.

## Production Tips

- Support idempotency keys on create/charge-style mutations so client retries and
  network re-sends do not duplicate effects.
- Wrap multi-step writes in a transaction inside the service so a partial failure
  rolls back rather than leaving inconsistent state.
- Emit an audit/event record for state changes so mutations are traceable after
  the fact.

## AI Review Checklist

- Does the mutation take a single input type and return a typed payload?
- Are expected failures returned as data (`userErrors`) rather than thrown?
- Is the actor authorized against the specific resource before the write?
- Is input validated in the resolver/service, independent of the type system?
- Is the write idempotent or protected by an idempotency key?

## Related

- `knowledge/graphql/04-queries.md`
- `knowledge/graphql/10-input-types.md`
- `knowledge/graphql/20-error-handling.md`
- `knowledge/graphql/19-authorization.md`
- `knowledge/graphql/02-schema.md`
