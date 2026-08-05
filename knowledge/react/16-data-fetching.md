---
id: react/16-data-fetching
topic: react
slug: data-fetching
title: "React Data Fetching"
type: doc
order: 16
status: ready
tags: [react, data-fetching, UserProfile, useQuery, "@tanstack", getUser, QueryClient, useEffect]
related: [react/09-custom-hooks, react/19-error-handling, react/18-state-management, nextjs/09-data-fetching]
when_to_use: "Read before implementing or reviewing remote data fetching, caching, or synchronization in React."
---
# React Data Fetching

## Purpose

This document defines the engineering standards for fetching, caching, synchronizing, and updating remote data in React applications.

The objective is to build applications that efficiently communicate with backend services while remaining predictable, performant, and maintainable.

Remote data should be treated differently from local UI state.

---

## Core Principle

Server state is not client state.

Do not manage remote data using local component state unless there is a specific reason.

Prefer dedicated server state management solutions.

Bad (server state re-implemented by hand with `useState` + `useEffect`):

```tsx
function UserProfile({ userId }: { userId: string }) {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        setLoading(true);
        fetch(`/api/users/${userId}`)
            .then((res) => res.json())
            .then(setUser) // no cache, no dedup, no cancellation, races on userId change
            .catch(setError)
            .finally(() => setLoading(false));
    }, [userId]);

    if (loading) return <Spinner />;
    if (error) return <ErrorMessage error={error} />;
    return <Profile user={user!} />;
}
```

Good (server state owned by a cache; loading/error/caching/dedup are handled for you):

```tsx
import { useQuery } from "@tanstack/react-query";

function UserProfile({ userId }: { userId: string }) {
    const { data: user, isPending, isError, error } = useQuery({
        queryKey: ["user", userId],
        queryFn: ({ signal }) => getUser(userId, signal),
    });

    if (isPending) return <Spinner />;
    if (isError) return <ErrorMessage error={error} />;
    return <Profile user={user} />;
}
```

The manual version silently accumulates bugs: no request deduplication, no
cross-component sharing, no cache, and a race condition when `userId` changes
mid-flight. Treat that as a signal to reach for a server-state library.

---

## Server State vs Client State

Understand the difference.

## Client State

Examples:

- modal visibility;
- selected tab;
- input values;
- sidebar state;
- theme selection.

The application owns this data.

---

## Server State

Examples:

- users;
- products;
- orders;
- blog posts;
- notifications;
- API responses.

The server owns this data.

Treat server state as a synchronized cache rather than local state.

---

## Data Fetching Workflow

Every data request should follow this lifecycle.

```
Request
        ↓
Loading
        ↓
Success / Error
        ↓
Caching
        ↓
Synchronization
        ↓
Invalidation
        ↓
Refetch
```

---

## Preferred Libraries

For modern React applications, prefer dedicated server state libraries.

Recommended:

- TanStack Query
- SWR

Avoid building custom caching solutions unless the project has specific requirements.

Configure a single `QueryClient` at the application root. Set sensible cache
defaults once instead of per-query.

```tsx
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            staleTime: 30_000, // data is "fresh" for 30s; no refetch within that window
            gcTime: 5 * 60_000, // unused cache entries are collected after 5 min (v5 name)
            retry: 2,
            refetchOnWindowFocus: true,
        },
    },
});

export function App() {
    return (
        <QueryClientProvider client={queryClient}>
            <Routes />
        </QueryClientProvider>
    );
}
```

