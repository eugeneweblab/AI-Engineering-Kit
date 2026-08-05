---
id: react/13-component-composition
topic: react
slug: component-composition
title: "Component Composition"
type: doc
order: 13
status: ready
tags: [react, component-composition, ReactNode, TabPanel, TabsContext, useTabs, TabList, setOpen]
related: [react/05-props, react/04-components, react/14-patterns, react/24-design-patterns, react/02-component-architecture]
when_to_use: "Read before designing a reusable component's API or when a component is drowning in configuration props."
---
# Component Composition

## Purpose

This document defines how to build components that combine cleanly — favoring
composition (passing content and behavior *in*) over configuration (adding a prop
for every variation). It covers `children`, slot props, compound components, and
where to draw component boundaries.

Composition is React's core reuse mechanism. React has no class inheritance model for
UI; you build complex UI by nesting and combining simple pieces. Getting composition
right is what keeps a component library flexible instead of a maze of boolean flags.

## Why It Matters

The alternative to composition is configuration, and configuration does not scale.
Each new use case adds a prop; props interact; the component accumulates conditional
branches until no one can safely change it. Composition inverts this: the parent
supplies the specifics, so the component stays small and open to cases its author
never imagined. Well-composed components are also easier to test — you can render
them with controlled children — and easier to read, because structure is visible in JSX.

## Core Principles

- **Prefer composition over configuration.** When a variation can be expressed by
  passing different children, do that instead of adding a `variant`/`show*` prop.
- **`children` is a prop.** Pass elements, not just data. A component that accepts
  `children` is open to content it will never need to know about.
- **Use named slots for multi-region layouts.** When a component has distinct areas
  (header/body/footer), accept them as separate element props, not one `children` blob.
- **Compose behavior, not just markup.** Wrapper components, render props, and custom
  hooks let you share logic without inheritance.
- **Keep components focused.** A component that both fetches data and renders a specific
  layout cannot be reused for either purpose alone. Split the concerns.

## Best Practices

- Design the public API as "what goes inside," not "which flags are set." A `<Card>`
  should take `children`, not `title`, `subtitle`, `footer`, `hasBorder`, `isRaised`.
- For components with fixed regions, expose element-typed props (`header`, `actions`)
  so callers control layout and content without you predicting every combination.
- Use **compound components** (a parent plus subcomponents sharing implicit state via
  Context) when parts must coordinate — tabs, accordions, menus. The caller composes
  the parts; the parent wires them together.
- Avoid `React.cloneElement` and index-based child inspection; they are fragile and
  break when children are wrapped or reordered. Share state through Context instead.
- Extract shared *logic* into [custom hooks](09-custom-hooks.md) and shared *layout*
  into wrapper components — do not force one component to do both.

## Examples

### Children and named slots

**Good Example** — one `children` slot plus a couple of element-typed slots for the
fixed regions. The caller controls all content; `Card` predicts nothing.

```tsx
import type { ReactNode } from "react";

// `children` is the open body; `header`/`actions` are named slots for fixed regions.
// Everything is a ReactNode, so callers pass elements — not strings or config objects.
function Card({
  header,
  actions,
  children,
}: {
  header?: ReactNode;
  actions?: ReactNode;
  children: ReactNode;
}) {
  return (
    <section className="card">
      {header && <header className="card__header">{header}</header>}
      <div className="card__body">{children}</div>
      {actions && <footer className="card__actions">{actions}</footer>}
    </section>
  );
}

// The caller composes structure freely — a badge, an image, whatever it needs —
// without Card growing a prop for each. Structure is visible at the call site.
<Card
  header={<h3>Pro plan</h3>}
  actions={
    <>
      <button>Cancel</button>
      <button>Upgrade</button>
    </>
  }
>
  <img src="/pro.png" alt="" />
  <p>Everything in Free, plus unlimited projects.</p>
</Card>;
```

**Bad Example** — configuration explosion: every variation becomes a prop.

```tsx
// Every variation is a prop; the component grows a branch per case.
function Card({
  title, subtitle, footer, imageUrl, hasBorder, isRaised, variant, actions, badge,
}: CardProps) {
  return (
    <section className={`card ${variant} ${hasBorder ? "bordered" : ""} ${isRaised ? "raised" : ""}`}>
      {badge && <span className="badge">{badge}</span>}
      {imageUrl && <img src={imageUrl} />}
      {title && <h3>{title}</h3>}
      {subtitle && <p>{subtitle}</p>}
      {/* The next feature request adds prop #10. Callers still cannot do the unforeseen case. */}
      {actions && <div className="actions">{actions}</div>}
      {footer && <footer>{footer}</footer>}
    </section>
  );
}
```

### Compound components (coordinating parts)

**Good Example** — a tabs widget whose parts coordinate through Context. The caller
composes the parts in any order; the parent wires shared state. This version uses
React 19 idioms: `<Context>` as the provider, `use(Context)` to read it, and `ref` as
a plain prop (no `forwardRef`).

