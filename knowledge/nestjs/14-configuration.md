---
id: nestjs/14-configuration
topic: nestjs
slug: configuration
title: "NestJS Configuration"
type: doc
order: 14
status: ready
tags: [nestjs, configuration, Injectable, Inject, process.env, Module, STRIPE_KEY, CanActivate]
related: [nestjs/02-modules, nestjs/28-deployment, nodejs/15-configuration, security/16-secrets-management]
when_to_use: "Read before adding or reviewing configuration, environment variables, or secrets handling in a NestJS application."
---
# NestJS Configuration

## Purpose

This document defines the engineering standards for managing configuration in NestJS applications.

The objective is to ensure that configuration remains centralized, type-safe, validated, secure, and environment-independent throughout the application lifecycle.

Configuration is infrastructure.

It should never contain business logic.

---

## Core Principle

Configuration should be loaded once.

Validated once.

Injected everywhere.

Never read environment variables directly throughout the application.

---

## Configuration Goals

Every configuration system should provide:

- centralized management;
- type safety;
- validation;
- immutable configuration;
- environment independence;
- secure secret handling.

Applications should fail during startup rather than during runtime.

---

## Configuration Flow

```
Environment Variables

↓

Validation

↓

Configuration Module

↓

Configuration Service

↓

Dependency Injection

↓

Application
```

Configuration should always enter the application through a single controlled path.

---

## Responsibilities

Configuration is responsible for:

- loading environment variables;
- validating configuration;
- exposing typed configuration objects;
- managing feature flags;
- selecting environment-specific settings.

Configuration should not:

- execute business logic;
- initialize services;
- access databases;
- call external APIs.

---

## Configuration Categories

Separate configuration by domain.

Example:

```
config/

    app.config.ts

    auth.config.ts

    database.config.ts

    cache.config.ts

    queue.config.ts

    storage.config.ts

    mail.config.ts
```

Avoid one large configuration file.

Use `registerAs` from `@nestjs/config` to define a namespaced, strongly typed
configuration factory per domain. The exported token (`.KEY`) and
`ConfigType<typeof factory>` give you fully typed injection later:

```ts
// config/database.config.ts
import { registerAs } from '@nestjs/config';

export default registerAs('database', () => ({
  url: process.env.DATABASE_URL as string,
  poolSize: parseInt(process.env.DATABASE_POOL_SIZE ?? '10', 10),
  ssl: process.env.DATABASE_SSL === 'true',
}));
```

```ts
// config/app.config.ts
import { registerAs } from '@nestjs/config';

export default registerAs('app', () => ({
  env: process.env.NODE_ENV ?? 'development',
  port: parseInt(process.env.PORT ?? '3000', 10),
  version: process.env.APP_VERSION ?? '0.0.0',
  apiKey: process.env.API_KEY as string,
}));
```

Each factory owns exactly one domain, so modules load only the configuration
they need.

---

## Environment Variables

Environment variables should contain only deployment-specific values.

Examples:

- database URL;
- JWT secret;
- Redis host;
- API keys;
- feature flags.

Never hardcode deployment-specific values.

---

## Validation

Validate every environment variable during startup.

Typical validation includes:

- required values;
- URLs;
- ports;
- numbers;
- booleans;
- enums;
- durations.

Applications should terminate immediately if configuration is invalid.

Register the configuration factories with `ConfigModule.forRoot` and attach a
validation schema. `@nestjs/config` runs the schema against `process.env`
during module initialization, so a missing or malformed variable throws before
the application accepts a single request:

```ts
// app.module.ts
import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import * as Joi from 'joi';
import appConfig from './config/app.config';
import databaseConfig from './config/database.config';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true, // ConfigService is available everywhere without re-importing
      cache: true, // read process.env once, then serve from memory
      expandVariables: true, // allow ${VAR} references inside .env
      load: [appConfig, databaseConfig],
      validationSchema: Joi.object({
        NODE_ENV: Joi.string()
          .valid('development', 'test', 'staging', 'production')
          .default('development'),
        PORT: Joi.number().port().default(3000),
        DATABASE_URL: Joi.string().uri().required(),
        DATABASE_POOL_SIZE: Joi.number().integer().min(1).default(10),
        DATABASE_SSL: Joi.boolean().default(false),
        JWT_SECRET: Joi.string().min(32).required(),
      }),
      validationOptions: {
        abortEarly: false, // report every invalid variable, not just the first
      },
    }),
  ],
})
export class AppModule {}
```

