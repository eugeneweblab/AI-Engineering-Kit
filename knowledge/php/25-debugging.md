---
id: php/25-debugging
topic: php
slug: debugging
title: "Debugging"
type: doc
order: 25
status: ready
tags: [php, debugging]
related: [php/08-error-handling, php/09-exceptions, php/15-testing, php/27-production, php/28-tooling]
when_to_use: "Read before diagnosing a bug, a slow request, or a failure that only appears in production."
---
# Debugging

## Purpose

This document defines how to find the cause of a PHP defect efficiently and safely: how to
make errors visible, how to inspect running code with a real debugger, and how to trace a
problem in production without leaking data or taking the site down. The goal is to replace
guesswork and scattered `var_dump()` calls with a repeatable method.

Debugging is the act of turning a symptom into a root cause. A good debugging setup makes
the program *tell you* what it is doing; a bad one makes you infer it from output.

## Why It Matters

PHP's request-per-execution model hides state between requests, so bugs often reproduce
only under specific input, load, or configuration. Left-in `var_dump()`/`print_r()` calls
leak internals to users, corrupt JSON responses, and get committed by accident. Meanwhile,
a misconfigured `display_errors` in production exposes stack traces and file paths to
attackers. Knowing the right tool — Xdebug step-through, structured logs, a profiler — turns
a multi-hour hunt into minutes and keeps sensitive data off the wire.

## Core Principles

- **Reproduce first, then instrument.** A failing test or a saved request that reliably
  triggers the bug is worth more than any amount of live poking.
- **Use a real debugger over dump statements.** Xdebug step-through shows the full call
  stack and variable state at a breakpoint without editing code you might forget to revert.
- **Errors must be loud in dev, silent to users in prod.** `display_errors=On` locally;
  `display_errors=Off` with `log_errors=On` in production. Never show stack traces to users.
- **Read the stack trace bottom-up to top-down.** The bottom frame is where it broke; the
  top is the entry point. The cause is usually the first frame you own.
- **Change one thing at a time.** Bisect the input, the commit history, or the config until
  the variable that flips the outcome is isolated.

## Best Practices

- Install Xdebug in the dev container only; set `xdebug.mode=debug,develop` and connect your
  editor. Keep it off in production — it imposes heavy overhead on every request.
- Log with a PSR-3 logger at appropriate levels and include context arrays; grep structured
  logs instead of adding temporary prints.
- Set `error_reporting(E_ALL)` in development so notices and deprecations surface early,
  before they become fatals on a newer PHP version.
- Use `git bisect` to find the commit that introduced a regression, and `git blame` on the
  suspect line to find the intent.
- Profile before optimizing: use Xdebug's profiler or a sampling profiler (Excimer,
  Blackfire, Tideways) to find the real hot path rather than guessing.
- For "works locally, fails in prod" bugs, compare PHP version, extensions, `php.ini`, and
  environment variables first — these differences cause most such reports.

## Examples

**Good Example** — reproduce with a test, inspect with a breakpoint

```php
<?php
// A failing test captures the exact input, so the bug is reproducible and stays fixed.
public function test_discount_never_makes_total_negative(): void
{
    $cart = new Cart(subtotal: 500);
    $cart->applyCoupon(new Coupon(amountOff: 900)); // the reported edge case

    // Set an Xdebug breakpoint on Cart::total() and step through instead of dumping.
    self::assertSame(0, $cart->total()); // codifies the correct behavior
}
```

**Bad Example** — dump-driven debugging left in the code path

```php
<?php
public function total(): int
{
    $total = $this->subtotal - $this->discount;
    var_dump($this->discount);        // corrupts JSON output, leaks internals to users
    error_log(print_r($_SESSION, true)); // writes session data (maybe PII) to logs
    return $total;                    // no clamp: returns a negative total, the real bug
}
```

## Common Mistakes

- Shipping `var_dump()`, `dd()`, `print_r()`, or `error_log(print_r(...))` to production.
- Leaving `display_errors=On` in production, exposing paths and stack traces to the world.
- Silencing errors with the `@` operator, which hides the very information you need.
- Optimizing based on a hunch instead of a profiler; the real hot path is rarely the guess.
- Debugging on production directly instead of reproducing the failing request locally.
- Ignoring deprecation notices in dev, then hitting a fatal error after a PHP upgrade.

## Production Tips

- Route logs to a structured sink (JSON to stdout, shipped to ELK/Loki) with a request/trace
  id so one failing request can be followed across services.
- Turn on the profiler behind a flag or header so you can sample a real production request
  without profiling every one.
- Keep an error tracker (Sentry, Bugsnag) that captures exception, stack, and request
  context — without the request body's secrets.

## AI Review Checklist

- Are all `var_dump`/`print_r`/`dd`/debug `error_log` calls removed from committed code?
- Is `display_errors` off and `log_errors` on for the production configuration?
- Is there a failing test or saved request that reproduces the bug before it is "fixed"?
- Are errors logged through a PSR-3 logger with context, not echoed to output?
- Is the `@` error-suppression operator absent from the changed code?
- Was any performance change justified by profiler output, not a guess?

## Related

- `knowledge/php/08-error-handling.md`
- `knowledge/php/09-exceptions.md`
- `knowledge/php/15-testing.md`
- `knowledge/php/27-production.md`
- `knowledge/php/28-tooling.md`
