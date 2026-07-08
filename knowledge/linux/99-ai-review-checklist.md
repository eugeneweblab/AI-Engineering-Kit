---
id: linux/99-ai-review-checklist
topic: linux
slug: ai-review-checklist
title: "AI Review Checklist"
type: doc
order: 99
status: ready
tags: [linux, ai-review-checklist]
related: [linux/24-scripting, linux/05-permissions, linux/08-systemd, linux/100-common-antipatterns, linux/98-production-checklist]
when_to_use: "Read when reviewing any Linux shell script, systemd unit, permission change, or provisioning code before it merges."
---
# AI Review Checklist

## Purpose

A focused checklist for reviewing Linux changes — shell scripts, systemd units,
permission edits, cron jobs, and provisioning code — before they merge or run.
Each item is a concrete yes/no an agent can verify by reading the diff. This is
the review-time companion to [common-antipatterns](100-common-antipatterns.md)
and the go-live [production-checklist](98-production-checklist.md).

## Why It Matters

Linux mistakes are cheap to make and expensive to catch in production: an unquoted
variable that deletes the wrong directory, a `chmod 777` that opens a hole, a
service that runs as root. These are all visible in the diff — if the reviewer
knows what to look for. This checklist encodes that pattern-matching so review
catches the class of bug, not just the one instance.

## Shell Scripts

- [ ] Does the script begin with `set -euo pipefail` (or documented equivalents)?
- [ ] Is every variable expansion quoted (`"$var"`, `"${arr[@]}"`) to prevent word-splitting and globbing?
- [ ] Are `rm -rf`, `mv`, and redirects guarded against empty/unset paths (e.g. `rm -rf "${dir:?}"`)?
- [ ] Is the exit status of critical commands checked, rather than assuming success?
- [ ] Does it avoid parsing `ls` output and use globs or `find -print0 | xargs -0` instead?
- [ ] Is the script idempotent — safe to run twice without duplicating or corrupting state?
- [ ] Are absolute paths or a pinned `$PATH` used, not reliance on the caller's working directory?

## Permissions & Ownership

- [ ] Are new files given the least permission that works — never `777` or `666`? ([permissions](05-permissions.md))
- [ ] Are secret files mode `600`/`640` and owned by the service user, not world-readable?
- [ ] Does the change avoid `chmod -R` / `chown -R` on broad trees like `/` or `$HOME`?
- [ ] Are setuid/setgid bits justified, or removed if not strictly required?

## Services & systemd

- [ ] Does the unit run as a dedicated non-root `User=`, not root? ([systemd](08-systemd.md))
- [ ] Are `Restart=` and a start condition set so the service self-heals and starts on boot?
- [ ] Are sandboxing directives (`NoNewPrivileges`, `ProtectSystem`, `ReadWritePaths`) applied where feasible?
- [ ] Are secrets loaded via `EnvironmentFile=` (mode 600), not inline in the unit or the repo?

## Scheduled Jobs & Automation

- [ ] Do cron/systemd-timer jobs redirect output somewhere, so failures are not silently mailed into the void?
- [ ] Is a lock (`flock`) used to prevent overlapping runs of the same job?
- [ ] Does provisioning code converge to a desired state (idempotent), not run one-shot imperative commands?

## Safety & Secrets

- [ ] Are there no hardcoded passwords, tokens, or keys in scripts, units, or history?
- [ ] Does the change avoid piping remote content straight into a root shell (`curl | sudo bash`)?
- [ ] Are destructive operations logged and, where irreversible, gated behind an explicit confirmation or dry-run?
- [ ] Is user-supplied input never interpolated unescaped into a shell command (injection)?

## Observability

- [ ] Does the change keep the service logging to a known place with bounded retention?
- [ ] Will a failure surface as an alertable signal (non-zero exit, log line, metric), not silence?

## Related

- `knowledge/linux/24-scripting.md`
- `knowledge/linux/05-permissions.md`
- `knowledge/linux/08-systemd.md`
- `knowledge/linux/100-common-antipatterns.md`
- `knowledge/linux/98-production-checklist.md`
