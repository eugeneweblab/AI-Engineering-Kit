---
id: devops/03-git-workflow
topic: devops
slug: git-workflow
title: "Git Workflow"
type: doc
order: 3
status: ready
tags: [devops, git-workflow]
related: [devops/04-branching-strategies, devops/02-development-lifecycle, devops/05-build-pipelines, devops/23-quality-gates, devops/00-overview]
when_to_use: "Read before committing, opening a pull request, rewriting history, or reviewing someone else's Git changes."
---
# Git Workflow

## Purpose

This document defines how an agent should use Git day to day: how to commit, structure a
pull request, keep history readable, and rewrite it safely. It covers the *mechanics* of
working with source control. How teams organize integration (trunk-based, release
branches) belongs to [04 Branching Strategies](04-branching-strategies.md); this doc is
about the commits and pull requests themselves.

## Why It Matters

Git history is the project's audit log and its debugging tool. When production breaks, a
clean history lets you `git bisect` to the exact commit, `git revert` it cleanly, and read
*why* it was made. A history of giant "wip" commits mixing ten unrelated changes makes
every one of those operations useless. History is written once and read hundreds of times;
the small discipline of a good commit pays back every time someone has to understand or
undo the change.

## Core Principles

- **Atomic commits.** One commit = one logical change that builds and passes tests on its
  own. This is what makes `revert`, `bisect`, and `cherry-pick` work.
- **Explain *why*, not *what*.** The diff already shows what changed. The commit message
  exists to record the reasoning a future reader cannot reconstruct.
- **Never rewrite shared history.** Rebasing or force-pushing a branch others have pulled
  destroys their work and breaks the shared record. Rewrite only your own unpushed or
  unshared commits.
- **Never commit secrets or generated artifacts.** Credentials, tokens, build output, and
  dependencies do not belong in the repo. A leaked secret in history is compromised even
  after you delete it.
- **The remote default branch is protected.** No direct pushes; changes land through
  reviewed pull requests that pass CI.

## Best Practices

- Write commit subjects in the imperative mood, ≤ 50 chars, with a body explaining the
  reasoning and any trade-offs. Follow [Conventional Commits](https://www.conventionalcommits.org)
  (`feat:`, `fix:`, `refactor:`) so tooling can derive changelogs and version bumps.
- Keep pull requests small and single-purpose — a reviewer can meaningfully review ~400
  lines, not 4,000. Large PRs get rubber-stamped, which defeats review.
- Rebase your *local* feature branch onto the latest default branch before opening a PR to
  keep history linear and surface conflicts early. Do not rebase a branch others share.
- Use `.gitignore` for build output, dependencies, and local env files; use a secrets
  manager for credentials. See [17 Secrets Management](17-secrets-management.md).
- Require CI to pass and at least one approving review before merge; enforce it with
  branch protection, not convention.

## Examples

**Good Example** — atomic commit, message explains the why

```text
fix(auth): reject tokens missing an `exp` claim

Tokens without an expiry never expire, so a leaked one is valid forever.
We now treat a missing `exp` as invalid rather than "no expiry". This is a
deliberate breaking change for any client relying on non-expiring tokens.

Refs: SEC-482
# Subject is imperative and scoped; body records WHY and the trade-off,
# which the diff alone cannot convey.
```

**Bad Example** — mixed, unexplained, history-rewriting

```bash
git add -A
git commit -m "fixes"          # bundles auth fix + refactor + a new secret in .env
git push --force origin main   # rewrites SHARED history on the protected branch
# "fixes" tells a future reader nothing; the mixed commit can't be reverted
# cleanly; the force-push destroys the shared record and breaks everyone's clone.
```

## Common Mistakes

- Committing secrets or `.env` files — they remain in history after deletion and must be
  treated as leaked (rotate the credential).
- Force-pushing a shared branch, discarding teammates' commits.
- Giant, multi-purpose PRs that reviewers cannot actually review.
- Commit messages like "fix", "wip", or "updates" that carry zero reasoning.
- Committing generated files (`node_modules/`, `dist/`) that bloat the repo and cause
  spurious merge conflicts.

## Production Tips

- Run a secret scanner (e.g. gitleaks) as a pre-commit hook and in CI so credentials are
  caught before they ever reach the remote.
- Sign commits/tags (GPG or Sigstore) where provenance matters, so you can prove who
  authored a change.
- Use `git revert` (not `reset`) to undo a change on a shared branch — it preserves history
  and creates an auditable "undo" commit.

## AI Review Checklist

- Is each commit atomic — one logical change that builds and passes tests alone?
- Does the commit message explain *why*, and does it follow Conventional Commits?
- Is the PR small and single-purpose enough to review meaningfully?
- Are there any secrets, credentials, or generated artifacts in the diff or history?
- Does the change avoid rewriting shared/protected-branch history?
- Do branch-protection rules require passing CI and review before merge?

## Related

- `knowledge/devops/04-branching-strategies.md`
- `knowledge/devops/02-development-lifecycle.md`
- `knowledge/devops/05-build-pipelines.md`
- `knowledge/devops/23-quality-gates.md`
- `knowledge/devops/00-overview.md`
