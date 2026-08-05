---
id: php/21-design-patterns
topic: php
slug: design-patterns
title: "PHP Design Patterns"
type: doc
order: 21
status: ready
tags: [php, design-patterns, InvalidArgumentException, plus, getInstance, self, total, __construct]
related: [php/04-oop, php/20-dependency-injection, php/22-clean-code, php/100-common-antipatterns]
when_to_use: "Read before reaching for a Gang-of-Four pattern, naming a class Manager/Factory/Strategy, or refactoring toward a known structure."
---
# PHP Design Patterns

## Purpose

This document defines how to apply design patterns in PHP: reusable solutions to
recurring design problems. It is written so an agent can pick the right pattern for a real
problem, implement it idiomatically, and — just as important — avoid forcing a pattern
where plain code would be clearer.

A pattern is a named shape (Strategy, Factory, Decorator, Observer, …), not a goal. The
goal is code that is easy to change; patterns are one means to that end.

## Why It Matters

Patterns give a shared vocabulary and battle-tested structures for problems like "swap an
algorithm at runtime" or "add behavior without editing a class." Used well, they make
intent legible: a reviewer who sees "Strategy" instantly knows how to extend it. Used
badly — a `SingletonFactoryManager` wrapping three lines — they add indirection, hide the
real logic, and make code harder to change than the naive version. The skill is not
knowing patterns; it is recognizing when a problem actually has the shape a pattern solves.

## Core Principles

- **A pattern must solve a problem you actually have.** Introduce one to remove real
  duplication or rigidity, never speculatively "for flexibility we might need."
- **Favor composition and small interfaces over deep inheritance.** Most GoF patterns
  (Strategy, Decorator, Adapter) are composition dressed up; inheritance hierarchies are not.
- **Program to an interface.** Patterns that vary behavior work because callers depend on
  an abstraction, not a concrete class — the same principle as dependency injection.
- **Prefer the simplest structure that works.** A closure or a `match` often replaces a
  full Strategy class hierarchy; a plain constructor often beats a Factory.
- **Avoid mutable global state.** Singleton is a global variable in a costume; it breaks
  testability and isolation. Reach for a shared service in a DI container instead.

## Best Practices

- Use **Strategy** (an interface with interchangeable implementations, or a first-class
  callable) when you must swap an algorithm at runtime — pricing rules, sort orders, exporters.
- Use a **Factory** when construction is non-trivial or the concrete type is chosen at
  runtime; skip it when `new` with clear arguments is enough.
- Use **Decorator** to add cross-cutting behavior (caching, logging, retries) around an
  interface without editing the wrapped class — compose, do not subclass.
- Use **Adapter** to fit a third-party or legacy API to the interface your code expects,
  isolating the foreign shape at one boundary.
- Use **Value Object** and **Repository** to keep domain models pure and persistence
  concerns separate; these carry more weight in PHP apps than the flashy creational patterns.
- Name classes for their role, not their pattern, unless the pattern is the contract
  (`PriceStrategy` is fine; `UserManager` names nothing).

## Examples

**Good Example** — Strategy via an interface, selected by injection

```php
interface ShippingCost
{
    public function for(Order $order): Money;
}

final class FlatRate implements ShippingCost
{
    public function for(Order $order): Money { return Money::eur(500); }
}

final class WeightBased implements ShippingCost
{
    public function for(Order $order): Money
    {
        return Money::eur($order->totalWeightGrams() * 2);
    }
}

final class Checkout
{
    // The algorithm varies without Checkout knowing which one — open for extension.
    public function __construct(private readonly ShippingCost $shipping) {}

    public function total(Order $order): Money
    {
        return $order->subtotal()->plus($this->shipping->for($order));
    }
}
```

**Bad Example** — pattern soup where a conditional would do

```php
// A Singleton "factory" wrapping a one-line calculation: global state, no seam,
// impossible to test in isolation, and far harder to read than the logic it hides.
final class ShippingCostFactoryManager
{
    private static ?self $instance = null;
    public static function getInstance(): self
    {
        return self::$instance ??= new self(); // hidden global, shared across all requests
    }

    public function calculate(string $type, Order $order): int
    {
        // A plain match on a value would be clearer and testable — no class needed.
        if ($type === 'flat')   return 500;
        if ($type === 'weight') return $order->totalWeightGrams() * 2;
        throw new InvalidArgumentException($type);
    }
}
```

## Common Mistakes

- Adding patterns speculatively, producing layers of indirection for flexibility never used.
- Using Singleton for shared services, smuggling in global mutable state that breaks tests.
- Naming classes `Manager`, `Helper`, `Util`, or `Processor` — grab-bags with no cohesive
  responsibility, usually a sign the design has no real pattern at all.
- Building a Factory/Builder for objects a simple typed constructor creates cleanly.
- Deep inheritance to "reuse" code where a Decorator or plain composition belongs.
- Treating patterns as the goal, refactoring working simple code into a textbook diagram.

## Production Tips

- Let the DI container own object lifetimes (shared vs. per-request); do not hand-roll
  Singletons to control instance count.
- When a `match`/closure Strategy grows conditionals per branch, promote it to an interface
  with implementations; when a class hierarchy has one trivial member, collapse it back.

## AI Review Checklist

- Does each pattern solve a concrete, present problem rather than a hypothetical one?
- Is there any Singleton / static mutable state that should be a DI-managed service?
- Do varying-behavior patterns depend on an interface, keeping callers open for extension?
- Are there `Manager`/`Helper`/`Util` classes that should be split by responsibility?
- Would a closure, `match`, or plain constructor be simpler than the pattern used here?

## Related

- `knowledge/php/04-oop.md`
- `knowledge/php/20-dependency-injection.md`
- `knowledge/php/22-clean-code.md`
- `knowledge/php/100-common-antipatterns.md`
