---
id: linux/03-bash
topic: linux
slug: bash
title: "Bash"
type: doc
order: 3
status: ready
tags: [linux, bash]
related: [linux/02-shell, linux/01-filesystem, linux/00-overview, linux/05-permissions, linux/04-users-and-groups]
when_to_use: "Read before writing or reviewing any Bash script that runs in CI, deploys, or automation."
---
# Bash

## Purpose

This document defines how to write correct, safe Bash *scripts* — as opposed to
interactive commands, which are covered in [shell](02-shell.md). It covers the strict
mode preamble, quoting discipline, functions, error handling, and the boundary at which
you should stop writing Bash and use a real programming language.

Bash is the default automation glue on Linux: entrypoints, deploy scripts, CI steps, and
health checks. This doc makes those scripts fail loudly and behave predictably.

## Why It Matters

Bash's defaults are hostile to reliability. By default a script keeps running after a
command fails, treats an unset variable as an empty string, and lets the failure of any
stage in a pipeline be hidden by the last stage's success. A deploy script that "worked"
may have silently skipped the build and shipped stale code. Because these scripts often
run as `root` in production during the riskiest moments (deploys, migrations), a silent
failure or an unquoted path can corrupt data or brick a host. Strict mode and quoting
turn silent, dangerous behavior into loud, safe behavior.

## Core Principles

- **Fail fast, fail loud.** Start every script with `set -euo pipefail`. Without it,
  errors are swallowed and the script marches on with bad state.
- **Quote everything.** An unquoted expansion is a latent bug that triggers the first
  time a value contains a space, glob, or newline. See [shell](02-shell.md).
- **A script is a program.** It deserves functions, a `main`, `local` variables, and
  input validation — not a flat wall of commands.
- **Idempotent and re-runnable.** Automation reruns after partial failures; a correct
  script produces the same end state whether run once or three times.
- **Know when to quit Bash.** Past ~100 lines, or when you need data structures,
  arithmetic, or JSON, Bash becomes a liability. Switch to Python or Go.

## Best Practices

- Begin with `#!/usr/bin/env bash` and `set -euo pipefail`; add `IFS=$'\n\t'` to tame
  word splitting.
- Declare function-scoped variables with `local`; a bare assignment is global and leaks
  between functions.
- Use `readonly` / `declare -r` for constants and `"${VAR:?message}"` to require a
  variable to be set, failing with a clear message if not.
- Wrap cleanup in `trap '...' EXIT` so temp files and locks are released even on error.
- Prefer `[[ ... ]]`, `(( ... ))` for tests and arithmetic; they are safer and clearer
  than `[ ]` and `expr`.
- Check that required tools exist (`command -v jq >/dev/null || die "jq required"`)
  before using them, so the script fails with a message, not a cryptic "not found".
- Lint every script with `shellcheck` in CI; it catches the majority of quoting and
  logic bugs mechanically.
- Never pipe untrusted input into `bash`, `eval`, or `sh -c`. Pass data as arguments.

## Examples

**Good Example** — strict mode, functions, cleanup, validation

```bash
#!/usr/bin/env bash
set -euo pipefail          # -e: exit on error, -u: unset var is error,
                           # -o pipefail: a failed pipe stage fails the pipeline
IFS=$'\n\t'

die() { echo "error: $*" >&2; exit 1; }

main() {
  local src=${1:?usage: deploy.sh <src-dir>}   # require an argument, clear message
  [[ -d "$src" ]] || die "not a directory: $src"

  local tmp; tmp="$(mktemp -d)"
  trap 'rm -rf -- "$tmp"' EXIT                  # cleanup runs even if we fail below

  rsync -a --delete -- "$src"/ "$tmp"/          # quoted paths, -- ends options
  echo "staged $(find "$tmp" -type f | wc -l) files"
}

main "$@"
```

**Bad Example** — no strict mode, unquoted, no cleanup

```bash
#!/bin/bash
SRC=$1                       # no validation; empty if unset, and unquoted below
cd $SRC                      # unquoted; if cd fails, script CONTINUES in wrong dir
TMP=/tmp/deploy              # predictable name, never cleaned up
rsync -a $SRC/ $TMP/         # unquoted paths break on spaces; no error if rsync fails
rm -rf $TMP/*                # runs even after a failed rsync → deletes wrong thing
```

## Common Mistakes

- Omitting `set -euo pipefail`, so a failed command silently continues.
- Relying on `cd dir` without `|| exit` under non-strict mode; the rest of the script
  then runs in the wrong directory.
- Global variables leaking between functions because `local` was not used.
- `pipefail` missing, so `false | true` reports success and masks the real failure.
- Building filenames or commands by string concatenation instead of arrays
  (`cmd=(rsync -a "$src" "$dst"); "${cmd[@]}"`).
- Growing a Bash script into a 500-line program with nested state that should be Python.
- Skipping `shellcheck`, then shipping a quoting bug that only fires on odd input.

## Production Tips

- Make scripts idempotent: check-before-create (`mkdir -p`, `id -u user || useradd`) so
  a rerun after failure converges instead of erroring or duplicating work.
- Guard concurrent runs with `flock` on a lockfile so cron overlaps do not corrupt state.
- Log to stderr with timestamps and exit non-zero on failure so the caller (CI, systemd,
  cron) can detect and alert.
- Pin behavior: prefer explicit tool paths or `command -v` checks over assuming GNU vs
  BSD flag variants across distros.

## AI Review Checklist

- Does the script start with `#!/usr/bin/env bash` and `set -euo pipefail`?
- Is every expansion quoted, and are arrays used for building argument lists?
- Are function variables `local`, and are required inputs validated with `:?`?
- Is cleanup handled via `trap ... EXIT`, and are temp dirs from `mktemp`?
- Is `cd` (and every critical command) guarded so failure stops the script?
- Is the script idempotent and safe to rerun after a partial failure?
- Does it pass `shellcheck`, and is untrusted input kept out of `eval`/`sh -c`?

## Related

- `knowledge/linux/02-shell.md`
- `knowledge/linux/01-filesystem.md`
- `knowledge/linux/00-overview.md`
- `knowledge/linux/05-permissions.md`
- `knowledge/linux/04-users-and-groups.md`
