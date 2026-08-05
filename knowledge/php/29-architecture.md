---
id: php/29-architecture
topic: php
slug: architecture
title: "PHP Architecture"
type: doc
order: 29
status: ready
tags: [php, architecture, UserRepository, existsByEmail, exists, store, __construct, declare]
related: [php/20-dependency-injection, php/21-design-patterns, php/04-oop, php/26-best-practices, php/09-exceptions]
when_to_use: "Read before structuring a new PHP application or a significant refactor of its layers."
---
# PHP Architecture

## Purpose

This document defines how to structure a PHP application so that business logic is
independent of the framework, the database, and the delivery mechanism (HTTP, CLI, queue).
It covers layering, dependency direction, and where PHP-specific pieces (Composer, PSR
interfaces, DI containers) fit. The aim is code where the core rules can be read, tested,
and changed without touching a controller or an ORM.

Architecture here means the arrangement of dependencies, not a specific framework. A good
PHP architecture makes the framework a detail you could replace, not the center of gravity.

## Why It Matters

Most PHP projects are organized around a framework: logic lives in controllers, and models
extend the ORM. That is fast to start and slow to change — business rules become entangled
with HTTP and SQL, so you cannot test them without a database or reuse them from a CLI
command. When the framework needs upgrading or the rules need to move to a queue worker,
the whole thing resists. Putting the domain at the center, with the framework at the edges,
keeps the expensive part (business logic) cheap to test and durable across framework churn.

## Core Principles

- **Dependencies point inward.** The domain depends on nothing; the application layer
  depends on the domain; the framework/infrastructure depends on both. Never the reverse.
- **Depend on interfaces, not implementations.** The domain defines a `RepositoryInterface`;
  infrastructure implements it. This is the seam that makes the core testable and swappable.
- **Keep the framework at the edge.** Controllers, ORM entities, and console commands are
  adapters — thin translators between the outside world and use cases.
- **A use case is a single business operation.** One class, one `__invoke`/`handle` method,
  explicit inputs and outputs. It orchestrates the domain; it contains no HTTP or SQL.
- **Model the domain in plain PHP.** Entities and value objects are `final` classes with
  behavior and invariants — not anemic bags of getters/setters mapped to tables.

## Best Practices

- Separate at least three layers: **domain** (entities, value objects, domain services),
  **application** (use cases / handlers), and **infrastructure** (framework, DB, HTTP,
  external APIs). Enforce the direction with a static tool (Deptrac).
- Define repository and gateway *interfaces* in the domain/application layer; bind them to
  concrete implementations in the container, so the core never names Eloquent/Doctrine.
- Inject dependencies through constructors resolved by a PSR-11 container; do not use
  service locators or static facades inside domain/application code.
- Keep controllers thin: parse and validate input, call one use case, format the response.
  Business decisions do not belong in a controller.
- Return typed results and throw domain exceptions from use cases; let an infrastructure
  layer map those to HTTP status codes.
- Choose the scale deliberately: a modular monolith with clear internal boundaries is the
  right default; reach for microservices only when independent scaling/deploy demands it.

## Examples

**Good Example** — domain defines the interface, infrastructure implements it

```php
<?php
declare(strict_types=1);

// Application layer: a use case orchestrates the domain, knows nothing about HTTP or SQL.
final class RegisterUser
{
    public function __construct(private UserRepository $users) {} // domain interface

    public function __invoke(EmailAddress $email, HashedPassword $password): UserId
    {
        if ($this->users->existsByEmail($email)) {
            throw new EmailAlreadyTaken($email); // domain exception, not an HTTP 409
        }
        $user = User::register($email, $password); // entity enforces its own invariants
        $this->users->save($user);
        return $user->id();
    }
}

// Infrastructure implements the domain's interface — swappable, and the core never sees it.
final class DoctrineUserRepository implements UserRepository { /* ... */ }
```

**Bad Example** — logic trapped in the controller and ORM

```php
<?php
final class UserController
{
    public function store(Request $request): JsonResponse
    {
        // Business rule, validation, persistence, and HTTP all fused in the framework edge.
        if (User::where('email', $request->email)->exists()) { // domain rule via ORM
            return response()->json(['error' => 'taken'], 409);
        }
        // Untestable without a DB and an HTTP request; unusable from a CLI or queue worker.
        $user = User::create($request->all());
        return response()->json($user, 201);
    }
}
```

## Common Mistakes

- Business logic in controllers or ORM models, so it cannot be tested or reused off HTTP.
- The domain layer importing framework/ORM classes, inverting the dependency direction.
- Anemic entities (only getters/setters) with rules scattered across services.
- Static facades and service locators inside domain code, hiding dependencies.
- Jumping to microservices for organizational reasons before a modular monolith is exhausted.
- No enforced boundaries, so layering exists in docs but not in the actual imports.

## Production Tips

- Enforce the dependency rule mechanically with Deptrac or PHPStan rules in CI; a boundary
  that is not checked erodes within weeks.
- Keep use cases free of framework types so the same core can be driven by a controller
  today and a queue consumer tomorrow without change.

## AI Review Checklist

- Do dependencies point inward — domain depends on nothing framework-specific?
- Does the domain define repository/gateway interfaces that infrastructure implements?
- Are controllers thin adapters that call a single use case?
- Is business logic in domain entities/services, not in ORM models or controllers?
- Are dependencies injected via constructor (PSR-11), not fetched via static facades?
- Are layer boundaries enforced by a tool in CI, not just described in docs?

## Related

- `knowledge/php/20-dependency-injection.md`
- `knowledge/php/21-design-patterns.md`
- `knowledge/php/04-oop.md`
- `knowledge/php/26-best-practices.md`
- `knowledge/php/09-exceptions.md`
