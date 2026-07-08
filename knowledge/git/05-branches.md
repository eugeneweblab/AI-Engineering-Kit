---
id: git/05-branches
topic: git
slug: branches
title: "Branches"
type: doc
order: 5
status: ready
tags: [git, branches]
related: [git/00-overview, git/04-commits, git/06-merging, git/16-push, git/23-trunk-based-development]
when_to_use: "Read before creating, switching, or deleting branches, or when deciding how to isolate and integrate work."
---
# Branches

## Purpose

This document explains what a branch actually is, how to use branches to isolate work, and
how to keep them short-lived and integratable. A branch is nothing more than a movable
pointer to a commit — that is the whole mechanism. Understanding this makes branching,
switching, and deleting predictable instead of scary, and makes it obvious why a long-lived
branch is a liability, not a safety net.

## Why It Matters

Branches are where work happens in parallel, but a branch that lives too long drifts from
the mainline until integrating it becomes a painful, conflict-ridden merge. The longer a
branch lives, the more the codebase moves underneath it. Short-lived branches keep merges
trivial and reviews small; stale branches accumulate risk. Because a branch is just a
pointer, the danger is never in creating one — it is in letting it diverge or in deleting
one with unmerged, unrecoverable work.

## Core Principles

- **A branch is a movable pointer to a commit.** Creating one is instant and free; it copies
  nothing. `HEAD` points at the current branch, which points at a commit. Switching just
  moves `HEAD`.
- **Branch to isolate, integrate to finish.** Every branch exists to be merged or rebased
  back. A branch that is never integrated is wasted work, not saved work.
- **Short-lived beats long-lived.** Keep feature branches to hours or days, not weeks. The
  cost of integration grows with divergence, so integrate early and often.
- **Deleting a merged branch is safe; deleting an unmerged one loses commits.** Git warns
  you (`-d` refuses, `-D` forces); heed the warning — forced deletion of unmerged work is
  only recoverable via the reflog.

## Best Practices

- Create and switch in one step with `git switch -c feature/x` (modern, unambiguous) rather
  than the overloaded `git checkout`. `switch` cannot accidentally touch files.
- Name branches with a consistent, descriptive convention (`feat/`, `fix/`, `chore/` plus a
  short slug) so intent is visible in `git branch` and in the remote.
- Keep branches current by regularly integrating the mainline (merge or rebase) so
  divergence — and eventual conflict — stays small.
- Push work-in-progress to a remote branch so it is backed up and reviewable; a branch that
  only exists locally is one `reset --hard` away from being lost.
- Delete branches after merge (`git branch -d`, and prune remotes) to keep the branch list
  meaningful. Stale branches make it unclear what is active.

## Examples

**Good Example** — short-lived, isolated, safely deleted

```bash
git switch -c feat/rate-limit       # instant: new pointer at current commit, HEAD moves to it
# ...make focused commits...
git push -u origin feat/rate-limit  # back up and open for review
git switch main
git merge feat/rate-limit           # integrate while divergence is small
git branch -d feat/rate-limit       # -d refuses if NOT merged — a safety check, not an obstacle
```

**Bad Example** — long-lived branch, forced delete

```bash
git switch -c big-refactor
# ...three weeks of commits, main moves 400 commits ahead, never integrated...
git switch main
git branch -D big-refactor          # -D force-deletes even though it was never merged;
                                    # weeks of commits are now only in the reflog, soon gone
```

## Common Mistakes

- Letting a feature branch live for weeks, turning the final merge into a conflict marathon.
- Using `git checkout` ambiguously (it both switches branches and discards file changes) and
  destroying working-tree edits by mistake — prefer `switch` and `restore`.
- Force-deleting (`-D`) an unmerged branch and losing its commits.
- Working only on a local branch with no remote, so an accidental `reset --hard` or a dead
  laptop erases everything.
- Piling unrelated work onto one branch instead of splitting into focused, mergeable branches.

## Production Tips

- Protect the mainline branch (require reviews and passing CI before merge) so no branch is
  integrated blind.
- Automate stale-branch pruning (`git fetch --prune`, periodic remote cleanup) so the branch
  list reflects only live work.

## AI Review Checklist

- Is each branch scoped to one focused change and expected to be short-lived?
- Is the branch pushed to a remote so the work is backed up and reviewable?
- Is the branch kept current with the mainline to minimize integration conflicts?
- Are branch deletions using `-d` (safe) rather than `-D` unless deletion of unmerged work
  is truly intended?
- Are merged branches cleaned up so the branch list stays meaningful?

## Related

- `knowledge/git/00-overview.md`
- `knowledge/git/04-commits.md`
- `knowledge/git/06-merging.md`
- `knowledge/git/16-push.md`
- `knowledge/git/23-trunk-based-development.md`
