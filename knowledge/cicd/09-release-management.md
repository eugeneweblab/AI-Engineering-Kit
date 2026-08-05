---
id: cicd/09-release-management
topic: cicd
slug: release-management
title: "CI/CD Release Management"
type: doc
order: 9
status: ready
tags: [cicd, release-management]
related: [cicd/08-versioning, cicd/10-deployment, cicd/13-feature-flags, cicd/14-rollbacks]
when_to_use: "Read before defining how changes are cut, approved, and shipped as releases."
---
# CI/CD Release Management

## Purpose

This document defines the process that turns merged code into a shipped release: how you
cut a release, what gates approve it, how you communicate it, and how you roll it back.
Release management is the layer of policy *around* the mechanics of
[deployment](10-deployment.md) and [versioning](08-versioning.md) — it decides *what* ships
and *when*, and makes that decision repeatable and auditable.

A good release process is boring: predictable, mostly automated, and reversible. Drama in
releases is a sign the process is missing.

## Why It Matters

Releases are where accumulated risk is realized. Batch a month of changes into one release
and any failure could be caused by any of hundreds of commits — long to diagnose, painful
to roll back. Ship small, frequent, well-labeled releases and each failure has a short list
of suspects and a clean revert. Release management also decouples *deploy* from *release*:
you can push code to production dark (behind a [flag](13-feature-flags.md)) and turn it on
separately, so "ship the code" and "expose the feature" are independent, lower-risk steps.
Without a defined process, releases depend on whoever remembers the steps — which fails
exactly when that person is on vacation during an incident.

## Core Principles

- **Small and frequent beats big and rare.** Smaller releases shrink the diagnosis surface
  and the blast radius. The cost is more release events; automate them so the cost is near
  zero.
- **Decouple deploy from release.** Deploying code and enabling a feature are separate
  actions. This lets you ship continuously while releasing on your own schedule.
- **Every release is reversible.** Before you ship, know the rollback path. A release with
  no defined rollback is a bet, not a plan.
- **Automate the mechanics, gate the decision.** Cutting, tagging, changelog, and deploy
  are automated; the human role is an explicit, recorded approval, not manual button-mashing.
- **A release is a record, not just an event.** What shipped, which version, who approved,
  when — captured automatically, so any release is auditable after the fact.

## Best Practices

- Adopt a clear branching/release model: **trunk-based development** with short-lived
  branches and release-from-main is the default; use release branches only when you must
  support multiple live versions.
- Generate release notes and changelogs from commit history (Conventional Commits +
  release automation) so they are accurate and free.
- Tie each release to a [version](08-versioning.md) tag and an immutable
  [artifact](07-artifacts.md); the release *is* that artifact plus its metadata.
- Require approvals as code: protected environments with required reviewers, so approval is
  enforced by the pipeline, not by convention.
- Use progressive delivery ([canary](12-canary-deployment.md),
  [blue-green](11-blue-green-deployment.md), or flags) so a release can be validated on a
  slice of traffic before full exposure.
- Keep a rollback that is one command or one revert — and rehearse it, so it works under
  pressure.
- Avoid Friday-afternoon or pre-holiday releases of risky changes unless your rollback is
  fully automated; align release timing with when responders are available.

## Examples

**Good Example** — automated cut, gated deploy, recorded release

```yaml
# On merge to main: automation decides the version and drafts the release
on:
  push: { branches: [main] }
jobs:
  release:
    steps:
      - uses: googleapis/release-please-action@v4 # computes version + changelog from commits
        id: rp

  deploy:
    needs: release
    if: ${{ needs.release.outputs.release_created }}
    environment: production      # protected env → requires a recorded human approval
    steps:
      - run: deploy --version ${{ needs.release.outputs.tag_name }} --strategy canary
        # Deploy is gated, tied to a version, and progressive — validated before full rollout.
```

**Bad Example** — manual, unrecorded, irreversible

```bash
# Someone SSHes into the box on a Friday and ships a month of accumulated changes at once
git pull                       # no version tag, no changelog, no artifact
npm run build && pm2 restart   # rebuilds in place — prod now differs from staging
# No approval record, no canary, and rollback = "hope the old node_modules is still around"
# If it breaks, any of 300 commits could be the cause and there is no clean revert.
```

## Common Mistakes

- Batching huge releases, so failures are slow to diagnose and scary to revert.
- Coupling deploy and release, so you cannot ship code without immediately exposing the
  feature.
- No changelog or release record, leaving no audit trail of what shipped when.
- Manual, tribal-knowledge release steps that only one person can run.
- Shipping without a rehearsed rollback path.
- Rebuilding in place at release time instead of promoting a tested artifact.

## Production Tips

- Publish releases to a visible channel (GitHub Releases, a `#deploys` feed) with version,
  changelog, and the deployed artifact digest, so the whole team shares one source of truth.
- Maintain a lightweight release calendar or freeze window for high-traffic events; make
  freezes explicit in the pipeline, not verbal.
- Track DORA metrics (deploy frequency, lead time, change-fail rate, MTTR); they tell you
  whether the process is actually improving.

## AI Review Checklist

- Are releases small and frequent rather than large and batched?
- Is deploy decoupled from release (code can ship dark, features enabled separately)?
- Is each release tied to a version tag, an immutable artifact, and a changelog?
- Is approval enforced by the pipeline (protected environment) and recorded?
- Is there a rehearsed, one-step rollback for every release?
- Is the release validated progressively (canary/blue-green/flag) before full exposure?
- Is the release process fully scripted rather than dependent on one person?

## Related

- `knowledge/cicd/08-versioning.md`
- `knowledge/cicd/10-deployment.md`
- `knowledge/cicd/13-feature-flags.md`
- `knowledge/cicd/14-rollbacks.md`
