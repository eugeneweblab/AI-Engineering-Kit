---
id: php/22-clean-code
topic: php
slug: clean-code
title: "Clean Code"
type: doc
order: 22
status: ready
tags: [php, clean-code]
related: [php/03-functions, php/04-oop, php/26-best-practices, php/24-psr-standards]
when_to_use: "Read before writing or reviewing everyday PHP for readability, naming, and function/class structure."
---
# Clean Code

## Purpose

This document defines the everyday habits that keep PHP readable and changeable: naming,
function size, control flow, and honest types. It is written so an agent produces code a
human reviewer accepts on the first pass, and can flag the specific things that make code
hard to read.

Clean code is not style pedantry; it is the difference between code that can be safely
changed under time pressure and code that cannot. The rules below are concrete and checkable.

## Why It Matters

Code is read far more often than it is written, and most of a system's cost is in changing
it later. A misleading name, a 200-line method, or a function that both computes and prints
forces every future reader to reconstruct intent from scratch — and that is where bugs
enter. Clean code front-loads a little discipline to remove that recurring tax. The cost is
real (naming and decomposition take thought), but it is paid once; the confusion it prevents
would be paid on every visit.

## Core Principles

- **Names state intent.** A variable or function name should answer "what" and "why," not
  "how." `$activeUsers` beats `$au`; `hasAccess()` beats `check()`.
- **A function does one thing at one level of abstraction.** Either it orchestrates calls
  or it does detail work — not both. Command (does something) and query (returns something)
  should not mix.
- **Small and shallow.** Keep functions short and nesting shallow. Guard-clause early
  returns beat pyramids of `if`. Deep nesting is a decomposition smell.
- **Make the code honest.** Declare strict types, type every parameter and return, and let
  the signature tell the whole truth. `mixed` and untyped params hide contracts.
- **Delete dead weight.** Remove commented-out code, unused parameters, and needless
  comments that restate the code. Version control remembers; the file should not.

## Best Practices

- Put `declare(strict_types=1);` at the top of every file so type mismatches fail loudly
  instead of silently coercing.
- Type-hint all parameters, returns, and properties; use union and nullable types instead
  of `mixed`. A precise signature is documentation the compiler enforces.
- Replace boolean and "flag" parameters that switch behavior with two well-named functions —
  `renderHtml()` / `renderText()` reads better than `render(true)`.
- Prefer early returns / guard clauses to reduce nesting; handle the error or edge case
  first, then let the happy path run unindented.
- Keep functions to a single screen; when a block needs a comment to explain what it does,
  extract it into a named function whose name is that comment.
- Use `readonly` properties and immutable value objects for data that should not change
  after construction, so a whole class of "who mutated this?" bugs cannot occur.
- Write comments that explain *why* (a non-obvious decision, a workaround), never *what*
  the next line already says.

## Examples

**Good Example** — honest types, guard clauses, one job

```php
declare(strict_types=1);

/** Returns the discounted price, or throws if the coupon does not apply. */
function priceWithCoupon(Money $price, Coupon $coupon, DateTimeImmutable $now): Money
{
    if ($coupon->isExpired($now)) {
        throw new CouponExpired($coupon->code); // guard first, happy path unindented
    }
    if ($price->lessThan($coupon->minimumSpend)) {
        throw new MinimumSpendNotMet($coupon->minimumSpend);
    }

    return $price->minusPercent($coupon->percentOff); // single, clear result
}
```

**Bad Example** — vague names, flag parameter, deep nesting, dishonest types

```php
function calc($p, $c, $flag) // untyped: contract is invisible; $flag switches behavior
{
    if ($c) {
        if (!$c['exp']) {                 // pyramid of conditionals
            if ($p >= $c['min']) {
                if ($flag) {
                    echo $p - ($p * $c['pct'] / 100); // computes AND prints: two jobs
                } else {
                    return $p - ($p * $c['pct'] / 100);
                }
            }
        }
    }
    return $p; // silent fallthrough hides the "coupon didn't apply" case
}
```

## Common Mistakes

- Abbreviated or generic names (`$data`, `$tmp`, `$x`, `handle()`) that force readers to
  guess the meaning from usage.
- Boolean flag parameters that make one function secretly two behaviors.
- Functions that both return a value and perform a side effect (print, log, mutate global),
  violating command/query separation.
- Untyped parameters, `mixed` returns, and missing `strict_types`, letting coercion hide bugs.
- Deep nesting where guard clauses would flatten the flow.
- Comments that narrate the code (`// increment i`) instead of explaining a decision.
- Leaving commented-out code and unused arguments behind as noise.

## Production Tips

- Enforce these mechanically: run a linter/formatter (PHP-CS-Fixer to PSR-12) and a static
  analyzer (PHPStan/Psalm at a high level) in CI so style and type honesty are not opinions.
- Set a complexity or method-length threshold in the analyzer to catch functions that grew
  past "one thing" before review, not after.

## AI Review Checklist

- Does every file declare `strict_types=1`, and is every parameter, return, and property typed?
- Do names state intent, with no single-letter or generic `data`/`tmp` identifiers?
- Does each function do one thing at one level, without a behavior-switching boolean flag?
- Are queries free of side effects and commands free of surprising return values?
- Is nesting shallow, using guard clauses instead of deep `if` pyramids?
- Is there any dead code, commented-out block, or comment that merely restates the line?

## Related

- `knowledge/php/03-functions.md`
- `knowledge/php/04-oop.md`
- `knowledge/php/26-best-practices.md`
- `knowledge/php/24-psr-standards.md`
