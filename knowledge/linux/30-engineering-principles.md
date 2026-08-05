---
id: linux/30-engineering-principles
topic: linux
slug: engineering-principles
title: "Linux Engineering Principles"
type: doc
order: 30
status: ready
tags: [linux, engineering-principles, ProtectSystem, NoNewPrivileges, EnvironmentFile, nohup, WantedBy, RestartSec]
related: [linux/26-best-practices, linux/05-permissions, linux/08-systemd, linux/24-scripting, linux/98-production-checklist]
when_to_use: "Read before building, provisioning, or automating any Linux host or service you expect to run in production."
---
# Linux Engineering Principles

## Purpose

This document defines the durable engineering principles for working on Linux
systems: how to design, provision, and operate hosts and services so they are
reproducible, observable, and safe to change. It is the reasoning layer beneath
the how-to docs — [permissions](05-permissions.md), [systemd](08-systemd.md),
[scripting](24-scripting.md) — and it explains *why* those rules exist so an
agent can apply them to situations no single doc covers.

These principles are technology-agnostic within Linux: they hold whether the host
is a bare-metal server, a cloud VM, or a container base image.

## Why It Matters

A Linux host is shared, stateful, and long-lived. A change made by hand at 2am —
an edited config, a loosened permission, a manually installed package — survives
invisibly until it causes an outage nobody can reproduce. The failure mode of
sloppy system work is not an immediate crash; it is *drift*: the running system
silently diverges from what any file, script, or human believes is true. Because
the divergence is invisible and the blast radius is the whole host, Linux
engineering is held to a higher bar than application code. Assume every host will
outlive your memory of how you built it.

## Core Principles

- **Reproducible over clever.** A host must be rebuildable from version-controlled
  config (Ansible, cloud-init, a Containerfile) — not from a person's memory. If
  you cannot destroy and recreate it, you do not understand it.
- **Least privilege by default.** Run services as dedicated non-root users, grant
  the narrowest file permissions and capabilities that work, and add access only
  when a concrete need proves it. Privilege is easy to grant and hard to reclaim.
- **Idempotent operations.** Every script and provisioning step must be safe to
  run twice. Convergence to a desired state beats one-shot commands that assume a
  starting point.
- **Fail loud, fail closed.** A script that hits an error must stop and signal
  failure, not limp forward on bad assumptions. Absent that, corruption compounds.
- **Everything observable.** If a service runs, it must log to a known place and
  expose its health. A process you cannot see is a process you cannot operate.
- **Explicit over implicit state.** Pin versions, name things fully, and avoid
  relying on ambient defaults (current directory, `$PATH`, locale) that differ
  between your shell and the service's.

## Best Practices

- Manage configuration as code and apply it through a tool ([automation](23-automation.md)),
  not by hand-editing files on live hosts. Hand edits create drift no one records.
- Run every service under [systemd](08-systemd.md) with a dedicated `User=`,
  `Restart=on-failure`, and sandboxing directives (`ProtectSystem`, `NoNewPrivileges`).
  The init system, not a `nohup` in a shell, owns process lifecycle.
- Start Bash scripts with `set -euo pipefail` and quote every expansion. An
  unquoted `$var` splits on whitespace and globs — a class of bug that only fires
  on the input you did not test. See [scripting](24-scripting.md).
- Prefer package-managed installs over `curl | bash`. Packages are versioned,
  signed, and removable; a piped script is an unauditable root shell.
- Keep secrets out of the image, the repo, and the environment listing. Load them
  from a secrets manager or a mode-`600` file owned by the service user at runtime.
- Make logs structured and centralized ([logging](15-logging.md)); alert on rates,
  not single lines. Set resource limits so one runaway process cannot starve the host.
- Test changes on an identical staging host built from the same config before
  touching production. "Works on my machine" is a statement about drift.

## Examples

**Good Example** — a service defined declaratively, least-privilege, self-healing

```ini
# /etc/systemd/system/api.service — the host can be rebuilt from this file alone.
[Unit]
Description=Orders API
After=network-online.target

[Service]
User=api                     # dedicated non-root account, not root
ExecStart=/opt/api/bin/api
Restart=on-failure           # systemd, not a human, recovers from crashes
RestartSec=2
NoNewPrivileges=true         # process can never gain privileges via setuid
ProtectSystem=strict         # filesystem is read-only except explicit paths
ReadWritePaths=/var/lib/api
EnvironmentFile=/etc/api/env # secrets in a mode-600 file, not baked into the unit

[Install]
WantedBy=multi-user.target
```

**Bad Example** — imperative, root, unmanaged, invisible

```bash
# Run by hand on the box; nothing records that this happened.
cd /opt/api
sudo ./bin/api &          # root, backgrounded in a shell: dies with the SSH session,
                          # no restart, no logs, no way to reproduce this host
echo "started"            # "success" is assumed, never verified
```

## Common Mistakes

- Configuring live hosts by hand, so no file or repo describes the real state.
- Running services as root because it "just works," expanding every bug's blast radius.
- Writing scripts without `set -euo pipefail`, so failures are swallowed and drift silently.
- Installing software via `curl | sudo bash`, giving an unaudited script root.
- Treating a host as a pet you nurse back to health instead of cattle you can rebuild.
- Emitting no logs or health signal, so the first sign of trouble is a user complaint.

## Production Tips

- Bake "can we rebuild this host from scratch?" into review — periodically prove it.
- Track config drift with a tool that reports diffs between desired and actual state.
- Ship distro security updates on a schedule ([security](17-security.md)); unpatched
  is the most common real-world compromise.
- Keep an out-of-band recovery path (console, rescue user) for when SSH breaks.

## AI Review Checklist

- Can this host or service be rebuilt entirely from version-controlled config?
- Does the service run as a dedicated non-root user with minimal permissions?
- Are all scripts idempotent and started with `set -euo pipefail` and quoted expansions?
- Is process lifecycle owned by systemd with `Restart=` and sandboxing, not a shell?
- Are secrets loaded at runtime from a protected source, never baked in or logged?
- Does every running service log to a known place and expose a health signal?

## Related

- `knowledge/linux/26-best-practices.md`
- `knowledge/linux/05-permissions.md`
- `knowledge/linux/08-systemd.md`
- `knowledge/linux/24-scripting.md`
- `knowledge/linux/98-production-checklist.md`
