---
id: git/27-best-practices
topic: git
slug: best-practices
title: "Best Practices"
type: doc
order: 27
status: ready
tags: [git, best-practices]
related: [git/04-commits, git/05-branches, git/07-rebasing, git/23-trunk-based-development, git/28-security]
when_to_use: "Read before establishing or reviewing a team's day-to-day Git workflow and commit conventions."
---
# Best Practices

## Purpose

This document defines the day-to-day habits that keep a Git history clean, reviewable, and
recoverable: how to commit, how to branch, how to write messages, and what never to push.
It is written so an agent can produce work that reads well in history and merges without
friction.

These are workflow rules, not Git mechanics. The mechanics live in
[commits](04-commits.md), [branches](05-branches.md), and [rebasing](07-rebasing.md); this
document is about *how to use them well* so history stays an asset instead of a liability.

## Why It Matters

Git history is read far more often than it is written — during code review, incident
response, [bisect](26-debugging.md), and onboarding. A history of small, well-described
commits lets a reader reconstruct *why* the code is the way it is; a history of "wip", "fix
fix", and 3,000-line dumps is opaque, and the reasoning is lost forever. Good habits also
prevent expensive accidents: pushing secrets, force-pushing shared branches, and merging
untested code all cost far more to undo than to avoid. The commit is the atomic unit of
review and rollback — its quality sets a ceiling on both.

## Core Principles

- **One logical change per commit.** A commit should do one thing and be revertable on its
  own. This is what makes [revert](10-revert.md) and [bisect](26-debugging.md) work.
- **Commit messages explain *why*, not *what*.** The diff already shows what changed; the
  message must capture intent and context the code cannot.
- **Rewrite local history, never shared history.** Clean up your own branch before review;
  never [rebase](07-rebasing.md) or force-push a branch others build on.
- **Keep the default branch always releasable.** Merge only reviewed, tested code;
  gate with CI. Prefer short-lived branches ([trunk-based](23-trunk-based-development.md)).
- **Never commit what should not be versioned.** Secrets, build output, and machine-local
  config stay out via `.gitignore` — some of it is irreversible if pushed.

## Best Practices

- Write commit subjects in the imperative mood, under ~50 characters
  (`Add retry to payment client`), then a blank line and a body explaining *why*.
- Adopt [Conventional Commits](04-commits.md) (`feat:`, `fix:`, `chore:`) if you automate
  changelogs or releases — the trade-off is a small format discipline for free tooling.
- Stage deliberately with `git add -p` so each commit is exactly the intended change, not
  whatever happened to be in the working tree.
- Rebase your feature branch onto the latest trunk before opening a PR to get a clean,
  linear diff; do this only while the branch is private.
- Keep pull requests small (a few hundred lines). Small PRs get real review; large ones get
  rubber-stamped. The cost is more PRs; the benefit is real scrutiny.
- Maintain a committed `.gitignore` (and consider a global one for editor/OS files) so
  junk never reaches a commit in the first place.
- Pull with `--rebase` (`git config pull.rebase true`) to avoid noisy merge commits on your
  own branch.

## Examples

**Good Example** — a focused commit with a message that explains why

```bash
git add -p                        # stage only the retry logic, not unrelated edits
git commit -m "fix: retry payment webhook on 5xx

The provider returns transient 503s during deploys, dropping ~2% of
webhooks. Retry with backoff up to 3 times so we stop losing events.
Closes #482."
# One logical change, imperative subject, body answers WHY, references the issue.
```

**Bad Example** — a dumping-ground commit on a shared branch

```bash
git add -A                        # sweeps in build output, .env, and unrelated work
git commit -m "stuff"             # tells a future reader nothing

git push --force origin main      # rewrites history others depend on -> broken clones
# The commit can't be cleanly reverted or bisected, leaked .env, and the force-push
# corrupted everyone else's view of main.
```

## Common Mistakes

- Giant commits mixing unrelated changes, so revert and bisect become useless.
- Messages like "fix", "wip", or "update" that record no intent.
- Force-pushing or rebasing a shared branch, breaking everyone else's history.
- Committing `.env`, credentials, or build artifacts because `.gitignore` was incomplete.
- Merging directly to the default branch without review or passing CI.
- Long-lived branches that drift for weeks and produce unmergeable conflicts.

## Production Tips

- Enforce message format and secret scanning with a [pre-commit hook](20-hooks.md); enforce
  the same server-side so local bypass (`--no-verify`) cannot slip past.
- Protect the default branch: require PRs, passing status checks, and disallow force-push.
- Use `CODEOWNERS` so the right reviewers are requested automatically.
- Squash-merge noisy feature branches so trunk history stays one meaningful commit per
  change, while the branch keeps its detail.

## AI Review Checklist

- Does each commit represent one logical, independently revertable change?
- Does the message explain *why*, with an imperative subject line?
- Is the branch short-lived and rebased/merged cleanly onto current trunk?
- Are secrets, build output, and local config excluded via `.gitignore`?
- Was history rewriting confined to private branches (no shared force-push)?
- Did the change go through review and CI before reaching the default branch?
- Is the PR small enough to be genuinely reviewable?

## Related

- `knowledge/git/04-commits.md`
- `knowledge/git/05-branches.md`
- `knowledge/git/07-rebasing.md`
- `knowledge/git/23-trunk-based-development.md`
- `knowledge/git/28-security.md`
