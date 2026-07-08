---
id: git/08-cherry-pick
topic: git
slug: cherry-pick
title: "Cherry Pick"
type: doc
order: 8
status: ready
tags: [git, cherry-pick]
related: [git/06-merging, git/07-rebasing, git/10-revert, git/04-commits, git/17-conflict-resolution]
when_to_use: "Read before copying a specific commit onto another branch, such as backporting a hotfix to a release branch."
---
# Cherry Pick

## Purpose

This document defines how to apply the change from one specific commit onto the current
branch with `git cherry-pick`. It covers backporting fixes, copying a single commit without
its branch, handling conflicts, and the duplicate-commit trade-off. It is written so an agent
can move an individual change deliberately without creating divergent, hard-to-track history.

Cherry-pick answers "I want *this one change*, not the whole branch." Unlike
[merge](06-merging.md) or [rebase](07-rebasing.md), which move ranges with shared ancestry, it
copies an isolated commit — creating a *new* commit with the same diff but a different hash.

## Why It Matters

Cherry-pick is the standard tool for backporting: a fix lands on `main`, and you need it on a
`release/2.x` branch that must not receive everything else from `main`. Done carefully it is
surgical. Done carelessly it creates duplicate commits that later merges see as conflicts, or
it lifts a fix out of the context (a helper, an import, a migration) it silently depended on —
so the "same" change compiles on one branch and breaks on another. The value is precision; the
risk is copying a change without its dependencies.

## Core Principles

- **Cherry-pick copies a diff, not a commit's history.** The new commit has a new hash and no
  link to the original. Git does not know they are "the same" change.
- **The change must be self-contained.** A commit that relies on earlier commits (a new import,
  a renamed function) will not apply cleanly, or will apply and then fail to build.
- **Duplicated commits can cause future conflicts.** When the source branch later merges into
  the target, git may re-see the same change and conflict. Prefer merge/rebase when you want
  the *whole* line of work.
- **Order matters for multiple picks.** Picking a range replays commits in sequence; a later
  fix may depend on an earlier one.
- **A cherry-pick can be aborted or continued** exactly like a merge when it conflicts.

## Best Practices

- Use `git cherry-pick -x <sha>` when backporting so the commit message records "(cherry picked
  from commit <sha>)". Do this because it gives auditors a trail back to the origin; the cost is
  a one-line message addition.
- Cherry-pick the *minimal* self-contained commit. If a fix spans several commits, pick the
  whole set (`git cherry-pick A^..C`) so dependencies come along.
- After picking a hotfix onto a release branch, verify it builds and tests pass *on that
  branch* — the surrounding code may differ from where it was written.
- When a picked commit conflicts, resolve it in the target branch's context, then
  `git cherry-pick --continue`; use `--abort` to bail out cleanly.
- Prefer picking a merge/rebase of the whole branch when you actually want everything; reserve
  cherry-pick for genuinely isolated changes.

## Examples

**Good Example** — backport a self-contained hotfix with traceability

```bash
git switch release/2.x
git fetch origin

# copy only the security fix from main, recording its origin
git cherry-pick -x 9f3a1c2
# ... conflict because release/2.x has an older config.ts ...
git status                 # see the conflicting file
# resolve config.ts in the context of release/2.x, not main
git add config.ts
git cherry-pick --continue

npm test                   # confirm the fix works against THIS branch's code
```

**Bad Example** — picking a commit that depends on earlier work

```bash
git switch release/2.x
git cherry-pick 4b7e900   # this commit USES a helper added in an earlier main commit
# it applies "cleanly" (no textual conflict) but the helper does not exist here
git commit --no-verify    # skips the failing build hook
# release branch now references an undefined helper: broken, but history looks fine
```

## Common Mistakes

- Cherry-picking a commit whose diff depends on a helper, import, or migration that only
  exists on the source branch.
- Copying many commits one by one when you actually wanted to merge the whole branch,
  producing duplicate history that conflicts on the next merge.
- Omitting `-x`, leaving no record of where a backported fix came from.
- Resolving a pick's conflict using the source branch's logic instead of adapting to the
  target branch's surrounding code.
- Assuming a clean apply means a correct result — no textual conflict does not mean it builds.

## Production Tips

- For a hotfix that must reach several release branches, script the picks and run the test
  suite on each target; never assume "applied cleanly" equals "correct".
- If a cherry-picked change and a later merge collide, `git rerere` (once enabled) will replay
  your earlier resolution automatically.
- To undo a cherry-pick you have not shared, `git reset --hard HEAD~1`; if already pushed, use
  [`git revert`](10-revert.md) instead.

## AI Review Checklist

- Is the picked commit self-contained, or does it depend on commits not present on the target?
- Does the code build and pass tests *on the target branch*, not just the source?
- Was `-x` used to record provenance for a backport?
- Was a conflict resolved in the target branch's context rather than copied from the source?
- Would a [merge](06-merging.md) or [rebase](07-rebasing.md) be more appropriate because the
  whole branch is wanted?

## Related

- `knowledge/git/06-merging.md`
- `knowledge/git/07-rebasing.md`
- `knowledge/git/10-revert.md`
- `knowledge/git/04-commits.md`
- `knowledge/git/17-conflict-resolution.md`
