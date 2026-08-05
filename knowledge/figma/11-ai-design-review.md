---
id: figma/11-ai-design-review
topic: figma
slug: ai-design-review
title: "AI Design Review Protocol"
type: doc
order: 11
status: ready
tags: [figma, ai-design-review]
related: [figma/10-design-qa, figma/16-accessibility-from-figma, ai/06-self-verification]
  - figma/01-figma-analysis
  - figma/03-design-token-extraction
  - figma/06-component-detection
  - figma/12-ai-prompts
  - figma/10-design-qa
  - figma/20-implementation-definition-of-done
  - workflows/01-implement-figma-design
  - ai/01-context-gathering
  - ai/02-task-planning
  - ai/06-self-verification
  - engineering/05-context-first-development
when_to_use: "Read as an AI assistant before implementing a Figma design, to follow the mandatory analyze-plan-reuse-verify reasoning process."
---
# AI Design Review Protocol

## Purpose

This document defines the mandatory reasoning process that every AI coding assistant must follow before implementing a Figma design.

The objective is to ensure that implementation is based on analysis, planning, reuse, and verification rather than immediate code generation.

Implementation without analysis is considered incomplete.

---

## Core Principle

Think before writing code.

The first response to a Figma design should never be code.

The first response should always be analysis.

---

## Primary Rule

When receiving a Figma task:

DO NOT immediately generate HTML, React, PHP, CSS or JavaScript.

Instead, complete the full review process described below.

Only after every phase has been completed may implementation begin.

---

## Mandatory Review Pipeline

Every implementation must follow this exact order.

```
Receive Design

        ↓

Understand Requirements

        ↓

Analyze Entire Page

        ↓

Identify Sections

        ↓

Identify Existing Components

        ↓

Identify Dynamic Content

        ↓

Identify Design Tokens

        ↓

Analyze Auto Layout

        ↓

Analyze Responsive Behavior

        ↓

Choose Architecture

        ↓

Implementation Plan

        ↓

Search Existing Code

        ↓

Implementation

        ↓

Self Review

        ↓

Compare Against Figma

        ↓

Fix Differences

        ↓

Final Verification
```

Skipping any phase is considered an implementation failure.

---

## Phase 1 — Understand Requirements

Determine:

- business objective;
- user goal;
- expected functionality;
- editing requirements;
- supported devices;
- accessibility expectations.

Never implement assumptions.

---

## Phase 2 — Analyze the Entire Design

Review the complete page before inspecting individual components.

Identify:

- page hierarchy;
- visual hierarchy;
- repeated sections;
- interaction patterns;
- navigation;
- layout consistency.

Never begin implementation after reviewing only one section.

---

## Phase 3 — Detect Existing Components

Search the project for:

- React components;
- WordPress templates;
- Gutenberg blocks;
- Divi modules;
- shared utilities;
- CSS components;
- design system elements.

The preferred solution is almost always reuse.

Search the repository before claiming a component does not exist — the claim has to be
verified, not assumed:

```bash
# Component definitions by name, whatever the stack.
rg -n --glob '!node_modules' -e 'function (Button|Card|Modal)' \
                             -e 'export (default )?(const|function) (Button|Card|Modal)'

# React/Vue/Svelte components in the shared UI layer.
fd -e tsx -e jsx -e vue -e svelte . src/components src/ui 2>/dev/null

# WordPress: registered blocks, shortcodes, and Divi modules.
rg -n 'register_block_type|add_shortcode|ET_Builder_Module' --glob '*.php'

# Design tokens already defined in the project.
rg -n 'theme\.extend|:root\s*\{|--color-|\$spacing-' \
   tailwind.config.* theme.json src/styles 2>/dev/null
```

Report the result explicitly in the analysis — "no existing `PlanCard`; `Button` found at
`src/components/ui/Button.tsx` and will be reused" — so the reviewer can check the claim. See
[Component Detection](06-component-detection.md) and
[AI — Context Gathering](../ai/01-context-gathering.md).

---

## Phase 4 — Detect Dynamic Content

Classify every visible element.

Categories include:

- static content;
- WordPress content;
- API data;
- WooCommerce data;
- user-generated content;
- configuration values.

