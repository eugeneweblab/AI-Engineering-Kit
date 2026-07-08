---
id: frontend/28-ui-patterns
topic: frontend
slug: ui-patterns
title: "UI Patterns"
type: doc
order: 28
status: ready
tags: [frontend, ui-patterns]
related: [frontend/09-accessibility, frontend/12-forms, frontend/13-error-handling, frontend/03-design-systems, frontend/27-best-practices]
when_to_use: "Read before building a common UI surface — modal, form, list, async view, toast — to reuse the correct, accessible pattern."
---
# UI Patterns

## Purpose

This document catalogs the recurring interaction patterns every app needs — async data
views, forms, modals/overlays, lists, notifications, optimistic updates — and the
correct, accessible way to build each. The goal is that an agent reaches for a known-good
pattern instead of reinventing one that mishandles focus, loading, or errors.

## Why It Matters

The same surfaces appear in every product, and each has a well-known correct behavior and
a dozen tempting wrong ones. A modal that doesn't trap focus, a list that loses scroll
position, a form that submits twice, an async view with no error state — these are not
edge cases; they are the default outcome when a pattern is built from scratch under
deadline. Users feel the difference immediately, and accessibility and correctness bugs
here affect everyone. Codifying the patterns turns a recurring judgment call into a
reusable, reviewed decision.

## Core Principles

- **Every async surface has four states.** Loading, error, empty, and success. Design and
  build all four; the empty and error states are where trust is won or lost.
- **Overlays own focus.** Modals, dialogs, and menus must trap focus, restore it on close,
  close on `Escape`, and be labeled — otherwise keyboard and AT users are stranded.
- **Optimistic UI must be reversible.** Show the intended result immediately, but keep the
  ability to roll back and surface the error if the request fails.
- **Preserve the user's context.** Keep scroll position, selection, and input across
  re-renders and navigation. Losing it feels like the app fighting the user.
- **Feedback is immediate and proportional.** Every action gets a response within ~100ms
  (disabled button, spinner, optimistic change); destructive actions get confirmation and
  an undo path.

## Best Practices

- Model async views with an explicit status (`idle | loading | error | success`) or a
  data-fetching library (TanStack Query/SWR) that gives you these states plus caching,
  retries, and dedupe. Never infer state from "is the data null?".
- Disable the submit button while a form request is in flight and re-enable on completion,
  to prevent double submits. Show field-level validation errors tied to inputs via
  `aria-describedby`.
- Build dialogs on the native `<dialog>` element or a vetted primitive (Radix, React Aria)
  that handles focus trap, `Escape`, scroll lock, and labeling — do not hand-roll them.
- For long lists, virtualize (windowing) beyond a few hundred rows, and paginate or
  infinitely-scroll from the server. Keep a stable key so scroll and selection survive updates.
- Use a single toast/notification region with `role="status"` (polite) or `role="alert"`
  (assertive) so screen readers announce it; auto-dismiss non-critical toasts, keep errors
  until dismissed.
- For destructive actions, prefer an **undo** window over a confirm dialog where possible —
  it is faster for the common case and safer than a reflexive "OK".
- Debounce or throttle high-frequency inputs (search-as-you-type, resize) and cancel
  stale in-flight requests so a slow response can't overwrite a newer one.

## Examples

**Good Example** — explicit states + accessible dialog

```tsx
function Users() {
  const { data, status, error } = useQuery({ queryKey: ["users"], queryFn: fetchUsers });
  if (status === "pending") return <Spinner aria-label="Loading users" />;
  if (status === "error")   return <ErrorState error={error} onRetry={/* refetch */} />;
  if (data.length === 0)    return <EmptyState message="No users yet" />;
  return <UserList users={data} />; // all four states handled
}

// Native dialog: focus trap, Escape, and backdrop handled by the platform.
<dialog ref={ref} aria-labelledby="title">
  <h2 id="title">Delete project?</h2>
  <button onClick={() => ref.current?.close()}>Cancel</button>
</dialog>;
```

**Bad Example** — happy-path only, focus-broken overlay

```tsx
function Users() {
  const { data } = useQuery({ queryKey: ["users"], queryFn: fetchUsers });
  return <UserList users={data ?? []} />; // no loading/error/empty: blank flash, silent failures
}

// "Modal" that is just an absolutely positioned div:
<div className="modal">           {/* no focus trap: Tab escapes to the page behind */}
  <h2>Delete project?</h2>        {/* Escape does nothing; AT never announces it opened */}
  <button onClick={remove}>Delete</button>
</div>;
```

## Common Mistakes

- Rendering only success; a null/loading state flashes blank and errors vanish silently.
- Hand-built modals that leak focus, ignore `Escape`, and are invisible to screen readers.
- Submit buttons that stay enabled during a request, causing duplicate submissions.
- Optimistic updates with no rollback, so a failed request leaves the UI lying.
- Toasts injected as plain elements with no `role`, so AT users never hear them.
- Non-virtualized lists of thousands of rows that freeze the main thread.
- Search-as-you-type with no request cancellation, letting stale results overwrite fresh.

## Production Tips

- Put each pattern's states (loading/empty/error/long-content/RTL) in the component
  catalog as stories so they are visually reviewed and regression-tested.
- Standardize on one dialog, one toast, and one async-list primitive per app; divergence
  here is where accessibility bugs multiply.

## AI Review Checklist

- Does every async surface handle loading, error, empty, and success?
- Do overlays trap focus, restore it on close, respond to `Escape`, and carry a label?
- Are submit actions guarded against double submission while in flight?
- Do optimistic updates roll back and surface the error on failure?
- Are notifications announced to AT via an appropriate `role`?
- Are long lists virtualized/paginated, and stale requests cancelled?

## Related

- `knowledge/frontend/09-accessibility.md`
- `knowledge/frontend/12-forms.md`
- `knowledge/frontend/13-error-handling.md`
- `knowledge/frontend/03-design-systems.md`
- `knowledge/frontend/27-best-practices.md`
