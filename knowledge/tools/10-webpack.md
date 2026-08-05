---
id: tools/10-webpack
topic: tools
slug: webpack
title: "Webpack"
type: doc
order: 10
status: ready
tags: [tools, webpack]
related: [tools/09-vite, tools/11-esbuild-and-swc, tools/12-babel, tools/18-monorepo-tools, tools/30-engineering-principles, performance/10-code-splitting]
when_to_use: "Read when working with a Webpack build — configuring loaders and plugins, splitting chunks, or deciding whether to migrate to a faster bundler."
---
# Webpack

## Purpose

This document defines how to work with Webpack: its core concepts, a production-shaped
configuration, and the caching and splitting settings that determine whether users re-download
your whole bundle on every deploy.

## Why It Matters

Webpack remains the bundler underneath `@wordpress/scripts`, older Next.js configurations,
Create React App descendants, and a large share of existing enterprise codebases. Most
engineers now meet it in maintenance rather than greenfield work — which is exactly when a
misconfigured `splitChunks` or a missing content hash quietly costs users a megabyte on every
release.

The other reason to understand it: migration decisions require knowing what the current build
actually does.

## Core Principles

- **Everything is a module.** Loaders transform files into modules; plugins act on the whole
  compilation. Those are separate mechanisms and are often confused.
- **Content hashes are cache correctness.** Without `[contenthash]`, a deploy either serves
  stale assets or invalidates everything.
- **Split by change frequency, not by size.** Vendor code changes rarely; application code
  changes daily. Chunking them together throws away the browser cache on every deploy.
- **Development and production configs differ in kind**, not just in a flag — source maps,
  minification, and hashing all change.

## Best Practices

```js
// webpack.config.js
const path = require('node:path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = (env, argv) => {
  const isProduction = argv.mode === 'production';

  return {
    entry: { main: './src/index.tsx' },

    output: {
      path: path.resolve(__dirname, 'dist'),
      // contenthash changes only when the chunk's content changes.
      filename: isProduction ? '[name].[contenthash:8].js' : '[name].js',
      chunkFilename: isProduction ? '[name].[contenthash:8].chunk.js' : '[name].chunk.js',
      publicPath: '/',
      clean: true,                       // replaces clean-webpack-plugin
    },

    resolve: {
      extensions: ['.tsx', '.ts', '.js'],
      alias: { '@': path.resolve(__dirname, 'src') },   // mirror in tsconfig paths
    },

    module: {
      rules: [
        {
          test: /\.tsx?$/,
          exclude: /node_modules/,
          use: {
            loader: 'swc-loader',        // faster than babel-loader; no type checking either
          },
        },
        {
          test: /\.css$/,
          use: [
            isProduction ? MiniCssExtractPlugin.loader : 'style-loader',
            'css-loader',
            'postcss-loader',
          ],
        },
        {
          test: /\.(png|jpe?g|svg|woff2?)$/,
          type: 'asset',                 // built-in; asset/resource and asset/inline also exist
          parser: { dataUrlCondition: { maxSize: 8 * 1024 } },
        },
      ],
    },

    optimization: {
      // Keep the runtime separate so app changes do not invalidate vendor chunks.
      runtimeChunk: 'single',
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            priority: 10,
          },
        },
      },
    },

    devtool: isProduction ? 'source-map' : 'eval-cheap-module-source-map',

    // Persistent cache: the single biggest local rebuild improvement.
    cache: {
      type: 'filesystem',
      buildDependencies: { config: [__filename] },
    },
  };
};
```

Type checking is a separate step, exactly as with Vite:

```json
{ "scripts": { "build": "tsc --noEmit && webpack --mode production" } }
```

## Examples

**Good Example** — a bundle-size budget that fails the build

```js
// webpack.config.js — alongside output, module, and optimization
module.exports = {
  performance: {
    hints: 'error',
    maxEntrypointSize: 250_000,   // bytes, uncompressed
    maxAssetSize: 250_000,
  },
};
```

A budget enforced by the build is a budget; a number in a document is an aspiration. See
[Performance — Performance Budget](../performance/23-performance-budget.md).

**Bad Example** — configuration that defeats caching and slows every build

```js
module.exports = {
  output: {
    filename: 'bundle.js',        // no hash: either stale caches or none at all
  },
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: 'ts-loader',         // type-checks on every rebuild; slow watch mode
        // no `exclude: /node_modules/` — transpiles dependencies too
      },
    ],
  },
  devtool: 'source-map',          // full source maps in dev: slowest option available
  // no splitChunks: one 3 MB bundle, fully invalidated by any change
};
```

## Common Mistakes

- No `[contenthash]` in production filenames.
- One bundle with no splitting, so every deploy re-downloads all dependencies.
- Missing `exclude: /node_modules/` on the JS/TS rule.
- `ts-loader` in watch mode instead of transpile-only plus a separate `tsc --noEmit`.
- Aliases in Webpack but not in `tsconfig.json`, or vice versa.
- The same `devtool` in development and production.
- No filesystem cache, making cold rebuilds needlessly slow.
- Loaders listed in the wrong order — they apply right to left, so `['style-loader',
  'css-loader']` means css-loader runs first.
- Environment variables inlined via `DefinePlugin` without checking which are safe to publish.

## Production Tips

- Inspect before optimizing: `webpack-bundle-analyzer` shows what the bundle actually
  contains, and the answer is usually one unexpected dependency.
- Migrating to Vite is usually worthwhile for application code, and usually not worth it when
  the build depends on many Webpack-specific plugins or on Module Federation.
- For WordPress projects, prefer `@wordpress/scripts` over a hand-written config — it wraps
  Webpack with the correct externals for `wp.*` globals and block asset handling.
- Keep `mode` explicit. Omitting it defaults to `production` with a warning, which surprises
  people debugging a "slow dev server".

## AI Review Checklist

- Do production filenames include `[contenthash]`?
- Is vendor code split from application code?
- Is `runtimeChunk` extracted so app changes do not invalidate vendors?
- Is type checking a separate step rather than a loader responsibility?
- Are aliases mirrored in TypeScript config?
- Is `devtool` appropriate per mode?
- Is the filesystem cache enabled?
- Is there a size budget that fails the build?

## Related

- `knowledge/tools/09-vite.md`
- `knowledge/tools/11-esbuild-and-swc.md`
- `knowledge/tools/12-babel.md`
- `knowledge/tools/18-monorepo-tools.md`
- `knowledge/tools/30-engineering-principles.md`
- `knowledge/performance/10-code-splitting.md`
