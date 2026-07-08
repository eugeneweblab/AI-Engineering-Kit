---
id: frontend/99-ai-review-checklist
topic: frontend
slug: ai-review-checklist
title: "AI Review Checklist"
type: doc
order: 99
status: ready
tags: [frontend, ai-review-checklist]
related: [frontend/30-engineering-principles, frontend/100-common-antipatterns, frontend/98-production-checklist, frontend/22-testing, frontend/27-best-practices]
when_to_use: "Read before reviewing a frontend diff or pull request; run each group against the changed code."
---
# AI Review Checklist

## Purpose

This is the checklist an agent runs when reviewing frontend code — a diff, a component, a
pull request. It targets the mistakes that pass typecheck and manual clicking but break under
real conditions: a slow network, a keyboard user, a re-render storm, an unescaped string.
Each item is a yes/no you can verify by reading the code; if you cannot confirm it, flag it.

## Why It Matters

Frontend bugs rarely throw at the reviewer. The build is green, the demo works, and the
defect only appears on a device you do not have or an input you did not try. Review is the
cheapest place to catch these — before they become a production incident with no stack trace.
A structured pass beats intuition because it forces you to check the states developers skip:
error paths, focus order, effect dependencies, and what the user actually downloads.

## State and Data

- [ ] Is every piece of state stored once, with derived values computed rather than stored and synced?
- [ ] Is server data managed by a caching layer, not hand-rolled `useEffect` fetch-and-set?
- [ ] Are async states modeled as a union, so `loading`, `error`, and `data` cannot contradict?
- [ ] Does every fetch handle loading, empty, and error, each with a usable UI?
- [ ] Are optimistic updates paired with a correct rollback on failure?
- [ ] Is state kept at the lowest common owner, not promoted to a global store by default?

## Rendering and Effects

- [ ] Is render pure — no fetches, mutations, or DOM writes during render?
- [ ] Do effects have complete, correct dependency arrays, with cleanup for subscriptions and timers?
- [ ] Is any effect actually a derivation that should be computed inline instead?
- [ ] Do list items use stable, data-derived keys — never the array index for reorderable lists?
- [ ] Are expensive computations memoized only where profiling shows a real cost, not reflexively?

## Performance

- [ ] Does the change stay within the route's bundle budget and avoid pulling in heavy dependencies?
- [ ] Is newly added heavy or below-the-fold code lazy-loaded rather than eagerly imported?
- [ ] Are new images responsive, correctly sized, and lazy-loaded where appropriate?
- [ ] Does the diff avoid patterns that cause layout shift (unsized media, late-injected content)?

## Accessibility

- [ ] Are semantic elements used (`button`, `a`, `nav`, `label`) instead of `div`s with click handlers?
- [ ] Is every interactive element keyboard-operable with a visible focus indicator?
- [ ] Do form inputs have associated labels and programmatically linked error messages?
- [ ] Is ARIA correct and minimal — added only where native semantics fall short?
- [ ] Do new colors meet WCAG AA contrast, and does motion respect `prefers-reduced-motion`?

## Security

- [ ] Is all user-controlled content escaped, with any raw-HTML injection sanitized?
- [ ] Are secrets and tokens kept out of the client bundle and out of `localStorage`?
- [ ] Are client-side checks treated as UX only, with authorization enforced on the server?
- [ ] Do external links carry `rel="noopener noreferrer"`?

## Testing and Resilience

- [ ] Are the failure and empty paths tested, not just the happy path?
- [ ] Do tests assert on user-visible behavior and roles, not implementation details?
- [ ] Is the feature wrapped in an error boundary so a crash is contained?

## Related

- `knowledge/frontend/30-engineering-principles.md`
- `knowledge/frontend/100-common-antipatterns.md`
- `knowledge/frontend/98-production-checklist.md`
- `knowledge/frontend/22-testing.md`
- `knowledge/frontend/27-best-practices.md`
