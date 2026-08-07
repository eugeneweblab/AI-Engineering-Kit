---
id: frontend/19-build-tools
topic: frontend
slug: build-tools
title: "Build Tools"
type: doc
order: 19
status: ready
tags: [frontend, build-tools, browserslist, STRIPE_SECRET, "@vitejs", react, defineConfig]
related: [frontend/20-bundling, frontend/21-code-splitting, frontend/18-assets, frontend/22-testing]
when_to_use: "Read before configuring or reviewing the toolchain that compiles, bundles, and serves a frontend app."
---
# Build Tools

## Purpose

This document defines how to choose and configure the build toolchain — the dev
server, transpiler, bundler, and task runner that turn source into shippable assets.
It is written so an agent can set up or review a build without creating slow,
non-reproducible, or insecure pipelines.

The build tool is the foundation everything else sits on. It decides how fast the
feedback loop is in development and how small and correct the output is in production.
It is closely tied to [bundling](20-bundling.md) and [code splitting](21-code-splitting.md),
which describe *what* the build produces.

## Why It Matters

A slow or misconfigured build taxes every developer on every change, and a
non-reproducible build ships different bytes to production than you tested locally.
Build tools also run arbitrary code from your dependency tree at compile time, making
them a supply-chain attack surface. And the difference between a naive and a tuned
build config is routinely a 2–5x difference in bundle size — bytes every user pays for.
Because the build sits between your code and every user, its defaults quietly shape
performance, security, and developer velocity all at once.

## Core Principles

- **Prefer the platform's fast default.** In 2026 use **Vite** (Rollup/Rolldown) for
  apps and a framework's built-in build (Next.js, Remix, Astro) when you use one.
  Reach for Webpack only to maintain existing config.
- **Separate dev and prod concerns.** Dev optimizes for fast HMR and readable errors;
  prod optimizes for minified, hashed, tree-shaken output. Never ship dev builds.
- **Make builds reproducible.** A lockfile plus a pinned toolchain must yield identical
  output on any machine and in CI. No network fetches at build time beyond dependencies.
- **Target real browsers, not "latest".** Drive transpilation and polyfills from an
  explicit `browserslist`; over-transpiling bloats modern browsers, under-transpiling
  breaks old ones.
- **Keep config declarative and minimal.** Every custom plugin or loader is code you
  must maintain and a supply-chain risk. Add only what earns its place.

## Best Practices

- Use ES modules and `esbuild`/`swc`-based transpilation (built into Vite) instead of
  Babel for speed; add Babel only for a specific plugin you cannot replace.
- Define `browserslist` in `package.json` and let it drive both transpilation and CSS
  autoprefixing so the two never disagree.
- Load configuration from typed env files (`import.meta.env`), and expose only
  variables with a public prefix (e.g. `VITE_`) to the client — never leak secrets.
- Enable source maps in production but upload them to your error tracker rather than
  serving them publicly.
- Pin the Node and package-manager version (`engines`, `packageManager`, `.nvmrc`) so
  CI and local builds match.
- Run the build in CI on every PR and fail on warnings, type errors, and budget
  overruns — the build is a quality gate, not just a packaging step.
- Cache node_modules and the build cache in CI keyed by the lockfile hash to keep
  builds fast without sacrificing reproducibility.

## Examples

**Good Example** — minimal, explicit, reproducible Vite config

```ts
// vite.config.ts — targets are explicit, secrets are not exposed
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  build: {
    target: "es2022",        // matches browserslist; no needless down-compiling
    sourcemap: "hidden",     // generated for the tracker, not served to users
    rollupOptions: {
      output: { manualChunks: { vendor: ["react", "react-dom"] } },
    },
  },
  // Only VITE_-prefixed vars reach the client; API keys stay server-side.
});
```
```json
// package.json — pinned toolchain makes the build reproducible
{
  "engines": { "node": ">=24" },
  "packageManager": "pnpm@9.12.0",
  "browserslist": ["> 0.5%", "last 2 versions", "not dead"]
}
```

**Bad Example** — non-reproducible and leaky

```ts
// vite.config.ts
export default {
  define: {
    // WHY BAD: inlines a real secret into client JS — visible to every user.
    "process.env.STRIPE_SECRET": JSON.stringify(process.env.STRIPE_SECRET),
  },
  build: { target: "esnext" }, // WHY BAD: no browserslist → breaks on older supported browsers
};
// No engines/packageManager pin → CI installs a different toolchain than the dev used,
// so the bytes tested locally are not the bytes shipped.
```

## Common Mistakes

- Serving a development build (unminified, HMR runtime included) to production.
- Inlining secrets into client bundles via `define`/env without a public prefix.
- Targeting `esnext` or `latest` with no `browserslist`, silently dropping supported users.
- Over-transpiling to ES5 for browsers that all support modern syntax, bloating output.
- Adding heavyweight Babel/Webpack plugins when the fast native toolchain already covers it.
- Unpinned Node/package-manager versions, so builds differ between laptop and CI.
- Publicly serving source maps that expose original source and comments.

## Production Tips

- Run `vite build` (or equivalent) with `--profile` occasionally to spot slow plugins.
- Split env config per environment (`.env.production`, `.env.staging`) and validate it
  at build start; fail fast on a missing required variable.
- Keep the toolchain patched — build tools are a supply-chain target; enable Dependabot
  and audit plugins before adding them.

## AI Review Checklist

- Is the production build minified, hashed, and tree-shaken (not a dev build)?
- Is `browserslist` defined and driving transpilation/autoprefixing?
- Are only public-prefixed env vars exposed to the client, with no secrets inlined?
- Are Node and the package manager pinned so CI matches local?
- Does CI run the build and fail on type errors, warnings, and budget overruns?
- Are production source maps generated but not publicly served?

## Related

- `knowledge/frontend/20-bundling.md`
- `knowledge/frontend/21-code-splitting.md`
- `knowledge/frontend/18-assets.md`
- `knowledge/frontend/22-testing.md`
