---
id: git/17-conflict-resolution
topic: git
slug: conflict-resolution
title: "Conflict Resolution"
type: doc
order: 17
status: ready
tags: [git, conflict-resolution]
related: [git/06-merging, git/07-rebasing, git/15-pull, git/09-reset, git/19-reflog]
when_to_use: "Read when a merge, rebase, pull, or cherry-pick stops with conflict markers and you must resolve them."
---
# Conflict Resolution

## Purpose

This document defines how to resolve merge conflicts correctly: understanding the
conflict markers, choosing the right resolution, verifying it, and completing the
operation. It is written so an agent resolves conflicts by *understanding both sides*
rather than blindly picking one, and never ships a resolution that silently drops work.

A conflict happens when [merge](06-merging.md), [rebase](07-rebasing.md),
[pull](15-pull.md), or cherry-pick cannot reconcile two changes to the same lines
automatically. Git stops and hands the decision to you. The resolution is a human
judgement about intent, not a mechanical text merge — which is exactly why it is
error-prone.

## Why It Matters

A botched conflict resolution is one of the most damaging git mistakes because it is
invisible. Deleting the conflict markers and keeping one side compiles and passes a
quick glance, but may have silently dropped a bug fix, a security patch, or another
developer's whole feature. The tests may still pass if coverage is thin. Unlike a
force-push, nothing warns you. The cost of resolving carelessly is not an error message
— it is a regression discovered weeks later with no obvious cause. Conflicts must be
resolved by comprehension, then verified by running the code.

## Core Principles

- **Understand both sides before choosing.** `<<<<<<<` (yours/HEAD), `=======`,
  `>>>>>>>` (theirs/incoming). The correct answer is often *neither verbatim* but a
  combination that preserves both intents.
- **Resolving is deciding, not deleting.** Removing markers to make the file "clean" is
  not resolution; you must produce code that reflects both changes' purpose.
- **Every conflict must be re-tested.** A resolution can compile and still be wrong.
  Build and run the affected tests after resolving, before continuing.
- **Know your escape hatch.** `git merge --abort` / `git rebase --abort` returns you to
  the pre-operation state cleanly. Use it the moment you're confused — don't guess.
- **Small, frequent integration prevents conflicts.** The real fix is upstream:
  short-lived branches and frequent syncing shrink conflicts to nothing.

## Best Practices

- Before resolving, see the scope: `git status` lists conflicted files; `git diff`
  shows the conflicting hunks with both sides.
- Use `git checkout --ours <file>` / `--theirs <file>` only when you *genuinely* want
  one side whole (e.g. a regenerated lockfile) — not as a shortcut to avoid reading.
- After editing each file, stage it (`git add <file>`) to mark it resolved, then
  `git merge --continue` / `git rebase --continue`.
- Turn on `rerere` (`git config rerere.enabled true`) so git remembers resolutions and
  replays them on repeated conflicts (common during long rebases).
- Use a three-way merge tool (`git mergetool`) for complex hunks so you see base, ours,
  and theirs together, not just the two-sided markers.
- Configure `merge.conflictStyle=zdiff3` to also show the common ancestor, making it
  clear what each side *changed* rather than just the final states.
- When lost, `--abort`, re-plan (maybe rebase in smaller steps), and retry.

## Examples

**Good Example** — read both sides, combine intent, verify, then continue

```bash
git merge feature-rate-limit
# Auto-merging failed in limiter.ts; git stopped with markers.
```

```ts
// limiter.ts — resolved by combining BOTH intents, not picking one.
// HEAD raised the limit; incoming added a burst allowance. Both are wanted.
const limit = 100;          // from HEAD: raised steady-state cap
const burst = 20;           // from incoming: new burst allowance
// (conflict markers removed only after the merged logic is correct)
```

```bash
npm test -- limiter          # re-run affected tests BEFORE finishing
git add limiter.ts           # mark resolved
git merge --continue         # complete the merge
```

**Bad Example** — delete markers, keep one side, ship it unverified

```ts
const limit = 100;
// <<<<<<< HEAD ... ======= ... >>>>>>> feature-rate-limit  ← just deleted
// Kept HEAD's version wholesale; the incoming burst-allowance change is now
// silently gone. Nobody re-ran the tests, so the regression ships unnoticed.
```

## Common Mistakes

- Deleting conflict markers and keeping one side without understanding what was dropped.
- Not running tests after resolving, so a logically broken merge compiles and ships.
- Blindly `--theirs`/`--ours` on whole files to make conflicts disappear.
- Forgetting to `git add` resolved files, leaving the merge/rebase stuck.
- Panicking and force-pushing to escape, instead of `--abort` and retry.
- Resolving the same conflict repeatedly in a rebase because `rerere` is off.
- Leaving stray `<<<<<<<`/`>>>>>>>` markers in a committed file (grep for them pre-commit).

## Production Tips

- Enable `rerere.enabled=true` and `merge.conflictStyle=zdiff3` globally; both make
  conflicts faster and safer to resolve.
- Add a pre-commit check that greps for `^<<<<<<< ` / `^>>>>>>> ` and blocks the commit
  — this catches unfinished resolutions before they land.
- Keep branches short-lived and rebase/merge from the integration branch daily; the
  cheapest conflict is the one that never grows large.
- For agents: after resolving, always run the build and the tests touching changed
  files, and diff the resolution against both parents to confirm nothing was dropped.

## AI Review Checklist

- Was **each side understood** and the resolution built to preserve both intents?
- Were **affected tests run** after resolving, before continuing/committing?
- Are there **no leftover conflict markers** (`<<<<<<<`, `=======`, `>>>>>>>`) anywhere?
- Were resolved files **staged** and the operation completed with `--continue`?
- Was `--ours`/`--theirs` used **only** where a whole side was genuinely correct?
- On confusion, was `--abort` used instead of a **force-push escape**?

## Related

- `knowledge/git/06-merging.md`
- `knowledge/git/07-rebasing.md`
- `knowledge/git/15-pull.md`
- `knowledge/git/09-reset.md`
- `knowledge/git/19-reflog.md`
