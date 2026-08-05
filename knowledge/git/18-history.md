---
id: git/18-history
topic: git
slug: history
title: "History"
type: doc
order: 18
status: ready
tags: [git, history, lines]
related: [git/04-commits, git/19-reflog, git/07-rebasing, git/26-debugging, git/27-best-practices]
when_to_use: "Read before investigating how or when code changed — searching, blaming, or auditing commit history."
---
# History

## Purpose

This document defines how to read a repository's recorded history: listing commits,
tracing who changed a line and why, following a file across renames, and searching for
when a behavior was introduced. It covers `git log`, `git show`, `git blame`, and the
history-search flags an agent uses to answer "what changed, when, and why".

History is the *committed* record — the immutable chain of commits on your branches.
It is distinct from the [reflog](19-reflog.md), which is your local, private record of
where refs *pointed* over time. Use history to understand the codebase; use the reflog
to recover from mistakes.

## Why It Matters

History is the primary evidence an agent has about intent. A diff shows *what* changed;
the commit message and surrounding history show *why*. Skipping history leads to blind
edits: reverting a fix that guarded against a known bug, re-introducing a reverted
change, or misreading a rename as a delete-plus-add. Good history reading turns a
confusing codebase into a documented one — every line has a commit, and every commit
has a reason.

## Core Principles

- **Read before you write.** Before changing unfamiliar code, run `git log` and
  `git blame` on it. The reason it looks odd is usually in the history.
- **The message is the interface.** History is only as useful as its commit messages.
  A commit that says "fix" teaches nothing; one that names the bug and the cause is a
  permanent explanation.
- **Follow content, not filenames.** Files move and rename. Use `--follow` and `-M` so
  history tracks the code, not the path.
- **Query, do not scroll.** History can hold millions of commits. Filter by author,
  path, date, or content instead of reading linearly.
- **History is append-only in shared branches.** Reading history is always safe;
  rewriting shared history is not (see [rebasing](07-rebasing.md)).

## Best Practices

- Use `git log --oneline --graph --decorate` for a compact, branch-aware overview.
- Scope by path: `git log -- path/to/file` shows only commits touching that file.
- Use `git log -p` to see the diff of each commit, and `git log -S"string"` (the
  "pickaxe") to find the commit that added or removed a specific string.
- Use `git log -L :funcName:file.c` to see the history of a single function.
- Prefer `git blame -w -M -C` to ignore whitespace and see through moved/copied code,
  so blame points at the author of the logic, not the last reformatter.
- Follow renames with `git log --follow -- path`; without it, history stops at the
  rename.
- Use `git shortlog -sn` to summarize contributions, and `git log --since/--until` to
  bound by time.
- When blame lands on a noise commit (a mass reformat), record that commit in
  `.git-blame-ignore-revs` and set `blame.ignoreRevsFile` so it is skipped
  automatically.

## Examples

**Good Example** — targeted, rename-aware history investigation

```bash
# Find WHEN a specific string was introduced or removed, across the whole repo.
# -S is the "pickaxe": it matches commits that changed the count of this string.
git log -S"MAX_RETRIES" --oneline

# Trace one function's evolution, following it through file renames.
git log --follow -L :calculateTax:src/billing.ts

# Blame that sees through moves and ignores whitespace-only churn,
# so it credits the author of the logic, not the last reformat.
git blame -w -M -C src/billing.ts
```

**Bad Example** — scrolling blindly and being misled by noise

```bash
# Dumps the entire history to a pager and scrolls by hand — no filter, no diff.
# On a large repo this finds nothing and wastes the whole session.
git log

# Plain blame credits whoever last reformatted the file, not who wrote the logic,
# because it does not ignore whitespace (-w) or follow moved lines (-M).
git blame src/billing.ts
```

## Common Mistakes

- Reading `git log` unfiltered on a large repo instead of scoping by path, string,
  or author.
- Running `git blame` without `-w`/`-M`, so a reformat commit hides the real author.
- Omitting `--follow`, so a file's history appears to start at its last rename.
- Trusting the diff alone and ignoring the commit message that explains *why*.
- Assuming history is truth about *current* refs — that is the [reflog](19-reflog.md),
  not `git log`.
- Rewriting shared history to "clean it up", breaking every collaborator's clone.

## Production Tips

- Add a `.git-blame-ignore-revs` file listing mass-reformat commits and commit it;
  GitHub and `git blame` both honor it once `blame.ignoreRevsFile` is set.
- Enforce a commit-message convention (e.g. Conventional Commits) in CI so history
  stays queryable and changelogs can be generated.
- For "when did this break", reach for [`git bisect`](26-debugging.md) — it binary-
  searches history far faster than reading it linearly.

## AI Review Checklist

- Did you consult `git log`/`git blame` on the code before changing it?
- Are history queries scoped (path, `-S`, author, date) rather than unfiltered?
- Is `--follow` used when a file may have been renamed?
- Does `git blame` use `-w -M` so it credits the logic author, not a reformatter?
- Are noise commits recorded in `.git-blame-ignore-revs`?
- Do new commit messages explain *why*, so future history reads are useful?

## Related

- `knowledge/git/04-commits.md`
- `knowledge/git/19-reflog.md`
- `knowledge/git/07-rebasing.md`
- `knowledge/git/26-debugging.md`
- `knowledge/git/27-best-practices.md`
