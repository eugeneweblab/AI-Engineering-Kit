---
id: docker/28-tooling
topic: docker
slug: tooling
title: "Tooling"
type: doc
order: 28
status: ready
tags: [docker, tooling]
related: [docker/10-buildkit, docker/18-security, docker/09-image-optimization, docker/29-ci-integration, docker/26-best-practices]
when_to_use: "Read when choosing which tools to build, lint, scan, or inspect Docker images with."
---
# Tooling

## Purpose

This document maps the ecosystem of tools around Docker — builders, linters,
scanners, and inspectors — and says which to use for what and why. It is written so
an agent can pick the right tool for a task instead of defaulting to `docker build`
for everything or reaching for whatever is most familiar.

Tooling is what turns the [best practices](26-best-practices.md) from advice into
automated, enforced checks. The goal is to catch problems mechanically — in the
editor and in [CI](29-ci-integration.md) — not to rely on reviewers to remember.

## Why It Matters

Container mistakes are consistent and detectable: an unpinned base, a root user, a
known-vulnerable dependency, a bloated layer. A human reviewer will miss these
under time pressure; a tool will not. Tooling also makes the invisible visible — an
SBOM tells you what is actually in an image, a scanner tells you which CVEs it
carries, a linter tells you the Dockerfile is fragile before you ship it. Skipping
tooling means shipping those problems and discovering them later, in production or
in a security audit, at far higher cost.

## Core Principles

- **Shift left.** The cheapest place to catch a bad Dockerfile is the editor; the
  next cheapest is a pre-commit hook; the most expensive is production. Push checks
  as early as possible.
- **Automate the checkable.** Anything a tool can verify (pinning, root user, CVEs)
  should be enforced by a tool, not left to review.
- **Prefer standard, portable tools.** Favor tools that read standard formats
  (OCI images, SBOM, SARIF) so results integrate and you are not locked in.
- **Fail on what matters.** Configure gates to block on high-severity, *fixable*
  findings; warnings for the rest. A gate that always fails gets bypassed.
- **One builder, understood.** Know whether you are using BuildKit, `buildx`, or a
  rootless builder — they differ in caching, secrets, and multi-arch support.

## Best Practices

- Build with [BuildKit](10-buildkit.md)/`docker buildx` (default in current
  Docker). Use `buildx` for multi-arch images and registry-backed cache.
- Lint Dockerfiles with **hadolint** in the editor and CI; it catches unpinned
  bases, `apt` without cleanup, root usage, and shell-form pitfalls.
- Scan images for CVEs with **Trivy** (or Grype/Docker Scout). Scan the built image,
  not just the base, so app-layer dependencies are covered.
- Generate an **SBOM** (Syft, or `docker buildx` with `--sbom=true`) so you can
  answer "does this image contain library X?" without rebuilding.
- Inspect layers with **dive** to find what is bloating an image and whether the
  cleanup landed in the right layer ([image optimization](09-image-optimization.md)).
- Sign and verify images (cosign/Sigstore) so deployers can prove an image came
  from your pipeline, not an attacker's.
- For local multi-service dev, use **Docker Compose**; for local Kubernetes parity,
  use **kind** or **k3d** rather than pointing dev at a shared cluster.

## Examples

**Good Example** — layered checks, machine-verifiable, tuned gates

```bash
# Lint the Dockerfile before building — fast, catches structural mistakes.
hadolint Dockerfile

# Build reproducibly with BuildKit and attach an SBOM to the image.
docker buildx build --sbom=true -t myorg/api:1.4.2 .

# Scan the FINAL image (not just the base) and fail only on fixable high/critical.
trivy image --severity HIGH,CRITICAL --ignore-unfixed \
  --exit-code 1 myorg/api:1.4.2

# Inspect layers to confirm the image is as small as expected.
dive myorg/api:1.4.2 --ci
```

**Bad Example** — no checks, wrong target, un-actionable gate

```bash
docker build -t myorg/api:latest .   # no lint, unpinned tag, no SBOM
# scan only the base image, missing every vulnerable app dependency:
trivy image node:22-slim
# gate fails on EVERY severity including un-fixable → team disables the scan
trivy image --exit-code 1 --severity UNKNOWN,LOW,MEDIUM,HIGH,CRITICAL myorg/api:latest
```

## Common Mistakes

- Treating `docker build` as the whole toolchain — no lint, no scan, no SBOM.
- Scanning the base image instead of the final built image, so app dependencies go
  unchecked.
- Failing CI on every severity including un-fixable CVEs, so the team disables the
  gate entirely.
- Running scanners once, manually, instead of on every build in
  [CI](29-ci-integration.md).
- Using `latest` in scan/build commands so results cannot be tied to a specific
  artifact.
- Adding a linter but ignoring its output, which is worse than not having it — it
  signals the checks are decorative.

## Production Tips

- Store scan and SBOM output as build artifacts keyed by image digest so audits can
  look back, not just look now.
- Emit findings as SARIF so they surface in the code host's security tab instead of
  buried in logs.
- Re-scan deployed images on a schedule: a CVE disclosed after you shipped affects
  an image that already passed once.
- Pin tool versions in CI so a scanner update does not silently change your gate.

## AI Review Checklist

- Is the Dockerfile linted (hadolint) in CI and, ideally, pre-commit?
- Is the final image (not just the base) scanned for CVEs?
- Does the CI gate fail on high/critical *fixable* findings and not on noise?
- Is an SBOM generated and retained per image digest?
- Are builds done with [BuildKit](10-buildkit.md)/`buildx`, with multi-arch where
  needed?
- Are images signed and verifiable in the deploy path?
- Are tool versions pinned so gates are stable?

## Related

- `knowledge/docker/10-buildkit.md`
- `knowledge/docker/18-security.md`
- `knowledge/docker/09-image-optimization.md`
- `knowledge/docker/29-ci-integration.md`
- `knowledge/docker/26-best-practices.md`
