---
id: nextjs/21-environment-variables
topic: nextjs
slug: environment-variables
title: "Next.js Environment Variables"
type: doc
order: 21
status: ready
tags: [nextjs, environment-variables, NEXT_PUBLIC_API_URL, NEXT_PUBLIC_, STRIPE_SECRET_KEY, DATABASE_URL, object]
related: [nextjs/26-deployment, nextjs/24-security, security/16-secrets-management]
when_to_use: "Read before managing environment variables or secrets across Next.js environments."
---
# Next.js Environment Variables

## Purpose

This document defines the engineering standards for managing environment variables in Next.js applications.

The objective is to create applications that are secure, portable, and easy to configure across multiple environments without modifying application code.

Environment variables are configuration, not application logic.

---

## Core Principle

Keep configuration outside the codebase.

The same build should be deployable to different environments by changing configuration rather than source code.

---

## Configuration Goals

Every application should provide:

- secure secret management;
- environment isolation;
- predictable configuration;
- reproducible deployments;
- minimal configuration duplication.

---

## Environment Types

Typical environments include:

- Development;
- Testing;
- Staging;
- Production.

Each environment should have its own independent configuration.

---

## Configuration Ownership

Environment variables should define:

- infrastructure configuration;
- external service endpoints;
- credentials;
- feature flags;
- deployment settings.

Business rules should never depend directly on environment variables.

---

## Naming Convention

Use descriptive, uppercase names.

Examples:

```
DATABASE_URL

REDIS_URL

NEXTAUTH_SECRET

STRIPE_SECRET_KEY

AWS_REGION
```

Avoid ambiguous names such as:

```
URL

KEY

SECRET

VALUE
```

---

## Public Variables

Variables prefixed with:

```
NEXT_PUBLIC_
```

are exposed to client-side JavaScript.

Use them only for information that is safe to make public.

Examples:

- public API base URL;
- analytics identifiers;
- feature toggles intended for the client.

Never expose secrets through public variables.

### Public variables are inlined at build time

`NEXT_PUBLIC_` variables are **statically replaced into the JavaScript bundle
during `next build`** — they are not read at runtime. The literal string value
is baked into every place you reference it.

```tsx
// app/analytics-provider.tsx
"use client";

import { useEffect } from "react";

export function AnalyticsProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    // At build time this becomes: init("G-ABC123") — a literal string.
    init(process.env.NEXT_PUBLIC_ANALYTICS_ID);
  }, []);

  return <>{children}</>;
}
```

Two consequences follow from build-time inlining:

- Changing a `NEXT_PUBLIC_` value requires a **rebuild**, not just a redeploy of
  the same image with new env. A single Docker image cannot be promoted across
  environments if it hardcodes public values that differ per environment.
- You must reference the variable by its **full literal name**. Dynamic access
  such as `process.env[key]` is not inlined and resolves to `undefined` in the
  browser.

```tsx
// Bad — not statically analyzable, undefined in the browser.
const key = "NEXT_PUBLIC_ANALYTICS_ID";
const dynamicId = process.env[key];

// Good — full literal name, inlined at build time.
const id = process.env.NEXT_PUBLIC_ANALYTICS_ID;
```

If you need per-environment public values from a single build, pass them from a
Server Component to a Client Component as props instead of relying on
`NEXT_PUBLIC_` inlining.

---

## Server Variables

Variables without the public prefix remain server-only.

Typical examples:

- database credentials;
- API keys;
- authentication secrets;
- encryption keys.

Server variables must never be exposed to the browser.

A non-prefixed variable read inside a Client Component resolves to `undefined`
in the browser — Next.js does not inline it. The real danger is accidentally
importing server code that *reads* a secret into a component that ships to the
client. Guard modules that touch secrets with the `server-only` package so such
a mistake fails the build instead of leaking at runtime.

```ts
// lib/stripe.ts
import "server-only"; // Build error if this module is imported by client code.
import Stripe from "stripe";

export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: "2025-06-30.basil",
});
```

