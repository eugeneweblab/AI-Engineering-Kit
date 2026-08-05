---
id: cicd/07-artifacts
topic: cicd
slug: artifacts
title: "Artifacts"
type: doc
order: 7
status: ready
tags: [cicd, artifacts, stage, stable, GITHUB_SHA, GITHUB_OUTPUT, RepoDigests]
related: [cicd/03-build-stage, cicd/06-security-scanning, cicd/08-versioning, cicd/10-deployment]
when_to_use: "Read before designing how a pipeline builds, stores, or promotes build artifacts."
---
# Artifacts

## Purpose

This document defines how a pipeline produces, stores, and promotes *artifacts* — the
immutable outputs of a build (a container image, a JAR, an npm tarball, a binary, a Helm
chart). The central rule: **build once, promote the same artifact through every
environment.** What you tested in staging must be byte-for-byte what you run in production.

An artifact is distinct from source. Source is what you commit; an artifact is what you
[build](03-build-stage.md) from it and [deploy](10-deployment.md). Everything downstream
of the build stage should consume artifacts, never rebuild from source.

## Why It Matters

Rebuilding per environment is one of the most common causes of "worked in staging, broke
in prod." A rebuild pulls fresh dependencies, a new base-image digest, a different
compiler — so the production binary is not the one you tested. Immutable, promoted
artifacts eliminate that entire class of bug and make deploys reproducible and rollbacks
instant: you re-point traffic at a previously-built, known-good artifact instead of
rebuilding history. Artifacts are also your supply-chain record — without provenance and
an SBOM, you cannot answer "what is actually running in production?" during an incident.

## Core Principles

- **Build once, promote everywhere.** The same artifact flows dev → staging → prod. The
  cost is you cannot patch per environment; the payoff is that testing actually means
  something.
- **Artifacts are immutable.** Never overwrite a published version. A given version
  identifier resolves to exactly one set of bytes, forever.
- **Address by digest, not just tag.** Tags move; digests do not. Deploy `sha256:…` so you
  know precisely what ran, even if someone re-pushes a tag.
- **Carry metadata with the artifact.** Version, git SHA, build time, and provenance let
  you trace any running artifact back to its source commit.
- **Separate build inputs from build outputs.** Cache dependencies for speed, but the
  published artifact must be a clean, reproducible build — not "whatever was on the runner."

## Best Practices

- Publish to a real artifact registry (GHCR, ECR, Artifactory, npm registry) with
  retention policies — not to a branch, a shared drive, or a re-pushed `latest` tag.
- Tag images with both an immutable identifier (git SHA or semver) **and** a moving alias
  (`latest`, `stable`) if needed — but deploy by the immutable one.
- Generate an **SBOM** (CycloneDX or SPDX) and a **provenance attestation** (SLSA) at build
  time and store them alongside the artifact.
- Sign artifacts (e.g. cosign) and verify the signature before deploy, so a tampered or
  unknown image cannot reach production.
- Set retention: keep every production-promoted artifact, expire old PR/branch builds after
  days. Storage is cheap, but unbounded registries are not.
- Make builds reproducible: pin base-image digests, pin toolchain versions, avoid
  timestamps that vary per run.

## Examples

**Good Example** — build once, tag by digest, attach SBOM, promote unchanged

```yaml
# Build stage: produce ONE image, addressed immutably
- name: Build & push
  run: |
    IMAGE=ghcr.io/acme/api
    SHA=${GITHUB_SHA::12}
    docker build -t $IMAGE:$SHA .
    docker push $IMAGE:$SHA
    # Capture the digest — this is the immutable handle we promote everywhere
    DIGEST=$(docker inspect --format='{{index .RepoDigests 0}}' $IMAGE:$SHA)
    echo "artifact=$DIGEST" >> "$GITHUB_OUTPUT"

- name: SBOM + provenance
  run: syft $DIGEST -o cyclonedx-json > sbom.json && cosign sign $DIGEST

# Deploy stage (staging AND prod): consume the SAME digest, never rebuild
- name: Deploy
  run: kubectl set image deploy/api api=$DIGEST # identical bytes in every environment
```

**Bad Example** — rebuild per environment, deploy a moving tag

```yaml
# Staging job
- run: docker build -t api:latest . && docker push api:latest
- run: deploy-to staging api:latest

# Production job — rebuilds from source, so `latest` is now DIFFERENT bytes
- run: docker build -t api:latest . && docker push api:latest # new deps, new base image
- run: deploy-to prod api:latest # you are shipping something staging never tested
# `latest` is mutable: two builds, same tag, no way to know what actually ran.
```

## Common Mistakes

- Rebuilding the artifact in each environment instead of promoting one build.
- Deploying `latest` (or any moving tag) so you cannot prove what version is running.
- Overwriting a published version, breaking reproducibility and rollback.
- No SBOM or provenance, leaving you blind during a supply-chain CVE.
- Unbounded registry growth because nothing has a retention policy.
- Storing artifacts as CI job outputs only, which expire — losing the ability to redeploy
  an old version.

## Production Tips

- Record the deployed digest in your release notes and observability tags so an alert can
  link straight back to the exact artifact and commit.
- Verify signatures at admission (e.g. Kubernetes admission controller + cosign) so
  unsigned images are rejected at the cluster, not just discouraged in CI.
- Keep artifacts and their SBOMs for at least as long as your compliance/audit window.

## AI Review Checklist

- Is the artifact built once and promoted unchanged through all environments?
- Is it addressed by an immutable identifier (digest or semver), not a moving tag?
- Is it published to a durable registry with a retention policy?
- Are an SBOM and provenance attestation generated and stored with it?
- Is the artifact signed, and is the signature verified before deploy?
- Can you trace a running artifact back to its exact source commit?
- Does rollback re-point to a prior artifact rather than rebuilding?

## Related

- `knowledge/cicd/03-build-stage.md`
- `knowledge/cicd/06-security-scanning.md`
- `knowledge/cicd/08-versioning.md`
- `knowledge/cicd/10-deployment.md`
