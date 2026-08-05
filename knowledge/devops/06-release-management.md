---
id: devops/06-release-management
topic: devops
slug: release-management
title: "DevOps Release Management"
type: doc
order: 6
status: ready
tags: [devops, release-management]
related: [devops/05-build-pipelines, devops/07-deployment-strategies, devops/04-branching-strategies, devops/24-change-management, devops/25-incident-management]
when_to_use: "Read before cutting a release, versioning an artifact, or designing how changes reach production."
---
# DevOps Release Management

## Purpose

This document defines how a validated build becomes a released version: versioning,
release artifacts, changelogs, approval, and rollback. It is written so an agent can
plan or review a release without shipping an unidentifiable, irreversible, or
unauditable change.

Release management is distinct from [deployment](07-deployment-strategies.md).
*Release* decides **what** is shipped and **that it is allowed to ship** (which commit,
which version, who approved it). *Deployment* decides **how** those bits reach running
servers. Keep the two separable — you should be able to build a release once and deploy
it many times without rebuilding.

## Why It Matters

A release is the unit you reason about when something breaks at 2 a.m. If you cannot
name the exact version running, diff it against the last known-good version, and roll
back to that version in one command, every incident becomes an archaeology project. The
cost of sloppy release management is paid entirely during outages — the worst possible
time. Good release hygiene is cheap to set up and turns a panicked rollback into a
routine one.

## Core Principles

- **Build once, promote the same artifact.** The bytes tested in staging must be the
  bytes that run in production. Rebuilding per environment reintroduces the "works on
  my machine" class of bug you were trying to eliminate.
- **Every release has an immutable, unique identifier.** A version string (SemVer) plus
  the exact commit SHA. Never re-tag or overwrite a published version.
- **A release is traceable to its inputs.** From a running version you must reach the
  commit, the build, the changelog, and the approver in a few clicks.
- **Rolling back is a first-class path, not an afterthought.** Every forward release
  must have a defined, tested way back.
- **Releasing is a decision, deploying is a mechanism.** Gate the decision (approval,
  quality checks); automate the mechanism.

## Best Practices

- Version with **Semantic Versioning** (`MAJOR.MINOR.PATCH`) for anything with a public
  contract; bump MAJOR on breaking changes so consumers can pin safely. Use date-based
  or monotonic build numbers for internal-only services where SemVer adds no signal.
- Tag the release commit in git (`v2.4.0`) and embed the same version + commit SHA in
  the artifact and in a `/version` or health endpoint. You want to read the version off
  the running process, not guess it.
- Generate the changelog from commit history (Conventional Commits make this
  mechanical). A human-readable "what changed and who is affected" section belongs in
  every release.
- Separate **release** from **rollout** using feature flags: ship code dark, enable it
  by flag. This decouples "deployed" from "live" and makes rollback a config change.
- Require an explicit approval gate for production releases, and record who approved
  what. Automate the gate's *checks* (tests, security scan, sign-off) so approval is
  informed, not ceremonial.
- Keep the last several releases immediately re-deployable so rollback is "deploy the
  previous artifact," not "rebuild an old commit and hope."

## Examples

**Good Example** — build once, tag immutably, promote the same artifact

```yaml
# CI: build a single, versioned, immutable artifact from a tagged commit.
build-release:
  # SemVer + commit SHA make the artifact uniquely identifiable and traceable.
  variables:
    VERSION: "2.4.0"
    IMAGE: "registry.example.com/api:2.4.0-${CI_COMMIT_SHORT_SHA}"
  script:
    - docker build -t "$IMAGE" .
    - docker push "$IMAGE"          # push once; this digest is now frozen
    - echo "$IMAGE" > release.txt   # promote this exact reference downstream

promote-to-prod:
  needs: [build-release]
  script:
    # Deploy the SAME image that passed staging — no rebuild, no drift.
    - deploy --image "$(cat release.txt)" --env production
```

**Bad Example** — rebuild per environment, mutable tag, no traceability

```yaml
deploy-prod:
  script:
    # Rebuilds from whatever main looks like NOW — not what was tested in staging.
    - docker build -t registry.example.com/api:latest .
    # "latest" is mutable: two deploys days apart can run different code under one tag.
    - docker push registry.example.com/api:latest
    - deploy --image registry.example.com/api:latest --env production
    # No version, no SHA, no changelog: the running code cannot be identified.
```

## Common Mistakes

- Rebuilding the artifact for production instead of promoting the tested one.
- Deploying a mutable tag (`latest`, `stable`) so the running code cannot be pinned.
- No changelog or a changelog that lists commits nobody can map to user-facing impact.
- Coupling release to deploy so a risky rollout cannot be flipped off without a redeploy.
- Treating rollback as "revert the PR and rebuild" — slow, and the rebuild may differ.
- Re-tagging or force-pushing a released version, destroying the audit trail.

## Production Tips

- Expose version + commit SHA + build time on a health/version endpoint; incident
  responders read it first.
- Keep a machine-readable release manifest (version, image digest, approver, timestamp)
  so tooling and audits do not depend on human memory.
- Practice rollback in a game day. An untested rollback path is a hope, not a plan.
- For libraries, publish immutable versions and never unpublish; downstream builds pin
  to them.

## AI Review Checklist

- Is the production artifact the *same* one that passed staging, not a rebuild?
- Does every release have a unique SemVer/version plus commit SHA, and is it immutable?
- Can the running version be read off a live endpoint and traced to its commit?
- Is there a generated changelog describing user-facing impact?
- Is there a defined, tested rollback to the previous release?
- Is release (the decision + approval) separable from deployment (the mechanism)?

## Related

- `knowledge/devops/05-build-pipelines.md`
- `knowledge/devops/07-deployment-strategies.md`
- `knowledge/devops/04-branching-strategies.md`
- `knowledge/devops/24-change-management.md`
- `knowledge/devops/25-incident-management.md`
