---
id: github/27-best-practices
topic: github
slug: best-practices
title: "Best Practices"
type: doc
order: 27
status: ready
tags: [github, best-practices]
related: [github/17-branch-protection, github/07-code-review, github/13-security, github/08-actions, github/30-engineering-principles]
when_to_use: "Read when setting up a new repository or auditing an existing one against GitHub hygiene standards."
---
# Best Practices

## Purpose

This document is the synthesis layer: the repository-level practices that make a GitHub
project safe, reviewable, and reproducible. It ties together branch protection, PR flow,
ownership, commit hygiene, and least privilege into a checklist of habits. It does not
re-teach each subsystem in depth — it points to the focused docs — but it defines the
*defaults every repo should have on day one*.

Most GitHub incidents are not exotic; they are a missing required review, an unprotected
`main`, a leaked secret, or a token with too much scope. The practices here close those gaps
before they cost you.

## Why It Matters

A repository is shared, long-lived infrastructure. Defaults are permissive: a fresh repo lets
anyone with write access push straight to `main`, force-push over history, and merge their own
unreviewed code. Every one of those is a way to ship a bug or a compromise that no second
person saw. The practices below cost minutes to configure and then run automatically forever —
the alternative is relying on every contributor to be careful every time, which does not scale
and does not survive a bad day.

## Core Principles

- **Protect the default branch; never commit to it directly.** Require PRs, at least one
  review, and passing checks before merge. The cost is a slightly slower path to `main`; the
  benefit is nothing reaches production unseen. See [branch-protection](17-branch-protection.md).
- **Small, focused PRs.** A change that does one thing is reviewable; a 2,000-line PR is
  rubber-stamped. Reviewers catch bugs in proportion to how well they can read the diff.
- **Least privilege everywhere.** People get the minimum org/repo role, tokens get the minimum
  scope, and Actions get the minimum permissions. Access you did not grant cannot be abused.
- **Automate the gates.** Encode standards as required status checks, rulesets, and CODEOWNERS
  so they are enforced by the platform, not by reviewer memory.
- **Make the repo reproducible and legible.** A README that says how to build/test/run, a
  lockfile, a `.gitignore`, a LICENSE, and clear commit messages let the next person (or agent)
  work without archaeology.

## Best Practices

- Turn on branch protection (or a **ruleset**) for `main`: require PRs, ≥1 approving review,
  passing status checks, up-to-date branches, and dismiss stale approvals on new commits.
- Add a **CODEOWNERS** file so the right people are auto-requested and their review is required
  for their areas.
- Keep PRs small and single-purpose; write a clear title and description saying *what* and *why*.
- Adopt a commit convention (e.g., Conventional Commits) so history is scannable and releases
  can be automated.
- Require **signed commits** on protected branches for provenance where it matters.
- Never commit secrets; enable [secret-scanning](16-secret-scanning.md) with push protection,
  [Dependabot](15-dependabot.md), and [CodeQL](14-codeql.md) so security is on by default.
- Pin third-party [actions](08-actions.md) to commit SHAs and set least-privilege workflow
  `permissions`.
- Include a README, LICENSE, `.gitignore`, CONTRIBUTING, and issue/PR templates so contribution
  is self-service.
- Prefer **squash merge** with a clean message for a linear, bisectable history; delete merged
  branches automatically.

## Examples

**Good Example** — CODEOWNERS scoping required review by area

```gitignore
# CODEOWNERS — a matching path REQUIRES that owner's review before merge (with branch protection).
*                     @acme/maintainers      # fallback owner for anything unmatched
/infra/               @acme/platform          # infra changes need platform team
/services/payments/   @acme/payments @acme/security  # money touches security too
```

**Bad Example** — unprotected repo, everything to one giant PR

```bash
# No branch protection, so this ships to production with zero review:
git checkout main
git commit -am "big refactor + new feature + secret config"   # 40 files, unrelated changes
git push origin main            # straight to main; no PR, no checks, no second pair of eyes
# .env with live credentials was staged too — no secret scanning to stop it.
```

## Common Mistakes

- Leaving `main` unprotected so anyone can push or force-push over history.
- Approving your own PR, or merging with failing/again-changed checks after approval.
- Giant, multi-purpose PRs that reviewers cannot meaningfully read.
- Granting everyone `admin`/`maintain` when `write` or `triage` would do.
- Committing secrets and `.env` files because push protection and `.gitignore` were absent.
- Using mutable action tags and `write-all` workflow permissions.
- No README/build instructions, so the repo is only usable by the person who wrote it.

## Production Tips

- Set org-level **default** branch protections / rulesets and required security features so new
  repos are safe without per-repo setup. See [enterprise](28-enterprise.md).
- Use repository or org **templates** so new projects start with the README, license, CI, and
  CODEOWNERS already in place.
- Periodically audit access: remove stale collaborators, downgrade over-broad roles, and rotate
  or expire long-lived tokens.
- Track the merge queue and required-check health; a check that is "required" but flaky trains
  people to bypass it.

## AI Review Checklist

- Is the default branch protected with required PRs, reviews, and status checks?
- Does a CODEOWNERS file route review to the right owners for sensitive paths?
- Are PRs small and single-purpose with a clear what/why description?
- Are secret scanning (push protection), Dependabot, and code scanning enabled?
- Are third-party actions SHA-pinned with least-privilege workflow permissions?
- Are collaborator roles and token scopes least-privilege, with no self-approval on merges?
- Does the repo have a README, LICENSE, `.gitignore`, and contribution templates?

## Related

- `knowledge/github/17-branch-protection.md`
- `knowledge/github/07-code-review.md`
- `knowledge/github/13-security.md`
- `knowledge/github/08-actions.md`
- `knowledge/github/30-engineering-principles.md`