---

## Type Safety

Configuration should expose strongly typed values. Reading raw string keys
through `ConfigService.get('DATABASE_URL')` returns `string | undefined` and
loses all IDE support. Inject the namespaced factory token instead and let
`ConfigType` infer the shape.

**Bad — untyped, stringly-keyed lookups scattered through a service:**

```ts
import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';

@Injectable()
export class BadDatabaseProvider {
  constructor(private readonly config: ConfigService) {}

  connect() {
    // Return type is `string | undefined`; a typo in the key fails silently.
    const url = this.config.get('DATABASE_URL');
    const poolSize = Number(this.config.get('DATABASE_POOL_SIZE'));
    return { url, poolSize };
  }
}
```

**Good — inject the typed, namespaced configuration object:**

```ts
import { Inject, Injectable } from '@nestjs/common';
import { ConfigType } from '@nestjs/config';
import databaseConfig from '../config/database.config';

@Injectable()
export class DatabaseProvider {
  constructor(
    @Inject(databaseConfig.KEY)
    private readonly config: ConfigType<typeof databaseConfig>,
  ) {}

  connect() {
    // `config.url` is `string`, `config.poolSize` is `number`, `config.ssl` is `boolean`.
    return {
      url: this.config.url,
      poolSize: this.config.poolSize,
      ssl: this.config.ssl,
    };
  }
}
```

Typed configuration improves maintainability and IDE support, and a renamed
field becomes a compile error instead of a runtime `undefined`.

---

## Fail Fast

Startup should fail if:

- required variables are missing;
- values have invalid types;
- secrets are empty;
- URLs are malformed.

Never allow partially configured applications to start.

---

## Secret Management

Secrets include:

- JWT secrets;
- API keys;
- OAuth credentials;
- encryption keys;
- database passwords.

Secrets should never:

- appear in source code;
- be committed to Git;
- be logged;
- be returned through APIs.

---

## Feature Flags

Feature flags should be configuration-driven.

Examples:

- beta features;
- maintenance mode;
- experimental functionality.

Business logic should not depend on hardcoded feature toggles.

---

## Environment Separation

Typical environments:

- development;
- testing;
- staging;
- production.

Behavior differences should be configuration-driven rather than code-driven.

---

## Configuration Injection

Inject configuration through dependency injection.

Avoid reading `process.env` inside:

- controllers;
- services;
- repositories;
- guards;
- interceptors.

Configuration access should remain centralized.

**Bad — reading `process.env` directly inside a guard:**

```ts
import { CanActivate, ExecutionContext, Injectable } from '@nestjs/common';

@Injectable()
export class ApiKeyGuard implements CanActivate {
  canActivate(context: ExecutionContext): boolean {
    const request = context.switchToHttp().getRequest();
    // Unvalidated, untyped, and impossible to override in tests.
    return request.headers['x-api-key'] === process.env.API_KEY;
  }
}
```

**Good — inject validated configuration through the constructor:**

```ts
import {
  CanActivate,
  ExecutionContext,
  Inject,
  Injectable,
} from '@nestjs/common';
import { ConfigType } from '@nestjs/config';
import appConfig from '../config/app.config';

@Injectable()
export class ApiKeyGuard implements CanActivate {
  constructor(
    @Inject(appConfig.KEY)
    private readonly config: ConfigType<typeof appConfig>,
  ) {}

  canActivate(context: ExecutionContext): boolean {
    const request = context.switchToHttp().getRequest();
    return request.headers['x-api-key'] === this.config.apiKey;
  }
}
```

The injected variant is validated at startup and can be swapped with a test
double through the DI container, whereas `process.env` reads are global,
untyped, and unmockable.

---

## Configuration Caching

Load configuration once during application startup.

Avoid repeatedly parsing environment variables during request processing.

---

## External Secret Providers

Large applications may integrate with:

- AWS Secrets Manager;
- Google Secret Manager;
- Azure Key Vault;
- HashiCorp Vault.

Application code should remain independent of the underlying secret provider.

---

## Logging

Configuration logs should never expose sensitive values.

Safe examples:

- environment name;
- enabled modules;
- application version.

Unsafe examples:

