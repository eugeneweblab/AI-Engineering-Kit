---
id: javascript/00-overview
topic: javascript
slug: overview
title: "JavaScript Overview"
type: doc
order: 0
status: ready
tags: [javascript, overview, arguments]
related: [javascript/01-language-fundamentals, javascript/02-execution-context, javascript/03-scope-and-closures, javascript/04-functions, javascript/05-objects-and-prototypes]
when_to_use: "Read first when starting any JavaScript work to see how the topic's docs fit together."
---
# JavaScript Overview

## Purpose

This document is the map for the JavaScript knowledge base. It explains what the
language is, how its documents are organized, and the order in which an agent should
consult them. Read it first so you know *which* document answers the question in front
of you instead of guessing from memory.

JavaScript is a single-threaded, dynamically typed, prototype-based language governed by
the ECMAScript specification (ES2015 through the current yearly editions). It runs in
browsers, in Node.js, and in edge runtimes. The rules here target modern JavaScript —
strict mode, ES modules, `let`/`const`, and standard library features that are stable as
of 2026. Legacy patterns (`var`, `arguments`, IIFE module wrappers) appear only as
things to recognize and avoid.

## Why It Matters

Most "weird JavaScript" bugs are not weird — they follow directly from a few mechanics
that the language never hides: how values are typed and coerced, how execution contexts
are created and hoisted, how scope and closures capture variables, how `this` is bound,
and how prototype lookup resolves properties. An agent that understands these mechanics
predicts behavior instead of discovering it in production. An agent that does not will
write code that passes the happy path and fails on `null`, on `0`, on an async callback,
or on a shared closure variable.

## Core Principles

- **Prefer the strict, explicit form.** `===` over `==`, `const` over `let` over `var`,
  ES modules over globals. Explicit code is reviewable code.
- **Understand a feature before using it.** Closures, `this`, and prototypes are not
  optional trivia — they change what your code does. Do not cargo-cult syntax.
- **Read the specific doc, not this one, for rules.** This overview only routes you.
- **Modern first.** Assume ES2020+ and strict mode unless a document says otherwise.

## Document Map

Read roughly in order; each builds on the previous.

- **[Language Fundamentals](01-language-fundamentals.md)** — types, values, coercion,
  equality, and `null`/`undefined`. The base every other doc assumes.
- **[Execution Context](02-execution-context.md)** — how the engine sets up each run:
  creation vs. execution phase, hoisting, and the temporal dead zone.
- **[Scope and Closures](03-scope-and-closures.md)** — lexical scope, the scope chain,
  and how closures capture variables (the source of most loop and callback bugs).
- **[Functions](04-functions.md)** — declarations vs. expressions vs. arrow functions,
  parameters, and higher-order functions.
- **[Objects and Prototypes](05-objects-and-prototypes.md)** — object creation, property
  descriptors, and the prototype chain that underlies inheritance and classes.

Beyond these fundamentals, sibling docs cover [classes](06-classes.md),
[modules](07-modules.md), [asynchronous JavaScript](08-asynchronous-javascript.md),
[the event loop](10-event-loop.md), [the `this` keyword](16-this-keyword.md),
[error handling](14-error-handling.md), and [common anti-patterns](100-common-antipatterns.md).

## Best Practices

- Start from Language Fundamentals when debugging unexpected values; most surprises are
  coercion or `null`/`undefined` issues, not framework bugs.
- Consult Scope and Closures before writing loops that create callbacks or timers.
- Consult the `this` and Functions docs before choosing between arrow and regular
  functions — the choice changes binding, not just syntax.
- Treat this overview as an index; do not copy rules from here — cite the specific doc.

## Common Mistakes

- Reaching for a framework explanation when the bug is a base-language mechanic (coercion,
  hoisting, closure capture) covered in these five docs.
- Reading only this overview and skipping the concept doc that actually states the rule.
- Assuming pre-ES2015 patterns still apply; this base targets modern JavaScript.

## AI Review Checklist

- Did you identify which fundamental doc governs the code under review?
- Does the code assume modern JavaScript (strict mode, `const`/`let`, ES modules)?
- Are the base mechanics — types, scope, `this`, prototypes — accounted for before
  blaming a library?

## Related

- `knowledge/javascript/01-language-fundamentals.md`
- `knowledge/javascript/02-execution-context.md`
- `knowledge/javascript/03-scope-and-closures.md`
- `knowledge/javascript/04-functions.md`
- `knowledge/javascript/05-objects-and-prototypes.md`
