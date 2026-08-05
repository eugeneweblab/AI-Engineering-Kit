---
id: javascript/23-clean-code
topic: javascript
slug: clean-code
title: "JavaScript Clean Code"
type: doc
order: 23
status: ready
tags: [javascript, clean-code]
related: [javascript/21-functional-programming, javascript/22-design-patterns, javascript/14-error-handling, javascript/28-best-practices, javascript/30-engineering-principles]
when_to_use: "Read before writing or reviewing everyday JavaScript for naming, function size, and readability."
---
# JavaScript Clean Code

## Purpose

This document defines the everyday habits that make JavaScript readable and maintainable:
meaningful naming, small single-purpose functions, clear control flow, honest error
handling, and consistent modern syntax. It is the baseline every other JavaScript doc
assumes.

Clean code is code optimized for the *reader*, not the writer. Code is read far more often
than it is written, so the standard is: could a competent engineer understand this on the
first pass, without you in the room to explain it?

## Why It Matters

Unclear code isn't a style preference — it's a defect multiplier. Ambiguous names, sprawling
functions, and deep nesting hide bugs, slow every future change, and make review
ineffective because the reviewer can't hold the logic in their head. JavaScript makes
messiness cheap: dynamic typing, implicit coercion, and `var` hoisting let sloppy code run
until it fails in production. Clean-code discipline is how you keep the language's
flexibility from becoming a liability. The payoff compounds: each clear function makes the
next change safer and faster.

## Core Principles

- **Names reveal intent.** A reader should understand a variable or function from its name
  alone, without tracing its implementation. `activeUsers`, not `data` or `arr`.
- **One function, one job.** A function should do a single thing at a single level of
  abstraction. If you need "and" to describe it, split it.
- **Small and shallow.** Keep functions short and nesting flat; guard clauses and early
  returns beat pyramids of `if`.
- **Say what, not how, at the call site.** High-level functions read like prose; details
  live one level down.
- **No surprises.** A function's name and signature should tell the whole truth — no
  hidden side effects, no silent mutation of arguments.
- **Delete dead weight.** Remove commented-out code, unused variables, and redundant
  comments; version control remembers history, the file shouldn't.
- **Comments explain *why*, not *what*.** Good code shows what it does; comments justify
  non-obvious decisions.

## Best Practices

- Use `const` by default, `let` when reassignment is genuinely needed, never `var`
  (function-scoped hoisting causes subtle bugs).
- Name booleans and functions as predicates/verbs: `isValid`, `hasAccess`, `fetchUser`.
  Avoid negatives-of-negatives like `isNotDisabled`.
- Replace magic numbers/strings with named constants explaining their meaning.
- Prefer early returns (guard clauses) to reduce nesting; handle the error/edge case
  first, then the happy path unindented.
- Keep parameter lists short (roughly ≤3); pass an options object for more, so call sites
  are self-documenting via keys.
- Use `===`/`!==` always; rely on explicit conversions, not implicit coercion, to avoid
  the well-known `==` surprises.
- Fail loudly: throw `Error` objects (never strings), and don't swallow errors in empty
  `catch` blocks. See error-handling for detail.
- Keep formatting automatic (Prettier) and lint (ESLint) in CI so style is never a review
  topic — reviewers spend attention on logic.

## Examples

**Good Example** — intent-revealing names, guard clauses, single purpose

```js
const MAX_LOGIN_ATTEMPTS = 5; // named: the "5" now explains itself

function authenticate(user, attempt) {
  // Guard clauses: handle the exceptional cases first, unindent the happy path.
  if (!user) throw new Error("User not found");
  if (user.lockedUntil > Date.now()) throw new Error("Account locked");
  if (user.attempts >= MAX_LOGIN_ATTEMPTS) throw new Error("Too many attempts");

  return verifyPassword(user, attempt); // one job; details live in verifyPassword
}
```

**Bad Example** — vague names, deep nesting, hidden mutation, magic values

```js
function proc(u, a) {                    // "proc"/"u"/"a" reveal nothing
  var r;                                 // var: function-scoped, hoisted surprise
  if (u) {                               // arrow of nesting instead of guard clauses
    if (u.lu < Date.now()) {
      if (u.att < 5) {                   // magic 5; also mutates the argument below
        u.att++;                         // side effect hidden inside a "check"
        if (u.pw == a) { r = true; }     // == coercion; silent on type mismatch
      }
    }
  }
  return r;                              // may be undefined — caller can't tell why it failed
}
```

## Common Mistakes

- One-letter or generic names (`d`, `data`, `temp`, `handle`) that force readers into the
  implementation to understand meaning.
- Functions that do several things, forcing the reader to track multiple concerns at once.
- Deep `if` nesting where guard clauses would flatten the flow.
- Magic numbers and strings scattered inline instead of named constants.
- `var` and `==`, reintroducing hoisting and coercion bugs the modern syntax avoids.
- Empty `catch {}` blocks that hide failures, or returning `undefined`/`null` where an
  error should be thrown.
- Commented-out code and comments that restate what the code plainly does.

## Production Tips

- Enforce the baseline mechanically: ESLint (with a strict config) + Prettier in a
  pre-commit hook and CI, so humans never argue formatting in review.
- Prefer `type`/`interface` (TypeScript) or JSDoc on public functions so signatures are
  self-documenting and misuse is caught before runtime.
- When a function grows past a screen or its name needs "and", that's the refactor
  signal — extract before it calcifies.

## AI Review Checklist

- Do names reveal intent without reading the implementation?
- Does each function do exactly one thing at one level of abstraction?
- Are guard clauses used to keep nesting shallow?
- Are magic numbers/strings replaced by named constants?
- Is `const`/`let` used (never `var`) and `===` used (never `==`)?
- Are errors thrown as `Error` objects and never silently swallowed?
- Is there no commented-out or dead code left in the file?

## Related

- `knowledge/javascript/21-functional-programming.md`
- `knowledge/javascript/22-design-patterns.md`
- `knowledge/javascript/14-error-handling.md`
- `knowledge/javascript/28-best-practices.md`
- `knowledge/javascript/30-engineering-principles.md`
