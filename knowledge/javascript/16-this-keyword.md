---
id: javascript/16-this-keyword
topic: javascript
slug: this-keyword
title: "This Keyword"
type: doc
order: 16
status: ready
tags: [javascript, this-keyword]
related: [javascript/04-functions, javascript/06-classes, javascript/03-scope-and-closures, javascript/02-execution-context, javascript/05-objects-and-prototypes]
when_to_use: "Read before writing or reviewing code where a method, callback, or class handler references `this`."
---
# This Keyword

## Purpose

This document defines what `this` refers to in JavaScript and how it is determined, so an
agent can write methods, callbacks, and class handlers that bind the right receiver. `this`
is not lexical like a variable — it is set by *how a function is called*, which is the
single most common source of "undefined is not a function" and lost-context bugs.

## Why It Matters

`this` is bound at **call time**, not definition time. The same method has a different
`this` depending on whether it is called as `obj.method()`, passed as a bare callback,
or invoked standalone. Detaching a method from its object — passing `this.handleClick`
to `addEventListener`, or `arr.map(obj.fn)` — silently rebinds `this`, so the code either
throws (`Cannot read properties of undefined`) or, worse, mutates the wrong object. The
failure is subtle and call-site-dependent, which makes it hard to reproduce and easy to
ship.

## Core Principles

- **`this` depends on the call, not the definition.** Four binding rules, in precedence
  order: `new` (the new instance) > explicit `call`/`apply`/`bind` > method call
  `obj.fn()` (the object) > plain call `fn()` (undefined in strict mode / modules, global
  otherwise).
- **Arrow functions have no own `this`.** They capture `this` lexically from the enclosing
  scope at definition. This is exactly what you want for callbacks inside a method.
- **Detaching a method loses its receiver.** `const f = obj.method; f()` — `this` is no
  longer `obj`. Passing a method as a callback does the same detachment.
- **Class methods run in strict mode**, so a lost `this` is `undefined` and throws
  immediately (a feature — it fails loudly instead of corrupting the global object).
- **`bind` returns a new, permanently-bound function.** It cannot be re-bound; a later
  `call`/`apply` cannot override it.

## Best Practices

- Use an **arrow function** for callbacks that need the surrounding `this` (inside methods,
  in `setTimeout`, in array iteration): `arr.forEach(x => this.add(x))`.
- For class event handlers, define them as **arrow-function class fields**
  (`handleClick = () => {...}`) so `this` is bound once and passing the reference stays
  safe.
- When passing a method as a callback, bind it explicitly (`obj.method.bind(obj)`) or wrap
  it in an arrow (`() => obj.method()`) — never pass the bare `obj.method`.
- Do **not** use arrow functions for object methods that rely on `this` referring to the
  object, or for prototype methods — they capture the outer scope, not the object.
- Use `call`/`apply` to invoke a function with an explicit receiver when borrowing methods;
  reach for `bind` when you need a reusable pre-bound function.
- Prefer passing needed values as arguments over relying on `this` when a function is used
  as a standalone callback — it removes the binding question entirely.

## Examples

**Good Example** — arrow captures the instance, handler stays bound

```js
class Counter {
  count = 0;

  // Arrow class field: `this` is the instance, permanently, even when detached.
  increment = () => {
    this.count++; // `this` is the Counter, no matter how increment is called
  };

  start(button) {
    // Passing the arrow-bound reference is safe — receiver travels with it.
    button.addEventListener("click", this.increment);

    // Arrow callback captures the method's `this` lexically → correct receiver.
    [1, 2, 3].forEach(() => this.count++);
  }
}
```

**Bad Example** — detached method loses `this`, wrong-scoped callback

```js
class Counter {
  count = 0;
  increment() { this.count++; } // ordinary method: `this` set by the call site

  start(button) {
    // Bare method reference detaches from the instance. On click `this` is undefined
    // (strict mode) → "Cannot read properties of undefined (reading 'count')".
    button.addEventListener("click", this.increment);

    // A regular function callback has its own `this` (undefined here), NOT the instance.
    [1, 2, 3].forEach(function () { this.count++; }); // throws
  }
}
```

## Common Mistakes

- Passing `obj.method` as a callback and losing `this` (the detachment bug).
- Using a regular `function` callback inside a method and expecting `this` to be the
  object — it is `undefined`/global instead.
- Using an arrow function as an object or prototype method, so `this` is the module scope,
  not the object.
- Assuming `this` in a plain function call is the global object — in modules and strict
  mode it is `undefined`.
- Re-binding an already-`bind`-ed function and expecting the new receiver to win (it does
  not).
- Relying on `this` inside a standalone extracted function that was written as a method.

## Production Tips

- Enable strict mode everywhere (modules are strict by default) so a lost `this` throws
  at the point of failure instead of silently writing to `globalThis`.
- Lint with `@typescript-eslint` / `eslint` rules that flag unbound method references
  passed as callbacks; TypeScript's `strictBindCallApply` and `noImplicitThis` catch many
  of these at compile time.

## AI Review Checklist

- Is any method passed as a bare callback without `bind` or an arrow wrapper?
- Are class event handlers arrow-function fields (or bound in the constructor)?
- Are callbacks inside methods arrow functions when they need the instance's `this`?
- Are object/prototype methods regular functions (not arrows) so `this` is the object?
- Does any code assume `this` is the global object in a plain call under strict mode?
- Is `bind`/`call`/`apply` used deliberately where an explicit receiver is required?

## Related

- `knowledge/javascript/04-functions.md`
- `knowledge/javascript/06-classes.md`
- `knowledge/javascript/03-scope-and-closures.md`
- `knowledge/javascript/02-execution-context.md`
- `knowledge/javascript/05-objects-and-prototypes.md`
