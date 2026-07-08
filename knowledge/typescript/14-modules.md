---
id: typescript/14-modules
topic: typescript
slug: modules
title: "Modules"
type: doc
order: 14
status: ready
tags: [typescript, modules]
related: [typescript/16-configuration, typescript/27-library-design, typescript/29-tooling, typescript/13-advanced-types]
when_to_use: "Read before setting up imports/exports, package `exports` maps, or debugging ESM/CJS interop."
---
# Modules

## Purpose

This document defines how TypeScript code should be split into modules and wired together:
ESM vs CommonJS, `import`/`export` syntax, type-only imports, path resolution, barrel files,
and the package `exports` field. It targets ES Modules (ESM) as the default for new code in
2026.

A module boundary is an API. What a file exports is its public surface; everything else is an
implementation detail. Getting boundaries right keeps the dependency graph acyclic, builds
fast, and refactors local.

## Why It Matters

Module structure is the skeleton the whole codebase hangs on, and it is expensive to change
later. Circular dependencies cause `undefined` exports at runtime that appear only under a
specific import order — brutal to debug. Mixing ESM and CJS wrong yields `ERR_REQUIRE_ESM` or
`__esModule` interop bugs that pass type-checking and fail at runtime. Leaking internals
through a broad barrel file means every consumer couples to details you meant to hide, and a
missing type-only import can drag runtime code into a build that should have been erased.
These are structural failures: they do not show up in one function, they show up across the
system.

## Core Principles

- **Prefer ESM for new code.** It is the standard, enables tree-shaking, and is what tooling
  and Node target by default in 2026. Only use CJS when a dependency forces it.
- **Export a deliberate surface.** Name what is public; keep helpers unexported. A file's
  exports are a contract others will depend on.
- **Keep the import graph acyclic.** Cycles are a design smell; break them by extracting the
  shared piece into a third module both can depend on.
- **Separate type imports from value imports.** `import type` is erased at build time and can
  never cause a runtime side effect.
- **Resolve paths through configuration, not `../../../`.** Path aliases or package `imports`
  keep moves cheap and intent clear.

## Best Practices

- Use `import type { T }` (or inline `import { type T }`) for anything used only in type
  positions, so the import is fully erased and cannot create a cycle or side effect.
- Prefer named exports over `default` exports: they are refactor-safe, autocomplete better,
  and force one canonical name across the codebase.
- Set `"type": "module"` in `package.json` for ESM; in `tsconfig`, use
  `"module": "nodenext"` / `"moduleResolution": "nodenext"` so TypeScript checks Node's real
  ESM rules (including mandatory file extensions in relative specifiers).
- Publish libraries with an `exports` map that lists exactly the public entry points; this
  blocks consumers from importing deep internal paths.
- Keep barrel files (`index.ts`) small and cycle-free; a barrel that re-exports everything can
  defeat tree-shaking and create import cycles.
- Configure path aliases (`paths` in tsconfig, or subpath `imports` with the `#` prefix) and
  ensure the runtime/bundler resolves them too — TypeScript aliases alone do not rewrite
  emitted paths.

## Examples

**Good Example** — explicit surface, erasable type import, no cycle

```ts
// user.ts
import type { Logger } from "./logger.ts"; // type-only: erased, cannot cause a runtime cycle

export interface User { id: string; email: string } // public API of this module

export function createUser(email: string, log: Logger): User {
  const user = { id: crypto.randomUUID(), email };
  log.info("user created");
  return user;
}

function normalize(email: string) { return email.toLowerCase(); } // private helper: not exported
```

**Bad Example** — default export, value import creating a cycle, deep internal reach

```ts
// user.ts
import { Logger } from "./logger.ts"; // value import; logger.ts imports user.ts back → cycle
import User from "../../../models/user"; // brittle relative path; default export renamed freely

export default function (email: string) {        // anonymous default: no stable name to import
  return { id: Math.random().toString(), email }; // non-crypto id, unrelated to the module's API
}
```

## Common Mistakes

- Circular imports that leave an export `undefined` at runtime under certain load orders.
- Omitting `import type`, so a type-only dependency pulls runtime code into the bundle or
  forms a cycle.
- Default exports that get imported under different names, making the symbol hard to find and
  refactor.
- Missing `.js`/`.ts` extensions in relative ESM specifiers under `nodenext`, which Node
  rejects at runtime even though older configs accepted it.
- A "god barrel" `index.ts` re-exporting the whole package, coupling consumers to internals
  and hurting tree-shaking.
- Assuming tsconfig `paths` rewrite emitted output — they do not; the runtime needs its own
  resolver (bundler, `tsc-alias`, or Node subpath `imports`).

## Production Tips

- Add an import-cycle check to CI (`madge --circular`, `eslint-plugin-import`'s
  `no-cycle`) — cycles are far cheaper to catch mechanically than to debug in production.
- For dual-published libraries, verify both the ESM and CJS entry points in the `exports` map
  actually load, using a tool like `arethetypeswrong`/`publint`.
- Keep the public `exports` surface minimal; every path you expose is a compatibility promise.

## AI Review Checklist

- Are type-only imports written with `import type` (or inline `type`) so they are erased?
- Is the module free of circular dependencies, checked in CI?
- Are named exports used instead of default exports for shared modules?
- Under `nodenext`, do relative ESM imports include file extensions?
- Do library packages restrict their surface with an `exports` map instead of exposing deep
  paths?
- Are path aliases resolved by the runtime/bundler, not just by TypeScript?

## Related

- `knowledge/typescript/16-configuration.md`
- `knowledge/typescript/27-library-design.md`
- `knowledge/typescript/29-tooling.md`
- `knowledge/typescript/13-advanced-types.md`
