---
id: tools/03-typescript-compiler
topic: tools
slug: typescript-compiler
title: "TypeScript Compiler"
type: doc
order: 3
status: ready
tags: [tools, typescript-compiler, paths, isolatedModules, target, noUncheckedIndexedAccess, tsconfig.json, strictNullChecks]
related: [tools/08-static-analysis, tools/11-esbuild-and-swc, tools/04-eslint, tools/18-monorepo-tools, tools/30-engineering-principles, typescript/16-configuration]
when_to_use: "Read before configuring tsconfig.json or wiring type checking into a build — choosing compiler options, separating checking from transpiling, or fixing slow type checks."
---
# TypeScript Compiler

## Purpose

This document defines how to configure `tsc`: which options actually affect correctness, why
type checking should be separate from transpiling in a modern build, and how to keep checks
fast as a codebase grows.

## Why It Matters

Most TypeScript configuration problems are silent. With `strict` off, the compiler accepts
code that will throw at runtime; with `skipLibCheck` misunderstood, a dependency's broken
types are hidden until an upgrade; with type checking left to the bundler, nothing checks
types at all — esbuild and SWC strip them without looking.

The common outcome is a codebase that appears typed and is not.

## Core Principles

- **`strict: true`, from day one.** Adding it later means fixing hundreds of errors at once.
  Its most valuable member, `strictNullChecks`, is what turns "cannot read property of
  undefined" into a compile error.
- **Type checking and transpiling are different jobs.** Modern bundlers transpile; `tsc
  --noEmit` checks. Running both is the correct setup, not redundancy.
- **The compiler is a gate, not a suggestion.** If `tsc --noEmit` is not in CI, type errors
  reach main.
- **Configuration expresses the runtime.** `target`, `lib`, and `module` describe where the
  code runs; guessing them produces either broken output or unavailable APIs.

## Best Practices

A configuration for an application bundled by Vite or Next.js:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "bundler",

    "strict": true,
    "noUncheckedIndexedAccess": true,   // arr[0] is T | undefined — usually true, usually ignored
    "noImplicitOverride": true,
    "exactOptionalPropertyTypes": true,

    "noEmit": true,                     // the bundler emits; tsc only checks
    "isolatedModules": true,            // required: single-file transpilers cannot see other files
    "verbatimModuleSyntax": true,       // type-only imports must say so

    "skipLibCheck": true,               // do not type-check node_modules .d.ts files
    "resolveJsonModule": true,
    "jsx": "react-jsx",

    "paths": { "@/*": ["./src/*"] }     // must be mirrored in the bundler's resolver
  },
  "include": ["src", "*.config.ts"],
  "exclude": ["node_modules", "dist"]
}
```

Three options deserve explanation because they are routinely misconfigured:

- **`skipLibCheck: true`** skips checking declaration files in dependencies. This is the
  recommended default — it is a large speedup, and errors in someone else's `.d.ts` are not
  actionable. It does **not** skip checking your use of those types.
- **`isolatedModules: true`** is mandatory when a single-file transpiler (esbuild, SWC, Babel)
  does the emitting. It forbids constructs that cannot be compiled one file at a time, such as
  re-exporting a type without `export type`.
- **`noUncheckedIndexedAccess`** is the strict option most teams skip. It is also the one that
  catches the most real bugs, because array and record access genuinely can return
  `undefined`.

Wire the check into scripts so it runs the same way everywhere:

```json
{
  "scripts": {
    "typecheck": "tsc --noEmit",
    "typecheck:watch": "tsc --noEmit --watch --preserveWatchOutput"
  }
}
```

## Examples

**Good Example** — separate configs for app and Node-side files

```json
// tsconfig.json — references, so each project checks with the right lib and target
{
  "files": [],
  "references": [{ "path": "./tsconfig.app.json" }, { "path": "./tsconfig.node.json" }]
}
```

```json
// tsconfig.node.json — build scripts and config files
{
  "compilerOptions": {
    "composite": true,               // required for project references
    "target": "ES2022",
    "lib": ["ES2022"],               // no DOM: these files never run in a browser
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "noEmit": true
  },
  "include": ["vite.config.ts", "scripts/**/*.ts"]
}
```

**Bad Example** — types that are not actually checked

```json
{
  "compilerOptions": {
    "strict": false,          // any is inferred everywhere; the types are decoration
    "noImplicitAny": false,
    "skipLibCheck": true,
    "allowJs": true,
    "checkJs": false          // JS files are invisible to the compiler
  }
}
```

```json
// ...and no typecheck script, so nothing ever runs tsc:
{ "scripts": { "build": "vite build", "dev": "vite" } }
```

Vite strips types with esbuild without checking them. This project has no type safety at all,
while appearing fully typed in the editor.

## Common Mistakes

- `strict: false`, or migrating to strict "later" and never doing it.
- No `tsc --noEmit` in CI, so the bundler's silent transpile is the only check.
- Missing `isolatedModules` with an esbuild/SWC-based build, producing errors only in
  production builds.
- `paths` configured in `tsconfig.json` but not in the bundler, so imports resolve in the
  editor and fail at build.
- `any` used to silence an error instead of `unknown` plus a narrowing check.
- `@ts-ignore` without a comment; `@ts-expect-error` is better because it fails when the error
  disappears.
- One `tsconfig.json` covering browser and Node code, so `DOM` types leak into scripts.
- Treating `skipLibCheck` as unsafe and disabling it, then spending minutes per check on
  dependency declarations.

## Production Tips

- For large repositories, use **project references** with `composite: true` and build
  incrementally (`tsc --build`); full checks scale badly past a few hundred files.
- Diagnose slow checks with `tsc --noEmit --extendedDiagnostics` and
  `--generateTrace ./trace`; the usual culprits are deeply recursive conditional types and
  overly wide `include` globs.
- Keep `skipLibCheck: true` and pin dependency versions instead — a dependency upgrade is the
  right place to discover broken types.
- Run type checking as its own CI job in parallel with lint and tests, so all three failures
  are reported in one run.

## AI Review Checklist

- Is `strict: true` enabled, along with `noUncheckedIndexedAccess`?
- Does CI run `tsc --noEmit` as a required check?
- If a single-file transpiler emits the output, is `isolatedModules` on?
- Do `target` and `lib` match the actual runtime?
- Are `paths` mirrored in the bundler and test runner resolvers?
- Are suppressions `@ts-expect-error` with a reason, rather than `@ts-ignore`?
- Are browser and Node files separated into different configs or project references?

## Related

- `knowledge/tools/08-static-analysis.md`
- `knowledge/tools/11-esbuild-and-swc.md`
- `knowledge/tools/04-eslint.md`
- `knowledge/tools/18-monorepo-tools.md`
- `knowledge/tools/30-engineering-principles.md`
- `knowledge/typescript/16-configuration.md`
