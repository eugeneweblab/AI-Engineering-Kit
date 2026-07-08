---
id: graphql/23-federation
topic: graphql
slug: federation
title: "Federation"
type: doc
order: 23
status: ready
tags: [graphql, federation]
related: [graphql/02-schema, graphql/16-dataloader, graphql/18-authentication, graphql/19-authorization, graphql/29-schema-evolution]
when_to_use: "Read before splitting a GraphQL schema across services or joining subgraphs behind a gateway."
---
# Federation

## Purpose

This document defines how to compose one GraphQL graph from multiple independently owned
subgraphs behind a gateway (Apollo Federation and compatible implementations). It covers
entities, reference resolution, ownership of types and fields, and the cross-cutting
concerns — auth, performance, errors — that change when the schema is distributed.

## Why It Matters

A single monolithic schema becomes a bottleneck once many teams contribute to it.
Federation lets each team own a subgraph and deploy independently while clients still see
one graph. But distribution moves the hard problems to the seams: a type is now split
across services, one query fans out to several subgraphs, and the [N+1](15-n1-problem.md)
reappears as an N+1 of *network* calls between gateway and subgraphs. Get the entity keys,
ownership, and cross-service auth wrong and you get slow, inconsistent, or leaky responses
that no single team can debug.

## Core Principles

- **An entity has one owning subgraph and a stable key.** The `@key` fields uniquely
  identify the entity and must be immutable and consistent everywhere it appears. Other
  subgraphs *extend* it; exactly one *defines* it.
- **Each field has exactly one owner.** Two subgraphs resolving the same field is a
  composition error and a source of inconsistency. Ownership is explicit in the schema.
- **The gateway plans; subgraphs resolve references.** A subgraph contributing fields to an
  entity implements `__resolveReference` to fetch its slice from the entity key.
- **Reference resolution batches or it doesn't scale.** The gateway calls `_entities` with a
  list of keys; resolve them with a [DataLoader](16-dataloader.md), or you recreate the N+1
  across the network.
- **Authenticate at the gateway; propagate a trusted principal.** Verify the end-user token
  once at the edge and forward signed identity/headers to subgraphs, rather than re-verifying
  everywhere (see [authentication](18-authentication.md)).

## Best Practices

- Choose `@key` fields that are stable and present wherever the entity is referenced;
  changing a key is a breaking [schema change](29-schema-evolution.md).
- Implement `__resolveReference` to accept the *batch* the gateway sends and back it with a
  DataLoader, so `_entities` resolves N keys in O(1) queries.
- Keep authorization decisions where the data lives: the subgraph owning a field authorizes
  it, using the principal the gateway forwarded (see [authorization](19-authorization.md)).
  Document the split so no field is left unguarded.
- Compose the supergraph in CI with schema checks; block a subgraph deploy that would break
  composition or remove a field a client uses.
- Propagate a trace/request id through the gateway to every subgraph so a distributed query
  is traceable end to end (see [monitoring](25-monitoring.md)).
- Normalize errors at the gateway: a subgraph fault should surface as a coded, located error,
  not leak the subgraph's internals (see [error handling](20-error-handling.md)).
- Minimize cross-subgraph fan-out in hot paths; a field that forces a call to three
  subgraphs per row is a latency and reliability liability.

## Examples

**Good Example** — one owner, stable key, batched reference resolution

```ts
// Reviews subgraph EXTENDS Product (owned elsewhere) and adds `reviews`.
const typeDefs = gql`
  type Product @key(fields: "id") {   # id is the shared, immutable key
    id: ID!
    reviews: [Review!]!               # this subgraph owns only `reviews`
  }
`;
const resolvers = {
  Product: {
    // Gateway sends a BATCH of {id} refs → resolve via DataLoader, not per ref.
    __resolveReference: (ref, ctx: Ctx) => ({ id: ref.id }),
    reviews: (product, _a, ctx: Ctx) =>
      ctx.loaders.reviewsByProduct.load(product.id), // batched → no network N+1
  },
};
```

**Bad Example** — duplicated ownership, per-reference fetch, re-verified auth

```ts
const typeDefs = gql`
  type Product @key(fields: "id") {
    id: ID!
    name: String!   # also defined in the catalog subgraph → composition conflict
    reviews: [Review!]!
  }
`;
const resolvers = {
  Product: {
    // Called once per entity ref with no batching → N network round-trips.
    reviews: (product, _a, ctx) => {
      verifyEndUserToken(ctx.req);        // re-verifying what the gateway already checked
      return db.review.findByProduct(product.id); // unbatched N+1
    },
  },
};
```

## Common Mistakes

- Two subgraphs defining the same field, producing composition conflicts and drift.
- Choosing a mutable or missing `@key`, breaking reference resolution and clients.
- Resolving `__resolveReference` one key at a time, recreating the N+1 over the network.
- Re-verifying the end-user token in every subgraph instead of trusting the gateway.
- Leaving authorization ambiguous across the seam, so a field ends up guarded by no one.
- Composing the supergraph only at runtime, so a breaking subgraph deploys undetected.
- Leaking subgraph-internal errors and endpoints through the gateway to clients.

## Production Tips

- Run schema composition checks in CI and gate deploys on them; a broken supergraph is a
  full outage, not one team's problem.
- Propagate and log a single trace id across gateway and subgraphs to debug fan-out latency.
- Track per-subgraph latency and error rate at the gateway; the slowest subgraph sets the
  query's p99.

## AI Review Checklist

- Does every entity have a single owning subgraph and a stable, immutable `@key`?
- Is each field owned by exactly one subgraph (no duplicate definitions)?
- Is `__resolveReference` batched with a DataLoader to avoid a network N+1?
- Is the end-user authenticated once at the gateway and identity forwarded to subgraphs?
- Is authorization explicitly placed for every field across the seam?
- Is supergraph composition validated in CI before deploy?

## Related

- `knowledge/graphql/02-schema.md`
- `knowledge/graphql/16-dataloader.md`
- `knowledge/graphql/18-authentication.md`
- `knowledge/graphql/19-authorization.md`
- `knowledge/graphql/29-schema-evolution.md`
