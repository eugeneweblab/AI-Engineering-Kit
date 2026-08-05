---
id: nodejs/29-tooling
topic: nodejs
slug: tooling
title: "Node.js Tooling"
type: doc
order: 29
status: ready
tags: [nodejs, tooling]
related: [nodejs/04-package-management, nodejs/21-testing, nodejs/22-debugging, nodejs/26-deployment, nodejs/28-best-practices]
when_to_use: "Read before setting up or reviewing a Node.js project's linting, formatting, type-checking, build, and CI toolchain."
---
# Node.js Tooling

## Purpose

This document defines the development toolchain for a Node.js project: linting,
formatting, type-checking, testing, building, and the CI gate that ties them together. It
is written so an agent can set up (or review) a toolchain that catches defects
automatically and produces identical results on every machine and in CI.

Tooling is the automated layer of quality that runs before code ships. Its goal is to make
the correct thing effortless and the incorrect thing fail loudly, so review effort goes to
design rather than to catching missing semicolons.

## Why It Matters

Manual discipline does not scale: humans forget to run the formatter, skip the type-check
when rushed, and disagree about style in review. A toolchain moves those checks from
"someone remembers" to "the machine enforces." The payoff is compounding — every check
automated is a class of bug that can never reach production and a category of review
comment that never needs writing again. The failure mode of weak tooling is subtle: the
project keeps working while inconsistency, dead code, and type holes accumulate until
changes become risky.

## Core Principles

- **Reproducible over convenient.** Pin the Node version and commit the lockfile so every
  install resolves identically (see [package management](04-package-management.md)). A build
  that depends on what happens to be installed is not a build.
- **Fast local feedback, authoritative CI.** The same checks run locally (for speed) and in
  CI (as the gate). CI is the source of truth; local is the preview.
- **One formatter, zero style debate.** A deterministic formatter removes style from review
  entirely. Configure it once; never argue about it again.
- **Types and lint are errors, not warnings.** A warning nobody fixes is noise. Fail the
  build on lint and type errors so they cannot accumulate.
- **Separate concerns.** Linting finds bugs, formatting enforces style, the type-checker
  proves shapes. Do not make one tool do another's job (e.g. lint rules for formatting).

## Best Practices

- Pin the toolchain: `.nvmrc` + `"engines"` for the Node version, an exact-versioned
  lockfile, and `npm ci` in CI for deterministic installs.
- Use **ESLint** (flat config) for correctness rules and **Prettier** for formatting; wire
  `eslint-config-prettier` so they do not fight over style.
- Adopt **TypeScript** in `strict` mode; it catches the null/undefined and shape errors that
  dominate Node bugs. Type-check in CI (`tsc --noEmit`) even if you build with esbuild/swc.
- Run tests with the framework the project standardizes on — the built-in `node:test`
  runner, **Vitest**, or **Jest** (see [testing](21-testing.md)) — and collect coverage in CI.
- Add a pre-commit hook (Husky + lint-staged) that formats and lints only staged files —
  fast feedback that keeps unformatted code out of history.
- Automate dependency hygiene: `npm audit`/Dependabot/Renovate in CI so vulnerable or stale
  deps surface as PRs, not surprises.
- Build for production with a fast bundler/transpiler (esbuild, swc, or `tsc`) and produce
  the single artifact you [deploy](26-deployment.md); build once, promote everywhere.
- Make CI the merge gate: install, lint, type-check, test, build — a red check blocks merge.

## Examples

**Good Example** — deterministic CI gate, checks as errors

```yaml
# .github/workflows/ci.yml — same steps, same versions, every run
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version-file: .nvmrc, cache: npm } # pinned Node, cached deps
      - run: npm ci                 # deterministic install from the committed lockfile
      - run: npm run lint           # ESLint — fails the build on any error
      - run: npm run typecheck      # tsc --noEmit — types are a gate, not a suggestion
      - run: npm test -- --coverage # tests + coverage on every PR
      - run: npm run build          # the same artifact that gets deployed
```

```json
// package.json — one command per concern, wired to the same tools CI runs
{
  "scripts": {
    "lint": "eslint .",
    "format": "prettier --write .",
    "typecheck": "tsc --noEmit",
    "test": "node --test",
    "build": "tsc -p tsconfig.build.json"
  },
  "engines": { "node": ">=22" }
}
```

**Bad Example** — non-deterministic, checks that never fail

```yaml
jobs:
  build:
    steps:
      - run: npm install           # no lockfile enforcement → drifts between runs
      - run: npx eslint . || true  # "|| true" makes lint failures invisible — pure theatre
      # no type-check, no tests: broken types and red tests merge freely
```

## Common Mistakes

- `npm install` instead of `npm ci` in CI, letting dependency versions drift between builds.
- Treating lint/type errors as warnings (or `|| true`), so they accumulate unchecked.
- Overlapping ESLint and Prettier without `eslint-config-prettier`, producing fights and
  churn over formatting.
- No committed lockfile or pinned Node version, so "works locally" and "fails in CI" diverge.
- Skipping `tsc --noEmit` because a fast bundler "compiles" TS — bundlers strip types without
  checking them, so type errors ship.
- Checks that run locally but are not enforced in CI, making them optional in practice.
- Formatting or linting the whole repo on every commit instead of staged files, killing speed.

## Production Tips

- Cache `node_modules`/build output in CI keyed on the lockfile hash to keep the gate fast;
  a slow gate gets bypassed.
- Fail CI on new `npm audit` high/critical findings, but triage via a policy so a single
  unfixable transitive dep does not permanently block merges.
- Keep tool configs (`eslint.config.js`, `.prettierrc`, `tsconfig.json`) in version control
  and identical for editor and CI, so local and pipeline never disagree.
- Version the Node engine requirement and bump it deliberately; a silent runtime upgrade can
  change behavior across a fleet.

## AI Review Checklist

- Is the Node version pinned (`.nvmrc`/`engines`) and the lockfile committed?
- Does CI use `npm ci` for a deterministic install?
- Do lint and type-check run in CI and fail the build on errors (no `|| true`)?
- Are ESLint (correctness) and Prettier (formatting) configured without conflict?
- Does CI run tests with coverage and produce the same artifact that is deployed?
- Are the same checks available locally (scripts / pre-commit) as in CI?
- Is dependency scanning (`npm audit`/Dependabot/Renovate) automated?

## Related

- `knowledge/nodejs/04-package-management.md`
- `knowledge/nodejs/21-testing.md`
- `knowledge/nodejs/22-debugging.md`
- `knowledge/nodejs/26-deployment.md`
- `knowledge/nodejs/28-best-practices.md`
