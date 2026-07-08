---
id: tailwind/13-state-variants
topic: tailwind
slug: state-variants
title: "State Variants"
type: doc
order: 13
status: ready
tags: [tailwind, state-variants]
related: [tailwind/14-pseudo-classes, tailwind/12-dark-mode, tailwind/11-responsive-design, tailwind/22-accessibility, tailwind/02-core-concepts]
when_to_use: "Read before styling interactive states — hover, focus, disabled, group/peer, or aria/data-driven UI."
---
# State Variants

## Purpose

This document defines how to style interactive and conditional states in
Tailwind CSS v4 with variants: `hover:`, `focus:`, `focus-visible:`, `active:`,
`disabled:`, and the relational and data-driven variants `group-*`, `peer-*`,
`aria-*`, `data-*`, and `has-*`. It is written so an agent can make UI respond to
interaction correctly — including with a keyboard, not just a mouse.

A variant is a prefix that scopes a utility to a condition:
`hover:bg-blue-700` applies `bg-blue-700` only while hovered. Variants stack
left-to-right (`dark:md:hover:...`) and compose with responsive and dark-mode
prefixes covered in [11-responsive-design](11-responsive-design.md) and
[12-dark-mode](12-dark-mode.md).

## Why It Matters

Interactive state is where accessibility bugs hide. `hover:` alone leaves
keyboard and touch users with no feedback. Removing focus outlines "because they
look ugly" strands every keyboard user. Styling `focus:` instead of
`focus-visible:` makes a persistent ring appear on mouse clicks, which designers
then ask you to remove — reintroducing the accessibility hole. And driving state
off ad-hoc JS class toggles, instead of `aria-*`/`data-*` variants, splits the
source of truth between markup and script. Variants let one accessible source of
truth drive both behavior and appearance.

## Core Principles

- **Every hover has a focus.** Any state you express with `hover:` must also be
  reachable with `focus-visible:`. Keyboard users get the same affordance.
- **Prefer `focus-visible:` over `focus:` for rings.** `focus-visible:` shows the
  ring only for keyboard/programmatic focus, not on every mouse click — so you
  never need to hack the outline away.
- **Never remove focus styling without replacing it.** `outline-none` /
  `focus:outline-none` is only acceptable when paired with a visible
  `focus-visible:ring-*`.
- **Drive state from accessible attributes.** Use `aria-*` and `data-*` variants
  so `aria-expanded`, `aria-disabled`, `data-state` both convey semantics *and*
  style the element. One attribute, two jobs.
- **Use `group`/`peer` for relational state.** Style a child from a parent's
  state (`group-hover:`) or a sibling from another's (`peer-checked:`) instead of
  wiring JS.

## Best Practices

- Pair interactive utilities: `hover:bg-blue-700 focus-visible:bg-blue-700`, or
  factor the shared value so both paths match.
- Style disabled explicitly: `disabled:opacity-50 disabled:cursor-not-allowed
  disabled:pointer-events-none`. Do not rely on the browser default alone.
- For a parent-driven child, mark the parent `class="group"` and use
  `group-hover:`, `group-focus-within:`, `group-aria-expanded:`. Name groups
  (`group/item`, `group-hover/item:`) when they nest.
- For sibling-driven UI (custom checkbox, floating label), mark the input
  `class="peer"` and style the sibling with `peer-checked:`, `peer-invalid:`,
  `peer-placeholder-shown:`.
- Use `has-*` for parent-reacts-to-child styling
  (`has-[:checked]:border-blue-500`) instead of a JS `onChange` toggle.
- Match `aria-*`/`data-*` variants to the attributes your JS already sets, so
  there is a single source of truth: `aria-expanded:rotate-180`,
  `data-[state=open]:block`.

## Examples

**Good Example** — keyboard-safe focus, attribute-driven, relational

```html
<!-- outline-none is SAFE because a visible focus-visible ring replaces it -->
<button
  class="rounded bg-blue-600 px-4 py-2 text-white
         hover:bg-blue-700
         focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-400
         disabled:opacity-50 disabled:cursor-not-allowed"
>Save</button>

<!-- aria-expanded is the single source of truth: JS sets it, CSS reacts -->
<button aria-expanded="false" class="group">
  <svg class="transition group-aria-expanded:rotate-180">…</svg>
</button>

<!-- peer: the input's state styles its sibling, no JS needed -->
<label>
  <input type="checkbox" class="peer sr-only" />
  <span class="opacity-50 peer-checked:opacity-100">Enabled</span>
</label>
```

**Bad Example** — mouse-only, focus removed, split state

```html
<!-- BUG: hover only → no keyboard/touch feedback -->
<!-- BUG: outline removed with no replacement → invisible keyboard focus -->
<button class="bg-blue-600 hover:bg-blue-700 focus:outline-none">Save</button>

<!-- BUG: state lives only in a JS class, not aria/data → not accessible,
     and appearance can drift out of sync with real state -->
<button class="js-open">
  <svg class="rotate-icon">…</svg>
</button>
```

## Common Mistakes

- Providing `hover:` without a matching `focus-visible:` state.
- `focus:outline-none` (or `outline-none`) with no `focus-visible:ring-*`
  replacement, deleting the keyboard focus indicator.
- Using `focus:` for rings, so they flash on every mouse click, then hacking them
  back off.
- Toggling appearance with bespoke JS classes instead of `aria-*`/`data-*`
  variants that also carry semantics.
- Reaching for JS to style a child from a parent's hover when `group-hover:` does
  it in markup.
- Forgetting the variant order matters when stacking with responsive/dark
  prefixes — read left to right as nested conditions.

## Production Tips

- Add an ESLint/Stylelint or grep check that flags `outline-none` /
  `focus:outline-none` not accompanied by `focus-visible:ring`.
- Tab through every interactive element manually before shipping; a visible focus
  indicator on each is the acceptance test.
- When custom variants recur (`data-[state=open]:`), give them names via
  `@custom-variant` so intent is explicit and reusable.

## AI Review Checklist

- Does every `hover:` interaction have a matching `focus-visible:` state?
- Is any `outline-none`/`focus:outline-none` paired with a visible
  `focus-visible:ring-*`?
- Are rings driven by `focus-visible:` rather than `focus:`?
- Are `disabled:` styles set explicitly (opacity, cursor, pointer-events)?
- Is conditional styling driven by `aria-*`/`data-*` attributes that also carry
  semantics, not JS-only classes?
- Are relational states expressed with `group`/`peer`/`has-*` instead of JS?

## Related

- `knowledge/tailwind/14-pseudo-classes.md`
- `knowledge/tailwind/12-dark-mode.md`
- `knowledge/tailwind/11-responsive-design.md`
- `knowledge/tailwind/22-accessibility.md`
- `knowledge/tailwind/02-core-concepts.md`
