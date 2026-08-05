---
id: frontend/20-bundling
topic: frontend
slug: bundling
title: "Bundling"
type: doc
order: 20
status: ready
tags: [frontend, bundling, sideEffects, immutable, output, webpack-bundle-analyzer, rollup-plugin-visualizer]
related: [frontend/21-code-splitting, frontend/19-build-tools, frontend/08-performance, frontend/18-assets]
when_to_use: "Read before tuning how modules are combined into output files, or reviewing bundle size and caching."
---
# Bundling

## Purpose

This document defines how source modules are combined into the JavaScript and CSS
files the browser downloads: tree shaking, minification, chunking, and long-term
caching. It is written so an agent can shape or review bundle output without shipping
dead code, duplicated dependencies, or cache-busting mistakes.

Bundling is *how* the [build tool](19-build-tools.md) packages your app;
[code splitting](21-code-splitting.md) is the specific technique of breaking one
bundle into many. This doc covers the shared fundamentals that keep total bytes down.

## Why It Matters

Every kilobyte of JavaScript is downloaded, parsed, and executed on the user's device
— and parse/execute cost on a mid-range phone dwarfs the download. A bundle bloated by
dead code, duplicated libraries, or accidental inclusion of a server-only module makes
the whole app slower to become interactive, hurting Interaction to Next Paint and
bounce rate. Bundling also governs caching: chunk the wrong way and a one-line change
invalidates your entire vendor bundle, forcing every returning user to re-download code
that never changed.

## Core Principles

- **Ship only what runs.** Tree shaking must remove unused exports; that requires ES
  modules and no side-effectful imports. Verify it actually happened.
- **Deduplicate dependencies.** One copy of each library. Multiple versions of the same
  package in the graph is silent, expensive bloat.
- **Separate stable from volatile.** Put rarely-changing vendor code in its own
  content-hashed chunk so app changes don't invalidate it.
- **Minify and compress.** Minify JS/CSS at build time and serve Brotli/Gzip over the
  wire — the two compound.
- **Measure the graph, don't guess.** Use a bundle analyzer to see what's actually in
  the output before optimizing.

## Best Practices

- Author and depend on ES-module packages; mark your package `"sideEffects": false`
  (or list the exceptions) so bundlers can drop unused modules safely.
- Import narrowly: `import { debounce } from "lodash-es"` or `lodash/debounce`, never
  `import _ from "lodash"`, which can pull the whole library.
- Content-hash every output filename (`app.[hash].js`) and serve hashed files
  `immutable` so a changed file gets a new URL and everything else stays cached.
- Split vendor code into a separate chunk, and split large independent libraries
  (charting, editors) into their own chunks so they cache and load independently.
- Keep CSS out of the JS bundle: extract it to hashed `.css` files so it can load in
  parallel and cache separately.
- Externalize truly shared runtime deps only when a CDN copy is genuinely reused;
  otherwise bundling is faster than an extra connection.
- Set a bundle-size budget in CI and analyze the graph on regressions.

## Examples

**Good Example** — tree-shakeable, deduped, cache-friendly

```ts
// Narrow imports keep only what is used; ES-module packages tree-shake.
import { debounce } from "lodash-es";
import { formatDate } from "date-fns"; // date-fns is fully tree-shakeable

// Build output (Vite/Rollup): stable vendor chunk is hashed independently
// vendor.4f2a.js   ← react, react-dom (changes rarely → stays cached)
// app.9c1d.js      ← your code (changes often → only this URL busts)
// app.9c1d.css     ← extracted, hashed, loads in parallel
export function render() { /* ... */ }
```
```json
// package.json — declare no side effects so unused modules are dropped
{ "sideEffects": ["*.css"] }
```

**Bad Example** — pulls whole libraries, breaks caching

```ts
import _ from "lodash";           // WHY BAD: default import can defeat tree shaking → ~70 KB
import moment from "moment";      // WHY BAD: not tree-shakeable, bundles all locales (~230 KB)
import "./styles.css";            // fine, but if CSS is inlined into JS it can't cache separately

// Build emits ONE giant unhashed bundle: app.js
// WHY BAD: any code change re-downloads the entire vendor code too;
// no content hash means you must disable caching to avoid staleness.
```

## Common Mistakes

- Default-importing large CommonJS libraries (lodash, moment) that defeat tree shaking.
- Duplicated dependency versions in the graph, silently doubling library weight.
- Non-hashed filenames, forcing a choice between stale caches and no caching.
- Bundling everything into one chunk so a trivial change re-downloads vendor code.
- Leaving `sideEffects` unset, so bundlers keep modules they could have dropped.
- Accidentally bundling server-only or dev-only code (secrets, mocks) into the client.
- Inlining large CSS into JS, preventing parallel download and separate caching.

## Production Tips

- Run `rollup-plugin-visualizer` / `webpack-bundle-analyzer` and review the treemap on
  every significant dependency change.
- Use `npm ls <pkg>` or `pnpm why <pkg>` to find and dedupe multiple versions.
- Enable Brotli at the CDN/edge; precompress static assets at build time when possible.
- Track main-bundle gzip size over time in CI and alert on regressions above a threshold.

## AI Review Checklist

- Is tree shaking effective (narrow imports, ES modules, `sideEffects` declared)?
- Are dependencies deduplicated to a single version each?
- Are output filenames content-hashed and served `immutable`?
- Is stable vendor code split from volatile app code for independent caching?
- Is CSS extracted to hashed files rather than inlined into JS?
- Is there a bundle-size budget enforced in CI with an analyzer available?

## Related

- `knowledge/frontend/21-code-splitting.md`
- `knowledge/frontend/19-build-tools.md`
- `knowledge/frontend/08-performance.md`
- `knowledge/frontend/18-assets.md`
