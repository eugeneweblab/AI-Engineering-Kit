---
id: typescript/16-configuration
topic: typescript
slug: configuration
title: "TypeScript Configuration"
type: doc
order: 16
status: ready
tags: [typescript, configuration, target, module, tsconfig.json, strictNullChecks]
related: [typescript/14-modules, typescript/29-tooling, typescript/15-decorators, typescript/28-best-practices]
when_to_use: "Read before creating or editing a `tsconfig.json`, or when type errors differ between machines."
---
# TypeScript Configuration

## Purpose

This document defines how to configure the TypeScript compiler through `tsconfig.json`: the
strictness flags that catch bugs, module/target settings that must match the runtime, and how
to structure configs across a project or monorepo. The compiler's behavior is almost entirely
driven by this file — a weak config makes TypeScript little better than JavaScript.

The single most important setting is `"strict": true`. Nearly every guarantee this knowledge
base assumes — no implicit `any`, no unchecked `null` — depends on it being on.

## Why It Matters

`tsconfig.json` decides how much TypeScript actually protects you. With strictness off, the
compiler silently infers `any` for untyped parameters and lets `null` flow into code that
does not expect it — the exact bugs the type system exists to prevent slip straight through.
Configuration is also a correctness contract with the *runtime*: set `module`/`target` wrong
and code type-checks but crashes on unsupported syntax or an unresolvable import. And because
the config is committed, a loose one weakens every file in the repo and every PR after it. A
misconfigured project gives a false sense of safety, which is worse than none.

## Core Principles

- **`strict: true` is non-negotiable.** It is a bundle of flags (`noImplicitAny`,
  `strictNullChecks`, and more) that together make the type system sound. Turn it on; do not
  disable its members individually.
- **The config must match the runtime.** `target`, `module`, `moduleResolution`, and `lib`
  describe where the code will actually run. A mismatch is a runtime bug the compiler hides.
- **One base config, extended, not copied.** Share settings via `extends` so a change happens
  in one place across a monorepo.
- **Fail the build on type errors.** Type-checking that is not enforced in CI is documentation,
  not a gate.
- **Prefer catching more, not less.** Additional strictness flags cost a few annotations and
  prevent whole classes of bugs; the trade is almost always worth it.

## Best Practices

- Start every project with `"strict": true`. Add `"noUncheckedIndexedAccess": true` so
  `arr[i]` is typed `T | undefined` — it prevents a common source of runtime `undefined`.
- Set `"target"` and `"lib"` to what the runtime supports (e.g. `"ES2023"` for modern Node
  20+/browsers). `target` too high emits syntax the runtime cannot run.
- Use `"module": "nodenext"` and `"moduleResolution": "nodenext"` for Node ESM so TypeScript
  enforces Node's real resolution rules; use `"bundler"` when a bundler owns resolution.
- Enable `"noImplicitOverride": true`, `"noFallthroughCasesInSwitch": true`, and
  `"forceConsistentCasingInFileNames": true` — cheap flags that catch real mistakes.
- Set `"verbatimModuleSyntax": true` so `import type` vs `import` is explicit and emit is
  predictable (replacing the older `importsNotUsedAsValues`/`isolatedModules` juggling).
- Add `"skipLibCheck": true` to skip type-checking `.d.ts` of dependencies (faster builds);
  keep type-checking your own code.
- Run `tsc --noEmit` in CI as a required check. If a bundler emits the JS, TypeScript's job is
  purely to type-check.

## Examples

**Good Example** — strict, runtime-matched, enforced

```jsonc
// tsconfig.json — sound defaults for a modern Node ESM service
{
  "compilerOptions": {
    "strict": true,                     // the whole point: sound null + implicit-any checks
    "noUncheckedIndexedAccess": true,   // arr[i] is T | undefined — forces a real check
    "target": "ES2023",                 // matches Node 20+; no unsupported syntax emitted
    "module": "nodenext",
    "moduleResolution": "nodenext",     // enforces Node's actual ESM resolution
    "verbatimModuleSyntax": true,       // import type stays erasable and explicit
    "noFallthroughCasesInSwitch": true,
    "skipLibCheck": true                // skip deps' .d.ts, still check our code
  },
  "include": ["src"]
}
// CI runs: tsc --noEmit  (a failing type check fails the build)
```

**Bad Example** — loose config that disables the type system

```jsonc
{
  "compilerOptions": {
    "strict": false,          // implicit any everywhere; null flows unchecked — bugs pass
    "noImplicitAny": false,   // untyped params become `any` silently
    "target": "ESNext",       // may emit syntax the deployed runtime cannot execute
    "allowJs": true,          // untyped .js dragged in without any checking
    "skipLibCheck": true
  }
  // no CI type-check step → errors never block a merge
}
```

## Common Mistakes

- Leaving `strict` off (or disabling `strictNullChecks`), so the type system's core guarantees
  do not apply.
- `target`/`lib` set higher than the runtime supports, emitting syntax that fails only in
  production.
- Not running `tsc --noEmit` in CI, so type errors accumulate and merge freely.
- Assuming the bundler's transpile is a type check — most bundlers strip types without checking
  them; you still need `tsc`.
- Copy-pasting `tsconfig.json` into each package instead of `extends`-ing a shared base, so
  settings drift.
- Overusing `"paths"` without matching runtime resolution, producing imports that type-check
  but fail to load.

## Production Tips

- Keep a shared `tsconfig.base.json` and have each package `extends` it; enable
  `"composite": true` with project references for fast incremental monorepo builds.
- Treat a strictness upgrade as its own PR: flip the flag, fix the fallout, review it in
  isolation rather than bundled with features.
- Pin the `typescript` version in `devDependencies`; a minor `tsc` bump can surface new errors
  and should be an intentional change.

## AI Review Checklist

- Is `"strict": true` set (and none of its member flags individually disabled)?
- Do `target`, `lib`, `module`, and `moduleResolution` match the actual deployment runtime?
- Is `tsc --noEmit` run as a required CI check, not left to the bundler?
- Is `"noUncheckedIndexedAccess"` enabled to guard array/object index access?
- Does the monorepo share one base config via `extends` rather than duplicated copies?
- If `"paths"` are used, does the runtime/bundler resolve them too?

## Related

- `knowledge/typescript/14-modules.md`
- `knowledge/typescript/29-tooling.md`
- `knowledge/typescript/15-decorators.md`
- `knowledge/typescript/28-best-practices.md`
