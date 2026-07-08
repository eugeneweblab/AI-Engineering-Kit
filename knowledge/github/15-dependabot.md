---
id: github/15-dependabot
topic: github
slug: dependabot
title: "Dependabot"
type: doc
order: 15
status: ready
tags: [github, dependabot]
related: [github/13-security, github/14-codeql, github/09-workflows, github/06-pull-requests, github/17-branch-protection]
when_to_use: "Read before configuring dependency updates or triaging a vulnerable-dependency alert."
---
# Dependabot

## Purpose

This document defines how to use **Dependabot** to keep dependencies patched and to
respond to vulnerable-dependency alerts. It covers the three distinct features people
conflate — **alerts** (notify on a known-vulnerable dependency), **security updates**
(auto-PR the fix), and **version updates** (routine dependency bumps via
`dependabot.yml`) — plus how to configure, group, and safely merge the resulting PRs.

Dependabot secures your **dependency tree**. It complements [CodeQL](14-codeql.md) (your
own code) and [secret scanning](16-secret-scanning.md) (leaked credentials). Enabling all
three is the baseline "supply chain + code + secrets" posture from the
[security hub](13-security.md).

## Why It Matters

Most of a modern application is third-party code, and vulnerabilities in it (Log4Shell,
event-stream, countless prototype-pollution and ReDoS issues) are disclosed constantly. An
unpatched transitive dependency is an open door that has nothing to do with your code
quality. The failure mode is **drift**: dependencies silently age until a bump is a scary
multi-major migration nobody wants to do during an incident. Small, continuous, automated
updates keep the tree patchable and turn a security response into a one-line diff.

## Core Principles

- **Enable alerts and security updates on every repo — they are free and high-signal.**
  A vulnerable dependency you don't know about is worse than one you're patching.
- **Automate the churn, gate the merge.** Auto-open update PRs, but require CI to pass
  before they merge. Never auto-merge across a major version.
- **Group updates to fight PR fatigue.** Ungrouped, Dependabot floods the repo with dozens
  of PRs a week and the team stops looking — which defeats the purpose.
- **A CI-green patch/minor update is low-risk; a major is a migration.** Treat them
  differently: auto-merge the former, human-review the latter.
- **Dependabot PRs run with your secrets — protect them.** Dependabot has a restricted
  token context by design; do not weaken it to hand these PRs production credentials.

## Best Practices

- Turn on Dependabot alerts, security updates, and the dependency graph at the org level so
  new repos inherit them.
- Add a `.github/dependabot.yml` for **version updates** on each ecosystem (npm, pip,
  Docker, `github-actions`, ...). Include `github-actions` so your pinned Action SHAs stay
  current.
- **Group** minor and patch updates into one PR per ecosystem to keep the volume sane.
- Auto-merge only patch/minor updates and only after required checks pass; require a human
  for `version-update:semver-major`.
- Keep the dependency count and update cadence modest (`open-pull-requests-limit`) so the
  queue stays reviewable.
- Make CI (tests + [CodeQL](14-codeql.md)) a required check so no update — automated or
  not — merges red.

## Examples

**Good Example** — grouped updates, Actions ecosystem included

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: npm
    directory: "/"
    schedule: { interval: weekly }
    open-pull-requests-limit: 5      # cap the queue so it stays reviewable
    groups:
      minor-and-patch:               # one PR instead of dozens → the team actually reviews
        update-types: [minor, patch]
  - package-ecosystem: github-actions  # keeps pinned Action SHAs patched
    directory: "/"
    schedule: { interval: weekly }
```

**Bad Example** — auto-merge everything, no gate

```yaml
# workflow that blindly merges every Dependabot PR, including breaking majors
on: pull_request_target        # runs with elevated context on untrusted PR content
jobs:
  merge:
    runs-on: ubuntu-latest
    steps:
      - run: gh pr merge --auto --merge "$PR_URL"
        # no check that CI passed, no filter on semver-major → a breaking bump
        # can auto-merge straight to main and take down production
```

## Common Mistakes

- Auto-merging major-version updates, letting breaking changes land unreviewed.
- No grouping, so a flood of PRs trains the team to ignore Dependabot entirely.
- Using `pull_request_target` carelessly to auto-merge, exposing secrets to untrusted PRs.
- Enabling alerts but never acting on them — the alert is only useful if it drives a patch.
- Forgetting the `github-actions` ecosystem, so pinned Action SHAs silently go stale.
- Merging an update without required CI, shipping a regression the bump introduced.

## Production Tips

- Route Dependabot alerts to the security overview and set an SLA by severity (critical
  first). Unrouted alerts accumulate unseen.
- Use `dependabot.yml` `ignore` sparingly and with a comment — a permanently ignored CVE
  is a decision that needs an owner and a review date.
- For monorepos, configure per-directory ecosystems so each package updates independently.
- Combine with a lockfile and reproducible install (`npm ci`, `pip install -r`) so a
  Dependabot bump is deterministic in CI.

## AI Review Checklist

- Are Dependabot alerts and security updates enabled on the repo?
- Does `dependabot.yml` cover every ecosystem, including `github-actions`?
- Are minor/patch updates grouped to keep PR volume reviewable?
- Is auto-merge restricted to CI-green patch/minor updates, with humans on majors?
- Are auto-merge workflows free of unsafe `pull_request_target` secret exposure?
- Is CI a required check so no update merges red?

## Related

- `knowledge/github/13-security.md`
- `knowledge/github/14-codeql.md`
- `knowledge/github/09-workflows.md`
- `knowledge/github/06-pull-requests.md`
- `knowledge/github/17-branch-protection.md`
