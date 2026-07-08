---
id: github/30-engineering-principles
topic: github
slug: engineering-principles
title: "Engineering Principles"
type: doc
order: 30
status: ready
tags: [github, engineering-principles]
related: [github/17-branch-protection, github/06-pull-requests, github/08-actions, github/27-best-practices, github/13-security]
when_to_use: "Read before designing a team's GitHub workflow, branch model, or CI/CD conventions."
---
# Engineering Principles

## Purpose

This document defines the durable principles for using GitHub as an engineering
platform: how to structure branches and pull requests, how to make CI the arbiter of
correctness, and how to encode process as configuration rather than tribal knowledge.
It is written so an agent can set up or review a repository's workflow without creating
the slow, fragile, or insecure patterns that plague real teams.

GitHub is not just a place to store code — it is where change is proposed, reviewed,
gated, and shipped. The principles here decide whether that pipeline is trustworthy.

## Why It Matters

The repository is the single source of truth for what runs in production. If `main` can
be broken, if a merge can bypass review, or if a workflow can leak a secret, the failure
is not local — it ships to every consumer of that code. Unlike an application bug that
affects one request, a broken delivery pipeline affects every change that follows it.
These failures are also easy to introduce and hard to notice: a green checkmark on an
unprotected branch looks identical to one on a protected branch. Because the blast radius
is the whole team's velocity and the whole product's integrity, repository engineering is
held to a higher bar than the code inside it.

## Core Principles

- **`main` is always releasable.** Every commit on the default branch must build, pass
  tests, and be deployable. Enforce this with branch protection, not with hope.
- **All change flows through pull requests.** Direct pushes to protected branches are
  disabled. The PR is the unit of review, CI, and audit — nothing bypasses it.
- **CI is the source of truth, not opinion.** If a check can be skipped or is advisory,
  it will eventually be ignored. Make required checks *required*, and keep them fast
  enough that people wait for them.
- **Process is configuration, not convention.** Rulesets, `CODEOWNERS`, workflow files,
  and templates live in the repo and are versioned. A rule that only exists in a wiki
  or a person's memory does not exist.
- **Least privilege by default.** Tokens, Actions permissions, and team access grant the
  minimum needed. Default-broad access is a standing liability, not a convenience.
- **Small, reversible changes.** Prefer many small PRs over one large one. Small changes
  review faster, break less, and revert cleanly — the cost of a mistake stays bounded.

## Best Practices

- Protect the default branch with a [ruleset](18-rulesets.md) or
  [branch protection](17-branch-protection.md): require PRs, required status checks,
  linear history, and signed commits where compliance demands it.
- Require review from code owners via a `CODEOWNERS` file so the right people are pulled
  in automatically; do not rely on authors to request the right reviewers.
- Keep the default `GITHUB_TOKEN` permissions read-only at the org or repo level and
  elevate per-job with an explicit `permissions:` block. The cost of broad tokens is a
  supply-chain foothold; the cost of scoped tokens is a few extra lines of YAML.
- Pin third-party [Actions](08-actions.md) to a full commit SHA, not a mutable tag like
  `@v4`. A tag can be moved to point at malicious code; a SHA cannot.
- Make required checks deterministic and fast. Flaky checks train people to hit re-run
  and merge anyway, which defeats the gate.
- Use [PR](06-pull-requests.md) and issue templates to make the required context
  (what changed, why, how tested) impossible to forget.
- Automate the mechanical parts — labeling, dependency updates via
  [Dependabot](15-dependabot.md), release notes — so humans review judgment, not chores.

## Examples

**Good Example** — least-privilege, SHA-pinned workflow that gates merges

```yaml
# .github/workflows/ci.yml
name: ci
on: pull_request            # runs on every PR, so it can be a required check
permissions:
  contents: read            # default-deny; grant only what this job needs
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      # Pinned to a commit SHA: a moved tag cannot swap in malicious code.
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
      - run: npm ci && npm test   # deterministic install + tests, the gate
```

**Bad Example** — broad token, mutable tag, and no gate

```yaml
name: ci
on: push                    # only runs after merge — cannot block a bad PR
permissions: write-all      # hands every job full write access to the repo
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@main   # mutable ref: today's code, tomorrow's surprise
      - run: npm install && npm test  # non-deterministic install; flaky by design
```

## Common Mistakes

- Allowing direct pushes or admin-bypass on `main`, so review and CI are optional.
- Making checks "informational" instead of required, so red builds get merged.
- Using `write-all` or `pull-requests: write` on jobs that only read code.
- Referencing Actions by mutable tag (`@v4`, `@main`) instead of a pinned SHA.
- Rules that live in a wiki or Slack instead of `CODEOWNERS`, rulesets, and templates.
- One giant PR that no one can review carefully and no one can revert cleanly.

## Production Tips

- Turn on required signed commits and linear history for repos under compliance scope;
  audit the ruleset, not each PR.
- Use environments with required reviewers and secrets scoped per environment so a
  staging deploy can never read production credentials.
- Enable branch protection *and* org-level rulesets — rulesets apply across many repos
  and are far easier to audit than per-repo settings.

## AI Review Checklist

- Is the default branch protected, with PRs and required status checks enforced for
  everyone, including admins?
- Do workflows set `permissions:` explicitly, defaulting to `contents: read`?
- Are all third-party Actions pinned to a full commit SHA?
- Is there a `CODEOWNERS` file that routes reviews to the right owners?
- Are required checks deterministic and fast enough to be trusted?
- Is repository process encoded as versioned config, not documented as convention?

## Related

- `knowledge/github/17-branch-protection.md`
- `knowledge/github/06-pull-requests.md`
- `knowledge/github/08-actions.md`
- `knowledge/github/27-best-practices.md`
- `knowledge/github/13-security.md`
