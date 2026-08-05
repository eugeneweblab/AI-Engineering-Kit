---
id: tools/14-playwright
topic: tools
slug: playwright
title: "Playwright"
type: doc
order: 14
status: ready
tags: [tools, playwright]
related: [tools/13-test-runners, tools/15-storybook, tools/21-debuggers, tools/29-observability-tools, tools/30-engineering-principles, testing/04-e2e-testing, testing/22-flaky-tests, figma/13-visual-regression]
when_to_use: "Read before writing or configuring browser tests — setting up Playwright, choosing selectors, handling authentication, or fixing flaky E2E runs."
---
# Playwright

## Purpose

This document defines how to configure and write Playwright tests: auto-waiting and why manual
waits are a defect, selector strategy, reusing authentication state, and the settings that
decide whether an E2E suite is trusted or routinely ignored.

## Why It Matters

End-to-end tests are the most expensive tests to run and the most valuable when they fail
honestly. The problem is that they usually do not: a suite with hardcoded waits, CSS
selectors, and shared state fails randomly, and a randomly failing suite gets re-run until
green. At that point it costs CI minutes and provides no signal.

Almost all of that flakiness is preventable through configuration and selector discipline.

## Core Principles

- **Never sleep.** Playwright's assertions and locators auto-wait. A `waitForTimeout` is
  either unnecessary or hiding a race that will resurface.
- **Select by role and accessible name.** That is what a user perceives; a CSS class is an
  implementation detail that changes with every refactor.
- **Every test owns its state.** Tests that depend on order or on data left by another test
  fail as soon as they are parallelized or sharded.
- **Test flows, not units.** E2E is for paths that cross real boundaries — login, checkout,
  publishing. Everything else belongs in cheaper tests.

## Best Practices

```ts
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,        // a stray test.only cannot land on main
  retries: process.env.CI ? 2 : 0,     // retries in CI only, and they must be visible
  workers: process.env.CI ? 2 : undefined,

  reporter: process.env.CI
    ? [['html', { open: 'never' }], ['github']]
    : [['list']],

  use: {
    baseURL: process.env.BASE_URL ?? 'http://localhost:3000',
    trace: 'on-first-retry',           // full timeline for the failure, no cost when passing
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  projects: [
    { name: 'setup', testMatch: /auth\.setup\.ts/ },
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'], storageState: 'e2e/.auth/user.json' },
      dependencies: ['setup'],
    },
  ],

  // Start the app automatically; reuse a running server locally.
  webServer: {
    command: 'pnpm build && pnpm start',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
```

Authenticate once and reuse the session, rather than logging in per test:

```ts
// e2e/auth.setup.ts
import { test as setup, expect } from '@playwright/test';

setup('authenticate', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill(process.env.E2E_USER!);
  await page.getByLabel('Password').fill(process.env.E2E_PASSWORD!);
  await page.getByRole('button', { name: 'Sign in' }).click();

  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();

  await page.context().storageState({ path: 'e2e/.auth/user.json' });
});
```

## Examples

**Good Example** — user-visible selectors, web-first assertions, no waits

```ts
import { test, expect } from '@playwright/test';

test('a customer can complete checkout', async ({ page }) => {
  await page.goto('/products/blue-widget');

  await page.getByRole('button', { name: 'Add to cart' }).click();
  await expect(page.getByRole('status')).toHaveText('Added to cart');

  await page.getByRole('link', { name: 'Checkout' }).click();
  await page.getByLabel('Card number').fill('4242424242424242');
  await page.getByRole('button', { name: 'Pay' }).click();

  // Auto-retries until the condition holds or the timeout expires.
  await expect(page.getByRole('heading', { name: 'Order confirmed' })).toBeVisible();
  await expect(page).toHaveURL(/\/orders\/\d+/);
});
```

**Bad Example** — every line is a source of flakiness

```ts
test('checkout', async ({ page }) => {
  await page.goto('/products/blue-widget');

  await page.click('.btn-primary.add-to-cart');   // breaks on any styling change
  await page.waitForTimeout(2000);                // too long locally, too short in CI

  await page.click('#checkout-link');
  await page.fill('input[name="card"]', '4242424242424242');
  await page.click('.pay');

  await page.waitForTimeout(3000);
  // Not a web-first assertion: reads the DOM once, with no retry.
  expect(await page.textContent('h1')).toBe('Order confirmed');
});
```

**Good Example** — isolating state through the API rather than the UI

```ts
test.beforeEach(async ({ request }) => {
  // Create fixtures via the API: faster and independent of UI changes.
  await request.post('/api/test/reset', { data: { seed: 'checkout' } });
});
```

## Common Mistakes

- `waitForTimeout` anywhere.
- CSS or XPath selectors instead of roles, labels, and `data-testid`.
- Logging in through the UI in every test.
- Tests that depend on data created by a previous test.
- Retries used to mask a real race rather than to absorb infrastructure noise.
- `test.only` committed — prevented by `forbidOnly` in CI.
- Traces and videos disabled, leaving CI failures undiagnosable.
- E2E tests written for logic that a unit test covers in milliseconds.
- Running against a production or shared database.

## Production Tips

- Open `trace.zip` in `npx playwright show-trace` for a failure: DOM snapshots, network, and
  console at every step. It answers most "cannot reproduce locally" questions immediately.
- Use `npx playwright codegen` to draft a test, then rewrite its selectors — the generator
  produces working code with poor selector choices.
- Keep the E2E suite small and about critical journeys. Ten reliable tests catch more real
  regressions than a hundred flaky ones.
- Add `data-testid` deliberately for elements with no accessible name, and treat it as part of
  the component contract.
- Combine with visual regression where layout matters — see
  [Figma — Visual Regression](../figma/13-visual-regression.md).

## AI Review Checklist

- Are there any `waitForTimeout` calls?
- Do locators use roles, labels, or explicit test IDs rather than CSS?
- Are assertions web-first (`await expect(locator)`) rather than one-shot DOM reads?
- Does each test set up its own state, and can the suite run fully parallel?
- Is authentication reused via `storageState`?
- Are trace, screenshot, and video enabled for failures?
- Is `forbidOnly` set in CI, and are retries limited and visible?
- Does the suite cover critical journeys only?

## Related

- `knowledge/tools/13-test-runners.md`
- `knowledge/tools/15-storybook.md`
- `knowledge/tools/21-debuggers.md`
- `knowledge/tools/29-observability-tools.md`
- `knowledge/tools/30-engineering-principles.md`
- `knowledge/testing/04-e2e-testing.md`
- `knowledge/testing/22-flaky-tests.md`
- `knowledge/figma/13-visual-regression.md`
