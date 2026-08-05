---
id: php/01-language-fundamentals
topic: php
slug: language-fundamentals
title: "PHP Language Fundamentals"
type: doc
order: 1
status: ready
tags: [php, language-fundamentals]
related: [php/02-types, php/03-functions, php/08-error-handling, php/05-namespaces, php/22-clean-code]
when_to_use: "Read before writing any PHP file to get the file layout, syntax, and evaluation rules right."
---
# PHP Language Fundamentals

## Purpose

This document defines the ground rules of a PHP source file: how a file opens, how
variables and control flow behave, how PHP's loose type juggling works, and the syntactic
choices an agent should make by default. Get these right and the rest of the language
composes cleanly; get them wrong and you ship subtle, hard-to-find bugs.

## Why It Matters

PHP is forgiving by design — it will run code that is almost certainly wrong. Undefined
variables, silent type coercion, and `==` comparisons that treat `"0"` and `false` as
equal are all *legal*. That leniency is where most PHP bugs live. The fundamentals below
turn those silent failures into loud, catchable ones, which is the entire point of writing
disciplined PHP.

## Core Principles

- **Every file starts with `<?php declare(strict_types=1);`.** Strict types disable
  scalar coercion at function boundaries, so a type mismatch throws a `TypeError` instead
  of silently converting. This is the single most important line in a PHP file.
- **Omit the closing `?>` in pure-PHP files.** Any whitespace after it is sent to the
  client and causes "headers already sent" errors. Files that are only PHP must end with
  the last statement.
- **Compare with `===`, never `==`.** Loose equality applies type juggling with
  surprising rules (`0 == "abc"` was `true` before PHP 8). Identity comparison checks
  type and value; use it unless you have a specific, commented reason not to.
- **Treat undefined variables as bugs.** Accessing one is an `E_WARNING` in PHP 8, not a
  fatal error. Static analysis must flag them; never rely on the empty-default behavior.
- **Prefer expressions that fail loudly.** Use `??` for known-nullable access, but do not
  use `@` error suppression to paper over problems.

## Best Practices

- Use `match` over `switch` for value mapping: it is strict (`===`), returns a value, has
  no fall-through, and throws `\UnhandledMatchError` on a missing case — eliminating a
  whole class of forgotten-`break` bugs.
- Use `??` (null coalescing) and `??=` for defaults; use `?->` (nullsafe) to short-circuit
  a call chain when a link may be null, instead of nested `if` guards.
- Prefer `foreach` over indexed `for` loops when iterating collections; it avoids
  off-by-one and stale-index errors.
- Cast intentionally and explicitly (`(int)`, `(string)`) at trust boundaries (request
  input, DB rows) rather than relying on implicit coercion deep inside logic.
- Keep one statement per line and one responsibility per file; see [clean-code](22-clean-code.md).

## Examples

**Good Example** — strict, explicit, fails loudly

```php
<?php

declare(strict_types=1); // scalar type errors throw instead of coercing silently

function shippingBand(int $grams): string
{
    // match is strict (===) and exhaustive: an unlisted value throws, not falls through
    return match (true) {
        $grams <= 500  => 'letter',
        $grams <= 2000 => 'parcel',
        default        => 'freight',
    };
}

$weight = (int) ($_GET['grams'] ?? 0); // explicit cast + default at the trust boundary
echo shippingBand($weight);
// no closing ?> — nothing can leak after the last statement
```

**Bad Example** — loose, silent, leaky

```php
<?php
// no declare(strict_types=1): "500" gets coerced to 500 without complaint

function shippingBand($grams) {          // untyped param hides mistakes
    if ($grams == "letter") return 0;    // == juggles types; comparison is nonsense
    switch ($grams) {
        case 500: $band = 'letter';      // missing break → falls through
        case 2000: $band = 'parcel';
    }
    return $band;                        // $band may be undefined → E_WARNING
}
?>
   <!-- trailing whitespace after ?> breaks header() calls downstream -->
```

## Common Mistakes

- Forgetting `declare(strict_types=1);`, so `"5"` silently becomes `5` and masks bugs.
- Using `==`/`!=` where `===`/`!==` is meant, hitting type-juggling surprises.
- Leaving a `?>` (with trailing newline) in a pure-PHP file, breaking `header()`/cookies.
- Relying on `switch` and forgetting a `break`, causing fall-through.
- Suppressing errors with `@` instead of handling the condition.
- Reading `$_GET`/`$_POST` values without casting or validating them first.

## AI Review Checklist

- Does every PHP file open with `<?php` and `declare(strict_types=1);`?
- Are pure-PHP files free of a closing `?>` tag?
- Are all comparisons `===`/`!==` unless a loose compare is explicitly justified?
- Is `match` used instead of `switch` for value selection where possible?
- Is external input cast/validated at the boundary rather than juggled implicitly?

## Related

- `knowledge/php/02-types.md`
- `knowledge/php/03-functions.md`
- `knowledge/php/05-namespaces.md`
- `knowledge/php/08-error-handling.md`
- `knowledge/php/22-clean-code.md`
