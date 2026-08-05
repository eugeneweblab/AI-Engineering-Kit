---
id: examples/02-react-component
topic: examples
slug: react-component
title: "Example — React Component"
type: doc
order: 2
status: ready
tags: [examples, react-component]
related: [examples/01-rest-endpoint, workflows/08-build-react-component, react/13-component-composition, accessibility/04-keyboard-navigation, react/21-testing]
when_to_use: "Read when building a React component end to end — props contract, every state, accessibility, and tests."
---
# Example — React Component

## The Feature

`SignupButton` — registers the current user for an event. It has to handle the loading,
error, full, already-registered, and past-event states, and remain usable by keyboard and
screen reader.

The process is [Workflow — Build a React Component](../workflows/08-build-react-component.md);
this is the result.

---

## 1. The Props Contract

```tsx
// SignupButton.tsx
type SignupButtonProps = {
  eventId: number;
  /** Server-rendered state, so the first paint is correct rather than flashing. */
  initialState: 'available' | 'full' | 'registered' | 'past';
  onRegistered?: (signupId: number) => void;
};
```

Four named states rather than three booleans. `isFull`, `isRegistered`, and `isPast` would
permit `{ isFull: true, isPast: true, isRegistered: true }` — a combination with no defined
rendering. A union makes the illegal states unrepresentable, so no component below has to
decide which flag wins.

---

## 2. The Component

```tsx
import { useState } from 'react';

export function SignupButton({ eventId, initialState, onRegistered }: SignupButtonProps) {
  const [state, setState] = useState(initialState);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleClick() {
    setPending(true);
    setError(null);

    try {
      const res = await fetch(`/api/v1/events/${eventId}/signups`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
      });

      // 409 is expected: the event filled, or another tab registered already.
      // Reflect the new reality rather than showing a generic failure.
      if (res.status === 409) {
        const body = await res.json();
        setState(body.error === 'Event is full' ? 'full' : 'registered');
        return;
      }

      if (!res.ok) throw new Error('Request failed');

      const signup = await res.json();
      setState('registered');
      onRegistered?.(signup.id);
    } catch {
      setError('Could not complete registration. Please try again.');
    } finally {
      setPending(false);   // in `finally`, so an error path cannot leave it stuck
    }
  }

  if (state === 'past') {
    return <p className="signup__note">This event has already taken place.</p>;
  }

  if (state === 'registered') {
    // role="status" announces the change without stealing focus.
    return (
      <p className="signup__note" role="status">
        You are registered for this event.
      </p>
    );
  }

  const isFull = state === 'full';

  return (
    <div className="signup">
      <button
        type="button"
        className="signup__button"
        onClick={handleClick}
        disabled={pending || isFull}
        // Describes the button by the error when one exists, so a screen reader
        // reaches the reason rather than just hearing "button".
        aria-describedby={error ? 'signup-error' : undefined}
      >
        {pending ? 'Registering…' : isFull ? 'Event is full' : 'Register'}
      </button>

      {error && (
        // role="alert" announces immediately; the id ties it to the button above.
        <p id="signup-error" className="signup__error" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
```

---

## 3. What the Details Are For

**`credentials: 'same-origin'`** — without it the session cookie is not sent and every
request is a 401.

**Handling 409 as a state change, not an error.** The server is telling you the world moved
on. Showing "something went wrong" when the real answer is "you are already registered"
makes the user retry a request that cannot succeed.

**`disabled` while pending** prevents the double-submit that produces two signups — the
server's idempotency is the real guard, but the UI should not invite the problem.

**A native `<button type="button">`** brings keyboard activation, focus, and the correct role
for free. A `div` with `onClick` needs `tabIndex`, `role`, and handlers for both Enter and
Space, and still behaves differently — see
[Accessibility — Keyboard Navigation](../accessibility/04-keyboard-navigation.md).

**`type="button"`** matters inside a form: the default is `submit`, and the button would post
the form.

---

## 4. Tests

