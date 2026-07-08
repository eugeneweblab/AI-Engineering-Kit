---
id: javascript/19-symbols
topic: javascript
slug: symbols
title: "Symbols"
type: doc
order: 19
status: ready
tags: [javascript, symbols]
related: [javascript/18-iterators-and-generators, javascript/05-objects-and-prototypes, javascript/17-es6-features, javascript/20-proxies-and-reflect]
when_to_use: "Read before adding non-string object keys, defining iteration/serialization hooks, or hiding internal metadata on objects."
---
# Symbols

## Purpose

This document defines what `Symbol` values are, when to use them as object keys, and how
the **well-known symbols** (`Symbol.iterator`, `Symbol.asyncIterator`, `Symbol.toPrimitive`,
`Symbol.hasInstance`, and others) let you hook into built-in language behavior. It also
covers the global `Symbol.for` registry versus unique symbols.

A symbol is a primitive whose only guarantee is **uniqueness**: `Symbol("x") !== Symbol("x")`.
Its description is a label for debugging, not an identity.

## Why It Matters

Symbols solve two concrete problems. First, **collision-free keys**: a symbol key cannot
clash with any string key, so you can attach metadata to objects you don't own (or that
third parties extend) without fear of overwrites. Second, **customization hooks**: the
language looks up well-known symbols to decide how an object iterates, converts to a
primitive, or reports its tag — implementing them is how you make your type behave like a
built-in. Misusing symbols (expecting privacy, or serializing them) produces bugs that
are hard to spot because symbol keys are invisible to `JSON.stringify`, `for...in`, and
`Object.keys`.

## Core Principles

- **Symbols are unique and immutable.** Two symbols with the same description are still
  different keys. Equality is by identity only.
- **Symbol keys are non-enumerable to string-based reflection.** They're skipped by
  `for...in`, `Object.keys`, and `JSON.stringify`; find them with
  `Object.getOwnPropertySymbols` or `Reflect.ownKeys`.
- **Symbols are "soft private", not secure.** They hide keys from casual enumeration but
  are fully reachable via reflection. Use `#private` fields for true encapsulation.
- **Well-known symbols are the extension points of the language.** Implementing
  `Symbol.iterator` makes a type iterable; `Symbol.toPrimitive` controls coercion.
- **`Symbol.for(key)` is a global, shared registry;** `Symbol(desc)` is always fresh.
  Use the registry only when the *same* symbol must be found across realms or modules.

## Best Practices

- Use a symbol key when attaching metadata to objects you don't own, to guarantee no
  collision with present or future string properties.
- Implement `[Symbol.iterator]` (or `[Symbol.asyncIterator]`) to make custom collections
  work with `for...of`, spread, and destructuring — the standard, expected interface.
- Prefer `#private` class fields for encapsulation; reach for symbols only when you need
  a key that is stable but deliberately off the enumerable path.
- Use `Symbol.for` sparingly and with namespaced keys (`"app.myLib.id"`) to avoid registry
  collisions; the registry is process-global and never garbage-collected.
- Set `[Symbol.toStringTag]` on custom types so `Object.prototype.toString` reports a
  meaningful tag for debugging and duck-typing.
- Never rely on symbols surviving serialization boundaries — persist an explicit string
  field if the data must cross JSON, `structuredClone`, or the network.

## Examples

**Good Example** — collision-free metadata and a language hook

```js
// Unique key: cannot clash with any current or future string property on the node.
const CACHE = Symbol("renderCache");

function memoizeRender(node) {
  if (!node[CACHE]) node[CACHE] = expensiveRender(node); // safe on foreign objects
  return node[CACHE];
}

class Temperature {
  constructor(c) { this.celsius = c; }
  // Language hook: controls how the object coerces in numeric/string contexts.
  [Symbol.toPrimitive](hint) {
    if (hint === "number") return this.celsius;
    return `${this.celsius}°C`;
  }
  get [Symbol.toStringTag]() { return "Temperature"; } // Object.prototype.toString tag
}

const t = new Temperature(21);
console.log(+t);                    // 21   → "number" hint
console.log(`${t}`);                // "21°C" → default/string hint
console.log(Object.prototype.toString.call(t)); // "[object Temperature]"
```

**Bad Example** — treating symbols as security and expecting persistence

```js
const SSN = Symbol("ssn");
class User {
  constructor(ssn) { this[SSN] = ssn; } // NOT private: reachable via reflection
}
const u = new User("123-45-6789");

// "Hidden" data is trivially recovered — symbols are not access control.
const key = Object.getOwnPropertySymbols(u)[0];
console.log(u[key]);                // "123-45-6789" — leaked

// Symbol-keyed data silently disappears across serialization.
console.log(JSON.stringify(u));     // "{}" — ssn dropped, likely a data-loss bug

// Fresh symbols never match: this lookup always fails.
console.log(u[Symbol("ssn")]);      // undefined — new symbol, different identity
```

## Common Mistakes

- Believing symbol keys are private; they are exposed by `getOwnPropertySymbols` and
  `Reflect.ownKeys`. Use `#fields` for real privacy.
- Expecting `JSON.stringify`, `Object.assign` (copies symbols but not deep), or
  `structuredClone` to preserve symbol-keyed data across boundaries.
- Creating a new `Symbol(desc)` and expecting it to equal a previously created one —
  only `Symbol.for(key)` returns the same symbol.
- Overusing the global registry, leaking process-global entries that are never collected.
- Forgetting to implement `Symbol.asyncIterator` on async sources, breaking `for await`.

## Production Tips

- When debugging "missing" object keys, dump `Reflect.ownKeys(obj)` — it lists string and
  symbol keys together, unlike `Object.keys`.
- Libraries use symbols to brand instances (`obj[BRAND] === true`) for reliable
  cross-version `instanceof`-style checks that survive bundler duplication.
- Avoid symbol keys in hot-path objects that get spread or `JSON`-cloned frequently; the
  extra reflection to preserve them adds cost and is easy to forget.

## AI Review Checklist

- Are symbols used for collision-free keys, not mistaken for access control?
- Is `#private` used where true encapsulation is required?
- Do custom iterables implement `Symbol.iterator` / `Symbol.asyncIterator` correctly?
- Is any symbol-keyed data that must persist also stored under an explicit string field?
- Is `Symbol.for` limited to genuine cross-realm needs with namespaced keys?
- Are symbol keys accounted for when copying or serializing objects?

## Related

- `knowledge/javascript/18-iterators-and-generators.md`
- `knowledge/javascript/05-objects-and-prototypes.md`
- `knowledge/javascript/17-es6-features.md`
- `knowledge/javascript/20-proxies-and-reflect.md`
- `knowledge/javascript/06-classes.md`
