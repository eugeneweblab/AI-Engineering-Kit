---
id: git/15-pull
topic: git
slug: pull
title: "Pull"
type: doc
order: 15
status: ready
tags: [git, pull]
related: [git/14-fetch, git/16-push, git/07-rebasing, git/06-merging, git/17-conflict-resolution]
when_to_use: "Read before running git pull, especially on a shared branch or when local changes exist."
---
# Pull

## Purpose

This document defines `git pull`: a [fetch](14-fetch.md) followed immediately by an
integration of the fetched work into your current branch. It is written so an agent
chooses the right integration mode (merge vs rebase), pulls safely with local changes
present, and avoids the accidental merge commits and rewritten history that careless
pulls create.

`git pull` = `git fetch` + `git merge` (default) or `git fetch` + `git rebase` (when
configured). The integration half is the part that can hurt, so the whole point of
understanding pull is understanding *which* integration it performs.

## Why It Matters

Pull is the command that quietly reshapes history. Its default (merge) sprays
"Merge branch 'main' of ..." commits across an otherwise linear history; its
rebase mode rewrites your local commits, which is dangerous if any were already pushed.
Pulling with a dirty working tree can abort mid-way or force a stash you didn't ask
for. And because pull integrates the instant it fetches, you discover conflicts only
*after* the operation started — no chance to inspect first. A wrong default here,
repeated across a team, is how a repository's history becomes an unreadable tangle.

## Core Principles

- **Know which integration pull runs.** Default is merge. Configure the mode
  explicitly per repo (`pull.rebase`) rather than relying on whatever the global
  default happens to be.
- **Never rebase-pull commits you've already pushed to a shared branch.** Rebase
  rewrites SHAs; anyone who has the old commits now diverges. Rebase only local work.
- **Pull with a clean tree.** Commit or [stash](11-stash.md) first. Pulling over
  uncommitted changes invites aborts and messy conflicts.
- **`--ff-only` is the safest default.** It refuses to pull when a merge would be
  needed, turning a silent merge commit into an explicit decision.
- **Prefer fetch + inspect + integrate for anything non-trivial.** Pull is a
  convenience for the fast-forward case, not a substitute for looking.

## Best Practices

- Set an explicit, intentional mode per repo:
  - Feature branches / linear history: `git config pull.rebase true`.
  - Shared long-lived branches: `git config pull.ff only` and integrate deliberately.
- Use `git pull --ff-only` in scripts and CI so a diverged history *fails loudly*
  instead of auto-merging.
- Commit or `git stash` before pulling; verify with `git status` that the tree is clean.
- When rebasing a pull, only do so on commits that are *not yet pushed*.
- After a conflicted pull, resolve per [conflict resolution](17-conflict-resolution.md),
  then `git rebase --continue` or `git merge --continue`; use `--abort` to back out
  cleanly.
- For collaboration on the same branch, prefer `git pull --rebase` to keep a linear
  history — but see the shared-commit caveat above.

## Examples

**Good Example** — explicit, fail-loud pull on a clean tree

```bash
git config pull.rebase true      # this repo integrates by rebase, decided on purpose

git status                       # confirm tree is clean before integrating
git stash                        # (only if there were changes to set aside)

git pull --rebase origin main    # linear history; replays only my *local* commits
git stash pop                    # restore set-aside work
```

**Bad Example** — dirty tree, unknown mode, rewriting shared commits

```bash
# Local commits here were ALREADY pushed to the shared branch.
git config pull.rebase true      # will rewrite those pushed commits' SHAs…
git pull                         # …over a dirty working tree, with no inspection.

# Result: teammates who fetched the old SHAs now diverge; the next push either
# fails or (if forced) clobbers their history. Uncommitted work may be left in a
# half-merged state.
```

## Common Mistakes

- Not knowing whether pull merges or rebases, so history changes shape unpredictably.
- Rebase-pulling commits already pushed to a shared branch, forcing everyone to reconcile.
- Pulling with uncommitted changes, hitting an aborted or half-applied integration.
- Relying on default merge and littering history with "Merge branch 'main'" commits.
- Using `git pull` in CI where a surprise merge commit or conflict breaks the build.
- Treating a conflicted pull as broken and force-pushing to escape, discarding work.

## Production Tips

- In automation, never bare-`git pull`. Use `git fetch` then an explicit
  `git merge --ff-only` or `git rebase`, so failures are diagnosable.
- Set `pull.ff only` as a team default; require an explicit merge/rebase when it fails.
- Document the team's chosen integration model (merge vs rebase) so pulls are consistent.

## AI Review Checklist

- Is the **integration mode** (merge vs rebase) set explicitly, not left to chance?
- Does any rebase-pull touch **only unpushed** commits?
- Is the working tree **clean** (committed or stashed) before the pull?
- Are scripts/CI using `--ff-only` (or fetch + explicit integrate) to **fail loudly**?
- After a conflict, is it resolved with `--continue`/`--abort`, **never** a force-push?

## Related

- `knowledge/git/14-fetch.md`
- `knowledge/git/16-push.md`
- `knowledge/git/07-rebasing.md`
- `knowledge/git/06-merging.md`
- `knowledge/git/17-conflict-resolution.md`
