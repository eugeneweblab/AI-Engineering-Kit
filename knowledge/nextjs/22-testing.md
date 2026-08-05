---
id: nextjs/22-testing
topic: nextjs
slug: testing
title: "Next.js Testing"
type: doc
order: 22
status: ready
tags: [nextjs, testing]
related: [nextjs/06-server-components, testing/04-e2e-testing, react/21-testing]
when_to_use: "Read before setting up or writing automated tests for a Next.js app."
---
# Next.js Testing

## Purpose

This document defines the engineering standards for testing Next.js applications.

The objective is to build reliable, maintainable, and production-ready applications through automated testing at multiple levels.

Testing should verify application behavior rather than implementation details.

---

## Core Principle

Test behavior.

Not implementation.

Tests should give confidence that the application works correctly from a user's perspective.

---

## Testing Goals

Every project should strive for:

- reliable releases;
- regression prevention;
- maintainable test suites;
- fast feedback;
- deterministic results;
- high developer confidence.

Testing is a quality assurance tool, not a coverage competition.

---

## Testing Pyramid

Prefer the following balance.

```
                E2E

          Integration

        Component Tests

          Unit Tests
```

Use each level for the problems it solves best.

---

## Test Types

A production application may contain:

- unit tests;
- component tests;
- integration tests;
- end-to-end tests;
- accessibility tests;
- visual regression tests;
- performance tests.

Not every project requires every test type.

---

## Recommended Tooling

For the App Router, use two complementary tools:

- **Vitest** (or Jest) with **React Testing Library** for unit and Client Component tests;
- **Playwright** for end-to-end and async Server Component coverage.

Next.js does not yet support async Server Components inside unit-test runners. Cover those with Playwright instead.

A minimal Vitest setup:

```ts
// vitest.config.ts
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import tsconfigPaths from "vite-tsconfig-paths";

export default defineConfig({
    plugins: [tsconfigPaths(), react()],
    test: {
        environment: "jsdom",
        setupFiles: ["./vitest.setup.ts"],
        globals: true,
    },
});
```

```ts
// vitest.setup.ts
import "@testing-library/jest-dom/vitest";
```

Keep the runner configuration in version control so CI and local runs behave identically.

---

## Unit Tests

Unit tests verify isolated logic.

Typical candidates include:

- utility functions;
- validation;
- formatting;
- business rules;
- custom hooks.

Unit tests should execute quickly and independently.

Extract pure logic out of components and route handlers so it can be tested without a runtime:

```ts
// src/lib/money.test.ts
import { describe, it, expect } from "vitest";
import { formatPrice } from "./money";

describe("formatPrice", () => {
    it("formats cents as USD", () => {
        expect(formatPrice(1999)).toBe("$19.99");
    });

    it("rejects negative amounts", () => {
        expect(() => formatPrice(-1)).toThrow();
    });
});
```

---

## Component Tests

Component tests verify UI behavior.

Review:

- rendering;
- user interactions;
- state changes;
- conditional rendering;
- accessibility.

Test components through their public interface.

---

## Integration Tests

Integration tests verify collaboration between multiple modules.

Examples:

- forms;
- authentication flow;
- database interaction;
- API communication;
- feature workflows.

Integration tests should reflect realistic application behavior.

---

## End-to-End Tests

End-to-end tests verify complete user journeys.

Typical scenarios:

- login;
- registration;
- checkout;
- search;
- profile updates.

Test the application as users experience it.

Playwright drives a real browser against a running build, which makes it the correct tool for async Server Components, streaming, and navigation:

```ts
// e2e/cart.spec.ts
import { test, expect } from "@playwright/test";

test("a shopper can add an item to the cart", async ({ page }) => {
    await page.goto("/products/widget");

    await page.getByRole("button", { name: /add to cart/i }).click();
    await expect(page.getByRole("status")).toHaveText(/added to cart/i);

    await page.goto("/cart");
    await expect(page.getByRole("listitem")).toContainText("Widget");
});
```

