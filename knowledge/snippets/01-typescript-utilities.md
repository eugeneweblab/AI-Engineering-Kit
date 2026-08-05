---
id: snippets/01-typescript-utilities
topic: snippets
slug: typescript-utilities
title: "TypeScript Utilities"
type: doc
order: 1
status: ready
tags: [snippets, typescript-utilities, clearTimeout, required, isError, assertNever, setTimeout, TypeError]
related: [snippets/02-php-wordpress, typescript/09-utility-types, javascript/08-asynchronous-javascript, react/09-custom-hooks, snippets/03-shell-scripts]
when_to_use: "Copy when you need money formatting, async control flow, or type-narrowing helpers."
---
# TypeScript Utilities

## Money

Store money as integers in the currency's minor unit. Floating point cannot represent `0.1`
exactly, and the error compounds across a cart.

```ts
/** Amounts are integers in the currency's minor unit (cents, pence, yen). */
export type Money = { readonly amountMinor: number; readonly currency: string };

export const money = (amountMinor: number, currency: string): Money => {
  if (!Number.isInteger(amountMinor)) {
    throw new TypeError(`Money must be an integer minor unit, received ${amountMinor}`);
  }
  return { amountMinor, currency };
};

export function formatMoney(value: Money, locale = 'en-US'): string {
  const formatter = new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: value.currency,
  });

  // resolvedOptions() reports the currency's real exponent: 2 for USD, 0 for JPY,
  // 3 for KWD. Dividing by a hardcoded 100 is wrong for a third of the world.
  const exponent = formatter.resolvedOptions().maximumFractionDigits ?? 2;
  return formatter.format(value.amountMinor / 10 ** exponent);
}

/** Split an amount without losing or inventing minor units. */
export function allocate(value: Money, ratios: number[]): Money[] {
  const total = ratios.reduce((sum, r) => sum + r, 0);
  const shares = ratios.map((r) => Math.floor((value.amountMinor * r) / total));

  // Distribute the rounding remainder one unit at a time, so the parts sum to the whole.
  let remainder = value.amountMinor - shares.reduce((sum, s) => sum + s, 0);
  for (let i = 0; remainder > 0; i = (i + 1) % shares.length, remainder--) {
    shares[i] += 1;
  }

  return shares.map((amount) => money(amount, value.currency));
}
```

---

## Async Control

```ts
/** Reject if a promise takes too long, without leaving the timer running. */
export async function withTimeout<T>(promise: Promise<T>, ms: number): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), ms);

  try {
    return await Promise.race([
      promise,
      new Promise<never>((_, reject) => {
        controller.signal.addEventListener('abort', () =>
          reject(new Error(`Timed out after ${ms}ms`)),
        );
      }),
    ]);
  } finally {
    clearTimeout(timer); // without this, the process stays alive until the timer fires
  }
}
```

```ts
/** Retry with exponential backoff and jitter. Retries only what is worth retrying. */
export async function retry<T>(
  fn: () => Promise<T>,
  { attempts = 3, baseMs = 200, isRetryable = () => true } = {},
): Promise<T> {
  let lastError: unknown;

  for (let attempt = 0; attempt < attempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      if (!isRetryable(error) || attempt === attempts - 1) throw error;

      // Jitter prevents a thundering herd when many clients fail simultaneously.
      const delay = baseMs * 2 ** attempt + Math.random() * baseMs;
      await new Promise((resolve) => setTimeout(resolve, delay));
    }
  }

  throw lastError;
}

// Retry transport failures and 5xx; never retry a 400 — it will fail identically.
await retry(() => fetch(url), {
  isRetryable: (e) => e instanceof TypeError || (e as { status?: number }).status! >= 500,
});
```

```ts
/** Run tasks with bounded concurrency, preserving input order in the results. */
export async function mapWithConcurrency<T, R>(
  items: readonly T[],
  limit: number,
  fn: (item: T, index: number) => Promise<R>,
): Promise<R[]> {
  const results = new Array<R>(items.length);
  let cursor = 0;

  const workers = Array.from({ length: Math.min(limit, items.length) }, async () => {
    while (cursor < items.length) {
      const index = cursor++;
      results[index] = await fn(items[index], index);
    }
  });

  await Promise.all(workers);
  return results;
}
```

