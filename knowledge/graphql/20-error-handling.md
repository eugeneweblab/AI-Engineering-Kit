---
id: graphql/20-error-handling
topic: graphql
slug: error-handling
title: "GraphQL Error Handling"
type: doc
order: 20
status: ready
tags: [graphql, error-handling, INTERNAL_SERVER_ERROR, extensions.code, errors, UNAUTHENTICATED, FORBIDDEN, EmailTakenError]
related: [graphql/18-authentication, graphql/19-authorization, graphql/07-resolvers, graphql/17-security, graphql/25-monitoring]
when_to_use: "Read before designing how a GraphQL API reports failures to clients or logs them internally."
---
# GraphQL Error Handling

## Purpose

This document defines how a GraphQL server should surface failures: the difference
between the transport-level `errors` array and domain results, how to classify errors
with `extensions.code`, what to expose to clients, and how partial results behave. It is
written so an agent produces error handling that is safe, debuggable, and useful to clients.

## Why It Matters

GraphQL does not use HTTP status codes for domain outcomes — a `200 OK` can carry a
partial result and a populated `errors` array. Teams that treat every failure as a thrown
GraphQLError get an all-or-nothing response and a client that cannot tell "you're logged
out" from "the database is down". Worse, an unformatted error leaks stack traces, SQL, and
internal paths to the client. Because one query spans many resolvers, error handling
determines whether a single field failure nulls that field or destroys the whole response.

## Core Principles

- **Distinguish transport errors from domain outcomes.** Use the `errors` array for
  *exceptional* failures (auth, validation, server faults). Model *expected* outcomes
  (e.g. "email already taken") as typed fields in the schema, so clients handle them by
  reading data, not by pattern-matching error strings.
- **Every error carries a stable `extensions.code`.** Clients branch on machine-readable
  codes (`UNAUTHENTICATED`, `FORBIDDEN`, `BAD_USER_INPUT`, `INTERNAL_SERVER_ERROR`), never
  on human-readable `message`.
- **Never leak internals to the client.** Strip stack traces, DB errors, and file paths in
  production. Log the full detail server-side, keyed by a request id.
- **Errors are located.** GraphQL attaches `path` and `locations`; preserve them so a
  client knows *which* field failed in a large query.
- **Fail the smallest scope.** A resolver throwing nulls only its field (and non-null
  ancestors up to the nearest nullable). Design nullability so one failure doesn't null the
  whole query.

## Best Practices

- Use a `formatError` hook to map internal errors to safe client shapes: keep `message` and
  `extensions.code`, drop everything else unless the error is explicitly client-safe.
- Throw `GraphQLError` with an explicit `code` for auth/validation/not-found; let unexpected
  throws become a single `INTERNAL_SERVER_ERROR` with a request id — not the raw exception.
- Model recoverable, expected failures as union/result types
  (`type CreateUserResult = User | EmailTakenError`) so they are part of the schema contract.
- Attach a `requestId`/`traceId` to `extensions` so clients can quote it in a support ticket
  and you can find the full log (see [monitoring](25-monitoring.md)).
- Make fields nullable where a partial failure should be tolerated; make them non-null only
  when the parent is meaningless without them, and understand the null-propagation cost.
- Keep `UNAUTHENTICATED` (no identity) and `FORBIDDEN` (insufficient permission) distinct,
  matching [authentication](18-authentication.md) and [authorization](19-authorization.md).
- Disable stack traces and verbose errors in production; enable them only in dev.

## Examples

**Good Example** — safe formatting, coded errors, expected outcome in the schema

```ts
// Expected, recoverable failures are part of the schema, handled as data:
// union CreateUserResult = User | EmailTakenError
const resolvers = {
  Mutation: {
    createUser: async (_p, { input }) => {
      if (await emailExists(input.email))
        return { __typename: "EmailTakenError", email: input.email }; // data, not `errors`
      return { __typename: "User", ...(await users.create(input)) };
    },
  },
};

// Exceptional failures are coded; internals are stripped before leaving the server.
const formatError = (formatted, error) => {
  const code = formatted.extensions?.code ?? "INTERNAL_SERVER_ERROR";
  logger.error({ error, requestId }); // full detail stays server-side
  if (code === "INTERNAL_SERVER_ERROR")
    return { message: "Unexpected error", extensions: { code, requestId } }; // no stack/SQL
  return formatted;
};
```

**Bad Example** — leaks internals, unstructured, all-or-nothing

```ts
const resolvers = {
  Mutation: {
    createUser: async (_p, { input }) => {
      // Raw DB exception bubbles up: unique-constraint text, table names, and a
      // stack trace all reach the client, and there is no `code` to branch on.
      return await users.create(input); // "duplicate key value violates unique constraint..."
    },
  },
};
// No formatError → every throw ships its full stack trace to the client in prod.
```

## Common Mistakes

- Returning raw exceptions, leaking stack traces, SQL, or file paths to clients.
- Omitting `extensions.code`, forcing clients to string-match on `message`.
- Using the `errors` array for expected domain outcomes, so clients parse error text.
- Making everything non-null, so one failed leaf nulls the entire query via propagation.
- Reusing one generic code for auth vs validation vs server faults — clients can't react.
- Logging nothing server-side, leaving no way to reconstruct what the client saw.
- Assuming an HTTP status reflects the result — GraphQL returns `200` with `errors`.

## Production Tips

- Alert on the *rate* of `INTERNAL_SERVER_ERROR`, not individual errors; a spike is a bug.
- Include the operation name and `path` in error logs so you can find the failing resolver.
- Return the same request id in `extensions` and in your logs to correlate reports to traces.

## AI Review Checklist

- Does every error carry a stable, machine-readable `extensions.code`?
- Are internal details (stacks, SQL, paths) stripped by `formatError` in production?
- Are expected domain outcomes modeled as schema types, not thrown as errors?
- Is nullability designed so a single field failure doesn't null the whole response?
- Are `UNAUTHENTICATED` and `FORBIDDEN` distinct and used correctly?
- Is a request/trace id attached to errors and logged for correlation?

## Related

- `knowledge/graphql/18-authentication.md`
- `knowledge/graphql/19-authorization.md`
- `knowledge/graphql/07-resolvers.md`
- `knowledge/graphql/17-security.md`
- `knowledge/graphql/25-monitoring.md`
