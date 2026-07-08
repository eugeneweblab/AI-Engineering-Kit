---
id: php/02-types
topic: php
slug: types
title: "Types"
type: doc
order: 2
status: ready
tags: [php, types]
related: [php/01-language-fundamentals, php/03-functions, php/04-oop, php/19-enums, php/23-modern-php]
when_to_use: "Read before declaring any parameter, property, or return type, or when a TypeError appears."
---
# Types

## Purpose

This document defines PHP's type system and how to use it to make illegal states
unrepresentable. It covers scalar and compound types, nullable/union/intersection types,
`declare(strict_types=1)`, and the modern type keywords (`mixed`, `never`, `void`,
`self`, `static`, `false`, `null`). The goal is code where the signatures alone tell you —
and a static analyzer — what is legal.

## Why It Matters

PHP is dynamically typed, but since 8.0 it has a rich *gradual* type system that a static
analyzer (PHPStan/Psalm) can check before the code ever runs. Types are executable
documentation: they catch mismatches at the boundary, drive IDE autocompletion, and remove
whole categories of defensive `is_string()` checks. Skipping them throws away PHP's biggest
safety improvement of the last decade and pushes bugs to production.

## Core Principles

- **Type everything you can.** Every function parameter, return, and class property should
  have a declared type. An untyped signature is an unchecked contract.
- **`strict_types=1` is what makes types enforce.** Without it, PHP coerces `"5"` to `5`
  and `1` to `true` at call boundaries. With it, a mismatch throws a `TypeError`. Always
  declare it. See [language-fundamentals](01-language-fundamentals.md).
- **Model nullability explicitly.** A value that can be absent is `?T` or `T|null`, not a
  bare `T` that you hope is set. The type forces callers to handle the null.
- **Narrow the type to the domain.** Prefer an [enum](19-enums.md) over a bag of string
  constants, and a value object over a raw `string`, so invalid values cannot be
  constructed.
- **`mixed` is a last resort.** It disables all checking. Use a union type instead if you
  can enumerate the possibilities.

## Best Practices

- Use union types (`int|string`) and intersection types (`Countable&Traversable`) instead
  of `mixed` when the set of accepted types is known.
- Type collections in docblocks with generics syntax PHPStan understands
  (`@return list<User>`, `@param array<string, int> $counts`); the native `array` type
  alone tells a reader nothing about contents.
- Use `void` for functions that return nothing and `never` for functions that always throw
  or exit — `never` lets the analyzer know code after the call is unreachable.
- Prefer `readonly` typed properties for immutable data so a wrong type can never be
  reassigned after construction. See [oop](04-oop.md).
- Cast at trust boundaries only; inside typed code, values already have the right type.

## Examples

**Good Example** — precise types make bad calls impossible

```php
<?php

declare(strict_types=1);

enum Currency: string
{
    case USD = 'USD';
    case EUR = 'EUR';
}

final class Money
{
    public function __construct(
        public readonly int $minorUnits,   // integer cents, never a float → no rounding drift
        public readonly Currency $currency, // enum, not a free-form string
    ) {}
}

/** @return list<Money> */
function nonZero(array $items): array // docblock generic tells PHPStan the element type
{
    return array_values(array_filter($items, fn (Money $m): bool => $m->minorUnits !== 0));
}
```

**Bad Example** — untyped and coercive

```php
<?php
// no strict_types, so "1500" and 15.0 slip through and corrupt the math

class Money {
    public $amount;      // untyped, mutable — any value, any type, anytime
    public $currency;    // string like "usd"/"USD"/"Usd" — no single source of truth
    function __construct($amount, $currency) { // untyped params accept anything
        $this->amount = $amount;
    }
}

function nonZero($items) {              // no param/return types; caller is guessing
    return array_filter($items, fn ($m) => $m->amount != 0); // == juggles 0.0/"0"/null
}
```

## Common Mistakes

- Declaring types but forgetting `strict_types=1`, so coercion still happens silently.
- Using `float` for money and hitting rounding errors; store minor units as `int`.
- Returning `array` with no docblock generic, leaving element types unknown.
- Overusing `mixed` and reintroducing the defensive type checks types were meant to remove.
- Representing a fixed set of values as loose strings instead of an [enum](19-enums.md).
- Making a nullable value a bare `T`, then hitting "null on non-object" at runtime.

## Production Tips

- Run PHPStan/Psalm at a strict level (level 8/max) in CI so type regressions block merge.
- Turn on `array` shape and generic checks; they catch the bugs the native type system
  cannot express.

## AI Review Checklist

- Do all parameters, returns, and properties have declared types?
- Is `declare(strict_types=1);` present so those types are enforced, not coerced?
- Are nullable values typed `?T`/`T|null` rather than assumed non-null?
- Are collections annotated with generic docblocks (`list<T>`, `array<K,V>`)?
- Is `mixed` avoided in favor of a specific union where the types are known?
- Is money stored as integer minor units, not `float`?

## Related

- `knowledge/php/01-language-fundamentals.md`
- `knowledge/php/03-functions.md`
- `knowledge/php/04-oop.md`
- `knowledge/php/19-enums.md`
- `knowledge/php/23-modern-php.md`
