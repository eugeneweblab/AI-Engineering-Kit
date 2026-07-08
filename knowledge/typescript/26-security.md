---
id: typescript/26-security
topic: typescript
slug: security
title: "Security"
type: doc
order: 26
status: ready
tags: [typescript, security]
related: [typescript/12-type-guards, typescript/17-error-handling, typescript/02-type-system, typescript/28-best-practices]
when_to_use: "Read before handling untrusted input, parsing external data, or reviewing TypeScript code at a trust boundary."
---
# Security

## Purpose

This document defines how TypeScript's type system helps — and, critically, fails to
help — with security. It focuses on the trust boundary: the moment untrusted data
(request bodies, query params, env vars, third-party APIs) enters your program. An agent
must know exactly where types stop being guarantees.

Security in TypeScript is mostly about *not trusting types you did not earn at runtime*.
For the broader security topic (auth, authz, secrets), see the `security/` knowledge base;
this doc is about the language-specific pitfalls.

## Why It Matters

TypeScript types are erased at compile time. A value typed `User` might, at runtime, be
`null`, an attacker-controlled object, or a string of JavaScript. The type annotation is
a *claim*, not a check. Developers routinely assert `req.body as CreateUserDto` and then
treat that lie as truth — the single most common security mistake in TypeScript codebases.
Every injection, prototype-pollution, and deserialization bug starts with trusting an
unvalidated shape. Because the compiler stays green, the hole is invisible in review
unless you know to look for the cast.

## Core Principles

- **A type assertion is not validation.** `x as T` and `<T>x` tell the compiler to stop
  checking; they verify nothing at runtime. Never cast untrusted input into a domain type.
- **Validate at the boundary, trust inside.** Parse external data once, at the edge, into
  a validated type. Everything downstream can then rely on the type honestly.
- **Fail closed on bad input.** If validation fails, reject the request — never coerce or
  patch the data into shape.
- **Types do not stop injection.** SQL, command, and HTML injection are runtime concerns;
  a `string` type does not sanitize anything.
- **Treat `any` as an unsanitized region.** Once a value is `any`, the compiler cannot
  protect you. Narrow it back to a known type before use.

## Best Practices

- Validate untrusted input with a runtime schema validator — **Zod**, **Valibot**, or
  **ArkType** — and derive the static type from the schema (`z.infer<...>`) so the type
  and the check can never drift apart.
- Never build SQL with template strings. Use parameterized queries / prepared statements;
  the driver, not string concatenation, separates code from data.
- Escape or use safe templating for HTML output; never `element.innerHTML = userInput`.
  Prefer `textContent` or a sanitizer like DOMPurify for rich content.
- Set `noUncheckedIndexedAccess: true` so `arr[i]` is `T | undefined`, forcing you to
  handle missing elements instead of assuming presence. See [type system](02-type-system.md).
- Use type guards, not casts, to narrow `unknown`. See [type guards](12-type-guards.md).
- Validate and type environment variables at startup with a schema; a missing secret
  should crash on boot, not silently be `undefined`.
- Freeze or clone objects derived from `JSON.parse` before merging into config to avoid
  prototype pollution (`__proto__` keys); reputable validators strip these.
- Keep secrets out of logs and error messages; a stack trace can leak tokens.

## Examples

**Good Example** — runtime validation at the boundary, parameterized query

```ts
import { z } from "zod";

// The schema is the single source of truth for the shape AND the runtime check.
const CreateUser = z.object({
  email: z.string().email(),
  age: z.number().int().min(0).max(150),
});
type CreateUser = z.infer<typeof CreateUser>; // type derived from the validator

async function handler(req: Request) {
  const parsed = CreateUser.safeParse(await req.json());
  if (!parsed.success) return badRequest(parsed.error); // fail closed on bad input

  const user = parsed.data; // now genuinely CreateUser at runtime, not just by claim
  // Parameterized query: `email` can never break out of the value position.
  await db.query("INSERT INTO users (email, age) VALUES ($1, $2)", [
    user.email,
    user.age,
  ]);
}
```

**Bad Example** — cast instead of validation, string-built SQL

```ts
async function handler(req: Request) {
  // The cast is a lie: nothing checks that the body matches CreateUser.
  const user = (await req.json()) as CreateUser;

  // `user.email` is attacker-controlled and spliced straight into SQL → injection.
  await db.query(
    `INSERT INTO users (email, age) VALUES ('${user.email}', ${user.age})`,
  );
}
```

## Common Mistakes

- Using `as SomeDto` on `req.body`, `JSON.parse`, or API responses instead of validating.
- Building SQL, shell commands, or HTML by string concatenation with user input.
- Setting `innerHTML` from user-controlled data (stored/reflected XSS).
- Leaving `noUncheckedIndexedAccess` off, so out-of-range access is silently `undefined`.
- Reading `process.env.X` directly without validating it exists and has the right shape.
- Letting a value stay `any` and using it as if it were validated.

## Production Tips

- Enable `strict` and `noUncheckedIndexedAccess` in `tsconfig` and treat them as security
  controls, not style. See [configuration](16-configuration.md).
- Add a lint rule (`@typescript-eslint/no-unsafe-*`) to flag `any` flowing into function
  calls, member access, and returns at trust boundaries.
- Run `npm audit` / a dependency scanner in CI and pin transitive versions with a lockfile.

## AI Review Checklist

- Is every external input validated at runtime, not merely cast with `as`?
- Is the static type derived from the validation schema (no manual duplicate)?
- Are all database queries parameterized rather than string-built?
- Is user-controlled data kept out of `innerHTML` and escaped on output?
- Is `noUncheckedIndexedAccess` enabled, and are index accesses handled?
- Are environment variables validated at startup and secrets kept out of logs?

## Related

- `knowledge/typescript/12-type-guards.md`
- `knowledge/typescript/17-error-handling.md`
- `knowledge/typescript/02-type-system.md`
- `knowledge/typescript/28-best-practices.md`
