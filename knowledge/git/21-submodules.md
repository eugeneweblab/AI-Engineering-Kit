---
id: git/21-submodules
topic: git
slug: submodules
title: "Submodules"
type: doc
order: 21
status: ready
tags: [git, submodules]
related: [git/24-monorepo, git/25-lfs, git/13-remote-repositories, git/15-pull, git/27-best-practices]
when_to_use: "Read before adding, updating, or cloning a repo that embeds another repo as a submodule."
---
# Submodules

## Purpose

This document defines how to use Git submodules — a mechanism for embedding one Git
repository inside another at a pinned commit. It covers adding, cloning, updating, and
the pitfalls that make submodules the most misused feature in Git. It also frames when
to reach for a submodule versus a [monorepo](24-monorepo.md), a package registry, or
[Git LFS](25-lfs.md).

A submodule records a *pointer*: the parent repo stores the exact commit SHA of the
child repo, not its files. The child is a full, independent repository with its own
history. Understanding that "the parent tracks a commit, not a branch" prevents most
submodule confusion.

## Why It Matters

Submodules solve a real problem — sharing a versioned dependency by source while keeping
histories separate — but they change the everyday workflow in ways that silently trap
teams. A normal `git clone` gives an empty submodule directory; a normal `git pull` does
not update submodule contents; committing in the parent without committing the child
first records a SHA no one else can fetch. These are not edge cases; they are the
default behavior. An agent that does not know them will produce a repo that builds on
one machine and fails on every other.

## Core Principles

- **The parent pins a commit, not a branch.** The submodule stays "detached" at that
  SHA until you deliberately move it and commit the new pointer in the parent.
- **Two commits, always in order.** Changing a submodule means committing *inside* the
  submodule first (and pushing it), then committing the updated pointer in the parent.
  Reverse that order and collaborators get a pointer to an unfetchable commit.
- **Clones are not recursive by default.** A submodule directory is empty until
  initialized. Cloning must use `--recurse-submodules` or the build breaks.
- **Pulls do not update submodules by default.** Fetching the parent does not fetch or
  check out new submodule contents; a separate update step is required.
- **Prefer a package or monorepo when you can.** Reach for submodules only when you
  genuinely need source-level, independently-versioned coupling.

## Best Practices

- Clone with `git clone --recurse-submodules <url>`; if you forgot, run
  `git submodule update --init --recursive`.
- After pulling the parent, run `git submodule update --init --recursive` (or set
  `git config submodule.recurse true` so `git pull` and `git checkout` do it for you).
- To advance a submodule to the latest of its tracked branch:
  `git submodule update --remote <path>`, then commit the new pointer in the parent
  with a message naming the child version.
- Always push the submodule repo *before* pushing the parent that references its new
  commit; enable `push.recurseSubmodules=check` so Git refuses a parent push that
  points at an unpushed submodule commit.
- Pin submodules to tags or reviewed commits, not a moving branch tip, for
  reproducible builds.
- Document the update workflow in the README — submodules fail through unfamiliarity
  more than through bugs.

## Examples

**Good Example** — add, update, and commit in the correct order

```bash
# Add a submodule pinned at a specific reviewed commit.
git submodule add https://example.com/libs/auth.git vendor/auth
git commit -m "chore: vendor auth lib at v2.3.0"

# Later, advance it and record the new pointer — child first, then parent.
cd vendor/auth && git checkout v2.4.0 && git -C . rev-parse HEAD
cd ../.. 
git config push.recurseSubmodules check   # refuse parent push if child isn't pushed
git add vendor/auth                        # stages the NEW commit pointer, not files
git commit -m "chore: bump auth lib to v2.4.0"
```

**Bad Example** — wrong order and a non-recursive clone

```bash
# Bumped the submodule but never pushed the child repo...
git add vendor/auth
git commit -m "bump auth" && git push       # parent now points at a commit
                                            # no one else can fetch → broken clones

# Teammate clones without --recurse-submodules: vendor/auth is EMPTY, build fails,
# and `git pull` alone will never populate it.
git clone https://example.com/app.git
```

## Common Mistakes

- Cloning without `--recurse-submodules`, leaving submodule directories empty.
- Pushing the parent's new pointer before pushing the submodule commit it references.
- Expecting `git pull` to update submodule contents — it does not without config.
- Editing submodule files and committing only in the parent, losing the change (the
  parent tracks a SHA, not your uncommitted edits).
- Pinning to a branch and being surprised the submodule "moves" only on explicit update.
- Reaching for submodules when a versioned package dependency would be simpler and
  safer.

## Production Tips

- Set `submodule.recurse=true` and `push.recurseSubmodules=check` in the repo's
  committed config or onboarding script so the safe behavior is the default.
- In CI, clone with `--recurse-submodules` (or run the init step) and cache the
  submodule fetch to keep pipelines fast.
- If submodules become a constant source of pain, re-evaluate against a monorepo or
  publishing the dependency to a registry; the coordination cost is often higher than
  the coupling benefit.

## AI Review Checklist

- Was the submodule commit pushed to its own remote before the parent pointer was
  pushed?
- Does the clone/CI step use `--recurse-submodules` (or an explicit init)?
- Is `submodule.recurse` (and/or `push.recurseSubmodules=check`) configured so pulls
  and pushes stay consistent?
- Is the submodule pinned to a tag or reviewed commit rather than a moving branch?
- Does the parent commit message record which child version it now points to?
- Was a simpler alternative (package registry, monorepo) considered and ruled out?

## Related

- `knowledge/git/24-monorepo.md`
- `knowledge/git/25-lfs.md`
- `knowledge/git/13-remote-repositories.md`
- `knowledge/git/15-pull.md`
- `knowledge/git/27-best-practices.md`
