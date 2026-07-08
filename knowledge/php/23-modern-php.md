---
id: php/23-modern-php
topic: php
slug: modern-php
title: "Modern PHP"
type: doc
order: 23
status: ready
tags: [php, modern-php]
related: [php/02-types, php/04-oop, php/19-enums, php/22-clean-code]
when_to_use: "Read before writing new PHP or modernizing legacy code, to use current language features instead of outdated idioms."
---
# Modern PHP

## Purpose

This document defines the modern PHP feature set (PHP 8.1 through 8.4) an agent should
reach for by default, and the legacy idioms it should stop writing. It is written so
generated code looks like 2026 PHP — concise, typed, and immutable by default — not
PHP 5 with newer syntax bolted on.

"Modern" here means: promoted constructors, readonly data, enums, `match`, named arguments,
the nullsafe operator, and property hooks — used because each removes a class of bug or
boilerplate, not for novelty.

## Why It Matters

The language changed substantially, and old habits produce worse code than the new
features allow. Manual constructor assignment, `switch` fallthrough, boolean nullchecks,
and mutable public properties are not just verbose — each is a common source of real bugs
that a modern feature designed them out of. Writing current PHP means less code to review,
stronger compiler-checked guarantees, and idioms other engineers recognize. The trade-off
is a minimum version requirement, so confirm the target runtime before using a feature
from a newer release.

## Core Principles

- **Immutable by default.** Prefer `readonly` properties and `readonly class` for data
  objects; mutation should be a deliberate exception, not the default.
- **Let the language enforce contracts.** Use enums, typed properties, typed class
  constants, and `#[\Override]` so mistakes fail at compile/analysis time, not in production.
- **Concise construction.** Use constructor property promotion and named arguments to
  remove boilerplate and make call sites self-documenting.
- **Expression over statement.** Prefer `match` (strict, returns a value, exhaustive) and
  the nullsafe operator over `switch` and nested null checks.
- **Know your target version.** Each feature has a minimum PHP version; using one your
  runtime does not support is a deploy-time fatal. Verify before you rely on it.

## Best Practices

- Promote constructor parameters (`public readonly string $name`) instead of declaring a
  property and assigning it in the body — one line, and immutability is explicit.
- Use `readonly class` (8.2+) for value objects and DTOs so no property can be mutated
  after construction, eliminating "who changed this?" bugs.
- Replace value-constant sets with backed enums (8.1); replace `switch` with `match`.
- Use named arguments for functions with several optional or boolean parameters, so call
  sites read `send(async: true)` instead of `send(null, null, true)`.
- Use the nullsafe operator `?->` for optional chains, and `??`/`??=` for defaults, instead
  of nested `isset`/`if` ladders.
- Adopt 8.3 typed class constants and `#[\Override]` (which errors if a method overrides
  nothing), and 8.4 property hooks / asymmetric visibility to replace boilerplate getters.
- Use first-class callable syntax (`$fn = strlen(...)`) instead of string callables or
  closures that just forward arguments.

## Examples

**Good Example** — modern idioms: readonly class, promotion, match, nullsafe

```php
declare(strict_types=1);

// Immutable value object in a few lines; every field typed and unchangeable.
final readonly class Address
{
    public function __construct(
        public string $street,
        public string $city,
        public string $countryCode,
    ) {}
}

enum Tier: string { case Free = 'free'; case Pro = 'pro'; case Team = 'team'; }

function seatLimit(Tier $tier): int
{
    return match ($tier) {           // strict, exhaustive, returns a value
        Tier::Free => 1,
        Tier::Pro  => 5,
        Tier::Team => 50,
    };
}

$city = $user->address?->city ?? 'unknown'; // nullsafe + default, no isset ladder
```

**Bad Example** — legacy idioms on a modern runtime

```php
class Address
{
    public $street;   // untyped, mutable, no promotion
    public $city;
    public $countryCode;

    public function __construct($street, $city, $countryCode)
    {
        $this->street = $street;      // manual assignment boilerplate
        $this->city = $city;
        $this->countryCode = $countryCode;
    }
}

function seatLimit($tier)
{
    switch ($tier) {                  // loose, fallthrough-prone, no return guarantee
        case 'free': return 1;
        case 'pro':  return 5;
        default:     return 50;       // silently accepts unknown tiers
    }
}

$city = isset($user->address) && $user->address->city ? $user->address->city : 'unknown';
```

## Common Mistakes

- Declaring mutable, untyped public properties for data that should be a `readonly` value object.
- Using `switch` (loose comparison, fallthrough) where `match` gives strictness and a return value.
- Manual constructor assignment instead of property promotion.
- Long positional argument lists with `null` placeholders instead of named arguments.
- Nested `isset`/`if` chains where `?->` and `??` express the intent in one line.
- Using a feature from a newer PHP version than the deployment target, causing a runtime fatal.
- Overriding a method without `#[\Override]`, so a renamed parent method silently orphans the child.

## Production Tips

- Pin the language level in `composer.json` (`"require": {"php": ">=8.3"}`) and set PHPStan's
  `phpVersion` to match, so the analyzer rejects features your runtime cannot run.
- Use an automated upgrader (Rector) with version-targeted rule sets to modernize legacy code
  in reviewable, mechanical steps rather than by hand.
- Track the PHP release calendar; do not adopt a version past its security-support window,
  and gate new-version features behind a confirmed runtime bump.

## AI Review Checklist

- Are data objects `readonly` (class or properties) unless mutation is genuinely required?
- Is `match` used instead of `switch`, and are backed enums used instead of value constants?
- Are constructors using property promotion with fully typed, promoted parameters?
- Are optional chains and defaults expressed with `?->`/`??` rather than `isset` ladders?
- Does every used feature exist in the pinned minimum PHP version?
- Do overriding methods carry `#[\Override]`?

## Related

- `knowledge/php/02-types.md`
- `knowledge/php/04-oop.md`
- `knowledge/php/19-enums.md`
- `knowledge/php/22-clean-code.md`
