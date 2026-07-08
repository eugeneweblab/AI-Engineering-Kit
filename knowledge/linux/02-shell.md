---
id: linux/02-shell
topic: linux
slug: shell
title: "Shell"
type: doc
order: 2
status: ready
tags: [linux, shell]
related: [linux/03-bash, linux/01-filesystem, linux/00-overview, linux/05-permissions, linux/04-users-and-groups]
when_to_use: "Read before typing any command line or reasoning about how quoting, globbing, redirection, or pipelines behave."
---
# Shell

## Purpose

This document explains what a shell is and how it turns the text you type into an
executed command: tokenization, expansion, word splitting, globbing, quoting,
redirection, pipelines, and exit status. It is written so an agent can predict exactly
what a command line does *before* running it.

The shell is the interactive and orchestration layer of Linux. This doc covers the
parsing model common to POSIX shells; writing non-trivial *scripts* in that model is
covered in [bash](03-bash.md).

## Why It Matters

The shell is a text-processing language, and its most dangerous feature is that it
rewrites your command before running it. An unquoted variable containing a space becomes
two arguments; a `*` becomes a list of filenames; a `;` inside a variable can become a
second command. Attackers and edge-case data exploit exactly these expansions. Most
"why did this delete everything" incidents are a misunderstanding of the order in which
the shell expands and splits a line. Understanding the pipeline of expansions is what
makes a command line predictable.

## Core Principles

- **The shell expands, then executes.** Variable expansion, globbing, and command
  substitution happen *first*, producing a final list of words; the program never sees
  your `$var` or `*`, only the result.
- **Word splitting happens after unquoted expansion.** `rm $file` where `file="a b"`
  runs `rm a b` (two files). Quoting — `rm "$file"` — suppresses splitting.
- **Quotes change meaning, not just style.** Single quotes are literal; double quotes
  allow `$` and `` ` `` expansion but preserve spaces; no quotes invites splitting and
  globbing.
- **Exit status is the truth signal.** `0` is success, non-zero is failure. Pipelines,
  `&&`, `||`, and `if` all key off it.
- **Redirection rewires file descriptors, in left-to-right order.** `>` truncates,
  `>>` appends, `2>&1` ties stderr to wherever stdout currently points.

## Best Practices

- Quote every expansion by default: `"$var"`, `"$(cmd)"`, `"${array[@]}"`. Only remove
  quotes when you *intend* splitting or globbing.
- Prefer `$(command)` over backticks — it nests cleanly and is easier to read.
- Use `&&` / `||` to sequence on success/failure instead of a bare `;`, which ignores
  the previous command's result.
- Test with `[[ ... ]]` in Bash (safer, no word-splitting inside) rather than `[ ... ]`
  when portability is not required; always quote operands regardless.
- End option parsing with `--` before user-controlled arguments so a value like `-rf`
  cannot be read as a flag.
- Preview a destructive glob with `echo` or `ls` first; the shell expands `*` the same
  way for `echo` as for `rm`.
- Never build a command string and pass it to `eval` or `sh -c` from untrusted input —
  that is shell injection. Pass data as arguments, not as code.

## Examples

**Good Example** — quoted expansion, checked status, explicit redirection

```bash
file="my report.txt"          # contains a space
if [[ -f "$file" ]]; then     # quoted, so it stays one argument
  # 2>&1 must come AFTER >out.log so stderr follows stdout into the file
  grep -c "error" -- "$file" >out.log 2>&1 \
    && echo "scan ok" \
    || echo "grep failed with status $?"   # branch on real exit status
fi
```

**Bad Example** — unquoted expansion and injection-prone eval

```bash
file=$1                       # unquoted below; a space or glob in $1 breaks it
rm $file                      # "my report.txt" → rm my report.txt (two files!)
grep error $file > out.log 2> out.log   # racy: two truncating redirects to same file
eval "backup_$USER $file"     # eval on external data → shell injection
```

## Common Mistakes

- Leaving `$var` unquoted, so spaces or globs in the value silently change the command.
- Assuming `2>&1 >file` sends both streams to the file — order matters; stderr binds to
  the *old* stdout (the terminal) here.
- Using `;` where you meant "only if the previous step succeeded" (`&&`).
- Parsing `ls` output or `for x in $(cmd)` to iterate names, which word-splits on spaces
  and newlines.
- Passing user input into `eval`, `sh -c "$x"`, or an unquoted command substitution.
- Forgetting that `*` does not match dotfiles by default, so `rm *` leaves `.env` behind
  while `rm -rf .*` can escape into the parent.

## AI Review Checklist

- Is every variable and command substitution quoted unless splitting is intended?
- Is command sequencing done with `&&`/`||` (not bare `;`) where success matters?
- Is redirection order correct, especially `>file 2>&1` vs `2>&1 >file`?
- Is any user-controlled data kept out of `eval` / `sh -c` and passed as arguments?
- Are destructive globs previewed, and is `--` used before untrusted path arguments?
- Is filename iteration whitespace-safe rather than parsing `ls`?

## Related

- `knowledge/linux/03-bash.md`
- `knowledge/linux/01-filesystem.md`
- `knowledge/linux/00-overview.md`
- `knowledge/linux/05-permissions.md`
- `knowledge/linux/04-users-and-groups.md`
