---
id: react/13-component-composition
topic: react
slug: component-composition
title: "Component Composition"
type: doc
order: 13
status: ready
tags: [react, component-composition]
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

**Good Example** — composition via children and slots

```tsx
// Open to any content; knows nothing about what it wraps.
function Card({ children }: { children: React.ReactNode }) {
  return <section className="card">{children}</section>;
}

// Compound component: parts coordinate through Context, caller composes them.
const TabsContext = createContext<{ active: string; select: (id: string) => void } | null>(null);

function Tabs({ defaultTab, children }: { defaultTab: string; children: React.ReactNode }) {
  const [active, select] = useReducer((_: string, id: string) => id, defaultTab);
  return <TabsContext.Provider value={{ active, select }}>{children}</TabsContext.Provider>;
}
function Tab({ id, children }: { id: string; children: React.ReactNode }) {
  const ctx = useContext(TabsContext)!;
  return <button aria-selected={ctx.active === id} onClick={() => ctx.select(id)}>{children}</button>;
}

// Caller composes freely — no prop explosion, structure is visible.
<Card><Tabs defaultTab="a"><Tab id="a">First</Tab><Tab id="b">Second</Tab></Tabs></Card>;
```

**Bad Example** — configuration explosion

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
