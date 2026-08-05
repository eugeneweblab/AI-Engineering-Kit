---
id: testing/04-e2e-testing
topic: testing
slug: e2e-testing
title: "E2E Testing"
type: doc
order: 4
status: ready
tags: [testing, e2e-testing, getByRole, goto, waitForTimeout, click, toBeVisible, textContent]
related: [testing/03-integration-testing, testing/13-ui-testing, testing/22-flaky-tests, testing/28-testing-strategy, testing/01-testing-fundamentals]
when_to_use: "Read before writing or reviewing a test that drives the whole system through its real entry point."
---
# E2E Testing

## Purpose

This document defines how to write end-to-end (E2E) tests: tests that drive the entire
system through its real entry point — a browser, a mobile app, or the public API — with
all real services running behind it. E2E tests sit at the top of the pyramid: the fewest,
the slowest, the most valuable per test but the most expensive to keep green. It is
written so an agent knows which flows deserve an E2E test and how to keep the suite from
becoming a flaky bottleneck.

An E2E test asks the question a user asks: *can I actually complete this journey?* Nothing
is mocked; the test exercises real wiring, real config, and real deployment glue.

## Why It Matters

Every other test layer verifies a part in isolation and *assumes* the parts connect. E2E
tests are the only ones that verify the assembled system: routing, auth, environment
config, third-party integrations, and the UI all cooperating. That is why a single E2E
test on checkout catches whole categories of "each piece worked but the app was broken"
outages. But E2E tests are also the slowest and flakiest — real timing, real networks,
real async UI. So the rule is inverted from unit tests: write as *few* as you can get away
with, covering only the journeys whose breakage would be a serious incident.

## Core Principles

- **Cover critical journeys only.** Sign-up, login, checkout, the core money path. If a
  flow breaking would not page someone, it does not need an E2E test.
- **Test as the user, through the real interface.** Interact via the UI or public API;
  never reach into the database or internal functions to shortcut the flow.
- **Do not re-test logic here.** Branches, validation, and edge cases belong in
  [unit](02-unit-testing.md) and [integration](03-integration-testing.md) tests. E2E
  verifies the assembly, not the arithmetic.
- **Determinism is the hardest and most important property.** Wait on *conditions*, never
  fixed sleeps; the top cause of [flaky tests](22-flaky-tests.md) lives here.
- **Isolate test data.** Each run creates the accounts and records it needs and cleans up,
  so runs do not collide.

## Best Practices

- Use a modern runner with auto-waiting and retry-until-visible assertions (Playwright or
  equivalent) so you assert on state, not on timers. See [UI testing](13-ui-testing.md).
- Select elements by user-facing roles and accessible labels (`getByRole`, `getByLabel`),
  not brittle CSS or XPath that break on any markup change.
- Never `sleep(2000)`. Wait for the element, response, or network idle you actually need —
  a fixed sleep is either too short (flaky) or too long (slow), never right.
- Seed state through the fastest reliable path (an API call or fixture), then *verify* the
  journey through the UI. Do not click through setup you are not testing.
- Keep each test independent and runnable in parallel with unique data; a shared account
  makes tests fight over state.
- Run E2E in a separate, later CI stage; quarantine and fix a flaky test immediately
  rather than adding blanket retries that hide real bugs.

## Examples

**Good Example** — real user path, condition-based waiting, stable selectors

```ts
import { test, expect } from "@playwright/test";

test("a signed-in user can check out a cart", async ({ page }) => {
  await loginViaApi(page, seededUser); // fast setup outside the flow under test

  await page.goto("/cart");
  await page.getByRole("button", { name: "Checkout" }).click(); // user-facing selector

  // Waits for the actual condition, not a fixed timer → deterministic.
  await expect(page.getByRole("heading", { name: "Order confirmed" })).toBeVisible();
});
```

**Bad Example** — fixed sleeps, brittle selectors, tests logic that belongs lower

```ts
test("checkout", async ({ page }) => {
  await page.goto("/cart");
  await page.click(".btn-primary.checkout-2"); // breaks on any CSS change
  await page.waitForTimeout(3000);             // flaky if slow, wasteful if fast

  // Re-checks discount math that a unit test already covers, in the slowest layer.
  expect(await page.textContent(".total")).toContain("180");
});
```

## Common Mistakes

- Fixed `waitForTimeout`/`sleep` calls instead of waiting on a condition — the single
  biggest source of E2E flakiness.
- Selecting elements by CSS classes or DOM structure that change on any restyle.
- Pushing edge-case and validation coverage into E2E, producing a slow suite that
  duplicates cheaper tests.
- Sharing accounts or data between tests, so parallel runs corrupt each other.
- Masking flakiness with automatic retries instead of fixing the race — retries hide real
  intermittent bugs from users.
- Shortcutting the flow by writing directly to the database, so the test no longer proves
  the user path works.

## Production Tips

- Run the critical-path E2E suite against a production-like environment before every
  deploy; it is the last gate that sees the whole system assembled.
- Capture a video, trace, and screenshot on failure — an E2E failure is expensive to
  reproduce by hand, so make the artifact do it for you.
- Track flakiness rate as a metric and treat a flaky E2E test as a broken test, not noise.

## AI Review Checklist

- Does the test cover a genuinely critical user journey, not incidental logic?
- Does it interact through the real UI/API rather than reaching into internals?
- Are all waits condition-based, with zero fixed sleeps?
- Are selectors based on user-facing roles/labels, not brittle CSS or XPath?
- Does each test create and clean up its own data and run safely in parallel?
- Is edge-case logic tested at a cheaper level instead of here?

## Related

- `knowledge/testing/01-testing-fundamentals.md`
- `knowledge/testing/03-integration-testing.md`
- `knowledge/testing/13-ui-testing.md`
- `knowledge/testing/22-flaky-tests.md`
- `knowledge/testing/28-testing-strategy.md`
