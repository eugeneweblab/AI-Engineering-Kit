---
id: javascript/06-classes
topic: javascript
slug: classes
title: "Classes"
type: doc
order: 6
status: ready
tags: [javascript, classes]
related: [javascript/05-objects-and-prototypes, javascript/16-this-keyword, javascript/04-functions, javascript/22-design-patterns]
when_to_use: "Read before writing or reviewing any `class`, inheritance chain, or method that relies on `this`."
---
# Classes

## Purpose

This document defines how to use JavaScript `class` syntax correctly: fields,
methods, inheritance, `static` members, private state, and the binding rules that
trip up almost every class-based bug. It is written so an agent can author or
review class code without introducing `this` leaks, broken inheritance, or shared
mutable state.

A `class` in JavaScript is syntactic sugar over the prototype system described in
[objects-and-prototypes](05-objects-and-prototypes.md). Understanding what the sugar
compiles to is what separates correct class code from cargo-culted class code.

## Why It Matters

Classes concentrate state and behavior in one place, so a mistake in a class
propagates to every instance and every subclass. A method that loses its `this`
binding fails only when passed as a callback — often in production, never in the
unit test that calls it directly. A field initialized to a shared object silently
couples unrelated instances. These bugs survive review because the class *looks*
object-oriented and familiar. Treat `this` binding and shared references as the two
default suspects whenever a class misbehaves.

## Core Principles

- **A class is a prototype factory, not a Java class.** Methods live on the shared
  prototype; instance fields live on each object. Know which is which before you
  reason about memory or `this`.
- **`this` is determined by the call site, not the definition.** A method detached
  from its instance loses `this`. See [this-keyword](16-this-keyword.md).
- **Prefer composition over deep inheritance.** Each `extends` level couples a
  subclass to its parent's internals. More than one or two levels is a smell.
- **Encapsulate with `#private` fields, not `_`-prefixed conventions.** `#` is
  enforced by the engine; a leading underscore is a hope.
- **Call `super()` before touching `this` in a subclass constructor.** The engine
  throws if you do not — `this` does not exist until `super` runs.

## Best Practices

- Use `#name` private fields and `#method()` private methods for anything not part
  of the public contract. Access outside the class is a syntax error, caught early.
- Bind event/callback methods with class fields (`handleClick = () => {...}`) when
  they will be passed by reference, so `this` stays attached. The cost is one
  closure per instance instead of one shared method — pay it only for callbacks.
- Never initialize a class field to a mutable literal you expect per-instance
  isolation from unless it is inside the constructor or a fresh literal per field —
  a field initializer `items = []` *is* per-instance; a value from an outer scope is not.
- Keep constructors cheap and side-effect-free. Do I/O in an explicit async factory
  method, not the constructor (constructors cannot be `async`).
- Use `static` for factory methods and constants that belong to the type, not an
  instance. Use `static #private` for type-level secrets.
- Prefer `instanceof` only for types you own; it breaks across realms (iframes,
  workers). For structural checks, test for the method you need.

## Examples

**Good Example** — private state, bound callback, `super` first

```js
class Counter {
  #count = 0;                 // truly private; per-instance
  #max;

  constructor(max) {
    this.#max = max;
  }

  // Arrow field: `this` stays bound even when passed as a callback.
  increment = () => {
    if (this.#count < this.#max) this.#count++;
    return this.#count;
  };

  get value() { return this.#count; }
}

class LoggingCounter extends Counter {
  constructor(max, logger) {
    super(max);               // MUST run before touching `this`
    this.logger = logger;
  }
}

const c = new Counter(3);
button.addEventListener("click", c.increment); // works: `this` is bound
```

**Bad Example** — leaked `this`, shared mutable field, fake privacy

```js
class Cart {
  _items = [];                // "_" is a convention, not privacy — anyone can mutate

  addItem(item) {             // regular method: `this` set by call site
    this._items.push(item);
  }

  get total() {
    return this._items.reduce((s, i) => s + i.price, 0);
  }
}

const cart = new Cart();
const add = cart.addItem;     // detached from instance
add({ price: 5 });            // TypeError: Cannot read properties of undefined
                              // `this` is undefined in strict-mode module scope
```

## Common Mistakes

- Passing a regular method as a callback (`onClick={this.handle}`) and losing `this`.
- Using `_field` and assuming it is private; external code and subclasses can still write it.
- Referencing `this` before `super()` in a subclass constructor.
- Putting async I/O in a constructor, or marking a constructor `async` (impossible).
- Initializing a field from a shared outer object and expecting per-instance state.
- Deep inheritance chains that force you to read three files to understand one method.
- Overriding a method but forgetting to call `super.method()` when the parent did real work.

## Production Tips

- In TypeScript, mark fields `readonly` when they are set once in the constructor;
  the compiler then guards against accidental reassignment.
- Prefer `static` factory methods (`User.fromRow(row)`) over overloaded constructors —
  they name intent and can be `async`.
- When a class grows past ~5 responsibilities, split it; a class is not a namespace.

## AI Review Checklist

- Are methods passed as callbacks bound (arrow field) so `this` cannot detach?
- Is private state declared with `#`, not a leading underscore?
- Does every subclass constructor call `super()` before using `this`?
- Are field initializers free of shared mutable references that should be per-instance?
- Is the constructor free of async work and heavy side effects?
- Is inheritance shallow, or would composition express the relationship better?
- Do overrides call `super.method()` when the parent behavior is still required?

## Related

- `knowledge/javascript/05-objects-and-prototypes.md`
- `knowledge/javascript/16-this-keyword.md`
- `knowledge/javascript/04-functions.md`
- `knowledge/javascript/22-design-patterns.md`
