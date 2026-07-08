---
id: php/03-functions
topic: php
slug: functions
title: "Functions"
type: doc
order: 3
status: ready
tags: [php, functions]
related: [php/02-types, php/04-oop, php/18-generators, php/22-clean-code, php/01-language-fundamentals]
when_to_use: "Read before writing or refactoring any function, closure, or callable."
---
# Functions

## Purpose

This document defines how to write PHP functions and closures: signatures, parameter
passing, named and variadic arguments, arrow functions, first-class callable syntax, and
the discipline that keeps functions pure and testable. It covers the choices that make a
function easy to call correctly and hard to call wrongly.

## Why It Matters

Functions are the unit of behavior. A well-typed, single-purpose function with an explicit
signature is self-documenting and testable in isolation. A sprawling function with
by-reference mutation, boolean flag parameters, and hidden global reads is a bug factory —
its behavior depends on state you cannot see from the call site. The rules here keep the
call site honest.

## Core Principles

- **Type the whole signature.** Every parameter and the return value carries a type; see
  [types](02-types.md). The signature is the function's contract.
- **Pass by value; return new values.** By default PHP passes copies (arrays included).
  Avoid `&` by-reference parameters — they let a function mutate the caller's variable
  invisibly. Return the result instead.
- **Prefer pure functions.** A function that depends only on its arguments and reads no
  global/`static` state is trivially testable and cannot cause spooky action at a distance.
- **Name arguments at the call site for clarity.** Named arguments (PHP 8.0+) make boolean
  and optional parameters self-explaining and order-independent.
- **One function, one job.** A function that needs a `bool $flag` to switch behavior is
  usually two functions. See [clean-code](22-clean-code.md).

## Best Practices

- Use **named arguments** to kill "boolean blindness": `send($msg, urgent: true)` reads
  better than `send($msg, true, false)` and survives parameter reordering.
- Give optional parameters sensible defaults and put them last; required parameters first.
- Use **variadics** (`...$items`) instead of an `array` parameter when a function takes a
  homogeneous list, so the type is checked per element.
- Use **arrow functions** (`fn () => ...`) for one-line closures — they capture outer
  scope automatically by value, so there is no `use (...)` to forget.
- Use **first-class callable syntax** (`strlen(...)`, `$obj->method(...)`) to pass a
  function as a value; it is type-checked, unlike a `'strlen'` string callable.
- Return early (guard clauses) to keep the happy path unindented and readable.

## Examples

**Good Example** — pure, typed, self-documenting call site

```php
<?php

declare(strict_types=1);

/**
 * Pure: output depends only on inputs; no globals, no by-ref mutation.
 * @param list<int> $prices minor units
 */
function totalWithTax(array $prices, float $taxRate, bool $roundUp = false): int
{
    $subtotal = array_sum($prices);
    $withTax  = $subtotal * (1 + $taxRate);

    return $roundUp ? (int) ceil($withTax) : (int) round($withTax);
}

// Named argument makes the boolean's meaning obvious at the call site.
$total = totalWithTax([1000, 2500], taxRate: 0.2, roundUp: true);

// First-class callable: type-checked reference, not a fragile 'function-name' string.
$lengths = array_map(strlen(...), ['a', 'bb', 'ccc']);
```

**Bad Example** — impure, by-reference, unreadable call

```php
<?php

$GLOBALS['rate'] = 0.2;

// Mutates the caller's array by reference AND reads a global — untestable in isolation.
function totalWithTax(array &$prices, $roundUp) {
    $sum = 0;
    foreach ($prices as $p) { $sum += $p; }
    $prices[] = $sum;                          // side effect: caller's array changed
    $withTax = $sum * (1 + $GLOBALS['rate']);  // hidden dependency on global state
    return $roundUp ? ceil($withTax) : round($withTax);
}

$items = [1000, 2500];
$total = totalWithTax($items, true); // what does `true` mean here? and $items just grew
```

## Common Mistakes

- Using `&` by-reference parameters to "return" extra values instead of returning a tuple
  or object.
- Reading `$GLOBALS`, `static` counters, or `date()`/`rand()` inside logic functions,
  making them non-deterministic and hard to test.
- Long parameter lists of positional booleans, so call sites are unreadable.
- Forgetting `use (...)` on a classic closure (arrow functions avoid this entirely).
- Passing callables as strings (`'App\\helper'`) that break silently on rename instead of
  the `...` first-class syntax.
- Deep nesting instead of early-return guard clauses.

## AI Review Checklist

- Are all parameters and the return value typed?
- Does the function avoid by-reference (`&`) parameters and global/`static` state?
- Are boolean/optional arguments passed by name at call sites?
- Is each function doing one job rather than branching on a mode flag?
- Are callables passed with first-class `...` syntax rather than string names?
- Does the function use guard clauses instead of deep nesting?

## Related

- `knowledge/php/02-types.md`
- `knowledge/php/04-oop.md`
- `knowledge/php/18-generators.md`
- `knowledge/php/22-clean-code.md`
- `knowledge/php/01-language-fundamentals.md`
