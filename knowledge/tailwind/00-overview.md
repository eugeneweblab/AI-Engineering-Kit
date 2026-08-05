---
id: tailwind/00-overview
topic: tailwind
slug: overview
title: "Tailwind CSS Overview"
type: doc
order: 0
status: ready
tags: [tailwind, overview, tailwind.config.js, text-lg, pt-4, gap-2, tailwindcss, display]
related: [tailwind/01-installation, tailwind/02-core-concepts, tailwind/03-utility-first, tailwind/04-layout, tailwind/05-flexbox]
when_to_use: "Read first when starting any Tailwind work to see how the topic's docs fit together."
---
# Tailwind CSS Overview

## Purpose

This document orients an agent to the `tailwind` topic. It explains what Tailwind CSS
is, which version this knowledge base targets, and how the sibling docs connect so you
can jump to the right one instead of guessing. It is a map, not a tutorial.

Tailwind CSS is a utility-first CSS framework: instead of writing custom stylesheets,
you compose designs from small, single-purpose classes (`flex`, `pt-4`, `text-center`)
applied directly in markup. This kit targets **Tailwind CSS v4** (Oxide engine,
CSS-first configuration), which is the current major version as of 2026.

## Why It Matters

Tailwind changed how teams write CSS, but its power is easy to misuse. Agents that
learned on v3 will emit deprecated patterns — `tailwind.config.js` content arrays,
`@tailwind base` directives, `npx tailwindcss init` — that silently break or no-op on
v4. Getting the mental model right up front (utilities, variants, the design token
system, and where configuration now lives) prevents a class of subtle bugs that pass
review but ship broken or bloated styles.

## Core Principles

- **Utility-first is the default.** Compose UI from utilities in the markup; reach for
  extracted components or `@apply` only when repetition becomes real duplication.
- **The design system is finite on purpose.** Tailwind constrains you to a spacing,
  color, and type scale so output stays consistent. Arbitrary values are an escape
  hatch, not the norm.
- **Configuration is CSS, not JavaScript (v4).** Theme tokens live in an `@theme` block
  in your CSS. There is no required `tailwind.config.js`.
- **Responsive and state styling are variants, not media-query files.** `md:`, `hover:`,
  `dark:`, and `focus-visible:` prefixes encode context inline.

## How The Docs Fit Together

- **Foundations** — start here. [01-installation](01-installation.md) sets up the build;
  [02-core-concepts](02-core-concepts.md) defines utilities, variants, and the token
  model; [03-utility-first](03-utility-first.md) explains the methodology and when to
  extract components.
- **Layout** — [04-layout](04-layout.md) covers `display`, `position`, and container
  behavior; [05-flexbox](05-flexbox.md) and `06-grid` cover the two layout engines;
  `07-spacing`, `08-sizing` cover the box model on the design scale.
- **Visual design** — `09-typography`, `10-colors`, and the customization docs
  (`15-customization`, `16-theme`, `21-design-system`) cover tokens and theming.
- **Adaptivity** — `11-responsive-design`, `12-dark-mode`, `13-state-variants`, and
  `14-pseudo-classes` cover context-sensitive styling.
- **Integration & quality** — `18-plugins`, `23-nextjs`, `24-react` cover ecosystem;
  `19-performance`, `20-optimization`, `27-production` cover shipping; `22-accessibility`,
  `25-debugging`, `26-best-practices`, `28-patterns` cover correctness.
- **Reference lists** — `98-production-checklist`, `99-ai-review-checklist`, and
  `100-common-antipatterns` are verifiable checklists you run against a diff.

## Best Practices

- Confirm the Tailwind major version before writing any config. Check `package.json`;
  if `tailwindcss` is `^4`, use CSS-first config and skip the JS config file entirely.
- Start from the most specific relevant doc. Layout question → `04`/`05`/`06`; theming
  question → `16-theme`; build question → `01-installation`.
- Prefer design-scale utilities (`p-4`, `text-lg`, `gap-2`) over arbitrary values
  (`p-[17px]`); the scale is what keeps a codebase visually coherent.

## Common Mistakes

- Assuming v3 mechanics on a v4 project (or vice versa). The config surface differs
  fundamentally; always version-check first.
- Treating Tailwind as inline styles. Utilities carry the design system, variants, and
  responsive logic that `style={{}}` cannot express.
- Reaching for custom CSS before checking whether a utility already exists.

## AI Review Checklist

- Is the Tailwind major version confirmed before any config change is proposed?
- Does the proposed pattern match the version's idioms (CSS `@theme` for v4)?
- Is the reader routed to the most specific sibling doc for their question?
- Are utilities and the design scale preferred over arbitrary values and inline styles?

## Related

- `knowledge/tailwind/01-installation.md`
- `knowledge/tailwind/02-core-concepts.md`
- `knowledge/tailwind/03-utility-first.md`
- `knowledge/tailwind/04-layout.md`
- `knowledge/tailwind/05-flexbox.md`