```tsx
// Bad — a Client Component pulls in server-only code and the secret it holds.
"use client";
import { stripe } from "@/lib/stripe"; // `server-only` turns this into a build error.

// Good — read the secret in a Server Action / Route Handler / Server Component,
// then pass only non-sensitive results to the client.
```

Reading `process.env.STRIPE_SECRET_KEY` is only safe in server contexts: Server
Components, Route Handlers (`app/**/route.ts`), Server Actions (`"use server"`),
and `middleware.ts`.

---

## Secrets

Treat all secrets as sensitive.

Examples:

- JWT signing keys;
- OAuth client secrets;
- payment provider credentials;
- SMTP passwords;
- cloud provider credentials.

Store secrets using a secure secret management solution.

---

## Validation

Validate required environment variables during application startup.

The application should fail immediately if critical configuration is missing or invalid.

Avoid discovering configuration problems during runtime.

Parse the environment once, at module load, with a schema. Importing the module
anywhere forces validation to run; a missing or malformed variable throws before
any request is served.

```ts
// config/env.ts
import { z } from "zod";

const serverSchema = z.object({
  NODE_ENV: z.enum(["development", "test", "production"]).default("development"),
  DATABASE_URL: z.string().url(),
  STRIPE_SECRET_KEY: z.string().min(1),
  // Coerce string env values into the types the app expects.
  PORT: z.coerce.number().int().positive().default(3000),
});

const parsed = serverSchema.safeParse(process.env);

if (!parsed.success) {
  // z.treeifyError avoids logging raw secret values from process.env.
  console.error("Invalid environment variables:", z.treeifyError(parsed.error));
  throw new Error("Invalid environment variables");
}

export const env = parsed.data;
```

---

## Type Safety

Access environment variables through a centralized configuration module.

Example:

```
config/

    env.ts
```

The module should:

- validate values;
- provide defaults where appropriate;
- expose typed configuration.

Avoid reading `process.env` throughout the application.

Consuming code imports the typed object instead of touching `process.env`:

```ts
// lib/db.ts
import { env } from "@/config/env"; // env.DATABASE_URL is a validated string.
import { drizzle } from "drizzle-orm/node-postgres";

export const db = drizzle(env.DATABASE_URL);
```

Keep the server schema (`config/env.ts`) out of client bundles: it references
secrets and is guarded by never importing it from `"use client"` files. Public
values that must be validated need their own client-safe schema that only reads
`NEXT_PUBLIC_`-prefixed keys **by literal name**, because Next.js inlines only
literal references — a schema that iterates `process.env` will not see them in
the browser.

```ts
// config/client-env.ts — safe to import from Client Components.
import { z } from "zod";

const clientSchema = z.object({
  NEXT_PUBLIC_API_URL: z.string().url(),
});

// Reference each key by its literal name so the value survives build-time inlining.
export const clientEnv = clientSchema.parse({
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
});
```

---

## Default Values

Provide defaults only when they are safe and intentional.

Examples:

- development logging level;
- local service endpoints.

Never provide insecure defaults for production secrets.

---

## Environment Files

Typical files include:

```
.env.local

.env.development

.env.test

.env.production
```

Each file should contain only the configuration required for its environment.

---

## Version Control

Do not commit files containing secrets.

Commit only example configuration files.

Example:

```
.env.example
```

Document every required variable.

---

## Third-Party Services

Store credentials for services such as:

- authentication providers;
- payment gateways;
- email providers;
- cloud services;
- monitoring platforms.

Keep credentials independent from application logic.

---

## Feature Flags

Feature flags may be configured through environment variables when:

- features are environment-specific;
- deployment behavior differs;
- experimental functionality is isolated.

Avoid using environment variables for frequently changing runtime behavior.

---

## Runtime Configuration

Changes to environment variables generally require application restart or redeployment.

Do not expect runtime updates unless supported by the hosting platform.

---

