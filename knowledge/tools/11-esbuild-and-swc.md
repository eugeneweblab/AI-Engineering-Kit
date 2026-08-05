---
id: tools/11-esbuild-and-swc
topic: tools
slug: esbuild-and-swc
title: "esbuild and SWC"
type: doc
order: 11
status: ready
tags: [tools, esbuild-and-swc, arethetypeswrong, isolatedModules, publint, exports]
related: [tools/12-babel, tools/09-vite, tools/03-typescript-compiler, tools/13-test-runners, tools/30-engineering-principles]
when_to_use: "Read before using esbuild or SWC — as a transpiler in a build chain, for a library bundle, or when replacing Babel."
---
# esbuild and SWC

## Purpose

This document defines when and how to use esbuild and SWC: what they do well, the guarantees
they deliberately give up in exchange for speed, and where each fits in a modern toolchain.

## Why It Matters

These tools are one to two orders of magnitude faster than Babel and `tsc`, which is why they
now sit underneath Vite, Next.js, Vitest, and most modern build pipelines. The speed comes
from a specific trade: they transform **one file at a time and never check types**.

Understanding that trade explains nearly every surprise people hit with them — why
`isolatedModules` is required, why `const enum` breaks, why type errors never appear, and why
declaration files still need `tsc`.

## Core Principles

- **They transpile; they do not type-check.** Types are stripped without validation. A
  separate `tsc --noEmit` is mandatory.
- **Single-file transforms.** No transformation may depend on another file's contents, which
  is what `isolatedModules: true` enforces at the type level.
- **esbuild bundles; SWC mostly transforms.** esbuild is a bundler and minifier with a
  transform API; SWC is a compiler used inside other bundlers (Next.js, Rspack) and test
  runners.
- **They do not emit `.d.ts` files.** Library builds still need `tsc --emitDeclarationOnly` or
  an equivalent.

## Best Practices

Most projects use these indirectly and should keep it that way — Vite, Next.js, and Vitest all
configure them correctly. Direct use is for libraries, CLIs, and server bundles:

```js
// build.mjs — bundling a Node CLI with esbuild
import { build } from 'esbuild';

await build({
  entryPoints: ['src/cli.ts'],
  outfile: 'dist/cli.js',
  bundle: true,
  platform: 'node',
  target: 'node20',
  format: 'esm',
  sourcemap: true,
  minify: false,                  // server code: readable stack traces beat bytes

  // Do not bundle dependencies into a published package.
  packages: 'external',

  banner: { js: '#!/usr/bin/env node' },
});
```

```json
// package.json — types come from tsc, code from esbuild
{
  "scripts": {
    "build": "node build.mjs && tsc --emitDeclarationOnly --outDir dist",
    "typecheck": "tsc --noEmit"
  }
}
```

SWC configuration, for direct use in a loader or test runner:

```json
// .swcrc
{
  "$schema": "https://swc.rs/schema.json",
  "jsc": {
    "parser": { "syntax": "typescript", "tsx": true },
    "target": "es2022",
    "transform": {
      "react": { "runtime": "automatic" }
    },
    "externalHelpers": false
  },
  "module": { "type": "es6" },
  "sourceMaps": true
}
```

## What They Do Not Support

The limitations are specific and worth knowing before adopting:

| Feature | Status | Why |
|---|---|---|
| Type checking | Never | By design — use `tsc --noEmit` |
| `.d.ts` emit | Never | Use `tsc --emitDeclarationOnly` |
| `const enum` | Not supported | Requires cross-file information |
| Legacy decorators | Partial | SWC supports both proposals; esbuild only the TS form |
| Namespaces with runtime code | Partial | Single-file limitation |
| Very old targets (ES5 and below) | Limited | Babel remains better for wide legacy support |

The `const enum` case is the one that surprises people mid-migration: it compiles fine with
`tsc` and fails or silently misbehaves under a single-file transpiler. Replace it with a plain
`enum` or an `as const` object.

## Examples

**Good Example** — the division of labor that works

```json
{
  "scripts": {
    "dev": "vite",                          // esbuild transforms, no type check
    "typecheck": "tsc --noEmit",            // types, separately
    "test": "vitest",                       // esbuild again, same trade
    "build": "pnpm typecheck && vite build" // gate before shipping
  }
}
```

**Bad Example** — assuming the fast tool checks anything

```json
{ "scripts": { "build": "esbuild src/index.ts --bundle --outfile=dist/index.js" } }
```

```ts
// This compiles and ships. The type error is real and never reported.
const total: number = "12" as unknown as number;
processPayment(total * qty);   // NaN in production
```

**Bad Example** — a construct the transform cannot see

```ts
// Fails under isolatedModules: the transpiler cannot know Config is a type.
export { Config } from './types';

// Correct:
export type { Config } from './types';
```

## Common Mistakes

- Treating a successful esbuild/SWC build as evidence that types are correct.
- Missing `isolatedModules: true`, so errors appear only at build time.
- `const enum` in a codebase transpiled per file.
- Publishing a library without declaration files because the bundler does not emit them.
- Bundling dependencies into a published package instead of marking them external.
- Minifying server bundles, making production stack traces unreadable.
- Expecting Babel plugins to work — the plugin ecosystems are entirely separate.
- Targeting a runtime older than these tools support well, where Babel is still correct.

## Production Tips

- Keep sourcemaps on for server bundles and upload them to the error tracker; the size cost
  is irrelevant server-side and the debugging value is high.
- For libraries, verify the published artifact with `publint` and `arethetypeswrong` — wrong
  `exports` maps and missing types are the usual defects.
- When migrating from Babel, check for plugins doing real work (macros, custom JSX pragmas,
  legacy decorators). Those are the migrations that fail.
- If a build depends on cross-file transforms, that is a signal the code should change rather
  than the tool.

## AI Review Checklist

- Is `tsc --noEmit` present as a separate, required step?
- Is `isolatedModules: true` set in `tsconfig.json`?
- For a library, are `.d.ts` files emitted and dependencies marked external?
- Are `const enum` and other cross-file constructs absent?
- Are server bundles unminified with sourcemaps retained?
- Is the target runtime within what these tools handle well?

## Related

- `knowledge/tools/12-babel.md`
- `knowledge/tools/09-vite.md`
- `knowledge/tools/03-typescript-compiler.md`
- `knowledge/tools/13-test-runners.md`
- `knowledge/tools/30-engineering-principles.md`