Configure `webServer` in `playwright.config.ts` to build and start the app so E2E runs against production output, not the dev server.

---

## Server Components

Server Components should be tested by verifying:

- rendered output;
- data loading;
- error handling;
- authorization behavior.

Avoid testing framework internals.

Async Server Components are not supported by jsdom-based unit runners, because their `async` render must run inside the Next.js server. Do not try to force them through Testing Library.

Bad example:

```tsx
// ❌ Async Server Components cannot be rendered this way.
// React Testing Library does not await the component's promise.
import { render } from "@testing-library/react";
import ProductPage from "@/app/products/[id]/page";

render(await ProductPage({ params: Promise.resolve({ id: "1" }) }));
```

Instead, extract the data loading into a plain async function, unit-test that in isolation, and verify the rendered page with an end-to-end test.

Good example:

```ts
// src/lib/products.ts — pure, directly testable
export async function getProduct(id: string) {
    const res = await fetch(`${process.env.API_URL}/products/${id}`, {
        // Next 15 leaves fetch uncached by default; opt in when data can go stale.
        next: { revalidate: 60 },
    });
    if (!res.ok) throw new Error("Product not found");
    return res.json();
}
```

```tsx
// src/app/products/[id]/page.tsx — thin wrapper, covered by Playwright
import { getProduct } from "@/lib/products";

export default async function ProductPage({
    params,
}: {
    params: Promise<{ id: string }>;
}) {
    const { id } = await params;
    const product = await getProduct(id);
    return <h1>{product.name}</h1>;
}
```

Note that in the App Router `params` (and `searchParams`) are Promises and must be awaited.

---

## Client Components

Review:

- interactions;
- local state;
- events;
- accessibility;
- loading states.

Focus on observable behavior.

Render the Client Component and drive it through the accessible interface, never through internal state:

```tsx
// src/components/counter.test.tsx
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Counter } from "./counter";

describe("<Counter />", () => {
    it("increments when the button is pressed", async () => {
        const user = userEvent.setup();
        render(<Counter />);

        await user.click(screen.getByRole("button", { name: /increment/i }));

        expect(screen.getByText("Count: 1")).toBeInTheDocument();
    });
});
```

Query by role and accessible name rather than by test ids or class names — that keeps the test tied to what the user actually experiences.

---

## Server Actions

Verify:

- validation;
- authorization;
- database mutations;
- error handling;
- cache invalidation.

Server Actions should remain independently testable.

A Server Action is an ordinary async function, so it can be imported and called directly. Mock the framework helpers it depends on (`next/cache`, `next/navigation`) and the data layer:

```ts
// src/app/products/actions.test.ts
import { describe, it, expect, vi, beforeEach } from "vitest";
import { revalidatePath } from "next/cache";
import { createProduct } from "./actions";
import { db } from "@/lib/db";

vi.mock("next/cache", () => ({ revalidatePath: vi.fn() }));
vi.mock("@/lib/db", () => ({
    db: { product: { create: vi.fn() } },
}));

beforeEach(() => vi.clearAllMocks());

describe("createProduct", () => {
    it("rejects a blank name without writing to the database", async () => {
        const form = new FormData();
        form.set("name", "");

        await expect(createProduct(form)).resolves.toEqual({
            error: "Name is required",
        });
        expect(db.product.create).not.toHaveBeenCalled();
    });

    it("creates the product and revalidates the listing", async () => {
        const form = new FormData();
        form.set("name", "Widget");

        await createProduct(form);

        expect(db.product.create).toHaveBeenCalledWith({
            data: { name: "Widget" },
        });
        expect(revalidatePath).toHaveBeenCalledWith("/products");
    });
});
```

Assert that authorization and validation run *before* any mutation — the denial path is the most important one to cover.

---

## API Routes

Every API endpoint should verify:

