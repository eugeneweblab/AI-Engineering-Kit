---
id: docker/13-environment-variables
topic: docker
slug: environment-variables
title: "Environment Variables"
type: doc
order: 13
status: ready
tags: [docker, environment-variables]
related: [docker/14-secrets, docker/12-docker-compose, docker/08-dockerfile, docker/18-security]
when_to_use: "Read before passing configuration into a container or reviewing how a Dockerfile or compose file wires env vars."
---
# Environment Variables

## Purpose

This document defines how to pass configuration into containers with environment
variables: where to set them, how they are layered, and where the line falls between
configuration and secrets. It is written so an agent can wire config into a container
without baking values into the image or leaking sensitive data.

Environment variables are the standard way to inject *configuration* that varies
between environments (dev, staging, prod). They are the wrong tool for *secrets* —
for passwords, tokens, and keys, see [secrets](14-secrets.md).

## Why It Matters

Configuration is what makes one image run correctly in many environments. Done right,
a single immutable image is promoted unchanged from CI to production, its behavior
steered only by the environment. Done wrong, config is baked into the image at build
time, so every environment needs its own rebuild, and any secret in a build arg or
an `ENV` line is permanently embedded in an image layer that anyone with the image
can extract with `docker history`. The mistake is invisible until someone pulls the
image and reads your database password out of it.

## Core Principles

- **Config in the environment, not in the image.** Set values at *run* time so one
  image serves every environment. Build-time `ENV` bakes the value into a layer.
- **Env vars are visible.** Anything in `ENV`, in build args, or passed on the
  command line shows up in `docker inspect`, `docker history`, and process listings.
  Never treat them as confidential.
- **Fail fast on missing required config.** Validate needed variables at startup and
  exit with a clear error, rather than running with silent defaults.
- **Provide sane, safe defaults only for non-secrets.** A default port is fine; a
  default password is a backdoor.
- **Document every variable.** A committed `.env.example` is the contract for what
  the container needs to run.

## Best Practices

- Set runtime config with `docker run -e`, compose `environment:`/`env_file:`, or an
  orchestrator's config object — not with `ENV` in the Dockerfile.
- Reserve Dockerfile `ENV` for values that are genuinely part of the image (e.g.
  `NODE_ENV=production` defaults, `PATH` additions), never for per-environment data.
- Never pass secrets through `ARG` or `ENV`; build args are recorded in image
  history and `ENV` persists in the final image. Use build secrets or runtime
  secret mounts instead (see [secrets](14-secrets.md)).
- Keep an `env_file: .env` out of version control and commit `.env.example` with
  placeholder values so required keys are discoverable.
- Validate configuration at process startup; crash loudly on a missing required
  variable so a misconfigured deploy fails immediately, not on first user request.
- Use uppercase, prefixed names (`APP_DB_HOST`) to avoid collisions with system vars.
- Remember precedence: an inline `-e` or compose `environment:` value overrides
  `env_file`, which overrides Dockerfile `ENV`. Rely on it deliberately.

## Examples

**Good Example** — image-level defaults only, runtime config injected, validated

```dockerfile
# Dockerfile — ENV holds only stable, non-secret image defaults
ENV NODE_ENV=production \
    PORT=8080
# No DATABASE_URL, no API keys here — those are injected at run time.
```

```yaml
# compose.yaml — per-environment config comes from an uncommitted .env
services:
  app:
    image: myorg/app:1.4.2
    env_file: .env            # DATABASE_URL, feature flags, etc. live here
    environment:
      PORT: "8080"            # explicit override; wins over env_file and ENV
```

```ts
// startup: validate required config, fail fast with a clear message
const required = ["DATABASE_URL", "JWT_SECRET"];
for (const key of required) {
  if (!process.env[key]) throw new Error(`Missing required env var: ${key}`);
}
```

**Bad Example** — secret baked into the image, no validation

```dockerfile
# Secret and per-env value are now permanent, extractable image layers
ARG DB_PASSWORD                       # recorded in `docker history`
ENV DATABASE_URL=postgres://app:hunter2@prod-db:5432/app  # leaks in `docker inspect`
ENV API_KEY=sk_live_9f3a...           # anyone who pulls the image reads this
# App also starts with silent defaults if these are unset → misconfig ships quietly
```

## Common Mistakes

- Putting secrets in `ARG` or `ENV`, where they are permanently recoverable from
  image history and metadata.
- Baking per-environment config into the image, forcing a rebuild per environment.
- Assuming env vars are private — they are readable via `docker inspect` and the
  host process list.
- No startup validation, so a missing variable surfaces as a confusing runtime error
  much later instead of an immediate, clear failure.
- Committing a real `.env` file to the repository.
- Providing an insecure default (a default admin password) that silently becomes the
  production value.

## Production Tips

- Render and inspect the effective environment in CI with `docker compose config`
  to confirm no secret or wrong value leaked in.
- Prefer an orchestrator's config primitive (ConfigMap, task definition) so config
  is versioned and auditable separately from the image.
- For twelve-factor alignment, keep *all* deploy-varying values in the environment
  and the image itself byte-identical across environments.

## AI Review Checklist

- Is per-environment configuration injected at run time, not baked with `ENV`?
- Are secrets kept out of `ARG`/`ENV` entirely (using secret mounts instead)?
- Does the app validate required variables at startup and fail fast if missing?
- Are defaults provided only for non-sensitive values (never a default credential)?
- Is `.env` gitignored with a committed `.env.example` documenting the keys?
- Is the same image promoted across environments without a rebuild?

## Related

- `knowledge/docker/14-secrets.md`
- `knowledge/docker/12-docker-compose.md`
- `knowledge/docker/08-dockerfile.md`
- `knowledge/docker/18-security.md`
