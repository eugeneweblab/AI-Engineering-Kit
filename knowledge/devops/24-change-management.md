---
id: devops/24-change-management
topic: devops
slug: change-management
title: "Change Management"
type: doc
order: 24
status: ready
tags: [devops, change-management]
related: [devops/06-release-management, devops/07-deployment-strategies, devops/23-quality-gates, devops/25-incident-management, devops/26-postmortems]
when_to_use: "Read before rolling out any production change, defining a deploy/rollback process, or reviewing a CI/CD promotion pipeline."
---
# Change Management

## Purpose

This document defines how a change reaches production safely: how it is proposed,
reviewed, approved, deployed, and — when it goes wrong — rolled back. It is written
so an agent can build or review a change process that is fast for routine work yet
still catches the changes that will break things.

Change management answers "how do we alter a running system without causing an
outage?". It is the discipline that sits between a merged commit and a healthy
production deploy. Do not confuse it with heavyweight bureaucracy — modern change
management is mostly automation, with human judgment reserved for genuine risk.

## Why It Matters

The large majority of production incidents are self-inflicted: they are triggered by
a change we made, not by hardware failing or traffic spiking. That makes the change
pipeline the single highest-leverage place to prevent outages. A change process that
is too loose lets a bad deploy reach every user at once; a process that is too rigid
pushes people to batch changes into rare, huge, high-risk releases — which are far
more dangerous than small frequent ones. The goal is to make the *safe* path also the
*fast* path, so nobody is tempted to route around it.

## Core Principles

- **Small changes, frequently.** A small diff fails in small, diagnosable ways. Large
  batched releases couple many changes so you cannot tell which one broke, and the
  blast radius is total. Optimize for lead time, not for release ceremony.
- **Every change is reversible.** Before you ship, know exactly how to undo it. A
  change with no rollback path is not ready, because "roll forward with a fix" is a
  hope, not a plan.
- **Automate the pipeline, gate on risk.** Routine, low-risk changes should flow
  through automated gates with no human sign-off. Reserve manual approval for changes
  that are high blast-radius, irreversible, or touch data.
- **Progressive exposure.** Do not flip a change to 100% of traffic at once. Ring it
  out to a small percentage, watch signals, then widen. See
  [deployment strategies](07-deployment-strategies.md).
- **A change record is the source of truth.** Every production change is traceable to
  a commit, an author, an approver (if any), and a timestamp — so that during an
  incident you can answer "what changed?" in seconds.

## Best Practices

- Decouple **deploy** from **release**: ship code dark behind a feature flag, then
  turn it on separately. This lets you roll back a *release* instantly without a
  redeploy, and turn features off under load.
- Classify changes by risk (standard / normal / emergency). Standard pre-approved
  changes auto-deploy; normal changes need review; emergency changes are allowed
  fast-track but require a retroactive record.
- Require the rollback method to be stated in the change/PR, and verify it actually
  works — test the rollback in staging, not just the roll-forward.
- Track the four DORA metrics (deploy frequency, lead time, change-failure rate, time
  to restore). They tell you whether the process is healthy without needing opinions.
- Freeze changes during known-risky windows (peak traffic, on-call gaps), but keep an
  explicit emergency path — a freeze must never block an incident fix.
- Announce production changes to a shared channel automatically so responders can
  correlate a change with an alert.

## Examples

**Good Example** — deploy decoupled from release, instant rollback

```yaml
# Ship the code inactive, then release by flipping a flag — not a redeploy.
deploy:
  strategy: canary          # 5% of traffic first, watch error rate + latency
  healthcheck: /healthz
  rollback: automatic        # abort + revert if canary SLO breaches
release:
  feature_flag: new_checkout_flow
  default: false             # code is live but OFF; turn on gradually
  # WHY: a bad release is undone by toggling the flag in seconds,
  # with no rebuild, no redeploy, no rollback window.
```

**Bad Example** — big-bang manual deploy with no way back

```bash
# Friday 5pm: merge a week of batched changes and push everything at once.
git merge release-candidate
ssh prod "cd /app && git pull && systemctl restart app"
# WHY THIS IS WRONG:
#  - No canary: 100% of users hit untested code simultaneously.
#  - Batched: if it breaks, you cannot tell which of 40 changes did it.
#  - No rollback: `git pull` moved forward; reverting means another manual push
#    while the site is down. Restart drops in-flight requests.
```

## Common Mistakes

- Batching many changes into a rare "big release" instead of shipping continuously.
- Treating a merged PR as "done" with no defined, tested rollback path.
- Requiring human approval for every change, which trains people to bypass the process.
- Deploying to 100% of traffic in one step with no canary or progressive rollout.
- A change freeze with no emergency exception, so the freeze itself blocks incident fixes.
- No change log, so during an incident nobody can answer "what just changed?".

## Production Tips

- Post deploys to the same channel as alerts, with commit SHA and author, so an alert
  and its likely cause sit next to each other.
- Keep the last known-good artifact immediately deployable; rollback should be one
  command or one button, not a rebuild.
- Measure change-failure rate per team and treat a rising trend as a signal to slow
  down and add gates, not to blame individuals.

## AI Review Checklist

- Does the change ship in a small, independently revertible unit?
- Is the rollback method explicitly stated and tested, not assumed?
- Is deploy decoupled from release (flag/canary) so exposure is progressive?
- Do only genuinely risky changes require human approval; do routine ones auto-flow?
- Is every production change recorded (SHA, author, time) and announced automatically?
- Is there an emergency path that is never blocked by a change freeze?

## Related

- `knowledge/devops/06-release-management.md`
- `knowledge/devops/07-deployment-strategies.md`
- `knowledge/devops/23-quality-gates.md`
- `knowledge/devops/25-incident-management.md`
- `knowledge/devops/26-postmortems.md`
