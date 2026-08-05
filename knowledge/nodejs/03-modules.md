---
id: nodejs/03-modules
topic: nodejs
slug: modules
title: "Node.js Modules"
type: doc
order: 3
status: ready
tags: [nodejs, modules, exports, package.json, import.meta.url, __filename, __dirname, "node:"]
related: [nodejs/04-package-management, nodejs/01-nodejs-runtime, nodejs/00-overview, nodejs/18-security, nodejs/15-configuration]
when_to_use: "Read before creating a new project, adding imports/exports, or debugging 'cannot use import statement' or ESM/CommonJS interop errors."
---
# Node.js Modules

## Purpose

This document defines how Node.js loads code: the two module systems (ESM and
CommonJS), how they interoperate, how `package.json` declares the format, and how to
avoid the interop errors that trip up nearly every mixed codebase. An agent that reads
this can add imports and structure a package without producing load-time crashes.

Node supports **ES Modules** (`import`/`export`, the JavaScript standard) and the older
**CommonJS** (`require`/`module.exports`). Which one a file uses is determined by its
extension and the nearest `package.json` `"type"` field — not by the syntax inside it.

## Why It Matters

Module-loading errors fail at import time, before any of your logic runs, and their
messages ("Cannot use import statement outside a module", "require() of ES Module not
supported", "Unexpected token 'export'") are notoriously confusing. A wrong `"type"`
field or a bad `exports` map can make a package unusable for every consumer. Because the
resolution rules are static and strict, getting them right once prevents a whole class
of "works in dev, breaks when published" failures.

## Core Principles

- **The file's format is decided by extension and `"type"`.** `.mjs` is always ESM,
  `.cjs` is always CommonJS, `.js` follows the nearest `package.json` `"type"`
  (`"module"` = ESM, absent/`"commonjs"` = CJS).
- **ESM is async and static; CommonJS is sync and dynamic.** ESM `import` is hoisted and
  resolved before execution; `require` runs synchronously wherever it appears.
- **ESM can import CommonJS, but not cleanly the reverse.** ESM can `import` a CJS
  package; CJS cannot `require` an ESM one — use dynamic `import()` from CJS instead.
- **Prefer ESM for new code.** It is the standard, enables top-level `await`, and is the
  ecosystem's direction. Reserve CommonJS for existing code and legacy consumers.
- **The `exports` field is the public API.** It controls what consumers can import;
  anything not listed is private and unreachable, which is a feature.

## Best Practices

- Set `"type": "module"` in `package.json` for new projects so `.js` files are ESM.
- Use the `exports` field to declare entry points and, where you must support both,
  provide `import` and `require` conditions pointing at the right build.
- Include the file extension in relative ESM imports (`./util.js`, not `./util`) — ESM
  does not guess extensions the way CommonJS did.
- Use the `node:` prefix for built-ins (`import fs from "node:fs"`) so intent is explicit
  and a malicious `fs` package on npm cannot shadow the core module.
- Import lazily with dynamic `import()` for optional or heavy dependencies so startup
  stays fast and unused code is never loaded.

## Examples

**Good Example** — ESM module with explicit built-in and clean exports

```js
// package.json has { "type": "module", "exports": "./index.js" }
import { readFile } from "node:fs/promises"; // node: prefix can't be shadowed by npm

export async function loadConfig(path) {
  const text = await readFile(path, "utf8"); // top-level await also available in ESM
  return JSON.parse(text);
}
// Only loadConfig is exported; helpers stay private to the module.
```

**Bad Example** — mixed systems and ambiguous resolution

```js
// In a file that is ESM (package "type":"module"), this throws at load time:
const fs = require("node:fs");        // require is not defined in an ES module
import helper from "./helper";        // missing ".js" extension → ERR_MODULE_NOT_FOUND

module.exports = { loadConfig };      // module.exports is undefined in ESM
```

## Common Mistakes

- Mixing `require` and `import` in the same file, or forgetting that `"type": "module"`
  makes every `.js` an ES module.
- Omitting the `.js` extension in relative ESM imports.
- Trying to `require()` an ESM-only package from CommonJS instead of using dynamic
  `import()`.
- Publishing a package without an `exports` map, leaking internal files as public API.
- Relying on `__dirname`/`__filename` in ESM (they do not exist there — derive them from
  `import.meta.url`).

## Production Tips

- If you must ship both formats, build to `dist/esm` and `dist/cjs` and wire them through
  conditional `exports`; keep the source single-format to avoid drift.
- Validate the package's entry points with a tool like `@arethetypeswrong/cli` or a smoke
  `import`/`require` in CI before publishing.
- Avoid deep-importing another package's internal paths; use only its documented exports
  so upgrades do not break you.

## AI Review Checklist

- Does `package.json` `"type"` match the syntax used in the `.js` files?
- Do relative ESM imports include the file extension?
- Are core modules imported with the `node:` prefix?
- Is CommonJS→ESM interop done with dynamic `import()`, not `require()`?
- Does the package expose a deliberate `exports` map rather than leaking internals?
- In ESM, is `import.meta.url` used instead of `__dirname`/`__filename`?

## Related

- `knowledge/nodejs/04-package-management.md`
- `knowledge/nodejs/01-nodejs-runtime.md`
- `knowledge/nodejs/00-overview.md`
- `knowledge/nodejs/18-security.md`
- `knowledge/nodejs/15-configuration.md`
