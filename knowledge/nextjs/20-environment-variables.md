# Next.js Environment Variables

## Purpose

This document defines the engineering standards for managing environment variables in Next.js applications.

The objective is to create applications that are secure, portable, and easy to configure across multiple environments without modifying application code.

Environment variables are configuration, not application logic.

---

# Core Principle

Keep configuration outside the codebase.

The same build should be deployable to different environments by changing configuration rather than source code.

---

# Configuration Goals

Every application should provide:

- secure secret management;
- environment isolation;
- predictable configuration;
- reproducible deployments;
- minimal configuration duplication.

---

# Environment Types

Typical environments include:

- Development;
- Testing;
- Staging;
- Production.

Each environment should have its own independent configuration.

---

# Configuration Ownership

Environment variables should define:

- infrastructure configuration;
- external service endpoints;
- credentials;
- feature flags;
- deployment settings.

Business rules should never depend directly on environment variables.

---

# Naming Convention

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

# Public Variables

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

---

# Server Variables

Variables without the public prefix remain server-only.

Typical examples:

- database credentials;
- API keys;
- authentication secrets;
- encryption keys.

Server variables must never be exposed to the browser.

---

# Secrets

Treat all secrets as sensitive.

Examples:

- JWT signing keys;
- OAuth client secrets;
- payment provider credentials;
- SMTP passwords;
- cloud provider credentials.

Store secrets using a secure secret management solution.

---

# Validation

Validate required environment variables during application startup.

The application should fail immediately if critical configuration is missing or invalid.

Avoid discovering configuration problems during runtime.

---

# Type Safety

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

---

# Default Values

Provide defaults only when they are safe and intentional.

Examples:

- development logging level;
- local service endpoints.

Never provide insecure defaults for production secrets.

---

# Environment Files

Typical files include:

```
.env.local

.env.development

.env.test

.env.production
```

Each file should contain only the configuration required for its environment.

---

# Version Control

Do not commit files containing secrets.

Commit only example configuration files.

Example:

```
.env.example
```

Document every required variable.

---

# Third-Party Services

Store credentials for services such as:

- authentication providers;
- payment gateways;
- email providers;
- cloud services;
- monitoring platforms.

Keep credentials independent from application logic.

---

# Feature Flags

Feature flags may be configured through environment variables when:

- features are environment-specific;
- deployment behavior differs;
- experimental functionality is isolated.

Avoid using environment variables for frequently changing runtime behavior.

---

# Runtime Configuration

Changes to environment variables generally require application restart or redeployment.

Do not expect runtime updates unless supported by the hosting platform.

---

# Logging

Never log:

- secrets;
- API keys;
- access tokens;
- database credentials.

Diagnostic logs should avoid exposing sensitive configuration.

---

# Security

Review:

- secret storage;
- variable exposure;
- access permissions;
- deployment configuration.

Configuration is part of the application's security model.

---

# Accessibility

Environment configuration should not alter accessibility behavior unexpectedly across environments.

---

# AI Execution Checklist

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

# Common Mistakes

Avoid:

Hardcoding credentials.

Exposing secrets through `NEXT_PUBLIC_`.

Reading `process.env` throughout the application.

Skipping startup validation.

Committing `.env` files.

Using unclear variable names.

Depending on undocumented configuration.

---

# Completion Criteria

Environment configuration is complete when:

- all required variables are documented;
- secrets remain protected;
- public variables expose only safe information;
- configuration is validated during startup;
- typed access is provided through a centralized module;
- deployments can be configured without modifying source code.

---

# Summary

Environment variables provide the foundation for secure and flexible application configuration.

By separating configuration from application logic, validating required values, protecting secrets, and centralizing configuration access, Next.js applications become easier to deploy, maintain, and operate across multiple environments.