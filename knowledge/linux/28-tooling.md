---
id: linux/28-tooling
topic: linux
slug: tooling
title: "Linux Tooling"
type: doc
order: 28
status: ready
tags: [linux, tooling, netstat, ifconfig, htop, curl, port, vmstat]
related: [linux/02-shell, linux/19-debugging, linux/16-monitoring, linux/24-scripting, linux/18-performance]
when_to_use: "Read when choosing which command-line tool to reach for on Linux, or reviewing which tool a script or diagnosis relies on."
---
# Linux Tooling

## Purpose

This document maps the standard Linux command-line toolset to the jobs it does:
inspecting processes, files, networks, and performance, and the text-processing
tools that glue them together. The goal is that an agent reaches for the right,
portable tool the first time and knows which are safe to assume everywhere.

It is a companion to [debugging](19-debugging.md), [monitoring](16-monitoring.md),
and [performance](18-performance.md), which use these tools; this doc is about
*choosing* the tool and using it correctly.

## Why It Matters

Picking the wrong tool wastes time and produces fragile automation. Parsing
`ls` output breaks on filenames with spaces; grepping `ps aux | grep foo`
matches the grep itself; assuming `htop` or `jq` is installed makes a script
fail on a minimal container. Knowing which tools are POSIX-guaranteed versus
which are nice-to-have determines whether your script runs on a stripped-down
production image or only on your workstation. The right tool, used with the
right flags, turns a brittle guess into a reliable, composable command.

## Core Principles

- **Right tool for the layer.** Process (`ps`, `top`), network (`ss`, `ip`),
  files (`find`, `stat`), performance (`iostat`, `vmstat`). Match the tool to the
  question instead of forcing one favorite.
- **Prefer machine-readable output.** Use `--json`, `-0`/`-print0`, and stable
  flags over scraping human-formatted output that changes between versions.
- **Know the portable baseline.** POSIX tools (`grep`, `sed`, `awk`, `find`, `ps`)
  exist everywhere; `jq`, `rg`, `htop`, `bat` do not. Depend on extras only when
  you control the environment.
- **Compose, do not reinvent.** Small tools piped together beat a bespoke script;
  each tool does one thing and reads stdin, writes stdout.
- **Modern replacements are opt-in.** `ss` over `netstat`, `ip` over `ifconfig`,
  `journalctl` over tailing files — use the current tool; keep the legacy one in
  mind for old hosts.

## Best Practices

- Use `ss -tulpn` instead of the deprecated `netstat` to list listening sockets;
  `ip a`/`ip r` instead of `ifconfig`/`route`.
- Never parse `ls`; use `find` with `-print0` piped to `xargs -0`, or globs, to
  handle spaces and newlines in filenames safely.
- Match processes with `pgrep -f pattern` / `pkill` instead of `ps aux | grep`,
  which matches its own grep and returns the wrong PID.
- Reach for `awk` for column extraction and arithmetic, `sed` for line edits, and
  `grep -E`/`rg` for search — do not chain five `cut`/`tr` calls where one `awk` fits.
- Use `jq` for JSON and `yq` for YAML rather than regex; but guard scripts that
  need them (`command -v jq >/dev/null || { echo "need jq" >&2; exit 1; }`).
- Prefer `curl -fsS` for HTTP checks: `-f` fails on HTTP errors, `-sS` is quiet but
  still shows real errors. Bare `curl` returns exit 0 on a 500.
- Check a tool exists before depending on it in automation, and document the
  package that provides it.

## Examples

**Good Example** — right tools, safe parsing, guarded dependencies

```bash
# find a listening service on a port (modern tool, machine-parseable)
ss -tulpn 'sport = :8080'

# find the PID of a process without matching the grep itself
pgrep -f 'api --serve'

# iterate files safely even with spaces/newlines in names
find /var/log -name '*.log' -mtime +7 -print0 | xargs -0 gzip

# parse JSON with the right tool, but fail clearly if it is missing
command -v jq >/dev/null || { echo "jq required" >&2; exit 1; }
curl -fsS https://api.local/health | jq -r '.status'   # -f fails on HTTP 5xx
```

**Bad Example** — deprecated tools, fragile parsing, silent failure

```bash
netstat -tulpn | grep 8080        # deprecated; may be absent on new hosts
ps aux | grep api | awk '{print $2}'   # matches the grep line -> wrong PID
for f in $(ls /var/log/*.log); do gzip "$f"; done   # breaks on spaces in names
curl https://api.local/health | grep ok   # bare curl exits 0 even on HTTP 500
```

## Common Mistakes

- Parsing `ls` or `ps aux | grep`, both of which break on edge cases (spaces,
  self-matching) and silently return wrong results.
- Using deprecated `netstat`/`ifconfig` that may not be installed on modern minimal images.
- Assuming `jq`, `htop`, `rg`, or `bat` exist in production containers without checking.
- Bare `curl` in health checks, which returns exit 0 on server errors — always use `-f`.
- Chaining many `cut`/`tr`/`sed` calls where a single `awk` program is clearer and faster.
- Ignoring `-print0`/`xargs -0`, so pipelines fail on filenames with whitespace.

## Production Tips

- Standardize a minimal toolset in your base images and document it, so scripts can
  rely on a known set instead of probing at runtime.
- Prefer tools that emit stable, versioned output (JSON) for anything an automation
  or [monitoring](16-monitoring.md) pipeline consumes.
- For interactive investigation, richer tools (`htop`, `btop`, `dust`, `procs`) are
  fine; keep scripts on the portable baseline so they run anywhere.

## AI Review Checklist

- Does the code use `ss`/`ip` rather than deprecated `netstat`/`ifconfig`?
- Are filenames handled with `-print0`/globs instead of parsing `ls`?
- Are processes matched with `pgrep`/`pkill` instead of `ps | grep`?
- Do health checks use `curl -f` so HTTP errors become nonzero exits?
- Are non-baseline tools (`jq`, `rg`) guarded with an existence check?
- Is output machine-readable where an automation consumes it?

## Related

- `knowledge/linux/02-shell.md`
- `knowledge/linux/19-debugging.md`
- `knowledge/linux/16-monitoring.md`
- `knowledge/linux/24-scripting.md`
- `knowledge/linux/18-performance.md`
