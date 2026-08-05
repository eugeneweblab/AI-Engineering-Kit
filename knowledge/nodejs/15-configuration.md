---
id: nodejs/15-configuration
topic: nodejs
slug: configuration
title: "Node.js Configuration"
type: doc
order: 15
status: ready
tags: [nodejs, configuration, process.env, JWT_SECRET, freeze, positive, DATABASE_URL]
related: [nodejs/14-environment, nodejs/18-security, nodejs/16-error-handling, nodejs/26-deployment, nodejs/28-best-practices]
when_to_use: "Read before designing how an application loads, validates, and exposes its configuration object."
---
# Node.js Configuration

## Purpose

This document defines how to turn raw [environment](14-environment.md) input into a single,
validated, typed configuration object that the rest of the application depends on. It covers
layering (defaults, files, environment), validation, immutability, and how to expose config
without leaking secrets.

Environment is the raw source; configuration is the product. Where the environment doc is
about *reading* `process.env` safely, this doc is about *structuring* the result into an
object your code can trust.

## Why It Matters

Configuration is the seam between your code and every environment it runs in — local, CI,
staging, production. Get it wrong and the same binary that passes tests silently misbehaves
in production: a default that should never apply, a URL pointing at the wrong database, a
feature flag stuck on. Because config is read at boot and threaded through everything,
mistakes are systemic, not local. A single validated, immutable config object built once at
startup makes the entire runtime configuration knowable, testable, and impossible to mutate
mid-flight.

## Core Principles

- **Build config once, at startup, then freeze it.** Configuration is not runtime state. Load,
  validate, `Object.freeze`, and export. Nothing rewrites config after boot.
- **Validate the whole schema before the app does any work.** An invalid config must crash the
  process immediately with a precise message, never fall back to a dangerous default.
- **Layer with a clear precedence.** Typically: hardcoded defaults < config file < environment
  variables < explicit overrides. Document the order; make it deterministic.
- **Separate config from secrets.** Non-secret config can live in versioned files; secrets come
  from the environment or a secrets manager and are never written to disk or logs.
- **Inject config; do not import global mutable state.** Pass the config object into modules
  (or a typed accessor) so units are testable with different configs.
- **Config is environment-specific, code is not.** The same artifact runs everywhere; only the
  injected config changes. No `if (env === "prod")` branches sprinkled through business logic.

## Best Practices

- Define a **single schema** (Zod/`convict`/`envalid`) that produces a typed object; derive the
  TypeScript type from the schema so config and types cannot drift.
- **Coerce and constrain**: ports are positive integers, URLs are valid URLs, enums are closed
  sets, timeouts have sane bounds. Reject anything outside the schema.
- Keep the config module **free of side effects** beyond reading env and validating — no DB
  connections, no network calls at import time.
- Provide **safe defaults for development only**; production-critical values (database URL,
  signing keys) must be required with no default, so a misconfigured deploy fails loudly.
- Expose a **redacted view** for logging/diagnostics that masks secrets, and use it in the
  startup banner and any config-dump endpoint.
- **Do not read `process.env` outside the config module.** One boundary, one source of truth.

## Examples

**Good Example** — layered, validated, frozen, redactable

```js
// config.js
import { z } from "zod";

const schema = z.object({
  env: z.enum(["production", "development", "test"]).default("development"),
  port: z.coerce.number().int().positive().default(3000),
  databaseUrl: z.string().url(),            // required, no default: bad deploy fails at boot
  jwtSecret: z.string().min(32),            // secret from env only
  logLevel: z.enum(["debug", "info", "warn", "error"]).default("info"),
});

// Map raw env -> schema, validate, then freeze so nothing mutates it later.
const config = Object.freeze(
  schema.parse({
    env: process.env.NODE_ENV,
    port: process.env.PORT,
    databaseUrl: process.env.DATABASE_URL,
    jwtSecret: process.env.JWT_SECRET,
    logLevel: process.env.LOG_LEVEL,
  }),
);

// Redacted view for logs — secrets never printed.
export const safeConfig = { ...config, jwtSecret: "[redacted]" };
export default config;
```

**Bad Example** — read anywhere, mutable, unsafe defaults

```js
export const config = {
  port: process.env.PORT || 3000,
  // Dangerous default: if JWT_SECRET is missing in prod, tokens use a public constant.
  jwtSecret: process.env.JWT_SECRET || "dev-secret",
  databaseUrl: process.env.DATABASE_URL, // may be undefined; discovered only at query time
};

// Config is a plain mutable object; any module can rewrite it at runtime.
config.logLevel = "debug";                // silently changes global behavior mid-run
// No validation: a typo'd or absent value is only found when something breaks in production.
```

## Common Mistakes

- Falling back to a hardcoded secret or production URL when the env var is missing.
- Leaving config mutable, letting modules change global behavior at runtime.
- Reading `process.env` in many files instead of a single config module.
- No schema validation, so misconfiguration surfaces as a runtime crash, not a boot failure.
- Committing secrets into versioned config files.
- Branching on the environment name inside business logic instead of injecting values.
- Deriving config types by hand so they drift from the actual runtime shape.

## Production Tips

- Log the **redacted** resolved config at startup so operators can confirm what loaded.
- Keep a documented precedence order and a checked-in `.env.example` listing every variable
  (names only) as living documentation.
- Reload config only via a full restart; hot-reloading config is a common source of
  inconsistency across [clustered](13-cluster.md) workers.

## AI Review Checklist

- Is config built once at startup, validated against a schema, and frozen?
- Do production-critical values have no fallback default, so a bad deploy fails at boot?
- Are secrets sourced from the environment/secrets manager and never committed or logged?
- Is `process.env` confined to the config module, with everything else importing typed config?
- Is there a redacted view used for logs and diagnostics?
- Is the config type derived from the schema rather than maintained separately?

## Related

- `knowledge/nodejs/14-environment.md`
- `knowledge/nodejs/18-security.md`
- `knowledge/nodejs/16-error-handling.md`
- `knowledge/nodejs/26-deployment.md`
- `knowledge/nodejs/28-best-practices.md`
