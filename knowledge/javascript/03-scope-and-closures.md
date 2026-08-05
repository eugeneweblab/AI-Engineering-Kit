---
id: javascript/03-scope-and-closures
topic: javascript
slug: scope-and-closures
title: "Scope And Closures"
type: doc
order: 3
status: ready
tags: [javascript, scope-and-closures, setTimeout]
related: [javascript/00-overview, javascript/02-execution-context, javascript/04-functions, javascript/15-memory-management, javascript/21-functional-programming]
when_to_use: "Read before writing loops that create callbacks, timers, or event handlers, or any factory function."
---
# Scope And Closures

## Purpose

This document defines how JavaScript resolves variable names (lexical scope and the scope
chain) and what a closure is: a function that keeps access to the variables of the scope
in which it was defined, even after that scope has returned. It equips an agent to reason
about which variable a name refers to and why a captured variable holds the value it does.

## Why It Matters

Closures are not an advanced feature you can opt out of — every callback, event handler,
`setTimeout`, and module private variable is a closure. The single most common closure
bug is capturing a shared, mutable variable in a loop, so every callback sees the final
value instead of the value at creation time. The fix is a one-word change (`var` to
`let`), but only if you understand *why*. Scope also governs memory: a closure that
retains a large object keeps it alive, which is how leaks happen (see
[memory management](15-memory-management.md)).

## Core Principles

- **Scope is lexical (static).** A name resolves by where the function is *written*, not
  where it is *called*. You can determine scope by reading the source.
- **The scope chain is a lookup order.** A name is searched in the current scope, then the
  enclosing scope, outward to the global scope; the first match wins.
- **`let`/`const` are block-scoped; `var` is function-scoped.** A block (`{ }`, loop
  body) creates a new scope only for `let`/`const`.
- **A closure captures variables, not values.** It holds a live reference to the binding,
  so later mutations are visible through the closure.
- **Each `let` loop iteration gets a fresh binding.** `var` shares one binding across all
  iterations — the root of the classic loop-closure bug.

## Best Practices

- Use `let`/`const` in loops that create closures so each iteration captures its own
  binding. This is the direct fix for "all callbacks log the last value."
- Keep variables in the narrowest scope that works; a name declared in a block cannot be
  misused outside it. Narrow scope shrinks the surface for bugs.
- Use closures deliberately for encapsulation (factory functions, private state) instead
  of exposing mutable globals.
- Null out or avoid capturing large objects you no longer need; a long-lived closure
  pins everything it references in memory.
- Do not shadow an outer variable with the same name unless intentional; shadowing hides
  the outer binding and confuses readers.

## Examples

**Good Example** — per-iteration binding and encapsulated state

```js
// `let` gives each iteration its own `i`, so each handler captures its own value.
for (let i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 0); // logs 0, 1, 2
}

// Closure as encapsulation: `count` is private, reachable only through the returned fns.
function makeCounter() {
  let count = 0;                       // lives on after makeCounter returns
  return { inc: () => ++count, get: () => count };
}
```

**Bad Example** — one shared binding captured by every closure

```js
for (var i = 0; i < 3; i++) {
  // `var i` is ONE function-scoped binding shared by all three closures.
  // By the time any timer fires, the loop has finished and i === 3.
  setTimeout(() => console.log(i), 0); // logs 3, 3, 3
}

let counter = 0;                        // exposed mutable state, not encapsulated
function inc() { return ++counter; }    // anyone can reassign `counter` directly
```

## Common Mistakes

- Using `var` in a loop that creates callbacks and getting the final value everywhere.
- Assuming scope follows the call site (dynamic scope); JavaScript is lexical.
- Accidentally shadowing an outer variable, then debugging why the outer one "didn't
  change" — the inner one did.
- Leaking memory by capturing a large object in a closure attached to a long-lived handler
  or module.
- Believing a closure snapshots a value; it references the live binding, so async reads
  see later mutations.

## Production Tips

- Detach event listeners and clear timers when a component unmounts; their closures keep
  the surrounding scope (and any captured DOM nodes) alive until then.
- Prefer module scope or closures over global variables for shared state; globals are one
  scope everyone can clobber.

## AI Review Checklist

- Do loops that create closures use `let`/`const`, not `var`?
- Is each variable declared in the narrowest scope it needs?
- Do closures intentionally capture only what they need, avoiding large retained objects?
- Are event listeners and timers cleaned up so their closures can be garbage-collected?
- Is any variable shadowing deliberate and clear, not accidental?

## Related

- `knowledge/javascript/00-overview.md`
- `knowledge/javascript/02-execution-context.md`
- `knowledge/javascript/04-functions.md`
- `knowledge/javascript/15-memory-management.md`
- `knowledge/javascript/21-functional-programming.md`
