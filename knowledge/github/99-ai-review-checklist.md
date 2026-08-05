---
id: github/99-ai-review-checklist
topic: github
slug: ai-review-checklist
title: "GitHub AI Review Checklist"
type: checklist
order: 99
status: ready
tags: [github, ai-review-checklist, "run:", pull_request_target, CODEOWNERS, "permissions:"]
related: [github/06-pull-requests, github/07-code-review, github/08-actions, github/17-branch-protection, github/100-common-antipatterns]
when_to_use: "Read before an AI agent reviews a pull request or repository configuration change on GitHub."
---
# GitHub AI Review Checklist

## Purpose

This is the checklist an AI agent runs when reviewing a GitHub pull request or a change
to repository configuration. It focuses on what an automated reviewer can verify from the
diff, the workflow files, and the repo settings — correctness, safety, and process
integrity — not subjective style. Each item is a yes/no question with a clear failure
mode.

## Why It Matters

An AI reviewer sees every PR, which makes it the ideal place to catch the systematic
mistakes humans wave through under time pressure: an Action bumped to a mutable tag, a
secret pasted into a workflow, a `permissions: write-all` slipped into CI. These are
low-visibility, high-impact changes. A consistent checklist turns the review from "looks
fine" into "verified against known failure modes."

## Pull Request Scope & Intent

**Rules:** [Pull Requests](06-pull-requests.md) · [Code Review](07-code-review.md)

- [ ] Does the PR do one thing? Unrelated changes should be split so each can be reviewed
      and reverted independently.
- [ ] Does the description state what changed, why, and how it was tested?
- [ ] Are generated files, lockfile churn, and formatting-only noise separated from
      logic changes so the real diff is reviewable?
- [ ] Does the PR target the correct base branch?

## Workflow & Actions Changes

**Rules:** [Actions](08-actions.md) · [Workflows](09-workflows.md)

- [ ] Are any newly added or modified [Actions](08-actions.md) pinned to a full commit
      SHA rather than a mutable tag (`@v4`, `@main`)?
- [ ] Does every workflow set `permissions:` explicitly and default to `contents: read`?
- [ ] Does the change avoid `pull_request_target` with checkout of untrusted PR code
      (a classic secret-exfiltration vector)?
- [ ] Are workflow inputs and PR-controlled values quoted/escaped, not interpolated
      directly into `run:` shell steps (script injection)?
- [ ] Do jobs that touch production use a protected environment with required reviewers?

## Secrets & Sensitive Data

**Rules:** [Secret Scanning](16-secret-scanning.md) · [Security](13-security.md)

- [ ] Does the diff introduce no hardcoded secrets, tokens, or credentials?
- [ ] Are secrets referenced via `secrets.*` / environment secrets, never echoed to logs?
- [ ] Does `.gitignore` still exclude `.env`, key files, and build artifacts?
- [ ] Are no internal hostnames, private URLs, or customer data added to public files?

## Repository Configuration Changes

**Rules:** [Branch Protection](17-branch-protection.md) · [Rulesets](18-rulesets.md)

- [ ] Does the change preserve [branch protection](17-branch-protection.md) and required
      checks — not weaken or bypass them?
- [ ] Does a `CODEOWNERS` edit still route ownership correctly and not orphan any path?
- [ ] Does a [permissions](21-permissions.md) or [teams](20-teams.md) change follow least
      privilege rather than granting broad admin?
- [ ] Are ruleset or protection edits accompanied by a stated reason?

## Correctness Signals

**Rules:** [CodeQL](14-codeql.md) · [Dependabot](15-dependabot.md)

- [ ] Do required status checks pass on this PR (tests, lint, build)?
- [ ] Does the change include or update tests for the behavior it modifies?
- [ ] Are new dependencies necessary, from a trusted source, and flagged by dependency
      review if vulnerable?
- [ ] Is the commit history clean enough to merge (no accidental merge commits, no
      committed conflict markers)?

## AI Review Checklist

- [ ] Are all modified Actions SHA-pinned and workflow tokens least-privilege?
- [ ] Does the diff contain zero hardcoded secrets and no untrusted-code execution path?
- [ ] Is branch protection and required-check enforcement preserved by this change?
- [ ] Is the PR single-purpose, tested, and passing required checks?
- [ ] Does any repo-config change follow least privilege with a documented rationale?

## Related

- `knowledge/github/06-pull-requests.md`
- `knowledge/github/07-code-review.md`
- `knowledge/github/08-actions.md`
- `knowledge/github/17-branch-protection.md`
- `knowledge/github/100-common-antipatterns.md`
