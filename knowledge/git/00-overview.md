---
id: git/00-overview
topic: git
slug: overview
title: "Git Overview"
type: doc
order: 0
status: ready
tags: [git, overview]
related: [git/01-version-control, git/03-repository, git/04-commits, git/05-branches, git/27-best-practices]
when_to_use: "Read first to understand how the git docs fit together and where to go next."
---
# Git Overview

## Purpose

This document is the map for the `git` topic. It orients an agent to what git is,
which docs cover which concern, and the order to read them in. It is not a tutorial —
each linked doc teaches its own subject in depth. Read this first so you know where a
given task belongs before you start changing history.

Git is a distributed version-control system: every clone is a full copy of the project
and its entire history. That single fact shapes every rule in this topic — commits are
cheap and local, history is a shared contract, and "undo" almost never means "delete."

## Why It Matters

Git is the substrate every other change flows through. A wrong `git push --force`, a
commit that leaks a secret, or a rebase of a shared branch can destroy a colleague's
work or expose credentials that are effectively permanent once pushed. Unlike a code
bug, a history mistake is often unrecoverable and always visible to the whole team.
Agents that edit code but treat git carelessly undo their own value. Getting git right
is a prerequisite for every task in this repository, not an afterthought.

## Core Principles

- **Commits are the unit of work and the unit of review.** Keep each one small,
  focused, and buildable. History is documentation, so write it for a future reader.
- **Local history is yours; shared history is a contract.** You may freely rewrite
  commits that have never left your machine. Rewriting anything others have pulled
  breaks their clones — do not do it without explicit coordination.
- **Prefer additive recovery over destructive deletion.** `revert` and the reflog
  recover mistakes without erasing history; `reset --hard` and force-push destroy it.
- **Nothing is committed until it is committed, and nothing is safe until it is
  pushed.** The working tree, the index, and the local repo are three distinct states.

## How These Docs Fit Together

- Start with **concepts**: [version control](01-version-control.md) explains the model,
  then [installation](02-installation.md) gets a correct, identified setup.
- **Local workflow**: [repository](03-repository.md) → [commits](04-commits.md) →
  [branches](05-branches.md) cover the day-to-day loop of staging, committing, and
  isolating work.
- **Combining work**: [merging](06-merging.md), [rebasing](07-rebasing.md),
  [cherry-pick](08-cherry-pick.md), and [conflict resolution](17-conflict-resolution.md)
  cover integrating branches.
- **Undoing**: [reset](09-reset.md), [revert](10-revert.md), [stash](11-stash.md), and
  [reflog](19-reflog.md) cover recovery, safest first.
- **Collaboration**: [remotes](13-remote-repositories.md),
  [fetch](14-fetch.md)/[pull](15-pull.md)/[push](16-push.md), and workflow models like
  [git-flow](22-git-flow.md) and [trunk-based development](23-trunk-based-development.md).
- **Cross-cutting**: [best practices](27-best-practices.md), [security](28-security.md),
  and the [AI review checklist](99-ai-review-checklist.md) apply to everything above.

## Best Practices

- Before any git operation, know which of the three states you are acting on: working
  tree, index (staging area), or committed history. Most confusion comes from mixing them.
- Read the doc that owns the operation before running it. `rebase`, `reset --hard`, and
  `push --force` each have a dedicated doc precisely because they are easy to misuse.
- When unsure whether an action is reversible, check the reflog doc first — most local
  actions are recoverable if you have not garbage-collected.

## Common Mistakes

- Treating git as a backup tool and committing large blobs of unrelated changes at once.
- Rewriting or force-pushing a branch others share, silently corrupting their history.
- Running a destructive command (`reset --hard`, `clean -fd`) before understanding which
  state it touches, then losing uncommitted work.
- Assuming a deleted commit is gone — it usually lives in the reflog for weeks.

## AI Review Checklist

- Does the task touch local-only history or shared history? Is the chosen command safe
  for that case?
- Is each proposed commit small, focused, and buildable on its own?
- Has the relevant per-operation doc been consulted before running a rewriting command?
- Is there any secret or large binary about to enter history that should not?

## Related

- `knowledge/git/01-version-control.md`
- `knowledge/git/03-repository.md`
- `knowledge/git/04-commits.md`
- `knowledge/git/05-branches.md`
- `knowledge/git/27-best-practices.md`
