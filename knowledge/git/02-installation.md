---
id: git/02-installation
topic: git
slug: installation
title: "Git Installation"
type: doc
order: 2
status: ready
tags: [git, installation]
related: [git/00-overview, git/03-repository, git/04-commits, git/28-security, git/29-tooling]
when_to_use: "Read before setting up git on a new machine or CI runner, or when commits show the wrong author or line-ending noise."
---
# Git Installation

## Purpose

This document covers installing git and configuring it so that commits are correctly
attributed, line endings are stable, and credentials are handled safely. Installation is
not just `apt install git` — an unconfigured git produces commits with the wrong author,
noisy diffs, and insecure credential storage. Get the config right once and every later
operation behaves.

## Why It Matters

The default global config is where identity and safety live. A missing `user.email`
attaches commits to the wrong person or breaks CI attribution. A wrong `core.autocrlf`
turns every line into a phantom change, poisoning diffs and reviews. Plaintext credential
storage leaks tokens. These are set-once mistakes that silently corrupt thousands of
commits, so treat first-time setup as security-relevant, not boilerplate.

## Core Principles

- **Identity must be set before the first commit.** `user.name` and `user.email` are
  baked into every commit's author and committer fields and cannot be fixed later without
  rewriting history. Set them globally, and per-repo when an account differs.
- **Config is layered: system → global → local.** `--local` (`.git/config`) overrides
  `--global` (`~/.gitconfig`) overrides system. Know which layer you are writing.
- **Line endings are a config decision, not a per-file accident.** Normalize them
  explicitly so the same file does not look changed on different operating systems.
- **Credentials belong in a helper, never in a URL or plaintext file.** Use the OS
  keychain or a credential manager; never commit a token or embed it in a remote URL.

## Best Practices

- Verify identity immediately after install with `git config --get user.email`. Do not
  rely on a globally guessed hostname-based default.
- Prefer `core.autocrlf=input` on macOS/Linux and `true` on Windows, or better, commit a
  `.gitattributes` with `* text=auto` so normalization is per-repo and portable.
- Set `init.defaultBranch=main` so new repos start on a consistent branch name.
- Use a platform credential helper (`osxkeychain`, `manager` on Windows,
  `libsecret`/`cache` on Linux). Never store credentials in plaintext.
- Sign commits (GPG or SSH signing via `commit.gpgsign=true`) on teams that require
  verified authorship; unsigned commits can be forged with any name and email.
- In CI, configure a scoped bot identity and inject tokens via secrets, never hardcoded.

## Examples

**Good Example** — deterministic, attributed, safe setup

```bash
git --version                                    # confirm a maintained version (>= 2.40)
git config --global user.name  "Ada Lovelace"
git config --global user.email "ada@example.com" # correct authorship on every commit
git config --global init.defaultBranch main
git config --global core.autocrlf input          # normalize CRLF on commit, leave LF on checkout
git config --global credential.helper osxkeychain # tokens live in the keychain, not plaintext
git config --get user.email                      # verify before the first commit
```

**Bad Example** — unverified identity and leaked credentials

```bash
git clone https://ada:ghp_realTokenValue@github.com/org/repo.git
# ^ embeds a live token in the URL — it lands in shell history, .git/config,
#   and process listings, effectively leaking a credential.

git commit -m "init"
# author becomes "root@buildbox.(none)" because user.email was never set,
# and the wrong identity is now permanent in history.
```

## Common Mistakes

- Committing before setting `user.email`, producing commits attributed to a machine
  default that cannot be corrected without rewriting history.
- Leaving line-ending config unset, so Windows and Unix contributors see whole files as
  changed and reviews fill with noise.
- Embedding a token in a clone/remote URL, leaking it into config and shell history.
- Setting values with `--local` when a global was intended (or vice versa), so the
  config silently does not apply where expected.

## Production Tips

- Standardize config via a checked-in `.gitattributes` and a documented setup script so
  every contributor and CI runner is identical.
- In containers and CI, set identity with environment variables
  (`GIT_AUTHOR_NAME`, `GIT_COMMITTER_EMAIL`) or an explicit `git config`, and mount
  tokens as secrets.

## AI Review Checklist

- Are `user.name` and `user.email` set at the correct config layer before any commit?
- Is line-ending normalization defined (`.gitattributes` or `core.autocrlf`)?
- Are credentials handled by a helper, with no token in any URL or committed file?
- Is `init.defaultBranch` set to the team's standard (usually `main`)?
- In CI, is identity scoped to a bot and are tokens injected as secrets?

## Related

- `knowledge/git/00-overview.md`
- `knowledge/git/03-repository.md`
- `knowledge/git/04-commits.md`
- `knowledge/git/28-security.md`
- `knowledge/git/29-tooling.md`
