---
id: docker/19-registry
topic: docker
slug: registry
title: "Registry"
type: doc
order: 19
status: ready
tags: [docker, registry]
related: [docker/03-images, docker/18-security, docker/29-ci-integration, docker/22-production, docker/09-image-optimization]
when_to_use: "Read before pushing, pulling, tagging, or configuring authentication for a container registry."
---
# Registry

## Purpose

This document defines how to name, tag, push, pull, and secure images in a container
registry — the shared store that CI writes to and every environment reads from. It is
written so an agent can wire up a registry workflow that is reproducible and auditable.

A registry is the single source of truth for what runs. Get tagging and authentication
wrong and you get non-reproducible deploys, leaked credentials, or a production node
pulling an image nobody can identify.

## Why It Matters

Everything downstream of the registry trusts what it holds. If a mutable tag like
`latest` can be overwritten, two nodes pulling "the same" image can run different code —
a class of bug that is nearly impossible to reproduce. If registry credentials are
broad or long-lived, one leaked token lets an attacker push a backdoored image that every
environment then pulls and runs. The registry is a supply-chain chokepoint: control it
tightly or inherit every mistake it stores.

## Core Principles

- **Tags are labels, digests are identity.** A tag can move; a `sha256` digest cannot.
  Deploy by digest when you need a guarantee of exactly-what-ran.
- **Immutability by policy.** Configure the registry so release tags cannot be
  overwritten. A rebuilt `v1.2.3` that differs from the original is a silent regression.
- **Least-privilege credentials.** CI needs push; production needs pull. Never share one
  admin token across both.
- **Authenticate every access.** Anonymous pull from a private registry, or an
  unauthenticated push, is a supply-chain hole.
- **Scan before promote.** An image should pass a vulnerability scan before it earns a
  release tag. See [security](18-security.md).

## Best Practices

- Tag with an immutable, meaningful identifier: a semver (`v1.4.2`) and/or the git SHA
  (`sha-9f3a1c`). Never deploy the moving `latest` tag to production.
- Reference images by digest in deployment manifests
  (`myapp@sha256:...`) so the exact artifact is pinned.
- Log in with short-lived, scoped tokens (OIDC federation in CI, IAM roles for cloud
  registries), not static passwords stored in the environment.
- Enable tag immutability / retention policies so releases cannot be clobbered and stale
  images are garbage-collected.
- Keep separate repositories or paths for untrusted PR builds vs. promoted releases.
- Use `docker buildx` to push multi-arch manifests when you serve both amd64 and arm64.
- Sign images (cosign) and verify signatures at pull time in production.

## Examples

**Good Example** — scoped login, immutable tags, digest-pinned deploy

```bash
# CI authenticates with a short-lived OIDC token, not a stored password.
echo "$OIDC_TOKEN" | docker login registry.example.com -u ci --password-stdin

# Tag immutably: semver plus the exact commit that produced it.
docker build -t registry.example.com/myapp:v1.4.2 \
             -t registry.example.com/myapp:sha-$GIT_SHA .
docker push registry.example.com/myapp:v1.4.2
docker push registry.example.com/myapp:sha-$GIT_SHA

# Capture the digest and deploy by it — guaranteed identical bytes everywhere.
DIGEST=$(docker inspect --format='{{index .RepoDigests 0}}' registry.example.com/myapp:v1.4.2)
echo "deploying $DIGEST"   # registry.example.com/myapp@sha256:...
```

**Bad Example** — mutable tag, static admin credential

```bash
# Long-lived admin password in the environment: one leak = full push access.
docker login registry.example.com -u admin -p "$REGISTRY_ADMIN_PASSWORD"

# 'latest' is mutable: this overwrite makes two nodes run different code
# while both claim to run myapp:latest.
docker build -t registry.example.com/myapp:latest .
docker push registry.example.com/myapp:latest

# Production pulls 'latest' — non-reproducible, unauditable.
docker run registry.example.com/myapp:latest
```

## Common Mistakes

- Deploying `latest` (or any reused tag) to production, so "the same image" varies by
  node and by pull time.
- Storing a static registry password in CI env vars instead of a short-lived OIDC token.
- Granting CI or developers admin/push rights on the production pull repository.
- Never pruning, so the registry fills with untagged layers and cost balloons.
- Assuming a tag is immutable when the registry allows overwrites — pin by digest to be
  sure.
- Pushing PR/build images into the same repo as releases, muddying provenance.

## Production Tips

- Verify image signatures at admission (Kyverno/cosign policy) so unsigned images cannot
  be scheduled.
- Mirror or cache upstream base images internally so a public-registry outage or a
  deleted upstream tag cannot break your builds.
- Set retention: keep the last N releases plus anything running; garbage-collect the rest.
- Record the deployed digest in your release log so an incident can be traced to exact bytes.

## AI Review Checklist

- Are release images tagged immutably (semver and/or git SHA), never bare `latest`?
- Do production manifests reference images by digest?
- Are registry credentials short-lived and least-privilege (push vs. pull separated)?
- Is tag immutability enabled so releases cannot be overwritten?
- Are images scanned and signed before they are promoted to a release tag?
- Is there a retention/GC policy so the registry does not grow unbounded?

## Related

- `knowledge/docker/03-images.md`
- `knowledge/docker/18-security.md`
- `knowledge/docker/29-ci-integration.md`
- `knowledge/docker/22-production.md`
- `knowledge/docker/09-image-optimization.md`
