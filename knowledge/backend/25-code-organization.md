---
id: backend/25-code-organization
topic: backend
slug: code-organization
title: "Code Organization"
type: doc
order: 25
status: ready
tags: [backend, code-organization, helpers, eslint-plugin-boundaries]
related: [backend/02-layered-architecture, backend/03-clean-architecture, backend/07-business-logic, backend/24-documentation]
when_to_use: "Read before creating a new module, restructuring a service, or deciding where a new piece of code belongs."
---
# Code Organization

## Purpose

This document defines how to physically structure a backend codebase: how to group files,
draw module boundaries, manage dependencies between modules, and decide where a new piece
of code belongs. It is about the *shape* of the code on disk, which shapes how it can be
changed. Architecture (see [layered](02-layered-architecture.md) and
[clean architecture](03-clean-architecture.md)) decides the layers; this document decides
how those layers map to folders, packages, and import rules.

## Why It Matters

The structure of a codebase is the most-used and least-documented interface a team has.
Every change starts with "where does this go?" — and a bad answer compounds. Code
organized by technical role (all controllers here, all models there) scatters a single
feature across the tree, so a one-feature change touches ten folders. Modules with tangled
dependencies cannot be tested, reused, or deleted independently. Good organization makes
the common change local, the boundary obvious, and the illegal dependency impossible to
write by accident.

## Core Principles

- **Organize by feature/domain, not by technical layer.** Group everything that changes
  together — a `billing` module — so a change stays in one place. Package-by-layer
  spreads one feature across the whole tree.
- **Dependencies point inward, one direction only.** Business logic must not import
  framework, HTTP, or database code. Enforce it, do not just intend it.
- **A module exposes an explicit public surface.** Everything else is internal. If any
  file can import any other file, there are no modules — only files.
- **High cohesion, low coupling.** Things that change together live together; things that
  change independently do not reach into each other's internals.
- **Make the boundary structural.** A rule that lives only in a wiki gets violated. Encode
  it in the build (import linter, module system, package visibility).

## Best Practices

- Structure top-level folders by bounded context (`orders/`, `payments/`, `identity/`),
  each containing its own domain, application, and adapter code.
- Keep the domain core (entities, business rules) free of any import from web, ORM, or
  queue libraries so it stays testable in isolation and portable across frameworks.
- Define an explicit public API per module (an `index`, `__init__`, or exported barrel);
  keep everything else package-private.
- Enforce allowed dependency directions with a tool — `import-linter` (Python),
  `eslint-plugin-boundaries` / `dependency-cruiser` (TS), `go vet`/internal packages, or
  ArchUnit (JVM) — so violations fail CI.
- Put shared, dependency-free utilities in a small `shared`/`common` module; resist making
  it a dumping ground that everything depends on.
- Keep files small and named for their responsibility; a 2,000-line "utils" file is a
  missing set of modules.
- Co-locate tests with the code they test, or mirror the structure exactly, so tests move
  when code moves.

## Examples

**Good Example** — package by feature, dependencies point inward

```
src/
  orders/
    domain/order.py          # pure business rules, no framework imports
    application/place_order.py
    adapters/http_routes.py   # imports application, never the reverse
    adapters/order_repo_sql.py
    __init__.py               # exports only place_order + Order
  payments/
    ...
# A change to "how orders are placed" lives entirely under orders/.
# http_routes may import application; domain may import nothing outward.
```

**Bad Example** — package by layer, everything reaches everywhere

```
src/
  controllers/    # order, payment, user controllers mixed together
  models/         # order, payment, user models mixed together
  services/       # one god-folder, no boundaries
# Adding one field to "order" edits three distant folders.
# models/order.py imports controllers/ for a helper -> circular, untestable,
# and nothing in the build stops it.
```

## Common Mistakes

- Packaging by technical layer, forcing every feature change to sprawl across the tree.
- A `utils`/`helpers` module that everything imports, creating a hidden hub of coupling.
- Circular imports between modules — a sign the boundary is in the wrong place.
- Business logic that imports the ORM or web framework, making it impossible to unit-test
  without a database or HTTP server.
- No enforced import rules, so architecture decays silently one convenient import at a
  time.
- One giant module because splitting "felt premature" — until it is 50 files and untouchable.

## Production Tips

- Add the dependency linter to CI on day one; retrofitting boundaries into a tangled
  codebase costs far more than preventing them.
- When a module's public surface keeps growing, that is a signal to split it — not to widen
  the interface.

## AI Review Checklist

- Is code grouped by feature/domain rather than by technical layer?
- Does the domain core avoid importing framework, ORM, or transport libraries?
- Does each module expose an explicit public API, with the rest kept internal?
- Are allowed dependency directions enforced by a linter in CI, not just documented?
- Are there any circular dependencies between modules?
- Do tests live with (or mirror) the code they cover?

## Related

- `knowledge/backend/02-layered-architecture.md`
- `knowledge/backend/03-clean-architecture.md`
- `knowledge/backend/07-business-logic.md`
- `knowledge/backend/24-documentation.md`
