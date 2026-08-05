---
id: php/26-best-practices
topic: php
slug: best-practices
title: "PHP Best Practices"
type: doc
order: 26
status: ready
tags: [php, best-practices, DomainException, declare, InvalidArgumentException, final, self, readonly]
related: [php/23-modern-php, php/22-clean-code, php/02-types, php/09-exceptions, php/13-security]
when_to_use: "Read before writing or reviewing any non-trivial PHP class or function."
---
# PHP Best Practices

## Purpose

This document collects the default habits that make PHP code correct, readable, and safe
across a whole team: strict types, immutability where it fits, narrow scope, explicit
errors, and modern language features. It is the baseline an agent should apply to every
file unless a specific doc overrides it. Deeper topics (security, testing, architecture)
have their own docs; this is the everyday hygiene layer.

These are defaults, not dogma. Each rule states the reason and the cost so you can tell
when an exception is justified.

## Why It Matters

PHP is permissive: it will coerce types, swallow undefined variables as `null`, and let a
function reach into global state. That flexibility is how legacy PHP earned its reputation.
Modern PHP (8.x) gives you the tools — `declare(strict_types=1)`, readonly properties,
enums, typed properties, first-class callables — to write code as safe as any statically
typed language. Applying these defaults prevents whole classes of bugs (silent coercion,
null surprises, mutation-at-a-distance) before they reach review or production.

## Core Principles

- **Turn on strict types.** Put `declare(strict_types=1);` at the top of every file so PHP
  rejects `"5"` where an `int` is required instead of silently coercing it.
- **Type everything.** Parameters, return values, and properties all get types. An untyped
  signature is an unstated assumption the next reader has to reverse-engineer.
- **Prefer immutability.** Use `readonly` properties and value objects; a value that cannot
  change cannot be corrupted by a distant caller. The cost is more object creation — cheap.
- **Fail with exceptions, not sentinels.** Return a typed value or throw; do not return
  `false`/`null` to mean "error" — callers forget to check and the bug moves downstream.
- **Keep scope small.** No global state, short functions, injected dependencies. Small scope
  is what makes code testable and reviewable.

## Best Practices

- Make classes `final` by default; open them for extension only when you have a real
  subclass, because inheritance is a commitment that is hard to walk back.
- Prefer composition and dependency injection over static calls and `new` inside a class,
  so behavior can be swapped and tested. See dependency-injection doc.
- Use `match` over `switch` for value mapping — `match` is strict (`===`), returns a value,
  and has no fall-through, eliminating the classic missing-`break` bug.
- Model closed sets of values as `enum`s, not string constants, so an invalid value cannot
  be constructed and the type system enforces exhaustiveness.
- Name things for intent: `activeSubscribers()` not `getData()`. The reader should not need
  the body to know what a method returns.
- Validate input at the boundary (controller, CLI, queue consumer) and pass typed value
  objects inward, so the core never re-checks the same thing.
- Use `??` and `?->` to handle absence explicitly instead of suppressing notices with `@`.

## Examples

**Good Example** — strict types, readonly value object, explicit failure

```php
<?php
declare(strict_types=1); // reject silent type coercion for the whole file

final class Money
{
    public function __construct(
        public readonly int $cents,       // immutable: cannot be mutated after construction
        public readonly Currency $currency // enum, not a raw string
    ) {
        if ($cents < 0) {
            throw new InvalidArgumentException('Money cannot be negative'); // fail loudly
        }
    }

    public function add(Money $other): self
    {
        if ($this->currency !== $other->currency) {
            throw new DomainException('Currency mismatch'); // explicit, typed error
        }
        return new self($this->cents + $other->cents, $this->currency); // returns a new value
    }
}
```

**Bad Example** — loose types, mutation, sentinel return

```php
<?php
// No declare(strict_types=1): "100" silently becomes 100, hiding caller bugs.

class Money
{
    public $cents;    // untyped, public, mutable — any caller can corrupt it
    public $currency; // raw string like "usd" vs "USD" — no validation

    public function add($other)
    {
        if ($this->currency != $other->currency) {
            return false; // sentinel: caller who forgets to check treats false as Money
        }
        $this->cents += $other->cents; // mutates self — action at a distance
        return $this;
    }
}
```

## Common Mistakes

- Omitting `declare(strict_types=1)`, so `"5"` passes where an `int` is expected.
- Public mutable properties, letting any caller put an object into an invalid state.
- Returning `false`/`null`/`-1` to signal errors instead of throwing a typed exception.
- Deep inheritance hierarchies where composition would be clearer and testable.
- `switch` with loose comparison and fall-through where `match` is safer.
- Suppressing notices with `@` instead of handling the missing value with `??`/`?->`.

## AI Review Checklist

- Does every file start with `declare(strict_types=1);`?
- Are all parameters, returns, and properties typed?
- Are value objects `readonly` / immutable where mutation is not required?
- Do errors throw typed exceptions rather than returning `false`/`null`?
- Are closed value sets modeled as `enum`s instead of string constants?
- Are classes `final` unless a real subclass justifies extension?
- Is input validated at the boundary and passed inward as typed values?

## Related

- `knowledge/php/23-modern-php.md`
- `knowledge/php/22-clean-code.md`
- `knowledge/php/02-types.md`
- `knowledge/php/09-exceptions.md`
- `knowledge/php/13-security.md`
