---
id: tools/13-test-runners
topic: tools
slug: test-runners
title: "Test Runners"
type: doc
order: 13
status: ready
tags: [tools, test-runners, useRealTimers, cleanup, toBeInTheDocument, defineConfig, afterEach, getByRole]
related: [tools/14-playwright, tools/09-vite, tools/11-esbuild-and-swc, tools/19-task-runners, tools/30-engineering-principles, testing/00-overview]
when_to_use: "Read before choosing or configuring a test runner — Vitest, Jest, or PHPUnit — including coverage, watch mode, and CI parallelism."
---
# Test Runners

## Purpose

This document defines how to configure the tools that execute tests: Vitest and Jest for
JavaScript, PHPUnit for PHP. It covers the configuration that determines speed and
reliability, not what to test — that is the [Testing](../testing/00-overview.md) topic.

## Why It Matters

The runner decides whether the suite is used. A suite that takes twelve minutes runs in CI
only; a suite that runs in eight seconds runs on every save, and defects are caught while the
context is still in the developer's head. That difference is mostly configuration:
transformation cost, parallelism, and how much of the environment each test loads.

## Core Principles

- **Match the runner to the build.** Vitest reuses Vite's config and resolver, so aliases and
  plugins work without a parallel setup. Using a different transform pipeline for tests than
  for the app guarantees divergence.
- **Isolation by default, shared only when measured.** Parallel workers with isolated
  environments prevent cross-test pollution; disabling isolation is a speed optimization with
  correctness risk.
- **Coverage is a report, not a gate on every run.** Collecting it on every watch run makes
  the loop slow for no benefit.
- **One command runs everything.** `pnpm test` and `composer test` must work with no
  arguments, identically in CI.

## Best Practices

```ts
// vitest.config.ts — inherits resolve.alias and plugins from vite.config.ts
import { defineConfig, mergeConfig } from 'vitest/config';
import viteConfig from './vite.config';

export default mergeConfig(viteConfig, defineConfig({
  test: {
    environment: 'jsdom',            // 'node' for server code — much faster
    globals: true,                   // describe/it/expect without imports
    setupFiles: ['./tests/setup.ts'],
    restoreMocks: true,              // reset spies between tests automatically
    clearMocks: true,

    // Isolation costs time; keep it on unless a measurement says otherwise.
    pool: 'threads',

    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov'],
      include: ['src/**/*.{ts,tsx}'],
      exclude: ['**/*.test.*', '**/*.stories.*', 'src/types/**'],
      thresholds: { lines: 80, functions: 80, branches: 70 },
    },
  },
}));
```

```ts
// tests/setup.ts — deterministic environment for every test
import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach, vi } from 'vitest';

afterEach(() => {
  cleanup();
  vi.useRealTimers();     // a leaked fake timer breaks the NEXT test, confusingly
});
```

For PHP:

```xml
<?xml version="1.0"?>
<phpunit xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:noNamespaceSchemaLocation="vendor/phpunit/phpunit/phpunit.xsd"
         bootstrap="tests/bootstrap.php"
         colors="true"
         failOnWarning="true"
         failOnDeprecation="true"
         beStrictAboutOutputDuringTests="true">
	<testsuites>
		<testsuite name="unit">
			<directory>tests/Unit</directory>
		</testsuite>
		<testsuite name="integration">
			<directory>tests/Integration</directory>
		</testsuite>
	</testsuites>
	<source>
		<include><directory>src</directory></include>
	</source>
</phpunit>
```

`failOnWarning` and `failOnDeprecation` matter more than they look: deprecation notices are
the early warning for the next PHP or framework upgrade, and they are invisible unless the
suite fails on them.

## Examples

**Good Example** — split suites so the fast one can run constantly

```json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest",
    "test:unit": "vitest run tests/unit",
    "test:coverage": "vitest run --coverage"
  }
}
```

```yaml
# CI: shard a large suite across machines
strategy:
  matrix:
    shard: [1, 2, 3, 4]
steps:
  - run: pnpm vitest run --shard=${{ matrix.shard }}/4 --reporter=verbose
```

**Bad Example** — a configuration that makes the suite unusable

```json
{
  "scripts": {
    "test": "vitest --coverage --no-threads"
  }
}
```

Watch mode with coverage on every save, single-threaded, is often ten times slower than
necessary — and being the default `test` script, it is also what CI runs.

**Bad Example** — nondeterminism from shared state

```tsx
// No cleanup between tests: the DOM from the previous test is still mounted,
// and getByRole finds two matching elements — failing only when run in a certain order.
test('renders the form', () => {
  render(<Form />);
  expect(screen.getByRole('button')).toBeInTheDocument();
});
```

## Common Mistakes

- A different transform pipeline for tests than for the application.
- Coverage collected on every watch run.
- No cleanup between tests, producing order-dependent failures.
- Fake timers or mocked modules leaking across tests.
- `jsdom` used for pure server-side code, paying a large startup cost per file.
- Coverage thresholds set to 100%, which drives tests written for the metric.
- A `test` script that requires arguments or environment setup to work.
- PHPUnit configured without `failOnWarning`, so deprecations accumulate silently.
- CI running the watch-mode command and hanging until it times out.

## Production Tips

- Run unit tests on every commit, integration tests on every push, and E2E on pull requests —
  match the cost of the suite to the frequency of the trigger.
- Shard long suites in CI; four shards typically cut wall-clock time by ~3x.
- Report coverage as a trend rather than a gate at a fixed number. A drop of five points in a
  pull request is meaningful; a threshold of 80% is arbitrary.
- Prefer `environment: 'node'` per-file (via a docblock or a suite split) rather than jsdom
  globally.
- If migrating Jest to Vitest, the APIs are largely compatible; the usual work is replacing
  `jest.mock` semantics and moving config into `vitest.config.ts`.

## AI Review Checklist

- Does the runner share the application's transform and resolver configuration?
- Does `test` run once, exit, and require no arguments?
- Is state — DOM, mocks, timers — reset between tests automatically?
- Is coverage separate from the default run?
- Is the environment (`node` vs `jsdom`) chosen per suite rather than globally?
- Are long suites sharded in CI?
- For PHPUnit, does the suite fail on warnings and deprecations?

## Related

- `knowledge/tools/14-playwright.md`
- `knowledge/tools/09-vite.md`
- `knowledge/tools/11-esbuild-and-swc.md`
- `knowledge/tools/19-task-runners.md`
- `knowledge/tools/30-engineering-principles.md`
- `knowledge/testing/00-overview.md`
