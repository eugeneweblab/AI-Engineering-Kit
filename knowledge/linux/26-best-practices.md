---
id: linux/26-best-practices
topic: linux
slug: best-practices
title: "Best Practices"
type: doc
order: 26
status: ready
tags: [linux, best-practices]
related: [linux/05-permissions, linux/24-scripting, linux/17-security, linux/23-automation, linux/30-engineering-principles]
when_to_use: "Read before operating on a Linux host or reviewing shell/ops work, to apply the habits that prevent avoidable outages."
---
# Best Practices

## Purpose

This document collects the cross-cutting habits that make Linux work safe and
repeatable: least privilege, idempotence, config as code, and thinking before
running a destructive command. These are the defaults every other doc in this
topic assumes, gathered in one place so an agent can apply them without
rediscovering each one.

Where individual docs go deep on a subject — [permissions](05-permissions.md),
[scripting](24-scripting.md), [security](17-security.md) — this doc is the short
list of principles that cut across all of them.

## Why It Matters

On Linux there is no undo. `rm` does not go to a trash can, `dd` writes straight
to a block device, and a command run as `root` trusts you completely. Most
serious incidents are not exotic attacks — they are a well-meaning operator
running the right command in the wrong place, or a script that assumed a
variable was set. Good practice is cheap insurance: quoting, `--dry-run`,
least privilege, and version-controlled config each cost seconds and prevent
outages that cost hours. Habits scale; heroics do not.

## Core Principles

- **Least privilege always.** Use the lowest privilege that works. Reach for
  `sudo` for a single command, never a root login shell for routine work.
- **Idempotence over imperative steps.** Prefer commands and configs that produce
  the same end state no matter how many times they run.
- **Config as code.** Every host change lives in version control (Ansible, unit
  files, dotfiles) — not typed once into a terminal and forgotten.
- **Think before destructive commands.** `rm`, `dd`, `mkfs`, `chmod -R`, and `>`
  are irreversible. Preview with `--dry-run`, `echo`, or `ls` first.
- **Explicit over clever.** A readable command someone can review beats a terse
  pipeline only the author understands. Ops code is read far more than written.

## Best Practices

- Work as a normal user; escalate per-command with `sudo`. A persistent root
  shell makes every typo catastrophic and every action unattributable.
- Preview destructive operations: `rsync --dry-run`, `find ... -print` before
  `-delete`, and read what a glob expands to before `rm` acts on it.
- Pin and document versions — package versions, base images, tool versions — so a
  host rebuilt next year behaves like the one built today.
- Prefer absolute paths and explicit flags in scripts and cron; the environment
  you test in is not the environment cron runs in — see [environment](13-environment.md).
- Set restrictive `umask` (027 for service accounts) and default-deny permissions;
  grant access explicitly rather than opening wide and clawing back.
- Keep changes small and reversible: one change, verify, then the next. Batched
  changes make it impossible to tell which one broke production.
- Automate anything done more than twice, but only after you can do it correctly
  by hand — automating a broken procedure just breaks faster.

## Examples

**Good Example** — least privilege, previewed, explicit

```bash
# escalate for exactly one command, not a root shell
sudo systemctl restart api.service

# preview what will be deleted before deleting anything
find /var/cache/app -type f -mtime +7 -print       # inspect the list first
find /var/cache/app -type f -mtime +7 -delete      # only then act

# sync with a dry run to confirm the plan
rsync -a --delete --dry-run ./build/ /srv/www/      # shows adds/deletes, changes nothing
```

**Bad Example** — root shell, unguarded, irreversible

```bash
sudo -i                                   # persistent root: every later typo is fatal
cd /var/cache/app
rm -rf ./*                                # no preview; wrong cwd deletes the wrong tree
rsync -a --delete ./build/ /srv/www/      # --delete with no dry run wipes unexpected files
chmod -R 777 /srv/www                     # world-writable "fix" opens a security hole
```

## Common Mistakes

- Living in a root shell (`sudo -i`) so mistakes are unattributable and unrecoverable.
- Running `rm -rf`, `chmod -R`, or `rsync --delete` without previewing the target set.
- `chmod 777` as a quick fix, silently making files world-writable.
- Making changes directly on hosts instead of in version-controlled config, so the
  next rebuild loses them.
- Assuming the cron/systemd environment matches your interactive shell (`PATH`, cwd,
  locale) — it does not.
- Batching many changes at once, making it impossible to bisect what broke.

## Production Tips

- Alias or wrap dangerous commands with confirmations in operator shells, but never
  rely on aliases inside scripts — scripts must be explicit.
- Record intent in commit messages and change tickets; the "why" is what the next
  responder needs, and it is never in the shell history.
- Review [engineering principles](30-engineering-principles.md) for the reasoning
  discipline these habits encode.

## AI Review Checklist

- Does the work use per-command `sudo` rather than a persistent root shell?
- Are destructive commands (`rm`, `dd`, `--delete`) previewed before they run?
- Are permissions default-deny, with no `777` or overly broad grants?
- Do host changes live in version-controlled config rather than ad-hoc commands?
- Are scripts explicit about `PATH`, cwd, and flags rather than assuming the shell env?
- Are changes small, reversible, and applied one at a time?

## Related

- `knowledge/linux/05-permissions.md`
- `knowledge/linux/24-scripting.md`
- `knowledge/linux/17-security.md`
- `knowledge/linux/23-automation.md`
- `knowledge/linux/30-engineering-principles.md`
