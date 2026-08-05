---
id: react/19-error-handling
topic: react
slug: error-handling
title: "React Error Handling"
type: doc
order: 19
status: ready
tags: [react, error-handling]
related: [react/15-forms, react/16-data-fetching, react/20-accessibility]
when_to_use: "Read before implementing or reviewing error boundaries, fallbacks, and failure handling in React."
---
# React Error Handling

## Purpose

This document defines the engineering standards for handling errors in React applications.

The objective is to build applications that fail gracefully, provide meaningful feedback to users, simplify debugging, and remain resilient under unexpected conditions.

Errors are inevitable.

Poor error handling is optional.

---

## Core Principle

Every error should be:

- detected;
- handled;
- logged;
- communicated appropriately.

An application should never fail silently.

---

## Error Handling Workflow

Every error should follow this lifecycle.

```
Error Occurs
        ↓
Capture
        ↓
Categorize
        ↓
Log
        ↓
Display Feedback
        ↓
Recover or Retry
        ↓
Continue Application
```

---

## Error Categories

Classify errors before deciding how to handle them.

## User Errors

Examples:

- invalid input;
- missing required fields;
- unsupported actions.

These should be explained clearly to the user.

---

## Network Errors

Examples:

- timeout;
- connection lost;
- API unavailable;
- request cancelled.

Provide retry mechanisms whenever appropriate.

---

## Server Errors

Examples:

- HTTP 500;
- invalid server response;
- unexpected API failures.

Do not expose internal server details.

---

## Authorization Errors

Examples:

- expired session;
- missing permissions;
- unauthorized request.

Handle consistently across the application.

---

## Unexpected Errors

Examples:

- JavaScript exceptions;
- rendering failures;
- invalid application state.

These should be logged and isolated whenever possible.

---

## Error Boundaries

Use Error Boundaries to isolate rendering failures.

Good candidates include:

- page layouts;
- dashboards;
- large widgets;
- independent feature areas.

Error Boundaries prevent a single rendering error from crashing the entire application.

