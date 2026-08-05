---
id: graphql/08-context
topic: graphql
slug: context
title: "Context"
type: doc
order: 8
status: ready
tags: [graphql, context, GraphQLError, requireUser, authenticate]
related: [graphql/07-resolvers, graphql/16-dataloader, graphql/18-authentication, graphql/19-authorization, graphql/06-subscriptions]
when_to_use: "Read before designing what shared per-request state resolvers receive, or when adding auth, loaders, or db handles to GraphQL context."
---
# Context

## Purpose

This document defines the GraphQL **context**: the per-request object passed as the third
argument to every [resolver](07-resolvers.md). It is written so an agent builds a context
that carries exactly the right shared state — authenticated user, data loaders, db handle —
without leaking it across requests or turning it into a global junk drawer.

The context is created once per operation by a `context` function that runs before any
resolver, and is then read (never mutated as a message bus) by every field.

## Why It Matters

Context is the seam between the transport (an HTTP request or WebSocket) and pure resolver
logic. Two failure modes make it dangerous. First, **cross-request leakage**: if context
is built once at server startup instead of per request, one user's authenticated identity
or cached data bleeds into another user's response — a silent, catastrophic auth bug.
Second, **per-request freshness**: [DataLoaders](16-dataloader.md) must be created *per
request*, because a loader's cache is only correct for the lifetime of one operation. Get
context wrong and every resolver downstream inherits the mistake.

## Core Principles

- **Build context per request, never once at boot.** The `context` function must run for
  each operation so that user identity and loaders are isolated. Sharing them is a leak.
- **Context is read-only shared state, not a mutable scratchpad.** Resolvers read from it;
  they do not stuff results back in to pass data between fields. Use `parent`/args for that.
- **Authenticate in the context function; authorize in resolvers.** Resolve *who* the
  caller is once, up front. Decide *what* they may do at each field, where the data lives.
- **Put dependencies in, not implementation.** Context carries handles (db, loaders,
  services, user), giving resolvers what they need without importing globals.
- **Keep it small and typed.** A precise `Context` type is the contract every resolver
  relies on; an `any` context hides every downstream mistake.

## Best Practices

- Create a fresh set of DataLoaders inside the context function for every request; never
  reuse a loader instance across requests (stale cache and cross-user data).
- Verify the auth token in the context function and expose a typed `user` (or `null`),
  plus helpers like `requireUser()`; do not re-parse the token in each resolver. See
  [authentication](18-authentication.md).
- Never throw *authorization* failures from the context function — an unauthenticated
  caller may still be allowed to run public fields. Throw only on malformed requests.
- Provide a request-scoped logger/trace id in context so all resolver logs correlate.
- For subscriptions, build context from the WebSocket handshake and keep it alive for the
  connection; re-check authorization per event in the resolver. See [subscriptions](06-subscriptions.md).
- Define an explicit `interface Context` and type the `context` function to it, so
  resolvers get autocomplete and the compiler catches missing fields.
- Do not place the raw framework `req`/`res` in context and reach into it from resolvers;
  extract what you need (ip, headers) up front to keep resolvers transport-agnostic.

## Examples

**Good Example** — per-request, typed, auth resolved once

```ts
interface Context {
  user: User | null;
  loaders: { userById: DataLoader<string, User> };
  db: Db;
  requireUser(): User; // throws GraphQLError if null
}

// Runs ONCE PER REQUEST — fresh loaders + fresh identity every time.
async function context({ req }): Promise<Context> {
  const user = await authenticate(req.headers.authorization); // may be null (public ok)
  return {
    user,
    db,
    loaders: { userById: makeUserLoader(db) }, // new instance => cache scoped to this request
    requireUser() {
      if (!user) throw new GraphQLError("Unauthenticated", { extensions: { code: "UNAUTHENTICATED" } });
      return user;
    },
  };
}
```

**Bad Example** — shared context, loaders built once, auth leaks

```ts
// Built ONCE at startup and reused for every request.
const sharedLoaders = { userById: makeUserLoader(db) }; // cache never resets → stale + cross-user

const context = {
  db,
  loaders: sharedLoaders,
  user: currentUser, // frozen at boot: every request sees the SAME user identity
};

// Passing the same object to every request means request A's data
// leaks into request B, and the loader cache never clears.
```

## Common Mistakes

- Constructing context (or its loaders) once at boot instead of per request.
- Reusing a DataLoader across requests, serving stale or another user's cached rows.
- Using context as a mutable bus to pass values between resolvers of one query.
- Throwing authorization errors in the context function, blocking legitimate public fields.
- Typing context as `any`, so no resolver knows what is actually available.
- Stashing the raw `req`/`res` and coupling resolvers to the HTTP framework.

## Production Tips

- Attach a request id and start time to context and emit them in resolver traces; this is
  how you attribute a slow field to a specific request in production.
- In tests, build context with an in-memory or mocked db and a stub user — a well-typed
  context makes resolver unit tests trivial and transport-free.

## AI Review Checklist

- Is the context function invoked per request (not a shared object from boot)?
- Are DataLoaders instantiated fresh inside context for each request?
- Is authentication resolved once in context, exposing a typed `user` and `requireUser()`?
- Does context avoid throwing authorization errors (only reject malformed requests)?
- Is there an explicit `Context` type, with no `any`?
- Do resolvers read dependencies from context rather than module globals or raw `req`?

## Related

- `knowledge/graphql/07-resolvers.md`
- `knowledge/graphql/16-dataloader.md`
- `knowledge/graphql/18-authentication.md`
- `knowledge/graphql/19-authorization.md`
- `knowledge/graphql/06-subscriptions.md`
