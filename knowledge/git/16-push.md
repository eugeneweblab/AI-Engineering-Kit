---
id: git/16-push
topic: git
slug: push
title: "Push"
type: doc
order: 16
status: ready
tags: [git, push]
related: [git/14-fetch, git/15-pull, git/13-remote-repositories, git/12-tags, git/28-security]
when_to_use: "Read before pushing to a shared remote, and always before considering any force-push."
---
# Push

## Purpose

This document defines `git push`: uploading local commits to a remote branch. It is
written so an agent publishes work safely, understands why force-pushing a shared
branch is dangerous, and uses the safe variant (`--force-with-lease`) on the rare
occasion a rewrite is legitimate.

Push is the one everyday git operation that can *destroy* other people's work. Fetch
and pull only affect you; push writes to the shared source of truth. That asymmetry is
why push deserves the most caution of any command in this topic.

## Why It Matters

A plain `git push` is safe — it is rejected if it would lose remote commits. The danger
is `git push --force`, which overwrites the remote branch unconditionally, silently
deleting any commits teammates pushed since your last fetch. On a shared branch that is
irreversible data loss for the team. Pushing to the wrong branch or remote leaks or
misplaces work. And pushing secrets — a committed `.env`, a key — cannot be undone by a
later commit; the secret lives in history forever and must be treated as compromised.
Push is where local mistakes become everyone's problem.

## Core Principles

- **Never `--force` a shared branch.** It deletes remote commits with no warning.
  Protected branches like `main` should reject force-push at the server.
- **If you must rewrite, use `--force-with-lease`.** It refuses the push if the remote
  moved since your last fetch, so you overwrite only the history you actually saw.
- **Push only what you meant to.** Set an upstream and rely on `push.default=simple` so
  a bare `git push` moves exactly the current branch, nothing else.
- **What you push is public and permanent.** A pushed secret is compromised; a pushed
  tag is immutable. There is no clean "undo" once others have fetched.
- **The remote can reject you — that's protection, not an error.** A non-fast-forward
  rejection means the remote has commits you don't. Fetch and integrate, don't force.

## Best Practices

- First push of a branch sets tracking: `git push -u origin feature-x`. After that,
  bare `git push` is unambiguous.
- Keep `push.default=simple` (the modern default) so push never touches other branches.
- When history was rewritten intentionally (interactive rebase on *your own* feature
  branch), publish with `git push --force-with-lease`, never plain `--force`.
- Before force-pushing anything, `git fetch` and confirm no one else pushed to the branch.
- Push tags explicitly and individually (`git push origin v1.4.0`); avoid `--tags`.
- On a rejected push, `git fetch` then integrate ([pull](15-pull.md)/rebase); re-push.
- If you pushed a secret: rotate it immediately, then purge history — the rotation is
  what actually protects you, not the history rewrite.

## Examples

**Good Example** — scoped push, lease-guarded rewrite of a personal branch

```bash
git push -u origin feature-login     # publish + set upstream; only this branch moves

# After an interactive rebase cleaned up MY feature branch's local commits:
git fetch origin                      # make sure I see the latest remote state
git push --force-with-lease origin feature-login
# --force-with-lease aborts if someone else pushed to feature-login since my fetch,
# so I can only overwrite history I actually reviewed.
```

**Bad Example** — unconditional force-push onto a shared branch

```bash
# main has commits from three teammates I haven't fetched.
git push --force origin main
# --force overwrites main with my local version unconditionally: their three
# commits are gone from the remote with no warning and no recovery for anyone
# who hadn't already fetched them. This is destructive and, on main, almost
# never justified.
```

## Common Mistakes

- Using `--force` instead of `--force-with-lease`, wiping teammates' commits.
- Force-pushing a shared/long-lived branch at all, rather than integrating and re-pushing.
- Treating a non-fast-forward rejection as an error to bypass, instead of a fetch signal.
- Pushing secrets in a commit and assuming a later commit "removes" them — it doesn't.
- Pushing with no upstream, moving an unintended branch (pre-`simple` defaults).
- Force-pushing right after `git pull --rebase` rewrote already-shared commits.

## Production Tips

- Enable **branch protection** on `main`/release branches: block force-push and require
  reviews. This makes the destructive path server-rejected, not just discouraged.
- Add a **pre-push hook** or CI secret-scanner to block commits containing credentials
  before they reach the remote.
- Gate pushes to protected branches behind pull requests; humans and agents alike push
  to feature branches and merge via review.
- Prefer `--force-with-lease` in any automation that legitimately rewrites; never `--force`.

## AI Review Checklist

- Is the branch pushed with a **set upstream** and `push.default=simple` (only that
  branch moves)?
- Is there **no plain `--force`** — is `--force-with-lease` used for any rewrite?
- Are **shared/protected branches** never force-pushed (and protected at the server)?
- On a rejected push, is the response to **fetch and integrate**, not force?
- Are **secrets** kept out of pushed commits (pre-push scan), and rotated if leaked?
- Are **tags** pushed explicitly, not dumped via `--tags`?

## Related

- `knowledge/git/14-fetch.md`
- `knowledge/git/15-pull.md`
- `knowledge/git/13-remote-repositories.md`
- `knowledge/git/12-tags.md`
- `knowledge/git/28-security.md`
