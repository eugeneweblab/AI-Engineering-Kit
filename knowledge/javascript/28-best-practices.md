---
id: javascript/28-best-practices
topic: javascript
slug: best-practices
title: "Best Practices"
type: doc
order: 28
status: ready
tags: [javascript, best-practices]
related: [javascript/23-clean-code, javascript/14-error-handling, javascript/01-language-fundamentals, javascript/17-es6-features, javascript/26-security]
when_to_use: "Read before writing everyday JavaScript, or when reviewing a PR for baseline code quality."
---
# Best Practices

## Purpose

This document collects the baseline habits that make everyday JavaScript correct,
readable, and safe from the language's well-known footguns: declarations, equality,
async control flow, immutability, and defensive access. It is the general-quality
companion to the deeper topic docs — it does not replace [clean code](23-clean-code.md)
or [error handling](14-error-handling.md), it enforces the non-negotiables an agent
should apply to every file.

## Why It Matters

JavaScript is permissive: it coerces types, hoists silently, swallows unhandled
rejections, and lets `var` leak across scopes. Code that ignores these traps runs today
and breaks mysteriously tomorrow — a `==` comparison that coerces `"0"` to `false`, a
mutated shared array that corrupts state three modules away, a forgotten `await` that
returns a Promise where a value was expected. Consistent, disciplined defaults remove a
whole category of bugs before they are written, which is far cheaper than debugging them
in production.

## Core Principles

- **Prefer `const`, then `let`; never `var`.** `const` signals intent and blocks
  reassignment; `var`'s function scoping and hoisting cause leaks and shadowing bugs.
- **Use `===`, never `==`.** Loose equality applies surprising coercion rules. Strict
  equality is predictable; the cost of `==` is a bug you cannot see in review.
- **Prefer immutability.** Treat inputs as read-only; return new values instead of
  mutating. Shared mutable state is the source of the hardest bugs.
- **Handle every async path.** Every Promise needs an `await` and a rejection path.
  Unhandled rejections crash Node and vanish in the browser.
- **Fail fast and explicitly.** Validate at boundaries, throw meaningful errors, and let
  them propagate — do not silently swallow.

## Best Practices

- Enable **strict mode** (native in ES modules) and lint with ESLint + a formatter
  (Prettier/Biome); make CI enforce both.
- Access possibly-missing values with optional chaining (`a?.b?.c`) and provide defaults
  with nullish coalescing (`?? fallback`) — not `||`, which also swallows `0`, `""`, and `false`.
- Use array/object methods (`map`, `filter`, `reduce`, destructuring, spread) over manual
  index loops when they read more clearly — but reach for a plain loop in hot paths.
- Keep functions small and single-purpose; return early instead of deep nesting.
- Name things for intent: `isActive`, `retryCount` — not `flag`, `tmp`, `data2`.
- Avoid `null`/`undefined` ambiguity: pick one convention (prefer `undefined` for "absent")
  and validate inputs at the edge.
- Prefer `async`/`await` over `.then()` chains for readability; use `Promise.all` for
  concurrency.
- Do not extend built-in prototypes or rely on implicit global state.

## Examples

**Good Example** — const, strict equality, safe access, immutable update

```js
const applyDiscount = (order, rate) => {
  if (rate < 0 || rate > 1) throw new RangeError("rate must be between 0 and 1"); // fail fast

  // Nullish coalescing: falls back only for null/undefined, so a real 0 tax survives.
  const tax = order.tax ?? 0;

  // Return a new object; the caller's order is never mutated.
  return { ...order, total: order.subtotal * (1 - rate) + tax };
};

const email = user?.contact?.email ?? "unknown"; // safe deep access with a default
```

**Bad Example** — var leak, loose equality, `||` default, mutation

```js
function applyDiscount(order, rate) {
  var tax = order.tax || 0;        // || turns a valid tax of 0... into 0 by luck, but 0 is falsy → masks real values
  if (rate == "0") return order;   // == coerces "0"; also compares number to string surprisingly
  order.total = order.subtotal;    // mutates the caller's object → spooky action at a distance
  return order;
}
const email = user.contact.email;  // throws if contact is undefined
```

## Common Mistakes

- Using `var`, or `let` where `const` would express intent.
- `==`/`!=` instead of `===`/`!==`, inviting coercion bugs.
- `|| default` where `0`, `""`, or `false` are valid values — use `??`.
- Mutating function arguments or shared arrays/objects.
- Forgetting `await`, so a Promise leaks where a value was expected.
- Swallowing errors (`catch {}`) instead of handling or rethrowing.
- Deep property access without optional chaining, throwing on missing data.
- Vague names (`data`, `tmp`, `flag`) that hide meaning.

## Production Tips

- Turn on `"strict": true` in `tsconfig` (or run `// @ts-check` on JS) to catch nullability
  and type mistakes before runtime.
- Make the linter fail the build, not just warn — warnings that never block get ignored.
- Add a `no-floating-promises` lint rule so un-awaited Promises are caught mechanically.

## AI Review Checklist

- Are all declarations `const`/`let` with no `var`?
- Is equality strict (`===`/`!==`) everywhere?
- Are defaults written with `??` where `0`/`""`/`false` are valid inputs?
- Are function inputs and shared state treated as immutable?
- Is every Promise awaited with a rejection path (no floating promises)?
- Is deep access guarded with optional chaining?
- Do names express intent, and do errors propagate rather than get swallowed?

## Related

- `knowledge/javascript/23-clean-code.md`
- `knowledge/javascript/14-error-handling.md`
- `knowledge/javascript/01-language-fundamentals.md`
- `knowledge/javascript/17-es6-features.md`
- `knowledge/javascript/26-security.md`
