---
id: php/17-attributes
topic: php
slug: attributes
title: "Attributes"
type: doc
order: 17
status: ready
tags: [php, attributes]
related: [php/04-oop, php/23-modern-php, php/20-dependency-injection, php/15-testing]
when_to_use: "Read before defining or consuming PHP attributes (native #[...] metadata) for routing, validation, ORM mapping, or DI."
---
# Attributes

## Purpose

This document defines how to use PHP **attributes** — the native `#[...]` metadata syntax
added in PHP 8.0 — correctly: how to declare an attribute class, how to read attributes
via reflection, and where they belong versus where they cause harm. Attributes replaced
the old docblock-annotation convention (Doctrine `@Annotation`) with a first-class,
type-checked language feature. This is a PHP 8+ topic; attributes do not exist earlier.

## Why It Matters

Attributes attach declarative metadata to code — routes on controllers, validation rules
on properties, ORM columns on fields — and frameworks (Symfony, Laravel, Doctrine ORM,
PHPUnit) now use them pervasively. Used well, they colocate configuration with the code
it describes and are checked by the parser instead of living in fragile string comments.
Used badly, they hide behavior inside reflection that no one can follow, run expensive
reflection in hot paths, or smuggle logic into what should be pure metadata. Knowing the
boundary is the difference between clarity and a debugging nightmare.

## Core Principles

- **Attributes are inert metadata, not code.** They do nothing until something reflects
  over them and acts. Never put side effects or heavy work in an attribute constructor.
- **Declare intent with the target.** Mark each attribute class with `#[Attribute(...)]`
  and the exact flags (`TARGET_METHOD`, `TARGET_PROPERTY`, `IS_REPEATABLE`) so misuse is
  a clear error, not silent nonsense.
- **Reflection is the only reader.** Attributes are visible solely via the Reflection API
  (`getAttributes()` + `newInstance()`); there is no magic auto-wiring.
- **Reflection is not free.** Reading attributes at runtime costs real time; cache or
  compile the result rather than reflecting on every request.
- **Prefer attributes for configuration, not control flow.** If a reader must branch on
  many attribute shapes to decide behavior, the logic belongs in code, not metadata.

## Best Practices

- Declare every attribute class with `#[Attribute]` and constrain its targets, e.g.
  `#[Attribute(Attribute::TARGET_PROPERTY)]`; add `IS_REPEATABLE` only when repetition is
  meaningful. This turns "attribute on the wrong element" into an immediate error.
- Keep the constructor a plain data holder: promote read-only properties, validate simple
  invariants, and do nothing else. An attribute must be cheap to instantiate.
- Read attributes with `ReflectionClass`/`ReflectionMethod::getAttributes(Name::class)`
  and call `->newInstance()` only when you actually need the object.
- Cache the reflection result — compile routes/validation maps at build or warmup time so
  production requests never pay for reflection. Frameworks do this; custom readers must too.
- Use attributes where they genuinely colocate config with code (routes, DI autowiring,
  validation, serialization). Do not invent an attribute for something a normal method
  call or constructor argument expresses more directly.
- Type attribute arguments with real types and enums, not loose strings, so the parser
  and static analysis catch mistakes at edit time.

## Examples

**Good Example** — typed metadata, targeted, read once and cached

```php
use Attribute;

// Metadata only: constrained to properties, immutable, no behavior.
#[Attribute(Attribute::TARGET_PROPERTY)]
final class MaxLength
{
    public function __construct(public readonly int $limit) {}
}

final class SignupForm
{
    #[MaxLength(50)]
    public string $username = '';
}

// A reader turns metadata into behavior — the attribute itself stays inert.
function lengthRules(string $class): array
{
    $rules = [];
    foreach ((new ReflectionClass($class))->getProperties() as $prop) {
        foreach ($prop->getAttributes(MaxLength::class) as $attr) {
            $rules[$prop->getName()] = $attr->newInstance()->limit; // cache this map!
        }
    }
    return $rules; // built once at warmup, not per request
}
```

**Bad Example** — logic and side effects inside the attribute

```php
#[Attribute(Attribute::TARGET_PROPERTY)]
final class MaxLength
{
    public function __construct(public int $limit)
    {
        // Side effect in a constructor that runs at unpredictable times → chaos.
        Logger::info("MaxLength applied");
        // Validation logic living inside metadata: readers cannot see it, cannot test it.
        if ($limit > 255) { throw new RuntimeException('too big'); }
    }
}

// And reflecting on every single request, paying the cost each time:
$rules = lengthRules(SignupForm::class); // no caching → reflection on the hot path
```

## Common Mistakes

- Treating an attribute as if it runs on its own; nothing happens until code reflects it.
- Omitting `#[Attribute(...)]` targets, so an attribute can be placed anywhere and misuse
  fails silently instead of erroring.
- Putting logic, I/O, or side effects in the attribute constructor — untestable, invisible,
  and executed at surprising moments.
- Reflecting on attributes inside a request loop with no caching, adding measurable latency.
- Using attributes for dynamic, runtime-varying data; attribute arguments must be
  compile-time constant expressions, not computed values.
- Reinventing configuration as attributes when a constructor argument or config file is
  clearer and easier to change.

## Production Tips

- Rely on the framework's compiled cache (Symfony container/router, Doctrine metadata) so
  attribute reflection happens at deploy/warmup, never per request. Clear it on deploy.
- If you write a custom reader, memoize per class and consider generating a static map at
  build time; runtime reflection over many classes adds up under load.
- Keep static analysis (PHPStan/Psalm) aware of your attributes so wrong targets and bad
  argument types are caught in CI, not production.

## AI Review Checklist

- Is every attribute class declared with `#[Attribute]` and constrained to valid targets?
- Is the attribute constructor pure data — no I/O, logging, or side effects?
- Are attribute arguments constant expressions, correctly typed (enums over strings)?
- Is attribute reflection cached/compiled rather than run on every request?
- Are attributes used for configuration, not to hide control flow that belongs in code?
- Does a distinct reader (not the attribute) turn the metadata into behavior?

## Related

- `knowledge/php/04-oop.md`
- `knowledge/php/23-modern-php.md`
- `knowledge/php/20-dependency-injection.md`
- `knowledge/php/15-testing.md`
