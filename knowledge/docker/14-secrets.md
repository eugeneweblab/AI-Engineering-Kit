---
id: docker/14-secrets
topic: docker
slug: secrets
title: "Docker Secrets"
type: doc
order: 14
status: ready
tags: [docker, secrets, ARG, NPM_TOKEN, POSTGRES_PASSWORD_FILE, COPY, "@github", "secrets:"]
related: [docker/13-environment-variables, docker/12-docker-compose, docker/08-dockerfile, docker/18-security, docker/22-production]
when_to_use: "Read before a container needs a password, token, API key, or private key at build or run time."
---
# Docker Secrets

## Purpose

This document defines how to get sensitive values — passwords, API keys, tokens,
TLS private keys — into a container without embedding them in the image or leaking
them through metadata. It is written so an agent can handle credentials in a
Dockerfile, a compose file, or an orchestrator without creating a permanent leak.

Secrets are distinct from ordinary [configuration](13-environment-variables.md). A
port or a hostname can safely sit in an environment variable; a private key cannot,
because the mechanisms that expose config also expose secrets to anyone who can read
image layers or container metadata.

## Why It Matters

A leaked secret is a total, silent compromise. Unlike a crashed service, a secret in
an image layer produces no error and no alert — the app runs perfectly while the
credential sits recoverable in `docker history` for everyone who ever pulls the
image. And a secret committed to a layer or a git repo cannot be truly removed:
deleting the line does not delete the earlier layer or commit that still contains it.
The only real remediation is rotation. Because the blast radius is total and the
failure is invisible, secret handling is held to a higher bar than ordinary config.

## Core Principles

- **Never bake a secret into an image.** `ENV`, `ARG`, `COPY`-ing a key file, and
  `RUN` commands with inline credentials all persist in image layers forever.
- **Deliver secrets at run time, from outside the image.** Mount them or inject them
  when the container starts, so the image stays non-sensitive and shareable.
- **Prefer file mounts over environment variables.** Env vars leak into
  `docker inspect`, crash dumps, and child-process listings; a mounted file at
  `/run/secrets/...` does not.
- **A leaked secret is a rotated secret.** If a credential ever touched a layer, a
  log, or a repo, rotate it — scrubbing the source is not enough.
- **Least privilege and short life.** Scope each secret to what needs it and prefer
  short-lived, rotatable credentials over long-lived static ones.

## Best Practices

- Use Docker's `secrets:` in compose or the orchestrator's secret store; both mount
  the value as a file under `/run/secrets/<name>`, not as an env var.
- Read the file at startup (`POSTGRES_PASSWORD_FILE`, or your own loader) rather than
  passing the raw value on the command line.
- For build-time secrets (a private package token), use BuildKit
  `RUN --mount=type=secret`, which exposes the value only during that `RUN` and never
  writes it to a layer. Never use `ARG` for a secret.
- Add secret files and `.env` to `.gitignore` and `.dockerignore` so they are never
  copied into the build context or committed.
- Rotate credentials on a schedule and immediately on any suspected exposure; design
  the app to reload them without a full redeploy where possible.
- In production, source secrets from a managed store (Vault, AWS/GCP Secrets Manager,
  Kubernetes Secrets with encryption at rest), not from files on disk.
- Scan images and history in CI for leaked credentials so a mistake is caught before
  the image is published.

## Examples

**Good Example** — file-mounted secret at run time, build secret via BuildKit

```yaml
# compose.yaml — secret is mounted as a file, never an env var
services:
  db:
    image: postgres:16.4
    environment:
      # Postgres reads the value from the file, not from a visible env var
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets: [db_password]

secrets:
  db_password:
    file: ./secrets/db_password.txt   # gitignored + dockerignored
```

```dockerfile
# Dockerfile — build-time token via BuildKit, never persisted to a layer
# syntax=docker/dockerfile:1
RUN --mount=type=secret,id=npm_token \
    NPM_TOKEN="$(cat /run/secrets/npm_token)" npm ci
# The token exists only during this RUN; `docker history` shows nothing.
```

**Bad Example** — secret embedded in the image, recoverable forever

```dockerfile
ARG NPM_TOKEN                          # recorded in image history
ENV DATABASE_PASSWORD=hunter2          # readable via `docker inspect`
COPY id_rsa /root/.ssh/id_rsa          # private key now a permanent layer
RUN git clone https://x:$NPM_TOKEN@github.com/org/private.git  # token in layer
# Deleting these lines later does NOT remove the earlier layers → must rotate.
```

## Common Mistakes

- Passing secrets through `ARG`/`ENV`, making them permanently recoverable from
  image history and `docker inspect`.
- `COPY`-ing a key or credential file into the image, creating a leaked layer.
- Committing `.env`, `*.pem`, or key files to git or leaving them in the build
  context (missing `.dockerignore`).
- Assuming that removing the offending line fixes the leak — the old layer or commit
  still holds it; the credential must be rotated.
- Logging a secret at startup ("connecting with password ...").
- Using a single long-lived credential everywhere instead of scoped, rotatable ones.

## Production Tips

- Integrate a secrets manager so credentials are versioned, access-controlled, and
  rotatable without touching the image.
- Enable encryption at rest for Kubernetes Secrets — by default they are only
  base64-encoded, not encrypted.
- Add automated secret scanning (git hooks + CI image scan) so an accidental commit
  is blocked before publish.
- Maintain a rotation runbook: any exposure triggers rotate-first, investigate-second.

## AI Review Checklist

- Are all secrets delivered at run time from outside the image (no `ENV`/`ARG`/COPY)?
- Are build-time secrets handled with BuildKit `--mount=type=secret`, not `ARG`?
- Are secrets mounted as files under `/run/secrets/` rather than env vars where
  possible?
- Are secret files listed in both `.gitignore` and `.dockerignore`?
- Is there no secret written to logs at startup or on error?
- Is there a rotation path, and does the review flag any exposed credential for
  rotation rather than mere deletion?

## Related

- `knowledge/docker/13-environment-variables.md`
- `knowledge/docker/12-docker-compose.md`
- `knowledge/docker/08-dockerfile.md`
- `knowledge/docker/18-security.md`
- `knowledge/docker/22-production.md`
