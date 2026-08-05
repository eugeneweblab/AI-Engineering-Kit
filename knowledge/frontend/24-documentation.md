---
id: frontend/24-documentation
topic: frontend
slug: documentation
title: "Documentation"
type: doc
order: 24
status: ready
tags: [frontend, documentation]
related: [frontend/03-design-systems, frontend/02-component-driven-development, frontend/25-folder-structure, frontend/27-best-practices, frontend/22-testing]
when_to_use: "Read before adding, reviewing, or restructuring docs for a component, package, or frontend app."
---
# Documentation

## Purpose

This document defines how to document a frontend codebase so that a new engineer —
or an AI agent — can find, understand, and safely change code without reading every
file. It covers component docs, READMEs, prop/type contracts, ADRs, and living
examples. The goal is documentation that stays true because it is generated from or
verified against the code, not prose that rots the day after it is written.

## Why It Matters

Frontend code is read far more than it is written, and the reader is usually deciding
whether a component is safe to reuse. Missing or stale docs push that reader to guess:
they copy a component, misuse a prop, or rebuild something that already exists. The
cost is duplication, inconsistent UI, and bugs that ship because nobody knew the
contract. Good documentation is the interface between people; when it is wrong, every
downstream decision is wrong too. Because docs drift silently, the only durable
documentation is the kind the build can check.

## Core Principles

- **Document the contract, not the implementation.** Describe what a component accepts,
  emits, and guarantees. Implementation details change; the public contract is the
  promise consumers rely on.
- **Co-locate docs with code.** A component's README, stories, and prop types live next
  to the component. Distant docs drift because nobody remembers they exist.
- **Make examples executable.** A runnable story or example is verified by CI; a
  copy-pasted snippet in a wiki is fiction the moment the API changes.
- **Types are documentation.** A precise prop type or interface tells the reader more,
  and never lies, because the compiler enforces it.
- **Write for the decision.** Documentation exists to answer "should I use this, and
  how?" — not to narrate the code line by line.

## Best Practices

- Give every shared component a doc block: purpose, when to use vs. alternatives, props
  table, and one canonical example. Generate the props table from types (e.g. Storybook
  autodocs, TypeDoc, react-docgen) so it cannot go stale.
- Use JSDoc/TSDoc on exported props and functions; describe *why* and constraints, not
  the obvious (`/** Max 40 chars; truncated with an ellipsis. */`), not (`/** the label */`).
- Keep a package/app README that answers: how to run, how to test, where things live,
  and the three things a newcomer always gets wrong. Link to deeper docs; do not inline
  them.
- Record non-obvious decisions as short ADRs (Architecture Decision Records): context,
  decision, consequences. One page. This is how future readers learn *why* the code is
  shaped this way.
- Prefer Storybook (or a live catalog) as the source of truth for UI. Each state —
  loading, empty, error, long text, RTL — is a story, so the docs double as visual and
  interaction tests.
- Document accessibility expectations inline: expected roles, keyboard behavior, and
  ARIA contracts belong in the component doc, not tribal knowledge.
- Delete docs that describe removed code in the same PR. A wrong doc is worse than none.

## Examples

**Good Example** — self-verifying contract via types + a runnable story

```tsx
/**
 * Primary call-to-action. Use for the single most important action on a view.
 * For secondary actions use <Button variant="ghost">. Do not nest inside links.
 */
export interface ButtonProps {
  /** Visible label. Keep under 3 words; the button is not a paragraph. */
  children: React.ReactNode;
  /** Disables interaction AND sets aria-disabled so AT announces it. */
  disabled?: boolean;
  onClick?: () => void;
}

// Button.stories.tsx — CI renders every state, so the "docs" cannot drift.
export const Disabled: Story = { args: { children: "Save", disabled: true } };
```

**Bad Example** — prose that lies the moment the code changes

```tsx
// README.md, hand-maintained, 200 lines away from the component:
// "Button takes a `label` string and an optional `color` prop (red | blue)."
//
// The actual component below no longer matches — the doc is now actively misleading.
export function Button({ children, variant }: ButtonProps) { /* ... */ }
```

## Common Mistakes

- Hand-writing a props table that duplicates the type definition — it silently diverges.
- README that explains architecture but not how to run or test the project.
- Documenting internals (private helpers, state shape) that consumers must not depend on.
- Screenshots in docs instead of live stories — they never update and hide broken states.
- Leaving `TODO`/`FIXME` as the only record of a known limitation instead of an ADR.
- One giant `docs/` folder disconnected from code, so nobody trusts or updates it.

## Production Tips

- Wire doc generation (Storybook build, TypeDoc) into CI and publish it per commit so
  the catalog always matches `main`.
- Add a link-checker to CI; broken internal links are the first sign of doc rot.
- Treat the component catalog as an onboarding tool and a design-review surface — it is
  where design and engineering agree on truth.

## AI Review Checklist

- Does every exported/shared component have a purpose line and a canonical example?
- Are props documented via types (auto-generated table), not a hand-maintained list?
- Do docs describe the contract (inputs/outputs/guarantees), not private internals?
- Are examples runnable stories that CI verifies, not static snippets?
- Were docs for changed or removed code updated in the same PR?
- Are non-obvious decisions captured as short ADRs with context and consequences?

## Related


- `knowledge/frontend/03-design-systems.md`
- `knowledge/frontend/02-component-driven-development.md`
- `knowledge/frontend/25-folder-structure.md`
- `knowledge/frontend/27-best-practices.md`
- `knowledge/frontend/22-testing.md`
