---
id: git/23-trunk-based-development
topic: git
slug: trunk-based-development
title: "Trunk Based Development"
type: doc
order: 23
status: ready
tags: [git, trunk-based-development, enabled, develop]
related: [git/22-git-flow, git/05-branches, git/06-merging, git/16-push, git/27-best-practices]
when_to_use: "Read before setting up a branching model for a continuously deployed service, or moving off Git Flow."
---
# Trunk Based Development

## Purpose

This document defines trunk-based development (TBD): a branching model where every
developer integrates into a single shared branch (`main`, the "trunk") at least daily,
using short-lived branches and feature flags to keep the trunk always releasable. It
explains the practices that make TBD safe and contrasts it with
[Git Flow](22-git-flow.md).

TBD is the branching model behind continuous delivery. Its core bet is that *frequent,
small integrations* are cheaper and safer than infrequent, large ones — that merge pain
grows super-linearly with branch age, so the fix is to never let a branch get old.

## Why It Matters

Long-lived branches are where integration risk hides. Two branches that each work in
isolation can conflict semantically in ways no merge tool detects, and the longer they
diverge the worse it gets. TBD attacks this directly: by merging to trunk daily, every
divergence is caught within hours, while it is small. The trade-off is discipline —
trunk must stay green and releasable at all times, which forces feature flags, strong
CI, and small changes. Teams that adopt TBD without those supports get a broken trunk
and blame the model.

## Core Principles

- **One shared trunk, always releasable.** `main` must be deployable at every commit.
  Anything that would break it hides behind a flag or does not merge.
- **Integrate at least daily.** Branches live hours to a day or two, not weeks. Branch
  age is the enemy; keep it near zero.
- **Small, incremental changes.** Break large features into small, independently
  mergeable, individually safe steps.
- **Feature flags decouple deploy from release.** Merge and deploy incomplete work dark;
  turn it on later. This is what lets unfinished code live on trunk safely.
- **CI is the gate, not review latency.** Fast, reliable automated tests on every change
  are non-negotiable; a slow or flaky pipeline makes daily integration impossible.
- **Fix the trunk first.** A broken trunk is a stop-the-line event — reverting or fixing
  it takes priority over new work.

## Best Practices

- Create short-lived branches off `main`, open a pull request within a day, merge, and
  delete. If a branch is older than ~48 hours, that is a smell — split it.
- Keep changes small enough to review quickly; large PRs slow integration and defeat the
  model.
- Hide any change that is not yet safe to release behind a feature flag; merge the flag
  off, enable it independently once complete and tested.
- Prefer merging trunk into your branch (or rebasing) frequently so your branch never
  drifts far from `main`.
- Make `main` a protected branch requiring green CI and review; forbid direct pushes and
  force-pushes.
- Release from trunk directly, or cut a short-lived `release/*` branch only to stabilize
  a specific version — never a long-lived parallel line.
- Invest in a fast, deterministic test suite; TBD's safety depends entirely on CI
  catching breakage in minutes.

## Examples

**Good Example** — merge incomplete work safely behind a flag

```bash
# Short-lived branch, opened and merged the same day.
git switch -c add-csv-export main
# ...small change, gated so it can ship dark...
```

```ts
// The new path is merged to trunk but OFF by default. Trunk stays releasable
// even though the feature is unfinished; the flag is flipped on later, separately.
if (flags.enabled("csv-export")) {
  return exportAsCsv(rows);
}
return exportAsJson(rows); // existing, proven behavior remains the default
```

**Bad Example** — long-lived feature branch, no flags

```bash
# A three-week "big feature" branch that never touches main.
git switch -c big-redesign main
# ...40 commits over 3 weeks, main moves on independently...

git switch main && git merge big-redesign
# Massive semantic conflicts CI never saw; trunk is red for a day.
# Because there was no feature flag, the half-done work can't be merged
# earlier and can't be turned off — it's all-or-nothing.
```

## Common Mistakes

- Long-lived branches that defeat the model's entire purpose — merge pain returns.
- Adopting TBD without feature flags, forcing an all-or-nothing "big bang" merge.
- Merging work that breaks the trunk and leaving it red instead of reverting
  immediately.
- Weak or slow CI, so daily integration is not actually safe and defects slip through.
- Oversized pull requests that cannot be reviewed quickly, throttling integration.
- Treating `main` as "someone else's problem" rather than everyone's shared,
  always-green responsibility.

## Production Tips

- Adopt a feature-flag system early; without it, TBD degrades into either broken trunks
  or long branches. Clean up stale flags on a schedule so they do not accumulate.
- Optimize CI ruthlessly — parallelize, cache, and quarantine flaky tests. Integration
  frequency is capped by pipeline speed and trust.
- Pair TBD with automated deploys: small changes flowing to production continuously is
  where the model's payoff (fast feedback, small blast radius) actually lands.
- For an existing Git Flow team, migrate by shortening branch life and shrinking
  `develop`'s role until trunk *is* the integration point.

## AI Review Checklist

- Are branches short-lived (hours to a day), integrated to trunk daily?
- Is `main` releasable at every commit, with unfinished work behind feature flags?
- Are changes small enough to review and merge quickly?
- Is CI fast, reliable, and required on every change before merge?
- Is a broken trunk treated as stop-the-line and reverted immediately?
- Are feature flags cleaned up once the work is fully released?

## Related

- `knowledge/git/22-git-flow.md`
- `knowledge/git/05-branches.md`
- `knowledge/git/06-merging.md`
- `knowledge/git/16-push.md`
- `knowledge/git/27-best-practices.md`
