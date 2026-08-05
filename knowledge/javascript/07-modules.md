---
id: javascript/07-modules
topic: javascript
slug: modules
title: "JavaScript Modules"
type: doc
order: 7
status: ready
tags: [javascript, modules]
related: [javascript/03-scope-and-closures, javascript/17-es6-features, javascript/29-tooling, javascript/15-memory-management]
when_to_use: "Read before creating, importing, or refactoring module files, or configuring ESM/CommonJS interop."
---
# JavaScript Modules

## Purpose

This document defines how to structure JavaScript code into ES modules (ESM):
`import`/`export`, static vs dynamic imports, side effects, circular dependencies,
and the interop rules between ESM and CommonJS. It is written so an agent can add or
refactor a module without breaking tree-shaking, load order, or the dependency graph.

ESM (`import`/`export`) is the standard module system in 2026 for browsers, Node,
Deno, and Bun. CommonJS (`require`/`module.exports`) still exists in the Node
ecosystem; knowing when each applies prevents a class of "cannot use import
statement outside a module" and "require is not defined" errors.

## Why It Matters

Modules are the unit of encapsulation and the unit of loading. The shape of your
imports decides what a bundler can eliminate as dead code, whether a browser can
parallelize downloads, and whether a change ripples across the graph. A single
default export where a named export belonged defeats tree-shaking for the whole
file. A top-level side effect turns an innocent `import` into a hidden action that
runs on load. Because module structure is set once and imported everywhere, getting
it wrong is expensive to reverse.

## Core Principles

- **ESM is static.** `import`/`export` are resolved before execution, which is what
  enables tree-shaking and cyclic-dependency handling. You cannot `import`
  conditionally at the top level — use dynamic `import()` for that.
- **Modules are singletons.** A module's top-level code runs once; every importer
  shares the same instance and the same exported bindings.
- **Exports are live bindings, not copies.** An imported value reflects later
  reassignment in the source module. This differs from CommonJS value copies.
- **A module should have no side effects on import** unless that is its explicit
  purpose (a polyfill, a registration). Importers must be able to reason about cost.
- **One concern per module.** Cohesion at the file level is what keeps the
  dependency graph shallow and reviewable.

## Best Practices

- Prefer **named exports** over a default export. Named exports are tree-shakeable,
  greppable, and rename-safe; a default export hides the symbol's name from tooling.
- Use **dynamic `import()`** to code-split heavy or rarely used code (charts, editors).
  It returns a promise and loads on demand — the cost is an extra network round trip.
- Keep the **public surface in an index barrel** (`index.js` re-exporting) only for
  small, stable packages; barrels can defeat tree-shaking and create cycles in large apps.
- Avoid **circular imports**; if A imports B and B imports A, one will see a partially
  initialized (possibly `undefined`) binding at module-eval time. Break the cycle by
  extracting the shared piece into a third module.
- Import **only what you use** by name so bundlers drop the rest: `import { debounce }`
  not `import _ from "lodash"`.
- In Node, declare module type explicitly (`"type": "module"` in `package.json`, or
  `.mjs`/`.cjs` extensions). Do not rely on the default.

## Examples

**Good Example** — named exports, no side effects, lazy heavy dependency

```js
// money.js — pure, named exports, tree-shakeable
export function format(cents, currency = "USD") { /* ... */ }
export function parse(input) { /* ... */ }
// No top-level side effects: importing this file does nothing but define bindings.

// checkout.js
import { format } from "./money.js";        // pull in only what is used

async function renderInvoice(data) {
  // Load the heavy PDF library only when an invoice is actually rendered.
  const { buildPdf } = await import("./pdf.js");   // dynamic, code-split
  return buildPdf(data, format);
}
```

**Bad Example** — default export, import-time side effect, hidden cost

```js
// analytics.js
console.log("analytics loaded");            // side effect runs on import
window.__analytics = new Analytics();       // mutates global just by being imported

export default new Analytics();             // default export: name is lost to tooling,
                                            // and this instance is created eagerly

// page.js
import a from "./analytics.js";             // paid the cost + side effect just to import
// tree-shaker cannot drop unused members of a default-exported object
```

## Common Mistakes

- Mixing `require` and `import` in the same file, or assuming ESM `import` works in a
  CommonJS file without `"type": "module"`.
- Default-exporting a large object, defeating tree-shaking for everything inside it.
- Top-level side effects (globals, network, `console`) that run merely on import.
- Circular imports that yield `undefined` bindings during module evaluation.
- Forgetting the file extension in relative ESM imports where the runtime requires it
  (Node ESM and browsers need `./util.js`, not `./util`).
- Deep barrel files that pull the entire subtree into the bundle.

## Production Tips

- Verify tree-shaking by inspecting the production bundle, not by trusting `import`
  syntax; a `sideEffects: false` flag in `package.json` lets bundlers prune aggressively.
- For ESM/CJS interop in Node, remember `import cjs from "cjs-pkg"` gives the
  `module.exports` object; named imports from CJS are synthesized and can be flaky.
- Use `import.meta.url` (ESM) instead of `__dirname`/`__filename`, which do not exist
  in ESM.

## AI Review Checklist

- Are exports named rather than default, unless a default is genuinely warranted?
- Does importing the module produce no side effects (no globals, I/O, or logging)?
- Is heavy or rarely used code split behind dynamic `import()`?
- Are there any circular imports that could yield partially initialized bindings?
- Do relative imports include the extension where the runtime requires it?
- Is the Node module type (`"type": "module"` or `.mjs`/`.cjs`) declared explicitly?
- Do wildcard/barrel imports pull in more than the code actually uses?

## Related

- `knowledge/javascript/03-scope-and-closures.md`
- `knowledge/javascript/17-es6-features.md`
- `knowledge/javascript/29-tooling.md`
- `knowledge/javascript/15-memory-management.md`
