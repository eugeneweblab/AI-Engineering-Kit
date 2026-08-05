---
id: tools/04-eslint
topic: tools
slug: eslint
title: "ESLint"
type: doc
order: 4
status: ready
tags: [tools, eslint]
related: [tools/05-prettier, tools/03-typescript-compiler, tools/16-git-hooks, tools/08-static-analysis, tools/30-engineering-principles]
when_to_use: "Read before configuring ESLint or adding rules — writing flat config, integrating TypeScript rules, or deciding what belongs in a linter versus a formatter."
---
# ESLint

## Purpose

This document defines how to configure ESLint: the flat-config format, which rule sets earn
their place, how linting divides responsibility with the formatter and the type checker, and
how to keep it fast enough to run on every commit.

## Why It Matters

A linter is the only tool that encodes *project-specific* correctness rules — that this
import is forbidden here, that this API must not be called directly, that a promise must be
awaited. Those rules cannot come from a formatter or a compiler.

The failure mode is a configuration nobody trusts: hundreds of warnings that never go to
zero, so real errors are invisible in the noise. A linter whose output is ignored is a linter
that is not running.

## Core Principles

- **Warnings are errors, or they are noise.** Run with `--max-warnings 0`; a permanent
  warning backlog trains everyone to ignore output.
- **The formatter owns formatting.** Disable every stylistic rule and let Prettier decide —
  see [Prettier](05-prettier.md).
- **The type checker owns types.** Do not reimplement type rules in ESLint; enable
  type-aware rules for what types alone cannot express (floating promises, unnecessary
  conditions).
- **Every rule should have a reason.** A rule set copied wholesale produces disabled rules
  scattered through the codebase.

## Best Practices

Flat config (ESLint 9+) is a plain JavaScript array — later entries override earlier ones:

```js
// eslint.config.js
import js from '@eslint/js';
import tseslint from 'typescript-eslint';
import react from 'eslint-plugin-react';
import hooks from 'eslint-plugin-react-hooks';
import prettier from 'eslint-config-prettier';

export default tseslint.config(
  { ignores: ['dist/**', 'coverage/**', '*.generated.ts'] },   // replaces .eslintignore

  js.configs.recommended,
  ...tseslint.configs.recommendedTypeChecked,   // needs type information

  {
    languageOptions: {
      parserOptions: {
        projectService: true,                    // resolves tsconfig per file
        tsconfigRootDir: import.meta.dirname,
      },
    },
    plugins: { react, 'react-hooks': hooks },
    rules: {
      // Type-aware rules that catch real defects the compiler allows:
      '@typescript-eslint/no-floating-promises': 'error',
      '@typescript-eslint/await-thenable': 'error',
      '@typescript-eslint/no-misused-promises': 'error',

      // Project rules — the ones only this codebase needs:
      'no-restricted-imports': ['error', {
        patterns: [{
          group: ['../../*'],
          message: 'Use the @/ alias instead of deep relative imports.',
        }],
      }],

      'react-hooks/rules-of-hooks': 'error',
      'react-hooks/exhaustive-deps': 'warn',
    },
  },

  // Test files relax rules that do not apply there.
  {
    files: ['**/*.test.ts', '**/*.test.tsx'],
    rules: { '@typescript-eslint/no-non-null-assertion': 'off' },
  },

  prettier,   // LAST: turns off every rule Prettier handles
);
```

The `prettier` entry must come last. Placed earlier, subsequent configs re-enable the
stylistic rules it disabled, and the two tools then fight on every save.

Wire it into scripts:

```json
{
  "scripts": {
    "lint": "eslint . --max-warnings 0",
    "lint:fix": "eslint . --fix"
  }
}
```

## Examples

**Good Example** — a rule that encodes a real project constraint

```js
// eslint.config.js — one entry in the exported array
export default [
  {
    rules: {
      'no-restricted-syntax': ['error', {
        selector: "CallExpression[callee.object.name='localStorage']",
        message: 'Use the storage service — it handles SSR and quota errors.',
      }],
    },
  },
];
```

This is what a linter is for: a rule the compiler cannot express and a reviewer would
otherwise have to remember.

**Bad Example** — noise, conflict, and blanket suppression

```js
export default [
  {
    rules: {
      'no-console': 'warn',            // never fixed; adds to a permanent backlog
      semi: ['error', 'always'],       // formatting — Prettier's job, and it will disagree
      quotes: ['error', 'single'],     // same
      '@typescript-eslint/no-explicit-any': 'off',   // disabled globally instead of per case
    },
  },
];
```

```ts
/* eslint-disable */          // an entire file exempted, with no reason given
```

A file-wide disable should be a `/* eslint-disable rule-name -- reason */` at the narrowest
scope that works.

## Common Mistakes

- Running without `--max-warnings 0`, so warnings accumulate forever.
- `eslint-config-prettier` missing or not last, leaving the linter and formatter in conflict.
- Using `eslint-plugin-prettier` to run Prettier as a lint rule — it is slower and turns every
  formatting difference into a lint error.
- Type-aware rules enabled without `projectService`, producing confusing parser errors.
- `/* eslint-disable */` at file scope instead of a targeted, commented suppression.
- Rules copied from another project without asking whether they apply here.
- Linting `dist/`, `coverage/`, or generated files.
- No cache, making the pre-commit hook slow enough to be bypassed.

## Production Tips

- Enable caching for local runs: `eslint . --cache --cache-location .eslintcache` (gitignored).
- On pre-commit, lint **staged files only** via lint-staged; lint everything in CI — see
  [Git Hooks](16-git-hooks.md).
- Type-aware rules are significantly slower than syntactic ones. If the pre-commit hook drags,
  run the syntactic set there and the full type-aware set in CI.
- When adopting ESLint in an existing codebase, generate a baseline of existing violations and
  fail only on new ones, rather than opening a thousand-file pull request.

## AI Review Checklist

- Is flat config used, with `ignores` replacing `.eslintignore`?
- Is `eslint-config-prettier` present and last in the array?
- Does the lint script use `--max-warnings 0`?
- Are type-aware rules configured with `projectService` where they are used?
- Do project-specific rules exist, or is the config only a copied preset?
- Are suppressions narrow and accompanied by a reason?
- Are build output and generated files excluded?

## Related

- `knowledge/tools/05-prettier.md`
- `knowledge/tools/03-typescript-compiler.md`
- `knowledge/tools/16-git-hooks.md`
- `knowledge/tools/08-static-analysis.md`
- `knowledge/tools/30-engineering-principles.md`
