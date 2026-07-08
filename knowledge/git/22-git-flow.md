---
id: git/22-git-flow
topic: git
slug: git-flow
title: "Git Flow"
type: doc
order: 22
status: ready
tags: [git, git-flow]
related: [git/23-trunk-based-development, git/05-branches, git/06-merging, git/12-tags, git/27-best-practices]
when_to_use: "Read before adopting or reviewing a branching model for a versioned, release-based product."
---
# Git Flow

## Purpose

This document defines Git Flow: a branching model built around long-lived `main` and
`develop` branches plus short-lived `feature/*`, `release/*`, and `hotfix/*` branches.
It explains how the branches relate, when Git Flow is the right choice, and — just as
important — when it is the wrong one and you should prefer
[trunk-based development](23-trunk-based-development.md) instead.

Git Flow is a *convention*, not a Git feature. It is a set of rules about which branch
merges into which, and when. An agent's job is to know the rules well enough to follow
them correctly and to recognize the (fairly narrow) situations where they pay off.

## Why It Matters

A branching model is a coordination contract for the whole team; getting it wrong
produces merge hell, lost hotfixes, and releases that ship the wrong commits. Git Flow
became popular because it maps cleanly onto products with *explicit, versioned releases*
and multiple versions supported in parallel — installers, firmware, libraries with LTS
lines. But applied to a web app that deploys continuously, Git Flow's long-lived
branches cause exactly the large, painful merges it claims to avoid. Choosing the model
that matches your release cadence matters more than executing either model perfectly.

## Core Principles

- **Two permanent branches with distinct roles.** `main` holds released, tagged,
  production code — every commit is a shippable version. `develop` is the integration
  branch where features accumulate for the next release.
- **Features branch from and merge back to `develop`**, never to `main`.
- **Releases are stabilized on a `release/*` branch** cut from `develop`; only fixes go
  there. It merges into both `main` (tagged) and `develop`.
- **Hotfixes branch from `main`**, fix production directly, and merge into *both* `main`
  and `develop` so the fix is not lost in the next release.
- **Every merge to `main` is tagged** with a version — `main`'s history is the release
  history.
- **It fits scheduled releases, not continuous deployment.** The more often you deploy,
  the less Git Flow's overhead is worth.

## Best Practices

- Use Git Flow only when you have *discrete, versioned releases* or must support
  multiple versions in parallel. For continuously deployed web services, prefer
  trunk-based development.
- Keep `feature/*` branches short-lived and rebase/merge `develop` into them often;
  long-lived features re-create the big-merge problem Git Flow is meant to avoid.
- Never commit directly to `main` or `develop` — go through a reviewed pull request from
  a feature, release, or hotfix branch.
- Tag every `main` merge with a semantic version and let that drive the changelog and
  deployment (see [tags](12-tags.md)).
- Always merge a `hotfix/*` back into `develop` too; forgetting this is the classic Git
  Flow bug — the fix reappears as a regression next release.
- Delete `feature/*`, `release/*`, and `hotfix/*` branches after they merge to keep the
  ref namespace legible.

## Examples

**Good Example** — a hotfix propagated to both permanent branches

```bash
# Production bug on the released version: branch from main (the released code).
git switch main && git switch -c hotfix/1.4.1
# ...fix, commit...

# Merge to main and TAG the patch release.
git switch main && git merge --no-ff hotfix/1.4.1
git tag -a v1.4.1 -m "Hotfix: session leak"

# CRITICAL: also merge into develop so the fix is not lost next release.
git switch develop && git merge --no-ff hotfix/1.4.1
git branch -d hotfix/1.4.1
```

**Bad Example** — Git Flow on a continuously deployed app, hotfix half-merged

```bash
# A web app that deploys on every merge to main adopts Git Flow anyway.
# develop drifts from main for weeks; the eventual release/* merge is a giant conflict.
git switch main && git switch -c hotfix/urgent
git switch main && git merge hotfix/urgent   # fixed prod...
# ...and stopped here. Never merged into develop.
# Next release from develop SILENTLY re-introduces the bug as a regression.
```

## Common Mistakes

- Adopting Git Flow for a continuously deployed service, where long-lived `develop`
  causes the large merges it was meant to prevent.
- Forgetting to merge a `hotfix/*` back into `develop`, so the fix regresses at the next
  release.
- Letting `feature/*` branches live for weeks, guaranteeing painful integration.
- Committing directly to `main` or `develop` instead of via reviewed branches.
- Merging to `main` without tagging, losing the release-to-commit mapping.
- Confusing `develop` with a deployable branch — only `main` is production.

## Production Tips

- Automate the model with tooling (the `git-flow` extension or platform release
  workflows) so branch sources and merge targets are not chosen by hand.
- Gate `release/*` and `main` with branch protection: required reviews, green CI, and
  no direct pushes.
- If you find yourself cutting releases daily and fighting `develop` merges, that is the
  signal to migrate to [trunk-based development](23-trunk-based-development.md) with
  feature flags.

## AI Review Checklist

- Does the project actually have discrete, versioned releases that justify Git Flow?
- Do features branch from and merge to `develop`, never directly to `main`?
- Is every `hotfix/*` merged into *both* `main` and `develop`?
- Is every merge to `main` tagged with a version?
- Are release/feature/hotfix branches short-lived and deleted after merge?
- Would trunk-based development fit better given the deploy cadence?

## Related

- `knowledge/git/23-trunk-based-development.md`
- `knowledge/git/05-branches.md`
- `knowledge/git/06-merging.md`
- `knowledge/git/12-tags.md`
- `knowledge/git/27-best-practices.md`
