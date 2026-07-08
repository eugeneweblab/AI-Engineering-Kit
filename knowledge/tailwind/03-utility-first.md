---
id: tailwind/03-utility-first
topic: tailwind
slug: utility-first
title: "Utility First"
type: doc
order: 3
status: ready
tags: [tailwind, utility-first]
related: [tailwind/02-core-concepts, tailwind/17-components, tailwind/24-react, tailwind/26-best-practices, tailwind/28-patterns]
when_to_use: "Read before deciding whether to inline utilities, extract a component, or use @apply."
---
# Utility First

## Purpose

This document explains the **utility-first methodology** — Tailwind's central idea — and,
more importantly, when to stop applying it. It gives an agent a concrete decision rule for
choosing between inline utilities, an extracted component, and `@apply`, so styling stays
both readable and DRY.

## Why It Matters

"Utility-first" is easy to caricature as "put everything in the class attribute." Taken to
an extreme, that produces 30-class elements duplicated across a codebase, which is as hard
to maintain as the tangled global CSS Tailwind replaced. Taken too timidly, teams wrap
every element in `@apply`-based classes and lose the whole benefit — colocation, no naming,
no dead CSS. The value is in knowing where the line is.

## Core Principles

- **Compose in markup by default.** Styling lives next to the element it styles, so you
  change appearance without hunting through stylesheets or inventing class names.
- **Extract on repetition, not on length.** A long class list is fine; a class list
  *copied to a second place* is the signal to extract.
- **Extract with the component model, not with CSS.** In a component framework, DRY comes
  from a reusable `<Button>` component, not from an `@apply .btn` rule.
- **`@apply` is a last resort.** It reintroduces the naming and indirection Tailwind
  removes. Use it only for markup you do not control (third-party HTML, Markdown output).

## Best Practices

- When a block of utilities appears a second time, extract a **component** (React/Vue/etc.)
  or a template partial — the single source of truth is then the component, not a class.
- Use loops/`.map()` to render repeated items so the utility string exists once in source.
- Keep utility strings readable: group by concern and let `prettier-plugin-tailwindcss`
  sort them so every element lists classes in the same order.
- Reserve `@apply` for styling generated HTML (a CMS body, `prose` overrides) where you
  cannot attach classes to the element yourself.
- Do not create a `.card`/`.btn` CSS layer as a habit; prove the duplication first.

## Examples

**Good Example** — extract the repeated element into a component

```tsx
// The utility list exists exactly once. Every button stays in sync by construction,
// and consumers customize via props, not by copying classes.
function Button({ children }: { children: React.ReactNode }) {
  return (
    <button className="px-4 py-2 rounded-md bg-blue-600 text-white hover:bg-blue-700">
      {children}
    </button>
  );
}

// Usage — no class duplication at the call sites
<Button>Save</Button>
<Button>Cancel</Button>
```

**Bad Example** — @apply used to avoid a component, recreating global CSS

```css
/* This is the pre-Tailwind problem in disguise: a named class in a separate file,
   with indirection between markup and style, and CSS that can go stale/unused. */
.btn {
  @apply px-4 py-2 rounded-md bg-blue-600 text-white hover:bg-blue-700;
}
```

```html
<!-- Styling is now split across two files; the "utility-first" benefit is gone. -->
<button class="btn">Save</button>
```

## Common Mistakes

- Copy-pasting a long utility string across files instead of extracting a component —
  updates now require editing every copy.
- Defaulting to `@apply` for reusable UI in a project that already has a component layer.
- Extracting too early: turning a one-off element into a component or `.class` before any
  duplication exists, adding indirection for no gain.
- Building class strings dynamically to "reduce repetition," which breaks Tailwind's
  static detection (see [02-core-concepts](02-core-concepts.md)).

## Production Tips

- Enforce class-order formatting in CI so utility strings are diff-stable and reviewable.
- When a component grows many style variants, drive them with a typed variant helper
  (e.g. `cva`/`tailwind-variants`) instead of conditional string concatenation, keeping
  every class literal statically visible to the compiler.

## AI Review Checklist

- Is repeated styling extracted into a component/partial rather than copy-pasted?
- Is `@apply` limited to markup the author cannot add classes to?
- Are one-off elements left inline instead of prematurely abstracted?
- Are variant class strings kept static (no dynamic concatenation the compiler can't see)?
- Is class ordering formatter-enforced for readable diffs?

## Related

- `knowledge/tailwind/02-core-concepts.md`
- `knowledge/tailwind/17-components.md`
- `knowledge/tailwind/24-react.md`
- `knowledge/tailwind/26-best-practices.md`
- `knowledge/tailwind/28-patterns.md`
