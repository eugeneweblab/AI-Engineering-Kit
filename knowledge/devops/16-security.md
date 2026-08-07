---
id: devops/16-security
topic: devops
slug: security
title: "DevOps Security"
type: doc
order: 16
status: ready
tags: [devops, security, "@sha", role-to-assume, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, id-token, GitHub]
related: [devops/17-secrets-management, devops/10-containerization, devops/05-build-pipelines, devops/08-infrastructure-as-code, devops/14-logging]
when_to_use: "Read before designing or reviewing a CI/CD pipeline, container image, cloud IAM policy, or any deployment path for security."
---
# DevOps Security

## Purpose

This document defines how to secure the *delivery and runtime platform* — the pipelines,
images, infrastructure, and access that move code to production. It covers supply-chain
integrity, least-privilege access, and hardening the deployment path, so an agent can
build a pipeline or infrastructure change that does not become the attack's entry point.

This is DevOps security ("securing how software ships and runs"), distinct from
application authentication and authorization, which live in the security topic. It leans
heavily on [secrets management](17-secrets-management.md) — treat that as the companion
doc.

## Why It Matters

The delivery pipeline is the highest-value target in a modern system: it has write
access to production, holds credentials to everything, and runs code from dozens of
dependencies. A single compromised build step, leaked deploy token, or over-permissioned
role does not break one feature — it hands over the whole environment. Supply-chain
attacks (a poisoned dependency, a malicious base image, a hijacked action) have become
the dominant breach vector precisely because one insertion point reaches everything
downstream. Platform security is not a feature you add; it is a property of every
pipeline and IAM policy, and its absence is invisible until it is catastrophic.

## Core Principles

- **Least privilege, everywhere.** Every identity — human, service, CI job — gets the
  minimum permission for its task, scoped and time-bound. The cost of a broad role is
  that a single leaked token owns everything it could touch.
- **Shift left, but verify at the gate.** Scan dependencies, images, and IaC in CI so
  issues are caught cheaply — but also *enforce* at the deploy boundary, because a scan
  you can skip is not a control.
- **Trust nothing unverified in the supply chain.** Pin dependencies and base images by
  digest, verify signatures, and generate an SBOM. "Latest" is an unaudited promise.
- **Immutable, reproducible artifacts.** Build once, sign it, promote the same digest
  through environments. Rebuilding per environment reopens the supply chain each time.
- **Secure defaults, fail closed.** Containers run as non-root, read-only, no extra
  capabilities; a missing security setting must deny, not permit.

## Best Practices

- **Scan every layer in CI**: dependencies (SCA), static code (SAST), container images,
  and IaC (e.g. `tfsec`/`checkov`). Fail the build on new high/critical findings, not
  the whole backlog, so the gate stays actionable.
- **Pin by digest, not tag.** Reference base images and actions by `@sha256:...` and lock
  dependency versions, so a mutated upstream cannot silently change your build.
- **Generate and store an SBOM** per build and **sign artifacts** (e.g. Sigstore/cosign);
  verify the signature before deploy so only known-good images run.
- **Use short-lived, federated credentials** (OIDC from CI to cloud) instead of
  long-lived static keys. A token that expires in minutes is far less useful when stolen.
- **Harden containers**: non-root user, read-only root filesystem, dropped Linux
  capabilities, no privileged mode. See [containerization](10-containerization.md).
- **Least-privilege IAM**: scope roles to specific resources and actions; no wildcards on
  production. Separate deploy identities per service so blast radius is bounded.
- **Protect the pipeline itself**: require reviews on pipeline config, restrict who can
  edit deploy workflows, and never run untrusted PR code with production credentials.
- **Log and alert on security-relevant events**: privilege grants, deploys, failed auth,
  and config changes (see [logging](14-logging.md)).

## Examples

**Good Example** — pinned, non-root, minimal image + keyless CI auth

```dockerfile
# Base image pinned by DIGEST -> a mutated upstream tag cannot change our build.
FROM node:22-slim@sha256:2c3f...e91a AS build
WORKDIR /app
COPY package-lock.json package.json ./
RUN npm ci --omit=dev            # locked versions, prod deps only

FROM gcr.io/distroless/nodejs22@sha256:9ab1...44cd
COPY --from=build /app /app
# non-root -> a container escape lacks host root
USER 10001
# distroless has no shell/package manager -> smaller attack surface
CMD ["/app/server.js"]
```

```yaml
# GitHub Actions: deploy with a SHORT-LIVED OIDC token, no static cloud keys stored.
permissions:
  id-token: write        # request an OIDC token
  contents: read         # least privilege for the job
jobs:
  deploy:
    steps:
      - uses: aws-actions/configure-aws-credentials@v4  # pin by SHA in production
        with:
          role-to-assume: arn:aws:iam::123:role/deploy-web  # scoped to this service
          # No AWS_ACCESS_KEY_ID secret -> nothing long-lived to leak.
```

**Bad Example** — mutable base, root, long-lived secret in the image

```dockerfile
# unpinned -> build is non-reproducible and unauditable
FROM node:latest
WORKDIR /app
# copies .env, .git, keys into the image layers
COPY . .
RUN npm install               # unlocked versions -> supply chain can shift under you
# long-lived key baked into an image layer FOREVER
ENV AWS_SECRET_ACCESS_KEY=AKIA...
# Runs as root by default -> a single RCE is now host root.
CMD ["node", "server.js"]
```

## Common Mistakes

- Referencing base images or CI actions by mutable tag (`latest`) instead of digest.
- Storing long-lived cloud keys as CI secrets instead of using OIDC federation.
- Baking secrets or `.env`/`.git` into image layers, where they persist permanently.
- Running containers as root, privileged, or with a writable root filesystem.
- Wildcard IAM policies (`Action: "*"`, `Resource: "*"`) on production roles.
- Scanning in CI but allowing the gate to be skipped, so it enforces nothing.
- Running untrusted pull-request code with access to production credentials.

## Production Tips

- Enforce image **admission control** in the cluster: reject images that are unsigned,
  unscanned, or running as root, so the control cannot be bypassed at deploy time.
- Rotate and **audit access regularly**; expire unused roles and tokens. Standing access
  is standing risk.
- Feed vulnerability findings into a triage flow with SLAs by severity, so criticals are
  fixed on a clock, not whenever someone notices.

## AI Review Checklist

- Are base images and CI actions pinned by digest, not mutable tags?
- Does CI scan dependencies, code, images, and IaC, and fail on new high/critical issues?
- Are artifacts signed and verified, with an SBOM generated per build?
- Does CI use short-lived OIDC credentials instead of long-lived static keys?
- Do containers run non-root, read-only, with dropped capabilities and no privilege?
- Are IAM roles scoped to specific resources/actions with no production wildcards?
- Are secrets kept out of image layers and env files (see secrets management)?
- Can the security gate be skipped, or is it enforced at the deploy boundary?

## Related

- `knowledge/devops/17-secrets-management.md`
- `knowledge/devops/10-containerization.md`
- `knowledge/devops/05-build-pipelines.md`
- `knowledge/devops/08-infrastructure-as-code.md`
- `knowledge/devops/14-logging.md`
