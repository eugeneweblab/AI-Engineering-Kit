---
id: react/05-props
topic: react
slug: props
title: "Props and Component API Design"
type: doc
order: 5
status: ready
tags: [react, props, CardHeader, ReactNode, UserAvatar, ButtonProps, Layout, Card, public, component, api]
related: [react/04-components, react/13-component-composition, react/06-state]
when_to_use: "Read before designing or reviewing a React component's props and public API."
---
# Props and Component API Design

## Purpose

This document defines the standards for designing React component APIs.

The objective is to create components that are predictable, reusable, self-documenting, and easy to integrate throughout the application.

A component's public API is one of the most important parts of its design. Poor APIs create unnecessary complexity that propagates throughout the codebase.

---

## Core Principle

Design the API before writing the implementation.

A clear API leads to a simple implementation.

---

## What Is a Component API?

A component API consists of everything another developer can use:

- props;
- children;
- callbacks;
- exposed refs;
- context providers;
- imperative methods.

Everything else is an implementation detail.

---

## API Design Principles

Every public API should be:

- minimal;
- explicit;
- predictable;
- consistent;
- well typed;
- difficult to misuse.

Adding new props should be easier than changing existing ones.

---

## Keep APIs Small

Prefer components with a small number of meaningful props.

Good:

```tsx
<Button
    variant="primary"
    size="large"
    disabled
>
    Save
</Button>
```

Avoid:

```tsx
<Button
    blue
    rounded
    shadow
    big
    largePadding
    whiteText
    animation
    customSpacing
    secondaryShadow
/>
```

Too many boolean props usually indicate poor API design.

---

## Prefer Explicit Names

Prop names should describe intent.

Good:

```tsx
isLoading

isDisabled

maxItems

selectedItem
```

Avoid:

```tsx
flag

value2

enabledMode

statusFlag
```

Names should communicate meaning without additional documentation.

---

## Boolean Props

Boolean props should read naturally.

Good:

```tsx
disabled

required

readonly

checked

open
```

Or:

```tsx
isLoading

isSelected

isExpanded

hasError
```

Avoid double negatives.

Bad:

```tsx
notDisabled

disableFalse

isNotClosed
```

---

## Children vs Props

Use `children` when the caller controls content.

Good:

```tsx
<Card>

    <ProductCard />

</Card>
```

Use props when the component controls rendering.

Good:

```tsx
<Avatar
    name={user.name}
    image={user.avatar}
/>
```

Do not duplicate both approaches unless necessary.

---

## Callbacks

Callbacks should describe completed actions.

Good:

```tsx
onSave

onClose

onSubmit

onDelete
```

Avoid implementation-focused names.

Bad:

```tsx
handleClick

buttonPressed

runFunction
```

Callbacks should communicate intent rather than UI mechanics.

---

## Controlled vs Uncontrolled Components

Whenever appropriate, support controlled components.

Controlled:

```tsx
value

onChange
```

Uncontrolled:

```tsx
defaultValue
```

Do not mix both patterns without a clear reason.

---

## Default Values

Provide sensible defaults.

Consumers should configure only what is necessary.

Avoid requiring props that almost always have the same value.

---

## Avoid Prop Explosion

When the number of props grows continuously, reconsider the design.

Possible solutions:

- split the component;
- introduce composition;
- extract child components;
- move logic into hooks.

Adding more props is rarely the best long-term solution.

---

## Prop Types

Every prop should have a clearly defined type.

Prefer:

- specific unions;
- enums when appropriate;
- interfaces;
- reusable types.

Avoid:

```tsx
any

object

unknown
```

unless technically required.

---

## Passing Objects

Pass only the data a component needs.

Prefer:

```tsx
<UserAvatar
    name={user.name}
    avatar={user.avatar}
/>
```

Instead of:

```tsx
<UserAvatar
    user={user}
/>
```

Large objects unnecessarily increase coupling.

---

## Component Variants

Use variants instead of creating multiple nearly identical components.

Example:

```tsx
<Button variant="primary" />

<Button variant="secondary" />

<Button variant="danger" />
```

Avoid:

```
PrimaryButton

SecondaryButton

DangerButton
```

unless behavior differs significantly.

---

## Accessibility

Public APIs should support accessibility.

Examples:

- aria-label;
- aria-describedby;
- role (when appropriate);
- disabled;
- required.

Accessibility should not require workarounds.

---

## AI Execution Checklist

## Investigation

☐ Identify the component's public API.

☐ Review similar components.

☐ Minimize required props.

☐ Define prop types.

---

## Planning

☐ Design a consistent API.

☐ Define callbacks.

☐ Define default values.

☐ Plan accessibility support.

---

## Verification

☐ API is easy to understand.

☐ Props are well named.

☐ No unnecessary props.

☐ Component remains reusable.

☐ Types are explicit.

☐ Accessibility supported.

---

## Examples

**Good Example** — a narrow, typed contract with sensible composition

```tsx
type ButtonProps = {
  variant?: 'primary' | 'secondary' | 'danger';   // a closed set, checked by the compiler
  size?: 'sm' | 'md';
  children: React.ReactNode;
} & Omit<React.ComponentPropsWithoutRef<'button'>, 'className'>;

export function Button({ variant = 'primary', size = 'md', children, ...rest }: ButtonProps) {
  // Forwarding the native props means onClick, type, disabled, and aria-* all
  // work without being re-declared here.
  return (
    <button className={cx(styles[variant], styles[size])} {...rest}>
      {children}
    </button>
  );
}
```

```tsx
// Composition instead of a boolean per variation: the card does not need to know
// which combination of header, media, and actions a caller wants.
export function Card({ children }: { children: React.ReactNode }) {
  return <div className="card">{children}</div>;
}
Card.Header = function CardHeader({ children }: { children: React.ReactNode }) {
  return <header className="card__header">{children}</header>;
};
```

**Bad Example** — a boolean for every case, and props threaded through five levels

```tsx
type CardProps = {
  // Each flag doubles the number of states to reason about, and nothing prevents
  // an impossible combination like compact + expanded.
  isCompact?: boolean;
  isExpanded?: boolean;
  hasHeader?: boolean;
  hasFooter?: boolean;
  showAvatar?: boolean;
  variant?: string;                  // any string: typos compile
  data?: any;                        // no contract at all
};

// Prop drilling: `user` is used only by Avatar, but every component in between
// declares it, and adding a field to it changes five signatures.
function Page({ user }: { user: User }) { return <Layout user={user} />; }
function Layout({ user }: { user: User }) { return <Sidebar user={user} />; }
function Sidebar({ user }: { user: User }) { return <Profile user={user} />; }
function Profile({ user }: { user: User }) { return <Avatar user={user} />; }
```

Pass the component instead of the data when the middle layers do not use it, or put the value
in context when genuinely many descendants need it.

---

## Common Mistakes

Avoid:

Adding props for every new feature.

Using ambiguous prop names.

Passing entire objects unnecessarily.

Using `any` for prop types.

Creating many boolean flags.

Breaking consistency between components.

Ignoring accessibility requirements.

---

## Completion Criteria

A component API is complete when:

- props are minimal and well named;
- types are explicit;
- callbacks describe user actions;
- composition has been preferred where appropriate;
- accessibility requirements are supported;
- the API is easy to understand without additional explanation.

---

## Summary

A well-designed component API makes components intuitive to use, easy to extend, and difficult to misuse.

Thoughtful API design reduces maintenance costs and creates a more consistent developer experience across the entire application.

## Related

- `knowledge/react/04-components.md`
- `knowledge/react/13-component-composition.md`
- `knowledge/react/06-state.md`