- passwords;
- API keys;
- JWT secrets.

---

## Security

Review configuration regularly.

Ensure:

- secrets rotate periodically;
- production values differ from development;
- debug settings are disabled in production;
- sensitive defaults are avoided.

---

## Testing

Provide dedicated configuration for:

- unit tests;
- integration tests;
- end-to-end tests.

Tests should not depend on production configuration.

---

## AI Decision Matrix

Configuration belongs here:

✓ Environment variables

✓ Secrets

✓ Feature flags

✓ Service endpoints

✓ Application settings

Do **not** store:

✗ Business rules

✗ Runtime state

✗ User preferences

✗ Database records

---

## AI Execution Checklist

## Investigation

☐ Identify required configuration.

☐ Separate secrets from regular settings.

☐ Review environment differences.

☐ Review validation requirements.

---

## Planning

☐ Centralize configuration.

☐ Validate at startup.

☐ Inject typed configuration.

☐ Protect secrets.

---

## Verification

☐ No direct process.env usage.

☐ Configuration validated.

☐ Secrets protected.

☐ Startup fails on invalid config.

☐ Configuration independently testable.

☐ Production-safe defaults.

---

## Examples

**Good Example** — parsed once, validated at boot, injected as a typed object

```ts
// config/env.validation.ts — the process refuses to start on bad configuration.
const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'test', 'production']),
  PORT: z.coerce.number().int().positive().default(3000),
  DATABASE_URL: z.string().url(),
  JWT_SECRET: z.string().min(32),
  STRIPE_KEY: z.string().startsWith('sk_'),
});

export type Env = z.infer<typeof envSchema>;

export function validateEnv(raw: Record<string, unknown>): Env {
  const parsed = envSchema.safeParse(raw);
  if (!parsed.success) {
    // Field names only — never the values, which are secrets.
    throw new Error(`Invalid configuration: ${Object.keys(parsed.error.flatten().fieldErrors)}`);
  }
  return parsed.data;
}
```

```ts
@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      cache: true,
      validate: validateEnv,        // runs during bootstrap, before the first request
      envFilePath: ['.env.local', '.env'],
    }),
  ],
})
export class AppModule {}

@Injectable()
export class StripeService {
  constructor(private readonly config: ConfigService<Env, true>) {}

  private readonly client = new Stripe(this.config.get('STRIPE_KEY', { infer: true }));
}
```

A missing or malformed variable fails the deploy in seconds, not on the first request that
happens to need it.

**Bad Example** — read from `process.env` at the point of use, unvalidated

```ts
@Injectable()
export class StripeService {
  // Non-null assertion on an unvalidated value: if STRIPE_KEY is absent the
  // client is constructed with `undefined` and fails at the first charge —
  // in production, hours after the deploy that broke it.
  private readonly client = new Stripe(process.env.STRIPE_KEY!);

  async charge(amountCents: number) {
    // A string where a number is expected: '1000' * 2 works, but comparisons do not.
    const max = process.env.MAX_CHARGE ?? 100_000;
    if (amountCents > max) {                    // string vs number comparison
      throw new Error('too large');
    }

    // A default that silently changes behaviour between environments.
    const currency = process.env.CURRENCY || 'usd';
    return this.client.charges.create({ amount: amountCents, currency });
  }
}
```

Scattering `process.env` also removes the one place where a reader could learn what the
service needs to run.

---

## Common Mistakes

Avoid:

Reading `process.env` throughout the application.

Hardcoding secrets.

Skipping configuration validation.

Logging secret values.

Sharing production credentials.

Using string keys everywhere.

Creating circular configuration dependencies.

---

## Completion Criteria

Configuration management is complete when:

- all configuration is centralized;
- environment variables are validated;
- typed configuration is injected through DI;
- secrets remain protected;
- startup fails on invalid configuration;
- applications behave consistently across environments.

---

## Summary

Configuration is the foundation of every production NestJS application.

By centralizing configuration, validating it during startup, exposing typed configuration through dependency injection, and protecting sensitive values, applications become significantly more secure, maintainable, and reliable across all deployment environments.

## Related

- `knowledge/nestjs/02-modules.md`
- `knowledge/nestjs/28-deployment.md`
- `knowledge/nodejs/15-configuration.md`
- `knowledge/security/16-secrets-management.md`
