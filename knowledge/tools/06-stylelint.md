---
id: tools/06-stylelint
topic: tools
slug: stylelint
title: "Stylelint"
type: doc
order: 6
status: ready
tags: [tools, stylelint]
related: [tools/05-prettier, tools/04-eslint, tools/16-git-hooks, tools/09-vite, tools/30-engineering-principles, css/21-architecture, tailwind/26-best-practices]
when_to_use: "Read before linting CSS — configuring Stylelint for plain CSS, SCSS, or Tailwind, or enforcing design-token usage in stylesheets."
---
# Stylelint

## Purpose

This document defines how to lint stylesheets: which rules catch real defects rather than
preferences, how Stylelint coexists with Prettier and Tailwind, and how to enforce design-token
usage automatically instead of in review.

## Why It Matters

CSS fails silently. A misspelled property, an invalid value, or a duplicate selector produces
no error — the declaration is simply ignored, and the page renders slightly wrong on one
breakpoint that nobody checked. Nothing in a normal build catches this.

The second reason is design-system drift: hardcoded hex values and one-off spacing multiply
until the token system exists only in documentation. That is enforceable with a rule and
unenforceable by review alone.

## Core Principles

- **Lint for correctness, not style.** Prettier formats; Stylelint catches invalid properties,
  unknown units, impossible selectors, and duplicates.
- **Enforce the design system.** Rules that reject raw colors and arbitrary spacing keep
  tokens authoritative.
- **Match the dialect.** Plain CSS, SCSS, and CSS-in-JS need different parsers and rule sets;
  the wrong one produces false errors that get the tool disabled.
- **Zero warnings.** As with any linter, a permanent backlog makes output worthless.

## Best Practices

```js
// stylelint.config.js
export default {
  extends: [
    'stylelint-config-standard',        // correctness rules for modern CSS
    'stylelint-config-prettier',        // drop rules Prettier owns (Stylelint <16 only)
  ],

  ignoreFiles: ['dist/**/*.css', '**/*.min.css'],

  rules: {
    // Correctness — these catch declarations the browser silently drops.
    'property-no-unknown': true,
    'declaration-property-value-no-unknown': true,
    'no-duplicate-selectors': true,
    'block-no-empty': true,
    'no-descending-specificity': true,

    // Design system: reject raw values, require tokens.
    'color-no-hex': true,
    'declaration-property-value-allowed-list': {
      '/^(margin|padding|gap)/': [ '/^var\\(--/', '0', 'auto', 'inherit' ],
    },

    // Modern CSS the codebase has standardized on.
    'color-function-notation': 'modern',      // rgb(0 0 0 / 50%) rather than rgba()
    'media-feature-range-notation': 'context', // (width >= 48rem)

    // Keep the cascade shallow.
    'max-nesting-depth': 2,
    'selector-max-id': 0,
    'selector-max-specificity': '0,4,0',
  },
};
```

For SCSS, add the syntax and its rule set:

```js
// stylelint.config.js
export default {
  extends: ['stylelint-config-standard-scss'],
  rules: {
    'scss/at-extend-no-missing-placeholder': true,   // @extend on a class is a specificity trap
    'scss/no-global-function-names': true,           // math.div, not the deprecated globals
  },
};
```

For a Tailwind codebase, the at-rules must be allowed or every file errors:

```js
// stylelint.config.js
export default {
  rules: {
    'at-rule-no-unknown': [true, {
      ignoreAtRules: ['tailwind', 'apply', 'layer', 'config', 'screen', 'variants'],
    }],
  },
};
```

## Examples

**Good Example** — the rule that keeps tokens authoritative

```css
/* Passes: every value comes from the token layer. */
.card {
	background: var(--color-surface);
	padding: var(--spacing-md);
	border-radius: var(--radius-lg);
	color: rgb(0 0 0 / 87%);
}
```

```css
/* Fails: color-no-hex, and padding is not an allowed token value. */
.card {
	background: #ffffff;
	padding: 17px;
	border-radius: 12px;
}
```

The failure is the point — the second block is exactly what accumulates during a deadline and
is invisible in review once there are forty of them.

**Bad Example** — Stylelint configured as a second formatter

```js
export default {
  rules: {
    indentation: 'tab',              // Prettier's job; the two will disagree
    'string-quotes': 'single',       // same
    'number-leading-zero': 'always', // same
    'color-no-hex': null,            // the rule that would have caught real drift, disabled
  },
};
```

## Common Mistakes

- Formatting rules enabled alongside Prettier, producing conflicts on save.
- `at-rule-no-unknown` left on in a Tailwind project, so `@apply` and `@tailwind` error.
- The wrong syntax package for SCSS or CSS-in-JS, generating parse errors that get the tool
  removed instead of configured.
- Linting compiled or minified CSS.
- `--fix` run over an unformatted codebase in the same commit as real changes.
- No token-enforcement rules, so the design system erodes silently.
- Warnings tolerated rather than fixed.
- Stylelint added but never wired into CI or the pre-commit hook.

## Production Tips

- Run on staged files via lint-staged, and on everything in CI:
  `stylelint "**/*.{css,scss}" --max-warnings 0`.
- Enable caching with `--cache` for local runs.
- Introduce token-enforcement rules with `severity: warning` first, fix the existing
  violations in a dedicated commit, then promote them to errors.
- If the project uses CSS-in-JS, `postcss-styled-syntax` handles template literals; without
  it, every styled component is a parse error.
- Keep the rule set small and deliberate — the same discipline as ESLint: every rule should be
  one the team would otherwise enforce by hand in review.

## AI Review Checklist

- Is Stylelint configured with the syntax matching the project's CSS dialect?
- Are formatting rules absent, leaving those to Prettier?
- For Tailwind, are its at-rules allowed?
- Do rules enforce design tokens rather than only catching syntax errors?
- Is the tool wired into both the pre-commit hook and CI, with zero warnings tolerated?
- Are build output and vendored stylesheets ignored?

## Related

- `knowledge/tools/05-prettier.md`
- `knowledge/tools/04-eslint.md`
- `knowledge/tools/16-git-hooks.md`
- `knowledge/tools/09-vite.md`
- `knowledge/tools/30-engineering-principles.md`
- `knowledge/css/21-architecture.md`
- `knowledge/tailwind/26-best-practices.md`
