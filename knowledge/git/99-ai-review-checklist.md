---
id: git/99-ai-review-checklist
topic: git
slug: ai-review-checklist
title: "AI Review Checklist"
type: doc
order: 99
status: ready
tags: [git, ai-review-checklist]
related: [git/04-commits, git/07-rebasing, git/09-reset, git/17-conflict-resolution, git/100-common-antipatterns]
when_to_use: "Read before reviewing a pull request, a branch, or any proposed git operation for correctness and safety."
---
# AI Review Checklist

## Purpose

This is the checklist an AI agent runs when it reviews git work — a diff, a branch, a PR,
or a proposed command — before approving or executing it. Each item is a concrete,
answerable question. The goal is to catch the class of mistakes that are invisible in the
final code but corrupt history, leak secrets, or destroy work. Use it as a gate: any "no"
on a blocking item stops the merge or the command.

## Why It Matters

Git review is different from code review. A perfect diff can still hide a committed
secret, a rebase that dropped a commit, a merge that silently reverted a fix, or a
`reset --hard` about to erase uncommitted work. These errors do not show up in the file
you are looking at — they show up in the history and the working tree. Reviewing git
specifically, with git-aware questions, is the only way to catch them before they land.

## Commit Quality

- [ ] Does each commit represent one logical, buildable change (not a "wip" grab-bag)?
- [ ] Is every commit message in the imperative mood with a subject that says what changed?
- [ ] Does the body explain *why* — the motivation or trade-off — when the change is non-obvious?
- [ ] Are unrelated formatting or debug changes excluded from the functional commit?
- [ ] Is author identity real and consistent (not `root`, `unknown`, or a placeholder)?

## History & Structure

- [ ] Is the branch rebased/updated onto the current target, or will it merge stale code?
- [ ] Is the history free of accidental merge bubbles from routine `git pull`?
- [ ] If history was rewritten, was the branch private (never pulled by others)?
- [ ] Does the diff include only intended files (no `.env`, `dist/`, `node_modules/`, IDE files)?
- [ ] Did a rebase or squash preserve every intended commit (compare `git log` counts before/after)?

## Merge & Conflict Safety

- [ ] Were [conflicts](17-conflict-resolution.md) resolved by keeping the correct code, not by blindly picking one side?
- [ ] After a merge, do the tests still pass (a "clean" merge can still be semantically broken)?
- [ ] Did the merge accidentally revert a change from the target branch (`git log --merges` / diff against base)?
- [ ] Is the merge strategy consistent with the repo's convention (squash vs. rebase vs. merge)?

## Destructive Operation Safety

- [ ] Before any `reset --hard`, `checkout -- .`, or `clean -fd`, is uncommitted work confirmed safe?
- [ ] Before any force-push, is the branch confirmed to be unshared or explicitly owner-approved?
- [ ] Is [revert](10-revert.md) used instead of [reset](09-reset.md) to undo a *published* commit?
- [ ] Is there a known recovery path ([reflog](19-reflog.md)) if the operation is wrong?

## Security & Secrets

- [ ] Are there zero secrets, tokens, or keys in the diff *and* anywhere in the branch's history?
- [ ] Are release commits/tags signed where the repo requires it?
- [ ] Are generated artifacts and dependencies ignored rather than committed?

## Examples

**Good Example** — reviewing a rebase before approving

```bash
# Confirm no commits were silently dropped during the rebase.
git log --oneline origin/main..HEAD   # expected: same N logical commits, now linear
git range-diff origin/main...@{u} origin/main...HEAD  # per-commit diff of what changed
# Scan the whole branch history for secrets, not just the tip.
git log -p origin/main..HEAD | grep -Ei 'api[_-]?key|secret|password'  # expect: no hits
```

**Bad Example** — "LGTM" from the diff alone

```bash
# Reviewer looked only at the final GitHub diff and approved.
# It hid: a force-push that dropped a teammate's commit, and a committed
# .env in an earlier commit of the same branch. Neither is visible in the
# rendered diff — only `git log`/`range-diff` and a history scan reveal them.
```

## Related

- `knowledge/git/04-commits.md`
- `knowledge/git/07-rebasing.md`
- `knowledge/git/09-reset.md`
- `knowledge/git/17-conflict-resolution.md`
- `knowledge/git/100-common-antipatterns.md`
