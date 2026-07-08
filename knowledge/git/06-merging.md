---
id: git/06-merging
topic: git
slug: merging
title: "Merging"
type: doc
order: 6
status: ready
tags: [git, merging]
related: [git/07-rebasing, git/05-branches, git/17-conflict-resolution, git/10-revert, git/19-reflog]
when_to_use: "Read before integrating one branch into another or configuring how pull requests land on the main branch."
---
# Merging

## Purpose

This document defines how to combine the history of one branch into another with
`git merge`. It covers fast-forward vs. three-way merges, merge commits, conflict
handling, and choosing a merge strategy for a pull request. It is written so an agent
can integrate work without losing commits, corrupting history, or hiding a conflict.

Merging is the *non-destructive* way to integrate branches: it never rewrites existing
commits, it adds new ones. That is the opposite trade-off from [rebasing](07-rebasing.md),
which rewrites. Choose consciously; do not merge and rebase the same range interchangeably.

## Why It Matters

The merge is where independent work becomes shared history. A bad merge silently drops a
change, resurrects a reverted bug, or resolves a conflict in favor of the wrong side — and
because the commit graph still looks healthy, nobody notices until production breaks. Merges
also define the *shape* of `main`: a repo full of accidental merge commits and octopus merges
is nearly impossible to bisect or read. Getting merges right keeps history both correct and
legible, which is what makes future debugging possible.

## Core Principles

- **A merge integrates whole branches, not lines.** Git computes a three-way diff between
  the two tips and their common ancestor. Understanding the ancestor tells you why a
  conflict happened.
- **Fast-forward is not always what you want.** If the target has no new commits, git just
  moves the pointer forward — no merge commit, no record that a branch existed.
- **A conflict is a question, not an error.** Git stops because it cannot know which change
  wins. Resolving means *deciding*, not just making the file compile.
- **Never merge with uncommitted work in the tree.** A dirty tree can block the merge or,
  worse, get entangled with it. Commit or [stash](11-stash.md) first.
- **The merge commit is a real commit.** It records both parents and is the natural place
  to describe *why* two lines of work were joined.

## Best Practices

- Update the target branch first (`git fetch` then merge, or `git pull --ff-only`) so you
  merge against current history, not stale history.
- Pick a strategy per branch and enforce it: `--ff-only` for a linear `main`, `--no-ff` to
  always record a merge commit for feature branches, or squash for one-commit-per-PR. Do
  this because a mixed policy makes history unreadable; the cost is one config decision.
- Prefer `git merge --no-ff` for feature branches when you want the branch boundary
  preserved for `git revert -m 1` and `git bisect`.
- Resolve conflicts by understanding both sides, then run the tests before committing the
  merge. A merge that compiles is not a merge that is correct.
- Use `git merge --abort` to return to the pre-merge state cleanly rather than hand-editing
  your way out of a half-finished merge.
- After a merge with conflicts, review the full diff (`git diff HEAD~1`) — conflict markers
  left in a file, or a side accidentally deleted, are common and invisible to the compiler.

## Examples

**Good Example** — deliberate, verified merge of a feature branch

```bash
git switch main
git fetch origin
git merge --ff-only origin/main   # move main to current remote tip, or fail loudly

git merge --no-ff feature/checkout   # keep the branch boundary as a merge commit
# ... git reports a conflict in cart.ts ...

git status                 # see exactly which files are unmerged
# edit cart.ts: choose the correct logic from BOTH sides, remove <<<< ==== >>>> markers
git add cart.ts
npm test                   # verify the resolution actually works before recording it
git merge --continue       # writes the merge commit only after tests pass
```

**Bad Example** — blind merge that hides a broken resolution

```bash
git merge feature/checkout
# conflict in cart.ts, but instead of reasoning about it:
git checkout --theirs cart.ts   # blindly take one side, discarding the other's change
git add -A
git commit --no-verify -m "merge"  # skips hooks, no tests run, one side silently lost
# history now looks clean but a real change from main was thrown away
```

## Common Mistakes

- Fast-forwarding when you needed a merge commit, erasing the fact that a feature branch
  existed (breaks `git revert -m` and `bisect` grouping).
- Resolving a conflict with `--ours`/`--theirs` wholesale instead of combining both changes.
- Committing a merge with leftover `<<<<<<<` markers still in the file.
- Merging a stale target, so the merge "succeeds" but is missing the latest `main` commits.
- Using `git pull` (which merges by default) on a branch you meant to keep linear, creating
  a surprise merge commit.
- Octopus-merging many branches at once, producing a commit no tool can bisect through.

## Production Tips

- Configure `merge.ff = false` on `main` (or branch protection "require merge commit") so
  every PR is a reviewable merge point.
- Enable `git rerere` (`git config rerere.enabled true`) so repeated conflict resolutions
  during long-lived merges are replayed automatically.
- To undo a merge you already committed but have not pushed, `git reset --hard HEAD@{1}`
  using the [reflog](19-reflog.md); to undo a *pushed* merge, use `git revert -m 1`.
- Keep feature branches short-lived; the longer a branch diverges, the larger and riskier
  the eventual merge conflict.

## AI Review Checklist

- Was the target branch updated before merging, so no commits are missing?
- Is the merge strategy (`--ff-only`, `--no-ff`, squash) consistent with the repo policy?
- Were conflicts resolved by combining both sides, not by discarding one wholesale?
- Do the tests pass on the merge result, not just on each branch individually?
- Are there any leftover conflict markers in the merged files?
- For a merge that must be undone later, is the branch boundary preserved for `revert -m`?

## Related

- `knowledge/git/07-rebasing.md`
- `knowledge/git/05-branches.md`
- `knowledge/git/17-conflict-resolution.md`
- `knowledge/git/10-revert.md`
- `knowledge/git/19-reflog.md`
