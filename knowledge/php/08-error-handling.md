---
id: php/08-error-handling
topic: php
slug: error-handling
title: "Error Handling"
type: doc
order: 8
status: ready
tags: [php, error-handling]
related: [php/09-exceptions, php/11-http, php/27-production, php/25-debugging]
when_to_use: "Read before configuring error reporting, writing a global handler, or deciding how a failure should surface."
---
# Error Handling

## Purpose

This document defines how a PHP application should detect, report, and recover from
failures at the *configuration and control-flow* level: the error-reporting settings, the
distinction between errors and exceptions, global handlers, and what the user versus the
logs should see. Throwing and catching specific exception types is covered in
[Exceptions](09-exceptions.md); this doc is the surrounding policy that makes those work.

## Why It Matters

How an app handles errors decides whether a small fault becomes a logged blip or a
data-corrupting, information-leaking outage. The two classic failures are opposite and
both dangerous: swallowing errors (`@`, empty `catch`) so problems vanish silently until
they compound, and displaying raw errors to users so stack traces leak file paths,
queries, and secrets to attackers. Correct error handling means *fail loudly to the logs,
gracefully to the user* — every failure is recorded with context, and no internal detail
ever reaches the client.

## Core Principles

- **Turn every error into an exception in your bootstrap.** Register `set_error_handler`
  to throw `ErrorException` so warnings and notices cannot be silently ignored, and are
  caught by the same machinery as real exceptions.
- **`display_errors` off in production, on in development.** Production must never render
  errors to output. All diagnostics go to a log, never to the response body.
- **Report everything; hide nothing at the source.** Set `error_reporting(E_ALL)`
  everywhere. Suppress *display*, never *detection*.
- **Never suppress with `@`.** The shut-up operator hides the error from your handler and
  from logs — the failure still happens, you just lose all evidence.
- **Have one global handler and one shutdown handler.** A top-level `set_exception_handler`
  and `register_shutdown_function` guarantee that even uncaught errors and fatals produce
  a logged, safe, generic response instead of a blank page or a leaked trace.

## Best Practices

- In the bootstrap, set `error_reporting(E_ALL)`, `ini_set('display_errors', '0')` for
  production (`'1'` for dev), and `ini_set('log_errors', '1')` with a writable `error_log`.
- Convert errors to exceptions: `set_error_handler` that throws `ErrorException`, so a
  deprecation or type warning is handled like any other failure.
- Install `set_exception_handler` to log the full exception and emit a generic message
  (or a safe error page / JSON body) with an appropriate status code.
- Install `register_shutdown_function` with `error_get_last()` to catch fatal errors
  (`E_ERROR`, out-of-memory) that bypass the exception handler.
- Log through a PSR-3 logger (Monolog) with structured context, not `echo`/`print_r`.
  Include a request/correlation id so a user report maps to a log line.
- Return the right HTTP status for the failure class (see [HTTP](11-http.md)): 400 for
  bad input, 404 for missing, 500 for unexpected — never 200 with an error body.

## Examples

**Good Example** — errors become exceptions; users get a safe response

```php
<?php
declare(strict_types=1);

error_reporting(E_ALL);
ini_set('display_errors', '0');   // production: never render internals to output
ini_set('log_errors', '1');

// Promote warnings/notices to exceptions so nothing is silently ignored.
set_error_handler(static function (int $severity, string $msg, string $file, int $line): bool {
    if (!(error_reporting() & $severity)) {
        return false;             // respect a caller that intentionally masked this level
    }
    throw new ErrorException($msg, 0, $severity, $file, $line);
});

// Last line of defence: log detail, show the user nothing sensitive.
set_exception_handler(static function (Throwable $e) use ($logger): void {
    $logger->error($e->getMessage(), ['exception' => $e]); // full trace to logs only
    http_response_code(500);
    echo json_encode(['error' => 'Internal Server Error']); // generic, no internals
});
```

**Bad Example** — suppression and leakage

```php
<?php
ini_set('display_errors', '1');            // prod: leaks paths, SQL, secrets to users

$data = @file_get_contents($url);          // @ hides the failure from logs entirely
if ($data === false) {
    // No log, no context; the error simply disappears and $data is false downstream.
}

try {
    risky();
} catch (Throwable $e) {
    // Empty catch: the app pretends nothing went wrong and continues in a bad state.
}
```

## Common Mistakes

- Leaving `display_errors` on in production, leaking stack traces and file paths.
- Using the `@` operator, which erases the error from handlers and logs.
- Empty `catch` blocks that swallow failures and continue in an inconsistent state.
- Catching `Throwable` broadly just to hide it, instead of handling or rethrowing.
- Returning HTTP 200 with an error payload, so clients and monitoring miss the failure.
- Logging with `var_dump`/`print_r` to output instead of a structured logger.
- No shutdown handler, so fatal errors produce a blank white page.

## Production Tips

- Ship logs to a central sink (ELK, Loki, CloudWatch) with severity and a correlation id;
  alert on error-rate spikes, not individual lines.
- Wire an error tracker (Sentry, Bugsnag) into the exception handler for grouping and
  release/deploy attribution.
- Scrub sensitive fields (passwords, tokens, PII) from logged context before it leaves
  the process.
- Test the failure paths in CI: assert that a thrown error yields the right status code
  and a body with no internal detail.

## AI Review Checklist

- Is `display_errors` off in production and diagnostics sent to a log instead?
- Is `error_reporting` set to `E_ALL` so nothing is hidden at the source?
- Are PHP errors converted to exceptions via `set_error_handler`?
- Are there global exception and shutdown handlers producing safe, generic responses?
- Is the `@` suppression operator absent from the codebase?
- Are there no empty `catch` blocks that swallow failures?
- Do failures return correct HTTP status codes rather than 200?

## Related

- `knowledge/php/09-exceptions.md`
- `knowledge/php/11-http.md`
- `knowledge/php/27-production.md`
- `knowledge/php/25-debugging.md`
