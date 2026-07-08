---
id: github/11-releases
topic: github
slug: releases
title: "Releases"
type: doc
order: 11
status: ready
tags: [github, releases]
related: [github/10-packages, github/09-workflows, github/08-actions, github/06-pull-requests, github/26-automation]
when_to_use: "Read before tagging, cutting, or automating a GitHub release."
---
# Releases

## Purpose

This document defines how to cut a **GitHub release** — the tagged, versioned source
milestone with release notes and optional attached assets. It covers tagging, versioning,
changelogs, and pre-releases. It is distinct from [packages](10-packages.md): a release
marks *a point in the source history* and communicates *what changed*; a package is the
*built artifact* produced from it. A release without honest notes is just a tag.

A release is a promise to consumers: "this version exists, it means X, and it will not
change." Everything downstream — deploys, package pins, changelogs — trusts that promise.

## Why It Matters

Releases are the public contract of a project. Consumers pin to a version, read the notes
to decide whether to upgrade, and expect the tag to point at exactly the code that was
tested. A moved tag silently changes what `v1.2.0` means for everyone who pinned it. Notes
that omit a breaking change cause downstream outages the maintainer never sees. A release
cut by hand from a dirty working tree ships untested local changes. Because releases are
the unit people upgrade *to*, their integrity determines whether upgrading is safe.

## Core Principles

- **Tags are immutable.** Never move or delete a published tag. If `v1.2.0` was wrong,
  release `v1.2.1`. Moving a tag breaks every consumer who pinned it and every cached build.
- **Version with semver, and mean it.** The number tells consumers the upgrade risk:
  MAJOR = breaking, MINOR = additive, PATCH = fix. Mislabeling breaks people silently.
- **Release from CI on a tag, not from a laptop.** Automated releases are reproducible and
  built from clean, tested source; manual releases ship whatever was in someone's checkout.
- **Notes must be honest and complete.** Every breaking change, every security fix, and a
  migration note belong in the release. Omission is the most common release bug.
- **Pre-releases are not stable.** Mark alphas/RCs as pre-release so tooling and consumers
  do not treat them as production-ready.

## Best Practices

- Create an **annotated, signed tag** (`git tag -s v1.2.0`) and push it; trigger the
  release workflow on `push: tags: ["v*"]` so the release is built from that exact commit.
- Generate release notes from merged PRs (GitHub's auto-generated notes or a
  changelog tool) so the notes match what actually landed, then edit for breaking changes.
- Keep a human-readable `CHANGELOG.md` in *Keep a Changelog* style and reconcile it with
  the release notes; the changelog serves readers browsing the repo.
- Attach and **checksum** build assets (`sha256sum`) so consumers can verify downloads;
  sign assets where authenticity matters.
- Mark `v1.2.0-rc.1` style tags as **pre-release**, and use `latest` only for the newest
  stable release.
- Enforce that only maintainers/CI can push tags (via rulesets) so a release cannot be
  cut from an unreviewed branch.

## Examples

**Good Example** — signed tag drives an automated, note-generating release

```bash
# Tag the exact reviewed, tested commit; annotated + signed for provenance.
git tag -s v1.2.0 -m "v1.2.0"
git push origin v1.2.0
```

```yaml
on:
  push:
    tags: ["v*"]                       # release is built from the pushed tag only
permissions:
  contents: write                      # needed to create the release + upload assets
jobs:
  release:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
      - run: |
          make build
          (cd dist && sha256sum * > checksums.txt)   # verifiable assets
      - run: |
          gh release create "$GITHUB_REF_NAME" dist/* \
            --generate-notes \                        # notes from merged PRs
            $([ "${GITHUB_REF_NAME#*-}" != "$GITHUB_REF_NAME" ] && echo --prerelease)
        env: { GH_TOKEN: ${{ github.token }} }
```

**Bad Example** — a hand-cut release from a dirty tree with a moved tag

```bash
# Working tree has uncommitted local edits that were never reviewed or tested.
git tag v1.2.0                         # lightweight, unsigned, from whatever is checked out
git push origin v1.2.0

# Later, "fix" the release by moving the tag — silently changing what v1.2.0 means:
git tag -f v1.2.0                      # breaks everyone pinned to the old v1.2.0
git push -f origin v1.2.0

# Release notes: "bug fixes" — hides a breaking API change that will page consumers.
```

## Common Mistakes

- Moving or deleting a published tag, breaking pinned consumers and cached builds.
- Lightweight, unsigned tags with no provenance about who cut the release or from what.
- Cutting a release manually from a dirty or unreviewed working tree.
- Release notes that omit breaking changes, security fixes, or migration steps.
- Bumping the wrong semver component (breaking change shipped as a PATCH).
- Not marking RCs/betas as pre-release, so tooling upgrades users to unstable code.
- Attaching assets with no checksums, leaving consumers unable to verify downloads.

## Production Tips

- Gate tag creation with a ruleset so only maintainers or the release workflow can push
  `v*` tags; this stops accidental or unreviewed releases.
- Wire the release workflow to also publish the built artifact to
  [packages](10-packages.md) so the source milestone and distributed artifact stay in lock
  step, versioned from the same tag.
- For libraries, automate version bumps and changelog entries from Conventional Commits so
  the release notes and version are derived, not hand-maintained.
- Keep an explicit support/deprecation policy in the notes for MAJOR releases so consumers
  know the upgrade window.

## AI Review Checklist

- Is the release tied to an immutable, never-moved, signed tag?
- Does the version correctly reflect semver (breaking vs additive vs fix)?
- Is the release built from CI on the tag, not cut manually from a local checkout?
- Do the notes list every breaking change, security fix, and migration step?
- Are pre-releases (RC/beta/alpha) marked as pre-release, not latest?
- Are attached assets checksummed (and signed where authenticity matters)?
- Is tag creation restricted to maintainers/CI via a ruleset?

## Related

- `knowledge/github/10-packages.md`
- `knowledge/github/09-workflows.md`
- `knowledge/github/08-actions.md`
- `knowledge/github/06-pull-requests.md`
- `knowledge/github/26-automation.md`
