---
id: frontend/100-common-antipatterns
topic: frontend
slug: common-antipatterns
title: "Frontend Common Antipatterns"
type: doc
order: 100
status: ready
tags: [frontend, common-antipatterns]
related: [frontend/30-engineering-principles, frontend/04-state-management, frontend/07-rendering, frontend/08-performance, frontend/09-accessibility]
when_to_use: "Read when reviewing or refactoring frontend code that feels slow, buggy, or hard to change — to name the smell and apply the fix."
---
# Frontend Common Antipatterns

## Purpose

This document catalogs the frontend antipatterns that recur across codebases and frameworks.
Each entry names the pattern, explains *why* it is wrong (the concrete failure it causes),
and gives the fix. It is written so an agent can recognize the smell in a diff and correct it
with a reason, not just a preference.

## Why It Matters

These patterns are attractive because they work in the demo. The bug they cause appears later
— under a slow network, on a real device, after the tenth feature — when it is expensive to
trace and risky to change. Naming them turns a vague "this feels wrong" into a specific,
fixable defect, and gives the fix a justification that survives review.

## The Antipatterns

### 1. Deriving state into `useState` + `useEffect`

**Why it is wrong:** Storing a value that can be computed from existing state creates a second
source of truth. The effect that syncs it runs *after* render, so there is always a frame
where the derived value is stale, and any missed dependency makes it wrong indefinitely.

**The fix:** Compute derived values inline during render. Reserve effects for synchronizing
with external systems (network, DOM, subscriptions), never for deriving one piece of state
from another.

```tsx
// Bad: fullName is a stored copy that can drift from first/last.
const [fullName, setFullName] = useState("");
useEffect(() => setFullName(`${first} ${last}`), [first, last]);

// Good: derived, always correct, no extra render.
const fullName = `${first} ${last}`;
```

### 2. Fetch-and-set in `useEffect` for server data

**Why it is wrong:** Hand-rolled fetching re-implements caching, deduplication, refetching,
and invalidation — badly. It produces waterfalls, races (a stale response overwriting a fresh
one), and missing loading/error states.

**The fix:** Use a server-state library (TanStack Query, SWR, RTK Query). It gives you
caching, request deduplication, background refetch, and typed loading/error states for free.

### 3. Array index as a list key

**Why it is wrong:** When the list reorders, inserts, or deletes, index keys make the
framework reuse the wrong DOM nodes. State bound to a row (input focus, checkbox, animation)
jumps to a different item, corrupting the UI silently.

**The fix:** Key on a stable identity from the data (`item.id`). Use the index only for
static, never-reordered lists.

### 4. Storing everything in a global store

**Why it is wrong:** Global state is shared mutable state. Putting a modal's open/closed flag
or a single form's draft in a global store makes every unrelated component a potential writer,
widens re-render scope, and turns local reasoning impossible.

**The fix:** Keep state at the lowest component that owns it; lift only to the nearest common
ancestor that needs it. Reserve global state for genuinely app-wide concerns (auth, theme).

### 5. `div` with an `onClick` instead of a `button`

**Why it is wrong:** A clickable `div` is invisible to keyboards and screen readers: no focus,
no Enter/Space activation, no role. You have shipped a control a large fraction of users
cannot operate, and it will pass a mouse-only demo.

**The fix:** Use the semantic element (`<button>`, `<a>`). It brings focus, keyboard
activation, and the correct role for free. Reach for ARIA only when no native element fits.

```tsx
// Bad: not focusable, not keyboard-operable, no role.
<div onClick={save}>Save</div>

// Good: focusable, Enter/Space work, announced as a button.
<button type="button" onClick={save}>Save</button>
```

### 6. Only building the happy path

**Why it is wrong:** In production, loading and error are the common case, not the exception.
A component that renders only on success shows a blank screen or a hung spinner the moment the
network is slow or the request fails — which is exactly when the user is watching.

**The fix:** Model every async read as loading | empty | error | success and render each state.
Design them before the happy path, and wrap subtrees in an error boundary for the unexpected.

### 7. Unescaped or unsanitized raw HTML

**Why it is wrong:** Passing user-controlled content to `dangerouslySetInnerHTML` or `v-html`
injects an XSS vector. An attacker's `<script>` runs with your origin's privileges and can
exfiltrate tokens and act as the user.

**The fix:** Render content as text so the framework escapes it. If raw HTML is truly required,
sanitize with a vetted library (DOMPurify) against an allowlist, never a hand-written regex.

### 8. Shipping one giant eager bundle

**Why it is wrong:** Every route's code loads on first visit, so time-to-interactive scales
with the whole app, not the page the user asked for. Parse and execution cost lands hardest on
the low-end devices that can least afford it.

**The fix:** Code-split at the route boundary and lazy-load interaction- and viewport-gated
chunks. Enforce a per-route bundle budget in CI so regressions fail the build.

### 9. Reflexive `useMemo`/`useCallback` everywhere

**Why it is wrong:** Memoization is not free — it costs memory and a dependency comparison
every render. Applied without a measured bottleneck, it adds complexity and can slow code down
while giving the illusion of optimization.

**The fix:** Write the straightforward version first, profile, and memoize only the specific
computations or referential identities that a profiler shows are expensive.

### 10. Layout shift from unsized media and late content

**Why it is wrong:** Images, ads, or async banners injected without reserved space push content
down after the user has started reading or aiming for a button, causing mis-taps and a poor CLS
score.

**The fix:** Reserve space up front: set `width`/`height` or `aspect-ratio` on media, and use
skeletons or fixed containers for content that arrives late.

### 11. Trusting the client for authorization

**Why it is wrong:** Hiding a button or filtering a list in the UI stops nobody — the API is
directly reachable with devtools or curl. Client checks are UX; treating them as security is a
hole.

**The fix:** Enforce every authorization and validation rule on the server. Use client-side
checks only to improve the experience, never as the enforcement point.

## AI Review Checklist

- Is any state stored that could be derived, then kept in sync with an effect?
- Is server data fetched with a caching library rather than raw `useEffect`?
- Do reorderable lists key on stable IDs instead of the array index?
- Is local state kept local, with global state reserved for app-wide concerns?
- Are interactive controls semantic elements, keyboard-operable and correctly announced?
- Does every async view render loading, empty, and error states?
- Is user-controlled HTML escaped or sanitized before it reaches the DOM?
- Is the app code-split and within its bundle budget?
- Is authorization enforced on the server, not just hidden in the UI?

## Related

- `knowledge/frontend/30-engineering-principles.md`
- `knowledge/frontend/04-state-management.md`
- `knowledge/frontend/07-rendering.md`
- `knowledge/frontend/08-performance.md`
- `knowledge/frontend/09-accessibility.md`