## Logging

Never log:

- secrets;
- API keys;
- access tokens;
- database credentials.

Diagnostic logs should avoid exposing sensitive configuration.

---

## Security

Review:

- secret storage;
- variable exposure;
- access permissions;
- deployment configuration.

Configuration is part of the application's security model.

---

## Accessibility

Environment configuration should not alter accessibility behavior unexpectedly across environments.

---

## AI Execution Checklist

## Investigation

☐ Identify required configuration.

☐ Separate public and private values.

☐ Review secret handling.

☐ Review deployment environments.

---

## Planning

☐ Centralize configuration.

☐ Validate required variables.

☐ Protect sensitive values.

☐ Document configuration.

---

## Verification

☐ Secrets protected.

☐ Public variables intentional.

☐ Validation implemented.

☐ Configuration documented.

☐ Type safety provided.

☐ Deployment verified.

---

## Examples

**Good Example** — one image promoted across environments, secrets read at runtime

```ts
// config/env.ts — server configuration, read at request time, never inlined.
import 'server-only';
import { z } from 'zod';

const serverSchema = z.object({
  DATABASE_URL: z.string().url(),
  STRIPE_SECRET_KEY: z.string().startsWith('sk_'),
  SESSION_SECRET: z.string().min(32),
});

export const env = serverSchema.parse(process.env);   // throws at boot on bad config
```

```tsx
// Per-environment public values passed from the server, so the same build works
// in staging and production without a rebuild.
export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const publicConfig = { apiUrl: process.env.API_URL!, environment: process.env.APP_ENV! };
  return (
    <html lang="en">
      <body>
        <ConfigProvider value={publicConfig}>{children}</ConfigProvider>
      </body>
    </html>
  );
}
```

```bash
# .env.example — committed. Documents every variable; contains no values.
DATABASE_URL=postgres://user:password@localhost:5432/app
STRIPE_SECRET_KEY=sk_test_replace_me
SESSION_SECRET=generate_with_openssl_rand_hex_32
API_URL=http://localhost:3000
```

**Bad Example** — per-environment values baked into the bundle, secrets exposed

```tsx
'use client';

export function Checkout() {
  // A secret with the NEXT_PUBLIC_ prefix is inlined into the JavaScript bundle
  // and readable by anyone who opens devtools. The prefix does not protect it —
  // it publishes it.
  const stripe = new Stripe(process.env.NEXT_PUBLIC_STRIPE_SECRET_KEY!);

  // Dynamic access is not statically replaced, so this is undefined in the
  // browser regardless of the prefix.
  const key = 'NEXT_PUBLIC_API_URL';
  const apiUrl = process.env[key];

  return <PayButton stripe={stripe} apiUrl={apiUrl} />;
}
```

```dockerfile
# The API URL is inlined at build time, so this image is bound to staging.
# Promoting the identical artifact to production is impossible; production gets
# a different build, which is a different thing from the one that was tested.
ARG NEXT_PUBLIC_API_URL=https://staging-api.example.com
RUN npm run build
```

---

## Common Mistakes

Avoid:

Hardcoding credentials.

Exposing secrets through `NEXT_PUBLIC_`.

Reading `process.env` throughout the application.

Skipping startup validation.

Committing `.env` files.

Using unclear variable names.

Depending on undocumented configuration.

---

## Completion Criteria

Environment configuration is complete when:

- all required variables are documented;
- secrets remain protected;
- public variables expose only safe information;
- configuration is validated during startup;
- typed access is provided through a centralized module;
- deployments can be configured without modifying source code.

---

## Summary

Environment variables provide the foundation for secure and flexible application configuration.

By separating configuration from application logic, validating required values, protecting secrets, and centralizing configuration access, Next.js applications become easier to deploy, maintain, and operate across multiple environments.

## Related

- `knowledge/nextjs/26-deployment.md`
- `knowledge/nextjs/24-security.md`
- `knowledge/security/16-secrets-management.md`
