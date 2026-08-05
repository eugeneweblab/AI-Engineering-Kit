---
id: git/11-stash
topic: git
slug: stash
title: "Stash"
type: doc
order: 11
status: ready
tags: [git, stash, apply]
related: [git/09-reset, git/05-branches, git/04-commits, git/06-merging, git/19-reflog]
when_to_use: "Read before shelving uncommitted work to switch branches, pull, or handle an interruption."
---
# Stash

## Purpose

This document defines how to temporarily shelve uncommitted changes with `git stash` and
restore them later. It covers stashing tracked and untracked files, applying vs. popping,
managing multiple stashes, and why a stash is a short-lived scratchpad — not a place to store
work. It is written so an agent can set work aside to switch context without losing changes.

Stash captures your working tree and index into a hidden stack and reverts the tree to a clean
`HEAD`, so you can [switch branches](05-branches.md), [pull](15-pull.md), or take a hotfix, then
restore your work. It is a convenience for *transient* interruptions, not a substitute for a
[commit](04-commits.md).

## Why It Matters

Half-finished work is fragile. When an urgent fix interrupts you, the tempting moves are risky:
committing broken code to your branch, or worse, losing edits to a branch switch or a
`reset --hard`. Stash gives a safe, reversible shelf. But it is easy to misuse — stashes are
easy to forget, invisible in `git log`, dropped silently by `pop` on conflict, and can silently
omit untracked or ignored files. Treating stash as durable storage is how work quietly
disappears. Used as intended — a quick, named, short-lived shelf — it prevents exactly the data
loss it is designed to avoid.

## Core Principles

- **A stash is a stack, not a folder.** Entries are `stash@{0}`, `stash@{1}`, ... Newest on top.
  Naming them is the only way to tell them apart later.
- **`apply` keeps the stash; `pop` applies then drops it.** Prefer `apply` when unsure — you can
  drop it manually once you have confirmed the restore worked.
- **Untracked and ignored files are not stashed by default.** Use `-u` for untracked and `-a`
  for ignored, or they stay behind and can be overwritten.
- **A stash is not a commit and not a backup.** It is not pushed, not in history, and easy to
  lose across a `git gc`. Anything you care about belongs in a commit.
- **`pop` can conflict.** If applying a stash conflicts, git keeps the stash entry (does not
  drop it) so you do not lose it while resolving.

## Best Practices

- Name every stash: `git stash push -m "wip: cart totals refactor"`. Do this because an unnamed
  stash is unidentifiable a day later; the cost is a few words.
- Include untracked files with `git stash push -u` when your work-in-progress adds new files —
  otherwise they are left dirty on the branch you switch to.
- Prefer `git stash apply` over `pop` when restoring onto a *different* branch or after a rebase,
  so a conflict does not leave you unsure whether the stash was kept.
- Keep the stash stack shallow. If work outlives the interruption, turn it into a commit or a
  branch (`git stash branch <name>`), which is durable and reviewable.
- List and inspect before restoring: `git stash list`, then `git stash show -p stash@{1}` to
  confirm you are applying the right one.
- Drop stashes you have confirmed applied (`git stash drop`) so the stack does not accumulate
  stale, confusing entries.

## Examples

**Good Example** — shelve WIP for a hotfix, then restore safely

```bash
git stash push -u -m "wip: search pagination"   # includes new untracked files, named

git switch hotfix/login          # clean tree; work on the urgent fix
# ...fix, commit, push...

git switch feature/search
git stash list                   # confirm which entry is mine
git stash apply stash@{0}        # apply but KEEP it until I've verified the restore
npm test
git stash drop stash@{0}         # only discard once I'm sure the work is back intact
```

**Bad Example** — using stash as long-term storage and losing work

```bash
git stash                        # unnamed, tracked-only: new files silently left behind
# ...days pass, several more `git stash` calls pile up unnamed entries...

git switch main
git stash pop                    # conflict! pop applied partially and I mis-resolve
# I assumed pop dropped it, but on conflict it did not — now I'm unsure what's applied,
# and the new untracked files were never stashed at all: work quietly lost
```

## Common Mistakes

- Leaving stashes unnamed, then being unable to tell which is which.
- Forgetting `-u`/`-a`, so untracked or ignored files are not stashed and get overwritten.
- Using `pop` and, on conflict, assuming the entry was dropped — leading to duplicate or
  half-applied work.
- Treating stash as durable storage; a `git gc` or a forgotten stack loses it.
- Applying the wrong stash from a deep stack because none were inspected first.
- Stashing to move work between branches when a proper commit or `git stash branch` is safer.

## Production Tips

- Recover a dropped stash: its commit still exists briefly — `git fsck --no-reflog | grep
  commit` or the stash reflog can surface it, then `git stash apply <sha>`.
- For anything you might need tomorrow, make a `wip:` commit on a throwaway branch instead of
  stashing; it is pushable, backed up, and survives `gc`.
- `git stash branch <name>` creates a new branch from the stash's base and applies it — the
  clean way to promote an interruption's work into real, reviewable history.

## AI Review Checklist

- Is every stash named so it can be identified later?
- Are untracked/ignored files included with `-u`/`-a` when the WIP adds files?
- Is `apply` (not `pop`) used when restoring across branches or after a rebase?
- Is long-lived work turned into a commit or branch instead of parked in a stash?
- Was the correct stash confirmed with `stash list`/`show` before applying?
- After a `pop` conflict, is it understood the entry was *not* dropped?

## Related

- `knowledge/git/09-reset.md`
- `knowledge/git/05-branches.md`
- `knowledge/git/04-commits.md`
- `knowledge/git/06-merging.md`
- `knowledge/git/19-reflog.md`
