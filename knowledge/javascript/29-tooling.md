---
id: javascript/29-tooling
topic: javascript
slug: tooling
title: "JavaScript Tooling"
type: doc
order: 29
status: ready
tags: [javascript, tooling, engines, browserslist, sideEffects, types, exports, format]
related: [javascript/07-modules, javascript/24-testing, javascript/28-best-practices, javascript/26-security, javascript/25-performance]
when_to_use: "Read before setting up or changing a JavaScript project's build, lint, format, or dependency tooling."
---
# JavaScript Tooling

## Purpose

This document defines how to set up the toolchain around JavaScript: package manager and
lockfile, linter and formatter, bundler/build, transpilation and targets, and CI gates.
It is written so an agent configures a project whose builds are reproducible, whose quality
gates run automatically, and whose dependencies are a managed risk rather than an open door.

## Why It Matters

Tooling is where consistency and safety become *mechanical* instead of aspirational. A
lockfile means the code that passed review is the code that ships — not a silently upgraded
transitive dependency. A formatter ends style debates in review. A linter catches the
floating Promise before a human has to. Without these gates, quality depends on everyone
remembering everything every time, which does not scale and does not happen. Weak tooling
also *is* a security surface: an unpinned dependency tree is a supply-chain vulnerability.

## Core Principles

- **Reproducible builds.** Commit a lockfile and use `npm ci` (or the pnpm/yarn frozen
  equivalent) in CI. `npm install` in CI can silently pull different versions — the cost is
  a build that passes locally and breaks in prod.
- **Automate the gates.** Lint, format-check, type-check, and test must run in CI and block
  merge. A gate that only runs when someone remembers is not a gate.
- **Fast local feedback.** Prefer fast, integrated tools (Vite, esbuild, Biome) so the
  inner loop is seconds, not minutes. Slow tooling gets bypassed.
- **Dependencies are liabilities.** Every package is code you run and maintain. Minimize the
  tree, pin it, audit it, and review updates.
- **Config as code, one source of truth.** Check in tool configs; do not rely on machine-local
  or editor-only settings.

## Best Practices

- Pick one package manager (**pnpm** for strictness and disk efficiency, or npm) and commit
  its lockfile. Never mix managers in one repo.
- Lint with **ESLint** (flat config) and format with **Prettier** or **Biome**; wire them so
  format and lint do not fight. Run `--fix`/`format` on pre-commit via a hook (husky +
  lint-staged), and re-check in CI.
- Build/bundle with **Vite** (apps) or **tsup/esbuild/Rollup** (libraries). Target the
  browsers/Node versions you actually support via `browserslist` / `engines` — do not
  over-transpile for environments you do not ship to.
- Type-check with TypeScript (`tsc --noEmit`) or `// @ts-check` + JSDoc on plain JS; run it
  as a CI gate separate from the build.
- Run `npm audit` / a supply-chain scanner and automated dependency PRs (Renovate/Dependabot)
  with review before merge.
- Publish libraries as ESM (with a CJS fallback if needed) and declare `exports`, `types`,
  and `sideEffects` so consumers tree-shake correctly.
- Keep the toolchain minimal; every added tool is more config to maintain and break.

## Examples

**Good Example** — reproducible, gated CI pipeline

```yaml
# ci.yml — every gate runs on every PR and blocks merge.
- run: npm ci                 # installs exactly the lockfile; no silent version drift
- run: npm run lint           # eslint --max-warnings=0: warnings fail the build
- run: npm run format:check   # prettier --check: formatting is verified, not just fixable
- run: npx tsc --noEmit       # type errors block merge
- run: npm test -- --run      # tests must pass
- run: npm audit --audit-level=high  # known high-severity CVEs fail the build
```

**Bad Example** — non-reproducible, ungated

```yaml
- run: npm install           # may resolve newer versions than were reviewed → "works on my machine"
- run: npm test || true      # swallows failures: a red suite still merges
# no lint, no type-check, no audit — quality depends on people remembering
```

## Common Mistakes

- Using `npm install` in CI instead of `npm ci`, so builds are not reproducible.
- No lockfile committed, or mixing package managers in one repo.
- Linter/formatter that only run locally, not enforced in CI.
- ESLint configured to warn but never fail (`--max-warnings=0` missing).
- Over-transpiling to ancient targets you do not support, bloating the bundle.
- Ignoring `npm audit` / dependency-update PRs until a CVE forces a scramble.
- Piling on tools with overlapping jobs (multiple formatters/bundlers) that conflict.

## Production Tips

- Cache dependencies and build artifacts in CI keyed on the lockfile hash — faster and still
  reproducible.
- Enforce `engines` in `package.json` and pin the Node version in CI (`.nvmrc`) so local and
  CI runtimes match.
- Generate and store a Software Bill of Materials (SBOM) for supply-chain traceability on
  anything you ship.

## AI Review Checklist

- Is a lockfile committed and does CI use `npm ci` (or a frozen-install equivalent)?
- Do lint, format-check, type-check, and tests all run in CI and block merge?
- Does the linter fail on warnings rather than merely reporting them?
- Are build targets scoped to supported environments via `browserslist`/`engines`?
- Is there a dependency-audit step and an automated update process with review?
- Is exactly one package manager and one formatter/bundler in use?
- Are tool configs checked into the repo, not machine- or editor-local?

## Related

- `knowledge/javascript/07-modules.md`
- `knowledge/javascript/24-testing.md`
- `knowledge/javascript/28-best-practices.md`
- `knowledge/javascript/26-security.md`
- `knowledge/javascript/25-performance.md`