Never hardcode data that belongs to a CMS or API.

Classify every text and image node before implementing, and name the source for each:

| Element in design | Classification | Source | Implementation |
|---|---|---|---|
| "Simple pricing" headline | static | copy deck | literal in template |
| Plan name, price, features | API data | Stripe products | props from server component |
| "Trusted by 4,000 teams" | CMS content | WP option / CMS field | editable field, never a literal |
| Customer logos | CMS media | media library | `next/image` with explicit dimensions |
| Currency symbol | configuration | locale config | formatter, not a hardcoded `$` |

Anything in the last three rows that reaches the code as a string literal is a defect, even
when it renders correctly today. It will be wrong the first time an editor changes it.

---

## Phase 5 — Detect Design Tokens

Extract:

- typography;
- spacing;
- colors;
- border radius;
- shadows;
- breakpoints;
- icon sizes.

Always search for existing tokens before creating new ones.

---

## Phase 6 — Analyze Layout

Review:

- containers;
- grid;
- Auto Layout;
- nesting;
- alignment;
- constraints.

Reproduce behavior instead of appearance.

---

## Phase 7 — Analyze Responsive Behavior

Review:

Desktop

↓

Laptop

↓

Tablet

↓

Mobile

Document:

- layout changes;
- stacking;
- spacing;
- typography;
- interactions.

Never invent responsive behavior unnecessarily.

---

## Phase 8 — Select Architecture

Choose:

- semantic HTML;
- reusable components;
- state management;
- data flow;
- WordPress architecture;
- React architecture.

Architecture decisions should precede implementation.

---

## Phase 9 — Create an Implementation Plan

Before writing code define:

- reusable components;
- file structure;
- implementation order;
- dependencies;
- risks;
- validation strategy.

Implementation should never be improvised.

---

## Phase 10 — Search Existing Code

Before creating anything new search for:

- similar layouts;
- shared utilities;
- helper functions;
- UI components;
- CSS utilities;
- templates.

Avoid duplicate implementations.

---

## Phase 11 — Implement

Only after all previous phases have been completed.

Implementation priorities:

1. correctness;
2. maintainability;
3. readability;
4. accessibility;
5. performance.

Speed is never the primary objective.

---

## Phase 12 — Self Review

After implementation review:

- HTML;
- CSS;
- JavaScript;
- responsiveness;
- accessibility;
- naming;
- architecture.

Review your own work before presenting it.

---

## Phase 13 — Compare With Figma

Review:

- layout;
- spacing;
- typography;
- colors;
- interactions;
- responsive behavior.

Every visual difference should have a justification.

---

## Phase 14 — Fix Differences

Before completing the task:

Correct:

- layout differences;
- spacing issues;
- responsive issues;
- accessibility issues;
- duplicated code;
- inconsistent naming.

Do not leave known problems unresolved.

---

## Phase 15 — Final Verification

Confirm:

☐ Requirements satisfied.

☐ Existing components reused.

☐ Responsive implementation complete.

☐ Accessibility verified.

☐ Performance acceptable.

☐ Design accurately reproduced.

☐ Code follows project standards.

Only then is the task complete.

---

## Expected AI Output

Before implementation, provide a concise summary covering:

## Design Analysis

- Sections identified
- Reusable components
- Dynamic content
- Responsive observations

## Implementation Plan

- Files to modify
- Components to reuse
- Components to create
- Potential risks

## Completion Report

- Completed work
- Design deviations (if any)
- Performance considerations
- Accessibility considerations

This creates transparency and reduces unnecessary revisions.

Emit it in a fixed shape, so a reviewer can scan it and a later agent can parse it:

