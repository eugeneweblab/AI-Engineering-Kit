---
id: php/16-cli
topic: php
slug: cli
title: "PHP CLI"
type: doc
order: 16
status: ready
tags: [php, cli]
related: [php/08-error-handling, php/14-performance, php/13-security, php/27-production]
when_to_use: "Read before writing a PHP command-line script, console command, cron job, or queue worker."
---
# PHP CLI

## Purpose

This document defines how to write PHP command-line programs that behave correctly as
Unix citizens: exit codes, streams, arguments, signals, and the memory discipline that
long-running workers demand. It covers plain scripts and framework console tooling
(Symfony Console, Laravel Artisan), which most non-trivial CLIs should build on rather
than parsing `$argv` by hand.

## Why It Matters

CLI PHP runs where nobody is watching: cron jobs, deploy scripts, and queue workers. A
web request that fails returns a 500 someone notices; a cron script that exits `0` after
silently failing corrupts data for weeks. The CLI runtime also differs from the web SAPI
— no request timeout, no per-request cleanup, `display_errors` defaults on, and `STDERR`
matters. Code that ignores these differences leaks memory until the worker is killed,
mixes errors into piped output, and reports success when it failed.

## Core Principles

- **Exit codes are the contract.** Return `0` only on success; any non-zero code signals
  failure. Cron, CI, and shell `&&` chains depend on this. Never `exit(0)` after an error.
- **Separate the streams.** Program output goes to `STDOUT`; diagnostics, progress, and
  errors go to `STDERR`. Mixing them corrupts pipes and machine-readable output.
- **Long-running means bounded memory.** A worker that processes millions of jobs must
  hold flat memory — release references and avoid unbounded accumulation.
- **Handle signals for graceful shutdown.** Trap `SIGTERM`/`SIGINT` so an in-flight job
  finishes and resources close before the process dies.
- **Input is still untrusted.** Arguments, environment variables, and piped data are
  inputs — validate them, and never pass them unescaped to a shell.

## Best Practices

- Build real commands on Symfony Console or Artisan for argument parsing, validation,
  help text, and consistent exit codes; reserve raw `$argv` for throwaway scripts.
- Guard against being run via the web: `if (PHP_SAPI !== 'cli') { exit(1); }` at the top
  of a script that must only run on the command line.
- Return an explicit exit code from `main`/command logic (Console's `Command::SUCCESS`
  and `Command::FAILURE`); do not rely on falling off the end.
- Write errors and progress bars to `STDERR` (`fwrite(STDERR, ...)`) so `STDOUT` stays
  pure data that can be piped or redirected.
- For workers, register a `pcntl_signal(SIGTERM, ...)` handler and check a "should stop"
  flag between jobs so shutdown is graceful, not mid-transaction.
- Keep worker memory flat: `unset()` large results, avoid growing static caches, and let
  a supervisor (Supervisor, systemd, Horizon) restart workers after N jobs as a backstop.
- Set `max_execution_time` awareness: it is `0` (unlimited) on CLI, so add your own
  timeouts around external calls — nothing else will stop a hung request.
- Escape any user/argument data passed to shell commands with `escapeshellarg()`, or
  prefer `proc_open()` with an argument array to avoid a shell entirely.

## Examples

**Good Example** — correct streams, exit codes, graceful worker

```php
#!/usr/bin/env php
<?php
if (PHP_SAPI !== 'cli') { exit(1); } // refuse to run under a web server

declare(ticks=1);
$stop = false;
pcntl_signal(SIGTERM, function () use (&$stop) { $stop = true; }); // finish, then quit

$queue = new Queue();
while (!$stop) {
    $job = $queue->reserve();
    if ($job === null) { usleep(100_000); continue; }

    try {
        $job->handle();
        fwrite(STDOUT, $job->id . "\n"); // result → STDOUT (pipeable)
    } catch (Throwable $e) {
        fwrite(STDERR, "job {$job->id} failed: {$e->getMessage()}\n"); // error → STDERR
        $queue->fail($job);
    }
    unset($job); // keep worker memory flat across millions of jobs
}
exit(0); // reached only on a clean, signalled shutdown
```

**Bad Example** — errors on STDOUT, always succeeds, leaks memory

```php
<?php
$log = [];
while (true) { // no signal handling → killed mid-job on deploy
    $job = reserve();
    try {
        $job->handle();
    } catch (Throwable $e) {
        echo "error: {$e->getMessage()}\n"; // pollutes STDOUT, corrupts any pipe
    }
    $log[] = $job; // grows forever → OOM after enough jobs
}
exit(0); // unreachable, and would falsely report success anyway
```

## Common Mistakes

- Exiting `0` (or just falling off the end) after an error, so cron and CI think it worked.
- Writing errors and progress to `STDOUT`, corrupting piped or redirected output.
- Accumulating data in an array or static cache inside an infinite worker loop → OOM.
- No `SIGTERM` handling, so deploys kill workers in the middle of a job.
- Hand-rolling `$argv` parsing (missing flags, no validation) instead of a console library.
- Assuming the web request timeout applies — CLI has none, so hung calls run forever.
- Passing arguments straight into `exec()`/`system()` without `escapeshellarg()`.

## Production Tips

- Run workers under a supervisor that restarts them on exit and after a max job count,
  so a slow memory creep or a crashed worker self-heals.
- Make scripts idempotent where possible; cron double-fires and jobs get retried.
- Use a lock (file lock or a `SETNX` in Redis) to prevent overlapping runs of the same
  cron job when one run runs long.
- Log to `STDERR` or a file with timestamps and job identifiers; there is no request log
  to correlate against on the CLI.

## AI Review Checklist

- Does the program return non-zero on every failure and `0` only on success?
- Do results go to `STDOUT` and errors/diagnostics to `STDERR`?
- Do long-running workers keep memory flat (no unbounded arrays or static growth)?
- Is `SIGTERM`/`SIGINT` trapped for graceful shutdown between jobs?
- Is argument and environment input validated, and escaped before any shell call?
- Does a supervisor restart workers, with a lock preventing overlapping cron runs?
- Are external calls given explicit timeouts, given CLI has no execution-time limit?

## Related

- `knowledge/php/08-error-handling.md`
- `knowledge/php/14-performance.md`
- `knowledge/php/13-security.md`
- `knowledge/php/27-production.md`
