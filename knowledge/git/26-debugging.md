---
id: git/26-debugging
topic: git
slug: debugging
title: "Git Debugging"
type: doc
order: 26
status: ready
tags: [git, debugging, reflog, rebase, bisect]
related: [git/19-reflog, git/18-history, git/09-reset, git/10-revert, git/17-conflict-resolution]
when_to_use: "Read before hunting down which commit introduced a bug or recovering from a bad Git operation."
---
# Git Debugging

## Purpose

This document defines how to use Git to investigate problems: find the commit that
introduced a bug, attribute a line of code, inspect what a command *will* do before
running it, and recover from destructive mistakes. It is written so an agent can diagnose
issues with Git evidence instead of guessing.

Git debugging is not the same as debugging application logic. It answers *when*, *where in
history*, and *by which change* a problem appeared — questions the code alone cannot
answer. The core tools are `bisect`, `blame`, `log`, and `reflog`.

## Why It Matters

"When did this break?" is often the fastest path to a fix, and history is the only record
of it. Guessing wastes hours; `git bisect` finds the culprit commit in a logarithmic
number of steps. Just as important, Git debugging includes *recovery*: most "I lost my
work" panics are recoverable because Git rarely deletes commits immediately — the
[reflog](19-reflog.md) still points to them. Knowing this turns a catastrophe into a
one-line fix. The danger is the opposite: a reflexive `git reset --hard` or forced
operation can turn a recoverable situation into real data loss.

## Core Principles

- **Let the history do the search.** `git bisect` binary-searches commits between a known
  good and bad point — O(log n) builds instead of reading every diff.
- **Inspect before you mutate.** `git diff`, `git log`, and `--dry-run` show what a
  command will change. Look before running anything destructive.
- **Nothing is lost until it is garbage-collected.** Commits you "lost" via reset, rebase,
  or a bad merge are still reachable through the [reflog](19-reflog.md) for weeks.
- **Attribute with `blame`, but read the surrounding commit.** A line's last author is a
  starting point, not the whole story — open the full commit for intent.
- **Reproduce on the exact commit.** Check out the suspect SHA in a clean worktree so the
  bug you are chasing is the bug you are seeing.

## Best Practices

- Automate bisect with a test script: `git bisect run ./test.sh` marks good/bad
  automatically and finds the first bad commit unattended.
- Use `git blame -L 40,60 file` to scope attribution to the lines you care about, and
  `git blame -w -C` to ignore whitespace and follow moved code.
- Use `git log -S"someString"` (the "pickaxe") to find the commit that added or removed a
  specific string — far faster than reading diffs.
- Use `git log -- path` and `git log --follow -- path` to see a single file's history,
  including across renames.
- Before any `reset --hard`, `rebase`, or `clean -fd`, run it with `--dry-run` where
  supported, or stash/branch first so you have an escape hatch.
- After a scary operation, run `git reflog` immediately — the entry you need is usually at
  the top.

## Examples

**Good Example** — automated bisect finds the first bad commit

```bash
git bisect start
git bisect bad                 # current HEAD is broken
git bisect good v1.4.0         # this tag was known good

# Git checks out the midpoint; the script exits non-zero on failure.
git bisect run ./scripts/repro-bug.sh
# -> "abc123 is the first bad commit" — the exact change that broke it.

git bisect reset               # always reset to restore your original HEAD
```

**Bad Example** — panic reset that risks real loss

```bash
# Rebase went wrong, so reach straight for the nuclear option.
git reset --hard HEAD~5        # discards 5 commits AND uncommitted work, no backup

git clean -fd                  # also deletes untracked files, unrecoverable
# Now the recovery path (reflog to the pre-rebase SHA) is harder to reason about,
# and the deleted untracked files are gone for good.
```

## Common Mistakes

- Reading diffs by hand to find a regression instead of running `git bisect`.
- Forgetting `git bisect reset`, leaving the repo checked out on an old commit.
- Treating `git blame` as blame — the last toucher may just have reformatted the line.
- Running `git reset --hard` or `git clean -fd` before checking the [reflog](19-reflog.md),
  destroying recoverable state.
- Assuming lost commits are gone; they persist in the reflog until garbage collection.
- Bisecting against a flaky test, which sends the binary search to the wrong commit.

## Production Tips

- Keep commits small and focused — bisect is only as precise as the commit that changed
  behavior. A 2,000-line commit tells you little.
- Use `git bisect skip` for commits that cannot be built or tested, so a broken
  intermediate state does not poison the search.
- For an obscure loss, widen the net: `git fsck --lost-found` surfaces dangling commits
  the reflog may not name.
- Record the repro command in the repo (a script) so bisect is reproducible by anyone.

## AI Review Checklist

- Was `git bisect` (ideally `bisect run`) used to locate a regression rather than manual
  diff reading?
- Was the [reflog](19-reflog.md) checked before any destructive recovery step?
- Were destructive commands previewed (`--dry-run`, stash, or a backup branch) first?
- Is blame output corroborated by reading the full introducing commit?
- After bisect, was `git bisect reset` run to restore HEAD?
- Are commits small enough that bisect can pinpoint a real behavior change?

## Related

- `knowledge/git/19-reflog.md`
- `knowledge/git/18-history.md`
- `knowledge/git/09-reset.md`
- `knowledge/git/10-revert.md`
- `knowledge/git/17-conflict-resolution.md`
