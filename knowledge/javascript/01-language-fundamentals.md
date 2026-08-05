---
id: javascript/01-language-fundamentals
topic: javascript
slug: language-fundamentals
title: "JavaScript Language Fundamentals"
type: doc
order: 1
status: ready
tags: [javascript, language-fundamentals]
related: [javascript/00-overview, javascript/02-execution-context, javascript/03-scope-and-closures, javascript/05-objects-and-prototypes, javascript/14-error-handling]
when_to_use: "Read before writing or reviewing any code that compares, coerces, or defaults values."
---
# JavaScript Language Fundamentals

## Purpose

This document defines JavaScript's value system: the primitive and object types, how
values convert between types (coercion), how equality and truthiness work, and how
`null` and `undefined` differ. It exists so an agent can predict what an expression
evaluates to without running it, and never ship a bug caused by an unexpected coercion.

## Why It Matters

JavaScript is dynamically typed and coerces aggressively. `[] + []` is `""`, `"" == 0`
is `true`, and `typeof null` is `"object"`. These are not bugs in the language — they are
specified rules. Code that ignores them fails on the exact inputs users produce: an empty
string, a `0` quantity, a missing field that is `undefined` instead of `null`. Getting
values right is the cheapest possible bug prevention, because every other layer of the
program manipulates these values.

## Core Principles

- **There are seven primitives plus objects.** `string`, `number`, `bigint`, `boolean`,
  `undefined`, `symbol`, `null`; everything else (arrays, functions, dates) is an object.
- **Primitives are immutable and compared by value; objects are compared by reference.**
  Two distinct objects with identical contents are never `===`.
- **Coercion is implicit type conversion.** Operators and comparisons convert operands by
  fixed rules. Know the rules or make conversion explicit.
- **`===` never coerces; `==` does.** Prefer `===` so equality means what it reads.
- **`null` is intentional absence; `undefined` is uninitialized absence.** They are
  distinct values with distinct meanings.

## Best Practices

- Always compare with `===` / `!==`. The one defensible use of `==` is `x == null` to
  test for `null` *or* `undefined` in a single check — comment it when you use it.
- Convert types explicitly: `Number(x)`, `String(x)`, `Boolean(x)`. Explicit conversion
  documents intent and avoids surprise coercions.
- Guard against falsy-but-valid values. `if (count)` is wrong when `0` is valid; use
  `if (count != null)` or `if (count !== undefined)`.
- Use `Number.isNaN(x)` and `Number.isInteger(x)`, not the global `isNaN` (which coerces)
  or `x === NaN` (always false, because `NaN !== NaN`).
- Use nullish coalescing `??` for defaults so `0` and `""` survive; use `||` only when any
  falsy value should trigger the default.
- Use `Array.isArray(x)` to detect arrays; `typeof [] === "object"`.

## Examples

**Good Example** — explicit conversion, nullish default, safe equality

```js
function priceLabel(input) {
  const price = Number(input);              // explicit: "" -> 0, "abc" -> NaN
  if (Number.isNaN(price)) {                // correct NaN test, not price === NaN
    throw new TypeError("price must be numeric");
  }
  // ?? keeps a valid 0; || would wrongly replace 0 with "Free"
  const currency = config.currency ?? "USD";
  return price === 0 ? "Free" : `${currency} ${price}`; // === never coerces
}
```

**Bad Example** — implicit coercion and falsy traps

```js
function priceLabel(input) {
  if (input == 0) return "Free";   // "" == 0 is true, "0.00" == 0 is true → false positives
  const currency = config.currency || "USD"; // a valid currency "" becomes "USD"
  if (input == NaN) return "?";    // ALWAYS false; NaN is never == to anything
  return currency + " " + input;   // string concatenation, not numeric formatting
}
```

## Common Mistakes

- Using `==` and being surprised by `0 == ""`, `null == undefined`, or `[] == false`.
- Treating `0`, `""`, or `false` as "missing" in a truthiness check when they are valid.
- Comparing objects or arrays with `===` and expecting structural equality.
- `typeof null === "object"` — testing for objects without excluding `null`.
- Using `x === NaN` (never true) or global `isNaN("")` (coerces `""` to `0`, returns
  false) instead of `Number.isNaN`.
- Mutating a primitive by assignment and expecting the original variable to change —
  primitives are copied by value.

## Production Tips

- Enable TypeScript or JSDoc types in CI; most coercion bugs become compile errors.
- In tests, cover the falsy-but-valid inputs explicitly: `0`, `""`, `false`, `null`,
  `undefined`, `NaN`. These are the values that break naive checks.

## AI Review Checklist

- Are all equality checks `===`/`!==`, except a deliberate, commented `== null`?
- Do defaults use `??` where `0`/`""`/`false` are valid values?
- Are type conversions explicit (`Number`, `String`, `Boolean`) rather than implicit?
- Is `NaN` tested with `Number.isNaN` and arrays with `Array.isArray`?
- Is object/array equality done by content (not `===`) where structural equality is meant?

## Related

- `knowledge/javascript/00-overview.md`
- `knowledge/javascript/02-execution-context.md`
- `knowledge/javascript/03-scope-and-closures.md`
- `knowledge/javascript/05-objects-and-prototypes.md`
- `knowledge/javascript/14-error-handling.md`
