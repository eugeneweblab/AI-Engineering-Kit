---
id: github/18-rulesets
topic: github
slug: rulesets
title: "Rulesets"
type: doc
order: 18
status: ready
tags: [github, rulesets, active, evaluate, disabled, DEFAULT_BRANCH, release, pull_request]
related: [github/17-branch-protection, github/19-organizations, github/13-security, github/06-pull-requests, github/22-api]
when_to_use: "Read before defining, migrating to, or reviewing repository or organization protection rules for branches and tags."
---
# Rulesets

## Purpose

This document defines how to protect branches and tags with **rulesets** — GitHub's
successor to classic branch protection. It is written so an agent can author, layer,
and review rulesets without weakening the repository's guarantees or locking out
automation.

A ruleset is a named, versioned collection of rules that targets branches or tags by
pattern and is enforced with an explicit status. Unlike classic
[branch protection](17-branch-protection.md), rulesets can be defined at the
**organization** level, target **tags**, run in a non-blocking **evaluate** mode, and
**stack** — several rulesets can apply to the same ref at once.

## Why It Matters

Rulesets are the enforcement point for your entire delivery process: who can merge,
what checks must pass, whether history stays linear, whether commits are signed. A gap
here is not a local bug — it lets unreviewed or unsigned code reach `main` across every
repository that inherits the org ruleset. Because rulesets *layer*, a subtle mistake
(an overly broad bypass, a pattern that misses `release/*`) silently disables the
protection you think you have. The failure is invisible until an incident, so rulesets
are held to the same bar as production access control.

## Core Principles

- **Stacking is additive and most-restrictive-wins.** When multiple rulesets target a
  ref, every rule from every active ruleset applies. You cannot loosen a rule by adding
  a second ruleset — only bypass lists relax enforcement.
- **Enforcement status is a first-class control.** `active` blocks, `evaluate` records
  violations without blocking (dry-run for new rules), `disabled` is off. Never ship a
  new org-wide rule straight to `active`.
- **Bypass is the only escape hatch — keep it tiny.** Only listed actors (roles, teams,
  or apps) can bypass, and only for the modes you grant. A bypass list is a standing
  privilege; treat it like admin access.
- **Target by intent, not by accident.** Patterns use `fnmatch`; `~DEFAULT_BRANCH` and
  `~ALL` are explicit targets. An unanchored pattern that misses a ref fails open.
- **Org rulesets beat per-repo drift.** Define baseline protection once at the org level
  so new repositories are covered on creation, not after someone remembers.

## Best Practices

- Roll out new or tightened rules in **`evaluate`** mode first, read the insights, then
  promote to `active`. The cost of skipping this is a broken merge queue for everyone.
- Protect `main` and release branches with: require a pull request, require status
  checks (mark them **strict**/up-to-date), block force pushes, and require linear
  history or signed commits per your policy.
- Add a **tag ruleset** that restricts who can create or delete `v*` tags — releases are
  as sensitive as branches and classic protection never covered them.
- Grant bypass to **automation apps by app id**, not to broad human roles. Prefer
  "bypass for pull requests only" over "always allow".
- Keep rulesets in version control by exporting them as JSON and applying via the
  [API](22-api.md); review changes in a PR like any other infrastructure.
- Use org-level rulesets with repository targeting (by name pattern or property) to set
  a floor; let repos add stricter rules on top, never looser.

## Examples

**Good Example** — layered, evaluated, minimal bypass (ruleset as JSON)

```json
{
  "name": "protect-main",
  "target": "branch",
  "enforcement": "active",                 // promoted only after an evaluate run
  "conditions": {
    "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] }
  },
  "bypass_actors": [
    { "actor_type": "Integration", "actor_id": 12345, "bypass_mode": "pull_request" }
    // only the release bot, and only via PR — no standing human bypass
  ],
  "rules": [
    { "type": "pull_request",
      "parameters": { "required_approving_review_count": 2,
                      "dismiss_stale_reviews_on_push": true } },
    { "type": "required_status_checks",
      "parameters": { "strict_required_status_checks_policy": true,   // must be up-to-date
                      "required_status_checks": [ { "context": "ci/build" } ] } },
    { "type": "non_fast_forward" },        // blocks force pushes
    { "type": "required_signatures" }
  ]
}
```

**Bad Example** — one blocking rule, broad bypass, wrong target

```json
{
  "name": "protect-everything",
  "target": "branch",
  "enforcement": "active",                 // shipped straight to blocking, no dry-run
  "conditions": {
    "ref_name": { "include": ["main"], "exclude": [] }   // literal 'main' misses release/*
  },
  "bypass_actors": [
    { "actor_type": "OrganizationAdmin", "bypass_mode": "always" }  // every admin, always
  ],
  "rules": [
    { "type": "required_status_checks",
      "parameters": { "strict_required_status_checks_policy": false, // stale merges allowed
                      "required_status_checks": [ { "context": "ci/build" } ] } }
    // no PR requirement → direct pushes to main are still allowed
  ]
}
```

## Common Mistakes

- Assuming a second ruleset can *loosen* a rule — it cannot; only bypass lists relax.
- Enabling a new org ruleset as `active` and breaking every team's merge at once,
  instead of running it in `evaluate` first.
- Using a literal branch name (`main`, `release`) instead of a pattern, so `release/2.0`
  is unprotected.
- Granting `bypass_mode: always` to a broad role, quietly disabling the whole ruleset.
- Forgetting tag rulesets, leaving release tags creatable and deletable by anyone.
- Running rulesets *and* legacy branch protection on the same ref, then debugging the
  confusing union of both.

## Production Tips

- Read the **Rule Insights** log to see what would have been blocked before promoting
  from `evaluate`; it names the actor, ref, and rule.
- Store the canonical ruleset JSON in a repo and reconcile it via a scheduled workflow
  so manual UI edits drift back into review.
- When migrating from classic protection, create the ruleset in `evaluate`, confirm no
  new violations, then delete the classic rule and set the ruleset `active`.

## AI Review Checklist

- Is every new or tightened rule shipped through `evaluate` before `active`?
- Do ref patterns cover all protected refs (`release/*`, tags), not just literal `main`?
- Is the bypass list minimal, app-scoped, and preferring `pull_request` over `always`?
- Are force pushes blocked and PR review + strict status checks required on `main`?
- Is there a tag ruleset restricting creation/deletion of release tags?
- Are rulesets stored as reviewed JSON rather than edited only in the UI?
- Is classic [branch protection](17-branch-protection.md) removed once a ruleset replaces it?

## Related

- `knowledge/github/17-branch-protection.md`
- `knowledge/github/19-organizations.md`
- `knowledge/github/13-security.md`
- `knowledge/github/06-pull-requests.md`
- `knowledge/github/22-api.md`
