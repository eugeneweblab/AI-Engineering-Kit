---
id: linux/24-scripting
topic: linux
slug: scripting
title: "Scripting"
type: doc
order: 24
status: ready
tags: [linux, scripting]
related: [linux/03-bash, linux/02-shell, linux/23-automation, linux/14-cron, linux/19-debugging]
when_to_use: "Read before writing or reviewing any shell script that runs unattended, in CI, or on production hosts."
---
# Scripting

## Purpose

This document defines how to write shell scripts that fail loudly, run safely,
and behave the same on a developer laptop and a production host. It covers the
non-negotiable header, quoting, error handling, and input validation that
separate a throwaway one-liner from a script you can schedule on a fleet.

Scripting here means POSIX `sh` and Bash. When logic outgrows a few hundred
lines, or needs data structures, tests, or error types, stop scripting and
reach for Python — see [automation](23-automation.md) for that boundary.

## Why It Matters

A shell script is code that runs as a real user, often as `root`, with no type
checker, no compiler, and word-splitting that turns an unquoted variable into a
different command. The classic `rm -rf "$DIR/"` where `$DIR` is empty deletes
`/`. Failures are silent by default: a pipeline reports success even when the
first command died. Because scripts glue together the operations that back up,
deploy, and clean up systems, a subtle bug does not throw an exception — it
quietly destroys data or exits 0 while doing nothing. Treat every script that
runs unattended as production software.

## Core Principles

- **Fail fast and loud.** Set strict mode at the top so an unset variable, a
  failed command, or a broken pipe aborts the script instead of continuing on
  corrupt state.
- **Quote everything.** Every `$var` and `$(cmd)` expansion is quoted unless you
  have a specific, commented reason not to. Unquoted expansion is the root cause
  of most shell bugs.
- **Validate before you act.** Check that inputs, files, and directories exist
  and are what you expect *before* running a destructive command.
- **Make it idempotent.** Running the script twice must be safe. Re-running is
  how humans and schedulers recover from partial failures.
- **Be explicit and portable.** Use `#!/usr/bin/env bash`, prefer long flags in
  scripts (`--recursive` over `-r`), and do not rely on interactive shell config.

## Best Practices

- Start every Bash script with `set -euo pipefail` and `IFS=$'\n\t'`. This aborts
  on error, on undefined variables, and on any failing command in a pipeline.
- Run `shellcheck` in CI and fix every warning; it catches quoting and portability
  bugs that only surface at runtime under specific inputs.
- Use `"${var:?message}"` to require a variable and `"${var:-default}"` to supply
  a fallback, instead of assuming a variable is set.
- Quote command substitutions and use arrays for argument lists:
  `cmd "${args[@]}"`, never `cmd $args`.
- Trap errors and clean up: `trap 'rm -f "$tmp"' EXIT` guarantees temp files are
  removed even on failure. Create temp files with `mktemp`, never fixed paths in `/tmp`.
- Send diagnostics to stderr (`echo "..." >&2`) and reserve stdout for real output
  so the script composes in a pipeline.
- Prefer `[[ ... ]]` over `[ ... ]` in Bash; it does not word-split and supports
  pattern matching. Use `$(( ))` for arithmetic, never `expr`.

## Examples

**Good Example** — strict mode, quoting, validation, cleanup

```bash
#!/usr/bin/env bash
set -euo pipefail                       # abort on error, unset var, or broken pipe
IFS=$'\n\t'                             # split only on newline/tab, not spaces

src="${1:?usage: backup.sh <src-dir>}"  # required arg; clear message if missing
[[ -d "$src" ]] || { echo "not a dir: $src" >&2; exit 1; }  # validate before acting

tmp="$(mktemp -d)"                      # unique temp dir, never a fixed name
trap 'rm -rf "$tmp"' EXIT               # cleanup runs even if the script fails

tar -czf "$tmp/backup.tgz" -C "$src" .  # quoted paths survive spaces and globs
mv "$tmp/backup.tgz" "/var/backups/$(date +%F).tgz"
```

**Bad Example** — no strict mode, unquoted, silently destructive

```bash
#!/bin/bash
DIR=$1                                  # unset if no arg is passed; no check
cd $DIR                                 # unquoted: word-splits on spaces
                                        # if cd fails, script keeps going...
rm -rf *                               # ...and deletes the current dir instead
tar czf /tmp/backup.tgz .              # fixed temp path: races and clobbers
# no `set -e`: any failure above is ignored, script still exits 0
```

## Common Mistakes

- Omitting `set -euo pipefail`, so a failed command mid-script leaves partial state.
- Leaving variables unquoted, causing word-splitting and glob expansion on input.
- `cd "$dir" && rm -rf .` without checking the `cd` succeeded — a failed `cd` runs
  the destructive command in the wrong directory.
- Parsing `ls` output instead of using globs or `find -print0` with `read -d ''`.
- Fixed temp paths (`/tmp/build`) that race between concurrent runs and can be hijacked.
- Silencing errors with `2>/dev/null` and no exit-code check, hiding real failures.
- Growing a 500-line Bash script that should be a Python program with tests.

## Production Tips

- Log to stderr with timestamps and exit with meaningful codes so schedulers and
  [cron](14-cron.md) can detect failure. `set -e` plus a nonzero exit is the
  contact point with your monitoring.
- Gate every script on `shellcheck` and `bash -n` (syntax check) in CI before merge.
- For anything scheduled, capture and route output; a cron job that emails a
  traceback nobody reads is not observable — see [logging](15-logging.md).

## AI Review Checklist

- Does the script start with `set -euo pipefail` (or an equivalent for `sh`)?
- Is every variable and command substitution quoted?
- Are required inputs validated and destructive commands guarded by existence checks?
- Are temp files created with `mktemp` and removed via a `trap ... EXIT`?
- Is the script idempotent — safe to run twice?
- Does it pass `shellcheck` with no suppressed warnings?
- Has the logic outgrown shell and belong in [automation](23-automation.md) instead?

## Related

- `knowledge/linux/03-bash.md`
- `knowledge/linux/02-shell.md`
- `knowledge/linux/23-automation.md`
- `knowledge/linux/14-cron.md`
- `knowledge/linux/19-debugging.md`
