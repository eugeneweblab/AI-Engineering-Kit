---
id: graphql/27-production
topic: graphql
slug: production
title: "GraphQL Production"
type: doc
order: 27
status: ready
tags: [graphql, production]
related: [graphql/17-security, graphql/22-performance, graphql/25-monitoring, graphql/21-caching, graphql/29-schema-evolution]
when_to_use: "Read before exposing a GraphQL API to untrusted traffic or promoting it to production."
---
# GraphQL Production

## Purpose

This document defines what has to be true before a GraphQL API takes real, untrusted
traffic: hardening the single endpoint against abusive queries, controlling what the schema
reveals, and shipping schema changes without downtime. It focuses on the operational gap
between "works on my machine" and "safe on the open internet."

The defaults that make GraphQL delightful in development — introspection on, arbitrarily
deep queries, unbounded lists, verbose errors — are exactly what make it dangerous in
production. Going live is largely the work of turning those defaults off.

## Why It Matters

GraphQL hands the client the query language. A single crafted request can ask for a cyclic,
deeply nested selection that fans out into millions of resolver calls — a denial-of-service
with no oversized payload to catch at the edge. Introspection, left on, publishes your entire
data model to attackers. Verbose errors leak stack traces and internal types. None of these
are exotic: they are the out-of-the-box behavior. Production readiness for GraphQL is
specifically about closing the abuse surface that the flexible query model opens.

## Core Principles

- **Bound the cost of every query.** Enforce maximum depth, complexity, and breadth before
  execution. An unbounded query language is an unbounded liability. See [performance](22-performance.md).
- **Reject unknown queries in high-trust paths.** Prefer persisted (allowlisted) operations
  for first-party clients, so the server only runs queries you have seen and approved.
- **Reveal nothing you did not choose to.** Disable introspection and field suggestions for
  untrusted clients; sanitize errors so internals never reach the wire. See [security](17-security.md).
- **Fail safe under load.** Time out slow resolvers, cap concurrency, and shed load rather
  than exhausting the database. A partial result beats a cascading outage.
- **Deploy schema and resolvers together, additively.** A rolling deploy runs old and new
  code simultaneously; ship changes that are safe in both. See [schema evolution](29-schema-evolution.md).

## Best Practices

- Add a validation rule that rejects queries over a max depth and a max complexity/cost
  *before* execution — this is your primary DoS defense, not a rate limiter alone.
- Cap pagination: enforce a maximum `first`/`last`, and reject requests that omit it. An
  unpaginated list is an unbounded query.
- Disable introspection in production for public APIs; keep it for internal tooling behind
  auth. Turn off "did you mean" field suggestions, which leak schema shape.
- Map every thrown error to a safe client error with a stable `extensions.code`; log the
  original server-side only. Never return stack traces. See [error handling](20-error-handling.md).
- Use persisted queries (automatic or registered) so untrusted arbitrary documents are
  rejected and CDN/edge caching becomes possible. See [caching](21-caching.md).
- Set per-request timeouts and DataLoader batch caps so one bad query cannot monopolize the
  event loop or the DB pool.
- Rate-limit by cost, not by request count — one GraphQL request can be 1000x another.

## Examples

**Good Example** — bounded, hardened server config

```ts
const server = new ApolloServer({
  schema,
  introspection: false,              // don't publish the data model to attackers
  includeStacktraceInErrorMessages: false, // never leak internals to clients
  validationRules: [
    depthLimit(10),                  // reject pathological nesting before execution
    costLimit({ maxCost: 1000 }),    // bound fan-out cost, not just request count
  ],
  plugins: [
    responseCachePlugin(),           // cache safe, persisted read operations
    usageReporting(),                // per-operation metrics for alerting
  ],
});
// Persisted operations only for the first-party app: the server runs known queries.
```

**Bad Example** — dev defaults shipped to production

```ts
const server = new ApolloServer({
  schema,
  introspection: true,               // full schema dump available to anyone
  includeStacktraceInErrorMessages: true, // stack traces + internal types on the wire
  // No depth limit, no cost limit: `{ a { b { a { b ... } } } }` fans out unbounded.
  // No pagination cap: `posts(first: 10000000)` is a valid, accepted request.
  // Arbitrary documents accepted: no persisted-query allowlist, no edge caching.
});
```

## Common Mistakes

- Leaving introspection and field suggestions enabled on a public endpoint.
- No depth or complexity limit, so a nested query is a one-line DoS.
- Returning stack traces or internal type names in the `errors` array.
- Unbounded list fields (`first` optional and uncapped), turning lists into full-table scans.
- Rate-limiting by request count, ignoring that one query can cost 1000x another.
- Shipping a breaking schema change in a rolling deploy where old clients still run.
- Reusing a single DataLoader instance across requests, leaking one user's data into another's.

## Production Tips

- Do a two-phase rollout for schema changes: deploy the additive schema + resolvers first,
  migrate clients, then remove the deprecated field in a later deploy. See [schema evolution](29-schema-evolution.md).
- Load-test with realistic *worst-case* queries (deep, wide, uncached), not just the happy path.
- Keep a break-glass path to re-enable introspection behind auth for incident debugging.
- Publish the schema to a registry on deploy so consumers and CI can diff against production.

## AI Review Checklist

- Are depth and complexity/cost limits enforced before execution?
- Is introspection (and are field suggestions) disabled for untrusted clients?
- Are all errors sanitized — no stack traces, no internal types — with stable codes?
- Is every list field paginated with an enforced maximum page size?
- Are persisted/allowlisted operations used for first-party clients?
- Is rate limiting based on query cost rather than raw request count?
- Are schema changes additive and safe to run alongside the previous deploy?

## Related

- `knowledge/graphql/17-security.md`
- `knowledge/graphql/22-performance.md`
- `knowledge/graphql/25-monitoring.md`
- `knowledge/graphql/21-caching.md`
- `knowledge/graphql/29-schema-evolution.md`