```tsx
import { createContext, use, useId, useState, type ReactNode, type Ref } from "react";

interface TabsContextValue {
  active: string;
  select: (id: string) => void;
  baseId: string;
}

const TabsContext = createContext<TabsContextValue | null>(null);

// Safe consumer hook: fails loudly outside <Tabs> instead of a silent null deref.
// Prefer this over `use(TabsContext)!` — the `!` hides the misuse.
function useTabs(): TabsContextValue {
  const ctx = use(TabsContext);
  if (!ctx) throw new Error("Tabs.* must be rendered inside <Tabs>");
  return ctx;
}

function Tabs({ defaultTab, children }: { defaultTab: string; children: ReactNode }) {
  const [active, setActive] = useState(defaultTab);
  const baseId = useId(); // unique, SSR-stable id prefix for aria wiring
  // React 19: render the context object directly as the provider.
  return (
    <TabsContext value={{ active, select: setActive, baseId }}>{children}</TabsContext>
  );
}

function TabList({ children }: { children: ReactNode }) {
  return <div role="tablist">{children}</div>;
}

// React 19: `ref` is a normal prop on a function component — no forwardRef wrapper.
function Tab({
  id,
  ref,
  children,
}: {
  id: string;
  ref?: Ref<HTMLButtonElement>;
  children: ReactNode;
}) {
  const { active, select, baseId } = useTabs();
  const selected = active === id;
  return (
    <button
      ref={ref}
      role="tab"
      id={`${baseId}-tab-${id}`}
      aria-selected={selected}
      aria-controls={`${baseId}-panel-${id}`}
      tabIndex={selected ? 0 : -1}
      onClick={() => select(id)}
    >
      {children}
    </button>
  );
}

function TabPanel({ id, children }: { id: string; children: ReactNode }) {
  const { active, baseId } = useTabs();
  if (active !== id) return null;
  return (
    <div role="tabpanel" id={`${baseId}-panel-${id}`} aria-labelledby={`${baseId}-tab-${id}`}>
      {children}
    </div>
  );
}

// Caller composes the parts — no prop explosion, structure is visible in JSX.
<Tabs defaultTab="overview">
  <TabList>
    <Tab id="overview">Overview</Tab>
    <Tab id="specs">Specs</Tab>
  </TabList>
  <TabPanel id="overview">Everything you need to know.</TabPanel>
  <TabPanel id="specs">Weight, size, materials.</TabPanel>
</Tabs>;
```

**Bad Example** — the same widget driven by data props and child inspection.

```tsx
// Config-driven: the caller cannot interleave custom markup, and cloneElement
// breaks the moment a Tab is wrapped (e.g. in a tooltip or a permission gate).
function Tabs({ tabs }: { tabs: { id: string; label: string; content: ReactNode }[] }) {
  const [active, setActive] = useState(tabs[0]?.id);
  return (
    <div>
      {tabs.map((t) => (
        <button key={t.id} onClick={() => setActive(t.id)}>{t.label}</button>
      ))}
      {tabs.find((t) => t.id === active)?.content}
    </div>
  );
}
```

### Composing behavior, not just markup

**Good Example** — share *logic* through a hook so unrelated components can reuse it
with their own markup. This keeps composition open without inheritance or HOC stacking.

```tsx
import { useState, useCallback } from "react";

// Behavior lives in a hook; each component composes it with whatever UI it wants.
function useDisclosure(initial = false) {
  const [open, setOpen] = useState(initial);
  const onOpen = useCallback(() => setOpen(true), []);
  const onClose = useCallback(() => setOpen(false), []);
  const onToggle = useCallback(() => setOpen((o) => !o), []);
  return { open, onOpen, onClose, onToggle } as const;
}

// A dialog and a dropdown share the exact same open/close behavior, no shared base class.
function FaqItem({ question, children }: { question: string; children: ReactNode }) {
  const { open, onToggle } = useDisclosure();
  return (
    <div>
      <button aria-expanded={open} onClick={onToggle}>{question}</button>
      {open && <div>{children}</div>}
    </div>
  );
}
```

## Common Mistakes

- Adding a boolean or `variant` prop for every visual case instead of accepting children.
- Building "god components" that fetch, transform, and render one fixed layout.
- Inspecting or cloning children with `cloneElement`/index access, which breaks on wrapping.
- Using props to pass large chunks of markup as strings or config objects instead of elements.
- Duplicating a component to tweak one region, when a slot prop would have covered it.
- Reaching for inheritance patterns (HOC stacking) where a hook or wrapper is simpler.

## Production Tips

- When a component crosses ~6 props or gains its third boolean, treat it as a signal to
  refactor toward composition.
- Document the intended composition in the component's example, so consumers use the
  slots as designed instead of forking the component.

## AI Review Checklist

- Does the component accept `children` or element slots instead of a prop per variation?
- Are coordinating parts (tabs, menus) built as compound components sharing Context?
- Is shared logic extracted to a custom hook rather than duplicated or inherited?
- Are children passed as elements, not inspected/cloned by index?
- Is each component focused on one concern (data OR layout, not both)?
- Would a new use case require a code change, or can the caller compose it today?

## Related

- `knowledge/react/05-props.md`
- `knowledge/react/04-components.md`
- `knowledge/react/14-patterns.md`
- `knowledge/react/24-design-patterns.md`
- `knowledge/react/02-component-architecture.md`
