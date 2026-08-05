---
id: tools/15-storybook
topic: tools
slug: storybook
title: "Storybook"
type: doc
order: 15
status: ready
tags: [tools, storybook]
related: [tools/14-playwright, tools/13-test-runners, tools/09-vite, tools/25-editor-setup, tools/30-engineering-principles, react/02-component-architecture, frontend/03-design-systems]
when_to_use: "Read before setting up Storybook or writing stories — documenting components in isolation, testing states, or wiring accessibility and visual checks."
---
# Storybook

## Purpose

This document defines how to use Storybook effectively: writing stories that document real
component states, keeping them useful as tests rather than decoration, and avoiding the
maintenance burden that makes teams abandon it.

## Why It Matters

Storybook's value is forcing components to be developed in isolation. A component that cannot
render outside the app is a component coupled to global state, routing, or a specific data
shape — and that coupling is exactly what makes it hard to test and reuse. Storybook surfaces
that immediately.

Its failure mode is equally predictable: stories written once at component creation, never
updated, showing only the happy path. That Storybook is a stale gallery, and the effort to
maintain it produces nothing.

## Core Principles

- **A story is a state, not a demo.** Loading, empty, error, overflowing, and disabled states
  are the ones worth capturing — the default state is visible in the app anyway.
- **Stories are test fixtures.** They can be rendered by the test runner, scanned for
  accessibility, and screenshotted for visual regression. That reuse is what justifies them.
- **If a component needs the whole app to render, fix the component.** Decorators exist for
  legitimate context (theme, i18n), not to reconstruct the application.
- **Co-locate stories with components.** A story in a distant directory goes stale
  immediately.

## Best Practices

```ts
// src/components/PlanCard/PlanCard.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { PlanCard } from './PlanCard';

const meta = {
  title: 'Commerce/PlanCard',
  component: PlanCard,
  parameters: {
    layout: 'centered',
    a11y: { config: { rules: [{ id: 'color-contrast', enabled: true }] } },
  },
  tags: ['autodocs'],            // generates a docs page from types and JSDoc
  args: {
    name: 'Professional',
    price: 4900,
    features: ['Unlimited projects', 'Priority support'],
  },
} satisfies Meta<typeof PlanCard>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const Featured: Story = {
  args: { featured: true },
};

// The states that actually break in production:
export const LongContent: Story = {
  args: {
    name: 'Enterprise Plus Extended Annual Commitment',
    features: Array.from({ length: 12 }, (_, i) => `A fairly long feature label ${i + 1}`),
  },
};

export const Loading: Story = { args: { loading: true } };

export const OutOfStock: Story = {
  args: { available: false },
};
```

Interaction tests turn a story into a behavioral test that runs in CI:

```ts
import { within, userEvent, expect } from '@storybook/test';

export const SelectsPlan: Story = {
  play: async ({ canvasElement, args }) => {
    const canvas = within(canvasElement);

    await userEvent.click(canvas.getByRole('button', { name: /choose/i }));

    await expect(args.onSelect).toHaveBeenCalledWith('professional');
  },
};
```

Global context belongs in decorators, declared once:

```tsx
// .storybook/preview.tsx
import type { Preview } from '@storybook/react';
import { ThemeProvider } from '../src/theme';
import '../src/styles/globals.css';

const preview: Preview = {
  decorators: [
    (Story) => (
      <ThemeProvider>
        <Story />
      </ThemeProvider>
    ),
  ],
  parameters: {
    controls: { expanded: true },
    backgrounds: { default: 'surface' },
  },
};

export default preview;
```

## Examples

**Good Example** — the story that catches a real defect

```ts
// Every card in the design has a two-word plan name. Production data does not.
export const OverflowingName: Story = {
  args: { name: 'Enterprise Plus Extended Annual Commitment Plan' },
};
```

This costs three lines and catches the truncation bug before it reaches a customer — the exact
case a Figma frame never shows.

**Bad Example** — stories that document nothing and break easily

```tsx
export const Primary = () => <Button>Click me</Button>;
export const Secondary = () => <Button variant="secondary">Click me</Button>;
export const Tertiary = () => <Button variant="tertiary">Click me</Button>;
// Three renderings of the same state. No loading, no disabled, no long label,
// no focus state — none of the cases that actually fail.
```

**Bad Example** — a component that cannot be isolated

```tsx
export const Default: Story = {
  decorators: [
    (Story) => (
      <ReduxProvider store={createRealStore()}>
        <RouterProvider router={createRealRouter()}>
          <ApolloProvider client={createRealClient()}>
            <AuthProvider><Story /></AuthProvider>
          </ApolloProvider>
        </RouterProvider>
      </ReduxProvider>
    ),
  ],
};
```

Four providers to render one card is a finding about the component, not about Storybook. The
data should arrive as props.

## Common Mistakes

- Stories for the default state only.
- Stories kept away from their components, going stale unnoticed.
- Storybook installed and never run in CI, so broken stories accumulate.
- Reconstructing the application in decorators instead of decoupling the component.
- Real network calls in stories rather than mocked handlers (MSW).
- Duplicating the design system's documentation site rather than replacing it.
- No accessibility addon, missing the cheapest automated check available at this level.
- A build that is never deployed, so designers and reviewers cannot see it.

## Production Tips

- Run `test-storybook` in CI: it renders every story, executes `play` functions, and fails on
  render errors — cheap coverage of every declared state.
- Add `@storybook/addon-a11y`; scanning components in isolation catches contrast and labelling
  issues before they are composed into a page.
- Deploy the static build (`storybook build`) per branch so design review happens on real
  components rather than screenshots.
- Feed stories into visual regression, where each story becomes a snapshot — see
  [Figma — Visual Regression](../figma/13-visual-regression.md).
- Use MSW for network-dependent components so stories stay deterministic.
- Track build time: a Storybook that takes five minutes to start stops being used.

## AI Review Checklist

- Does every component have stories for its non-default states?
- Are stories co-located with their components?
- Do decorators supply only genuine global context?
- Does CI render stories and run interaction tests?
- Is the accessibility addon enabled?
- Are network calls mocked rather than real?
- Is the built Storybook deployed somewhere reviewers can reach it?

## Related

- `knowledge/tools/14-playwright.md`
- `knowledge/tools/13-test-runners.md`
- `knowledge/tools/09-vite.md`
- `knowledge/tools/25-editor-setup.md`
- `knowledge/tools/30-engineering-principles.md`
- `knowledge/react/02-component-architecture.md`
- `knowledge/frontend/03-design-systems.md`
