---
id: git/100-common-antipatterns
topic: git
slug: common-antipatterns
title: "Git Common Antipatterns"
type: doc
order: 100
status: ready
tags: [git, common-antipatterns]
related: [git/06-merging, git/07-rebasing, git/09-reset, git/16-push, git/27-best-practices]
when_to_use: "Read before running a destructive git command or when a repository's history has become hard to follow."
---
# Git Common Antipatterns

## Purpose

This document catalogs the recurring git mistakes that corrupt history, destroy work, or
leak secrets — and gives the concrete fix for each. These are the patterns an agent must
recognize and refuse to reproduce. Every entry states the anti-pattern, *why it is wrong*
(the concrete failure it causes), and *the fix*.

## Why It Matters

Git anti-patterns are uniquely costly because history is append-only and shared. A bad
commit convention degrades every future `git log`; a force-push over shared history breaks
every teammate's clone; a committed secret is public the instant it is pushed and cannot
be un-leaked by deletion. Unlike a code smell you can refactor later, most of these are
either irreversible or expensive to unwind. Recognizing them *before* the command runs is
the whole game.

## Anti-Patterns

### 1. The "wip" / "fixes" commit stream

- **Why it is wrong:** Commits like `wip`, `fix`, `fix again`, `stuff` carry no
  information. `git bisect` lands on one and tells you nothing; `git log` becomes noise;
  reverting a single logical change is impossible because changes are smeared across
  timestamped saves.
- **The fix:** Make each commit one logical, buildable change with an imperative subject
  and a *why* in the body. Reshape messy local history with `git rebase -i` before pushing.

### 2. `git add -A` for everything

- **Why it is wrong:** It sweeps unrelated changes, debug prints, and stray files into one
  commit. The commit is no longer atomic, so it cannot be reverted or cherry-picked
  cleanly, and secrets or build output ride along unnoticed.
- **The fix:** Stage deliberately with `git add -p` (hunk by hunk) or by explicit path.
  Keep one commit to one concern.

### 3. Force-pushing shared history

- **Why it is wrong:** `git push --force` rewrites the remote branch. Every teammate who
  pulled the old history now has a diverged clone; their next pull conflicts or, worse,
  they re-push the old commits and undo your rewrite. Work gets lost in the reconciliation.
- **The fix:** Only rewrite branches nobody else has pulled. When a push is rejected on a
  shared branch, `git pull --rebase` and re-push. If you *must* force on a personal branch,
  use `git push --force-with-lease`, which refuses if the remote moved underneath you.

### 4. `git reset --hard` to "clean up"

- **Why it is wrong:** `reset --hard` discards all uncommitted changes in the working tree
  and index with no confirmation and no trash bin. Uncommitted work — never having been a
  commit — is not in the reflog and is genuinely gone.
- **The fix:** Stash first (`git stash`) or commit to a scratch branch before resetting. To
  undo a *committed* change that is already pushed, use `git revert`, which adds an
  inverse commit instead of erasing history. See [reset](09-reset.md) vs [revert](10-revert.md).

### 5. Committing secrets and generated files

- **Why it is wrong:** A key committed and pushed is compromised immediately, even if you
  delete it in the next commit — it lives in history forever and bots scrape public repos in
  seconds. Committed `node_modules`/`dist` bloat every clone and cause noisy diffs.
- **The fix:** Add them to `.gitignore` *before* the first commit. Store secrets in a secrets
  manager. If a secret was pushed, rotate it immediately (do not rely on scrubbing history).

### 6. Resolving conflicts by picking a side blindly

- **Why it is wrong:** Accepting "ours" or "theirs" wholesale to make the conflict marker
  go away silently drops one side's real changes. The merge compiles, tests may pass, and
  a fix from the target branch is quietly reverted.
- **The fix:** Read both sides, keep the correct *combined* behavior, and run the tests.
  See [conflict resolution](17-conflict-resolution.md).

### 7. Long-lived feature branches

- **Why it is wrong:** A branch that lives for weeks drifts far from the target. The
  eventual merge is a high-risk, conflict-heavy event, and CI never validated the
  integrated code until the end.
- **The fix:** Keep branches short-lived; integrate to the trunk daily behind a feature
  flag if needed. See [trunk-based development](23-trunk-based-development.md).

### 8. Committing as the wrong author

- **Why it is wrong:** Commits authored as `root`, `unknown`, or a shared account destroy
  the audit trail and `git blame`, and may bypass signed-commit requirements.
- **The fix:** Set `git config user.name` and `user.email` per repository; require signed
  commits on protected branches.

### 9. Merging without rebasing to sync

- **Why it is wrong:** Running `git pull` (a merge) repeatedly to sync a feature branch
  litters history with "Merge branch main into feature" bubbles that carry no logical
  change and make the branch's real story unreadable.
- **The fix:** Use `git pull --rebase` for routine syncs so your commits replay on top of
  the latest target, keeping history linear. Reserve merge commits for actual integration.

## Examples

**Good Example** — safe recovery instead of a destructive reset

```bash
git stash push -m "wip before experiment"  # park uncommitted work safely
# ...try the risky thing...
git stash pop                              # nothing lost either way
```

**Bad Example** — the irreversible cleanup

```bash
git reset --hard HEAD       # silently deletes ALL uncommitted work, no undo
git push --force            # rewrites shared history, breaking every teammate's clone
# Both "worked" and both are the exact operations that cause real, permanent loss.
```

## AI Review Checklist

- Are commit messages meaningful, or are they "wip"/"fix" placeholders?
- Was anything staged with a blanket `git add -A` that pulled in unrelated files?
- Is a force-push targeting a shared branch (and is `--force-with-lease` used at minimum)?
- Is `reset --hard` about to run with uncommitted work unstashed?
- Are any secrets or generated files in the diff or history?
- Were conflicts resolved by combining both sides, not blindly picking one?

## Related

- `knowledge/git/06-merging.md`
- `knowledge/git/07-rebasing.md`
- `knowledge/git/09-reset.md`
- `knowledge/git/16-push.md`
- `knowledge/git/27-best-practices.md`
