---
id: typescript/27-library-design
topic: typescript
slug: library-design
title: "Library Design"
type: doc
order: 27
status: ready
tags: [typescript, library-design]
related: [typescript/08-generics, typescript/09-utility-types, typescript/14-modules, typescript/16-configuration]
when_to_use: "Read before designing a public TypeScript API, package exports, or shipping type declarations."
---
# Library Design

## Purpose

This document defines how to design a TypeScript library that others depend on: its
public API, its type declarations, and its package configuration. The audience is
consumers you will never meet, on TypeScript versions you do not control. The goal is an
API that is hard to misuse and safe to evolve.

A library's types *are* its contract. Once published, every exported type is a promise;
breaking it breaks builds across every downstream project at once.

## Why It Matters

Application code can be refactored freely because you own every caller. Library code
cannot — a careless change to an exported signature is a breaking change for strangers,
surfacing as red builds they cannot fix. Worse, TypeScript makes some "compatible-looking"
changes silently breaking (widening a return type, adding a required parameter). Good
library design front-loads this discipline: precise types, minimal surface, and explicit
versioning, so consumers can upgrade with confidence instead of fear.

## Core Principles

- **Export the smallest surface that works.** Every exported name is a maintenance
  obligation and a potential breaking change. What is not exported can change freely.
- **Make illegal states unrepresentable.** Model the API so the compiler rejects misuse,
  rather than documenting rules the caller must remember.
- **Accept wide, return narrow.** Take the most general input you can (`readonly T[]`,
  interfaces over concrete classes) and return the most specific type you can.
- **Types are the contract; version them.** Any change to an exported signature follows
  semver. Widening what you return or requiring a new argument is a major bump.
- **Do not leak internals.** Never export a type that references a private or `@internal`
  shape; consumers will depend on it and you will be unable to change it.

## Best Practices

- Ship your own `.d.ts` types (via `"types"`/`"exports"` in `package.json`); do not make
  consumers install a separate `@types` package for a TS-native library.
- Use the `exports` field with explicit `types`, `import`, and `require` conditions so
  types resolve correctly under `moduleResolution: "bundler"`/`"node16"`. See
  [modules](14-modules.md) and [configuration](16-configuration.md).
- Prefer `interface` for public object contracts consumers may need to extend, and
  discriminated unions for closed sets of variants. See [utility types](09-utility-types.md).
- Keep generic parameters inferable from arguments; a generic the caller must specify by
  hand is a design smell. Provide sensible defaults (`<T = unknown>`). See
  [generics](08-generics.md).
- Mark deprecations with `@deprecated` JSDoc so editors warn before you remove anything.
- Compile with `declaration: true` and `strict: true`; test the emitted `.d.ts` against a
  real consumer project or with `tsd`/`@arethetypeswrong/cli`.
- Avoid `enum` in public APIs (it emits runtime code and has assignability quirks); prefer
  a union of string literals or `as const` objects.
- Do not re-export third-party types you do not control from your public surface unless
  you intend to own that compatibility forever.

## Examples

**Good Example** — narrow return, inferable generic, illegal states excluded

```ts
// Discriminated union: a caller cannot read `data` on an error, or `error` on success.
export type Result<T, E = Error> =
  | { ok: true; data: T }
  | { ok: false; error: E };

// T is inferred from `fn`; the caller never writes the type parameter by hand.
export async function attempt<T>(fn: () => Promise<T>): Promise<Result<T>> {
  try {
    return { ok: true, data: await fn() };
  } catch (error) {
    return { ok: false, error: error as Error };
  }
}
// Accepts a wide input (readonly), returns a precise type.
export function first<T>(items: readonly T[]): T | undefined {
  return items[0];
}
```

**Bad Example** — leaky, loose, and impossible to evolve safely

```ts
// `any` return: every consumer loses type safety and depends on runtime behaviour.
export function attempt(fn: Function): any { /* ... */ }

// Exposes an internal type; you can now never rename or change _InternalNode.
export function build(node: _InternalNode): _InternalNode { /* ... */ }

// Generic the caller must specify manually, with no default and no inference site.
export function make<T>(): T {
  return {} as T; // and it lies about the runtime value
}
```

## Common Mistakes

- Exporting internal or third-party types, then being unable to change them without a
  breaking release.
- Returning `any` or an over-wide type, pushing type work onto every consumer.
- Requiring callers to pass generic parameters that could be inferred.
- Using `enum` in the public API, emitting runtime code and creating nominal quirks.
- Missing or wrong `exports`/`types` fields, so types fail to resolve under modern module
  resolution.
- Widening a return or adding a required parameter without a major version bump.

## Production Tips

- Run `@arethetypeswrong/cli` in CI to catch broken `exports`/`types` resolution before
  publishing.
- Keep a changelog and follow semver strictly; automate release notes from commits.
- Add an example consumer package in the repo that type-checks against the built output,
  so a breaking type change fails CI, not a user's build.

## AI Review Checklist

- Is the exported surface minimal, with no internal or private types leaked?
- Are inputs accepted wide (`readonly`, interfaces) and outputs returned narrow?
- Are generics inferable from arguments, with defaults where useful?
- Does `package.json` expose `types`/`exports` correctly for modern resolution?
- Are breaking type changes gated behind a major version bump?
- Are public variant sets modeled as discriminated unions rather than loose objects?

## Related

- `knowledge/typescript/08-generics.md`
- `knowledge/typescript/09-utility-types.md`
- `knowledge/typescript/14-modules.md`
- `knowledge/typescript/16-configuration.md`
