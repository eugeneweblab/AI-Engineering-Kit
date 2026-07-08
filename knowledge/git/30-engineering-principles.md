---
id: git/30-engineering-principles
topic: git
slug: engineering-principles
title: "Engineering Principles"
type: doc
order: 30
status: ready
tags: [git, engineering-principles]
related: [git/04-commits, git/05-branches, git/07-rebasing, git/23-trunk-based-development, git/27-best-practices]
when_to_use: "Read before designing a team's git workflow or when deciding how to structure commits, branches, and history."
---
# Engineering Principles

## Purpose

This document defines the durable principles that govern how to *use* git well —
independent of any specific command. Commands like `rebase`, `reset`, and `merge` are
covered in their own docs; this doc explains the reasoning that decides *when* to reach
for them and *what a healthy history looks like*. An agent that internalizes these
principles will produce a repository that is auditable, bisectable, and safe to
collaborate on.

The mental model: **git is a content-addressed database whose value is a truthful,
navigable record of how the code reached its current state.** Every principle below
protects that record.

## Why It Matters

History is the one artifact every engineer trusts implicitly. When it is clean, you can
`git bisect` a regression in minutes, revert one feature without touching another, and
read a `git log` as a design document. When it is noisy — "wip", "fix", "fix again",
merge bubbles, unrelated changes crammed into one commit — every one of those tools
degrades, and the cost compounds forever because history is append-only. You cannot
retroactively make a bad history good on a shared branch without a force-push that
rewrites everyone's clone. The discipline is cheap at commit time and expensive to
recover later.

## Core Principles

- **A commit is the atomic unit of change, not a save point.** Each commit should build,
  pass tests, and represent exactly one logical change. This is what makes `revert` and
  `bisect` work.
- **History is communication.** The audience is a future engineer (often you) debugging
  at 2 a.m. Write the message that person needs: *why*, not *what* — the diff already
  shows what.
- **Rewrite freely in private, never in public.** Reshape your own local/feature history
  with rebase and amend until it is clean; once others have pulled a branch, its history
  is frozen. See [rebasing](07-rebasing.md).
- **Branch to isolate, integrate quickly.** Long-lived branches accumulate merge risk.
  Prefer short-lived branches merged often, per
  [trunk-based development](23-trunk-based-development.md).
- **The working tree, the index, and HEAD are three distinct states.** Most git confusion
  is losing track of which one you are acting on. Know before you run a command whether it
  touches staged, unstaged, or committed content.
- **Nothing committed is truly lost.** Reachable or not, objects survive in the
  [reflog](19-reflog.md) until garbage collection. Recovery is almost always possible —
  panic-force-pushing over a mistake is what causes real data loss.

## Best Practices

- Make **small, cohesive commits**. If a commit message needs the word "and", it is
  probably two commits. Small commits revert and cherry-pick cleanly.
- Write messages in the **imperative mood** with a concise subject (≤ 50 chars) and a body
  that explains motivation and trade-offs. `git commit` (no `-m`) forces you to slow down.
- **Rebase your feature branch onto the target before merging** to get a linear,
  reviewable history — but never rebase a branch others share.
- **Commit generated artifacts and secrets nowhere.** Use `.gitignore` for build output
  and a secrets manager for credentials; a leaked key in history is public forever.
- **Pull with `--rebase`** on feature work to avoid pointless merge commits from syncing.
- Use **`git add -p`** to stage in hunks so unrelated changes do not ride along in one
  commit.
- Tag releases with **annotated tags** (`git tag -a`) so the tag carries a message, date,
  and author; lightweight tags are just movable pointers.

## Examples

**Good Example** — one logical change, imperative subject, reasoned body

```bash
# Stage only the change that belongs to this commit, not the whole tree.
git add -p src/auth/session.ts

git commit
# Subject and body written in the editor:
#
#   Expire sessions after 30m idle to close fixation window
#
#   Sessions never timed out, so a stolen cookie stayed valid until logout.
#   Add an absolute + idle TTL checked on every request. Chosen over a
#   sliding-only window because sliding alone never bounds a hijacked session.
```

**Bad Example** — grab-bag commit that breaks bisect and revert

```bash
git add -A                       # sweeps in unrelated formatting + a debug print
git commit -m "fixes"            # non-actionable subject, no reasoning
# This commit mixes an auth fix, a lint reformat, and a stray console.log.
# git bisect will point here and tell you nothing; you cannot revert the auth
# fix without also reverting the reformat. One "logical change" is now three.
```

## Common Mistakes

- Treating commits as timed backups ("wip", "eod") instead of logical units.
- Rewriting shared history with `rebase`/`--force`, forcing teammates to reconcile clones.
- Committing build output, `node_modules`, or secrets instead of ignoring them.
- Force-pushing to recover from a mistake before checking the [reflog](19-reflog.md).
- Letting a feature branch live for weeks, guaranteeing a painful integration merge.
- Squashing everything into one commit, destroying the review-time reasoning trail.

## Production Tips

- Enforce these principles with mechanism, not memory: a `commit-msg` hook for message
  format, a `pre-commit` hook for secret scanning, and branch protection requiring linear
  history. See [hooks](20-hooks.md).
- Standardize on one integration model (rebase-and-merge or squash-and-merge) and encode
  it in the platform's merge-button default so history stays uniform.

## AI Review Checklist

- Does each commit represent exactly one logical, buildable change?
- Do messages explain *why* (motivation, trade-off), not just restate the diff?
- Was any shared branch's history rewritten or force-pushed?
- Are generated files, dependencies, and secrets kept out of the commit?
- Is the feature branch short-lived and rebased onto an up-to-date target?
- Is recovery attempted via reflog before any destructive command?

## Related

- `knowledge/git/04-commits.md`
- `knowledge/git/05-branches.md`
- `knowledge/git/07-rebasing.md`
- `knowledge/git/23-trunk-based-development.md`
- `knowledge/git/27-best-practices.md`
