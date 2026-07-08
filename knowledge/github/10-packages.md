---
id: github/10-packages
topic: github
slug: packages
title: "Packages"
type: doc
order: 10
status: ready
tags: [github, packages]
related: [github/11-releases, github/08-actions, github/21-permissions, github/15-dependabot, github/13-security]
when_to_use: "Read before publishing, consuming, or versioning artifacts through GitHub Packages."
---
# Packages

## Purpose

This document defines how to publish and consume artifacts through **GitHub Packages** —
the registry integrated with a repository for npm, container (GHCR), Maven, NuGet, Gradle,
and RubyGems packages. It covers authentication, versioning, visibility, and cleanup. It
does not cover cutting a source release or changelog — that is [releases](11-releases.md).
A package is a *built, versioned artifact* consumers depend on; a release is the *source
milestone* it was built from.

Once published, a version is public API for its consumers. Treat every published version
as immutable and permanent.

## Why It Matters

A package registry is a distribution point: what you publish, other systems automatically
pull and run. Overwrite a version and you silently change what already-deployed consumers
get on their next install — a reproducibility and supply-chain nightmare. Publish with a
mutable `latest` tag and consumers get surprise upgrades. Leave old versions uncleaned and
you accumulate storage cost and confusion. And a package published from CI is signed with
your identity — a leaked publish token lets an attacker ship malware under your name.

## Core Principles

- **Versions are immutable.** Never republish or overwrite an existing version. Bug in
  `1.2.3`? Publish `1.2.4`. Consumers must be able to trust that a version never changes.
- **Follow semantic versioning.** MAJOR for breaking changes, MINOR for features, PATCH
  for fixes. The version number is a contract; violating it breaks consumers silently.
- **Authenticate with least-privilege, short-lived tokens.** Publish from CI using
  `GITHUB_TOKEN` with `packages: write` scoped to that job — not a personal token.
- **Pin what you consume.** Depend on exact versions or digests (`@sha256:...` for images),
  not floating tags, so builds are reproducible.
- **Match package visibility to the source repo.** A private package must not be publicly
  installable; verify visibility on first publish.

## Best Practices

- Publish from a workflow triggered by a release/tag, using `GITHUB_TOKEN` and job-scoped
  `permissions: { packages: write, contents: read }` — no long-lived PAT in secrets.
- Derive the package version from the git tag so the artifact and the source milestone
  always agree; never hand-edit the version at publish time.
- Tag container images with **both** an immutable version and a moving alias
  (`1.4.2` and `1.4`), and reference by **digest** in production deployments.
- Configure a **retention/cleanup policy** to delete untagged and old pre-release versions
  automatically, keeping storage and the version list manageable.
- Include provenance/SBOM (e.g., build attestations) so consumers can verify the artifact
  was built by your pipeline from the expected source.
- Consume GitHub Packages by authenticating the client to the registry host
  (`npm.pkg.github.com`, `ghcr.io`) with a read-scoped token, never an admin PAT.

## Examples

**Good Example** — CI publishes a container to GHCR, versioned from the tag

```yaml
on:
  push:
    tags: ["v*"]                     # publish only from a real release tag

jobs:
  publish:
    runs-on: ubuntu-24.04
    permissions:
      contents: read
      packages: write                # least privilege; no personal token needed
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
      - uses: docker/login-action@9780b0c442fbb1117ed29e0efdff1e18412f7567 # v3.3.0
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - run: |
          VERSION="${GITHUB_REF_NAME#v}"        # tag v1.4.2 -> 1.4.2
          IMAGE="ghcr.io/${{ github.repository }}"
          # Immutable version tag + moving minor alias; never overwrite an old version.
          docker build -t "$IMAGE:$VERSION" -t "$IMAGE:${VERSION%.*}" .
          docker push "$IMAGE:$VERSION"
          docker push "$IMAGE:${VERSION%.*}"
```

**Bad Example** — overwriting a mutable tag with a long-lived PAT

```yaml
on: push                                    # publishes on every commit
jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - run: |
          echo "${{ secrets.ADMIN_PAT }}" | docker login ghcr.io -u me --password-stdin
          # A single mutable tag, rebuilt every push → consumers get silent, untracked
          # changes and there is no immutable version to roll back to.
          docker build -t ghcr.io/acme/app:latest .
          docker push ghcr.io/acme/app:latest
```

## Common Mistakes

- Overwriting or force-pushing an existing version, breaking reproducibility for consumers.
- Publishing only a mutable tag (`latest`, `main`) with no immutable version.
- Violating semver — shipping a breaking change as a PATCH — and breaking downstreams.
- Publishing from CI with a broad personal access token instead of scoped `GITHUB_TOKEN`.
- Deploying containers by tag rather than digest, so the running image can change silently.
- No retention policy, so untagged layers and abandoned pre-releases pile up.
- Publishing a private package as public (or vice versa) by not checking visibility.

## Production Tips

- Reference production images by immutable **digest** in deployment manifests; tags can be
  repointed, digests cannot.
- Generate and attach a build attestation/SBOM so downstream consumers can verify
  provenance during their own security review.
- Automate cleanup with the `delete-package-versions` action or the registry's retention
  rules; keep the last N releases and prune untagged versions.
- Let Dependabot watch the ecosystems you consume so you get PRs when a dependency you
  pulled from Packages has a new secure version.

## AI Review Checklist

- Is the published version immutable and never overwritten?
- Does the version follow semver and derive from the git tag, not a manual edit?
- Is publishing done with a job-scoped `GITHUB_TOKEN`/`packages: write`, not a PAT?
- Are container images tagged with an immutable version and referenced by digest in prod?
- Is a retention/cleanup policy configured for old and untagged versions?
- Does package visibility match the source repository's visibility?
- Is provenance/SBOM attached so consumers can verify the artifact's origin?

## Related

- `knowledge/github/11-releases.md`
- `knowledge/github/08-actions.md`
- `knowledge/github/21-permissions.md`
- `knowledge/github/15-dependabot.md`
- `knowledge/github/13-security.md`
