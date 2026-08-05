---
id: react/23-code-style
topic: react
slug: code-style
title: "Code Style"
type: doc
order: 23
status: ready
tags: [react, code-style, PascalCase, onSelect, flag, eslint-plugin-react-hooks, handleClick]
related: [react/26-best-practices, react/22-folder-structure, react/29-tooling, react/30-engineering-principles, react/14-patterns]
when_to_use: "Read before writing or reviewing React components so naming, structure, and formatting stay consistent."
---
# Code Style

## Purpose

This document defines the code-style conventions for React components: naming,
file organization, prop typing, hook usage, JSX formatting, and what to let tooling
enforce. Its goal is consistency — code that reads the same regardless of who wrote it,
so reviewers spend attention on logic, not on style debates.

Style rules here are opinionated defaults, not moral claims. The value is agreement: pick
these, enforce them with tooling, and stop re-litigating. Deviate only with a reason.

## Why It Matters

Inconsistent style taxes every reader. When one file uses arrow functions and another
`function`, when props are typed here and `any` there, when imports are ordered randomly,
each file forces a fresh context switch. Multiply across a codebase and it slows every
review and onboarding. Most of this is mechanical and should be enforced by a formatter
and linter, not by humans — reserving human review for the decisions that actually matter.

## Core Principles

- **Let tooling own formatting.** Prettier for layout, ESLint for correctness (including
  `react-hooks/rules-of-hooks` and `exhaustive-deps`). Never hand-format or argue whitespace.
- **Name by role, not implementation.** Components are `PascalCase` nouns; hooks are
  `useX`; event handlers are `handleX`; booleans read as `isX`/`hasX`.
- **Type the boundaries.** Props and public hook returns are explicitly typed. `any`
  and unchecked casts are style violations, not conveniences.
- **One component per file, named after the file.** Predictable location beats clever grouping.
- **Prefer readable over clever.** Early returns over nested ternaries; named variables
  over inline logic buried in JSX.

## Best Practices

- Use **function declarations** for components (`function Button() {}`); they hoist and
  give clear stack-trace names. Reserve arrow functions for callbacks and tiny helpers.
- Destructure props in the signature with a typed shape, so the component's API is visible
  at a glance and unused props surface immediately.
- Order imports: external packages, then internal absolute imports, then relative — with a
  blank line between groups. Let the linter sort within groups.
- Keep JSX shallow. If a component's returned JSX exceeds ~50 lines or nests deeply,
  extract subcomponents. Deep JSX is a smell that a component does too much.
- Avoid inline object/array/function literals in props on hot paths only when they cause
  measured re-renders; do not obscure simple code chasing micro-optimizations.
- Name event handlers `handleClick`, and the prop that receives them `onClick` — the
  `on*`/`handle*` split makes data flow direction obvious.

## Examples

**Good Example** — typed props, declaration, early return, clear names

```tsx
type UserBadgeProps = {
  name: string;
  isOnline: boolean;
  onSelect: (name: string) => void;
};

// Function declaration: hoisted, named in stack traces.
// Props destructured + typed: the API is the signature.
function UserBadge({ name, isOnline, onSelect }: UserBadgeProps) {
  // Early return keeps the happy path unindented.
  if (!name) return null;

  const handleClick = () => onSelect(name); // handle* names the local handler

  return (
    <button onClick={handleClick} aria-pressed={isOnline}>
      {name} {isOnline ? "●" : "○"}
    </button>
  );
}
```

**Bad Example** — untyped, anonymous, nested ternary, unclear names

```tsx
// Anonymous arrow assigned to const: no hoisting, "Anonymous" in traces.
// Untyped props (`any`): no API contract, no autocomplete, no safety.
const badge = (props: any) => {
  return (
    <button
      onClick={() => props.cb(props.n)} // cb/n say nothing about intent
    >
      {/* Nested ternary in JSX: hard to read, hard to extend. */}
      {props.n ? (props.o ? props.n + " ●" : props.n + " ○") : "unknown"}
    </button>
  );
};
```

## Common Mistakes

- Typing props as `any` or omitting types, discarding the contract and autocomplete.
- Mixing arrow-const and `function` components with no convention across the codebase.
- Nesting ternaries inside JSX instead of using early returns or extracted variables.
- Vague names (`data`, `item`, `cb`, `flag`) where a role-based name would document intent.
- Hand-formatting and bikeshedding whitespace instead of running Prettier.
- Files with multiple components and mismatched names, so nothing is where you expect.

## Production Tips

- Enforce style in CI: `prettier --check`, `eslint --max-warnings=0`, and `tsc --noEmit`
  must pass before merge, so style never regresses through review fatigue.
- Add `eslint-plugin-react-hooks` and treat its warnings as errors — misused hooks are
  correctness bugs disguised as style.

## AI Review Checklist

- Are props and public hook returns explicitly typed, with no `any`?
- Are components `PascalCase` function declarations, one per file, matching the filename?
- Do handlers use `handleX` and their props use `onX`, and booleans read as `isX`/`hasX`?
- Is deep/long JSX broken into subcomponents, with early returns over nested ternaries?
- Are imports grouped and ordered consistently?
- Would Prettier, ESLint, and `tsc` all pass on this file with zero warnings?

## Related

- `knowledge/react/26-best-practices.md`
- `knowledge/react/22-folder-structure.md`
- `knowledge/react/29-tooling.md`
- `knowledge/react/30-engineering-principles.md`
- `knowledge/react/14-patterns.md`
