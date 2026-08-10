---
id: prisma/18-error-handling
topic: prisma
slug: error-handling
title: "Prisma Error Handling"
type: doc
order: 18
status: ready
tags: [prisma, error-handling, AppError, P2025, P2002, meta, createUser, super]
related: [prisma/07-crud, prisma/08-transactions, prisma/20-debugging, prisma/24-best-practices]
when_to_use: "Read before writing any code that catches a Prisma query failure or maps it to an API response."
---
# Prisma Error Handling

## Purpose

This document defines how to catch, classify, and translate the errors Prisma Client
throws so that failures become predictable, typed outcomes instead of leaked stack
traces. It covers the error class hierarchy, the known error codes worth handling by
name, and how to surface them at the API boundary.

## Why It Matters

A Prisma query touches the network, a connection pool, and a database that enforces its
own constraints. Any of those can fail, and the failure arrives as a thrown exception —
not a return value. If you catch everything as a generic `Error`, you lose the one piece
of information that lets you respond correctly: *why* it failed. A unique-constraint
violation is a 409, a missing record is a 404, and a dropped connection is a 503 you
should retry. Collapse them all into a 500 and you both mislead the client and bury the
signal you need to debug. Worse, an uncaught Prisma error serializes its message — which
can include column names, query fragments, and the connection string — straight into an
HTTP response.

## Core Principles

- **Errors are typed; use the type.** Prisma throws specific classes. Narrow with
  `instanceof` and switch on the `.code`, never on `error.message` string matching.
- **Map at the boundary, not in the query.** Data-access functions throw; the HTTP or
  RPC layer decides the status code. Keep the two concerns separate.
- **Fail closed and specific.** An unrecognized error code is a 500, logged with full
  detail server-side and a generic message returned to the caller.
- **Never leak internals.** The client sees a stable, human message; the raw Prisma
  error goes only to your logs.
- **Distinguish retryable from terminal.** Connection and transaction-conflict errors
  are transient; constraint violations are not. Retrying a P2002 just fails again.

## Best Practices

- Import the namespace and match classes explicitly: `Prisma.PrismaClientKnownRequestError`
  for database-enforced failures, `Prisma.PrismaClientValidationError` for bad argument
  shapes (a programming bug, usually a 500), and `Prisma.PrismaClientInitializationError`
  for startup/connection problems.
- Handle these codes by name — they are the ones worth branching on:
  `P2002` (unique constraint), `P2025` (record not found for update/delete/connect),
  `P2003` (foreign-key constraint), `P2000` (value too long). Read `error.meta` for the
  offending field(s).
- Use `error.meta.target` on `P2002` to tell the user *which* field collided, but only
  echo whitelisted field names — do not blindly reflect `meta` back to the client.
- Prefer `findUniqueOrThrow` / `findFirstOrThrow` over manual null checks when "missing"
  is genuinely an error path; they throw `P2025` you can catch uniformly.
- Wrap multi-statement writes in `$transaction` so a mid-sequence failure rolls back;
  handle `P2028` (transaction timeout/expired) and serialization conflicts as retryable.
- Define a single `handlePrismaError(e)` mapper and route every catch block through it,
  so status mapping lives in one auditable place.

## Examples

**Good Example** — narrow by class and code, map at the boundary

```ts
import { Prisma } from "@/generated/prisma/client";

class AppError extends Error {
  constructor(public status: number, message: string) { super(message); }
}

// One mapper, reused everywhere. Callers get a typed AppError, never a raw Prisma error.
function toAppError(e: unknown): AppError {
  if (e instanceof Prisma.PrismaClientKnownRequestError) {
    switch (e.code) {
      case "P2002": // unique violation — safe to name the field, it is user-supplied
        return new AppError(409, `${(e.meta?.target as string[])?.join(", ")} already exists`);
      case "P2025": // update/delete target did not exist
        return new AppError(404, "Record not found");
      case "P2003": // FK constraint — referenced row missing or still referenced
        return new AppError(409, "Related record constraint failed");
    }
  }
  // Unknown/validation errors: log the detail, return a generic 500 (no leak).
  console.error("Unhandled Prisma error", e);
  return new AppError(500, "Internal server error");
}

async function createUser(email: string) {
  try {
    return await prisma.user.create({ data: { email } });
  } catch (e) {
    throw toAppError(e); // boundary layer turns this into an HTTP status
  }
}
```

**Bad Example** — string matching, leaked internals, swallowed cause

```ts
async function createUser(email: string) {
  try {
    return await prisma.user.create({ data: { email } });
  } catch (e: any) {
    // Matching on message text: breaks on any Prisma version bump or locale change.
    if (e.message.includes("Unique constraint")) {
      throw new Error(e.message); // leaks the full query + column names to the client
    }
    return null; // silently swallows connection failures as "no user" — a hidden 500
  }
}
```

## Common Mistakes

- Catching `catch (e: any)` and inspecting `e.message` instead of `e.code`.
- Returning `null` on error, so a transient DB outage looks like "not found".
- Re-throwing the raw Prisma error, leaking column names and query fragments to clients.
- Treating `PrismaClientValidationError` as a user error — it means your code passed a
  malformed argument object and is almost always a bug to fix, not a 400 to display.
- Retrying constraint violations (`P2002`, `P2003`); they are deterministic failures.
- Ignoring `P2025` on `update`/`delete`, so a delete of a nonexistent row 500s.

## Production Tips

- Log the full error with `code`, `meta`, and a request id server-side; return only the
  stable message and status to the caller.
- Add bounded retry with backoff around transaction serialization failures and
  `PrismaClientInitializationError`, but cap attempts so you never retry forever.
- Alert on spikes of a single code — a surge of `P2002` often signals a client bug or a
  missing idempotency key, not user behavior.

## AI Review Checklist

- Are catches narrowed with `instanceof Prisma.PrismaClientKnownRequestError` and a
  `switch` on `.code`, not string matching on `.message`?
- Is there one central mapper from Prisma error → HTTP status, reused by every route?
- Do client responses hide raw Prisma messages, `meta`, and query text?
- Are `P2002`, `P2025`, and `P2003` each mapped to a sensible, distinct status?
- Are transient errors retried and constraint violations not?
- Do `update`/`delete` paths handle `P2025` instead of assuming the row exists?

## Related

- `knowledge/prisma/07-crud.md`
- `knowledge/prisma/08-transactions.md`
- `knowledge/prisma/20-debugging.md`
- `knowledge/prisma/24-best-practices.md`
