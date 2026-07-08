---
id: typescript/98-production-checklist
topic: typescript
slug: production-checklist
title: "Production Checklist"
type: doc
order: 98
status: ready
tags: [typescript, production-checklist]
related: [typescript/16-configuration, typescript/24-testing, typescript/25-performance, typescript/26-security, typescript/29-tooling]
when_to_use: "Read before shipping a TypeScript service or library to production."
---
# Production Checklist

## Purpose

This is a pre-ship gate for TypeScript code. Every item is a verifiable yes/no
you can confirm by reading a config file, running a command, or inspecting the
build output — not a matter of taste. Work top to bottom before a release or a
merge to the main branch. If an item is "no", it is a release blocker or a
consciously recorded exception, never a silent skip.

## Why It Matters

TypeScript's guarantees hold only when the toolchain is configured to enforce
them and the build actually runs the checks. It is entirely possible to ship a
bundle that "compiled" while type errors, `any` leaks, and unvalidated inputs
sailed through because the bundler transpiled without type-checking. This
checklist catches the gap between "the editor was green" and "the deployed
artifact is sound".

## Compiler & Configuration

- [ ] `strict: true` is set in the tsconfig with no per-file or per-directory opt-outs.
- [ ] `noUncheckedIndexedAccess` and `exactOptionalPropertyTypes` are enabled.
- [ ] `tsc --noEmit` runs in CI as its own step and passes with zero errors.
- [ ] `target`/`lib`/`module` match the actual runtime (Node version or browser baseline).
- [ ] `@ts-ignore` is banned; every suppression is `@ts-expect-error` with a reason.
- [ ] Path aliases in tsconfig resolve identically at build and runtime.

## Type Safety

- [ ] No `any` in shipped code (lint enforces `no-explicit-any`); `unknown` is used at boundaries.
- [ ] Every `as` cast and `!` non-null assertion is backed by an adjacent runtime check.
- [ ] All external inputs (HTTP, env, files, message queues) are schema-validated before use.
- [ ] `process.env` access goes through one validated, typed config module.
- [ ] Public/exported functions have explicit parameter and return types.

## Errors & Async

- [ ] Every `await`ed promise and floating promise is handled (`no-floating-promises` on).
- [ ] Fallible domain operations return typed errors/`Result`, not untyped throws.
- [ ] `catch` blocks type the error as `unknown` and narrow before use.
- [ ] Unhandled rejection and uncaught exception handlers are registered in services.

## Build & Dependencies

- [ ] The build emits with the type-check gate green — transpile-only builds are not the release path.
- [ ] `.d.ts` declarations are generated and published for any library artifact.
- [ ] `package.json` `exports`, `types`, and `main`/`module` fields are correct and tested by import.
- [ ] Dependencies are pinned/locked and audited (`npm audit` / equivalent) with no known criticals.
- [ ] Source maps are generated and either shipped privately or uploaded to the error tracker.

## Testing & CI

- [ ] Unit and integration tests pass in CI on the target runtime version.
- [ ] Type-level expectations (e.g. `expectTypeError`, `tsd`) cover public API contracts.
- [ ] Lint (`eslint` + `@typescript-eslint`) and format (`prettier`) run and pass in CI.
- [ ] The full check suite runs on the merge commit, not only locally.

## Observability & Runtime

- [ ] Logs are structured and never contain secrets, tokens, or full request bodies.
- [ ] An error tracker captures unhandled errors with de-minified stack traces.
- [ ] Configuration and feature flags are read once at startup and validated to fail fast.

## AI Review Checklist

- Does CI run a dedicated `tsc --noEmit` step that gates the merge?
- Is `strict` on with no opt-outs, and is `any` absent from shipped code?
- Are all external inputs validated, and is `process.env` centralized and typed?
- Are floating promises impossible (lint on) and errors typed rather than thrown loosely?
- Are library artifacts shipping correct `.d.ts` and `exports` maps?

## Related

- `knowledge/typescript/16-configuration.md`
- `knowledge/typescript/24-testing.md`
- `knowledge/typescript/25-performance.md`
- `knowledge/typescript/26-security.md`
- `knowledge/typescript/29-tooling.md`