- request validation;
- authentication;
- authorization;
- response structure;
- HTTP status codes;
- error handling.

API tests should remain deterministic.

Route handlers in `app/**/route.ts` export functions named for the HTTP method. Import the handler and invoke it with a `NextRequest`, then assert on the returned `Response`:

```ts
// src/app/api/products/route.ts
import { NextRequest, NextResponse } from "next/server";
import { listProducts } from "@/lib/products";

export async function GET(request: NextRequest) {
    const limit = Number(request.nextUrl.searchParams.get("limit") ?? "20");

    if (!Number.isInteger(limit) || limit < 1 || limit > 100) {
        return NextResponse.json({ error: "invalid limit" }, { status: 400 });
    }

    return NextResponse.json({ products: await listProducts(limit) });
}
```

```ts
// src/app/api/products/route.test.ts
import { describe, it, expect, vi } from "vitest";
import { NextRequest } from "next/server";
import { GET } from "./route";

vi.mock("@/lib/products", () => ({
    listProducts: vi.fn(async (n: number) =>
        Array.from({ length: n }, (_, i) => ({ id: i + 1 })),
    ),
}));

describe("GET /api/products", () => {
    it("returns 400 for an out-of-range limit", async () => {
        const res = await GET(
            new NextRequest("http://localhost/api/products?limit=999"),
        );
        expect(res.status).toBe(400);
    });

    it("returns products for a valid limit", async () => {
        const res = await GET(
            new NextRequest("http://localhost/api/products?limit=2"),
        );
        expect(res.status).toBe(200);
        await expect(res.json()).resolves.toEqual({
            products: [{ id: 1 }, { id: 2 }],
        });
    });
});
```

Cover both the success and the rejection status codes for every handler.

---

## Mocking

Mock only external dependencies.

Examples:

- payment providers;
- email services;
- cloud storage;
- external APIs.

Avoid mocking application logic unnecessarily.

Prefer intercepting the network at the boundary with **MSW** rather than replacing your own `fetch` wrappers, so the code under test runs unchanged:

```ts
// vitest.setup.ts (MSW extension)
import { setupServer } from "msw/node";
import { http, HttpResponse } from "msw";
import { afterAll, afterEach, beforeAll } from "vitest";

const server = setupServer(
    http.get("https://api.example.com/products/:id", ({ params }) =>
        HttpResponse.json({ id: params.id, name: "Widget" }),
    ),
);

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

Setting `onUnhandledRequest: "error"` surfaces any real network call the tests forgot to stub.

---

## Test Data

Use predictable test data.

Test data should be:

- isolated;
- repeatable;
- easy to understand.

Avoid shared mutable test state.

---

## Accessibility Testing

Verify:

- keyboard navigation;
- semantic HTML;
- form labels;
- focus management;
- ARIA usage.

Accessibility should be tested continuously.

Run automated axe checks inside the Playwright suite so regressions fail CI:

```ts
// e2e/a11y.spec.ts
import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test("the home page has no detectable accessibility violations", async ({
    page,
}) => {
    await page.goto("/");

    const results = await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa"])
        .analyze();

    expect(results.violations).toEqual([]);
});
```

Automated scans catch only a fraction of issues; keep manual keyboard and screen-reader checks in the review process.

---

## Performance Testing

Review:

- rendering speed;
- page load time;
- API latency;
- Core Web Vitals.

Performance regressions should be identified before release.

---

## Test Organization

Organize tests consistently.

Example:

```
src/

    features/

        products/

            ProductCard.tsx

            ProductCard.test.tsx

            ProductCard.integration.test.tsx
```

Keep tests close to the code they verify whenever practical.

---

## Continuous Integration

Run automated tests during CI.

Recommended sequence:

```
Lint

↓

Type Check

↓

Unit Tests

↓

Integration Tests

↓

Build

↓

E2E Tests

↓

