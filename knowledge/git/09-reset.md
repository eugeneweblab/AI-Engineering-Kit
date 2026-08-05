---
id: git/09-reset
topic: git
slug: reset
title: "Reset"
type: doc
order: 9
status: ready
tags: [git, reset, reset]
related: [git/10-revert, git/19-reflog, git/11-stash, git/04-commits, git/07-rebasing]
when_to_use: "Read before running git reset — especially --hard — or before undoing local commits or unstaging files."
---
# Reset

## Purpose

This document defines how to move the branch pointer and optionally the index and working
tree with `git reset`. It covers the three modes (`--soft`, `--mixed`, `--hard`), unstaging
files, undoing local commits, and why reset is for *local* history only. It is written so an
agent can undo work precisely without destroying committed changes or a colleague's history.

Reset rewrites where your branch points. On unpushed commits that is exactly the tool you
want; on pushed commits it rewrites shared history and you should use [`git revert`](10-revert.md)
instead. The `--hard` variant is the single most common way to permanently lose uncommitted work.

## Why It Matters

`git reset --hard` is the classic footgun: one command discards uncommitted changes with no
undo prompt and no trash bin. Committed work can be recovered from the [reflog](19-reflog.md),
but changes that were never committed are simply gone. Reset is also frequently confused with
revert — people run `reset` on a pushed branch, rewrite public history, and then force-push,
breaking everyone downstream. Understanding exactly what each mode touches — pointer, index,
working tree — is the difference between a clean undo and irreversible data loss.

## Core Principles

- **Reset moves the current branch pointer; the mode decides how far the change reaches.**
  `--soft` = pointer only. `--mixed` (default) = pointer + index. `--hard` = pointer + index
  + working tree.
- **`--hard` discards uncommitted changes permanently.** They are not in any commit, so the
  reflog cannot bring them back. Commit or [stash](11-stash.md) first if unsure.
- **Committed history is recoverable; uncommitted work is not.** After resetting past a commit,
  its hash lives in the reflog for a while — that is your safety net for commits, not for the
  working tree.
- **Reset is for local, unpushed history.** Resetting a pushed branch and force-pushing
  rewrites shared history; use [revert](10-revert.md) for anything already published.
- **`git reset <path>` is unstaging, not resetting history** — it copies a file from the last
  commit into the index without touching the pointer or the working tree.

## Best Practices

- Unstage a file with `git reset <path>` (or the clearer `git restore --staged <path>`) — it
  removes it from the index without discarding your edits.
- Undo the last commit but keep the changes staged with `git reset --soft HEAD~1`; use this to
  re-commit with a better message or split a commit.
- Before any `git reset --hard`, run `git status` and consider `git stash` — do this because
  hard reset has no undo for uncommitted work; the cost is a few seconds.
- Prefer `git restore` for file-level "throw away my edits" operations; it is scoped to the
  working tree and cannot accidentally move the branch pointer.
- Note the reflog line printed before a reset (`git reflog`), so you can `git reset --hard
  HEAD@{1}` to get back if the reset was a mistake.
- Never `git reset --hard` a branch others have pushed to; rewrite only your own local history.

## Examples

**Good Example** — undo a local commit while keeping the work

```bash
# I committed too early and want to keep editing before re-committing
git reset --soft HEAD~1    # pointer back one commit; index + working tree untouched
git status                 # changes are still staged, nothing lost
# ...make more edits...
git commit -m "checkout: validate cart totals and handle empty cart"

# Unstage one file I added by mistake, without losing its edits:
git restore --staged secrets.env   # leaves the file and its contents exactly as they were
```

**Bad Example** — hard reset destroys uncommitted work and public history

```bash
# working tree has hours of uncommitted changes
git reset --hard HEAD~3    # discards the 3 commits AND every uncommitted change — gone
# the uncommitted edits are in no commit, so the reflog cannot recover them

git push --force           # this branch was shared: rewrites history for everyone
# teammates' branches now point at commits that no longer exist upstream
```

## Common Mistakes

- Running `git reset --hard` with uncommitted changes in the tree and losing them permanently.
- Using reset (which rewrites history) on a pushed branch instead of [revert](10-revert.md).
- Confusing `--soft`, `--mixed`, and `--hard` and discarding more than intended.
- Believing the reflog can restore uncommitted working-tree changes — it only tracks commits.
- Using `git reset <path>` expecting it to discard edits (it only unstages; use
  `git restore <path>` to discard).
- Force-pushing after a reset on a shared branch, breaking every downstream clone.

## Production Tips

- Recover a "lost" commit after a reset: `git reflog`, find the pre-reset `HEAD@{n}`, then
  `git reset --hard <sha>` or `git branch rescue <sha>`.
- Configure your shell prompt to show a dirty working tree so `--hard` never surprises you.
- For undoing *published* work, standardize on [`git revert`](10-revert.md) in team docs so
  nobody reaches for reset on `main`.

## AI Review Checklist

- Is the branch being reset local and unpushed (not shared)?
- Does any `--hard` reset risk discarding uncommitted work that should be stashed first?
- Is the correct mode chosen — `--soft`/`--mixed`/`--hard` — for the intended reach?
- Is [revert](10-revert.md) used instead of reset for anything already pushed?
- Is `git reset <path>` (unstage) not being mistaken for discarding edits?
- Is there a reflog recovery path noted before an irreversible-looking reset?

## Related

- `knowledge/git/10-revert.md`
- `knowledge/git/19-reflog.md`
- `knowledge/git/11-stash.md`
- `knowledge/git/04-commits.md`
- `knowledge/git/07-rebasing.md`
