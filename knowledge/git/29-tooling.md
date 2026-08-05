---
id: git/29-tooling
topic: git
slug: tooling
title: "Git Tooling"
type: doc
order: 29
status: ready
tags: [git, tooling]
related: [git/20-hooks, git/02-installation, git/27-best-practices, git/17-conflict-resolution, git/28-security]
when_to_use: "Read before configuring Git aliases, hooks, diff/merge tools, or CI integrations for a repo or team."
---
# Git Tooling

## Purpose

This document defines the tooling around Git that makes it safe and productive at scale:
configuration, aliases, hook managers, diff/merge tools, and CI integrations. It is
written so an agent can set up an ergonomic, consistent Git environment without
introducing surprises or hidden footguns.

Tooling is what turns raw Git commands into a repeatable workflow. The mechanics live in
[hooks](20-hooks.md) and [installation](02-installation.md); this document is about
*choosing and wiring* tools so the whole team gets the same behavior.

## Why It Matters

Git's defaults are conservative and machine-local, so two developers on the same repo can
behave differently — different line endings, different merge conflict styles, different
hooks — and produce inconsistent, noisy history. Tooling closes that gap by moving
configuration and enforcement *into the repository*, where everyone shares it. It also
prevents whole classes of mistakes automatically: a hook manager runs the linter before
every commit, so nobody has to remember. The risk is the opposite — opaque tooling (a
magic alias, a global hook) that changes what a command does can be more dangerous than no
tooling, because the surprise is invisible.

## Core Principles

- **Share config through the repo, not private dotfiles.** Line endings, hooks, and merge
  settings that live in the repo (`.gitattributes`, a committed hook manager config) give
  every clone identical behavior.
- **Enforce, do not merely suggest.** A hook manager (pre-commit, Husky, Lefthook) that
  every clone installs beats a wiki page nobody reads.
- **Aliases must not hide danger.** An alias may shorten a safe command; it must never
  silently make a destructive one (force-push, hard reset) easy or ambiguous.
- **Tools augment Git; they do not replace understanding.** A GUI or wrapper is fine, but
  the underlying commands must remain legible for debugging.
- **Configuration is layered.** System < global < repo-local < command flag. Know which
  layer a setting lives in before changing it.

## Best Practices

- Set safe global defaults once: `git config --global pull.rebase true`,
  `init.defaultBranch main`, `push.autoSetupRemote true`, and
  `merge.conflictStyle zdiff3` for clearer [conflict](17-conflict-resolution.md) markers.
- Normalize line endings in a committed `.gitattributes` (`* text=auto`), not per-machine
  `core.autocrlf`, so cross-OS teams do not churn diffs.
- Manage hooks with a tool that installs on clone (Lefthook, pre-commit, Husky) and points
  `core.hooksPath` at a committed directory — otherwise hooks live only in `.git/` and
  ship to no one.
- Add short, read-only aliases (`git lg` for a graph log); keep destructive operations
  spelled out so they are deliberate.
- Wire the same checks (format, lint, secret scan, tests) into both hooks and CI, so a
  local bypass is still caught server-side.
- Use `git maintenance start` to schedule background gc/commit-graph upkeep on large repos.

## Examples

**Good Example** — repo-shared, enforced tooling

```bash
# Committed .gitattributes normalizes line endings for everyone.
echo "* text=auto" > .gitattributes

# Lefthook config (committed) runs checks that install on clone.
cat > lefthook.yml <<'EOF'
pre-commit:
  parallel: true
  commands:
    lint:   { run: npm run lint }
    secrets: { run: gitleaks protect --staged --redact }
EOF
git config core.hooksPath .lefthook   # hooks path lives in the repo, not just .git/

# Safe, readable alias — shortens a non-destructive command only.
git config --global alias.lg "log --oneline --graph --decorate"
```

**Bad Example** — a hidden, destructive alias

```bash
# Alias silently makes a shared-history-destroying command trivial to fire.
git config --global alias.sync "!git reset --hard origin/main && git push --force"

# A teammate runs `git sync` expecting a pull; it discards their work AND
# force-pushes over main. The danger is invisible at the call site.
```

## Common Mistakes

- Keeping hooks only in `.git/hooks/`, so they never reach other clones.
- Relying on per-machine `core.autocrlf` instead of a committed `.gitattributes`, causing
  cross-OS line-ending churn.
- Aliases that wrap destructive commands (`push --force`, `reset --hard`) behind an
  innocent name.
- Configuring checks only in hooks, which `--no-verify` bypasses, with no CI backstop.
- Assuming a GUI's "sync" or "update" button maps to a known Git command — it may rebase,
  merge, or force-push unpredictably.
- Editing the wrong config layer (global vs repo-local) and not understanding why a setting
  did not take effect.

## Production Tips

- Vendor a bootstrap script (`make setup` or `npm run prepare`) that installs the hook
  manager and applies repo config, so a fresh clone is correct with one command.
- Pin tool versions (hook manager, scanners) so every environment runs the same checks.
- Mirror hook checks exactly in CI; treat CI as the source of truth and hooks as fast local
  feedback.
- Audit global aliases periodically — they follow a developer across every repo and are an
  easy place for a footgun to hide.

## AI Review Checklist

- Are hooks managed by a tool that installs on clone, via a committed `core.hooksPath`?
- Are line endings normalized in `.gitattributes` rather than per-machine config?
- Do aliases wrap only safe commands, never hidden destructive ones?
- Are lint/secret/test checks mirrored in both hooks and CI?
- Is shared Git config committed to the repo so all clones behave identically?
- Is there a one-command bootstrap that applies the tooling to a fresh clone?

## Related

- `knowledge/git/20-hooks.md`
- `knowledge/git/02-installation.md`
- `knowledge/git/27-best-practices.md`
- `knowledge/git/17-conflict-resolution.md`
- `knowledge/git/28-security.md`
