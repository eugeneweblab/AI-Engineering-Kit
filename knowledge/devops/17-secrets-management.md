---
id: devops/17-secrets-management
topic: devops
slug: secrets-management
title: "Secrets Management"
type: doc
order: 17
status: ready
tags: [devops, secrets-management]
related: [devops/16-security, devops/09-configuration-management, devops/05-build-pipelines, devops/10-containerization, devops/14-logging]
when_to_use: "Read before handling any credential, API key, token, or certificate in code, config, CI, or infrastructure."
---
# Secrets Management

## Purpose

This document defines how to store, deliver, rotate, and revoke secrets — passwords, API
keys, tokens, private keys, certificates — across code, CI, and running services. It is
written so an agent never commits a credential, never bakes one into an image, and always
delivers secrets in a way that can be rotated and revoked without a redeploy.

A secret is any value whose disclosure grants access or forgeability. Secrets management
is the operational half of [security](16-security.md): even a perfectly hardened pipeline
is worthless if the keys it uses are sitting in a Git history.

## Why It Matters

Leaked secrets are one of the most common and most expensive breaches, and the leak is
usually silent: a key committed to a repo, printed in a log, or baked into an image keeps
working — for you *and* for whoever finds it. The blast radius is the secret's full
scope, and the exposure window runs from the moment of the leak until someone notices,
often months later. Two properties bound the damage: **secrets must never be persisted
where they are not needed** (repos, images, logs, tickets), and **every secret must be
rotatable and revocable quickly**. A system that cannot rotate a leaked key without a
week of coordinated redeploys is a system that stays compromised.

## Core Principles

- **Never commit secrets to source control.** Git history is forever; a secret pushed
  once is compromised even after you delete it. Assume anything in the repo is public.
- **Separate secrets from config.** Non-secret config can live in the repo; secrets come
  from a dedicated store at runtime. Mixing them is how secrets end up in Git.
- **Inject at runtime, never bake in.** Deliver secrets to the process at start (env from
  a secrets manager, mounted file, sidecar) — never into image layers or build artifacts,
  which are immutable and widely copied.
- **Prefer short-lived, dynamically issued secrets.** A credential that auto-expires
  limits the damage of a leak far more than any storage hardening. Static long-lived keys
  are the worst case.
- **Every secret must be rotatable and revocable — fast.** Design so rotating a key is a
  routine, low-risk operation, because after a leak it is an emergency one.

## Best Practices

- **Store secrets in a dedicated manager** (HashiCorp Vault, AWS/GCP/Azure secret stores,
  or the platform's sealed-secret mechanism). It gives you access control, audit logs,
  versioning, and rotation in one place.
- **Deliver via env vars or mounted files at runtime**, sourced from the manager. The app
  reads `DATABASE_URL` from its environment and never knows where it came from.
- **Prefer dynamic/short-lived credentials**: database creds and cloud tokens issued on
  demand and expired in minutes. Use OIDC federation for CI→cloud instead of static keys.
- **Rotate on a schedule and on any suspicion of leak.** Automate rotation so it is not a
  scary manual event; test that the app picks up rotated values without downtime.
- **Scan for secrets in CI and pre-commit** (e.g. gitleaks, trufflehog) so a credential
  is caught before it ever lands in history.
- **Encrypt secrets at rest and in transit**; if you must store secrets in Git (e.g.
  GitOps), use envelope encryption (SOPS, Sealed Secrets) so the committed value is a
  ciphertext, not the secret.
- **Never log secrets** and redact them at the logging boundary (see
  [logging](14-logging.md)); scrub them from error messages and stack traces too.
- **Treat a leaked secret as compromised, always.** Rotate it — do not rationalize that
  "the repo is private". Revocation, not hope, is the control.

## Examples

**Good Example** — secret injected at runtime, read from the environment

```yaml
# Kubernetes: secret is stored in a manager and mounted as an env var at runtime.
# The value never appears in the image, the manifest, or Git (this references it).
env:
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: web-db          # managed externally (e.g. External Secrets from Vault)
        key: url
```

```python
import os

# App reads the secret from its environment; it has no idea where it came from,
# so rotating the underlying value never requires a code change.
DATABASE_URL = os.environ["DATABASE_URL"]   # fail fast if the secret is not injected

# The secret is never logged, never written to disk, never returned in an error.
```

**Bad Example** — hardcoded, committed, and unrotatable

```python
# Anti-pattern: a live credential in source. Git history keeps it forever; deleting the
# line later does NOT remove it from past commits. Anyone with repo access owns the DB.
DATABASE_URL = "postgres://admin:S3cr3tPassw0rd@prod-db:5432/app"
API_KEY = "sk_live_9f8a7b6c5d4e3f2a"        # long-lived, static -> maximum blast radius

# To rotate this you must edit code, review, build, and redeploy every consumer.
# During a leak, that is hours the attacker keeps using the key.
```

## Common Mistakes

- Committing secrets to Git (including in `.env`, test fixtures, or config defaults),
  where history retains them permanently.
- Baking secrets into container image layers or build artifacts.
- Using long-lived static keys where short-lived, dynamic credentials are available.
- Printing secrets in logs, error messages, or stack traces.
- Having no rotation path, so a leak cannot be remediated quickly.
- Storing plaintext secrets in GitOps repos instead of envelope-encrypting them.
- Assuming a "private" repo or "internal" ticket makes an exposed secret safe.

## Production Tips

- Wire **secret scanning into pre-commit and CI** so leaks are blocked at the source, not
  discovered after a push.
- **Alert on secret access anomalies** using the manager's audit log — an unusual read of
  a production key is an early breach signal.
- Practice **rotation as a drill**, not just a policy: a rotation path you have never
  exercised will fail during the incident when you need it most.

## AI Review Checklist

- Are there zero secrets committed to source control, including `.env` and fixtures?
- Are secrets sourced from a dedicated manager and injected at runtime, not baked in?
- Are short-lived/dynamic credentials or OIDC used instead of static long-lived keys?
- Is there an automated, tested rotation and revocation path for every secret?
- Does CI/pre-commit scan for secrets to block leaks before they land?
- Are GitOps-stored secrets envelope-encrypted, never plaintext?
- Are secrets redacted from all logs, errors, and stack traces?

## Related

- `knowledge/devops/16-security.md`
- `knowledge/devops/09-configuration-management.md`
- `knowledge/devops/05-build-pipelines.md`
- `knowledge/devops/10-containerization.md`
- `knowledge/devops/14-logging.md`
