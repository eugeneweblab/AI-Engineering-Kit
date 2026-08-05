---
id: devops/04-branching-strategies
topic: devops
slug: branching-strategies
title: "Branching Strategies"
type: doc
order: 4
status: ready
tags: [devops, branching-strategies, enabled, CONFLICT, feat, develop, release]
related: [devops/03-git-workflow, devops/05-build-pipelines, devops/06-release-management, devops/07-deployment-strategies, devops/02-development-lifecycle]
when_to_use: "Read before choosing or reviewing how a team integrates work — trunk-based, GitHub Flow, or release branches."
---
# Branching Strategies

## Purpose

This document defines how a team should organize integration: how many long-lived
branches exist, how long feature branches live, and how releases are cut. Where
[03 Git Workflow](03-git-workflow.md) covers individual commits and PRs, this doc covers
the *branch topology* those PRs flow through. The choice directly shapes integration
pain, release cadence, and how fast a fix reaches production.

## Why It Matters

The branching model is the single biggest lever on integration risk. Long-lived branches
that diverge from `main` for weeks produce "merge hell" — huge conflicts, and the discovery
that two features are incompatible only at merge time, when both are expensive to change.
Continuous Integration is literally named for the practice this doc governs: integrating
frequently so conflicts and incompatibilities surface while they are small. The strategy
also determines your worst-case time-to-fix: a heavyweight release-branch model can add
hours of ceremony to shipping a one-line hotfix.

## Core Principles

- **Short-lived branches.** A feature branch should live hours to a couple of days, not
  weeks. The longer it lives, the more it diverges and the harder it integrates.
- **`main` is always releasable.** The default branch must stay green and deployable at all
  times. Broken code never lands there. This is what lets you ship on demand.
- **Prefer the simplest model that fits.** Trunk-based development (everyone commits to
  `main` behind reviews and CI) is the default recommendation and correlates with elite
  DORA performance. Add complexity only when a real constraint demands it.
- **Feature flags over feature branches.** Merge incomplete work to `main` *dark* behind a
  flag rather than hiding it on a branch. This keeps integration continuous while the
  feature stays hidden from users. See [09 Configuration Management](09-configuration-management.md).

## The Common Models

- **Trunk-based development** — everyone integrates to `main` many times a day; short branches
  merge fast; incomplete work hides behind flags. Best for continuous delivery. The default.
- **GitHub Flow** — one `main` plus short-lived feature branches merged via PR, deployed on
  merge. A lightweight, widely used variant of trunk-based; excellent for web services.
- **Git Flow** — long-lived `develop`, `release`, and `hotfix` branches around `main`. Built
  for versioned, scheduled releases (e.g. installed software). Heavy and slow for
  continuously deployed services; usually the *wrong* default in 2026.
- **Release branches** — cut a `release/x.y` branch from `main` to stabilize a version while
  `main` moves on. Use when you must maintain multiple shipped versions at once.

## Best Practices

- Default to trunk-based or GitHub Flow for anything you deploy continuously. Reach for
  Git Flow only when you ship discrete, versioned, supported releases.
- Enforce short branch lifetimes: if a branch is older than a few days, rebase and merge or
  split it. Track branch age as a health signal.
- Protect `main`: require green CI and review before merge, and forbid direct pushes. See
  [23 Quality Gates](23-quality-gates.md).
- Cherry-pick hotfixes from `main` onto active release branches (fix forward, then
  back-port), so the fix exists on the mainline and does not get lost on the next release.
- Delete branches after merge to keep the branch list meaningful.

## Examples

**Good Example** — trunk-based with a feature flag

```bash
git switch -c add-csv-export     # short-lived branch off main
# ...small change, guarded by a flag so it can merge before it's user-ready...
git commit -am "feat(export): add CSV export behind `csv_export` flag"
# Merge to main today, even though the feature is incomplete:
#   if (flags.enabled("csv_export")) renderCsvButton()
# main stays releasable; integration stays continuous; the flag hides the feature.
```

**Bad Example** — long-lived divergent branch

```bash
git switch -c big-redesign
# ...3 weeks of commits, never rebased onto main...
git merge main
# CONFLICT (content): 47 files.
# Two features touched the same modules for weeks. The conflicts and the design
# incompatibility both surface now, at the most expensive possible moment.
```

## Common Mistakes

- Adopting Git Flow for a continuously deployed web service, adding release ceremony that
  buys nothing and slows every fix.
- Feature branches that live for weeks, guaranteeing painful merges and hidden conflicts.
- Committing directly to an unprotected `main`, so a broken commit blocks everyone.
- Hotfixing only a release branch and forgetting to merge the fix back to `main`, so it
  regresses on the next release.
- Never deleting merged branches, leaving a branch list nobody can navigate.

## Production Tips

- Instrument feature flags with a clear lifecycle: every flag needs an owner and a removal
  date, or you accumulate permanent dead branches in code.
- Automate versioning and changelog generation from Conventional Commits so release
  branches don't require manual bookkeeping. See [06 Release Management](06-release-management.md).

## AI Review Checklist

- Is the strategy the simplest that fits — trunk-based/GitHub Flow unless versioned
  releases genuinely require Git Flow?
- Are feature branches short-lived (hours to a couple of days)?
- Is `main` protected, always green, and always releasable?
- Is incomplete work merged behind a feature flag rather than parked on a long branch?
- Are hotfixes applied to `main` and back-ported/cherry-picked to active release branches?

## Related

- `knowledge/devops/03-git-workflow.md`
- `knowledge/devops/05-build-pipelines.md`
- `knowledge/devops/06-release-management.md`
- `knowledge/devops/07-deployment-strategies.md`
- `knowledge/devops/02-development-lifecycle.md`
