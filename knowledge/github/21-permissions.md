---
id: github/21-permissions
topic: github
slug: permissions
title: "GitHub Permissions"
type: doc
order: 21
status: ready
tags: [github, permissions, admin, write, triage, maintain, GITHUB_TOKEN, "permissions:"]
related: [github/19-organizations, github/20-teams, github/22-api, github/08-actions, github/13-security]
when_to_use: "Read before assigning repository roles, designing custom roles, or scoping tokens and Actions permissions."
---
# GitHub Permissions

## Purpose

This document defines how GitHub **permissions** are structured — repository roles, org
base permissions, custom roles, and token scopes — so an agent can grant exactly the
access a task needs and no more. It covers the precedence rules that decide what a user
or token can actually do when several grants overlap.

Permissions answer "what can this identity do to this resource?". They are the
[authorization](../security/04-authorization.md) layer for GitHub, sitting on top of the
[organization](19-organizations.md) and [team](20-teams.md) structure that decides who
holds them.

## Why It Matters

Over-granted access is the most common and most damaging GitHub misconfiguration. A
`GITHUB_TOKEN` with `write` when it needed `read` turns a compromised dependency into a
supply-chain attack; a repo role of `admin` when `write` sufficed lets someone disable
[branch protection](17-branch-protection.md). Permissions fail *open and silent*: the
task keeps working with too much power, and the excess is only discovered when it is
abused. Because the effective permission is the **union** of every grant, one forgotten
broad grant defeats a dozen careful ones.

## Core Principles

- **Least privilege, always.** Grant the lowest role or scope that completes the task.
  Escalate deliberately and temporarily, never "to be safe".
- **Permissions are additive; the widest grant wins.** Effective access is the union of
  org base permission, team grants, and direct grants. You cannot narrow access by
  layering a lower role on top of a higher one.
- **Roles are ordered.** `read < triage < write < maintain < admin`. Give `maintain`
  (manage repo without destructive settings) or `triage` (manage issues/PRs without
  push) instead of jumping to `admin`.
- **Tokens are identities too.** A PAT, GitHub App installation token, or `GITHUB_TOKEN`
  has its own scoped permissions — scope them as tightly as human roles.
- **Prefer fine-grained over classic.** Fine-grained PATs and GitHub App tokens grant
  per-repository, per-resource permissions; classic PATs grant broad, org-wide scopes.

## Best Practices

- Assign the **standard role** that matches the job: `triage` for issue/PR gardeners,
  `write` for contributors, `maintain` for repo leads, `admin` only for those who must
  change protection and settings. The cost of `admin`-by-default is silent bypass power.
- Define **custom repository roles** at the org level when the built-ins do not fit
  (e.g. write + manage-webhooks but not delete), instead of over-granting `admin`.
- Set the **`GITHUB_TOKEN` default to read-only** org-wide and elevate per workflow with
  an explicit `permissions:` block scoped to only what that job writes.
- Use **fine-grained PATs** or **GitHub App installation tokens** with per-repo selection
  and short expiry; never a classic `repo`-scoped PAT for automation.
- **Review the union**, not each grant in isolation: check org base permission first,
  since it silently raises everyone's floor.
- Make privileged grants **time-bound** and re-audited; standing `admin` is a liability.

## Examples

**Good Example** — scoped workflow token, least privilege

```yaml
# Workflow default is read-only (org policy); this job elevates ONLY what it writes.
permissions:
  contents: read          # clone the repo
  packages: write         # publish the built package — the one write it needs
  # everything else (issues, deployments, id-token, actions) stays 'none'

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ./scripts/publish.sh   # cannot touch issues, releases, or settings
```

**Bad Example** — blanket write, classic token

```yaml
permissions: write-all     # grants write to contents, issues, packages, deployments, ...
                           # a compromised step can now rewrite history or edit releases

# ...and the deploy step authenticates with a classic PAT that has full 'repo' + 'admin:org'
# scope across EVERY repository in the org — total blast radius if it leaks.
```

## Common Mistakes

- Granting `admin` because it "just works", handing out power to disable protection and
  delete the repo.
- Assuming a lower grant restricts a higher one — access is the union, so the broad grant
  still wins.
- Using `permissions: write-all` (or omitting `permissions:` when the org default is
  write) so every workflow step runs with maximal rights.
- Using classic, org-wide PATs for automation instead of fine-grained or App tokens.
- Ignoring the **org base permission**, which raises everyone's floor regardless of team
  design.
- Leaving privileged grants standing forever with no re-audit.

## Production Tips

- Generate an access report from the API periodically (`/repos/{o}/{r}/collaborators`
  with `affiliation` and `permission`) and diff it against expected roles.
- Alert on any new `admin` grant or any classic PAT creation via the audit log.
- Pin custom roles in code and reconcile them, so role definitions are reviewed like
  other infrastructure.

## AI Review Checklist

- Does each human hold the lowest role that fits (`triage`/`write`/`maintain` over `admin`)?
- Is the effective access reviewed as a *union*, including org base permission?
- Is the `GITHUB_TOKEN` read-only by default and elevated per job with a scoped block?
- Do automations use fine-grained PATs or App tokens, not classic org-wide PATs?
- Are custom roles used instead of over-granting `admin` for edge cases?
- Are privileged grants time-bound and periodically re-audited?

## Related

- `knowledge/github/19-organizations.md`
- `knowledge/github/20-teams.md`
- `knowledge/github/22-api.md`
- `knowledge/github/08-actions.md`
- `knowledge/github/13-security.md`
