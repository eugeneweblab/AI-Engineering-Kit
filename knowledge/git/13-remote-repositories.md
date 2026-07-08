---
id: git/13-remote-repositories
topic: git
slug: remote-repositories
title: "Remote Repositories"
type: doc
order: 13
status: ready
tags: [git, remote-repositories]
related: [git/14-fetch, git/15-pull, git/16-push, git/05-branches, git/28-security]
when_to_use: "Read before adding, renaming, or authenticating to any remote, or when tracking branches misbehave."
---
# Remote Repositories

## Purpose

This document defines how to connect a local repository to *remotes* — named
references to other copies of the repository, typically hosted on GitHub, GitLab, or a
server. It is written so an agent can configure remotes, authenticate securely, and
set up branch tracking without leaking credentials or pushing to the wrong place.

A remote is just a name (conventionally `origin`) mapped to a URL. All network
operations — [fetch](14-fetch.md), [pull](15-pull.md), [push](16-push.md) — target a
remote. Getting the remote layout right is the precondition for every collaboration
workflow.

## Why It Matters

The remote is the shared source of truth for a team. Misconfigure it and the damage is
concrete: push to the wrong URL and secrets land in the wrong place; embed a token in a
remote URL and it leaks into `.git/config`, shell history, and CI logs; point at an
HTTP URL and traffic is unauthenticated and interceptable. Tracking configuration also
decides what a bare `git push` or `git pull` does — an ambiguous default here silently
moves the wrong branch. These are one-line settings with repository-wide blast radius,
so they are worth getting exactly right.

## Core Principles

- **`origin` is a convention, not magic.** It is the default name for the primary
  remote. A repo can have many remotes (e.g. `origin` for your fork, `upstream` for the
  source). Name them for what they are.
- **Authenticate with SSH keys or a credential helper — never inline tokens.** A token
  in the URL (`https://user:token@host/...`) is persisted in plaintext and logged.
- **Always use encrypted transport.** SSH or HTTPS. Never `git://` or `http://` for
  anything you care about — they are unauthenticated and unencrypted.
- **A local branch should track exactly one upstream.** The upstream is what
  `git pull`/`git push` default to; ambiguity here is how work goes to the wrong place.
- **The remote is untrusted input.** Fetching does not run code, but never blindly run
  hooks or scripts a remote ships. Verify what you pull.

## Best Practices

- Add remotes explicitly: `git remote add upstream git@github.com:org/repo.git`.
- Prefer SSH URLs (`git@host:org/repo.git`) or HTTPS with a credential manager (`git
  config --global credential.helper`). Store tokens in the OS keychain, not the URL.
- Set upstream when you first push a branch: `git push -u origin feature-x`. Thereafter
  bare `git push`/`git pull` resolve correctly.
- Inspect before you trust: `git remote -v` shows fetch/push URLs; `git remote show
  origin` shows tracking and stale branches.
- Prune deleted remote branches routinely: `git fetch --prune` or set
  `fetch.prune=true`.
- Split read and write when needed: a remote can have a different push URL
  (`git remote set-url --push origin ...`), e.g. fetch from a mirror, push to canonical.
- Rotate a leaked credential immediately and rewrite any config that embedded it.

## Examples

**Good Example** — SSH remote, explicit tracking, credentials out of config

```bash
# SSH URL: authentication is handled by your key/agent, nothing secret in config.
git remote add origin git@github.com:acme/api.git

# First push also records the upstream, so later `git push`/`git pull` are unambiguous.
git push -u origin main

# Add the source repo of a fork under a clear, separate name.
git remote add upstream git@github.com:acme-oss/api.git
git remote -v            # verify URLs and names before doing anything networked
```

**Bad Example** — token baked into the URL over plain HTTP

```bash
# Token is now stored plaintext in .git/config and printed in any command that
# echoes the URL (CI logs, `git remote -v`). Plain http = no encryption.
git remote add origin http://user:ghp_AbC123SecretToken@github.com/acme/api.git

git push                 # no upstream set → git may refuse or push the wrong branch
```

## Common Mistakes

- Embedding a personal access token in the remote URL, leaking it into config and logs.
- Using `http://` or `git://`, exposing traffic to interception and tampering.
- Never setting an upstream, so `git push`/`git pull` are ambiguous or error out.
- Pushing to a fork (`origin`) when you meant the source (`upstream`), or vice versa.
- Letting deleted remote branches accumulate locally because `--prune` is never run.
- Assuming one remote — forgetting a second `upstream` exists and pulling from the wrong one.

## Production Tips

- Standardize on SSH deploy keys or a short-lived token via a credential helper in CI;
  never write long-lived tokens to disk.
- Enforce branch protection on the host so `main` cannot be force-pushed even if a
  local remote is misconfigured.
- Set `fetch.prune=true` and `push.default=simple` globally for predictable defaults.
- Audit `git remote -v` in onboarding scripts to catch typo'd or stale URLs early.

## AI Review Checklist

- Are remote URLs **SSH or HTTPS**, never `http://` or `git://`?
- Are credentials in a **keychain/credential helper**, never inlined in the URL?
- Does each working branch have a **single, correct upstream** set?
- Are `origin` and any `upstream`/fork remotes **named for their real role**?
- Is stale-branch **pruning** configured (`fetch.prune=true` or `--prune`)?
- On the host, is **branch protection** enabled so a bad remote can't force-push `main`?

## Related

- `knowledge/git/14-fetch.md`
- `knowledge/git/15-pull.md`
- `knowledge/git/16-push.md`
- `knowledge/git/05-branches.md`
- `knowledge/git/28-security.md`
