---
id: javascript/100-common-antipatterns
topic: javascript
slug: common-antipatterns
title: "JavaScript Common Antipatterns"
type: doc
order: 100
status: ready
tags: [javascript, common-antipatterns, res.ok, save, innerHTML, addEventListener, setTimeout]
related: [javascript/30-engineering-principles, javascript/14-error-handling, javascript/08-asynchronous-javascript, javascript/16-this-keyword, javascript/26-security]
when_to_use: "Read when writing or reviewing JavaScript to recognize and remove recurring failure patterns."
---
# JavaScript Common Antipatterns

## Purpose

This document catalogs the JavaScript antipatterns that cause the most production
failures and the most review churn. Each entry states the pattern, *why it is wrong*
(the concrete failure it produces), and *the fix*. It is a lookup reference: when you see
one of these shapes in a diff, replace it. These are the defaults JavaScript's
permissiveness makes easy to write and expensive to keep.

## Why It Matters

JavaScript rarely stops you from writing dangerous code — it coerces, it hoists, it
ignores dropped promises, and it happily mutates shared objects. So the same antipatterns
recur in codebase after codebase, and AI-generated code reproduces them because they
"look" correct. Naming them makes them recognizable, and recognizing one is most of
fixing it. Every pattern below maps to a real class of incident: a leaked email, a silent
data-loss bug, a hung request, a security hole.

## Antipatterns

### 1. Swallowing errors in an empty `catch`

**Why it is wrong:** `catch {}` (or catch-and-`console.log`) hides failures. The caller
cannot distinguish "no data" from "the call blew up," so bugs surface far from their
cause and never reach your error tracker.

**The fix:** Handle the error meaningfully or rethrow it. If you truly must ignore it,
comment why.

```js
// Bad — the failure vanishes
try { await save(order); } catch {}

// Good — handle or propagate
try {
  await save(order);
} catch (err) {
  logger.error("order save failed", { orderId: order.id, err });
  throw err; // let the caller decide
}
```

### 2. Loose equality (`==`) coercion

**Why it is wrong:** `==` triggers implicit coercion, so `0 == ""`, `null == undefined`,
and `"" == false` are all `true`. The wrong branch runs on innocuous input.

**The fix:** Always use `===`/`!==`. For null-ish checks use `x == null` only as the
deliberate idiom for "null or undefined," and comment it.

```js
if (count === 0) { /* ... */ }   // Good: no coercion
if (count == false) { /* ... */ } // Bad: "0", "", [] all match
```

### 3. Serial `await` for independent work

**Why it is wrong:** Awaiting each independent call in a loop runs them one at a time,
turning N parallel requests into N sequential round-trips — latency multiplies.

**The fix:** Fire them concurrently with `Promise.all` (or `allSettled` when partial
failure is acceptable).

```js
// Bad — sequential, slow
const results = [];
for (const id of ids) results.push(await fetchUser(id));

// Good — concurrent
const results = await Promise.all(ids.map(fetchUser));
```

### 4. `async` callback passed to `forEach`

**Why it is wrong:** `Array.forEach` ignores the promise each callback returns, so
`await` outside the loop resolves before the async work finishes — data races and
"why didn't it wait?" bugs.

**The fix:** Use `for...of` with `await` for sequential work, or `Promise.all(map(...))`
for concurrent work.

```js
// Bad — the awaits are dropped on the floor
items.forEach(async (i) => { await process(i); });

// Good
await Promise.all(items.map(process));
```

### 5. Mutating shared or argument objects

**Why it is wrong:** Mutating a function argument or a module-level object changes state
for every other holder of that reference. The mutation and the bug appear in different
files, making it one of the hardest classes to debug.

**The fix:** Return a new object; treat inputs as read-only.

```js
// Bad — caller's object is silently changed
function withDefaults(opts) { opts.retries ??= 3; return opts; }

// Good — no mutation of the input
function withDefaults(opts) { return { retries: 3, ...opts }; }
```

### 6. Building HTML from user input with `innerHTML`

**Why it is wrong:** Interpolating user-controlled strings into `innerHTML`, `eval`,
`new Function`, or `document.write` is a cross-site scripting (XSS) hole — the attacker's
markup runs as your code.

**The fix:** Use `textContent` for text, `createElement` for structure, or a templating
library that escapes by default. See [security](26-security.md).

```js
// Bad — XSS: name = "<img src=x onerror=steal()>"
el.innerHTML = `Hello ${name}`;

// Good — inert text
el.textContent = `Hello ${name}`;
```

### 7. Not checking `res.ok` after `fetch`

**Why it is wrong:** `fetch` only rejects on network failure — a `404` or `500` resolves
normally. Skipping the status check means you parse an error page as if it were valid
data.

**The fix:** Check `res.ok` (or the status) before reading the body.

```js
const res = await fetch(url);
if (!res.ok) throw new Error(`HTTP ${res.status}`); // Good
return res.json();
```

### 8. `var` and function-scope hoisting surprises

**Why it is wrong:** `var` is function-scoped and hoisted, so loop closures capture the
final value and variables are usable before their apparent declaration — subtle,
hard-to-spot logic errors.

**The fix:** Use `const` by default and `let` when you reassign; both are block-scoped.

```js
// Bad — every handler logs the last i
for (var i = 0; i < 3; i++) setTimeout(() => console.log(i));

// Good — each closure captures its own i
for (let i = 0; i < 3; i++) setTimeout(() => console.log(i));
```

### 9. Losing `this` by passing a method as a callback

**Why it is wrong:** Passing `obj.method` as a callback detaches it from `obj`; when
called, `this` is `undefined` (strict mode) or the global object, throwing or corrupting
state.

**The fix:** Bind it, wrap it in an arrow function, or define the method as a class field
arrow. See [the `this` keyword](16-this-keyword.md).

```js
btn.addEventListener("click", this.save);          // Bad: this is lost
btn.addEventListener("click", () => this.save());  // Good: arrow keeps this
```

### 10. Unbounded caches and uncleaned listeners

**Why it is wrong:** A module-level object used as a cache that never evicts, or event
listeners/timers never removed, grow without limit — a memory leak that degrades the
process until it crashes.

**The fix:** Bound caches (LRU / max size), and remove listeners, `clearTimeout`, and
`disconnect()` observers when the owner is torn down. See
[memory management](15-memory-management.md).

```js
// Bad — grows forever
const cache = {};
function get(k) { return (cache[k] ??= compute(k)); }

// Good — bounded
const cache = new LRUCache({ max: 500 });
```

## AI Review Checklist

- Are there any empty or log-only `catch` blocks that swallow errors?
- Is `==` used anywhere it should be `===`?
- Is independent async work run concurrently rather than serially?
- Are any arguments or shared objects mutated in place?
- Does user data reach `innerHTML`, `eval`, or another injection sink?
- Is `res.ok` checked after every `fetch`, and are listeners/caches bounded?

## Related

- `knowledge/javascript/30-engineering-principles.md`
- `knowledge/javascript/14-error-handling.md`
- `knowledge/javascript/08-asynchronous-javascript.md`
- `knowledge/javascript/16-this-keyword.md`
- `knowledge/javascript/26-security.md`
