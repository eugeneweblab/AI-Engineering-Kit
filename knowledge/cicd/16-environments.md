---
id: cicd/16-environments
topic: cicd
slug: environments
title: "Environments"
type: doc
order: 16
status: ready
tags: [cicd, environments, DATABASE_URL, LOG_LEVEL]
related: [cicd/15-secrets, cicd/10-deployment, cicd/09-release-management, cicd/13-feature-flags, cicd/17-github-actions]
when_to_use: "Read before creating or wiring up dev, staging, or production environments in a pipeline."
---
# Environments

## Purpose

This document defines how to structure deployment environments (development, staging,
production, and ephemeral preview environments) so a change flows through them predictably
and what runs in production has already been validated in a faithful copy. It is written
so an agent can design an environment topology that catches problems before they reach
users.

An environment is a distinct, isolated instance of the system with its own data,
configuration, and secrets. The pipeline promotes an artifact through environments —
never rebuilding it — so that the exact bytes tested in staging are the bytes that run in
production.

## Why It Matters

Environments exist to answer one question before users do: "does this change work in a
realistic setting?" If staging diverges from production — different config, different
dependency versions, different data shape — then a green staging run guarantees nothing,
and the divergence surfaces as a production incident. The most common outage cause is not
bad code but environment drift and mismatched configuration. Building environments as
identical, isolated, and reproducible is what makes the pipeline's earlier gates
meaningful; without it, every gate tests a different system than the one users hit.

## Core Principles

- **Promote one immutable artifact through all environments.** Build once; deploy the
  same artifact to dev → staging → prod. Rebuilding per environment breaks the guarantee
  that what you tested is what you ship.
- **Configuration is per-environment; code is not.** The artifact is identical; only
  injected config and secrets differ, supplied at runtime — never compiled in.
- **Keep environments isolated.** Separate data stores, credentials, and network
  boundaries. A non-prod environment must never read from or write to production data.
- **Keep non-prod faithful to prod.** Same runtime versions, same topology, comparable
  data shape. Divergence makes lower environments lie.
- **Environments are reproducible from code.** Define them with infrastructure-as-code so
  any environment can be rebuilt identically and drift is detectable.

## Best Practices

- Externalize all configuration (12-factor style): read config from the environment at
  runtime, keep secrets in a per-environment [secret store](15-secrets.md), and never
  check environment-specific values into the artifact.
- Use ephemeral preview environments per pull request so reviewers test the real change
  in isolation, then tear them down automatically to control cost.
- Gate promotion between environments: automated tests and quality gates to staging;
  manual approval (protected environment) to production.
- Never let non-prod point at production databases, queues, or third-party live accounts;
  use separate credentials and sandboxes.
- Seed non-prod with production-*shaped* data — anonymized/synthetic, never raw PII copied
  from prod.
- Detect drift: run IaC in a mode that flags manual changes, and reconcile them back into
  code rather than leaving snowflakes.
- Name and label resources by environment so ownership and cost are attributable and
  cross-environment mistakes are obvious.

## Examples

**Good Example** — one image, per-environment config injected at deploy

```yaml
# Same immutable image tag deployed everywhere; only config/secrets vary by environment.
image: registry.example.com/api:1.8.3     # identical bytes across dev/staging/prod

# staging values                          # production values (separate store)
env:
  DATABASE_URL:  ${{ secrets.STAGING_DATABASE_URL }}    # isolated staging DB
  LOG_LEVEL:     debug                                   # prod would set 'info'
  FEATURE_FLAGS_ENV: staging
# No prod credentials exist in staging; promotion re-uses the SAME image with prod config.
```

**Bad Example** — rebuild per environment, prod data in staging

```yaml
# Anti-pattern: build separately for prod, so prod runs untested bytes.
build:
  script: docker build -t api:prod --build-arg ENV=prod .   # different image than staging tested
staging:
  env:
    DATABASE_URL: postgres://prod-db.internal/app          # staging points at PROD data!
    # a bad test migration in staging now corrupts production
```

## Common Mistakes

- Rebuilding the artifact for each environment, so production runs bytes that were never
  tested.
- Compiling environment-specific config or secrets into the artifact instead of injecting
  at runtime.
- Pointing non-prod at production data stores, risking corruption and PII exposure.
- Letting staging drift from production (different versions, manual hotfixes), so green
  staging means nothing.
- Copying raw production PII into lower environments for "realistic" testing.
- Creating environments by hand instead of from IaC, producing unreproducible snowflakes.
- No promotion gate to production, letting unreviewed changes reach users.

## Production Tips

- Make production a protected environment requiring approval and restricting who/what can
  deploy to it (see [GitHub Actions environments](17-github-actions.md)).
- Track which artifact version is in each environment in one place so "what's in prod?" is
  always answerable.
- Automatically expire and garbage-collect preview environments to keep cost and sprawl
  under control.

## AI Review Checklist

- Is a single immutable artifact promoted through all environments, not rebuilt per stage?
- Is all environment-specific config and secrets injected at runtime, not baked in?
- Are environments isolated, with non-prod never touching production data?
- Is staging faithful to production in runtime versions, topology, and data shape?
- Are environments defined in infrastructure-as-code and checked for drift?
- Is production a protected environment gated by approval?
- Is lower-environment data anonymized/synthetic rather than raw production PII?

## Related

- `knowledge/cicd/15-secrets.md`
- `knowledge/cicd/10-deployment.md`
- `knowledge/cicd/09-release-management.md`
- `knowledge/cicd/13-feature-flags.md`
- `knowledge/cicd/17-github-actions.md`