```markdown
## Design Analysis — /pricing (Figma 2:10 · 2:11 · 2:12)

**Sections**: Hero · PlanGrid · ComparisonTable · FAQ · CTA
**Reuse**: Button (`src/components/ui/Button.tsx`), Badge, Accordion
**Create**: PlanCard — 6 occurrences, variants: grid | list
**Dynamic**: plans (Stripe API), testimonials (CMS), logo wall (CMS media)
**Tokens**: reuse color-surface, spacing-md/xl, radius-lg · new: shadow-plan-card (justified: no existing elevation matches)
**Responsive**: 3 cols → 2 cols @1024 → 1 col @768; ComparisonTable becomes a horizontally scrollable region on mobile
**Risks**:
  - Mobile frame omits ComparisonTable — assuming "scrollable, not hidden"; needs confirmation.
  - Plan names come from Stripe and are unbounded — card must wrap, design shows one line only.

## Implementation Plan
1. `PlanCard` component + story/test — no dependencies
2. `PlanGrid` section consuming `PlanCard`
3. Wire plans from the server; loading and empty states
4. Responsive pass, then accessibility pass

## Completion Report  <!-- filled after implementation -->
**Done**: …
**Deviations**: … (each with a reason)
**Verification**: breakpoints checked · axe clean · keyboard path verified
```

The `Risks` block is the most valuable part of the report: it converts silent assumptions into
questions a human can answer cheaply. See [AI — Task Planning](../ai/02-task-planning.md).

---

## AI Self-Questions

Before writing code ask:

- Do I understand the entire page?
- Have I searched for existing components?
- Am I duplicating existing functionality?
- Have I identified all reusable patterns?
- Have I planned responsive behavior?
- Can this solution be simplified?
- Would another engineer understand this implementation?

If any answer is uncertain, continue analysis.

---

## Common Failures

Never:

Generate code immediately.

Copy Figma layer hierarchy.

Hardcode repeated values.

Ignore the design system.

Ignore accessibility.

Ignore responsiveness.

Duplicate existing components.

Implement before planning.

---

## Examples

**Good Example** — the review states evidence and confidence separately

```text
Review of PR #482 — Checkout page against Checkout / Desktop (node 12:340)

VERIFIED (measured against the file)
  ✓ palette matches Surface/Card, Ink/Primary, Accent/Blue
  ✓ spacing uses the 8-point scale throughout
  ✗ submit button 36×32, design says 44×44                    → change requested

NOT VERIFIABLE (absent from the design)
  ? mobile layout — no frame below 1440 exists in the file
  ? field error state — not designed; the implementation invented one
  → both raised as questions, not as findings

OUT OF SCOPE
  · the type scale differs from the design system doc; that is a system-level
    decision, not a defect in this PR
```

Separating "measured against the file" from "absent from the file" is what makes the review
usable: the first list is actionable now, the second is a question for the designer.

**Bad Example** — confident assertions with no source

```text
The design looks mostly implemented correctly. The spacing seems a bit tight in
places and the colours might be slightly off. The mobile version should probably
use a single column. Overall looks good, approving.
```

Every sentence hedges, none cites a node, and the mobile claim is invented — there is no
mobile frame to compare against. An approval on this basis records that a review happened
without any of the checking it implies.

---

## Completion Criteria

The protocol has been successfully followed when:

- all review phases are completed;
- implementation follows the project architecture;
- reusable components are prioritized;
- design differences have been reviewed;
- self-review has been completed;
- the implementation is considered production-ready.

---

## Related Knowledge

- [Figma Analysis](01-figma-analysis.md) — the analysis artifacts this protocol produces.
- [AI Prompting Standard for Figma Tasks](12-ai-prompts.md) — how the task should be phrased in the first place.
- [Design QA](10-design-qa.md) — the verification pass for Phases 13–15.
- [Implementation Definition of Done](20-implementation-definition-of-done.md) — the completion bar.
- [AI — Context Gathering](../ai/01-context-gathering.md), [AI — Task Planning](../ai/02-task-planning.md), and [AI — Self Verification](../ai/06-self-verification.md) — the general form of this protocol.
- [Engineering — Context-First Development](../engineering/05-context-first-development.md) — why analysis precedes generation.
- [Workflow — Implement a Figma Design](../workflows/01-implement-figma-design.md) — the end-to-end workflow.

---

## Summary

Professional engineering is defined not by how quickly code is written, but by how systematically problems are analyzed before implementation.

This review protocol transforms AI coding assistants from reactive code generators into disciplined engineering collaborators capable of producing predictable, maintainable, high-quality implementations.