```tsx
// SignupButton.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer();
beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

// Queried by role and accessible name — the same way a user finds it.
const button = () => screen.getByRole('button', { name: /register/i });

it('registers the user and confirms', async () => {
  server.use(
    http.post('/api/v1/events/12/signups', () => HttpResponse.json({ id: 4471 }, { status: 201 })),
  );
  const onRegistered = vi.fn();

  render(<SignupButton eventId={12} initialState="available" onRegistered={onRegistered} />);
  await userEvent.click(button());

  expect(await screen.findByRole('status')).toHaveTextContent(/you are registered/i);
  expect(onRegistered).toHaveBeenCalledWith(4471);
});

it('shows the full state when the server reports a conflict', async () => {
  server.use(
    http.post('/api/v1/events/12/signups', () =>
      HttpResponse.json({ error: 'Event is full' }, { status: 409 }),
    ),
  );

  render(<SignupButton eventId={12} initialState="available" />);
  await userEvent.click(button());

  expect(await screen.findByRole('button', { name: /event is full/i })).toBeDisabled();
  expect(screen.queryByRole('alert')).not.toBeInTheDocument();   // a conflict is not an error
});

it('announces a failure and allows a retry', async () => {
  server.use(http.post('/api/v1/events/12/signups', () => HttpResponse.error()));

  render(<SignupButton eventId={12} initialState="available" />);
  await userEvent.click(button());

  expect(await screen.findByRole('alert')).toHaveTextContent(/could not complete/i);
  expect(button()).toBeEnabled();   // recoverable, not stuck
});

it('is operable by keyboard', async () => {
  server.use(
    http.post('/api/v1/events/12/signups', () => HttpResponse.json({ id: 1 }, { status: 201 })),
  );

  render(<SignupButton eventId={12} initialState="available" />);
  await userEvent.tab();
  expect(button()).toHaveFocus();

  await userEvent.keyboard('{Enter}');
  expect(await screen.findByRole('status')).toBeInTheDocument();
});

it.each(['full', 'registered', 'past'] as const)('renders the %s state', (initialState) => {
  render(<SignupButton eventId={12} initialState={initialState} />);
  expect(screen.queryByRole('button', { name: 'Register' })).not.toBeInTheDocument();
});
```

Every query goes through role and accessible name. That is not a style preference: a test
that finds the button by `.signup__button` passes even when the element has no accessible
name at all, so the test suite cannot tell you the component became unusable.

---

## What a Real Implementation Adds

- **Optimistic UI** — React's `useOptimistic` for instant feedback with a rollback path.
- **A shared fetch layer** — retries, timeouts, and error normalization, rather than raw
  `fetch` in a component.
- **Analytics** — a conversion event on success.
- **Internationalization** — every string above is hardcoded English.
- **Stories** — one per state, feeding visual regression; see
  [Tools — Storybook](../tools/15-storybook.md).

---

## Examples

**Good Example** — every state the component can be in is built and testable

```tsx
export function ProductCard({ product, onAdd }: ProductCardProps) {
  return (
    <article className={styles.card}>
      {product.imageUrl ? (
        <img src={product.imageUrl} alt={product.imageAlt} width={800} height={600} loading="lazy" />
      ) : (
        <div className={styles.imageFallback} aria-hidden="true" />
      )}

      <h3 className={styles.title}>{product.name}</h3>
      <p className={styles.price}>{formatCurrency(product.priceCents)}</p>

      <Button onClick={() => onAdd(product.id)} disabled={!product.inStock}>
        {product.inStock ? 'Add to basket' : 'Out of stock'}
      </Button>
    </article>
  );
}
```

```tsx
// The states are enumerated once and reused by Storybook and the tests.
export const Default: Story  = { args: { product: aProduct() } };
export const LongName: Story = { args: { product: aProduct({ name: 'x'.repeat(64) }) } };
export const NoImage: Story  = { args: { product: aProduct({ imageUrl: null }) } };
export const OutOfStock: Story = { args: { product: aProduct({ inStock: false }) } };
```

**Bad Example** — the happy path, with the rest discovered by users

```tsx
export function ProductCard({ data }: { data: any }) {
  return (
    <div className="card" onClick={() => addToBasket(data.id)}>
      {/* Null imageUrl renders a broken image icon. */}
      <img src={data.img} />
      <div className="title">{data.name}</div>
      {/* Float arithmetic on money, and no out-of-stock state at all. */}
      <div className="price">£{data.price / 100}</div>
    </div>
  );
}
```

---

## Related


- `knowledge/examples/01-rest-endpoint.md`
- `knowledge/workflows/08-build-react-component.md`
- `knowledge/react/13-component-composition.md`
- `knowledge/accessibility/04-keyboard-navigation.md`
- `knowledge/react/21-testing.md`
