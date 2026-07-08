---
id: git/10-revert
topic: git
slug: revert
title: "Revert"
type: doc
order: 10
status: ready
tags: [git, revert]
related: [git/09-reset, git/06-merging, git/08-cherry-pick, git/04-commits, git/19-reflog]
when_to_use: "Read before undoing a commit that has already been pushed or merged to a shared branch."
---
# Revert

## Purpose

This document defines how to undo a change *safely on shared history* with `git revert`. It
covers reverting a single commit, reverting a merge commit, why revert is preferred over reset
for published work, and the "re-applying a reverted change" pitfall. It is written so an agent
can back out a bad change on `main` without rewriting history that others depend on.

Revert is the *additive* undo: instead of deleting a commit like [`git reset`](09-reset.md), it
creates a **new** commit that applies the inverse diff. History is preserved and moves forward,
which is exactly what makes it safe for branches other people have already pulled.

## Why It Matters

When a bad commit reaches `main`, you cannot rewrite it away — teammates and CI have already
built on it. Revert is the only safe undo in that situation: it leaves the original commit in
place and adds a compensating one, so nobody's history breaks and the audit trail stays intact.
The subtle danger is *re-introduction*: because the reverted commit still exists, merging the
same branch again (or reverting the revert) can silently bring the bad change back. Knowing when
to revert, and how to revert a merge, prevents both broken teammates and resurrected bugs.

## Core Principles

- **Revert adds an inverse commit; it never rewrites history.** The original commit and the
  revert both stay in the log. This is what makes it safe on shared branches.
- **Use revert for pushed/shared commits, reset for local ones.** If others may have pulled it,
  revert. If it never left your machine, [reset](09-reset.md) is fine.
- **Reverting a merge needs `-m` to pick the mainline parent.** A merge has two parents; git
  cannot guess which side to undo, so you must specify (`-m 1` is usually the branch you merged
  *into*).
- **A revert can be reverted.** To bring back a change you reverted, revert the revert — do not
  try to re-merge the original branch, which behaves surprisingly.
- **Revert may conflict.** Applying an inverse diff to code that has moved on can conflict just
  like a merge; resolve and continue.

## Best Practices

- Revert a bad commit on `main` with `git revert <sha>`; let git write a clear default message
  ("Revert ...") and add *why* in the body. Do this because the history stays linear and
  auditable; the cost is one extra commit.
- To revert a range, use `git revert <old>..<new>` (git creates one revert commit per commit,
  newest first) rather than a single hand-built inverse.
- When reverting a merge, use `git revert -m 1 <merge-sha>` and record in the message that the
  branch is reverted — so a future re-merge is done consciously (often by reverting the revert
  first).
- Prefer revert over reset for anything shared, because reset + force-push breaks every clone.
- Run the tests after the revert; an inverse diff can reintroduce an old assumption that the
  rest of the code has since dropped.

## Examples

**Good Example** — safely back out a bad commit on a shared branch

```bash
git switch main
git fetch origin && git merge --ff-only origin/main

git revert 7c1d9ab         # creates a NEW commit that undoes 7c1d9ab; original stays
# ... optional conflict if surrounding code changed ...
git revert --continue
npm test                   # confirm the inverse diff leaves a working tree
git push                   # normal push — no force, nobody's history is rewritten
```

**Bad Example** — using reset + force-push to "undo" published history

```bash
git switch main
git reset --hard 7c1d9ab~1   # deletes the bad commit locally by rewriting history
git push --force             # rewrites SHARED main; every teammate's main now diverges
# CI, open PRs, and clones all break; the "undo" caused more damage than the bug
```

## Common Mistakes

- Reverting a merge commit without `-m`, which fails, or with the wrong parent number, which
  undoes the wrong side.
- Re-merging a branch after reverting its merge and being surprised the change does *not* come
  back (you must revert the revert first).
- Using [reset](09-reset.md) + force-push on a shared branch instead of revert.
- Assuming a revert is conflict-free; it can conflict when later code depends on the reverted
  change.
- Writing a bare "Revert" message with no explanation of *why* the change was backed out.
- Reverting individual commits of a squashed feature when a single feature revert was intended.

## Production Tips

- For incident response, revert first to stop the bleeding, then investigate — a revert is fast,
  safe, and fully reversible.
- Keep revert commits self-describing: reference the original SHA and the incident/ticket so the
  audit trail is complete.
- If you later want the reverted work back, `git revert <revert-sha>` reintroduces it cleanly;
  document that in the PR so reviewers understand the double negative.

## AI Review Checklist

- Is revert (not [reset](09-reset.md)) used because the commit is already shared/pushed?
- For a merge commit, is `-m` supplied with the correct mainline parent?
- Does the revert commit message explain *why*, and reference the original SHA?
- Do the tests pass after the revert, confirming the inverse diff is coherent?
- Is a future re-merge handled by reverting the revert, not by naive re-merging?
- Was a normal push used (no force), preserving everyone's history?

## Related

- `knowledge/git/09-reset.md`
- `knowledge/git/06-merging.md`
- `knowledge/git/08-cherry-pick.md`
- `knowledge/git/04-commits.md`
- `knowledge/git/19-reflog.md`
