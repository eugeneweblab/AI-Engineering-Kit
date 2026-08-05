---
id: cicd/15-secrets
topic: cicd
slug: secrets
title: "CI/CD Secrets"
type: doc
order: 15
status: ready
tags: [cicd, secrets]
related: [cicd/16-environments, cicd/06-security-scanning, cicd/17-github-actions, cicd/03-build-stage, cicd/28-production]
when_to_use: "Read before handling any credential, token, or key in a pipeline, build, or deployment."
---
# CI/CD Secrets

## Purpose

This document defines how to handle secrets — API keys, database passwords, tokens,
private keys, signing certificates — in CI/CD pipelines and deployments. It is written so
an agent can inject a credential into a build or runtime without leaking it into source
control, logs, artifacts, or the shell environment of untrusted code.

A secret is any value whose disclosure grants access or forgery ability. In a pipeline,
secrets are especially exposed: they pass through checkouts, build steps, third-party
actions, and logs, any of which can leak them. Treat every one as high-value and
short-lived.

## Why It Matters

A leaked secret is a total, silent compromise: the system keeps working while an attacker
uses your credential. Secrets leak most often not through a dramatic breach but through
mundane channels — a key committed to git history, a token echoed in a build log, an env
var readable by a malicious pull-request workflow. Because git history and log storage are
permanent, a secret committed once is compromised forever and must be rotated, not just
deleted. The blast radius scales with the credential's scope, which is why least-privilege
and rotation matter as much as storage.

## Core Principles

- **Never commit secrets to source control.** Not in code, not in config, not in
  `.env` files that get checked in. Git history is permanent; a committed secret is a
  rotated secret.
- **Inject at runtime from a secrets manager.** Store secrets in a dedicated system
  (Vault, cloud KMS/Secrets Manager, CI secret store) and pull them at deploy/run time,
  never bake them into the image or artifact.
- **Least privilege and short lifetimes.** Each credential grants the minimum scope and
  expires quickly. Prefer short-lived, dynamically issued tokens over long-lived static
  keys — and prefer OIDC federation over any stored key at all.
- **Never log or print a secret.** Mask them in CI output and scrub them from error
  messages. Assume anything written to stdout is retained.
- **Rotate on a schedule and on exposure.** Rotation must be routine, not a one-time
  incident response; a secret that cannot be rotated cheaply is a liability.

## Best Practices

- Use short-lived cloud credentials via OIDC (GitHub Actions → AWS/GCP/Azure with no
  stored key) instead of long-lived access keys wherever the platform supports it.
- Scope pipeline secrets to the smallest job/environment that needs them; do not expose
  production secrets to CI stages that only build or test.
- Do not pass secrets to untrusted code paths — e.g. `pull_request` workflows from forks
  must not receive repository secrets. Use manual approval or `pull_request_target` with
  care.
- Reference secrets by name from the secret store; never interpolate them into command
  lines that appear in logs or process listings.
- Keep secrets out of build args and image layers (they persist in the image history);
  mount them at runtime instead.
- Add secret scanning (gitleaks, trufflehog, provider push protection) to CI and
  pre-commit so a leak is caught before merge — see [security scanning](06-security-scanning.md).
- Maintain an audited access log for who/what read each secret.

## Examples

**Good Example** — OIDC federation, no stored key, scoped and masked

```yaml
# GitHub Actions: exchange a short-lived OIDC token for cloud creds. No secret stored.
permissions:
  id-token: write        # allow the runner to request an OIDC token
  contents: read
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production    # scopes the deploy + its protections to prod only
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::111111111111:role/deploy  # least-privilege role
          aws-region: us-east-1
          # credentials are minted per-run, expire in minutes, never persisted anywhere
```

**Bad Example** — long-lived key committed and echoed into logs

```yaml
env:
  AWS_ACCESS_KEY_ID: AKIA...REDACTED      # static key hard-coded in the repo → in git forever
  AWS_SECRET_ACCESS_KEY: wJalr...REDACTED # permanent, broad, unrotated
steps:
  - run: echo "Deploying with $AWS_SECRET_ACCESS_KEY"  # secret now printed to build log
  - run: ./deploy.sh                                    # key readable by every step + action
```

## Common Mistakes

- Committing a `.env`, keyfile, or token to the repository (compromised the moment it is
  pushed, even if later deleted).
- Baking secrets into Docker build args or image layers, where they persist in history.
- Echoing secrets in log output or passing them as visible command-line arguments.
- Using long-lived static cloud keys where OIDC federation is available.
- Sharing one broad credential across all environments instead of scoped per-environment
  secrets.
- Exposing repository secrets to fork pull-request workflows, letting untrusted code
  exfiltrate them.
- Treating rotation as incident-only, so keys live for years until one leaks.

## Production Tips

- Turn on the provider's push protection / secret scanning at the org level so leaks are
  blocked at push time, not found later.
- When a secret is exposed, rotate first, then investigate; deleting the commit does not
  remove it from clones and history.
- Keep a rotation runbook and, where possible, automate rotation via the secrets manager.

## AI Review Checklist

- Are all secrets injected from a secrets manager at runtime, never committed to the repo?
- Are short-lived OIDC credentials used instead of long-lived static keys where possible?
- Is each secret scoped to the least-privilege role, job, and environment that needs it?
- Are secrets masked in logs and never passed as visible command-line arguments?
- Are secrets kept out of Docker build args and image layers?
- Do fork/pull-request workflows receive no production secrets?
- Is secret scanning enabled in CI/pre-commit, and is there a rotation schedule?

## Related

- `knowledge/cicd/16-environments.md`
- `knowledge/cicd/06-security-scanning.md`
- `knowledge/cicd/17-github-actions.md`
- `knowledge/cicd/03-build-stage.md`
- `knowledge/cicd/28-production.md`
