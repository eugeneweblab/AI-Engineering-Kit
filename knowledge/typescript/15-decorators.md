---
id: typescript/15-decorators
topic: typescript
slug: decorators
title: "Decorators"
type: doc
order: 15
status: ready
tags: [typescript, decorators]
related: [typescript/16-configuration, typescript/13-advanced-types, typescript/22-design-patterns, typescript/14-modules]
when_to_use: "Read before writing a decorator, or picking between the standard and legacy `experimentalDecorators` modes."
---
# Decorators

## Purpose

This document defines how to use decorators in TypeScript: what they are (functions that
observe or replace a class, method, accessor, field, or getter/setter at definition time),
the difference between the **standard ECMAScript decorators** (TC39 Stage 3, the default in
2026) and the **legacy `experimentalDecorators`** flavor, and when a decorator is the right
tool versus a plain function.

Decorators add cross-cutting behavior — logging, validation, memoization, dependency
injection metadata — declaratively at the point of definition. They are a sharp tool: elegant
when they encode a genuine cross-cutting concern, confusing when they hide ordinary logic.

## Why It Matters

Decorators run *implicitly*. A reader cannot see what `@Cache` does from the call site, so an
opaque or side-effecting decorator makes code harder to reason about, not easier. Worse, the
ecosystem is mid-migration: the standard decorators (Stage 3) and the old experimental ones
have **different signatures, different execution order, and incompatible metadata models**.
Frameworks like NestJS, TypeORM, and Angular still rely on the legacy mode plus
`reflect-metadata`; new standalone code should target the standard. Choosing the wrong mode,
or mixing them, produces runtime errors that type-checking never reveals. Understanding which
model you are in is the whole game.

## Core Principles

- **Know which decorator model you are in.** Standard (Stage 3) is the default with modern
  `tsc`/`target`; legacy requires `"experimentalDecorators": true`. Their APIs are not
  interchangeable.
- **A decorator should be transparent and side-effect-light at definition time.** It runs when
  the class is defined; heavy work or surprising mutations there are a trap.
- **Use a decorator only for cross-cutting concerns.** If the behavior belongs to one method's
  core logic, write it inline; decorators are for orthogonal aspects.
- **Follow the framework, not your preference.** Inside NestJS/Angular/TypeORM, use their
  decorators and their required config; do not fight the framework's model.
- **Prefer composition over a decorator when either works.** A higher-order function or
  wrapper is explicit and needs no compiler flag.

## Best Practices

- For new, framework-free code, use **standard decorators**: signature
  `(value, context) => value | void`, where `context` carries `kind`, `name`, `addInitializer`,
  and `static`/`private` flags.
- For framework code, keep `"experimentalDecorators": true` and `"emitDecoratorMetadata": true`
  and import `reflect-metadata` once at the entry point — those frameworks depend on it.
- Do not mix the two models in one project unless the build is explicitly configured for it;
  pick one and be consistent.
- Keep decorator *factories* (`@log("info")`) pure: the outer call configures, the returned
  decorator applies — no I/O in either.
- Preserve the original behavior when replacing a method: call through to it and return its
  result, keeping `this` bound correctly.
- Document what each custom decorator does and its ordering, since application order
  (bottom-up for a stacked list) is not obvious from the source.

## Examples

**Good Example** — standard decorator that wraps without changing intent

```ts
// Standard (Stage 3) method decorator: logs entry, then delegates unchanged.
function logged<A extends any[], R>(
  target: (this: unknown, ...args: A) => R,
  context: ClassMethodDecoratorContext,
) {
  return function (this: unknown, ...args: A): R {
    console.log(`calling ${String(context.name)}`);
    return target.apply(this, args); // preserve `this` and the real return value
  };
}

class Service {
  @logged
  fetch(id: string) { return `item:${id}`; } // core logic stays here, undecorated
}
```

**Bad Example** — hidden side effects and a mode mismatch

```ts
// Assumes legacy metadata (needs experimentalDecorators + reflect-metadata) but the project
// targets standard decorators → this signature is wrong and fails at runtime.
function Injectable(target: any) {
  registry.push(new target());           // instantiates at definition time — surprising side effect
  fetch("/telemetry/registered");        // network I/O when the class is merely defined
}

@Injectable
class Repo { /* ... */ } // reader cannot see any of the above from here
```

## Common Mistakes

- Mixing standard and legacy decorators, or copying a legacy-signature decorator into a
  standard-mode project (and vice versa) — the signatures differ.
- Forgetting `import "reflect-metadata"` (or `emitDecoratorMetadata`) in a framework that needs
  it, causing DI/ORM to fail at runtime.
- Doing I/O, instantiation, or global mutation at definition time, so importing a file has
  side effects.
- Replacing a method but losing `this` binding or not returning the original result.
- Using a decorator for logic that belongs inline, hiding core behavior from readers.
- Relying on decorator evaluation order without documenting it; stacked decorators apply
  bottom-to-top.

## Production Tips

- Pin the decorator mode explicitly in `tsconfig` and note it in the README; a silent default
  change during a `tsc` upgrade can break a whole DI graph.
- When adopting standard decorators, migrate framework code only after that framework
  officially supports them — check its version, do not assume.
- Add a test that constructs and exercises decorated classes; decorator bugs surface at
  instantiation, not compilation.

## AI Review Checklist

- Is the project's decorator mode (standard vs `experimentalDecorators`) explicit and
  consistent across all decorators?
- Does each custom decorator avoid I/O, instantiation, and global mutation at definition time?
- When a method is wrapped, is `this` preserved and the original return value passed through?
- For framework code, are `reflect-metadata` and `emitDecoratorMetadata` present where
  required?
- Is the decorator a genuine cross-cutting concern rather than hidden core logic?

## Related

- `knowledge/typescript/16-configuration.md`
- `knowledge/typescript/13-advanced-types.md`
- `knowledge/typescript/22-design-patterns.md`
- `knowledge/typescript/14-modules.md`
