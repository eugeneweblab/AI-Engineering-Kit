---
id: frontend/06-data-fetching
topic: frontend
slug: data-fetching
title: "Data Fetching"
type: doc
order: 6
status: ready
tags: [frontend, data-fetching, setState, useEffect, AbortController, setUser, reject, useUser]
related: [frontend/04-state-management, frontend/07-rendering, frontend/08-performance, frontend/13-error-handling, frontend/14-security]
when_to_use: "Read before writing any code that reads or mutates server data from the browser."
---
# Data Fetching

## Purpose

This document defines how the frontend talks to a server: reads, mutations, caching,
loading and error states, and race conditions. It is written so an agent can wire up
data flow without leaking secrets, shipping a waterfall, or rendering stale data as if
it were fresh.

Data fetching is *server state* management, and server state is fundamentally different
from local UI state (see [state management](04-state-management.md)): it is asynchronous,
shared, and can go stale the instant you receive it. Treat it as a cache of a remote
source of truth, never as data you own.

## Why It Matters

Fetching is where the frontend meets the network — the slowest, least reliable part of
the system. Naive code assumes requests are instant, succeed, and arrive in order; none
of that is true. The visible cost of getting it wrong is spinners that never resolve,
duplicate requests hammering the API, and — worst — the wrong response overwriting the
right one because two requests raced. The invisible cost is caching bugs that show one
user another user's data. Fetching code deserves the same rigor as the API it calls.

## Core Principles

- **Server state is a cache, not source of truth.** Model it with a caching library
  (TanStack Query, RSC, SWR), not hand-rolled `useEffect` + `useState`. The cost of
  DIY is that you re-implement caching, deduplication, and invalidation — badly.
- **Every request has three states, not one.** Loading, error, and success must all be
  designed. A UI that only handles success will hang or crash on the other two.
- **Cancel or ignore stale responses.** When inputs change, the previous request's
  response is garbage; discarding it prevents the race where slow-old overwrites fast-new.
- **Fetch on the server when you can.** Server-side fetching removes round trips, hides
  credentials, and ships less JavaScript. Reach for the client only for interactivity.
- **Never trust the client with secrets.** API keys and tokens belong on the server or in
  `HttpOnly` cookies — never in client bundles or `localStorage`.

## Best Practices

- Use a query library keyed by a stable, serializable **query key** so identical requests
  dedupe and share one cache entry. Invalidate by key after mutations.
- Set explicit **staleness** and **cache** windows. "Stale-while-revalidate" gives instant
  paint plus a background refresh; pick windows per resource, do not accept defaults blindly.
- Pass an `AbortController.signal` to `fetch` and abort on unmount or input change, so
  in-flight requests are cancelled instead of resolving into a dead component.
- **Parallelize independent requests** with `Promise.all`; never `await` them in sequence.
  Sequential awaits create a waterfall that adds every latency together.
- For lists you page or scroll, use cursor-based pagination and prefetch the next page on
  intent (hover, near-viewport) so navigation feels instant.
- On mutation, prefer **optimistic updates** with a rollback path: apply the change locally,
  fire the request, revert on failure. It hides latency without lying permanently.
- Validate and narrow responses at the boundary (e.g. Zod). The server can send anything;
  a runtime schema check turns a silent `undefined.map` crash into a handled error.
- Retry only **idempotent** reads, with backoff and a cap. Never blindly retry POSTs — you
  will double-charge or double-post.

## Examples

**Good Example** — cancellable, race-safe fetch with all three states

```tsx
function useUser(id: string) {
  const [state, setState] = useState<Result<User>>({ status: "loading" });

  useEffect(() => {
    const ctrl = new AbortController();
    setState({ status: "loading" });
    fetch(`/api/users/${id}`, { signal: ctrl.signal })
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(String(r.status)))))
      .then((data) => setState({ status: "success", data: UserSchema.parse(data) }))
      .catch((e) => {
        if (e.name !== "AbortError") setState({ status: "error", error: e }); // ignore cancels
      });
    return () => ctrl.abort(); // new id or unmount cancels the stale request
  }, [id]);

  return state; // caller must render loading / error / success — not just success
}
```

**Bad Example** — waterfall, race condition, no error state

```tsx
function Profile({ id }: { id: string }) {
  const [user, setUser] = useState<User>();
  const [posts, setPosts] = useState<Post[]>();

  useEffect(() => {
    // Sequential awaits: posts wait for user for no reason → latency stacks.
    (async () => {
      const u = await fetch(`/api/users/${id}`).then((r) => r.json());
      setUser(u);
      const p = await fetch(`/api/users/${id}/posts`).then((r) => r.json());
      setPosts(p); // no abort: if id changes, an old response can land last and win
    })();
  }, [id]); // no error handling → a 500 renders a permanent spinner

  return <div>{user?.name}</div>;
}
```

## Common Mistakes

- Hand-rolling fetch in `useEffect` and re-implementing caching, dedupe, and retries badly.
- Awaiting independent requests in sequence, creating a network waterfall.
- Not cancelling stale requests, so a slow old response overwrites a fresh new one.
- Rendering only the success state; loading and error hang or crash the UI.
- Putting API keys or bearer tokens in the client bundle or `localStorage`.
- Retrying non-idempotent mutations, causing duplicate writes.
- Trusting response shape without runtime validation, then crashing on missing fields.

## Production Tips

- Surface a global error boundary and a toast for unexpected fetch failures; never let a
  rejected promise vanish silently.
- Instrument request duration and error rate per endpoint (see [monitoring](23-monitoring.md));
  slow queries are invisible until measured.
- Debounce or throttle fetches driven by typing (search-as-you-type) to protect the API.
- Set sensible timeouts; a request with no timeout can hang a UI indefinitely.

## AI Review Checklist

- Is server state managed by a caching library rather than raw `useEffect` + `useState`?
- Are loading, error, and success states all handled for every request?
- Are stale/in-flight requests cancelled or ignored when inputs change?
- Are independent requests parallelized instead of awaited in sequence?
- Are secrets kept off the client, and responses validated at the boundary?
- Are retries limited to idempotent reads with backoff?
- Are mutations followed by cache invalidation of the affected query keys?

## Related

- `knowledge/frontend/04-state-management.md`
- `knowledge/frontend/07-rendering.md`
- `knowledge/frontend/08-performance.md`
- `knowledge/frontend/13-error-handling.md`
- `knowledge/frontend/14-security.md`
