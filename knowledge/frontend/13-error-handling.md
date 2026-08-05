---
id: frontend/13-error-handling
topic: frontend
slug: error-handling
title: "Frontend Error Handling"
type: doc
order: 13
status: ready
tags: [frontend, error-handling]
related: [frontend/06-data-fetching, frontend/12-forms, frontend/23-monitoring, frontend/14-security, frontend/04-state-management]
when_to_use: "Read before writing any code that can fail: data fetches, form submits, render boundaries, or async effects."
---
# Frontend Error Handling

## Purpose

This document defines how the UI should behave when something goes wrong: a failed
request, a thrown render, a rejected promise, an unexpected shape. It covers error
boundaries, async failure states, user-facing messaging, and what to report versus what
to swallow, so an agent can build a UI that degrades gracefully instead of showing a
blank screen.

Error handling is not an afterthought bolted onto the happy path — it is a first-class
part of every async and render surface. A component that only handles success is
incomplete.

## Why It Matters

In a browser, an unhandled error does not crash a process a supervisor can restart — it
leaves a real user staring at a frozen or blank page. A single uncaught exception during
render can unmount an entire React tree; a swallowed fetch failure leaves a spinner
spinning forever. Users cannot read a stack trace and will not retry a screen that gave
them nothing. Worse, verbose error messages that leak stack traces, internal URLs, or
raw server responses hand attackers a map of your system. Deliberate error handling is
what separates a resilient app from one that appears broken the first time the network
hiccups.

## Core Principles

- **Every async operation has three states, not one.** Loading, success, and error must
  all be represented in the UI. A component that renders only success is unfinished.
- **Contain the blast radius.** Wrap independent regions in error boundaries so one
  failing widget does not blank the whole page.
- **Distinguish expected from unexpected failures.** A 404 or a validation error is a
  normal flow to render inline; a thrown exception is a bug to catch, report, and show a
  fallback for.
- **Tell the user what to do, not what broke.** Show a plain, actionable message. Never
  surface raw stack traces or server internals to the screen.
- **Report before you swallow.** If you catch an error and continue, send it to
  monitoring first. A silently caught error is a bug you will never learn about.

## Best Practices

- Use an **error boundary** around each independently-recoverable region (route, panel,
  widget) with a fallback UI and a retry action. Boundaries catch render/lifecycle errors
  only — they do not catch errors inside event handlers or async callbacks.
- Handle promise rejections explicitly in event handlers and effects; a data-fetching
  library's `error` state or a `try/catch` is required — unhandled rejections never hit a
  boundary.
- Show a **retry** affordance for transient failures (network, 5xx). Do not auto-retry
  non-idempotent actions like payments.
- Map error categories to distinct UI: offline, not-found, forbidden, server error,
  validation. A generic "Something went wrong" for all of them frustrates users.
- Log the technical detail to your monitoring service; show the user a stable,
  human-readable message and a correlation id they can quote to support.
- Reset boundary state on navigation so a user is not stuck on a stale error after moving
  to a different route.
- Never let a `catch` block be empty. At minimum, report it.

## Examples

**Good Example** — boundary with fallback, reported, actionable

```tsx
class ErrorBoundary extends React.Component<Props, { error: Error | null }> {
  state = { error: null };
  static getDerivedStateFromError(error: Error) {
    return { error }; // render the fallback instead of an unmounted tree
  }
  componentDidCatch(error: Error, info: React.ErrorInfo) {
    reportError(error, info); // send to monitoring BEFORE swallowing
  }
  render() {
    if (this.state.error) {
      return (
        <div role="alert">
          <p>This section failed to load.</p> {/* actionable, no stack trace */}
          <button onClick={() => this.setState({ error: null })}>Try again</button>
        </div>
      );
    }
    return this.props.children;
  }
}

function Profile() {
  const { data, error, isLoading, refetch } = useUser();
  if (isLoading) return <Spinner />;              // loading state represented
  if (error) return <InlineError onRetry={refetch} />; // error state represented
  return <ProfileCard user={data} />;
}
```

**Bad Example** — swallowed error, forever-spinner, leaked internals

```tsx
function Profile() {
  const [user, setUser] = useState(null);
  useEffect(() => {
    fetch("/api/me")
      .then((r) => r.json())
      .then(setUser)
      .catch(() => {}); // swallowed: no report, spinner never resolves
  }, []);

  if (!user) return <Spinner />; // "loading" and "failed" are indistinguishable
  return <ProfileCard user={user} />;
}
```

And elsewhere, the opposite failure — showing the raw error to the user:

```ts
try {
  await saveSettings(values);
} catch (e) {
  alert(e.stack); // leaks file paths / internals to the screen
}
```

## Common Mistakes

- Rendering only the success case, so a failed request shows an infinite spinner.
- Empty `catch {}` blocks that swallow errors without reporting them to monitoring.
- Assuming an error boundary catches async and event-handler errors — it does not.
- Showing raw stack traces, server JSON, or internal URLs directly to users.
- One generic error message for every failure, so offline and forbidden look identical.
- Auto-retrying non-idempotent actions (payments, orders), causing duplicate side effects.
- No retry path, forcing a full page reload to recover from a transient blip.

## Production Tips

- Attach a correlation/trace id to every error you report and display it in the fallback
  UI so a user's screenshot maps to a specific log entry.
- Add a global `window.onunhandledrejection` and `window.onerror` handler as a safety net
  that reports what your boundaries and try/catch missed — but treat those reports as bugs
  to fix at the source, not as the primary strategy.
- Rate-limit and deduplicate client error reports so one broken component cannot flood
  your monitoring quota.

## AI Review Checklist

- Does every async operation render distinct loading, success, and error states?
- Are independently-failing regions wrapped in error boundaries with a fallback?
- Is every caught error reported to monitoring before being swallowed?
- Are user-facing messages plain and actionable, with no stack traces or server internals?
- Do transient failures offer a retry, and are non-idempotent actions excluded from it?
- Are different error categories (offline, 404, 403, 5xx, validation) shown distinctly?
- Is boundary state reset on navigation so users are not stuck on a stale error?

## Related

- `knowledge/frontend/06-data-fetching.md`
- `knowledge/frontend/12-forms.md`
- `knowledge/frontend/23-monitoring.md`
- `knowledge/frontend/14-security.md`
- `knowledge/frontend/04-state-management.md`
