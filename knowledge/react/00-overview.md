---
id: react/00-overview
topic: react
slug: overview
title: "React Overview"
type: doc
order: 0
status: ready
tags: [react, overview]
related: [react/01-react-philosophy, react/04-components, react/08-hooks, react/06-state, react/11-rendering]
when_to_use: "Read first when starting any React work, to find which doc in this topic answers your question."
---
# React Overview

## Purpose

This document orients an agent to the React knowledge base. React is a library for
building user interfaces out of composable, declarative components. This topic teaches
how to write React that renders correctly, updates predictably, and performs well —
without the subtle bugs that come from misunderstanding rendering, state, and effects.

Use this page as a map. It tells you which sibling document owns each concern so you
read the right rules before writing or reviewing code.

## Why It Matters

React's mental model is small but unforgiving. The same code can be "correct" JavaScript
and still be wrong React: a state mutation that never re-renders, an effect that fires
twice, a key that reuses the wrong DOM node. These bugs pass code review because they
look reasonable — they only surface as flicker, stale data, or lost input under real use.
Getting the core model right (components, props, state, rendering, effects) prevents an
entire class of defects that are hard to reproduce and expensive to debug in production.

## Core Principles

- **UI is a function of state.** You describe what the UI should look like for the
  current state; React figures out the DOM changes. Never mutate the DOM directly.
- **Data flows down, events flow up.** Parents pass data via props; children request
  changes via callbacks. One-way flow makes behavior traceable.
- **Rendering must be pure.** A component, given the same props and state, must return
  the same output and cause no side effects during render. Side effects belong in events
  or effects.
- **State is minimal and derived where possible.** Store the smallest source of truth;
  compute the rest during render instead of duplicating it into more state.

## The Documents in This Topic

- **Foundations** — [react philosophy](01-react-philosophy.md),
  [component architecture](02-component-architecture.md), [JSX](03-jsx.md).
  Read these to understand the model and the syntax.
- **Building blocks** — [components](04-components.md), [props](05-props.md),
  [state](06-state.md), [lifecycle](07-lifecycle.md). The core unit and its inputs.
- **Behavior** — [hooks](08-hooks.md), [custom hooks](09-custom-hooks.md),
  [context](10-context-api.md), [rendering](11-rendering.md),
  [performance](12-performance.md). How components remember, share, and update.
- **Composition & patterns** — [composition](13-component-composition.md),
  [patterns](14-patterns.md), [design patterns](24-design-patterns.md).
- **Application concerns** — [forms](15-forms.md), [data fetching](16-data-fetching.md),
  [routing](17-routing.md), [state management](18-state-management.md),
  [error handling](19-error-handling.md), [accessibility](20-accessibility.md).
- **Engineering** — [testing](21-testing.md), [folder structure](22-folder-structure.md),
  [code style](23-code-style.md), [security](25-security.md),
  [best practices](26-best-practices.md), [debugging](27-debugging.md),
  [production](28-production.md), [tooling](29-tooling.md).
- **References** — [common anti-patterns](100-common-antipatterns.md),
  [production checklist](98-production-checklist.md),
  [AI review checklist](99-ai-review-checklist.md).

## Best Practices

- Start from the data: decide the minimal state, then render it. Do not start from the DOM.
- Prefer function components and hooks. Class components are legacy; do not write new ones.
- Keep components small and single-purpose. Extract when a component juggles unrelated
  concerns, because small components are easier to test and reuse.
- Reach for the specific doc before improvising. The rules here encode failure modes that
  are not obvious from the API surface alone.

## Common Mistakes

- Treating React like jQuery — imperatively poking the DOM instead of updating state.
- Copying props into state, then wondering why the copy goes stale.
- Adding state for values that can be computed from existing state or props.
- Reading a concept doc but skipping the rendering and effects rules, then shipping a
  double-fetch or an infinite render loop.

## AI Review Checklist

- Does the change keep UI as a pure function of props and state?
- Is data flowing down through props and up through callbacks, not sideways?
- Is new state the minimal source of truth, with derived values computed in render?
- Are function components and hooks used instead of new class components?
- Did you consult the topic-specific doc (state, hooks, rendering) for the concern touched?

## Related

- `knowledge/react/01-react-philosophy.md`
- `knowledge/react/04-components.md`
- `knowledge/react/06-state.md`
- `knowledge/react/08-hooks.md`
- `knowledge/react/11-rendering.md`
