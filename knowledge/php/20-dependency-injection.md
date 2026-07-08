---
id: php/20-dependency-injection
topic: php
slug: dependency-injection
title: "Dependency Injection"
type: doc
order: 20
status: ready
tags: [php, dependency-injection]
related: [php/04-oop, php/21-design-patterns, php/15-testing, php/29-architecture]
when_to_use: "Read before wiring services together, adding a container, or refactoring code that news up its own collaborators."
---
# Dependency Injection

## Purpose

This document defines how to supply an object's collaborators from the outside —
dependency injection (DI) — and how a DI container fits in. It is written so an agent can
build classes that are testable and loosely coupled, and can tell the difference between
DI (a design principle) and a container (a tool that automates it).

DI means a class receives what it needs through its constructor or methods instead of
constructing those things itself. A **container** is optional infrastructure that resolves
and wires those dependencies for you.

## Why It Matters

A class that `new`s its own database connection, HTTP client, or clock is welded to those
concrete types. You cannot test it without a real database, cannot swap the implementation,
and cannot see its true dependencies without reading the whole body. Injecting
dependencies inverts that: collaborators become visible in the constructor signature,
substitutable in tests with a fake, and reconfigurable in one wiring location. The cost
is a small amount of wiring code (or a container to manage it) — cheap compared to the
untestable, rigid graph you get otherwise.

## Core Principles

- **Depend on abstractions, not concretions.** Type-hint an interface the class actually
  needs, so any conforming implementation can be injected. This is the "D" in SOLID.
- **Prefer constructor injection.** Required dependencies belong in the constructor so an
  object is never in a half-built state. Use setter/method injection only for optional ones.
- **Inject dependencies, not the container.** A class that receives the container can pull
  anything and hides its real needs — that is the Service Locator anti-pattern.
- **Composition happens at the edge.** Wire the object graph once, at the application's
  entry point (or in container config), not scattered through business logic.
- **A dependency is anything non-deterministic or external.** Clocks, randomness, the
  filesystem, and network clients are dependencies — inject them so they can be faked.

## Best Practices

- Declare every collaborator as a constructor parameter, ideally with PHP 8
  constructor property promotion, typed against an interface.
- Register bindings (interface → implementation) in the container's configuration, so the
  concrete choice lives in one place and can differ per environment.
- Configure services as **singletons/shared** when stateless, and as fresh instances when
  they carry request-scoped state; never share mutable request state as a singleton.
- Pass configuration values (DSNs, API keys) as explicit typed parameters or a config
  object — do not read `getenv()` deep inside a class.
- Keep constructors free of work: assign dependencies and return. No I/O, no side effects.
- For tests, construct the class directly with fakes; you should never need the container
  to unit-test a class — if you do, the class is over-coupled.

## Examples

**Good Example** — interface injection, no hidden dependencies

```php
interface Clock
{
    public function now(): DateTimeImmutable;
}

final class SubscriptionService
{
    // Both collaborators are explicit, abstract, and required.
    public function __construct(
        private readonly SubscriptionRepository $repository,
        private readonly Clock $clock, // injectable → time is controllable in tests
    ) {}

    public function isExpired(int $id): bool
    {
        $sub = $this->repository->find($id);
        return $sub->expiresAt < $this->clock->now(); // deterministic under a fake clock
    }
}

// Wiring lives at the composition root, e.g. container config:
$service = new SubscriptionService($repo, new SystemClock());
```

**Bad Example** — self-constructed, time-dependent, untestable

```php
final class SubscriptionService
{
    private PDO $db;

    public function __construct()
    {
        // Concrete dependency created inside: no seam to substitute a test double.
        $this->db = new PDO(getenv('DB_DSN')); // config read from deep inside, too
    }

    public function isExpired(int $id): bool
    {
        $sub = $this->find($id);
        return $sub->expiresAt < new DateTimeImmutable(); // real clock → non-deterministic test
    }
}
```

## Common Mistakes

- Injecting the container itself (Service Locator), so a class's real dependencies are
  invisible and anything can be resolved at runtime.
- Calling `new`, `getenv()`, `time()`, `rand()`, or static singletons inside a class,
  reintroducing the coupling DI was meant to remove.
- Type-hinting concrete classes everywhere, making implementations impossible to swap.
- Doing I/O or heavy work in the constructor, so simply creating the object has side effects.
- Registering request-stateful services as shared singletons, leaking state between requests.
- Over-abstracting: creating an interface for a type with exactly one implementation and no
  test-substitution need adds indirection with no payoff.

## Production Tips

- Use a mature container (Symfony DI, PHP-DI, or Laravel's) with autowiring so most
  bindings resolve from type hints; register explicit bindings only for interfaces.
- Compile/cache the container in production so resolution is not re-computed per request.
- Fail fast on a missing or ambiguous binding at boot (or in a CI container-lint step),
  not on the first request that needs the service.

## AI Review Checklist

- Are all required collaborators declared as typed constructor parameters?
- Are dependencies type-hinted against interfaces where substitution is plausible?
- Is the container injected anywhere it should not be (Service Locator)?
- Do any classes `new` collaborators, read env, or call `time()`/`rand()` internally?
- Is object-graph wiring confined to a composition root / container config?
- Can each class be unit-tested by constructing it directly with fakes?

## Related

- `knowledge/php/04-oop.md`
- `knowledge/php/21-design-patterns.md`
- `knowledge/php/15-testing.md`
- `knowledge/php/29-architecture.md`
