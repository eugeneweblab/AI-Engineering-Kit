---
id: git/01-version-control
topic: git
slug: version-control
title: "Version Control"
type: doc
order: 1
status: ready
tags: [git, version-control, commit, nothing]
related: [git/00-overview, git/03-repository, git/04-commits, git/13-remote-repositories, git/27-best-practices]
when_to_use: "Read before reasoning about git's model — the three states, distributed history, and what an operation actually changes."
---
# Version Control

## Purpose

This document explains the mental model behind git so an agent can predict what any
command does before running it. Version control tracks *changes* to files over time and
lets many people work on the same project without overwriting each other. Git is a
particular kind of version control — **distributed** and **snapshot-based** — and those
two properties explain nearly every rule in this topic.

## Why It Matters

Almost every git mistake traces back to a wrong mental model: acting on the wrong state,
assuming an operation is centralized when it is local, or thinking git stores diffs when
it stores snapshots. If you understand what a command *moves* — a pointer, a snapshot, a
ref — you rarely need to memorize flags, and you never run a destructive command by
accident. This model is the foundation every other git doc builds on.

## Core Principles

- **Git stores snapshots, not diffs.** Each commit is a complete picture of the tree,
  addressed by the SHA-1/SHA-256 hash of its content. Diffs are computed on demand.
  This is why branching and switching are cheap.
- **Content is addressed by hash.** Identical content is stored once; a commit's identity
  is derived from its content *and* its parent, so rewriting any commit changes the hash
  of every commit after it. That is why history rewrites cascade.
- **There are three states, always.** The **working tree** (files on disk), the **index**
  (a.k.a. staging area — what the next commit will contain), and the **committed history**
  (the object database). Every command acts on one or two of these; name them before you act.
- **Git is distributed.** Your clone holds the full history. `commit` is local and
  instant; only `push`/`fetch`/`pull` touch the network. Nothing you do locally affects
  anyone until you push.

## Best Practices

- Before running a command, state which of the three states it reads and writes. If you
  cannot, look it up — do not guess with destructive commands.
- Use `git status` and `git diff` (working tree vs index) and `git diff --staged`
  (index vs HEAD) constantly to see exactly where changes live.
- Treat the commit hash as the source of truth for identity. Branch names are just
  movable labels pointing at commits; deleting a branch does not delete its commits.
- Reason about history as a directed acyclic graph of commits, each pointing at its
  parent(s). Merges create a commit with two parents; that graph shape is the whole model.

## Examples

**Good Example** — inspect state before acting

```bash
git status              # which files are untracked, modified, staged?
git diff                # working tree vs index: unstaged changes
git diff --staged       # index vs HEAD: what a commit would capture now
git add -p              # stage deliberately, hunk by hunk, into the index
git commit -m "..."     # snapshot the index into local history — no network
```

**Bad Example** — acting blind, then network-panic

```bash
git commit -am "fix"    # -a stages ALL tracked changes without review;
                        # unrelated edits sneak into one snapshot
git reset --hard        # discards working tree AND index with no inspection first
# ...then confusion about why local work is gone and why teammates
# see nothing (commit was never pushed) — a model mismatch, not a git bug
```

## Common Mistakes

- Believing git stores diffs, then being surprised that switching branches is instant.
- Confusing the index with the working tree — staging one file and assuming the whole
  commit is captured.
- Thinking a local commit is shared (it is not until `push`) or that a `push` is needed
  to save work locally (it is not; `commit` already did).
- Assuming deleting a branch deletes its commits; the commits persist until garbage
  collection, and often long after via the reflog.

## AI Review Checklist

- For each git command in a plan, is it clear which of the three states it changes?
- Does the plan distinguish local operations (commit, branch, reset) from network ones
  (fetch, pull, push)?
- Does any step assume diff-based storage or centralized behavior that git does not have?
- Is branch-vs-commit identity treated correctly (branches are movable pointers)?

## Related

- `knowledge/git/00-overview.md`
- `knowledge/git/03-repository.md`
- `knowledge/git/04-commits.md`
- `knowledge/git/13-remote-repositories.md`
- `knowledge/git/27-best-practices.md`
