---
id: php/100-common-antipatterns
topic: php
slug: common-antipatterns
title: "PHP Common Antipatterns"
type: antipatterns
order: 100
status: ready
tags: [php, common-antipatterns, hash_equals, prepare, __construct, execute, strict_types, TypeError]
related: [php/99-ai-review-checklist, php/13-security, php/08-error-handling, php/22-clean-code, php/30-engineering-principles]
when_to_use: "Read when writing or reviewing PHP to recognize and remove recurring failure patterns."
---
# PHP Common Antipatterns

## Purpose

A catalog of PHP antipatterns an agent must recognize and refuse to write. Each entry names
the pattern, explains *why it is wrong* (the concrete failure it causes), and gives *the
fix*. These are the recurring smells behind most PHP bugs, breaches, and outages.

## Why It Matters

PHP's tolerance for loose types, silent coercion, and global state means antipatterns run
without complaint until the exact input that breaks them arrives — often in production, often
from an attacker. Learning to see these patterns is cheaper than debugging their
consequences. The fixes below are idiomatic modern PHP (8.3+, 2026).

## Antipatterns

### 1. Omitting `declare(strict_types=1)`

- **Why it is wrong:** PHP silently coerces `"5abc"` to `5`, `""` to `false`, and `null` to
  `0`, so type mismatches never surface where they happen — they corrupt data downstream.
- **The fix:** Start every file with `declare(strict_types=1);` so a wrong type throws a
  `TypeError` at the call boundary.

### 2. Loose equality (`==`) for comparisons

- **Why it is wrong:** `0 == "a"`, `"1e3" == "1000"`, and `null == false` are all true under
  `==`, producing security bugs (e.g. a password hash comparison passing on `"0"`).
- **The fix:** Use `===`/`!==` by default; use `hash_equals()` for secret comparison.

```php
if ($providedToken === $storedToken) { /* type + value checked */ }   // correct
if (hash_equals($storedToken, $providedToken)) { /* constant-time */ } // for secrets
```

### 3. SQL built by string concatenation

- **Why it is wrong:** Interpolating user input into SQL is the classic injection hole; one
  crafted value dumps or destroys the database.
- **The fix:** Always use prepared statements with bound parameters.

```php
// Bad: injectable
$db->query("SELECT * FROM users WHERE email = '$email'");
// Good: parameterized
$stmt = $pdo->prepare('SELECT * FROM users WHERE email = ?');
$stmt->execute([$email]);
```

### 4. Suppressing errors with `@`

- **Why it is wrong:** `@` hides the exact diagnostic you need, still incurs the error's cost,
  and turns a fixable warning into an invisible failure.
- **The fix:** Check preconditions explicitly, or catch the specific exception. Never suppress.

### 5. Returning `false`/`null` for error conditions

- **Why it is wrong:** Callers forget to check the sentinel and proceed on invalid data;
  `false` also collides with legitimate values. The failure moves far from its cause.
- **The fix:** Throw a typed exception. Reserve `null` for genuine "absent," not "failed."

### 6. Arrays as ad-hoc structs

- **Why it is wrong:** `$user['emial']` never fails — typos and missing keys surface as `null`
  much later. The shape is undocumented and unchecked.
- **The fix:** Use a typed DTO or `readonly` value object; the engine and static analysis then
  enforce the shape.

```php
final readonly class User {
    public function __construct(public string $email, public string $name) {}
}
```

### 7. Global state and static singletons in logic

- **Why it is wrong:** `$GLOBALS`, `static::$instance`, and hidden container calls create
  invisible coupling, make tests order-dependent, and prevent parallel/async safety.
- **The fix:** Inject dependencies through the constructor and type-hint interfaces.

### 8. Fat controllers / God classes

- **Why it is wrong:** Business rules embedded in a 1,000-line controller cannot be reused or
  unit-tested and drift out of sync across endpoints.
- **The fix:** Keep controllers thin (parse, delegate, respond); put rules in domain services.

### 9. Swallowing exceptions with an empty catch

- **Why it is wrong:** `catch (\Throwable $e) {}` erases the failure, so the system continues in
  a corrupt state and the root cause is unknowable.
- **The fix:** Catch the specific type, log with context, and rethrow or convert to a
  meaningful error. Never leave a catch body empty.

### 10. Floats for money

- **Why it is wrong:** IEEE-754 cannot represent `0.10` exactly, so sums drift and
  reconciliation fails.
- **The fix:** Store integer minor units (cents) or use `brick/math` `BigDecimal`.

### 11. Unbounded queries and N+1 loops

- **Why it is wrong:** `SELECT *` with no limit loads the whole table into memory; a query
  inside a loop issues thousands of round-trips under load.
- **The fix:** Paginate, select only needed columns, and eager-load/join to collapse N+1.

### 12. Trusting `$_GET`/`$_POST`/`$_REQUEST` directly

- **Why it is wrong:** Raw superglobals are attacker-controlled; using them unvalidated in
  paths, queries, or output causes injection and traversal.
- **The fix:** Validate and cast at the boundary (a form/request object), then pass typed
  values inward.

## Common Mistakes

- Treating these as style preferences rather than defect sources — each maps to a real
  outage or CVE class.
- Fixing the symptom (adding an `isset`) instead of the pattern (introducing a typed shape).
- Assuming framework "magic" removes the need for parameterized queries or output escaping.

## AI Review Checklist

- Is `strict_types` on and are comparisons strict?
- Are all queries parameterized and all output escaped?
- Are errors thrown (not `@`-suppressed or returned as `false`), and are catches specific?
- Are typed DTOs/value objects used instead of ad-hoc arrays and globals?
- Is money integer/decimal, and are queries bounded with no N+1?

## Related

- `knowledge/php/99-ai-review-checklist.md`
- `knowledge/php/13-security.md`
- `knowledge/php/08-error-handling.md`
- `knowledge/php/22-clean-code.md`
- `knowledge/php/30-engineering-principles.md`
