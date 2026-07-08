---
id: git/04-commits
topic: git
slug: commits
title: "Commits"
type: doc
order: 4
status: ready
tags: [git, commits]
related: [git/00-overview, git/01-version-control, git/05-branches, git/07-rebasing, git/27-best-practices]
when_to_use: "Read before staging and writing commits, or when a diff bundles unrelated changes or has a vague message."
---
# Commits

## Purpose

This document defines what makes a good commit: how to stage changes deliberately, how to
write a message a future reader can use, and how to keep each commit atomic. A commit is
the atomic unit of change, of review, and of `revert`. History is the most durable
documentation a project has, so commits are written for the person — or agent — who will
read them months later trying to understand *why* a line looks the way it does.

## Why It Matters

`git blame`, `git bisect`, `git revert`, and code review all operate on commits. A commit
that bundles three unrelated changes cannot be reverted cleanly, breaks `bisect`, and
hides intent. A message that says "fix" tells a future debugger nothing. Good commits turn
history into a searchable explanation of the codebase; bad commits turn it into noise that
actively slows every future investigation. The cost of a sloppy commit is paid repeatedly,
by everyone.

## Core Principles

- **One logical change per commit.** A commit should do exactly one thing and remain
  buildable. This is what makes `revert`, `bisect`, and review work. If you cannot
  summarize it in one line without "and," it is two commits.
- **Stage deliberately, not wholesale.** The index exists so you can compose a commit from
  exactly the changes that belong together. Use `git add -p` to include hunks on purpose.
- **The message explains *why*, not *what*.** The diff already shows what changed. The
  message's job is intent, context, and consequences — the information the diff cannot show.
- **A commit is a promise the code works.** Do not commit broken or half-applied states on
  a shared branch; each commit should pass at least a basic build.

## Best Practices

- Write a message with a concise imperative subject (≤ ~50 chars, e.g. "Add retry to
  fetch"), a blank line, then a body explaining why and any trade-offs. Imperative mood
  matches git's own generated messages.
- Follow a convention (e.g. Conventional Commits: `feat:`, `fix:`, `chore:`) when the team
  uses one, so tooling can derive changelogs and versions automatically.
- Use `git add -p` and review `git diff --staged` before committing to keep unrelated
  changes out of the snapshot.
- Amend only unpushed commits with `git commit --amend` to fix the last commit; never amend
  or rebase commits already shared (it rewrites history others depend on — see
  [rebasing](07-rebasing.md)).
- Reference the issue or ticket in the body (`Refs #123`) so the commit links back to its
  rationale.

## Examples

**Good Example** — atomic change, intent-revealing message

```bash
git add -p src/http/client.ts        # stage only the retry hunk, nothing else
git diff --staged                    # verify the snapshot is exactly this change
git commit -m "fix: retry transient 5xx responses in HTTP client" -m \
"Upstream returns intermittent 503s under load. Retry idempotent GETs
up to 3 times with backoff so callers stop seeing spurious failures.
Refs #482"
# ^ subject states the change; body states WHY and the constraint (idempotent only)
```

**Bad Example** — bundled changes, empty intent

```bash
git commit -am "fixes"
# -a stages every tracked change: the retry fix, an unrelated CSS tweak,
# and a stray debug print all land in one commit.
# "fixes" tells a future debugger nothing, and the commit cannot be
# reverted without also reverting the unrelated changes.
```

## Common Mistakes

- Using `git commit -am` habitually, bundling unrelated edits into one un-revertable commit.
- Writing messages like "fix", "wip", or "update" that carry zero intent.
- Describing *what* changed (the diff already shows it) instead of *why*.
- Committing a broken or non-building state on a shared branch, breaking `bisect` for
  everyone after it.
- Amending or rewriting an already-pushed commit, silently diverging from teammates' history.

## Production Tips

- Enforce message format with a commit-msg hook (e.g. `commitlint`) so conventions are
  mechanical, not manual.
- Squash noisy "wip" commits before merging a feature branch so the mainline history stays
  one-logical-change-per-commit.

## AI Review Checklist

- Does each commit make exactly one logical change and stay buildable?
- Was staging deliberate (no unrelated hunks swept in via `-a` or `add .`)?
- Does the subject line use imperative mood and stay concise?
- Does the body explain *why* and any trade-offs, not restate the diff?
- Are amend/rewrite operations limited to unpushed commits only?

## Related

- `knowledge/git/00-overview.md`
- `knowledge/git/01-version-control.md`
- `knowledge/git/05-branches.md`
- `knowledge/git/07-rebasing.md`
- `knowledge/git/27-best-practices.md`
