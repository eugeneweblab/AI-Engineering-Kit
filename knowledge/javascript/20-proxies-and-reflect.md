---
id: javascript/20-proxies-and-reflect
topic: javascript
slug: proxies-and-reflect
title: "Proxies And Reflect"
type: doc
order: 20
status: ready
tags: [javascript, proxies-and-reflect]
related: [javascript/19-symbols, javascript/05-objects-and-prototypes, javascript/16-this-keyword, javascript/25-performance]
when_to_use: "Read before intercepting object operations for validation, reactivity, virtualization, or access control."
---
# Proxies And Reflect

## Purpose

This document defines how to use `Proxy` to intercept fundamental object operations
(property get/set, `has`, `deleteProperty`, function calls, construction) via **traps**,
and how `Reflect` provides the matching default behavior for each trap so you can forward
correctly. Together they are the low-level mechanism behind reactive frameworks,
validation layers, and virtualized objects.

A `Proxy` wraps a *target* with a *handler* of trap functions. `Reflect` is a namespace of
functions (`Reflect.get`, `Reflect.set`, `Reflect.has`, …) that perform the default
operation the trap intercepts — the correct way to "do what would normally happen."

## Why It Matters

Proxies let you add cross-cutting behavior (logging, validation, lazy loading, change
tracking) without modifying the target or its class. This power comes with sharp edges:
a trap that forgets to forward an operation silently changes semantics; one that returns
the wrong shape triggers a `TypeError` from the proxy's internal invariant checks; and a
missing `receiver` argument breaks getters on the prototype chain. Because a proxy sits on
the hottest path — every property access — a careless handler can also dominate runtime.
`Reflect` exists precisely to make correct forwarding a one-liner instead of hand-rolled,
subtly-wrong reimplementations.

## Core Principles

- **A proxy is transparent only if every trap forwards.** Traps you don't define fall
  through to the target; traps you *do* define must reproduce default behavior for cases
  you're not customizing.
- **Use `Reflect` as the default operation.** `Reflect.get(target, prop, receiver)` is the
  spec-correct default; reimplementing it with `target[prop]` loses `receiver` and breaks
  inherited getters/setters.
- **Preserve invariants or throw.** Proxies enforce internal consistency (e.g. a
  non-configurable property must report a matching value); violate one and the engine
  throws a `TypeError`.
- **Pass `receiver` through.** It keeps `this` bound to the proxy so accessors and
  subclasses see the wrapper, not the raw target.
- **Proxies are not free.** Every operation goes through a JS function call and defeats
  many engine optimizations; do not wrap hot, allocation-heavy objects casually.
- **Proxies are not transparent to identity.** `proxy !== target`, and they cannot proxy
  private `#fields` of the target from outside the class.

## Best Practices

- Always forward via `Reflect` with all arguments, including `receiver`, then layer your
  custom logic around it — this keeps prototype chains and accessors correct.
- Return the exact type each trap requires (`has`/`deleteProperty` → boolean, `ownKeys` →
  array of string/symbol) so invariant checks pass.
- Keep trap bodies small and side-effect-light; they run on every access and are easy to
  turn into accidental O(n) or I/O-in-a-getter hazards.
- Prefer a plain class, getters/setters, or `Object.defineProperty` when you need to guard
  a *known, fixed* set of properties — proxies are for *dynamic or unknown* keys.
- Use `Proxy.revocable` when handing a capability to untrusted code so you can sever access
  later; a live proxy is a permanent handle.
- Validate in the `set` trap and **throw** on invalid writes (in strict mode a `false`
  return also throws) so bad data never lands on the target.

## Examples

**Good Example** — validating proxy that forwards correctly via Reflect

```js
function validated(target, schema) {
  return new Proxy(target, {
    get(obj, prop, receiver) {
      // Reflect.get with `receiver` → inherited getters see the proxy as `this`.
      return Reflect.get(obj, prop, receiver);
    },
    set(obj, prop, value, receiver) {
      const check = schema[prop];
      if (check && !check(value)) {
        throw new TypeError(`Invalid value for "${String(prop)}": ${value}`);
      }
      // Default assignment, done correctly — respects setters and receiver.
      return Reflect.set(obj, prop, value, receiver);
    },
  });
}

const user = validated({}, { age: v => Number.isInteger(v) && v >= 0 });
user.age = 30;          // ok
user.name = "Ada";      // ok: no rule → forwarded unchanged
try { user.age = -1; }  // throws: never written to the target
catch (e) { console.log(e.message); }
```

**Bad Example** — hand-rolled forwarding that breaks semantics

```js
const handler = {
  get(target, prop) {
    // No `receiver`: an inherited getter that reads `this.other` sees the raw
    // target, not the proxy, so wrapping/validation on siblings is bypassed.
    return target[prop];
  },
  set(target, prop, value) {
    if (prop === "age" && value < 0) return false; // silently rejected in sloppy mode
    target[prop] = value;   // ignores setters and receiver; may violate invariants
    return true;
  },
  ownKeys() { return "nope"; }, // WRONG type: `ownKeys` must return an array-like object
};
const p = new Proxy({}, handler);
Object.keys(p);             // throws TypeError: ownKeys trap must return an array-like object
```

## Common Mistakes

- Reimplementing defaults with `target[prop]` / `target[prop] = value` instead of
  `Reflect`, dropping `receiver` and breaking inherited accessors.
- Returning the wrong type from a trap (`has`, `deleteProperty`, `defineProperty` need
  booleans; `ownKeys` needs an array) and hitting invariant `TypeError`s.
- A `set` trap that returns `false` in sloppy mode, swallowing failed writes silently.
- Wrapping performance-critical objects and paying a per-access function-call tax.
- Assuming a proxy can read the target's private `#fields` — it cannot from outside.
- Forgetting `proxy !== target`, so identity/`Map`-key comparisons diverge.

## Production Tips

- Frameworks like Vue use proxies for reactivity — the takeaway is to keep traps pure and
  cheap, and to memoize derived work outside the trap.
- Use `Proxy.revocable` for sandboxing untrusted plugins; call `revoke()` on teardown so
  the object graph can be garbage-collected.
- When debugging "impossible" `TypeError`s on property access, suspect a proxy invariant
  violation and log which trap fired.

## AI Review Checklist

- Do all traps forward defaults via `Reflect` with `receiver` passed through?
- Does every trap return the type its operation requires (boolean, array, value)?
- Does the `set` trap **throw** (not just return `false`) on invalid input?
- Is a proxy actually warranted, versus getters/`defineProperty` for fixed keys?
- Is `Proxy.revocable` used when exposing objects to untrusted code?
- Has proxy overhead been considered for objects on a hot path?

## Related

- `knowledge/javascript/19-symbols.md`
- `knowledge/javascript/05-objects-and-prototypes.md`
- `knowledge/javascript/16-this-keyword.md`
- `knowledge/javascript/25-performance.md`
- `knowledge/javascript/06-classes.md`
