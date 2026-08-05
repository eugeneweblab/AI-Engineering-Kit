---
id: nodejs/14-environment
topic: nodejs
slug: environment
title: "Node.js Environment"
type: doc
order: 14
status: ready
tags: [nodejs, environment]
related: [nodejs/15-configuration, nodejs/10-process, nodejs/18-security, nodejs/26-deployment, nodejs/16-error-handling]
when_to_use: "Read before reading, validating, or depending on environment variables and NODE_ENV in a Node.js app."
---
# Node.js Environment

## Purpose

This document defines how to consume the runtime environment — `process.env`, `NODE_ENV`,
and platform-injected variables — safely. Environment variables are the standard channel for
per-deployment settings and secrets. This doc covers *reading and validating* that input;
turning it into a typed, structured config object is covered in
[configuration](15-configuration.md).

The line is deliberate: environment is the raw, untyped, string-only source; configuration
is the validated, typed result your code actually uses.

## Why It Matters

`process.env` is untyped, mutable global state populated by whoever launched the process —
a shell, a container runtime, a CI system. Every value is a string or `undefined`; a missing
variable is silently `undefined`, and a typo reads as `undefined` too. Code that reads
`process.env` directly, deep inside modules, fails late and mysteriously: the app boots fine,
then throws on the first request because `DATABASE_URL` was never set. Treating the
environment as hostile, validated input at startup turns those runtime landmines into a loud,
immediate boot failure.

## Core Principles

- **Read the environment once, at startup, in one place.** Everything downstream imports a
  typed config object — never `process.env` scattered across the codebase.
- **Everything is a string or undefined.** `process.env.PORT` is `"3000"`, not `3000`.
  `process.env.DEBUG` is `"false"` (a truthy string), not `false`. Parse and coerce explicitly.
- **Fail fast on missing or invalid values.** A required variable that is absent or malformed
  must crash the process at boot, not degrade silently at runtime.
- **`NODE_ENV` is an environment signal, not a feature flag.** It has three canonical values
  (`production`, `development`, `test`) and controls framework/optimization behavior. Do not
  overload it with app logic like `NODE_ENV === "staging"`.
- **Secrets live in the environment, never in the repo.** No secrets in code, `.env` files
  committed to git, or logs.

## Best Practices

- Validate the whole environment at startup with a schema (**Zod**, `envalid`, or equivalent)
  and export the parsed result. Missing/invalid vars should throw with a clear message.
- Set **`NODE_ENV=production`** explicitly in production. Many libraries (Express, React) run
  slower or leak debug info when it is unset — the default is not production.
- Use a separate variable (e.g. `APP_ENV` or `DEPLOY_ENV`) for staging/preview distinctions so
  `NODE_ENV` stays canonical.
- Load `.env` files for **local development only**, and add `.env` to `.gitignore`. In
  production, inject variables through the platform (Kubernetes secrets, ECS task definitions,
  the CI/CD secret store). Node 20.6+ can load them natively with `--env-file`, avoiding a
  `dotenv` dependency.
- Coerce and default at the boundary: parse numbers with validation, treat `"true"`/`"false"`
  as booleans, and reject unknown enum values.
- Never log the full environment or echo secret values in error messages.

## Examples

**Good Example** — validated once, typed, fails fast

```js
// env.js — imported by everything that needs config
import { z } from "zod";

const schema = z.object({
  NODE_ENV: z.enum(["production", "development", "test"]).default("development"),
  PORT: z.coerce.number().int().positive().default(3000), // "3000" -> 3000, validated
  DATABASE_URL: z.string().url(), // required: absent or malformed => boot fails loudly
});

// Throws at startup with a precise message if anything is missing/invalid.
export const env = schema.parse(process.env);
```

**Bad Example** — scattered raw reads, silent coercion

```js
// db.js
const pool = createPool(process.env.DATABASE_URL); // undefined if unset → obscure runtime error

// server.js
const port = process.env.PORT || 3000; // string "3000" vs number 3000 depends on the source

// feature.js
if (process.env.ENABLE_CACHE) enableCache(); // "false" is truthy → cache ALWAYS on
// NODE_ENV never asserted, so production runs in dev mode without anyone noticing.
```

## Common Mistakes

- Reading `process.env.X` directly throughout the codebase instead of one validated module.
- Treating `process.env.FLAG` as a boolean — any non-empty string, including `"false"`, is truthy.
- Using `process.env.PORT` as a number without `Number()`/coercion and validation.
- Leaving `NODE_ENV` unset in production, silently disabling framework optimizations.
- Committing `.env` files or hardcoding secrets, leaking them through git history.
- Overloading `NODE_ENV` with custom values like `"staging"`, breaking library assumptions.
- Logging the entire environment during debugging and exposing secrets.

## Production Tips

- Inject secrets from a manager (Vault, AWS Secrets Manager, Kubernetes Secrets) at deploy
  time; do not bake them into images.
- Print a **redacted** startup summary of resolved config (names and non-secret values) so
  operators can confirm what the process actually loaded.
- Fail the deployment, not the first request: run env validation as the very first thing in
  the entrypoint. See [error handling](16-error-handling.md) for boot-failure behavior.

## AI Review Checklist

- Is `process.env` read and validated once at startup, then consumed as a typed object?
- Are all required variables validated so a missing one crashes at boot, not at request time?
- Are numbers and booleans explicitly coerced rather than used as raw strings?
- Is `NODE_ENV` set to `production` in production and limited to its three canonical values?
- Are `.env` files gitignored and secrets injected by the platform, never committed?
- Are secrets kept out of logs and error messages?

## Related

- `knowledge/nodejs/15-configuration.md`
- `knowledge/nodejs/10-process.md`
- `knowledge/nodejs/18-security.md`
- `knowledge/nodejs/26-deployment.md`
- `knowledge/nodejs/16-error-handling.md`
