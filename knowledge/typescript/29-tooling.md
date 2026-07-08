---
id: typescript/29-tooling
topic: typescript
slug: tooling
title: "Tooling"
type: doc
order: 29
status: ready
tags: [typescript, tooling]
related: [typescript/16-configuration, typescript/24-testing, typescript/28-best-practices, typescript/14-modules]
when_to_use: "Read before setting up or reviewing a TypeScript project's compiler, linter, formatter, and build pipeline."
---
# Tooling

## Purpose

This document defines the toolchain that turns TypeScript source into shipped software and
enforces quality along the way: the compiler, linter, formatter, bundler/transpiler, and
CI. The goal is a setup where correctness is enforced by machines, not memory — an agent
should never rely on a human to remember to run a check.

Tooling choices matter because they decide *what the build guarantees*. A pipeline that
transpiles without type-checking gives you the syntax of TypeScript and none of the safety.

## Why It Matters

Most fast TypeScript build tools — esbuild, swc, Babel, Vite — strip types without
checking them. They are transpilers, not type-checkers. If your build only runs one of
these, `tsc` never runs, and type errors ship to production while the build stays green.
This is the single most consequential tooling mistake in the ecosystem. Beyond that,
consistent formatting and linting remove whole categories of review friction and bugs, and
they only work if they run automatically. Tooling is where "we should be careful" becomes
"the pipeline won't let us be careless".

## Core Principles

- **Type-check separately from bundling.** Fast bundlers erase types without validating
  them; you must run `tsc --noEmit` as its own gate. The cost of skipping it is that type
  errors reach production.
- **Automate every check.** A check that depends on a human running it locally will be
  skipped under pressure. Put it in CI and in a pre-commit hook.
- **One source of truth for config.** `tsconfig.json` drives the compiler; the linter and
  bundler should read from it, not redefine target/module independently.
- **Fail the build on violations.** Warnings that do not fail are noise that accumulates.
  Decide what matters and make it an error.
- **Pin versions.** A lockfile and pinned tool versions make builds reproducible; floating
  versions turn "works on my machine" into a debugging tax.

## Best Practices

- Run `tsc --noEmit` in CI as a dedicated step, even if you bundle with esbuild/swc/Vite.
  This is non-negotiable. See [configuration](16-configuration.md).
- Use **ESLint** with `typescript-eslint` (flat config, type-aware rules via
  `parserOptions.project`) for correctness lint that understands types.
- Use **Prettier** (or Biome) for formatting and run it in CI with `--check`; never argue
  about style in review — let the formatter decide.
- Consider **Biome** as a single fast tool that covers lint + format when you want fewer
  dependencies; keep `tsc` for type-checking regardless.
- For builds: **tsup**/**esbuild** for libraries, **Vite** for apps, `tsc --build` with
  project references for large multi-package monorepos. See [modules](14-modules.md).
- Use **Vitest** for tests so the test runner shares config with the bundler. See
  [testing](24-testing.md).
- Enforce checks pre-push with a lightweight hook runner (**lefthook**/**husky** +
  **lint-staged**) so obvious failures never reach CI.
- Enable `incremental` and cache `node_modules`/`.tsbuildinfo` in CI to keep the pipeline
  fast; slow pipelines get bypassed.
- Manage the Node/tool version with a pinned `.nvmrc`/`engines` field and a committed
  lockfile.

## Examples

**Good Example** — CI runs type-check, lint, format, and tests as separate gates

```jsonc
// package.json — each concern is its own script, all run in CI.
{
  "scripts": {
    "typecheck": "tsc --noEmit",        // the safety gate the bundler skips
    "lint": "eslint . --max-warnings 0", // warnings fail the build, so they get fixed
    "format:check": "prettier --check .",
    "test": "vitest run",
    "build": "tsup src/index.ts --dts",  // emits JS + .d.ts for consumers
    "ci": "npm run typecheck && npm run lint && npm run format:check && npm run test"
  }
}
```

**Bad Example** — bundler only, no type-checking, warnings ignored

```jsonc
{
  "scripts": {
    // esbuild strips types WITHOUT checking them → type errors ship silently.
    "build": "esbuild src/index.ts --bundle --outfile=dist/index.js",
    // No `tsc --noEmit` anywhere. The build is green while the types are wrong.
    "lint": "eslint . || true"          // `|| true` means lint can never fail CI
  }
}
```

## Common Mistakes

- Relying on esbuild/swc/Babel/Vite for the build and never running `tsc --noEmit`, so
  type errors are never caught.
- Letting lint warnings pass (`--max-warnings` unset or `|| true`), so they pile up.
- Formatting rules encoded in ESLint instead of a formatter, causing rule conflicts.
- No lockfile or unpinned tool versions, making CI non-reproducible.
- Type-aware lint rules configured without `parserOptions.project`, so they silently do
  nothing.
- Duplicating `target`/`module` settings across bundler and `tsconfig` until they drift.

## Production Tips

- Cache `.tsbuildinfo` and dependencies in CI; a fast pipeline is one people keep green.
- Run type-check, lint, and tests as parallel CI jobs so feedback is quick.
- Add `@arethetypeswrong/cli` and a `publint` step for libraries to validate published
  package exports.

## AI Review Checklist

- Does CI run `tsc --noEmit` as a real gate, independent of the bundler?
- Do lint warnings and format violations fail the build?
- Is `typescript-eslint` configured with type-aware rules (`parserOptions.project`)?
- Is formatting owned by a formatter, not by conflicting ESLint style rules?
- Are tool versions pinned and a lockfile committed for reproducible builds?
- Are checks enforced automatically (CI and pre-commit), not left to memory?

## Related

- `knowledge/typescript/16-configuration.md`
- `knowledge/typescript/24-testing.md`
- `knowledge/typescript/28-best-practices.md`
- `knowledge/typescript/14-modules.md`
