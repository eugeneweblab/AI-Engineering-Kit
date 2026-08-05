---
id: linux/13-environment
topic: linux
slug: environment
title: "Linux Environment"
type: doc
order: 13
status: ready
tags: [linux, environment, systemd, cron, DATABASE_URL, EnvironmentFile, child, bash]
related: [linux/02-shell, linux/03-bash, linux/08-systemd, linux/24-scripting]
when_to_use: "Read before passing configuration or secrets to a process, or debugging why a variable is unset at runtime."
---
# Linux Environment

## Purpose

This document defines how the process environment works on Linux — environment
variables, where they are set, how they are inherited, and how to pass configuration and
secrets to a program correctly. It is written so an agent can wire up configuration
without leaking secrets or shipping a service that works in the shell but fails under
`systemd` or in a container.

## Why It Matters

The environment is the most common channel for configuration, and the most common place
secrets leak. A variable set in an interactive shell is invisible to a service manager;
a variable printed in a log or baked into an image is exposed forever. Environment bugs
are confusing because they depend on *who* started the process and *how* — the same
binary behaves differently under `bash`, `cron`, `systemd`, and Docker. Getting this
right removes a whole class of "works on my machine" failures.

## Core Principles

- **The environment is inherited, not global.** A child process gets a copy of its
  parent's environment at exec time. Setting a variable after a child starts does not
  reach it, and a child cannot change its parent's environment.
- **Interactive shell config is not runtime config.** `~/.bashrc` and `~/.profile` run
  for login/interactive shells only. `cron`, `systemd`, and containers do not source
  them, so anything a service needs must be set where the service is defined.
- **Secrets in the environment are readable.** Any process can read its own environment;
  a set variable can appear in `/proc/<pid>/environ`, crash dumps, and child processes.
  Treat env secrets as a convenience, not a vault.
- **Config comes from the environment; defaults come from code.** Read config once at
  startup, validate it, and fail fast if a required variable is missing.
- **Export or it is invisible.** An unexported shell variable is local to that shell and
  never reaches a child process.

## Best Practices

- Distinguish shell variables (`FOO=bar`) from environment variables (`export FOO=bar`).
  Only exported variables are inherited by child processes.
- Set service configuration in the unit's `Environment=`/`EnvironmentFile=`, or the
  container's env, not in a developer's dotfiles.
- Load `.env` files with a real loader in the app, and keep `.env` out of version control
  (`.gitignore`). It is for local development, not production secrets.
- Validate required variables at startup and exit non-zero with a clear message if one is
  missing — do not let an empty string silently become a bad default.
- Namespace your variables (`MYAPP_DB_URL`, not `DB_URL`) to avoid collisions with the
  many variables the OS and other tools already define.
- Prefer secret managers or `systemd` `LoadCredential=` for real secrets; pass the path,
  not the value, when you can.

## Examples

**Good Example** — explicit, validated, per-service configuration

```bash
#!/usr/bin/env bash
set -euo pipefail

# Require the variable; fail loudly instead of running with a wrong default.
: "${DATABASE_URL:?DATABASE_URL is required}"

# Export so the child (the app) actually inherits it.
export DATABASE_URL
exec /usr/local/bin/myapp
```

```ini
# myapp.service — systemd does NOT read ~/.bashrc, so config lives here.
[Service]
EnvironmentFile=/etc/myapp/env   # 0640, owned by the service user
ExecStart=/usr/local/bin/myapp
```

**Bad Example** — relies on shell config the service never sees

```bash
# In ~/.bashrc — works when you test by hand, invisible to systemd/cron/docker.
DATABASE_URL=postgres://localhost/app   # not exported → child never sees it
export API_KEY=sk_live_hardcoded_secret # secret in a tracked dotfile → leaked
myapp   # if DATABASE_URL is empty, app starts with a broken default and no error
```

## Common Mistakes

- Setting variables in `~/.bashrc` and expecting `cron` or `systemd` jobs to see them.
- Forgetting `export`, so a variable is set in the shell but absent in the child process.
- Committing a `.env` file with real secrets to git.
- Echoing the environment in a debug log or CI output, leaking secrets to log storage.
- Treating an empty/unset variable as a valid default instead of failing fast.
- Assuming `PATH` is the same under `cron` (minimal) as in your login shell; use absolute
  paths in scheduled jobs.

## Production Tips

- Audit `/proc/<pid>/environ` expectations: anything sensitive there is visible to root
  and to anyone who can read the process. Prefer file-based credentials with tight modes.
- Keep `EnvironmentFile` at mode `0640`, owned by the service account, out of world-read
  paths.
- Log the *names* of loaded config keys at startup (never the values) so misconfiguration
  is diagnosable without leaking secrets.

## AI Review Checklist

- Are variables the service needs set where the service actually runs (unit/container),
  not only in a dotfile?
- Are variables `export`ed so child processes inherit them?
- Are required variables validated at startup with a fail-fast error?
- Is `.env` gitignored, and are real secrets kept out of tracked files?
- Do scheduled jobs use absolute paths instead of relying on an inherited `PATH`?
- Is the environment never printed to logs or CI output?

## Related

- `knowledge/linux/02-shell.md`
- `knowledge/linux/03-bash.md`
- `knowledge/linux/08-systemd.md`
- `knowledge/linux/24-scripting.md`
