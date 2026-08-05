---
id: javascript/05-objects-and-prototypes
topic: javascript
slug: objects-and-prototypes
title: "Objects And Prototypes"
type: doc
order: 5
status: ready
tags: [javascript, objects-and-prototypes, for...in, Object.prototype, __proto__, Object.keys, constructor, prototype]
related: [javascript/00-overview, javascript/01-language-fundamentals, javascript/04-functions, javascript/06-classes, javascript/16-this-keyword]
when_to_use: "Read before creating objects, extending prototypes, or debugging inherited/missing properties."
---
# Objects And Prototypes

## Purpose

This document explains how JavaScript objects work: creating them, property descriptors
and mutability, and the prototype chain that resolves property access and powers
inheritance. It lets an agent predict where a property comes from, avoid mutating shared
prototypes, and understand what [classes](06-classes.md) compile down to.

## Why It Matters

JavaScript inheritance is prototype-based, not class-based — `class` is syntax over
prototypes. Property access walks a chain of objects until it finds the name or reaches
`null`. Misunderstanding this chain produces subtle bugs: reading an inherited property
you meant to be own, mutating `Object.prototype` and poisoning every object, or leaking a
prototype through `for...in`. Because prototypes are shared by every instance, a mistake
on a prototype is a mistake in every object at once.

## Core Principles

- **Objects are keyed collections; keys are strings or symbols.** Values can be any type,
  including functions (methods).
- **Every object has an internal prototype** (`[[Prototype]]`, read via
  `Object.getPrototypeOf`). Property lookup walks it until a match or `null`.
- **Own vs. inherited matters.** `obj.hasOwnProperty(k)` (or `Object.hasOwn(obj, k)`)
  distinguishes a property on the object from one found up the chain.
- **Assignment creates an own property; it never mutates the prototype.** But reading and
  *mutating* an inherited object value does affect the shared prototype.
- **Property descriptors control behavior.** `writable`, `enumerable`, `configurable`, and
  getters/setters govern how a property can be used.

## Best Practices

- Create objects with literals `{}` or `Object.create(proto)`; reserve `class`/`new` for
  when you need instances with shared methods.
- Use `Object.hasOwn(obj, key)` (or `Object.getOwnPropertyNames`) to test own properties;
  do not trust `for...in` for own-only iteration — it walks the chain.
- Never add or modify properties on built-in prototypes (`Object.prototype`,
  `Array.prototype`); it affects every object/array in the program and breaks feature
  detection.
- Iterate objects with `Object.keys`/`Object.entries`/`Object.values` (own + enumerable),
  not `for...in`, unless you specifically want inherited keys.
- Use `Object.freeze` for constants and configuration you must not mutate; freezing is
  shallow, so freeze nested objects too if needed.
- Copy with `structuredClone(obj)` for deep copies, or spread `{...obj}` for shallow ones
  — and know spread does not clone nested references.

## Examples

**Good Example** — explicit prototype, own-property check, no shared mutation

```js
const base = { greet() { return `Hi, ${this.name}`; } }; // shared method on prototype

function makeUser(name) {
  const user = Object.create(base); // user's prototype is `base`
  user.name = name;                 // OWN property, does not touch `base`
  return user;
}

const u = makeUser("Ada");
u.greet();                       // "Hi, Ada" — greet found via the prototype chain
Object.hasOwn(u, "name");        // true  — own property
Object.hasOwn(u, "greet");       // false — inherited, not own
```

**Bad Example** — polluting a built-in prototype and unsafe iteration

```js
// Adds an enumerable property to EVERY object in the program.
Object.prototype.tag = "x";

const config = { host: "db", port: 5432 };
for (const key in config) {
  // for...in walks the prototype chain, so this also yields "tag".
  console.log(key); // host, port, tag  ← leaked inherited key
}
config.hasOwnProperty; // now unreliable across the app; feature checks break
```

## Common Mistakes

- Extending `Object.prototype` or `Array.prototype` and breaking `for...in`, JSON
  handling, and library feature detection everywhere.
- Using `for...in` to iterate an object's own keys and picking up inherited/enumerable
  properties.
- Assuming spread `{...obj}` or `Object.assign` deep-clones; they copy top-level
  references, so nested objects stay shared.
- Calling `obj.hasOwnProperty(k)` on an object whose prototype is `null`
  (`Object.create(null)`) — use `Object.hasOwn(obj, k)` instead.
- Mutating an object read through the prototype chain and unexpectedly changing the shared
  prototype's value.

## Production Tips

- Prefer `Map` over a plain object when keys are dynamic or user-supplied; `Map` has no
  prototype keys, so there is no `__proto__`/`constructor` collision or prototype-pollution
  risk.
- Guard against prototype-pollution when merging untrusted JSON: reject or skip
  `__proto__`, `constructor`, and `prototype` keys.

## AI Review Checklist

- Are built-in prototypes left unmodified?
- Is own-vs-inherited handled correctly (`Object.hasOwn`, `Object.keys`) instead of raw
  `for...in`?
- Are deep copies done with `structuredClone`, with an awareness that spread is shallow?
- Is `Map` used instead of a plain object for dynamic/untrusted keys?
- Is untrusted merge input guarded against `__proto__`/`constructor` prototype pollution?

## Related

- `knowledge/javascript/00-overview.md`
- `knowledge/javascript/01-language-fundamentals.md`
- `knowledge/javascript/04-functions.md`
- `knowledge/javascript/06-classes.md`
- `knowledge/javascript/16-this-keyword.md`
