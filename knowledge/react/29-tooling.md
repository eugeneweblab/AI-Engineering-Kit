---
id: react/29-tooling
topic: react
slug: tooling
title: "React Tooling"
type: doc
order: 29
status: ready
tags: [react, tooling]
related: [react/23-code-style, react/21-testing, react/28-production, react/12-performance, react/22-folder-structure]
when_to_use: "Read when setting up a React project's build, lint, format, type-check, or CI toolchain."
---
# React Tooling

## Purpose

This document defines the toolchain a React project needs to stay correct and fast:
build tool, type checker, linter, formatter, test runner, and the CI that enforces
them. Good tooling catches whole classes of bugs before code review — mutation, missing
dependencies, type errors, unformatted diffs — so humans and agents spend attention on
logic instead of mechanics.

The rule that ties this together: **if a rule matters, a machine enforces it.** A
convention that lives only in a style doc will be violated. A convention enforced by
CI cannot be.

## Why It Matters

Tooling is leverage. A linter that flags a missing effect dependency prevents a
stale-closure bug for every developer, forever, at zero marginal cost. A type checker
turns a runtime crash into a red squiggle. A formatter ends every whitespace debate.
Without this layer, the same mistakes recur in review after review, and the reviews
themselves become slow and inconsistent. The cost of setting up tooling is paid once;
the cost of not having it is paid on every change.

## Core Principles

- **Use a modern build tool.** Vite (or a framework like Next.js) for its fast dev
  server, native ESM, and optimized production build. Hand-rolled Webpack configs are
  legacy maintenance you don't need.
- **TypeScript in `strict` mode.** Strict catches null/undefined and type mismatches at
  compile time. Loosening it trades a compile error now for a runtime crash later.
- **Lint for correctness, not just style.** `eslint-plugin-react-hooks` catches real
  bugs (missing deps, conditional hooks). Treat its warnings as errors.
- **Format automatically.** Prettier removes formatting from human judgment; run it on
  save and in a pre-commit hook so diffs stay meaningful.
- **CI is the source of truth.** Type-check, lint, test, and build must pass in CI on
  every PR. Local green is a courtesy; CI green is the gate.

## Best Practices

- Scaffold with Vite or a maintained framework; keep the build tool and React version current.
- Enable `strict: true` in `tsconfig.json`; avoid `any` and `@ts-ignore` — prefer
  `unknown` and narrow. See [code style](23-code-style.md).
- Configure ESLint with the React, hooks, and jsx-a11y plugins; run `eslint --max-warnings=0`
  in CI so warnings can't accumulate.
- Run Prettier via a pre-commit hook (lint-staged + husky) so unformatted code never lands.
- Use Vitest or Jest with React Testing Library for tests; run them in CI. See [testing](21-testing.md).
- Automate dependency updates (Renovate/Dependabot) and pin versions with a lockfile
  that's committed and used by CI (`npm ci`, not `npm install`).
- Analyze the bundle (`rollup-plugin-visualizer`) and enforce a size budget in CI. See
  [performance](12-performance.md).

## Examples

**Good Example** — CI gate that enforces every rule

```yaml
# .github/workflows/ci.yml — one job, all gates, warnings fail
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci                       # reproducible install from the lockfile
      - run: npx tsc --noEmit             # type errors fail the build
      - run: npx eslint . --max-warnings=0 # warnings are errors here
      - run: npx prettier --check .        # unformatted code fails
      - run: npm test -- --run             # tests must pass
      - run: npm run build                 # production build must succeed
```

**Bad Example** — nothing enforced, everything optional

```jsonc
// package.json — "scripts" exist but nothing runs them on PRs
{
  "scripts": {
    "lint": "eslint .",      // never run in CI → warnings pile up
    "build": "vite build"
  }
  // no tsc, no prettier check, no test gate, no CI workflow.
  // "strict": false in tsconfig, `npm install` in CI → non-reproducible builds.
}
```

## Common Mistakes

- Running `npm install` in CI instead of `npm ci`, producing non-reproducible builds.
- Leaving TypeScript non-strict, or scattering `@ts-ignore` / `any`.
- Treating ESLint warnings as advisory so they accumulate indefinitely.
- Relying on developers to run the linter/formatter manually instead of hooks + CI.
- No bundle budget, so size regressions ship unnoticed.
- Not committing the lockfile, so every machine resolves different versions.

## Production Tips

- Cache dependencies in CI to keep the pipeline fast; a slow gate gets bypassed.
- Fail the PR (don't just warn) on type, lint, format, and test failures.
- Keep the toolchain versions in the lockfile so upgrades are explicit and reviewable.

## AI Review Checklist

- Is the project on a modern build tool (Vite / maintained framework)?
- Is TypeScript in `strict` mode with `any`/`@ts-ignore` avoided?
- Are the React-hooks and a11y ESLint plugins enabled and warnings failing CI?
- Is formatting enforced by a pre-commit hook?
- Does CI run type-check, lint, format-check, tests, and build on every PR?
- Is the lockfile committed and installed with `npm ci`?

## Related

- `knowledge/react/23-code-style.md`
- `knowledge/react/21-testing.md`
- `knowledge/react/28-production.md`
- `knowledge/react/12-performance.md`
- `knowledge/react/22-folder-structure.md`