Deploy
```

Deployment should depend on successful verification.

---

## Error Handling

Tests should verify:

- expected failures;
- invalid input;
- authorization denial;
- unavailable services.

Failure scenarios are as important as successful ones.

---

## Security

Verify:

- authentication;
- authorization;
- protected routes;
- input validation.

Security-sensitive behavior should always be tested.

---

## AI Execution Checklist

## Investigation

☐ Identify feature behavior.

☐ Identify critical workflows.

☐ Review edge cases.

☐ Review security requirements.

---

## Planning

☐ Select appropriate test type.

☐ Isolate external dependencies.

☐ Use deterministic data.

☐ Verify expected behavior.

---

## Verification

☐ Critical paths covered.

☐ Error cases tested.

☐ Accessibility verified.

☐ Security verified.

☐ Tests deterministic.

☐ CI integration complete.

---

## Examples

**Good Example** — Server Components tested end to end, client logic tested in isolation

```ts
// e2e/checkout.spec.ts — Playwright drives the real app, including Server Actions.
import { test, expect } from '@playwright/test';

test('a signed-in user can cancel a pending order', async ({ page }) => {
  await page.goto('/orders/ord_123');

  await page.getByRole('button', { name: 'Cancel order' }).click();

  // Asserts what the user observes, not which function ran.
  await expect(page.getByRole('status')).toHaveText('Order cancelled');
  await expect(page.getByRole('button', { name: 'Cancel order' })).toBeHidden();
});
```

```tsx
// Client Components are unit-tested with Testing Library, queried by role.
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

test('the search box pushes the query to the URL', async () => {
  const user = userEvent.setup();
  const push = vi.fn();
  vi.mocked(useRouter).mockReturnValue({ push } as never);

  render(<SearchBox initialQuery="" />);
  await user.type(screen.getByRole('textbox'), 'lamps{Enter}');

  expect(push).toHaveBeenCalledWith('/search?q=lamps');
});
```

```ts
// Pure server functions are tested directly — no HTTP, no rendering.
test('cancelOrder refuses an order owned by someone else', async () => {
  const result = await cancelOrderFor('user-b', 'order-owned-by-user-a');
  expect(result).toEqual({ ok: false, error: 'This order can no longer be cancelled' });
});
```

**Bad Example** — rendering async Server Components in jsdom, asserting implementation

```tsx
// An async Server Component is not a React function component jsdom can render:
// it returns a Promise, so this either throws or silently asserts on nothing.
test('dashboard shows stats', async () => {
  render(<DashboardPage />);
  expect(await screen.findByText('Paid orders')).toBeInTheDocument();
});

test('search calls the API', async () => {
  render(<SearchBox initialQuery="" />);
  await userEvent.type(screen.getByTestId('search-input'), 'lamps');

  // Selecting by test id proves nothing about the accessible name, and asserting
  // the fetch URL couples the test to the transport rather than the behaviour.
  expect(fetchSpy).toHaveBeenCalledWith('/api/search?q=lamps');
});
```

---

## Common Mistakes

Avoid:

Testing implementation details.

Writing brittle tests.

Mocking everything.

Ignoring failure scenarios.

Sharing mutable test data.

Relying on test execution order.

Skipping accessibility tests.

Treating code coverage as the primary objective.

---

## Completion Criteria

A testing strategy is complete when:

- critical workflows are covered;
- behavior is verified at the appropriate testing level;
- failure scenarios are tested;
- security and accessibility are validated;
- tests run reliably in CI;
- developers can refactor with confidence.

---

## Summary

Testing is an essential part of building reliable Next.js applications.

By focusing on observable behavior, selecting the appropriate testing strategy, automating verification, and continuously validating accessibility, security, and critical user workflows, teams can deliver production-ready applications with greater confidence.

## Related

- `knowledge/nextjs/06-server-components.md`
- `knowledge/testing/04-e2e-testing.md`
- `knowledge/react/21-testing.md`
