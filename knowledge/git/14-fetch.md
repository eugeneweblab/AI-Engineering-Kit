---
id: git/14-fetch
topic: git
slug: fetch
title: "Fetch"
type: doc
order: 14
status: ready
tags: [git, fetch]
related: [git/15-pull, git/16-push, git/13-remote-repositories, git/06-merging, git/07-rebasing]
when_to_use: "Read before syncing with a remote, or when you need to see remote changes without touching your working tree."
---
# Fetch

## Purpose

This document defines `git fetch`: downloading commits, branches, and tags from a
remote into your local repository *without* changing your working tree or current
branch. It is written so an agent knows when to fetch (almost always, first) versus
[pull](15-pull.md) (fetch plus integrate), and how to inspect what arrived before
integrating it.

Fetch is the safe half of syncing. It updates the remote-tracking refs
(`origin/main`, `origin/feature-x`) so you can *see* what the remote has, and leaves
integration — [merge](06-merging.md) or [rebase](07-rebasing.md) — as a separate,
deliberate step you control.

## Why It Matters

`git pull` fetches and immediately integrates in one shot; if the incoming history
conflicts or you were mid-change, that surprise merge lands on your working tree at the
worst moment. Fetching first turns that surprise into information: you download the
remote state, review it (`git log HEAD..origin/main`), and then decide how and whether
to integrate. For agents and automation this separation is essential — you can compute
the diff, check for conflicts, and choose merge vs rebase *before* mutating anything,
instead of reacting to a half-applied pull.

## Core Principles

- **Fetch never touches your working tree.** It only advances remote-tracking refs. It
  is always safe to run — no uncommitted work is at risk.
- **Fetch, then integrate — as two steps.** Downloading and merging are separate
  concerns. Doing them separately gives you a checkpoint to inspect before committing.
- **Remote-tracking refs are read-only mirrors.** `origin/main` reflects what the
  remote had at last fetch. You do not commit onto it; you integrate *from* it.
- **Prune to stay honest.** Remote branches deleted upstream linger locally until you
  prune. Stale `origin/*` refs mislead tooling and humans.
- **Fetch is not a decision; it is a measurement.** After fetching, `HEAD..origin/main`
  and `origin/main..HEAD` tell you exactly how you diverge.

## Best Practices

- Fetch before starting or resuming work: `git fetch origin`. It is cheap and safe.
- Inspect the delta before integrating: `git log --oneline HEAD..origin/main` (what's
  incoming) and `git log --oneline origin/main..HEAD` (what's local-only).
- Prune deleted branches: `git fetch --prune`, or set `fetch.prune=true` once.
- Fetch a single branch when you only need one: `git fetch origin main`.
- Fetch tags deliberately: `git fetch --tags` (or rely on default tag-following); do
  not assume tags always come along.
- In CI, use `--depth`/`--filter` for shallow or partial fetches on huge repos, but
  fetch full history when you need `git describe`, blame, or bisect.
- Never `git fetch --force` a tracking ref unless you understand the upstream rewrote
  history — it is a signal something unusual happened.

## Examples

**Good Example** — fetch, inspect, then integrate as a deliberate second step

```bash
git fetch --prune origin              # download + drop refs deleted upstream; safe

# See exactly what arrived before changing anything local.
git log --oneline HEAD..origin/main   # commits I don't have yet
git log --oneline origin/main..HEAD   # commits only I have

# Now integrate intentionally, having seen the diff.
git rebase origin/main                # (or: git merge origin/main)
```

**Bad Example** — blind pull that integrates before you've looked

```bash
# Fetches AND merges in one step, onto whatever state your tree is in.
# If histories diverged, you get a surprise merge/conflict mid-task with no
# chance to inspect, choose rebase, or abort cleanly beforehand.
git pull

# Stale origin/* refs were never pruned, so `git branch -r` still lists
# branches that upstream deleted weeks ago.
```

## Common Mistakes

- Reaching for `git pull` when you only wanted to *see* remote changes — fetch does that.
- Never pruning, so `git branch -r` and tab-completion are cluttered with dead branches.
- Assuming a fetch updated your current branch — it did not; it updated `origin/*` refs.
- Forgetting tags don't always follow, then wondering why a release ref is missing.
- Shallow-fetching in CI, then failing on `git blame`/`bisect`/`describe` that need history.

## Production Tips

- Set `fetch.prune=true` globally so every fetch and pull self-cleans.
- In CI, be explicit: `git fetch --no-tags --depth=1 origin <sha>` for a build-only
  checkout; full clone when history-dependent tooling runs.
- Schedule background fetches (`git fetch` in a cron or editor plugin) so `origin/*` is
  fresh without manual steps — but integrate only on purpose.

## AI Review Checklist

- Is `git fetch` used to **inspect** remote state before any integration?
- Is the incoming delta **reviewed** (`HEAD..origin/main`) before merge/rebase?
- Is **pruning** enabled or run so stale `origin/*` refs don't accumulate?
- If a **shallow/partial** fetch is used in CI, is full history available where
  blame/bisect/describe need it?
- Is integration a **separate, deliberate step**, not an implicit `git pull`?

## Related

- `knowledge/git/15-pull.md`
- `knowledge/git/16-push.md`
- `knowledge/git/13-remote-repositories.md`
- `knowledge/git/06-merging.md`
- `knowledge/git/07-rebasing.md`