---

## Type Guards

```ts
/** Narrow unknown errors without asserting. `catch` gives you `unknown`, not `Error`. */
export function isError(value: unknown): value is Error {
  return value instanceof Error;
}

export function errorMessage(value: unknown): string {
  if (isError(value)) return value.message;
  if (typeof value === 'string') return value;
  return 'Unknown error';
}

/** Filter out null and undefined while telling the compiler about it. */
export const isPresent = <T>(value: T | null | undefined): value is T => value != null;

const names = [' ada', null, 'grace'].filter(isPresent).map((n) => n.trim());
```

```ts
/** Exhaustiveness check: adding a variant becomes a compile error, not a silent fallthrough. */
export function assertNever(value: never): never {
  throw new Error(`Unhandled variant: ${JSON.stringify(value)}`);
}

type Status = 'pending' | 'paid' | 'refunded';

function label(status: Status): string {
  switch (status) {
    case 'pending': return 'Awaiting payment';
    case 'paid': return 'Paid';
    case 'refunded': return 'Refunded';
    default: return assertNever(status);
  }
}
```

---

## Debounce with Cleanup

```ts
export function debounce<A extends unknown[]>(fn: (...args: A) => void, ms: number) {
  let timer: ReturnType<typeof setTimeout> | undefined;

  const debounced = (...args: A) => {
    if (timer) clearTimeout(timer);
    timer = setTimeout(() => fn(...args), ms);
  };

  // Cancellation is what makes this safe in a component: without it, a pending
  // callback fires after unmount and writes to state that no longer exists.
  debounced.cancel = () => {
    if (timer) clearTimeout(timer);
    timer = undefined;
  };

  return debounced;
}
```

---

## Environment Validation

```ts
/** Fail at startup with the name of the missing variable, not at first use with `undefined`. */
function required(name: string): string {
  const value = process.env[name];
  if (!value) throw new Error(`Missing required environment variable: ${name}`);
  return value;
}

export const env = {
  databaseUrl: required('DATABASE_URL'),
  stripeSecretKey: required('STRIPE_SECRET_KEY'),
  logLevel: process.env.LOG_LEVEL ?? 'info',
} as const;
```

---

## Examples

**Good Example** — a snippet adapted to the codebase it lands in

```ts
// Pasted, then adapted: the project's Result type, its error codes, and its
// logger — not the generic version from the snippet.
import { type Result, ok, err } from '@/lib/result';

export function parseMoney(input: string): Result<number, 'INVALID_AMOUNT'> {
  const cents = Math.round(Number(input.replace(/[^0-9.-]/g, '')) * 100);

  if (!Number.isFinite(cents) || !Number.isSafeInteger(cents)) {
    return err('INVALID_AMOUNT');
  }

  return ok(cents);   // integer cents, as the codebase requires everywhere
}
```

**Bad Example** — pasted as-is, next to something that already exists

```ts
// A second formatter, three directories from src/lib/format.ts, disagreeing
// with it: this one takes a float, rounds differently, and hardcodes the locale
// the rest of the app reads from the user.
export function formatPrice(price: number): string {
  return '£' + price.toFixed(2);
}

// Copied from a snippet without reading it: `any` in a strict codebase, and a
// silent catch that turns a parse failure into 0.
export function parseAmount(input: any): number {
  try {
    return parseFloat(input);
  } catch {
    return 0;
  }
}
```

Prices now differ by a penny between screens — a defect that surfaces in accounting rather
than in tests.

---

## Related

- `knowledge/snippets/02-php-wordpress.md`
- `knowledge/typescript/09-utility-types.md`
- `knowledge/javascript/08-asynchronous-javascript.md`
- `knowledge/react/09-custom-hooks.md`
- `knowledge/snippets/03-shell-scripts.md`
