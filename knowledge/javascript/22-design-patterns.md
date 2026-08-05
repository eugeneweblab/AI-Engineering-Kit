---
id: javascript/22-design-patterns
topic: javascript
slug: design-patterns
title: "JavaScript Design Patterns"
type: doc
order: 22
status: ready
tags: [javascript, design-patterns, getInstance, quote, freeze, SingletonFactoryManager, API_URL]
related: [javascript/21-functional-programming, javascript/05-objects-and-prototypes, javascript/06-classes, javascript/23-clean-code, javascript/07-modules]
when_to_use: "Read before reaching for a classical design pattern, or when a problem repeats and you need a proven, idiomatic structure."
---
# JavaScript Design Patterns

## Purpose

This document defines how classical design patterns map onto idiomatic JavaScript, which
patterns the language makes trivial (or obsolete), and how to choose one without
over-engineering. It focuses on the patterns that recur in real JavaScript: module,
factory, singleton, observer, strategy, and decorator.

Patterns are named solutions to recurring design problems — a shared vocabulary, not a
goal. In JavaScript, closures, first-class functions, and modules often express a pattern
in a few lines that would need a class hierarchy elsewhere.

## Why It Matters

Applied well, patterns communicate intent instantly ("this is a strategy") and steer you
toward structures that decouple, extend, and test cleanly. Applied badly, they are the
main source of accidental complexity: a `SingletonFactoryManager` where a plain object
would do. JavaScript's dynamism changes the calculus — many Gang-of-Four patterns exist to
work around limitations JavaScript doesn't have (no first-class functions, no modules), so
copying them verbatim adds ceremony without benefit. Knowing which patterns are native and
which are anti-patterns here is what separates clean design from cargo-culting Java.

## Core Principles

- **Reach for a pattern when a problem repeats, not preemptively.** Introduce structure to
  solve a concrete pain (duplication, coupling), never "in case."
- **Prefer the language's native form.** A module is the module pattern; a closure is
  encapsulation; a function is a strategy. Don't rebuild these with classes.
- **Favor composition over inheritance.** Combine small behaviors; deep class hierarchies
  are rigid and hard to change in a duck-typed language.
- **Program to an interface (shape), not a concrete type.** Depend on the methods you call,
  which lets you swap implementations — strategy, factory, and DI all rely on this.
- **A pattern is a means, not the goal.** If the plain version is clearer, the plain
  version wins; naming a pattern doesn't justify complexity.

## Best Practices

- Use ES **modules** for singletons and namespacing — a module's exports are evaluated
  once and shared, giving you a singleton without a class or global.
- Use a **factory function** (returns a configured object/closure) instead of `new` when
  construction has branching logic or you want to hide the concrete type.
- Implement **strategy** by passing a function; select behavior with a lookup object
  (`{ [key]: fn }`) rather than a `switch` that grows with every new case.
- Use the **observer** pattern via `EventTarget` (browser/Node) or a small emitter for
  decoupled pub/sub; unsubscribe on teardown to avoid leaks.
- Apply the **decorator** pattern by wrapping functions/objects (higher-order functions)
  to add cross-cutting behavior — logging, caching — without touching the original.
- Avoid the classical **singleton class with lazy `getInstance`**; it hides global state
  and wrecks testability. If you must, make the shared state injectable so tests can reset.

## Examples

**Good Example** — idiomatic strategy + module singleton

```js
// Strategy as data: adding a shipping method is one entry, no branching to edit.
const shippingCost = {
  standard: (w) => w * 1.0,
  express:  (w) => w * 2.5,
  freight:  (w) => 50 + w * 0.2,
};
function quote(method, weight) {
  const strat = shippingCost[method];
  if (!strat) throw new Error(`Unknown method: ${method}`);
  return strat(weight); // behavior selected by lookup, open for extension
}

// Singleton via module: config.js is evaluated once; every importer shares it.
// export const config = Object.freeze({ apiUrl: process.env.API_URL });

// Decorator as a higher-order function: adds caching without changing `fetchUser`.
const withCache = (fn) => {
  const cache = new Map();
  return (id) => (cache.has(id) ? cache.get(id) : cache.set(id, fn(id)).get(id));
};
```

**Bad Example** — Java-style ceremony for what the language gives free

```js
// Reinventing modules/singletons with a class + global mutable state.
class ConfigManager {
  static instance;
  static getInstance() {
    if (!ConfigManager.instance) ConfigManager.instance = new ConfigManager();
    return ConfigManager.instance; // hidden global; tests can't reset it
  }
  constructor() { this.values = {}; }
}
ConfigManager.getInstance().values.apiUrl = "x"; // spooky action at a distance

// Strategy as an ever-growing switch: every new method edits this function.
function quote(method, weight) {
  switch (method) {                // violates open/closed; merge-conflict magnet
    case "standard": return weight * 1.0;
    case "express":  return weight * 2.5;
    // ...forever
    default: throw new Error("unknown");
  }
}
```

## Common Mistakes

- Porting Gang-of-Four class patterns literally instead of using closures, functions, and
  modules — adding ceremony JavaScript doesn't need.
- Building a singleton class with `getInstance` where a module export is simpler and
  testable.
- Growing a `switch`/`if-else` chain where a strategy lookup object belongs.
- Deep inheritance hierarchies that are hard to refactor; prefer composition/mixins.
- Introducing a pattern speculatively, adding indirection no current requirement needs.
- Observer/event listeners that never unsubscribe, leaking memory and firing stale handlers.

## Production Tips

- For dependency injection, pass collaborators as function/constructor arguments rather
  than importing them directly — it makes units testable without module mocking.
- Prefer `EventTarget`/`AbortController` for pub/sub and cleanup over bespoke emitters;
  `AbortSignal` gives you cancellation and teardown for free.
- When a "pattern" makes a reviewer ask "why is this here?", that's the signal to delete
  the abstraction and inline the plain version.

## AI Review Checklist

- Is a pattern solving a real, present problem, or added speculatively?
- Are singletons/namespacing done with modules rather than `getInstance` classes?
- Is branching behavior a strategy lookup instead of a growing `switch`?
- Does the design favor composition over deep inheritance?
- Do observers/event listeners have a matching unsubscribe/teardown path?
- Would a plain function or object be clearer than the named pattern used here?

## Related

- `knowledge/javascript/21-functional-programming.md`
- `knowledge/javascript/05-objects-and-prototypes.md`
- `knowledge/javascript/06-classes.md`
- `knowledge/javascript/23-clean-code.md`
- `knowledge/javascript/07-modules.md`
