---
id: php/30-engineering-principles
topic: php
slug: engineering-principles
title: "PHP Engineering Principles"
type: doc
order: 30
status: ready
tags: [php, engineering-principles, capture, phpstan, StripeGateway, __construct, InvalidArgumentException, charge]
related: [php/22-clean-code, php/26-best-practices, php/24-psr-standards, php/20-dependency-injection, php/28-tooling]
when_to_use: "Read before designing a new PHP module, service, or package to set the engineering baseline."
---
# PHP Engineering Principles

## Purpose

This document defines the non-negotiable engineering principles for writing PHP that is
correct, maintainable, and safe to run in production. It is the baseline an agent applies
to every file it authors or reviews, independent of framework. Topic-specific rules live
in the sibling docs (security, performance, testing); this doc covers the reasoning that
holds across all of them.

## Why It Matters

PHP runs a large share of the web, and much of it runs untyped, unversioned, and untested.
Because the language will happily coerce `"0"` to `false`, silently return `null`, and
execute a request with an undefined variable, undisciplined PHP fails *quietly* — it keeps
serving traffic while producing wrong results. The cost of a weak baseline is not a crash;
it is a corrupted database discovered weeks later. Applying strict, explicit engineering
principles turns those silent failures into loud, early ones you can fix before shipping.

## Core Principles

- **`declare(strict_types=1)` in every PHP file.** Without it, PHP coerces arguments and
  hides bugs (passing `"5 apples"` where an `int` is expected). Strict types make the
  mismatch a `TypeError` at the boundary. The cost is you must cast intentionally — that is
  the point.
- **Type everything you can express.** Parameter, return, and property types are checked by
  the engine and by static analysis. An untyped signature is an untested contract.
- **Make illegal states unrepresentable.** Use enums, readonly properties, and value
  objects so an object cannot exist in an invalid state. Validation you do once at
  construction beats validation you repeat at every call site.
- **Depend on abstractions, not concretions.** Type-hint interfaces and inject
  dependencies; never `new` a database connection or call a static singleton inside domain
  logic. Untestable code is a design defect, not a testing problem.
- **Fail loud and fail closed.** Prefer exceptions over `false`/`null` returns for error
  conditions. Convert warnings to exceptions in tests. A swallowed error is a future
  incident.
- **Follow PSR standards** (PSR-12 style, PSR-4 autoloading, PSR-3 logging, PSR-7/15 HTTP).
  Conformance is what lets your code interoperate with the ecosystem and other agents.

## Best Practices

- Pin `composer.json` to a supported PHP version (8.3+ in 2026) and commit
  `composer.lock`. Reproducible builds require both.
- Run `phpstan`/`psalm` at max level and `php-cs-fixer` in CI. A green pipeline is the
  contract; local discipline does not scale across contributors.
- Prefer immutability: `readonly` properties and `readonly` classes (PHP 8.2+) for value
  objects. Immutable objects are safe to share and cannot drift out of a valid state.
- Keep functions small and single-purpose; return early to avoid deep nesting.
- Use constructor property promotion and named arguments to keep constructors honest and
  call sites self-documenting.
- Never suppress errors with `@`. It hides the exact information you need to diagnose a
  failure and imposes a runtime cost.
- Handle money and precise decimals with `brick/math` or integer minor units — never
  floats. `0.1 + 0.2 !== 0.3` in IEEE-754.

## Examples

**Good Example** — typed, immutable, injectable, fails loud

```php
<?php
declare(strict_types=1); // coercion off: a wrong-typed arg throws at the boundary

final readonly class Money // immutable value object; cannot drift into a bad state
{
    public function __construct(
        public int $minorUnits,        // store cents as int — never float for money
        public Currency $currency,     // enum, not a free-text string
    ) {
        if ($minorUnits < 0) {
            throw new InvalidArgumentException('Money cannot be negative.'); // fail closed
        }
    }
}

final class Checkout
{
    public function __construct(private PaymentGateway $gateway) {} // depend on interface

    public function charge(Money $amount): Receipt
    {
        return $this->gateway->capture($amount); // testable: swap gateway with a fake
    }
}
```

**Bad Example** — untyped, coercive, hard-wired dependency, fails silent

```php
<?php
// no strict_types: "12.50" and 12.5 both "work", then rounding corrupts the total

class Checkout
{
    public function charge($amount) // untyped: any value flows through unchecked
    {
        $gateway = new StripeGateway(getenv('KEY')); // hard-wired: cannot be tested
        $result = @$gateway->capture($amount);       // @ hides the real error
        return $result ?: false;                     // false return: caller ignores it
    }
}
```

## Common Mistakes

- Omitting `declare(strict_types=1)`, so type errors are silently coerced away.
- Leaving parameters and returns untyped "to keep it flexible" — flexibility here means
  undetected bugs.
- Using arrays as ad-hoc structs (`$user['emial']` typos never fail) instead of typed
  objects or enums.
- Instantiating dependencies with `new` inside business logic, making it untestable.
- Returning `null`/`false` for errors, so callers forget to check and proceed on bad data.
- Using floats for money, then chasing rounding drift in reconciliation.

## Production Tips

- Set `zend.assertions=-1` and `display_errors=Off` in production `php.ini`; log to a
  handler, never to the response body.
- Enable OPcache with `opcache.validate_timestamps=0` on immutable deploys for a large
  throughput win; invalidate by restarting the pool on release.
- Gate merges on `phpstan` level max plus the full test suite so the baseline is enforced
  mechanically, not by review memory.

## AI Review Checklist

- Does every PHP file start with `declare(strict_types=1)`?
- Are all parameters, returns, and properties typed as specifically as the domain allows?
- Are dependencies injected via interfaces rather than constructed inline or via statics?
- Do error conditions throw typed exceptions instead of returning `null`/`false`?
- Are value objects `readonly` and validated at construction?
- Is money handled as integer minor units or `brick/math`, never floats?
- Do `phpstan`/`psalm` and the style fixer pass at the configured level in CI?

## Related

- `knowledge/php/22-clean-code.md`
- `knowledge/php/26-best-practices.md`
- `knowledge/php/24-psr-standards.md`
- `knowledge/php/20-dependency-injection.md`
- `knowledge/php/28-tooling.md`
