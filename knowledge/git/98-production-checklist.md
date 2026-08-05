---
id: git/98-production-checklist
topic: git
slug: production-checklist
title: "Git Production Checklist"
type: doc
order: 98
status: ready
tags: [git, production-checklist, vMAJOR.MINOR.PATCH, README, user.email, pre-commit]
related: [git/12-tags, git/16-push, git/20-hooks, git/28-security, git/27-best-practices]
when_to_use: "Read before cutting a release, setting up branch protection, or hardening a repository for a team."
---
# Git Production Checklist

## Purpose

This is the pass/fail gate for a git repository that real teams and CI/CD systems depend
on. Each item is a verifiable yes/no fact you can confirm by running a command or reading
a setting — not a suggestion. Work top to bottom before you call a repository
"production-grade," and re-run the release section on every tag.

## Why It Matters

A repository is production infrastructure: it feeds CI, triggers deploys, and is the
audit trail when something breaks. A missing branch protection, a committed secret, or an
untagged release is not a style problem — it is an outage or a breach waiting for a
trigger. These checks are cheap to verify and expensive to skip, so treat an unchecked box
as a blocker, not a nice-to-have.

## Repository Hygiene

**Rules:** [Repository](03-repository.md) · [Best Practices](27-best-practices.md)

- [ ] A `.gitignore` exists and excludes build output, dependencies, editor files, and
  local env files (verify: `git status --ignored` shows them ignored, not tracked).
- [ ] No secrets, keys, or `.env` files are tracked (`git ls-files | grep -Ei 'secret|\.env|\.pem|credential'` returns nothing).
- [ ] Large binaries are handled by [Git LFS](25-lfs.md), not committed raw (`git lfs ls-files` lists them).
- [ ] The default branch is named and set consistently (e.g. `main`) across the repo and CI config.
- [ ] `.gitattributes` normalizes line endings (`* text=auto`) so cross-OS diffs stay clean.
- [ ] A `README` and license are present at the repo root.

## Branch Protection & Access

**Rules:** [Branches](05-branches.md) · [Trunk Based Development](23-trunk-based-development.md)

- [ ] The default branch is protected: no direct pushes, no force-pushes, no deletion.
- [ ] Merging requires a passing CI status check and at least one approving review.
- [ ] Linear history (or a chosen squash/rebase-merge strategy) is enforced by the platform.
- [ ] Stale approvals are dismissed when new commits are pushed to a PR.
- [ ] Repository access follows least privilege; no shared personal accounts.

## Commit & History Integrity

**Rules:** [Commits](04-commits.md) · [History](18-history.md)

- [ ] Signed commits/tags are required for release branches (`git log --show-signature` verifies).
- [ ] Author identity is correct (`git config user.name` / `user.email` set per repo, not a placeholder).
- [ ] History is free of merge bubbles from routine syncs (feature branches rebased before merge).
- [ ] No committed secret exists anywhere in history (a scanner such as gitleaks/trufflehog passes).

## Release & Tagging

**Rules:** [Tags](12-tags.md) · [Flow](22-git-flow.md)

- [ ] Every release is marked with an **annotated** tag (`git tag -a vX.Y.Z`), not lightweight.
- [ ] Tags follow a documented scheme (e.g. SemVer `vMAJOR.MINOR.PATCH`) and are immutable once pushed.
- [ ] Tags are pushed to the remote explicitly (`git push origin vX.Y.Z`, or `git push --follow-tags`; never bulk `--tags`) and visible in the platform's releases.
- [ ] The tagged commit builds and passes the full test suite in CI before the tag is published.
- [ ] A changelog or release notes map each tag to its user-facing changes.

## Automation & Hooks

**Rules:** [Hooks](20-hooks.md) · [Tooling](29-tooling.md)

- [ ] A `pre-commit` or CI step runs secret scanning and lint before code lands.
- [ ] Server-side protections (not just local hooks) enforce the rules — local hooks are advisory only.
- [ ] CI checks out the exact commit SHA (not a floating branch) so builds are reproducible.
- [ ] Deploy pipelines pin to a tag or SHA, never to `latest` or a moving branch.

## Recovery & Safety

**Rules:** [Reflog](19-reflog.md) · [Revert](10-revert.md)

- [ ] The remote is not the only copy; the hosting platform's backups/retention are confirmed.
- [ ] The team knows [reflog](19-reflog.md) recovery exists before anyone force-pushes.
- [ ] Force-push, if ever allowed, is restricted to non-default branches and audited.

## AI Review Checklist

- Is the default branch protected against direct and force pushes?
- Does merging require passing CI and review?
- Are all secrets absent from both the working tree and full history?
- Are releases marked with signed, annotated, immutable SemVer tags?
- Do deploys pin to a tag or SHA rather than a moving branch?
- Are protections enforced server-side, not just by local hooks?

## Related

- `knowledge/git/12-tags.md`
- `knowledge/git/16-push.md`
- `knowledge/git/20-hooks.md`
- `knowledge/git/28-security.md`
- `knowledge/git/27-best-practices.md`
