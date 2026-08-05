---
id: javascript/04-functions
topic: javascript
slug: functions
title: "JavaScript Functions"
type: doc
order: 4
status: ready
tags: [javascript, functions]
related: [javascript/00-overview, javascript/02-execution-context, javascript/03-scope-and-closures, javascript/16-this-keyword, javascript/21-functional-programming]
when_to_use: "Read before defining functions, choosing arrow vs. regular, or writing higher-order callbacks."
---
# JavaScript Functions

## Purpose

This document covers how to define and use functions in JavaScript: declarations,
expressions, and arrow functions; parameters (defaults, rest, destructuring); return
behavior; and higher-order functions. It helps an agent choose the right function form —
a choice that changes `this` binding, hoisting, and readability, not just syntax.

## Why It Matters

Functions are JavaScript's primary unit of behavior and its main abstraction tool. The
form you choose has semantic consequences: arrow functions inherit `this` and have no
`arguments`, while regular functions get `this` from the call site and can be constructors.
Picking the wrong form causes real bugs — a lost `this` in a callback, a broken method,
an arrow used as a constructor throwing `TypeError`. Because callbacks pass functions
across boundaries constantly, these binding rules apply everywhere.

## Core Principles

- **Declaration vs. expression vs. arrow are different, not interchangeable.**
  Declarations hoist with their body; expressions and arrows do not; arrows also change
  `this`.
- **Arrow functions have no own `this`, `arguments`, or `prototype`.** They inherit `this`
  lexically and cannot be `new`-ed. Use them for callbacks that should keep the outer
  `this`.
- **Regular functions get `this` from the call site.** As a method, `this` is the object;
  detached, `this` is `undefined` (strict) or the global object.
- **Functions are values.** They can be passed, returned, and stored — the basis of
  higher-order functions like `map`, `filter`, and `reduce`.
- **Prefer pure functions.** Same input, same output, no side effects; they are trivially
  testable and safe to reuse.

## Best Practices

- Use arrow functions for inline callbacks and when you need to preserve the surrounding
  `this` (e.g., inside a class method's `.map`). Use regular functions or methods when the
  call site should supply `this`.
- Default parameters over in-body `x = x || default`; defaults only trigger on
  `undefined`, so a valid `0` or `""` survives.
- Use rest parameters `(...args)` instead of the legacy `arguments` object — rest is a
  real array and works in arrows.
- Keep functions small and single-purpose; a function that does one thing is easier to
  name, test, and reuse.
- Prefer returning values over mutating arguments; mutation-by-side-effect is hard to
  trace. If you must mutate, make it obvious in the name.
- Do not rely on a function *expression* being hoisted — it is not callable before its
  line (TDZ / `undefined`).

## Examples

**Good Example** — arrow preserves `this`, defaults handle absence

```js
class Cart {
  constructor() { this.items = []; }

  // Regular method: `this` is the Cart instance at the call site.
  totalWith(taxRate = 0) {           // default only applies when arg is undefined
    // Arrow callback inherits `this` from totalWith, so `this.items` is correct.
    const subtotal = this.items.reduce((sum, i) => sum + i.price, 0);
    return subtotal * (1 + taxRate);
  }
}
```

**Bad Example** — wrong function forms lose `this` and misuse defaults

```js
class Cart {
  constructor() { this.items = []; }

  total(taxRate) {
    taxRate = taxRate || 0.2;   // a valid 0 becomes 0.2 — wrong tax
    // Regular function callback: `this` is undefined here, so this.items throws.
    return this.items.reduce(function (sum, i) {
      return sum + i.price;
    }, 0) * (1 + taxRate);
  }
}
const t = new Cart().total; // detached method: `this` is lost when called as t()
```

## Common Mistakes

- Using a regular `function` as an array-method callback inside a method and losing
  `this`; use an arrow or bind.
- Using an arrow function as a method or constructor — it has no own `this` and cannot be
  `new`-ed.
- Defaulting with `||`, which replaces valid falsy arguments; use parameter defaults or
  `??`.
- Reaching for `arguments` in code that should use rest parameters (and which fails in
  arrow functions).
- Passing an object method as a callback (`arr.forEach(obj.handle)`) without binding, so
  `this` inside `handle` is wrong.

## Production Tips

- When passing a method as a callback, bind it once (`this.handle = this.handle.bind(this)`
  or define it as a class field arrow) rather than binding on every render/call.
- Name functions even when assigned to a variable; named functions produce readable stack
  traces in production error reports.

## AI Review Checklist

- Is each function's form (declaration / expression / arrow) chosen for its `this` and
  hoisting behavior, not by habit?
- Are arrow functions used for callbacks that must retain the outer `this`, and avoided
  for methods and constructors?
- Do optional parameters use default parameters or `??`, so valid falsy values survive?
- Are rest parameters used instead of `arguments`?
- Are methods passed as callbacks bound so `this` is preserved?

## Related

- `knowledge/javascript/00-overview.md`
- `knowledge/javascript/02-execution-context.md`
- `knowledge/javascript/03-scope-and-closures.md`
- `knowledge/javascript/16-this-keyword.md`
- `knowledge/javascript/21-functional-programming.md`
