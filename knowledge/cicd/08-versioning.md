---
id: cicd/08-versioning
topic: cicd
slug: versioning
title: "Versioning"
type: doc
order: 8
status: ready
tags: [cicd, versioning]
related: [cicd/07-artifacts, cicd/09-release-management, cicd/10-deployment, cicd/14-rollbacks]
when_to_use: "Read before choosing a version scheme or automating version bumps in a pipeline."
---
# Versioning

## Purpose

This document defines how to assign versions to [artifacts](07-artifacts.md) and releases
so that every deploy is identifiable, comparable, and traceable. A version is a contract:
it tells consumers what changed and whether an upgrade is safe. It also tells *you*,
during an incident, exactly which build is running and what came before it.

The rule of thumb: **the version must uniquely and monotonically identify a build**, and
for anything with an API surface it should communicate compatibility via
[Semantic Versioning](https://semver.org).

## Why It Matters

Bad versioning turns "roll back to the last good version" into archaeology. If two builds
share a version, or versions are hand-edited and skip around, you cannot answer "what is in
prod?" or "is this newer than that?" — the two questions every rollback and every incident
depend on. Versioning is also how consumers reason about risk: a bump from `2.4.1` to
`2.4.2` should be safe to take blindly, and from `2.x` to `3.0` should not. Break that
convention and every upgrade becomes a manual audit. Versions are cheap to get right and
extremely expensive to retrofit once released.

## Core Principles

- **One version, one build, forever.** A version identifier maps to exactly one artifact.
  Never re-tag a version onto different bytes; that destroys reproducibility and rollback.
- **Monotonic and comparable.** Versions must sort so that "newer" is unambiguous. This is
  why timestamps or auto-incremented semver beat hand-picked numbers.
- **SemVer for anything with consumers.** `MAJOR.MINOR.PATCH`: breaking / feature / fix.
  The trade-off is discipline — you must actually classify changes — but it lets downstream
  automation upgrade safely.
- **Derive versions from the repo, not from a human.** Compute from git tags/commits in
  CI so the version cannot drift from what was actually built.
- **Bind version to commit.** Every version must resolve back to one git SHA, and the
  running app must be able to report its version and SHA.

## Best Practices

- Use **SemVer** for libraries, packages, and public APIs. Bump MAJOR on breaking changes,
  MINOR on backward-compatible features, PATCH on fixes.
- For continuously-deployed services where SemVer's compatibility signal adds little, use a
  monotonic scheme: git SHA, `YYYY.MM.DD.<n>`, or `<tag>-<commits>-g<sha>` from
  `git describe`. Still bind it to a commit.
- Automate bumps from commit history (Conventional Commits + `semantic-release`,
  Changesets, or release-please) so classification is enforced and mechanical.
- Tag the git commit with the version and push the tag; the tag is the source of truth that
  ties source, artifact, and release together.
- Embed the version and SHA into the build (build arg, ldflags, env) so `/version` or
  `--version` reports exactly what is running.
- Use pre-release identifiers (`1.4.0-rc.1`, `-beta.2`) for candidates; never publish a
  release version for something unreleased.

## Examples

**Good Example** — version derived from git, embedded, single source of truth

```yaml
- name: Compute version
  id: v
  run: |
    # Derive from the nearest tag + commits since — monotonic and traceable to a SHA
    VERSION=$(git describe --tags --always --dirty)  # e.g. v2.4.1-3-g9f1c2ab
    echo "version=$VERSION" >> "$GITHUB_OUTPUT"

- name: Build with version baked in
  run: |
    docker build \
      --build-arg VERSION=${{ steps.v.outputs.version }} \
      --build-arg GIT_SHA=${GITHUB_SHA} \
      -t ghcr.io/acme/api:${{ steps.v.outputs.version }} .
    # The image tag, the /version endpoint, and the git tag all agree.
```

**Bad Example** — hand-edited, mutable, disconnected from source

```yaml
- run: echo "1.0.0" > VERSION            # edited by hand; nobody bumps it reliably
- run: docker build -t api:1.0.0 . && docker push api:1.0.0
# Next merge forgets to bump → a DIFFERENT build is pushed as 1.0.0 again.
# The tag now points at two different images; rollback-to-1.0.0 is ambiguous.
# The running app has no idea which commit it was built from.
```

## Common Mistakes

- Hand-editing a `VERSION` file and forgetting to bump it, so multiple builds share a
  version.
- Re-tagging an existing version onto new bytes (mutable versions break rollback).
- Bumping MAJOR/MINOR/PATCH arbitrarily, so the SemVer compatibility signal is meaningless.
- Versions that do not sort (e.g. `v10` < `v9` under string comparison, or random build
  numbers), making "which is newer?" unanswerable.
- The running service cannot report its own version, so incident responders must guess.
- Publishing a plain release version for a release candidate instead of a `-rc` pre-release.

## Production Tips

- Expose version + git SHA + build time on a `/version` or health endpoint and in log
  metadata, so any alert links straight to the exact build.
- Keep a generated changelog tied to version tags; it is the human-readable index for
  [release management](09-release-management.md) and rollback decisions.
- If you ship SDKs, document your compatibility policy explicitly — consumers only trust
  SemVer if you honor it.

## AI Review Checklist

- Does each version map to exactly one immutable artifact and one git SHA?
- Are versions monotonic and correctly sortable so "newer" is unambiguous?
- Do public APIs/libraries follow SemVer, with MAJOR reserved for breaking changes?
- Is the version derived from the repo in CI rather than hand-edited?
- Is the version embedded in the artifact and reported at runtime?
- Are release candidates marked with pre-release identifiers?
- Is the version tag pushed to git, tying source, artifact, and release together?

## Related

- `knowledge/cicd/07-artifacts.md`
- `knowledge/cicd/09-release-management.md`
- `knowledge/cicd/10-deployment.md`
- `knowledge/cicd/14-rollbacks.md`
