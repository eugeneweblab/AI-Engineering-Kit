---
id: javascript/17-es6-features
topic: javascript
slug: es6-features
title: "Es6 Features"
type: doc
order: 17
status: ready
tags: [javascript, es6-features]
related: [javascript/01-language-fundamentals, javascript/04-functions, javascript/07-modules, javascript/16-this-keyword, javascript/23-clean-code]
when_to_use: "Read before writing modern JavaScript syntax — destructuring, spread, template literals, let/const, default params, arrows."
---
# Es6 Features

## Purpose

This document defines the modern JavaScript features introduced in ES2015 (ES6) and
maintained since — `let`/`const`, arrow functions, destructuring, spread/rest, template
literals, default parameters, and modules — and the correctness traps hidden inside their
convenience. It is written so an agent uses these features idiomatically without hitting
their sharp edges.

## Why It Matters

ES6 syntax is universally supported and is the default style of all modern JavaScript, so
an agent must both read and write it fluently. But several features have subtle semantics
that cause real bugs: spread copies only one level deep (a shallow copy that shares nested
references), destructuring defaults only fire on `undefined` (not `null`), and `const`
prevents reassignment but not mutation. Code that misunderstands these looks correct and
passes casual review, then corrupts shared state or misapplies a fallback in production.
Fluency means knowing the edge, not just the happy path.

## Core Principles

- **`const` by default, `let` when reassigning; never `var`.** `const`/`let` are
  block-scoped and not hoisted into usable form (temporal dead zone). `var` is
  function-scoped and leaks, causing classic loop-closure bugs.
- **`const` freezes the binding, not the value.** A `const` object can still be mutated;
  use `Object.freeze` (shallow) or immutable patterns for true immutability.
- **Spread and `Object.assign` are shallow.** They copy top-level properties; nested
  objects/arrays are shared by reference. Mutating a nested field mutates the "copy" too.
- **Destructuring defaults apply only to `undefined`.** A property that is `null`, `0`,
  `""`, or `false` does *not* trigger its default. Same rule for default parameters.
- **Arrow functions capture `this` lexically and have no `arguments`.** Great for
  callbacks, wrong for methods and constructors (see the `this` document).

## Best Practices

- Declare with `const`; switch to `let` only where a variable is genuinely reassigned. Let
  the reader trust that a `const` never changes identity.
- Use destructuring with defaults for options objects, but remember defaults guard only
  `undefined` — pass through, do not coerce `null` to a default unless you intend to.
- Copy with spread for shallow clones (`{ ...obj }`, `[...arr]`); for nested data use
  `structuredClone(obj)` or explicit per-level copies. Do not assume spread deep-clones.
- Use template literals for interpolation and multi-line strings, but for HTML use a
  tagged template or escaping — string interpolation into markup is an XSS sink.
- Use rest parameters (`function f(...args)`) instead of the array-like `arguments`
  object; rest is a real array and works in arrows.
- Prefer named ES module `import`/`export` over CommonJS in new code; keep imports at the
  top, static, for tree-shaking.
- Combine spread for merging (`{ ...defaults, ...overrides }`) so the last spread wins,
  giving a clear override order.

## Examples

**Good Example** — const, defaults, deep copy where needed

```js
const DEFAULTS = { retries: 3, verbose: false };

function connect(options = {}) {
  // Shallow merge: later spread overrides earlier. Defaults for missing keys.
  const config = { ...DEFAULTS, ...options };

  // Destructuring default fires ONLY when timeout is undefined (not null/0).
  const { timeout = 5000 } = options;

  return { config, timeout };
}

const base = { db: { host: "local" } };
const copy = structuredClone(base); // true deep copy — nested db is independent
copy.db.host = "prod";              // does NOT affect base.db.host
```

**Bad Example** — var leak, shallow-copy aliasing, null defeats default

```js
function connect(options) {
  var config = Object.assign({}, options); // shallow: config.db === options.db (shared!)
  config.db.host = "prod";                 // mutates the caller's object too — aliasing bug

  // Default only guards undefined; passing null leaves timeout = null, not 5000.
  var { timeout = 5000 } = options;

  for (var i = 0; i < 3; i++) {
    // `var i` is function-scoped: every deferred callback sees the final i (3).
    setTimeout(() => console.log(i), 0); // logs 3, 3, 3 — classic var-loop bug
  }
  return { config, timeout };
}
```

## Common Mistakes

- Assuming spread/`Object.assign` deep-clones; mutating a nested field then corrupts the
  original (shared reference).
- Expecting a destructuring or parameter default to apply for `null`, `0`, or `""` — it
  only replaces `undefined`.
- Treating `const` as immutability and then mutating the object's contents.
- Using `var` (or a regular `function` where an arrow's lexical `this` was needed), hitting
  hoisting and loop-closure bugs.
- Interpolating untrusted data into a template literal that becomes HTML → XSS.
- Using an arrow function as a method or constructor and losing/omitting `this`.
- Relying on `arguments` inside an arrow function — it does not exist there; use rest.

## Production Tips

- Enforce `const`/`let` and ban `var` with ESLint (`no-var`, `prefer-const`); these rules
  eliminate an entire class of scoping bugs mechanically.
- Set a compile target matching your supported runtimes; native ES6 is faster and smaller
  than transpiled equivalents, so avoid unnecessary down-leveling.
- Use `structuredClone` (built into modern browsers and Node 17+) instead of the
  `JSON.parse(JSON.stringify(x))` hack, which drops `undefined`, functions, `Date`, and
  cyclic references.

## AI Review Checklist

- Is `const` used by default, `let` only for reassignment, and `var` absent?
- Are spread/`Object.assign` copies treated as shallow, with deep copies used where
  nested data is mutated?
- Do destructuring/parameter defaults account for `null` and other falsy values, not just
  `undefined`?
- Are arrow functions used for callbacks and avoided for methods/constructors?
- Is untrusted data kept out of template literals that render as HTML?
- Are rest parameters used instead of `arguments`, especially inside arrows?

## Related

- `knowledge/javascript/01-language-fundamentals.md`
- `knowledge/javascript/04-functions.md`
- `knowledge/javascript/07-modules.md`
- `knowledge/javascript/16-this-keyword.md`
- `knowledge/javascript/23-clean-code.md`
