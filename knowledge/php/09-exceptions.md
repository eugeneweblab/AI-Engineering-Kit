---
id: php/09-exceptions
topic: php
slug: exceptions
title: "Exceptions"
type: doc
order: 9
status: ready
tags: [php, exceptions]
related: [php/08-error-handling, php/04-oop, php/11-http, php/26-best-practices]
when_to_use: "Read before throwing, catching, or designing exception types for a component or API boundary."
---
# Exceptions

## Purpose

This document defines how to *throw*, *catch*, and *design* exceptions in PHP: which type
to raise, what to catch, how to preserve the cause, and where handling belongs. It builds
on the app-wide policy in [Error Handling](08-error-handling.md), which sets up the global
handlers; here we cover the control flow and type design that lets those handlers do their
job. The goal is exceptions that carry precise meaning and are handled at the right layer.

## Why It Matters

Exceptions are how a component signals "I cannot fulfill this contract." Handled well,
they let each layer fail cleanly and the caller decide what to do. Handled badly, they
either explode with leaked internals or are caught so broadly that a database outage and a
validation error become indistinguishable. The type you throw and the type you catch are a
communication protocol between layers — imprecise types force callers to guess, and
guessing at failure handling is how corrupted state and wrong recovery paths appear.

## Core Principles

- **Throw the most specific type; catch the most specific type you can act on.** Catching
  `\Throwable` "just in case" hides bugs — it swallows `TypeError` and `Error` you should
  have fixed. Catch what you can recover from and let the rest propagate.
- **Distinguish `Exception` from `Error`.** `Error` (and subclasses like `TypeError`,
  `\Error`) signals a programmer/runtime fault you should fix, not handle. `Exception`
  signals a runtime condition callers may reasonably handle. Both implement `\Throwable`.
- **Use SPL exceptions to express intent.** `InvalidArgumentException`,
  `OutOfRangeException`, `RuntimeException`, `LogicException` have defined meanings — a
  `LogicException` is a bug in the caller; a `RuntimeException` is an environmental fault.
- **Always preserve the cause.** When rethrowing, pass the original as the third
  `$previous` argument so the full chain reaches the logs.
- **Handle at the boundary, not everywhere.** Let exceptions propagate to the layer that
  can make a real decision (the HTTP/CLI boundary), instead of catching-and-continuing
  deep inside domain code.

## Best Practices

- Define domain exception types (extending `\RuntimeException` or `\DomainException`) so
  callers can `catch` your errors specifically: `catch (UserNotFoundException $e)`.
- Never catch an exception only to `return null`/`false` and drop the context; that turns
  a described failure into an ambiguous sentinel the caller must re-diagnose.
- When translating a low-level failure, wrap it: `throw new StorageException('...', 0, $e)`
  preserves the SQL/driver cause while presenting a clean domain type upward.
- Use `finally` for cleanup that must run regardless of outcome (closing handles, releasing
  locks) — it runs whether the try succeeds, throws, or returns.
- Keep exception messages descriptive for logs but free of secrets; the message may reach
  a developer, never assume it is private.
- Do not use exceptions for ordinary control flow (e.g. "not found" in a hot loop) where a
  return value is clearer and cheaper — reserve them for exceptional conditions.

## Examples

**Good Example** — specific types, preserved cause, boundary handling

```php
<?php
declare(strict_types=1);

final class UserNotFoundException extends \RuntimeException {}

final class UserRepository
{
    public function find(int $id): User
    {
        try {
            $row = $this->db->fetchOne('SELECT * FROM users WHERE id = ?', [$id]);
        } catch (\PDOException $e) {
            // Wrap the driver error in a domain type, keeping $e as the cause ($previous).
            throw new StorageException("Failed loading user {$id}", 0, $e);
        }
        if ($row === false) {
            throw new UserNotFoundException("User {$id} does not exist"); // precise type
        }
        return User::fromRow($row);
    }
}

// At the HTTP boundary the caller decides how each failure maps to a response.
try {
    $user = $repo->find($id);
} catch (UserNotFoundException $e) {
    http_response_code(404);            // recoverable, specific handling
}
```

**Bad Example** — swallowed, imprecise, cause discarded

```php
<?php
public function find(int $id): ?User
{
    try {
        $row = $this->db->fetchOne('SELECT * FROM users WHERE id = ?', [$id]);
        return $row ? User::fromRow($row) : null;
    } catch (\Throwable $e) {           // catches TypeError/Error too, hiding real bugs
        return null;                    // DB down and "not found" now look identical
        // $e is discarded: no log, no cause chain, caller cannot tell what happened
    }
}
```

## Common Mistakes

- Catching `\Throwable` or `\Exception` broadly and swallowing or nulling the result.
- Rethrowing without passing `$previous`, losing the original stack trace.
- Returning `null`/`false` in place of a meaningful exception, forcing callers to guess.
- Throwing bare `new \Exception('...')` where a specific SPL/domain type would carry
  intent.
- Catching an exception deep in domain code and continuing in a half-updated state.
- Using exceptions as normal control flow, degrading readability and performance.
- Leaking secrets or raw SQL in exception messages that later reach logs or users.

## Production Tips

- Map exception types to HTTP status codes at a single boundary (middleware/handler) so
  the mapping is consistent and testable — domain code stays transport-agnostic.
- Log the full chain (`$e->getPrevious()`) so wrapped causes are visible in the tracker.
- Add assertions/tests that specific error conditions throw the *specific* type, not just
  "an exception" — this locks the contract callers depend on.

## AI Review Checklist

- Is the thrown type the most specific one that fits (SPL or a domain exception)?
- Are `catch` clauses narrow — catching only what the layer can actually handle?
- Is the original exception passed as `$previous` on every rethrow/wrap?
- Are there no empty or null-returning catches that erase failure context?
- Is `Error`/`TypeError` left to propagate rather than caught and hidden?
- Is exception-to-response mapping done once at the boundary, not scattered?
- Are messages free of secrets and raw query text?

## Related

- `knowledge/php/08-error-handling.md`
- `knowledge/php/04-oop.md`
- `knowledge/php/11-http.md`
- `knowledge/php/26-best-practices.md`