React itself only exposes error boundaries through class component lifecycle methods (`getDerivedStateFromError`, `componentDidCatch`). To stay on function components and hooks, use the community standard [`react-error-boundary`](https://github.com/bvaughn/react-error-boundary) package, which wraps that mechanism for you.

Good:

```tsx
import { ErrorBoundary } from "react-error-boundary";

function DashboardFallback({
    error,
    resetErrorBoundary,
}: {
    error: Error;
    resetErrorBoundary: () => void;
}) {
    return (
        <div role="alert">
            <p>The dashboard could not be displayed.</p>
            <button onClick={resetErrorBoundary}>Try again</button>
        </div>
    );
}

function DashboardPage({ userId }: { userId: string }) {
    return (
        <ErrorBoundary
            FallbackComponent={DashboardFallback}
            onError={(error, info) => logError(error, info.componentStack)}
            // Re-mount and retry when the identity of the data changes.
            resetKeys={[userId]}
        >
            <Dashboard userId={userId} />
        </ErrorBoundary>
    );
}
```

Scope boundaries per feature area, not once at the app root. A boundary around each widget lets one widget fail while the rest of the page stays interactive.

In React 18/19 you can also observe errors globally when creating the root. These are for logging and telemetry, not for rendering fallbacks:

```tsx
import { createRoot } from "react-dom/client";

const root = createRoot(document.getElementById("root")!, {
    // React 19: errors an Error Boundary caught.
    onCaughtError: (error, info) => logError(error, info.componentStack),
    // React 19: errors that reached the root with no boundary.
    onUncaughtError: (error, info) => logFatal(error, info.componentStack),
    // React 18+: errors React recovered from (e.g. hydration mismatch).
    onRecoverableError: (error) => logWarning(error),
});
```

---

## What Error Boundaries Do Not Catch

Error Boundaries do not automatically catch:

- asynchronous errors;
- event handler exceptions;
- network request failures;
- timer callbacks;
- server-side errors.

These must be handled explicitly.

For code outside the render path, catch the error and either handle it locally or forward it into the nearest boundary with the `useErrorBoundary` hook.

Bad:

```tsx
// A throw inside an event handler escapes every Error Boundary
// and surfaces as an unhandled exception.
function DeleteButton({ id }: { id: string }) {
    return <button onClick={() => deleteItem(id)}>Delete</button>;
}
```

Good:

```tsx
import { useErrorBoundary } from "react-error-boundary";

function DeleteButton({ id }: { id: string }) {
    const { showBoundary } = useErrorBoundary();

    async function handleDelete() {
        try {
            await deleteItem(id);
        } catch (error) {
            // Route unexpected async failures to the nearest boundary.
            showBoundary(error);
        }
    }

    return <button onClick={handleDelete}>Delete</button>;
}
```

---

## Async Error Handling

Handle asynchronous failures close to the request.

Example workflow:

```
Request

↓

Success

or

↓

Error

↓

Display Feedback

↓

Retry
```

Never ignore rejected promises.

When you own the loading state manually, keep error state alongside data and loading, and always resolve the rejected path:

Good:

```tsx
function useOrders(userId: string) {
    const [data, setData] = useState<Order[] | null>(null);
    const [error, setError] = useState<Error | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const controller = new AbortController();

        setIsLoading(true);
        setError(null);

        fetchOrders(userId, { signal: controller.signal })
            .then(setData)
            .catch((err) => {
                // Ignore the abort we triggered on cleanup.
                if (err.name !== "AbortError") setError(err);
            })
            .finally(() => setIsLoading(false));

        return () => controller.abort();
    }, [userId]);

    return { data, error, isLoading };
}
```

With React 19, prefer `use()` to unwrap a promise and let a Suspense boundary render the loading state and an Error Boundary render the failure. A promise rejection thrown by `use()` propagates to the nearest Error Boundary automatically:

```tsx
import { Suspense, use } from "react";
import { ErrorBoundary } from "react-error-boundary";

function Orders({ ordersPromise }: { ordersPromise: Promise<Order[]> }) {
    const orders = use(ordersPromise); // suspends, or throws on rejection
    return (
        <ul>
            {orders.map((o) => (
                <li key={o.id}>{o.total}</li>
            ))}
        </ul>
    );
}

function OrdersPanel({ ordersPromise }: { ordersPromise: Promise<Order[]> }) {
    return (
        <ErrorBoundary fallback={<p role="alert">Unable to load your orders.</p>}>
            <Suspense fallback={<Spinner />}>
                <Orders ordersPromise={ordersPromise} />
            </Suspense>
        </ErrorBoundary>
    );
}
```

Create the promise outside render (in an event handler, a cache, or a framework loader) so it is stable across renders. Never construct it inline in the component body, or `use()` receives a new promise on every render.

---

## Error Messages

Messages should:

- explain what happened;
- explain what the user can do;
- avoid technical jargon.

Good:

```
Unable to load your orders.

Please try again.
```

Avoid:

```
TypeError: Cannot read property...
```

Technical details belong in logs, not in the UI.

---

## Retry Strategy

Retry only when appropriate.

Good candidates:

- temporary network failures;
- timeouts;
- intermittent server errors.

Avoid automatic retries for:

- validation failures;
- authorization errors;
- malformed requests.

Automatic retries should use exponential backoff with a bounded attempt count so a failing service is not hammered:

```tsx
async function withRetry<T>(
    fn: () => Promise<T>,
    { retries = 3, baseDelay = 300 } = {},
): Promise<T> {
    for (let attempt = 0; ; attempt++) {
        try {
            return await fn();
        } catch (error) {
            // Do not retry client-side or auth failures.
            if (attempt >= retries || !isRetryable(error)) throw error;
            const delay = baseDelay * 2 ** attempt + Math.random() * 100;
            await new Promise((resolve) => setTimeout(resolve, delay));
        }
    }
}
```

For render-time failures, retrying means re-mounting the subtree. `react-error-boundary` exposes this through `resetErrorBoundary()` and `resetKeys`, which is why the fallback should offer an explicit "Try again" control rather than a full page reload.

---

## Fallback UI

Every important feature should define an appropriate fallback.

Examples:

- empty state;
- retry button;
- placeholder;
- maintenance message.

Fallback interfaces should remain functional and accessible.

---

## Logging

Errors should be logged consistently.

Log:

- error message;
- stack trace;
- request details;
- user action;
- timestamp.

Avoid logging sensitive information.

---

## Monitoring

Production applications should integrate centralized monitoring.

Typical examples include:

- runtime error tracking;
- performance monitoring;
- API failure tracking.

Monitoring should support investigation rather than replace good error handling.

---

## Recovery

Whenever possible, allow the user to recover.

Examples:

- retry request;
- reload section;
- refresh data;
- navigate elsewhere.

Avoid forcing a full page reload unless necessary.

---

## Forms

Validation errors should remain local to the form.

Unexpected failures should:

- preserve user input;
- explain the issue;
- allow another submission.

Do not discard entered data after failures.

In React 19, model submission with an Action and `useActionState`. The action returns an error state instead of throwing, so the component stays mounted, the entered values survive, and `isPending` drives the disabled/loading state:

Good:

```tsx
import { useActionState } from "react";

type FormState = { error: string | null; values: { email: string } };

async function subscribeAction(
    _prev: FormState,
    formData: FormData,
): Promise<FormState> {
    const email = String(formData.get("email") ?? "");
    if (!email.includes("@")) {
        // Local validation error: keep it in state, do not throw.
        return { error: "Enter a valid email address.", values: { email } };
    }
    try {
        await subscribe(email);
        return { error: null, values: { email: "" } };
    } catch {
        // Unexpected failure: preserve input so the user can retry.
        return { error: "Something went wrong. Please try again.", values: { email } };
    }
}

function SubscribeForm() {
    const [state, formAction, isPending] = useActionState(subscribeAction, {
        error: null,
        values: { email: "" },
    });

    return (
        <form action={formAction}>
            <label htmlFor="email">Email</label>
            <input
                id="email"
                name="email"
                type="email"
                defaultValue={state.values.email}
                aria-invalid={state.error ? true : undefined}
                aria-describedby={state.error ? "email-error" : undefined}
            />
            {state.error && (
                <p id="email-error" role="alert">
                    {state.error}
                </p>
            )}
            <button type="submit" disabled={isPending}>
                {isPending ? "Subscribing..." : "Subscribe"}
            </button>
        </form>
    );
}
```

If the action throws (or a rejection escapes), React re-throws during render and the nearest Error Boundary takes over, replacing the form and losing the entered input. Return the error as state instead so recovery stays inline.

---

## Accessibility

Error feedback should be accessible.

Verify:

- error messages are announced;
- focus moves appropriately when needed;
- invalid fields are identified;
- retry actions are keyboard accessible.

Accessibility applies to failures as well as successful interactions.

Announce errors with a live region so assistive technology reads them without a focus change. `role="alert"` (an assertive live region) fits blocking errors; `aria-live="polite"` fits non-urgent status. Tie invalid fields to their message with `aria-describedby` and mark them `aria-invalid`.

Good:

```tsx
// Announced immediately when it renders into the DOM.
{error && (
    <div role="alert">
        <p>Unable to load your orders.</p>
        <button onClick={retry}>Try again</button>
    </div>
)}
```

For errors that resolve to a specific field, move focus to it so keyboard users land on the problem:

```tsx
const emailRef = useRef<HTMLInputElement>(null);

useEffect(() => {
    if (fieldError) emailRef.current?.focus();
}, [fieldError]);
```

In React 19 you can pass `ref` directly as a prop to your own components (`function Field({ ref }) { ... }`), so forwarding focus to a wrapped input no longer needs `forwardRef`.

---

## AI Execution Checklist

## Investigation

☐ Identify possible failure points.

☐ Classify expected errors.

☐ Define recovery strategy.

☐ Review accessibility.

---

## Planning

☐ Define fallback UI.

☐ Define logging strategy.

☐ Define retry strategy.

☐ Define monitoring requirements.

---

## Verification

☐ Errors handled consistently.

☐ Error messages understandable.

☐ Retry available where appropriate.

☐ Errors logged.

☐ Accessibility preserved.

☐ Application remains usable after failures.

---

## Examples

**Good Example** — boundaries per region, reported, with a way back

```tsx
// A boundary around a region, not the whole app: a failing chart does not blank
// the page, and the fallback offers a real recovery action.
export function Dashboard() {
  return (
    <>
      <ErrorBoundary
        fallbackRender={({ error, resetErrorBoundary }) => (
          <ErrorState
            title="The revenue chart could not be loaded"
            detail={error.message}
            onRetry={resetErrorBoundary}
          />
        )}
        onError={(error, info) => reportError(error, { componentStack: info.componentStack })}
      >
        <RevenueChart />
      </ErrorBoundary>

      <OrdersTable />   {/* still renders if the chart failed */}
    </>
  );
}
```

```tsx
// Async failures never reach an error boundary — handle them where they happen.
function SaveButton({ onSave }: { onSave: () => Promise<void> }) {
  const [error, setError] = useState<string | null>(null);

  async function handleClick() {
    setError(null);
    try {
      await onSave();
    } catch (err) {
      reportError(err);                                  // the details go to the log
      setError('Could not save. Your changes are still here.');   // the user gets a plan
    }
  }

  return (
    <>
      <button onClick={handleClick}>Save</button>
      {error && <p role="alert">{error}</p>}
    </>
  );
}
```

**Bad Example** — one boundary at the root, failures swallowed

```tsx
// A single boundary around the whole tree: any error anywhere replaces the
// entire application with a blank apology, and there is no way back but reload.
<ErrorBoundary fallback={<p>Something went wrong</p>}>
  <App />
</ErrorBoundary>
```

```tsx
function SaveButton({ onSave }: { onSave: () => Promise<void> }) {
  async function handleClick() {
    try {
      await onSave();
    } catch {
      // Swallowed: the user sees nothing happen and clicks again, monitoring
      // records no failure, and the cause is never known.
    }
  }
  return <button onClick={handleClick}>Save</button>;
}

function Profile() {
  const [user, setUser] = useState(null);
  // A rejected promise here is an unhandled rejection, not a caught error:
  // no boundary catches it, and the spinner stays forever.
  useEffect(() => {
    fetch('/api/me').then((r) => r.json()).then(setUser);
  }, []);
  return user ? <ProfileCard user={user} /> : <Spinner />;
}
```

---

## Common Mistakes

Avoid:

Ignoring rejected promises.

Showing technical errors to users.

Swallowing exceptions.

Logging sensitive information.

Retrying every failed request.

Reloading the entire application unnecessarily.

Losing user input after failures.

Ignoring accessibility during error handling.

---

## Completion Criteria

Error handling is complete when:

- expected errors are handled;
- unexpected errors are isolated;
- users receive meaningful feedback;
- recovery paths exist where appropriate;
- logging and monitoring are implemented;
- accessibility requirements are satisfied.

---

## Summary

Robust error handling improves reliability, usability, and maintainability.

By treating errors as expected scenarios rather than exceptional events, React applications become more resilient and provide a significantly better user experience.

## Related

- `knowledge/react/16-data-fetching.md`
- `knowledge/react/28-production.md`
- `knowledge/frontend/13-error-handling.md`
