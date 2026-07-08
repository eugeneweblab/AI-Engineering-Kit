---
id: graphql/17-security
topic: graphql
slug: security
title: "Security"
type: doc
order: 17
status: ready
tags: [graphql, security]
related: [graphql/18-authentication, graphql/19-authorization, graphql/20-error-handling, graphql/14-filtering, graphql/22-performance]
when_to_use: "Read before exposing a GraphQL endpoint publicly, or when reviewing a schema and server for query-abuse and disclosure risks."
---
# Security

## Purpose

This document defines the security concerns specific to a GraphQL endpoint: query-based
denial of service (depth, complexity, batching, aliases), introspection exposure,
information disclosure through errors, and injection through arguments. It complements
the dedicated [authentication](18-authentication.md) and
[authorization](19-authorization.md) docs, which cover *who* the caller is and *what*
they may do; this doc covers the abuse surface that the query language itself creates.

GraphQL's flexibility is also its attack surface. A single endpoint that accepts
arbitrary client-shaped queries can be driven into pathological work, so the server must
bound query cost and control disclosure at the transport layer, before resolvers run.

## Why It Matters

Unlike REST, where each endpoint has a fixed, known cost, a GraphQL query's cost is
composed by the client at request time. A cyclic schema (`user → posts → author → posts`)
lets a client request a deeply nested query that expands into millions of resolver calls
from a few hundred bytes of input — a query-of-death that exhausts CPU, memory, or the
database with one request. Field aliasing and query batching multiply this further, and
the standard introspection query hands an attacker a full map of your schema.

Because these attacks arrive as valid GraphQL, they pass parsing and authentication;
only cost analysis and disclosure controls stop them. And GraphQL's habit of returning
rich error objects means a misconfigured server leaks stack traces, SQL, and internal
type names by default. Security here is about constraining a language, not guarding a
handful of routes.

## Core Principles

- **Bound query cost before execution.** Enforce a maximum query **depth** and a
  **complexity budget** (weighted field cost) and reject over-budget queries at
  validation time, before any resolver runs. Unbounded queries are unbounded cost.
- **Disable introspection and field suggestions in production.** Introspection is a
  development affordance; in production it hands attackers your schema. "Did you mean"
  suggestions leak field names one probe at a time.
- **Never leak internals through errors.** Return safe, coded messages to clients; keep
  stack traces, SQL, and provider errors server-side. See [error handling](20-error-handling.md).
- **Bound batching and aliases.** Cap the number of operations per batch and the number
  of aliased duplicates of the same field, or attackers amplify a single request.
- **Validate and parameterize every argument.** Arguments reaching a data store must be
  bound parameters, never interpolated — GraphQL does not immunize you from injection.

## Best Practices

- Add a validation rule that rejects queries over a max depth (e.g. 10–15) and over a
  complexity score (`graphql-query-complexity`, Apollo's cost plugin, or an equivalent),
  assigning higher cost to list and connection fields.
- Enforce a **persisted-queries allowlist** for first-party clients in production: the
  server executes only pre-registered operations, which eliminates arbitrary-query abuse
  entirely for those clients.
- Turn off introspection (`introspection: false`) and disable field suggestions in
  production; ship the schema to clients out of band (SDL artifact) instead.
- Set a server-side execution **timeout** and a request **body-size limit** so a slow or
  huge query fails fast rather than tying up a worker.
- Rate-limit by cost, not just by request count — weight each request by its computed
  complexity so ten cheap queries and one expensive one are treated proportionally.
- Require authentication before expensive operations and re-check authorization inside
  resolvers, not just at the gateway (see [authorization](19-authorization.md)).
- Keep mutations idempotent-safe and rate-limited; they are the write surface.

## Examples

**Good Example** — depth + complexity limits, introspection off, masked errors

```ts
const server = new ApolloServer({
  schema,
  introspection: process.env.NODE_ENV !== "production", // schema hidden in prod
  validationRules: [
    depthLimit(12),                       // reject deeply nested / cyclic queries
    createComplexityLimitRule(1000, {     // weighted budget; lists cost more
      listFactor: 10,
    }),
  ],
  // Strip internals from client-facing errors; log the original server-side.
  formatError: (formatted, error) => {
    logger.error(error);                  // full detail stays on the server
    return { message: formatted.message, extensions: { code: formatted.extensions?.code } };
  },
});
```

**Bad Example** — no cost limits, introspection on, raw errors leaked

```ts
const server = new ApolloServer({
  schema,
  introspection: true,   // full schema map exposed to anyone in production
  // No depthLimit, no complexity rule → a cyclic query can expand into millions
  // of resolver calls and exhaust the process from one small request.
  // Default formatError returns the raw error → stack traces, SQL, and internal
  // type names leak to the client.
});
```

## Common Mistakes

- Shipping with introspection and "did you mean" suggestions enabled in production.
- No depth or complexity limit, leaving the endpoint open to query-of-death DoS.
- Rate-limiting by request count while ignoring per-query cost, so one heavy query slips
  through the same budget as a trivial one.
- Returning raw resolver errors to clients, disclosing stack traces, SQL, and internals.
- Interpolating GraphQL argument values into database queries instead of binding them.
- Not capping query batch size or aliased field repetition, enabling amplification.
- Enforcing authorization only at the gateway, so nested resolvers over-expose data.

## Production Tips

- Adopt persisted queries for your own clients and reject non-persisted operations from
  them; this is the strongest single control against arbitrary-query abuse.
- Log rejected queries (depth/complexity violations) with the operation name to spot
  probing and to tune limits without blocking legitimate traffic.
- Put the endpoint behind a WAF/rate limiter that understands POST bodies, and alert on
  spikes in query complexity, not just request volume.
- Keep the schema artifact in CI so clients get types without needing live introspection.

## AI Review Checklist

- Are query depth and complexity limited and enforced at validation time?
- Is introspection (and are field suggestions) disabled in production?
- Are client-facing errors masked, with full detail logged only server-side?
- Is batching size and aliased-field repetition capped?
- Is rate limiting weighted by query cost, not just request count?
- Are argument values bound parameters, never interpolated into data-store queries?
- Is authorization re-checked inside resolvers, not only at the gateway?

## Related

- `knowledge/graphql/18-authentication.md`
- `knowledge/graphql/19-authorization.md`
- `knowledge/graphql/20-error-handling.md`
- `knowledge/graphql/14-filtering.md`
- `knowledge/graphql/22-performance.md`
