---
id: devops/09-configuration-management
topic: devops
slug: configuration-management
title: "Configuration Management"
type: doc
order: 9
status: ready
tags: [devops, configuration-management, Pool, NODE_ENV, object, parse]
related: [devops/08-infrastructure-as-code, devops/17-secrets-management, devops/10-containerization, devops/11-orchestration, devops/06-release-management]
when_to_use: "Read before adding a config value, wiring environment variables, or reviewing how an app reads its settings across environments."
---
# Configuration Management

## Purpose

This document defines how an application gets its settings — environment values, feature
flags, tuning knobs — separately from its code, in a way that is consistent, auditable,
and safe across environments. It is written so an agent can wire configuration without
baking environment-specific values into an artifact or leaking secrets.

This is about **non-secret** configuration and the discipline around it. Secret values
(keys, passwords, tokens) follow stricter rules in
[secrets management](17-secrets-management.md); the infrastructure that *hosts* config
belongs to [infrastructure as code](08-infrastructure-as-code.md).

## Why It Matters

Configuration is where "the same build" behaves differently in dev, staging, and prod —
and where a one-character typo takes production down without a code change. If config is
baked into the artifact, you cannot promote one tested build across environments (the
core rule of [release management](06-release-management.md)). If config is scattered and
untracked, you cannot answer "what value was live when it broke?" Configuration mistakes
are common, high-impact, and often invisible until the wrong environment reads the wrong
value.

## Core Principles

- **Separate config from code.** The same immutable artifact runs everywhere; only the
  injected configuration differs per environment. (This is the Twelve-Factor rule and it
  is what makes "build once, promote" possible.)
- **Config is environment, not logic.** Anything that varies between deploys is config;
  anything that is the same everywhere is code and belongs in the repo.
- **Never commit secrets as config.** Non-secret config can live in the repo; secrets go
  to a secrets manager and are injected at runtime.
- **Fail fast on missing/invalid config.** Validate all required config at startup and
  refuse to boot if something is missing or malformed — do not discover it on first use.
- **Config changes are changes.** They are versioned, reviewed, and rollback-able like
  code, because a bad config value breaks production exactly like a bad deploy.

## Best Practices

- Inject per-environment values through the environment (env vars, mounted config,
  ConfigMaps), not through code branches like `if (env === "prod")`. Branching on
  environment inside code is untestable and drifts.
- Provide **safe defaults for development**, but require production values to be set
  explicitly — never let a missing prod value silently fall back to a dev default.
- **Validate config at startup** with a schema; coerce types (an env var is always a
  string) and reject unknown or missing keys. A boot-time failure is far cheaper than a
  runtime one under load.
- Keep a checked-in, non-secret `.env.example` / config template documenting every key
  so the required surface is discoverable and reviewable.
- Store non-secret config in version control; use a config service or ConfigMap for
  values that must change without a redeploy, and treat those changes as reviewed events.
- Use feature flags for behavior you want to toggle at runtime, but track flag values and
  clean up stale flags — an unmanaged flag is untracked config.

## Examples

**Good Example** — external config, validated once, typed, fail-fast

```ts
import { z } from "zod";

// One schema is the single source of truth for what config the app requires.
const ConfigSchema = z.object({
  PORT: z.coerce.number().default(3000),        // dev-safe default
  DATABASE_URL: z.string().url(),               // required, no default → must be set
  MAX_CONNECTIONS: z.coerce.number().min(1),    // env vars are strings; coerce + validate
  FEATURE_NEW_CHECKOUT: z.coerce.boolean().default(false),
});

// Parse at startup: if a required prod value is missing/invalid, the process refuses
// to boot instead of failing on the first request in production.
export const config = ConfigSchema.parse(process.env);
```

**Bad Example** — config baked in, branch on environment, read ad hoc

```ts
// Environment logic hardcoded into the artifact: the SAME build can't run everywhere,
// and this branch is impossible to test for the "prod" path in CI.
const dbUrl =
  process.env.NODE_ENV === "production"
    ? "postgres://prod-db:5432/app"   // prod host baked into source control
    : "postgres://localhost:5432/app";

// Read raw and untyped at call sites, no validation: a typo or missing value surfaces
// only when this code path runs — possibly hours into a production deploy.
const pool = new Pool({ connectionString: dbUrl, max: Number(process.env.MAX_CONNECTIONS) });
```

## Common Mistakes

- Baking environment-specific values (hosts, URLs) into the artifact so builds are not
  promotable.
- Branching on `NODE_ENV`/environment inside application logic instead of injecting config.
- No startup validation, so a missing or mistyped value fails deep in a request path.
- Letting a missing production value silently fall back to a development default.
- Committing secrets into config files "just for now."
- Reading `process.env` untyped and scattered across the codebase with no single schema.

## Production Tips

- Log the *effective, non-secret* config at startup so you can confirm what the process
  actually loaded — never log secret values.
- Roll config changes out like deploys: reviewed, versioned, and reversible.
- For values that must change without redeploy, use a config service with an audit log;
  reloading config should be explicit, not a surprise.
- Alert on config drift between environments that are supposed to match.

## AI Review Checklist

- Is per-environment config injected, so one immutable artifact runs in every environment?
- Is all required config validated and type-coerced at startup, failing fast if invalid?
- Are there zero secrets committed as configuration?
- Does application logic avoid branching on the environment name?
- Do production-required values have no silent dev fallback?
- Is there a checked-in template documenting every config key?

## Related

- `knowledge/devops/08-infrastructure-as-code.md`
- `knowledge/devops/17-secrets-management.md`
- `knowledge/devops/10-containerization.md`
- `knowledge/devops/11-orchestration.md`
- `knowledge/devops/06-release-management.md`
