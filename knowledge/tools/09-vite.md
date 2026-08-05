---
id: tools/09-vite
topic: tools
slug: vite
title: "Vite"
type: doc
order: 9
status: ready
tags: [tools, vite]
related: [tools/10-webpack, tools/11-esbuild-and-swc, tools/13-test-runners, tools/03-typescript-compiler, tools/30-engineering-principles]
when_to_use: "Read before configuring a Vite build — setting up dev server, environment variables, aliases, proxying, or optimizing the production bundle."
---
# Vite

## Purpose

This document defines how to configure Vite: how its two-mode architecture works, how
environment variables are exposed (and accidentally leaked), and which build options matter
for production output.

## Why It Matters

Vite behaves differently in development and production — native ESM with on-demand transforms
in dev, a Rollup bundle in build. That split is why it is fast, and also why "works in dev,
breaks in build" is its characteristic failure. Understanding which mode does what turns that
class of bug from mysterious into obvious.

The second recurring issue is environment variables: Vite inlines anything prefixed `VITE_`
into the client bundle. A secret given that prefix is published to every visitor.

## Core Principles

- **Dev and build are different pipelines.** Always verify with `vite build && vite preview`
  before shipping; dev-only success proves little.
- **Only `VITE_`-prefixed variables reach the client** — and everything with that prefix
  reaches the client. There are no client-side secrets.
- **Vite does not type-check.** esbuild strips types without validating them; `tsc --noEmit`
  is a separate, required step.
- **Aliases must be declared twice** — in `vite.config.ts` and in `tsconfig.json` — or the
  editor and the build disagree.

## Best Practices

```ts
// vite.config.ts
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import { fileURLToPath, URL } from 'node:url';

export default defineConfig(({ mode }) => {
  // Third arg '' loads ALL vars, including unprefixed ones — for config use only,
  // never for injecting into client code.
  const env = loadEnv(mode, process.cwd(), '');

  return {
    plugins: [react()],

    resolve: {
      alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
    },

    server: {
      port: 5173,
      proxy: {
        // Avoids CORS in development without weakening the API's production config.
        '/api': {
          target: env.API_URL ?? 'http://localhost:8000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
        },
      },
    },

    build: {
      target: 'es2022',
      sourcemap: true,          // ship maps to the error tracker, not necessarily to users
      rollupOptions: {
        output: {
          // Split rarely-changing dependencies so app deploys do not bust their cache.
          manualChunks: {
            react: ['react', 'react-dom'],
          },
        },
      },
    },
  };
});
```

Environment variables, with the boundary made explicit:

```bash
# .env.local — gitignored
VITE_API_URL=https://api.example.com     # public: shipped in the bundle
VITE_SENTRY_DSN=https://…                # public by design
DATABASE_URL=postgres://…                # NOT exposed — no VITE_ prefix
STRIPE_SECRET_KEY=sk_live_…              # NOT exposed
```

```ts
// src/env.ts — validate once, fail at startup rather than at first use
const apiUrl = import.meta.env.VITE_API_URL;

if (!apiUrl) {
  throw new Error('VITE_API_URL is not set');
}

export const env = { apiUrl } as const;
```

## Examples

**Good Example** — a build pipeline that catches what Vite does not

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc --noEmit && vite build",
    "preview": "vite preview",
    "verify": "pnpm typecheck && pnpm lint && pnpm test && pnpm build"
  }
}
```

**Bad Example** — a secret published to every visitor

```bash
# .env
VITE_STRIPE_SECRET_KEY=sk_live_51H...    # inlined into the JS bundle, world-readable
```

```ts
// The value is not "read at runtime from the server" — it is a literal in the shipped file.
const stripe = new Stripe(import.meta.env.VITE_STRIPE_SECRET_KEY);
```

Anything a browser can use, a visitor can extract. Secrets belong on a server; the client gets
publishable keys only.

**Bad Example** — dev-only verification

```bash
pnpm dev        # works
git push        # production build fails: a dependency has no ESM entry,
                # a dynamic import path is not statically analyzable,
                # or an unused import was tree-shaken away with its side effect
```

## Common Mistakes

- Secrets given a `VITE_` prefix.
- No `tsc --noEmit`, so types are never checked.
- Aliases in `vite.config.ts` but not in `tsconfig.json` (or vice versa).
- Never running `vite build` locally before pushing.
- `import.meta.env` used without validation, so a missing variable becomes `undefined` deep in
  the app.
- Sourcemaps disabled in production, making error-tracker stack traces unusable.
- Everything in one chunk, so any change invalidates the entire cached bundle.
- Node-only packages imported into client code, failing at build with confusing polyfill
  errors.

## Production Tips

- Analyze the bundle before optimizing it: `rollup-plugin-visualizer` shows what is actually
  large, which is rarely what the team assumes.
- Prefer dynamic `import()` at route boundaries over manual chunking; manual chunks are for
  stable vendor code.
- Upload sourcemaps to the error tracker and exclude them from the public deploy if the code
  is sensitive.
- Vitest shares Vite's config and resolver, so aliases and plugins work in tests without a
  second setup — see [Test Runners](13-test-runners.md).
- For a library rather than an app, use `build.lib` with `external` for peer dependencies, so
  consumers do not get a second copy of React.

## AI Review Checklist

- Are all `VITE_`-prefixed variables safe to publish?
- Does the build script run `tsc --noEmit` before `vite build`?
- Are aliases declared in both Vite and TypeScript config?
- Is `vite build && vite preview` part of local verification and CI?
- Are environment variables validated at startup?
- Are sourcemaps generated and routed to the error tracker?
- Is the chunk strategy deliberate rather than default-everything?

## Related

- `knowledge/tools/10-webpack.md`
- `knowledge/tools/11-esbuild-and-swc.md`
- `knowledge/tools/13-test-runners.md`
- `knowledge/frontend/19-build-tools.md`
