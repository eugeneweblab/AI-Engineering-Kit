---
id: docker/29-ci-integration
topic: docker
slug: ci-integration
title: "CI Integration"
type: doc
order: 29
status: ready
tags: [docker, ci-integration]
related: [docker/28-tooling, docker/10-buildkit, docker/19-registry, docker/22-production, docker/18-security]
when_to_use: "Read before wiring Docker builds, scans, or pushes into a CI/CD pipeline."
---
# CI Integration

## Purpose

This document defines how to build, test, scan, and publish Docker images from a CI
pipeline correctly: how to make builds reproducible and fast on ephemeral runners,
how to tag and push, and how to gate on quality and security. It is written so an
agent can wire a pipeline that produces a trustworthy, traceable artifact.

CI is where the [tooling](28-tooling.md) runs automatically and where the
[best practices](26-best-practices.md) become enforced. The output is a single
immutable image, identified by digest, that flows unchanged to
[production](22-production.md).

## Why It Matters

CI is the only place every image is guaranteed to pass through, which makes it the
right chokepoint for enforcement — a check here covers every change, no exceptions.
It is also where reproducibility is won or lost: ephemeral runners with cold caches
turn a 30-second local build into a 10-minute pipeline, and mutable tags turn a
green build into an artifact nobody can reproduce. Get CI right and every deploy is
a known, scanned, traceable image; get it wrong and you ship whatever happened to
build that day.

## Core Principles

- **One build, one artifact, promoted.** Build the image once, tag by immutable
  digest, and promote that same image through environments. Never rebuild per
  stage — a rebuild is a different image.
- **Reproducible on cold runners.** Pin bases by digest and restore a layer cache;
  a pipeline that only works with a warm local cache is not reproducible.
- **Cache across runs.** Ephemeral runners lose the local cache; use registry or
  remote cache so builds reuse layers.
- **Gate before publish.** Lint, test, and scan must pass before the image is
  pushed. A gate after publish protects nothing.
- **No secrets in the image or logs.** Use the CI's secret store and BuildKit secret
  mounts; never `--build-arg` a token or echo it.

## Best Practices

- Build with `docker buildx` using registry-backed cache
  (`--cache-to`/`--cache-from type=registry`) so ephemeral runners reuse layers
  across pipeline runs.
- Tag images with the commit SHA (or a semver from a tag) and push by digest.
  Reserve `latest`/moving tags for human convenience, never for deploys.
- Run the [tooling](28-tooling.md) gates in order: hadolint lint, unit tests, build,
  Trivy scan, SBOM. Fail the pipeline on high/critical fixable findings.
- Provide build-time secrets via `--mount=type=secret`, sourced from the CI secret
  store — never as build args, which persist in image history.
- Use multi-arch builds (`--platform linux/amd64,linux/arm64`) only for the arches
  you actually deploy; each adds build time.
- Push to the [registry](19-registry.md) only after all gates pass, then have the
  deploy step reference the pushed digest, not a tag.
- Sign the image (cosign) in CI so the deploy environment can verify provenance.

## Examples

**Good Example** — cached, gated, digest-pinned, secret-safe (GitHub Actions)

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3      # BuildKit builder

      - name: Lint Dockerfile                    # gate BEFORE building
        run: hadolint Dockerfile

      - name: Build with registry cache
        run: |
          docker buildx build \
            --cache-from type=registry,ref=ghcr.io/org/api:cache \
            --cache-to   type=registry,ref=ghcr.io/org/api:cache,mode=max \
            --tag ghcr.io/org/api:${{ github.sha }} \
            --secret id=npmrc,env=NPM_TOKEN \     # secret mount, not build-arg
            --load .

      - name: Scan image                          # gate BEFORE push
        run: trivy image --severity HIGH,CRITICAL --ignore-unfixed \
               --exit-code 1 ghcr.io/org/api:${{ github.sha }}

      - name: Push immutable, SHA-tagged image
        run: docker push ghcr.io/org/api:${{ github.sha }}
```

**Bad Example** — no cache, no gate, secret leaked, mutable tag

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      # cold build every run: no BuildKit cache → slow, wasteful
      - run: docker build --build-arg NPM_TOKEN=${{ secrets.NPM_TOKEN }} \
               -t org/api:latest .   # token now baked into image history forever
      - run: docker push org/api:latest  # pushed with NO lint, NO test, NO scan
      # deploy will pull ":latest" — unreproducible, untraceable to a commit
```

## Common Mistakes

- Rebuilding the image in each stage (build/staging/prod) instead of promoting one
  digest, so "tested" and "deployed" are different bytes.
- No cross-run cache, so every pipeline is a full cold build.
- Passing secrets as `--build-arg`, permanently embedding them in image layers.
- Pushing before (or without) scanning, so the gate protects nothing.
- Deploying `latest`, making it impossible to tie a running image to a commit.
- Building every architecture "to be safe", doubling build time for arches you
  never deploy.
- Ignoring scanner exit codes so a failing scan does not actually fail the
  pipeline.

## Production Tips

- Record image digest, SBOM, and scan report against the commit so any deployed
  image is fully traceable.
- Have the deploy step resolve and pin the digest it deploys; if the tag moves
  later, prod is unaffected.
- Fail fast: run the cheap gates (lint, unit tests) before the expensive build so
  broken changes stop in seconds, not minutes.
- Re-scan and optionally rebuild on a schedule to catch CVEs disclosed after the
  original green build.

## AI Review Checklist

- Is the image built once and promoted by digest, not rebuilt per stage?
- Is a cross-run [BuildKit](10-buildkit.md) cache (registry/remote) configured?
- Do lint, test, and [scan](28-tooling.md) gates run *before* the push?
- Are build secrets provided via secret mounts, never `--build-arg`?
- Are images tagged by commit SHA and deployed by digest, not `latest`?
- Does a failing scan actually fail the pipeline (exit code honored)?
- Are digest, SBOM, and scan results retained for traceability?

## Related

- `knowledge/docker/28-tooling.md`
- `knowledge/docker/10-buildkit.md`
- `knowledge/docker/19-registry.md`
- `knowledge/docker/22-production.md`
- `knowledge/docker/18-security.md`
