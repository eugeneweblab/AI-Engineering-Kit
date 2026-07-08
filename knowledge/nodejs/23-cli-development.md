---
id: nodejs/23-cli-development
topic: nodejs
slug: cli-development
title: "CLI Development"
type: doc
order: 23
status: ready
tags: [nodejs, cli-development]
related: [nodejs/10-process, nodejs/11-child-process, nodejs/16-error-handling, nodejs/14-environment, nodejs/04-package-management]
when_to_use: "Read before building or reviewing a Node.js command-line tool intended for humans or scripts."
---
# CLI Development

## Purpose

This document defines how to build a well-behaved Node.js command-line tool: one
that composes in pipelines, reports failure honestly through exit codes, parses
arguments predictably, and works both interactively and inside CI scripts. A CLI is
a program with a Unix contract — stdin/stdout/stderr, exit codes, signals — and
violating that contract breaks every script that calls it, silently.

## Why It Matters

A CLI is an API whose consumers are shell scripts and other programs, not just
humans. If it prints errors to stdout, exits 0 on failure, or hangs waiting for a TTY
in CI, it corrupts pipelines and makes automation impossible to trust — a failed
build reports success and ships broken code. Unlike a web service, a CLI has no retry
layer in front of it; its exit code *is* the contract. Getting the streams, codes,
and signal handling right is what separates a tool people can automate from one they
work around.

## Core Principles

- **Exit codes are the contract.** `0` means success, non-zero means failure. Scripts
  branch on this; an exit-0-on-error CLI makes `set -e` and `&&` chains unsafe.
- **stdout is data, stderr is diagnostics.** Machine-readable results go to stdout;
  logs, progress, and errors go to stderr. Mixing them corrupts piped output.
- **Parse arguments explicitly and validate early.** Use a real parser, reject bad
  input with a clear message and non-zero exit before doing any work.
- **Behave in a pipe, not just a terminal.** Detect `process.stdout.isTTY`; suppress
  colors, spinners, and prompts when output is piped or `CI` is set.
- **Handle signals and clean up.** On `SIGINT`/`SIGTERM`, stop work, release resources,
  and exit with a conventional code (`130` for SIGINT). Never leave orphaned processes.

## Best Practices

- Parse args with the built-in `node:util` `parseArgs` for simple tools, or
  `commander`/`yargs` for subcommands and rich help. Do not hand-roll `process.argv` slicing.
- Write results to stdout and everything else (errors, progress, `--verbose` logs) to
  stderr, so `mytool | jq` works and errors still reach the user.
- Set an explicit `process.exitCode` (preferred over `process.exit()`, which can
  truncate pending stdout writes) and return a documented non-zero code per error class.
- Add a shebang (`#!/usr/bin/env node`), mark the file executable, and declare `bin`
  in `package.json` so `npx`/global install work. See `nodejs/04-package-management`.
- Detect non-interactive contexts (`!process.stdout.isTTY` or `process.env.CI`) and
  disable color, animations, and interactive prompts — accept flags or fail instead of hanging.
- Provide `--help` and `--version`, honor `NO_COLOR`, and read config from flags >
  env > file in that precedence. See `nodejs/14-environment`.
- Handle `EPIPE` on stdout (e.g. `... | head`) gracefully instead of crashing with an unhandled error.

## Examples

**Good Example** — validated args, correct streams, honest exit code

```js
#!/usr/bin/env node
import { parseArgs } from "node:util";

const { values, positionals } = parseArgs({
  options: { format: { type: "string", default: "json" } },
  allowPositionals: true,
});

async function main() {
  if (positionals.length === 0) {
    process.stderr.write("error: expected a file path\n"); // diagnostics → stderr
    process.exitCode = 2;                                   // non-zero → failure
    return;
  }
  const result = await convertFile(positionals[0], values.format);
  process.stdout.write(JSON.stringify(result) + "\n");     // data → stdout, pipeable
}

process.on("SIGINT", () => process.exit(130)); // conventional code for Ctrl-C
main().catch((err) => {
  process.stderr.write(`error: ${err.message}\n`);
  process.exitCode = 1;
});
```

**Bad Example** — breaks every script that calls it

```js
const file = process.argv[2]; // no validation; undefined if missing

convertFile(file).then((result) => {
  console.log("Done!");                 // human noise on stdout corrupts pipes
  console.log(JSON.stringify(result));  // mixed with the noise above
}).catch((err) => {
  console.log("Something failed: " + err); // error on stdout, not stderr
  // no exit code set → exits 0, so `mytool && deploy` deploys after a failure
});
```

## Common Mistakes

- Exiting `0` after an error, so calling scripts treat failure as success.
- Writing errors or progress to stdout, corrupting machine-readable piped output.
- Calling `process.exit()` mid-write, truncating buffered stdout before it flushes.
- Prompting for input or rendering spinners when output is piped or in CI, causing hangs.
- Slicing `process.argv` by hand instead of using a parser, mishandling `--flag=value` and quoting.
- Ignoring `SIGINT`/`SIGTERM`, leaving temp files and child processes orphaned.
- Crashing on `EPIPE` when the consumer (`head`, `less`) closes the pipe early.

## Production Tips

- Emit machine-readable output behind a `--json` flag and human-formatted output by
  default, chosen automatically by `isTTY`, so the same tool serves people and scripts.
- Respect `NO_COLOR` and `FORCE_COLOR` conventions rather than always colorizing.
- Test the CLI as a subprocess in CI: assert on exit code, stdout, and stderr separately.
- Document every exit code in `--help` so callers can branch on specific failures.

## AI Review Checklist

- Does the tool exit non-zero on every error path and zero only on success?
- Is data written to stdout and are diagnostics/errors written to stderr?
- Are arguments parsed with a real parser and validated before work begins?
- Does it disable colors/prompts/spinners when non-interactive or in CI?
- Are `SIGINT`/`SIGTERM` handled with cleanup and conventional exit codes?
- Is `process.exitCode` set (rather than `process.exit()` mid-write) so stdout flushes?
- Are `EPIPE` and closed-pipe consumers handled without crashing?

## Related

- `knowledge/nodejs/10-process.md`
- `knowledge/nodejs/11-child-process.md`
- `knowledge/nodejs/16-error-handling.md`
- `knowledge/nodejs/14-environment.md`
- `knowledge/nodejs/04-package-management.md`
