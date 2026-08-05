---
id: git/07-rebasing
topic: git
slug: rebasing
title: "Rebasing"
type: doc
order: 7
status: ready
tags: [git, rebasing, origin, develop]
related: [git/06-merging, git/09-reset, git/19-reflog, git/17-conflict-resolution, git/05-branches]
when_to_use: "Read before running git rebase, cleaning up a feature branch, or deciding whether to rebase or merge."
---
# Rebasing

## Purpose

This document defines how to move or rewrite a series of commits with `git rebase`. It
covers replaying a branch onto a new base, interactive rebase for cleaning history, the
golden rule about shared branches, and recovering from a rebase gone wrong. It is written
so an agent can rewrite history deliberately without destroying a teammate's work.

Rebasing is the *destructive* counterpart to [merging](06-merging.md): it creates new
commits with new hashes and discards the originals. That produces a linear, readable history
at the cost of rewriting — which is safe on private branches and dangerous on shared ones.

## Why It Matters

Rebase is the sharpest tool in git. Used well, it turns a messy work-in-progress branch into
a clean, bisectable story that reviewers can actually read. Used carelessly on a branch other
people have pulled, it rewrites commits out from under them, forces painful re-merges, and can
lose work permanently. The difference between "elegant history" and "team-wide data loss" is a
single judgment call: has anyone else based work on these commits? Every rebase decision hinges
on answering that correctly.

## Core Principles

- **Never rebase commits that others have pulled.** The golden rule. Rewriting shared history
  forces everyone downstream into a forced re-sync and risks lost commits. Rebase only private,
  unpushed (or explicitly personal) branches.
- **Rebase creates new commits.** The old ones survive only in the [reflog](19-reflog.md) until
  garbage-collected. A hash you rebased is gone from the branch.
- **Rebase replays commits one at a time.** Each commit can conflict independently, so you may
  resolve conflicts several times — once per replayed commit.
- **Interactive rebase is for shaping history**, not for logic changes: reorder, squash, fixup,
  edit, and drop commits before they are shared.
- **A rebase can be aborted at any pause.** `git rebase --abort` restores the exact pre-rebase
  state. You are never trapped mid-rebase.

## Best Practices

- Use `git pull --rebase` (or set `pull.rebase = true`) to keep a linear history when syncing
  a feature branch, instead of littering it with merge commits from `origin`.
- Clean up a feature branch with `git rebase -i` before opening or updating a PR: squash "fix
  typo" commits, reorder for a logical story. Do this because reviewers read commits, not just
  the final diff; the cost is that it rewrites, so finish it before others pull.
- Prefer `git commit --fixup=<sha>` during work, then `git rebase -i --autosquash` to fold the
  fixups automatically and safely.
- When force-pushing a rebased branch, always use `git push --force-with-lease`, never plain
  `--force`. Lease refuses the push if the remote moved, protecting a teammate's commits.
- Enable `git config rerere.enabled true` so conflict resolutions are remembered across the
  repeated replays of a rebase.
- If a rebase gets confusing, `git rebase --abort` and reconsider; do not push through blindly.

## Examples

**Good Example** — clean up a private branch, then update it safely

```bash
git switch feature/search
git fetch origin
git rebase origin/main          # replay my commits on top of the latest main

# ... conflict in query.ts on the 2nd replayed commit ...
git status                      # shows which commit is being applied
# resolve query.ts, keeping the intent of THIS commit
git add query.ts
git rebase --continue           # move on to the next commit

git rebase -i origin/main       # squash "wip" and "fix typo" into their parent commits
git push --force-with-lease     # safe force: refuses if someone else pushed meanwhile
```

**Bad Example** — rebasing shared history and force-pushing over teammates

```bash
git switch main
git rebase feature/big-refactor   # rewriting main, which everyone has pulled
git push --force                  # clobbers the remote unconditionally
# every teammate's local main now diverges; their next push/pull can lose commits
# and any PR branched off the old main points at commits that no longer exist
```

## Common Mistakes

- Rebasing `main`, `develop`, or any branch others have based work on.
- Using `git push --force` instead of `--force-with-lease`, overwriting commits pushed
  after your last fetch.
- Rebasing to "fix" a conflict, ending up resolving the same conflict on every replayed
  commit, and resolving it inconsistently.
- Losing work in a rebase and assuming it is gone — it is almost always recoverable from
  the [reflog](19-reflog.md) (`git reflog`, then `git reset --hard <sha>`).
- Interactive-rebasing to change code logic and calling it a cleanup; that hides real
  changes inside a "history tidy" commit.
- Rebasing a branch that a PR is already under review on, invalidating reviewers' comments.

## Production Tips

- Team policy should be explicit: rebase feature branches, merge into `main` (see
  [trunk-based development](23-trunk-based-development.md)). Write it down so it is enforced,
  not assumed.
- Recover a lost pre-rebase state with `git reflog` — find the `HEAD@{n}` before the rebase
  and `git reset --hard` to it. This works even after a bad `--force-with-lease` locally.
- For very long rebases, split the work: rebase in smaller ranges so each conflict batch is
  tractable.

## AI Review Checklist

- Are the rebased commits private/unshared, satisfying the golden rule?
- Is every force-push a `--force-with-lease`, never a bare `--force`?
- Were per-commit conflicts resolved consistently with each commit's intent?
- Does the interactive rebase only reshape history, not smuggle in logic changes?
- Is the choice of rebase (vs. [merge](06-merging.md)) consistent with the repo's policy?
- Is there a reflog-based recovery path if the rebase result is wrong?

## Related

- `knowledge/git/06-merging.md`
- `knowledge/git/09-reset.md`
- `knowledge/git/19-reflog.md`
- `knowledge/git/17-conflict-resolution.md`
- `knowledge/git/05-branches.md`
