---
id: react/30-engineering-principles
topic: react
slug: engineering-principles
title: "Engineering Principles"
type: doc
order: 30
status: ready
tags: [react, engineering-principles]
related: [react/13-component-composition, react/26-best-practices, react/24-design-patterns, react/02-component-architecture, react/09-custom-hooks]
when_to_use: "Read when making design decisions about component structure, boundaries, or where logic belongs."
---
# Engineering Principles

## Purpose

This document states the durable engineering principles behind good React code — the
reasoning that outlives any specific API. Hooks change, frameworks change, but
composition over inheritance, single responsibility, and one-way data flow do not.
Where the other docs give rules, this one gives the *why* those rules share, so an
agent can make sound judgments on situations no rule anticipated.

These principles are how you decide the questions no checklist covers: where does this
logic belong, how should these components split, how much abstraction is enough.

## Why It Matters

Rules cover known cases; principles cover the rest. An agent that only pattern-matches
rules will make locally-correct choices that add up to an unmaintainable codebase —
prop-drilling ten levels, a 600-line component, state duplicated everywhere. Principles
give a consistent basis for trade-offs, so independent decisions compose into a coherent
system. They also tell you when to *break* a rule: a rule followed against its own
principle is cargo-culting.

## Core Principles

- **Composition over inheritance.** Build UIs by combining small components and passing
  `children`/render props — React has no class-inheritance story and doesn't need one.
  Composition keeps pieces independent and reusable. See [composition](13-component-composition.md).
- **Single responsibility.** A component renders one thing or coordinates one concern.
  When it does two, split it — the seam is usually already visible in the JSX.
- **One-way data flow.** Data flows down through props; changes flow up through
  callbacks. Predictable flow makes state traceable to a single owner.
- **Separate what from how.** Keep business logic and data-fetching in
  [custom hooks](09-custom-hooks.md); keep components focused on presentation. Each side
  is then testable and replaceable on its own.
- **Least abstraction that works.** Add an abstraction when duplication has proven a
  pattern (rule of three), not in anticipation. Wrong abstractions cost more than
  duplication because everything depends on them.

## Best Practices

- Prefer many small, single-purpose components over few large ones; small components are
  easier to test, reuse, and reason about. See [architecture](02-component-architecture.md).
- Push state down to the component that uses it and lift it only when sharing demands;
  this minimizes the blast radius of a change. See [best practices](26-best-practices.md).
- Extract logic to a custom hook when it has state or effects and is reused, or when it
  clutters a component's presentation.
- Design component APIs (props) for the caller's intent, not your internal structure —
  a good prop name describes *what*, not *how*.
- Make the common case simple and the complex case possible; sensible defaults with
  escape hatches beat a config object with twenty required fields. See [patterns](24-design-patterns.md).
- Optimize for readability first; you write a component once and read it many times.

## Examples

**Good Example** — logic in a hook, presentation composed and single-purpose

```tsx
// "How": data + logic, testable without a DOM.
function useSortedUsers(users: User[]) {
  return useMemo(() => [...users].sort((a, b) => a.name.localeCompare(b.name)), [users]);
}

// "What": pure presentation, one responsibility, composes children.
function UserList({ users }: { users: User[] }) {
  const sorted = useSortedUsers(users);
  return (
    <List>
      {sorted.map((u) => <UserRow key={u.id} user={u} />)}
    </List>
  );
}
```

**Bad Example** — one component owns fetching, sorting, and rendering

```tsx
function UserList() {
  const [users, setUsers] = useState<User[]>([]);
  useEffect(() => { fetch("/api/users").then(r => r.json()).then(setUsers); }, []);

  // Fetching + sorting + row markup + empty/error handling all inline here.
  // Nothing is reusable or unit-testable; the component grows without bound.
  const sorted = [...users].sort((a, b) => a.name.localeCompare(b.name));
  return (
    <ul>
      {sorted.map((u, i) => <li key={i}>{u.name}</li>)} {/* index key, too */}
    </ul>
  );
}
```

## Common Mistakes

- God components that fetch, transform, and render, growing past comprehension.
- Reaching for inheritance or HOC towers where composition with `children` is simpler.
- Abstracting after the first duplication, locking in the wrong shape too early.
- Prop-drilling deeply instead of composing or using context at the right level.
- Designing props around internal implementation rather than caller intent.
- Optimizing for cleverness over the next reader's comprehension.

## AI Review Checklist

- Does each component have a single, nameable responsibility?
- Is business/data logic in hooks, separated from presentation?
- Does data flow down via props and up via callbacks, with one clear owner?
- Is composition used in place of inheritance or unnecessary HOCs?
- Is each abstraction justified by proven duplication, not speculation?
- Do prop names describe caller intent rather than internal structure?

## Related

- `knowledge/react/13-component-composition.md`
- `knowledge/react/26-best-practices.md`
- `knowledge/react/24-design-patterns.md`
- `knowledge/react/02-component-architecture.md`
- `knowledge/react/09-custom-hooks.md`
