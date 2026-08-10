---
id: git/24-monorepo
topic: git
slug: monorepo
title: "Monorepo"
type: doc
order: 24
status: ready
tags: [git, monorepo, CODEOWNERS, holds, projects, committing]
related: [git/25-lfs, git/23-trunk-based-development, git/21-submodules, git/20-hooks, git/18-history]
when_to_use: "Read before setting up, scaling, or committing to a single repository that holds many projects."
---
# Monorepo

## Purpose

This document defines how to run a single Git repository that holds many projects,
packages, or services. It covers structure, performance at scale, partial checkouts,
and the workflow rules that keep a large shared history usable. It is written so an
agent can set up or modify a monorepo without degrading clone times or CI for everyone
else in it.

A monorepo is one version-controlled tree with many buildable units. It is not the same
as a "monolith" (a deployment shape) and not the same as [submodules](21-submodules.md)
(many repos stitched together). The whole point is one atomic history across projects.

## Why It Matters

The monorepo's benefit — atomic cross-project changes and one source of truth — is also
its risk: everyone shares the same object store, the same history, and the same CI. One
bad commit (a checked-in build artifact, a 500 MB binary, a rewritten history) taxes
every developer's clone, fetch, and checkout forever. Git's cost scales with the number
of files, refs, and history depth, not with how much *you* touched. Discipline that is
optional in a small repo becomes mandatory here, because the blast radius is the entire
organization.

## Core Principles

- **One atomic history, many projects.** A single commit can change a library and every
  caller together. Preserve that — do not fracture it with submodules unless a subtree
  has genuinely independent access control or release cadence.
- **Cost scales with tree size and history depth.** Every checked-in file and every
  commit is paid by everyone. Keep binaries out (use [LFS](25-lfs.md)) and keep the
  working tree lean.
- **Prefer [trunk-based development](23-trunk-based-development.md).** Long-lived
  branches in a monorepo diverge across hundreds of projects and produce brutal merges.
- **Make partial work possible.** At scale, nobody needs the whole tree checked out.
  Sparse-checkout and partial clone are first-class, not workarounds.
- **CI must be change-scoped.** Building and testing everything on every commit does not
  scale. Only affected projects should run.

## Best Practices

- Use `git sparse-checkout` so a developer materializes only the directories they work
  in. This shrinks the working tree, not the history.
- Use partial clone (`git clone --filter=blob:none`) to skip downloading blobs until
  they are actually checked out — the biggest win for large histories.
- Turn on the filesystem monitor (`git config core.fsmonitor true`) and commit-graph
  (`git config fetch.writeCommitGraph true`) so `status` and `log` stay fast.
- Enforce a `.gitignore` that blocks build output (`dist/`, `node_modules/`, `target/`)
  and a pre-receive hook that rejects large binaries. Prevention beats cleanup.
- Route large assets through Git [LFS](25-lfs.md); never commit them into the main object
  store where they bloat every clone.
- Scope CI to changed paths using the tool's affected-graph (Nx, Turborepo, Bazel) or a
  `git diff --name-only` gate. Never rebuild the world on every push.
- Adopt a clear ownership map (`CODEOWNERS`) so reviews route to the right team even
  though everything lives together.

## Examples

**Good Example** — a fast, scoped checkout of one project

```bash
# Partial clone: skip blobs until checkout needs them — history downloads in seconds.
git clone --filter=blob:none --sparse git@example.com:org/mono.git
cd mono

# Materialize only the directories this developer owns.
git sparse-checkout set services/payments libs/money

# Local speedups that cost nothing but help everyone's daily commands.
git config core.fsmonitor true
git config fetch.writeCommitGraph true
```

**Bad Example** — the commit that taxes the whole org

```bash
# Full clone of a 40 GB history just to edit one service.
git clone git@example.com:org/mono.git

# Committing build output and a binary into the shared object store.
git add node_modules/ dist/ vendor/model-weights.bin   # bloats every future clone
git commit -m "wip"
# node_modules and the 500 MB blob are now permanent history for everyone.
```

## Common Mistakes

- Committing `node_modules/`, `dist/`, or vendored binaries — they live in history
  forever and are re-downloaded on every clone.
- Reaching for [submodules](21-submodules.md) to "split" a monorepo, which throws away
  the atomic-change property that justified the monorepo in the first place.
- Running full-tree CI on every commit, so pipeline time grows with the repo, not the
  change.
- Long-lived feature branches that diverge from trunk across many projects and produce
  unmergeable conflicts.
- Rewriting shared history to "clean up" — it invalidates every teammate's clone.
- Ignoring commit-graph/fsmonitor, then blaming Git for a slow `git status`.

## Production Tips

- Run `git maintenance start` (or a scheduled `git gc --aggressive` + `git commit-graph
  write`) on the server and on developer machines to keep pack files healthy.
- Track repository health: number of loose objects, largest blobs, clone time. Alert when
  they trend up.
- If a big file was already committed, remove it from history with `git filter-repo` in a
  coordinated, announced rewrite — never silently.
- Provide a bootstrapped clone script so new developers get the partial + sparse config
  by default instead of a naive full clone.

## AI Review Checklist

- Is build output and are large binaries excluded via `.gitignore` and a server-side
  size hook?
- Are large assets routed through [LFS](25-lfs.md) rather than the main object store?
- Does the workflow use partial clone and sparse-checkout for large trees?
- Is CI scoped to changed projects rather than rebuilding everything?
- Is the branching model trunk-based rather than long-lived feature branches?
- Is `CODEOWNERS` present so reviews route correctly across projects?
- Are commit-graph and fsmonitor enabled to keep common commands fast?

## Related

- `knowledge/git/25-lfs.md`
- `knowledge/git/23-trunk-based-development.md`
- `knowledge/git/21-submodules.md`
- `knowledge/git/20-hooks.md`
- `knowledge/git/18-history.md`
