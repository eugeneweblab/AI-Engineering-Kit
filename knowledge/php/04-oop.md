---
id: php/04-oop
topic: php
slug: oop
title: "OOP"
type: doc
order: 4
status: ready
tags: [php, oop, readonly, isActive, time, __construct, InvalidArgumentException]
related: [php/02-types, php/05-namespaces, php/19-enums, php/20-dependency-injection, php/21-design-patterns]
when_to_use: "Read before designing a class hierarchy, interface, or trait, or when reviewing OOP code."
---
# OOP

## Purpose

This document defines how to model behavior with PHP's object system: classes, interfaces,
abstract classes, traits, visibility, constructor promotion, `readonly`, `final`, and the
enum-as-object features. It covers the design decisions that keep objects encapsulated,
substitutable, and easy to test.

## Why It Matters

Objects are how PHP applications manage complexity: they bundle state with the operations
allowed on it and hide the rest. Done well, an object exposes a small, typed surface and
guarantees its own invariants. Done badly — public mutable state, deep inheritance, "god"
classes — objects become tangled shared state that any code can corrupt. Modern PHP
(8.1–8.4) added the tools (promotion, `readonly`, enums, first-class DI-friendly design)
to do it well; the rules below apply them.

## Core Principles

- **Encapsulate: default to `private`.** Expose behavior through methods, not raw
  properties. Public mutable state lets any caller break an invariant you cannot then
  guarantee.
- **Depend on interfaces, not concretions.** Type-hint the abstraction (`LoggerInterface`)
  so implementations are swappable and mockable. This is the basis of
  [dependency-injection](20-dependency-injection.md).
- **Favor composition over inheritance.** Inheritance couples a subclass to a parent's
  internals; composition wires small objects together. Use inheritance only for a genuine
  "is-a" relationship, and keep hierarchies shallow.
- **Make objects immutable where you can.** `readonly` properties set in the constructor
  cannot change afterward, eliminating a class of aliasing bugs. See [types](02-types.md).
- **Mark classes `final` by default.** A class open for extension is a contract you must
  maintain forever; make it explicit and open one only when you designed for subclassing.

## Best Practices

- Use **constructor property promotion** to declare and assign dependencies in one place;
  it removes boilerplate and keeps the type next to the assignment.
- Use **`readonly` classes** (PHP 8.2+) for value objects and DTOs so the whole object is
  immutable without annotating each property.
- Use **traits** for genuinely shared, stateless behavior — not as a substitute for a
  collaborator you should inject. Traits copy code in at compile time; overuse hides
  dependencies.
- Validate invariants in the constructor and throw on violation, so an object cannot exist
  in an invalid state.
- Prefer **enums** (backed or pure) over class constants for a closed set of values; they
  are type-safe and can carry methods. See [enums](19-enums.md).
- Keep interfaces small and role-based (Interface Segregation); a fat interface forces
  implementers to stub methods they do not need.

## Examples

**Good Example** — encapsulated, immutable, interface-driven

```php
<?php

declare(strict_types=1);

interface Clock // depend on the abstraction, not on time() directly
{
    public function now(): \DateTimeImmutable;
}

final readonly class Subscription // readonly: state is fixed after construction
{
    public function __construct(
        private \DateTimeImmutable $startsAt,   // promoted + private: no external mutation
        private \DateInterval $period,
    ) {
        // Invariant enforced at construction: an invalid Subscription cannot exist.
        if ($period->days !== null && $period->days < 1) {
            throw new \InvalidArgumentException('period must be at least one day');
        }
    }

    public function isActive(Clock $clock): bool // injected Clock → testable, no hidden now()
    {
        return $clock->now() < $this->startsAt->add($this->period);
    }
}
```

**Bad Example** — leaky state, hidden dependency, open to corruption

```php
<?php

class Subscription {
    public $startsAt;   // public + mutable: any code can overwrite it later
    public $days;       // no invariant; -5 days is representable

    function __construct($startsAt, $days) {
        $this->startsAt = $startsAt; // accepts any type; no validation
        $this->days = $days;
    }

    function isActive() {
        // Reads the real clock directly → cannot be tested without freezing system time.
        return time() < strtotime($this->startsAt) + $this->days * 86400;
    }
}
```

## Common Mistakes

- Public mutable properties instead of private state behind methods.
- Deep inheritance chains where composition or a strategy object would be clearer.
- Type-hinting concrete classes, making code impossible to mock or swap.
- Calling `time()`, `new PDO(...)`, or other collaborators inside a method instead of
  injecting them.
- Using traits to share state, which hides dependencies and creates implicit coupling.
- Objects that can be constructed in an invalid state because the constructor validates
  nothing.

## Production Tips

- Let a DI container wire dependencies; do not `new` collaborators inside domain classes.
  See [dependency-injection](20-dependency-injection.md).
- Static analysis at a strict level will flag missing property types and unsafe casts that
  break encapsulation — run it in CI.

## AI Review Checklist

- Are properties `private` (or `readonly`) with behavior exposed through methods?
- Do methods depend on interfaces rather than concrete classes?
- Are value objects/DTOs immutable via `readonly`?
- Are collaborators (clock, DB, HTTP) injected rather than created inside methods?
- Is inheritance shallow and used only for true "is-a"; is composition preferred otherwise?
- Do constructors enforce invariants so no invalid object can exist?
- Are closed value sets modeled as enums rather than loose constants?

## Related

- `knowledge/php/02-types.md`
- `knowledge/php/05-namespaces.md`
- `knowledge/php/19-enums.md`
- `knowledge/php/20-dependency-injection.md`
- `knowledge/php/21-design-patterns.md`
