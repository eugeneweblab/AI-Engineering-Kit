---
id: graphql/18-authentication
topic: graphql
slug: authentication
title: "Authentication"
type: doc
order: 18
status: ready
tags: [graphql, authentication]
related: [graphql/19-authorization, graphql/08-context, graphql/17-security, graphql/20-error-handling, graphql/07-resolvers]
when_to_use: "Read before wiring login, tokens, or identity into a GraphQL server or gateway."
---
# Authentication

## Purpose

This document defines how to verify *who* is making a GraphQL request: how the
transport carries a credential, where identity is established, and how it flows to
resolvers. It is written so an agent can add authentication to a GraphQL API without
opening a hole.

Authentication answers "are you who you claim to be?". It is distinct from
[authorization](19-authorization.md) ("are you allowed to see or do this?"). In GraphQL
the two are easy to blur because a single request touches many fields — get them right
in that order: authenticate once per request, authorize per field.

## Why It Matters

GraphQL exposes one endpoint (`/graphql`) that fans out to your entire domain. A single
request can traverse dozens of resolvers across many types. If identity is verified
inconsistently — checked in some resolvers, assumed in others — an attacker only needs
to find the one query path that skips the check. Because the surface is a graph, not a
list of REST routes, an ad-hoc, per-resolver approach fails silently: the schema keeps
resolving, just for the wrong user.

## Core Principles

- **Authenticate at the edge, not in resolvers.** Verify the credential once in the
  server context builder (or an upstream gateway) and put the resulting principal on
  `context`. Resolvers read identity; they never parse tokens.
- **Absent or invalid credentials produce an anonymous principal, not a thrown request.**
  A public query and a private query share the same endpoint; rejecting the whole request
  breaks introspection and public fields. Deny at the field level instead.
- **Never invent your own token scheme.** Use OAuth 2.1 / OIDC access tokens or signed
  sessions. Verify signature, `alg`, issuer, audience, and expiry before trusting a JWT.
- **Identity is immutable within a request.** Resolve it once; do not re-fetch or allow a
  resolver to mutate `context.user`. A mutating context is a race and an audit black hole.
- **Transport carries the credential; the body never does.** Read tokens from the
  `Authorization` header or an `HttpOnly` cookie — never from a GraphQL argument or variable.

## Best Practices

- Build identity in the context factory, which runs once per HTTP request (or once per
  WebSocket connection for subscriptions). Return `{ user }` or `{ user: null }`.
- For subscriptions over WebSockets, authenticate in `onConnect` (the connection-init
  payload), not per-message. Reject the connection if the token is missing or expired.
- Verify JWTs with a vetted library and a cached JWKS; enforce `exp` and reject `alg: none`.
- Keep tokens out of query strings and persisted-query keys — they land in logs and caches.
- Return a machine-readable `extensions.code` of `UNAUTHENTICATED` for missing identity so
  clients can trigger a refresh (see [error handling](20-error-handling.md)).
- Rate-limit the endpoint and cap query depth/complexity *before* auth work runs, so an
  unauthenticated flood cannot exhaust CPU verifying nothing (see [security](17-security.md)).
- For federated graphs, authenticate at the gateway and forward a signed principal to
  subgraphs; do not re-verify the end-user token in every subgraph.

## Examples

**Good Example** — verify once in context, expose a principal, deny per field

```ts
// context is built once per request; resolvers just read `user`.
async function buildContext({ req }): Promise<Ctx> {
  const token = req.headers.authorization?.replace(/^Bearer /, "");
  // No token → anonymous, NOT an error. Public fields must still resolve.
  const user = token ? await verifyAccessToken(token) : null;
  return { user };
}

const resolvers = {
  Query: {
    publicStats: () => getStats(),            // anyone, even anonymous
    me: (_p, _a, ctx: Ctx) => {
      if (!ctx.user) throw new GraphQLError("Not authenticated", {
        extensions: { code: "UNAUTHENTICATED" },  // client can refresh + retry
      });
      return ctx.user;
    },
  },
};
```

**Bad Example** — parses the token inside resolvers, rejects the whole request

```ts
const resolvers = {
  Query: {
    me: (_p, _a, ctx) => {
      // Duplicated in every private resolver — one will be forgotten.
      const user = verifyAccessToken(ctx.req.headers.authorization); // sync + unbatched
      return user;
    },
    publicStats: (_p, _a, ctx) => {
      verifyAccessToken(ctx.req.headers.authorization); // throws for anonymous users,
      return getStats();                                // breaking a public field
    },
  },
};
```

## Common Mistakes

- Verifying the token in each resolver instead of once in context — inconsistent and slow.
- Throwing at the request level for missing auth, breaking public fields and introspection.
- Reading the token from a GraphQL argument/variable, so it leaks into query logs.
- Skipping `onConnect` auth for subscriptions, leaving the WebSocket channel unauthenticated.
- Trusting a JWT without checking signature, `alg`, issuer, audience, and `exp`.
- Re-verifying the end-user token in every federated subgraph instead of trusting the gateway.
- Storing tokens in `localStorage` on the client, exposing them to any XSS.

## Production Tips

- Cache the JWKS and honor its TTL; a key-rotation event must not require a redeploy.
- Log authentication *outcomes* (anonymous, authenticated, rejected) with a request id —
  never the token itself.
- Make the operation name and principal id available to tracing so slow queries can be
  attributed to a caller (see [monitoring](25-monitoring.md)).

## AI Review Checklist

- Is the credential verified exactly once, in the context factory or gateway?
- Does a missing/invalid token yield an anonymous principal rather than a rejected request?
- Are subscriptions authenticated in `onConnect`, not per message?
- Is the JWT validated for signature, `alg`, issuer, audience, and expiry?
- Is the token read from a header or `HttpOnly` cookie, never from arguments/variables?
- Is authentication clearly separated from [authorization](19-authorization.md)?

## Related

- `knowledge/graphql/19-authorization.md`
- `knowledge/graphql/08-context.md`
- `knowledge/graphql/17-security.md`
- `knowledge/graphql/20-error-handling.md`
- `knowledge/graphql/07-resolvers.md`
