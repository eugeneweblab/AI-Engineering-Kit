---
id: git/03-repository
topic: git
slug: repository
title: "Repository"
type: doc
order: 3
status: ready
tags: [git, repository, node_modules, gitleaks, clone, README, init]
related: [git/00-overview, git/01-version-control, git/04-commits, git/13-remote-repositories, git/28-security]
when_to_use: "Read before initializing or cloning a repo, choosing what to track, or wiring up .gitignore."
---
# Repository

## Purpose

This document covers creating and shaping a git repository: `init` vs `clone`, the
`.git` directory, what to track and what to exclude, and how to keep the repository clean
from day one. Decisions made when a repo is born — what gets committed, how it is
ignored, where its remote lives — are expensive to reverse, because everything committed
becomes part of shared history.

## Why It Matters

A repository is a permanent record. A secret, a 200 MB binary, or a `node_modules`
directory committed on day one stays in history forever unless you rewrite it — a
disruptive, coordinated operation. The `.gitignore` you set up front is the cheapest
possible defense; the cleanup after a bad commit is the most expensive. What a repo
tracks also defines what reviewers see, what CI builds, and how fast every clone is.

## Core Principles

- **A repository is the `.git` directory.** The working tree is just a checked-out view of
  it. Deleting `.git` deletes the entire history; everything else is reconstructable from it.
- **Track source, not artifacts.** Commit what humans author (code, config, docs) and
  exclude anything generated, downloaded, or secret. Artifacts bloat clones and cause
  merge conflicts with no value.
- **Ignore before you add.** `.gitignore` only affects *untracked* files; once a file is
  tracked, ignoring it does nothing. Set ignores before the first `git add`.
- **Secrets never enter the repository.** Credentials, keys, and `.env` files must be
  ignored from the start; a pushed secret is compromised and must be rotated, not just
  deleted.

## Best Practices

- Start a new project with `git init` and immediately add a `.gitignore` and `README`
  before staging code, so artifacts never get tracked in the first place.
- Use language/tool-appropriate ignore templates (e.g. GitHub's `gitignore` templates)
  rather than hand-listing files you will inevitably miss.
- Keep binaries and large assets out of git; use [Git LFS](25-lfs.md) or external storage.
  Git stores full snapshots, so large files bloat every clone permanently.
- Clone with `--depth` for CI when full history is not needed, to speed up and shrink
  checkouts; use a full clone when history operations are required.
- Verify what is tracked with `git ls-files` and check for accidental additions with
  `git status` before the first commit — the first commit sets the baseline.

## Examples

**Good Example** — ignore before add, secrets excluded

```bash
git init
cat > .gitignore <<'EOF'
node_modules/     # generated dependencies — reinstallable, never committed
dist/             # build output — regenerated from source
.env              # secrets — must never enter history
*.log
EOF
git add .gitignore README.md src/
git status        # confirm no .env, no node_modules staged
git commit -m "chore: initialize project"
```

**Bad Example** — everything staged, secrets and artifacts included

```bash
git init
git add .                       # stages .env, node_modules/, dist/ — all of it
git commit -m "initial commit"  # secret is now in history permanently;
                                # deleting .env later does NOT remove it from past commits
git push                        # secret is now leaked to the remote — rotate it, do not just delete
```

## Common Mistakes

- Running `git add .` before writing `.gitignore`, permanently committing artifacts and
  secrets on the first commit.
- Adding a `.gitignore` entry for a file that is already tracked and expecting it to stop
  being tracked (it will not — run `git rm --cached` first).
- Committing large binaries directly, bloating every future clone with content git can
  never garbage-collect out of history.
- Assuming deleting a committed secret fixes the leak; the secret persists in history and
  must be rotated and scrubbed with a history rewrite.

## Production Tips

- Add a pre-commit secret scanner (e.g. `gitleaks`) so credentials are caught before they
  reach history, not after.
- Commit a `.gitattributes` alongside `.gitignore` to lock line endings and mark binary
  files, keeping diffs clean across contributors.

## AI Review Checklist

- Was `.gitignore` in place before the first `git add`?
- Are any secrets, `.env` files, or credentials staged or already tracked?
- Are generated artifacts (`node_modules`, `dist`, build output) excluded?
- Are large binaries handled via LFS or external storage rather than committed directly?
- Does `git ls-files` show only human-authored source and config?

## Related

- `knowledge/git/00-overview.md`
- `knowledge/git/01-version-control.md`
- `knowledge/git/04-commits.md`
- `knowledge/git/13-remote-repositories.md`
- `knowledge/git/28-security.md`
