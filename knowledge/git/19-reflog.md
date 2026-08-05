---
id: git/19-reflog
topic: git
slug: reflog
title: "Reflog"
type: doc
order: 19
status: ready
tags: [git, reflog, reflog, rebase, never, checkout, reset]
related: [git/09-reset, git/07-rebasing, git/18-history, git/08-cherry-pick, git/27-best-practices]
when_to_use: "Read before or right after a destructive operation (reset --hard, rebase, branch delete) to recover lost commits."
---
# Reflog

## Purpose

This document defines how to use the reflog — Git's local log of where each ref
(branch, `HEAD`) pointed over time — to recover work that seems lost after a bad
`reset`, `rebase`, `checkout`, or branch deletion. It covers `git reflog`,
`HEAD@{n}` syntax, and the recovery workflow.

The reflog is the safety net beneath almost every "destructive" Git command. Because
Git rarely deletes commit objects immediately, a commit you can no longer reach from
any branch is usually still recoverable through the reflog for weeks.

## Why It Matters

A `git reset --hard` or a botched interactive rebase can appear to vaporize hours of
work, and panic makes people do worse things (re-cloning, forcing pushes) that turn a
recoverable situation into a real loss. Knowing the reflog exists changes the emotional
math: almost nothing committed is truly gone. The reflog is what lets an agent
confidently answer "I ran the wrong command, get my commits back" instead of "the work
is lost."

## Core Principles

- **Committed work is rarely lost.** If a change was ever committed, its commit object
  survives in the reflog even after the branch that pointed to it is gone.
- **The reflog is local and private.** It lives in `.git/logs`, is never pushed, and
  differs on every clone. You cannot recover a *teammate's* lost commit from *your*
  reflog.
- **Uncommitted changes are not protected.** The reflog records ref movements, not your
  working tree. `git reset --hard` or `git checkout` over dirty, uncommitted files
  loses them with no reflog entry.
- **Entries expire.** Reachable entries default to 90 days, unreachable ones to 30
  (`gc.reflogExpire`). Recover promptly; do not assume it is forever.
- **Recover by pointing a ref at the lost commit**, then verify before continuing.

## Best Practices

- After any destructive command, run `git reflog` (or `git reflog show <branch>`)
  *before* doing anything else — later operations push the entry down the list.
- Read entries as `HEAD@{n}`: `HEAD@{0}` is now, `HEAD@{1}` the state before the last
  ref move. `git reflog` labels each with the action (`reset:`, `rebase:`, `commit:`).
- Recover to a *new* branch so you never overwrite current work:
  `git branch recovered <sha>`. Inspect it, then merge or reset onto it deliberately.
- Use `git reflog show <branch>@{yesterday}` or `@{2.hours.ago}` for time-based
  recovery when you do not know the index.
- To undo a bad rebase entirely, find the pre-rebase `HEAD@{n}` and
  `git reset --hard HEAD@{n}` — but only when the working tree is clean.
- Combine with `git fsck --lost-found` to surface dangling commits that no reflog
  entry names (e.g. a dropped stash).

## Examples

**Good Example** — recover commits after an accidental hard reset

```bash
# You ran: git reset --hard HEAD~5  and lost 5 good commits.
git reflog
# ab12cd3 HEAD@{0}: reset: moving to HEAD~5
# ef45gh6 HEAD@{1}: commit: add invoice export   <-- the tip you want back

# Point a NEW branch at the pre-reset tip so nothing else is touched or overwritten.
git branch recovered ef45gh6

# Inspect it, confirm it is the lost work, then move your branch back deliberately.
git log --oneline recovered
git reset --hard recovered   # only once the working tree is clean
```

**Bad Example** — panicking and destroying the safety net

```bash
# After a bad reset, immediately force-resetting again or re-cloning.
git reset --hard origin/main   # discards the very reflog tip you needed
rm -rf my-repo && git clone …  # your local reflog (the only copy) is now gone

# Or running reset --hard with UNCOMMITTED changes and expecting the reflog to help.
git reset --hard HEAD~1        # uncommitted edits are gone; reflog cannot restore them
```

## Common Mistakes

- Assuming lost commits are unrecoverable and re-cloning, which deletes the reflog.
- Expecting the reflog to restore *uncommitted* working-tree changes — it cannot.
- Recovering by resetting the current branch directly instead of first parking the
  commit on a new branch, risking a second loss.
- Trying to recover a colleague's lost commit from your machine — reflogs are local.
- Waiting past the expiry window and letting `git gc` prune the dangling commit.

## Production Tips

- Increase retention on important repos: set `gc.reflogExpire` and
  `gc.reflogExpireUnreachable` (e.g. `never`) so critical recovery windows do not close.
- Teach the workflow "reset/rebase went wrong → `git reflog` → branch the good sha"
  as a reflex; it prevents most self-inflicted data loss.
- The stash is reflog-backed too: a dropped stash often survives as a dangling commit
  findable via `git fsck --unreachable | grep commit`.

## AI Review Checklist

- After a destructive command failed, did you check `git reflog` before anything else?
- Are you recovering onto a *new* branch rather than resetting the current one blindly?
- Did you confirm the changes were committed (not just working-tree edits) before
  relying on the reflog?
- Are you aware the reflog is local and cannot recover a teammate's work?
- Is the recovery within the expiry window, before `gc` could prune the commit?

## Related

- `knowledge/git/09-reset.md`
- `knowledge/git/07-rebasing.md`
- `knowledge/git/18-history.md`
- `knowledge/git/08-cherry-pick.md`
- `knowledge/git/27-best-practices.md`