Note the v5 naming: `gcTime` replaced the old `cacheTime`, and the loading flag
is `isPending` (not `isLoading`, which now means "pending and actively
fetching"). SWR exposes the same ideas through `useSWR(key, fetcher)`.

---

## Fetching Strategy

Data should be fetched:

- when required;
- as late as practical;
- as early as beneficial for user experience.

Avoid unnecessary requests.

---

## Loading States

Every request should expose explicit loading states.

Typical states:

- idle;
- loading;
- success;
- error.

Users should always understand what is happening.

Two common strategies:

- render-as-you-fetch with explicit flags (`isPending` / `isError` from a query
  hook), shown in the examples above;
- Suspense with React 19's `use()`, which reads a promise and lets a parent
  `<Suspense>` boundary render the fallback.

```tsx
import { Suspense, use } from "react";

// The promise must be created outside render (or memoized) so it is stable
// across re-renders — never call fetch() directly in the render body.
function Profile({ userPromise }: { userPromise: Promise<User> }) {
    const user = use(userPromise); // suspends until the promise resolves
    return <h1>{user.name}</h1>;
}

function Page({ userPromise }: { userPromise: Promise<User> }) {
    return (
        <Suspense fallback={<Spinner />}>
            <Profile userPromise={userPromise} />
        </Suspense>
    );
}
```

Combine Suspense with an error boundary so rejected promises render a fallback
instead of crashing the tree. `use()` does not replace a caching library —
without one you still need to keep the promise stable and handle invalidation
yourself.

---

## Error Handling

Every request should define an error strategy.

Examples:

- retry;
- fallback UI;
- error message;
- logging.

Never ignore failed requests.

---

## Caching

Reuse previously fetched data whenever appropriate.

Benefits:

- improved performance;
- reduced network usage;
- faster navigation;
- better user experience.

Caching should be automatic whenever possible.

---

## Cache Invalidation

Data should be refreshed when it becomes stale.

Common triggers:

- mutation;
- manual refresh;
- window focus;
- reconnect;
- scheduled refresh.

Do not invalidate more data than necessary.

Invalidation is key-scoped. Passing a query-key prefix invalidates every query
whose key starts with it, so structure keys hierarchically.

```tsx
const queryClient = useQueryClient();

// Invalidate one list — refetches only the todos list, not unrelated caches.
await queryClient.invalidateQueries({ queryKey: ["todos"] });

// Invalidate a single entity by its full key.
await queryClient.invalidateQueries({ queryKey: ["todo", todoId] });
```

Bad (nuking the entire cache after one write forces every screen to refetch):

```tsx
queryClient.invalidateQueries(); // no key: invalidates everything
```

---

## Background Refetching

Prefer background synchronization when appropriate.

Benefits:

- fresh data;
- minimal UI interruption;
- better perceived performance.

Avoid unnecessary loading indicators during silent updates.

---

## Mutations

Mutations change server state.

Examples:

- create;
- update;
- delete;
- upload.

Every mutation should define:

- loading state;
- success handling;
- error handling;
- cache invalidation.

With TanStack Query, `useMutation` bundles all four. Invalidate the affected
queries in `onSuccess` so the UI reflects the new server state.

```tsx
import { useMutation, useQueryClient } from "@tanstack/react-query";

function AddTodo() {
    const queryClient = useQueryClient();

    const { mutate, isPending, isError, error } = useMutation({
        mutationFn: (title: string) => createTodo(title),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["todos"] });
        },
    });

    return (
        <form
            onSubmit={(e) => {
                e.preventDefault();
                const title = new FormData(e.currentTarget).get("title") as string;
                mutate(title);
            }}
        >
            <input name="title" />
            <button type="submit" disabled={isPending}>
                {isPending ? "Adding…" : "Add"}
            </button>
            {isError && <p role="alert">{error.message}</p>}
        </form>
    );
}
```

In React 19 you can also drive a mutation with a form Action and
`useActionState`, which manages the pending flag and the returned result for
you. Pair it with `useQueryClient` when you need to invalidate the cache.

```tsx
import { useActionState } from "react";

function AddTodoAction() {
    const [error, submitAction, isPending] = useActionState(
        async (_prev: string | null, formData: FormData) => {
            const title = formData.get("title") as string;
            try {
                await createTodo(title);
                return null; // success: clear any prior error
            } catch (err) {
                return (err as Error).message; // becomes the next `error` value
            }
        },
        null,
    );

    return (
        <form action={submitAction}>
            <input name="title" />
            <button type="submit" disabled={isPending}>Add</button>
            {error && <p role="alert">{error}</p>}
        </form>
    );
}
```

---

## Optimistic Updates

Use optimistic updates only when:

- failures are uncommon;
- rollback is possible;
- user experience benefits.

Every optimistic update must support rollback.

With TanStack Query, snapshot the cache in `onMutate`, apply the optimistic
change, and restore the snapshot in `onError`. Always refetch in `onSettled` to
reconcile with the true server state.

```tsx
useMutation({
    mutationFn: toggleTodo,
    onMutate: async (updated) => {
        await queryClient.cancelQueries({ queryKey: ["todos"] });
        const previous = queryClient.getQueryData<Todo[]>(["todos"]);
        queryClient.setQueryData<Todo[]>(["todos"], (old = []) =>
            old.map((t) => (t.id === updated.id ? { ...t, done: updated.done } : t)),
        );
        return { previous }; // context handed to onError
    },
    onError: (_err, _updated, context) => {
        if (context?.previous) {
            queryClient.setQueryData(["todos"], context.previous); // rollback
        }
    },
    onSettled: () => {
        queryClient.invalidateQueries({ queryKey: ["todos"] });
    },
});
```

React 19's `useOptimistic` handles the transient UI state for a single Action.
The optimistic value is shown while the Action is pending and automatically
reverts to the real state if the Action throws — no manual rollback code.

```tsx
import { useOptimistic } from "react";

function TodoItem({ todo, save }: { todo: Todo; save: (done: boolean) => Promise<void> }) {
    const [optimisticDone, setOptimisticDone] = useOptimistic(todo.done);

    async function toggle(formData: FormData) {
        const next = formData.get("done") === "on";
        setOptimisticDone(next); // instant UI update
        await save(next); // if this rejects, React reverts optimisticDone
    }

    return (
        <form action={toggle}>
            <input type="checkbox" name="done" defaultChecked={optimisticDone} />
            <span style={{ opacity: optimisticDone !== todo.done ? 0.5 : 1 }}>
                {todo.title}
            </span>
        </form>
    );
}
```

---

## Request Deduplication

Avoid duplicate requests for identical resources.

Review:

- multiple components requesting the same data;
- repeated requests during navigation;
- unnecessary refetches.

The query key is the deduplication unit. Any number of components calling
`useUser("42")` share one in-flight request and one cache entry, because they
resolve to the same `["user", "42"]` key. Keep keys serializable and
deterministic; include every input that changes the result.

```tsx
// Same key everywhere → one network request, shared across the tree.
useQuery({ queryKey: ["user", id], queryFn: () => getUser(id) });
```

Bad (a new object identity or a non-deterministic value in the key defeats
dedup and caching):

```tsx
useQuery({ queryKey: ["user", { id, at: Date.now() }], queryFn: fetchUser });
```

---

## Pagination

Large datasets should support pagination or infinite loading.

Avoid requesting thousands of records at once.

Choose the strategy that best fits the product requirements.

For infinite lists, `useInfiniteQuery` tracks pages and cursors. Provide
`initialPageParam` and derive the next cursor with `getNextPageParam`.

```tsx
import { useInfiniteQuery } from "@tanstack/react-query";

function Feed() {
    const { data, fetchNextPage, hasNextPage, isFetchingNextPage } =
        useInfiniteQuery({
            queryKey: ["feed"],
            queryFn: ({ pageParam, signal }) => getFeed(pageParam, signal),
            initialPageParam: 0,
            getNextPageParam: (lastPage) => lastPage.nextCursor ?? undefined,
        });

    return (
        <>
            {data?.pages.flatMap((page) => page.items).map((item) => (
                <FeedRow key={item.id} item={item} />
            ))}
            {hasNextPage && (
                <button onClick={() => fetchNextPage()} disabled={isFetchingNextPage}>
                    {isFetchingNextPage ? "Loading…" : "Load more"}
                </button>
            )}
        </>
    );
}
```

Returning `undefined` from `getNextPageParam` tells the cache there are no more
pages, which flips `hasNextPage` to `false`.

---

## Filtering and Sorting

Filtering should be performed:

- on the server for large datasets;
- on the client only when the complete dataset is already available.

Avoid transferring unnecessary data.

---

## API Layer

Keep API communication separate from presentation.

Example:

```
Component
        ↓
Custom Hook
        ↓
API Client
        ↓
Backend
```

Components should not know implementation details of HTTP requests.

The API client owns transport concerns (base URL, headers, status handling,
JSON parsing). The custom hook owns cache keys and query configuration. The
component owns rendering.

```tsx
// api/users.ts — transport layer, framework-agnostic
async function request<T>(path: string, signal?: AbortSignal): Promise<T> {
    const res = await fetch(`/api${path}`, { signal });
    if (!res.ok) {
        throw new Error(`Request failed: ${res.status} ${res.statusText}`);
    }
    return res.json() as Promise<T>;
}

export function getUser(id: string, signal?: AbortSignal) {
    return request<User>(`/users/${id}`, signal);
}

// hooks/useUser.ts — cache layer
import { useQuery } from "@tanstack/react-query";

export function useUser(id: string) {
    return useQuery({
        queryKey: ["user", id],
        queryFn: ({ signal }) => getUser(id, signal),
    });
}

// components/UserCard.tsx — presentation only
function UserCard({ id }: { id: string }) {
    const { data, isPending, isError } = useUser(id);
    if (isPending) return <Spinner />;
    if (isError) return <ErrorMessage />;
    return <Profile user={data} />;
}
```

---

## Cancellation

Long-running requests should support cancellation when appropriate.

Examples:

- page navigation;
- search input;
- component unmount.

Avoid updating state after a request is no longer relevant.

TanStack Query passes an `AbortSignal` into every `queryFn`; forward it to
`fetch` and stale requests are cancelled automatically when the key changes or
the component unmounts.

```tsx
useQuery({
    queryKey: ["search", term],
    queryFn: ({ signal }) => request(`/search?q=${term}`, signal),
});
```

If you must fetch inside `useEffect` (for example, without a query library),
wire cancellation manually and ignore aborted results.

```tsx
useEffect(() => {
    const controller = new AbortController();

    fetch(`/api/search?q=${term}`, { signal: controller.signal })
        .then((res) => res.json())
        .then(setResults)
        .catch((err) => {
            if (err.name !== "AbortError") setError(err); // ignore intentional aborts
        });

    return () => controller.abort(); // cancel on unmount / term change
}, [term]);
```

---

## Authentication

Authenticated requests should:

- use centralized authentication;
- refresh tokens when required;
- handle unauthorized responses consistently.

Authentication logic should not be duplicated across components.

---

## Performance

Review:

- request frequency;
- payload size;
- duplicate requests;
- cache hit rate;
- unnecessary refetching.

Network performance is often more important than rendering performance.

---

## Accessibility

Loading and error states should be accessible.

Verify:

- loading indicators;
- status announcements;
- retry actions;
- focus management after updates.

Users should always understand the result of asynchronous operations.

---

## AI Execution Checklist

## Investigation

☐ Identify server state.

☐ Review existing API layer.

☐ Review caching strategy.

☐ Review loading and error states.

---

## Planning

☐ Select data fetching strategy.

☐ Define cache behavior.

☐ Define invalidation strategy.

☐ Define mutation workflow.

---

## Verification

☐ Server state separated from UI state.

☐ Loading states implemented.

☐ Errors handled.

☐ Cache behaves correctly.

☐ Duplicate requests avoided.

☐ Accessibility preserved.

---

## Examples

**Good Example** — a cache-aware client, with every state rendered

```tsx
export function UserProfile({ userId }: { userId: string }) {
  const { data, status, error, refetch } = useQuery({
    queryKey: ['user', userId],           // the key IS the cache identity
    queryFn: ({ signal }) => fetchUser(userId, signal),   // cancelled on unmount
    staleTime: 60_000,
  });

  if (status === 'pending') return <ProfileSkeleton />;
  if (status === 'error') return <ErrorState error={error} onRetry={refetch} />;

  return <Profile user={data} />;
}
```

```ts
// The fetcher throws on a non-2xx, so the error state is actually reachable.
export async function fetchUser(id: string, signal?: AbortSignal): Promise<User> {
  const res = await fetch(`/api/users/${id}`, { signal });
  if (!res.ok) {
    throw new HttpError(res.status, `Failed to load user ${id}`);
  }
  return res.json();
}
```

**Bad Example** — a hand-rolled effect with a race and no error path

```tsx
export function UserProfile({ userId }: { userId: string }) {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    // No cleanup and no AbortController: navigating from user A to user B can
    // land A's response last, showing the wrong profile.
    fetch(`/api/users/${userId}`)
      .then((r) => r.json())      // a 500 body parses fine and yields garbage
      .then(setUser);
  }, [userId]);

  // "Loading" and "failed" are indistinguishable: a failed request shows this
  // spinner forever, and nothing reports the error.
  if (!user) return <Spinner />;

  return <Profile user={user} />;
}
```

Fetching inside a child that is rendered after its parent's own request resolves creates a
waterfall — start independent requests together, or move the fetch to the route.

---

## Common Mistakes

Avoid:

Using `useEffect` for every request.

Managing server state with `useState`.

Ignoring caching.

Ignoring request cancellation.

Duplicating API calls.

Refetching excessively.

Mixing API logic with UI components.

Ignoring loading and error states.

---

## Completion Criteria

Data fetching is complete when:

- server state is managed separately from UI state;
- loading, success, and error states are implemented;
- caching and invalidation are defined;
- mutations are handled consistently;
- duplicate requests have been minimized;
- accessibility requirements have been satisfied.

---

## Summary

Effective data fetching is built on clear separation between server state and client state.

By using dedicated server state management, consistent caching strategies, and predictable request lifecycles, React applications become faster, more reliable, and easier to maintain as they scale.

## Related

- `knowledge/react/09-custom-hooks.md`
- `knowledge/react/19-error-handling.md`
- `knowledge/react/18-state-management.md`
- `knowledge/nextjs/09-data-fetching.md`
