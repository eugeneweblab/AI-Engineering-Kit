---
id: tools/12-babel
topic: tools
slug: babel
title: "Babel"
type: doc
order: 12
status: ready
tags: [tools, babel]
related: [tools/11-esbuild-and-swc, tools/10-webpack, tools/13-test-runners, tools/09-vite, tools/30-engineering-principles, javascript/17-es6-features]
when_to_use: "Read when a project still uses Babel — configuring presets and browser targets, understanding polyfills, or deciding whether to migrate away."
---
# Babel

## Purpose

This document defines how to work with Babel where it is still the right tool: browser-target
transpilation, polyfill strategy, and plugin-based transforms that faster tools cannot
perform. It also states plainly when to migrate away.

## Why It Matters

Babel has been displaced by esbuild and SWC for the common case, but it remains the only
option for several real situations: broad legacy browser support, custom AST transforms, and
compile-time macros. Meanwhile, many existing codebases still run it — often with a
`browserslist` targeting browsers nobody uses, transpiling modern syntax into bulky ES5 for no
reason.

Auditing that configuration is frequently the single largest available bundle reduction.

## Core Principles

- **Targets decide output size.** `browserslist` is the most consequential setting in the
  project; an over-broad target inflates every file.
- **`preset-env` needs targets to be useful.** Without them it transpiles to ES5 by default.
- **Polyfills are separate from syntax.** Babel transforms syntax; `core-js` supplies missing
  APIs. Conflating them produces either bloat or runtime errors.
- **Migrate when no plugin does real work.** If the config is only `preset-env` and
  `preset-typescript`, SWC or esbuild will do the same job far faster.

## Best Practices

```js
// babel.config.js
module.exports = {
  presets: [
    ['@babel/preset-env', {
      // Read from browserslist; do not duplicate the list here.
      bugfixes: true,
      // 'usage' injects only the polyfills the code actually needs.
      useBuiltIns: 'usage',
      corejs: { version: '3.38', proposals: false },
    }],
    ['@babel/preset-react', { runtime: 'automatic' }],
    '@babel/preset-typescript',   // strips types; does NOT check them
  ],
  plugins: [],
};
```

```
# .browserslistrc — the single source of truth for targets
> 0.5%
last 2 versions
not dead
not op_mini all
```

Check what that resolves to before assuming it is reasonable:

```bash
npx browserslist                       # the actual browser list
npx browserslist --coverage            # what share of users it covers
```

A target list including IE 11 or Android 4 in 2026 costs every user extra bytes for browsers
with no measurable traffic. Modern applications targeting `defaults and supports es6-module`
ship substantially less code.

## Polyfills

```js
// useBuiltIns: 'usage' — Babel inspects each file and injects only what it uses.
// Requires core-js as a real dependency, not a devDependency.
const items = [1, 2, 3].flatMap((n) => [n, n * 2]);
// → import "core-js/modules/es.array.flat-map.js" injected automatically when targets need it
```

Two rules prevent the common failures:

- **`core-js` is a runtime dependency.** In `devDependencies` it disappears from a production
  install and the app throws on first use.
- **For libraries, use `@babel/plugin-transform-runtime`** with `corejs: 3` instead of
  `useBuiltIns: 'usage'`. The former imports helpers from a namespaced runtime; the latter
  pollutes the consumer's globals with polyfills they did not ask for.

## Examples

**Good Example** — Babel where it is genuinely required

```js
// A compile-time transform no single-file transpiler can perform:
// this plugin reads a GraphQL document at build time and inlines the parsed AST.
module.exports = {
  presets: [['@babel/preset-env', { useBuiltIns: 'usage', corejs: '3.38' }]],
  plugins: ['babel-plugin-graphql-tag', 'babel-plugin-macros'],
};
```

**Bad Example** — paying Babel's cost for nothing

```js
// No plugins, no macros, no legacy targets — SWC does this 20x faster.
module.exports = {
  presets: ['@babel/preset-env', '@babel/preset-typescript'],
};
```

```
# ...combined with a target list that inflates every output file:
ie 11
> 0.1%
```

**Bad Example** — the polyfill that is missing in production

```json
{
  "devDependencies": { "core-js": "^3.38.0" }
}
```

```bash
npm ci --omit=dev     # core-js not installed
# → Uncaught Error: Cannot find module 'core-js/modules/es.array.flat-map.js'
```

## Common Mistakes

- No `browserslist`, so `preset-env` transpiles to ES5 by default.
- A target list inherited from years ago and never re-examined.
- `core-js` in `devDependencies`.
- `useBuiltIns: 'entry'` without the corresponding import, so no polyfills are injected at all.
- `useBuiltIns: 'usage'` in a published library, forcing polyfills onto consumers.
- Assuming `preset-typescript` checks types.
- Babel and SWC both configured in one project, each transforming a different subset of files.
- `babel.config.js` versus `.babelrc` confusion: the former applies repository-wide, the
  latter only to its own directory tree — a frequent cause of "the config is ignored" in
  monorepos.

## Production Tips

- Audit targets first when reducing bundle size; it usually beats any code change available.
- Enable Babel's cache in Webpack (`cacheDirectory: true` on `babel-loader`) — it is the
  difference between a tolerable and an intolerable watch mode.
- To migrate away, remove Babel-specific plugins one at a time, verify output equivalence, then
  swap the loader for `swc-loader` or move the project to Vite.
- If Jest is the only remaining Babel consumer, `@swc/jest` replaces `babel-jest` with no
  behavioral change in most projects — see [Test Runners](13-test-runners.md).

## AI Review Checklist

- Does a `browserslist` exist, and does its coverage match the real audience?
- Is `core-js` a runtime dependency with a pinned major?
- Is the polyfill strategy correct for the artifact type (app versus library)?
- Is type checking handled separately from `preset-typescript`?
- Do any plugins perform work that a faster transpiler cannot?
- Is there exactly one transpiler configured for the project?
- Is Babel's cache enabled in the build?

## Related


- `knowledge/tools/11-esbuild-and-swc.md`
- `knowledge/tools/10-webpack.md`
- `knowledge/tools/13-test-runners.md`
- `knowledge/tools/09-vite.md`
- `knowledge/tools/30-engineering-principles.md`
- `knowledge/javascript/17-es6-features.md`
