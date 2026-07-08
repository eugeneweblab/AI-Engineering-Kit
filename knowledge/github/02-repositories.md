---
id: github/02-repositories
topic: github
slug: repositories
title: "Repositories"
type: doc
order: 2
status: ready
tags: [github, repositories]
related: [github/01-github-platform, github/06-pull-requests, github/17-branch-protection, github/18-rulesets, github/13-security]
when_to_use: "Read before creating, configuring, or restructuring a repository, or before pushing changes into one you do not own."
---
# Repositories

## Purpose

A repository is the unit that holds code, its full history, and the settings that
govern how the code changes: branches, protection, visibility, collaborators, and
metadata files. This document defines how to lay out and configure a repository so
that history stays clean, secrets stay out, and every change enters through a
reviewed, tested path.

## Why It Matters

The repository is the project's source of truth. Get its structure wrong and the
damage compounds: a leaked secret in history is exposed forever, a mis-set default
branch breaks everyone's clones, an unprotected `main` lets a bad force-push erase
work. Repository configuration is not cosmetic — it is where you encode the rules
that keep a codebase safe and reviewable at scale, before any feature code is
written.

## Core Principles

- **History is append-only and public-forever in spirit.** Anything committed —
  especially a secret — must be treated as permanently exposed. Rewriting history
  on a shared branch is a last resort, never a routine tool.
- **`main` is protected, not a scratchpad.** The default branch changes only through
  reviewed PRs that pass required checks. Direct pushes are disabled.
- **Configuration lives in the repo.** `README`, `LICENSE`, `.gitignore`,
  `CODEOWNERS`, and CI workflows are versioned files, so the rules travel with the
  code and are themselves reviewable.
- **Least-visibility by default.** New repositories start private; visibility is
  widened deliberately, never by accident.
- **A repository does one thing.** Prefer a focused repo (or a well-structured
  monorepo with clear ownership) over a junk-drawer that mixes unrelated projects.

## Best Practices

- Set a protected default branch and require PRs + passing status checks to merge.
  See [branch protection](17-branch-protection.md) and [rulesets](18-rulesets.md).
- Add a `.gitignore` before the first commit so build artifacts, `.env`, and
  credentials never enter history in the first place.
- Add a `CODEOWNERS` file so the right reviewers are auto-requested; pair it with
  "require review from Code Owners" in protection rules.
- Include `README.md` (what/why/how to run), `LICENSE` (legal reuse terms), and a
  `SECURITY.md` (how to report vulnerabilities) at the root.
- Enable [secret scanning](16-secret-scanning.md) with push protection and
  [Dependabot](15-dependabot.md) at creation time, not after an incident.
- Choose a squash-or-rebase merge policy deliberately and disable the merge methods
  you do not use, so history style stays consistent.
- Archive a dead repository (read-only) instead of deleting it, preserving history
  and links.

## Examples

**Good Example** — a `.gitignore` that keeps secrets and noise out of history

```gitignore
# Ignore local environment and secrets BEFORE the first commit, because anything
# committed—even once, even if later deleted—remains recoverable in history forever.
.env
.env.*
*.pem
secrets/

# Ignore build output and dependencies: they are reproducible and bloat clones.
node_modules/
dist/
__pycache__/
```

```
# CODEOWNERS — auto-requests the right reviewers so no PR merges unreviewed.
*                     @acme/maintainers
/infra/               @acme/platform     # infra changes need platform sign-off
/services/billing/    @acme/payments
```

**Bad Example** — secrets committed, everything mixed together

```bash
git init
echo "DB_PASSWORD=hunter2" > .env   # a real secret...
git add .                           # ...staged with everything, no .gitignore
git commit -m "initial commit"      # secret now permanent in history
git push                            # and now public; rotating the credential is
                                    # the ONLY safe remedy—deleting the file won't help
```

## Common Mistakes

- Committing `.env`, keys, or tokens; deleting them later does *not* remove them
  from history — the credential must be rotated.
- Leaving `main` unprotected, allowing direct pushes and force-pushes.
- Creating the repo public when it should be private (irreversible exposure).
- No `CODEOWNERS`, so critical files merge without the right reviewer.
- Renaming or deleting the default branch and breaking every existing clone/PR.
- One giant repo mixing unrelated apps, making ownership and CI impossible to scope.

## Production Tips

- If a secret is committed, rotate it immediately, then optionally scrub history —
  rotation is what protects you, scrubbing is cleanup.
- Store repo configuration (protection, rulesets, labels) as code with a tool like
  Terraform so it is reproducible and auditable.
- Use repository templates to bootstrap new services with protection, CODEOWNERS,
  and CI already wired in.

## AI Review Checklist

- Is a `.gitignore` present that excludes `.env`, keys, and build output?
- Is the default branch protected with required reviews and checks?
- Are `README`, `LICENSE`, and `SECURITY.md` present at the root?
- Is `CODEOWNERS` defined and enforced by protection rules?
- Is visibility set to the least exposure the project needs?
- Are secret scanning and Dependabot enabled?

## Related

- `knowledge/github/01-github-platform.md`
- `knowledge/github/06-pull-requests.md`
- `knowledge/github/17-branch-protection.md`
- `knowledge/github/18-rulesets.md`
- `knowledge/github/13-security.md`
