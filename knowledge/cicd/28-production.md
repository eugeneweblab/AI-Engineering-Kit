---
id: cicd/28-production
topic: cicd
slug: production
title: "CI/CD Production"
type: doc
order: 28
status: ready
tags: [cicd, production, deploy-prod, staging, failure]
related: [cicd/10-deployment, cicd/14-rollbacks, cicd/12-canary-deployment, cicd/16-environments, cicd/23-monitoring]
when_to_use: "Read before shipping a pipeline that deploys to production, or before a production release changes hands."
---
# CI/CD Production

## Purpose

This document defines what a CI/CD pipeline must guarantee when its target is
production — the environment where mistakes reach real users. It covers controlled
promotion, approvals, safe deployment strategies, rollback readiness, and the
audit trail that lets you answer "what changed and when" during an incident.

Production is not just another environment with a different URL. It is the one
where the cost of a bad deploy is real and immediate. Everything a pipeline does
for lower environments still applies here, plus additional gates whose purpose is
to make failure recoverable rather than catastrophic.

## Why It Matters

A production deploy is the highest-leverage, highest-risk action a pipeline takes.
Done well, it turns shipping from a nerve-wracking event into a routine,
several-times-a-day non-event. Done poorly — no rollback, no approval, no
observability — a single bad deploy causes an outage that takes down revenue and
trust at once.

The defining property of a production pipeline is *recoverability*. You cannot
prevent every bad change from reaching production, so the pipeline's real job is to
detect it fast and reverse it faster. A deploy you can't roll back in one step is a
deploy you should not run.

## Core Principles

- **Promote, never rebuild.** Ship the exact artifact that passed staging. Building
  a new artifact for production means shipping something no environment ever
  tested.
- **Every production deploy must be reversible in one step.** Automated
  [rollback](14-rollbacks.md) (or forward-fix) must be ready *before* the deploy
  starts, not improvised during the incident.
- **Gate production behind explicit approval and green checks.** A human approval
  or a required protection rule sits between "merged" and "live" for high-risk
  changes; all gates must be green.
- **Deploy gradually and watch.** Prefer [canary](12-canary-deployment.md) or
  [blue-green](11-blue-green-deployment.md) so a bad release hits a small fraction
  of traffic and is caught by [monitoring](23-monitoring.md) before full rollout.
- **Everything is audited.** Who deployed what, from which commit, when, and what
  the health was — recorded automatically, because incidents are reconstructed
  from this trail.

## Best Practices

- Use a protected production environment with required reviewers and required
  status checks so nothing reaches prod on a red or unreviewed pipeline.
- Deploy the artifact promoted from staging by digest, and record that digest in
  the release so the running version is unambiguous.
- Automate health checks post-deploy (readiness probes, smoke tests, key SLOs) and
  auto-rollback or halt on failure rather than waiting for a user report.
- Roll out progressively (canary %, then ramp) and bake in an observation window at
  each step before proceeding.
- Decouple deploy from release using [feature flags](13-feature-flags.md) so code
  can ship dark and be enabled independently, shrinking deploy risk.
- Keep production secrets in a managed store with least privilege and short-lived
  credentials (OIDC), never in pipeline files or environment defaults.
- Emit a deploy marker to [monitoring](23-monitoring.md) so dashboards annotate the
  exact moment of each release for fast incident correlation.

## Examples

**Good Example** — approval-gated, promote-by-digest, health-checked, reversible

```yaml
deploy-prod:
  needs: [staging-verified]
  environment:
    name: production          # protected env: required reviewers + checks
    url: https://app.example.com
  concurrency: prod-deploy    # serialize deploys; no overlapping releases
  steps:
    - run: |
        # Promote the EXACT image validated in staging (by digest, not tag).
        kubectl set image deploy/app app=registry/app@${{ needs.staging-verified.outputs.digest }}
        kubectl rollout status deploy/app --timeout=120s   # fail if it doesn't come up
    - run: ./smoke-test.sh https://app.example.com          # verify before declaring success
    - if: failure()
      run: kubectl rollout undo deploy/app                  # one-step automated rollback
```

**Bad Example** — rebuild, no approval, no rollback, no verification

```yaml
deploy-prod:
  # no environment protection, no approval -> anyone's merge goes straight to prod
  steps:
    - run: docker build -t app:latest . && docker push app:latest  # rebuilds untested artifact
    - run: kubectl set image deploy/app app=app:latest             # mutable tag: unclear what's live
    # no rollout status, no smoke test, no rollback path -> failure = manual scramble
```

## Common Mistakes

- Rebuilding for production instead of promoting the tested artifact, so prod runs
  code no environment validated.
- Deploying with mutable tags (`latest`) so the running version is ambiguous during
  an incident.
- No pre-planned rollback, turning every bad deploy into an improvised outage.
- Skipping human approval or required checks for high-risk production changes.
- Full-fleet deploys with no canary, so a bad release hits 100% of users at once.
- No post-deploy health check, so the pipeline reports success while production is
  down.
- Allowing concurrent/overlapping production deploys that race and leave an
  unknown state.

## Production Tips

- Rehearse rollback regularly — an untested rollback path is not a rollback path.
- Maintain a deploy freeze mechanism for high-risk windows, and make it explicit in
  the pipeline rather than tribal knowledge.
- Keep a one-page runbook linked from production [notifications](24-notifications.md)
  so the first responder acts, not searches.
- Record deploy frequency, change-failure rate, and time-to-restore (DORA metrics)
  to measure whether the production path is actually improving.

## AI Review Checklist

- Does production receive a promoted, digest-pinned artifact rather than a rebuild?
- Is there a one-step, tested rollback (or forward-fix) ready before deploy?
- Are approvals and required green checks enforced on the production environment?
- Is the rollout progressive (canary/blue-green) with an observation window?
- Are post-deploy health checks automated to halt/rollback on failure?
- Are concurrent production deploys prevented, and is every deploy audited with
  commit, actor, and time?

## Related

- `knowledge/cicd/10-deployment.md`
- `knowledge/cicd/14-rollbacks.md`
- `knowledge/cicd/12-canary-deployment.md`
- `knowledge/cicd/16-environments.md`
- `knowledge/cicd/23-monitoring.md`
