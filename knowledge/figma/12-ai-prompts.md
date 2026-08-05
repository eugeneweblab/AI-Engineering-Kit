---
id: figma/12-ai-prompts
topic: figma
slug: ai-prompts
title: "AI Prompting Standard for Figma Tasks"
type: doc
order: 12
status: ready
tags: [figma, ai-prompts, TypeScript, passes, WordPress]
related: [figma/01-figma-analysis, figma/11-ai-design-review, prompts/01-code-review]
when_to_use: "Read when writing prompts for an AI coding assistant to implement Figma tasks with minimal ambiguity."
---
# AI Prompting Standard for Figma Tasks

## Purpose

This document defines the standard workflow for interacting with AI coding assistants when implementing Figma designs.

The objective is to minimize ambiguous instructions, reduce implementation iterations, and ensure that every task follows the project's engineering standards.

This document applies to Cursor, Claude Code, Codex, GitHub Copilot, Cline, Gemini CLI, and any future AI coding assistant.

---

## Core Principle

Never ask AI to "implement the design."

Instead, provide enough context for AI to reason about the implementation.

Better context produces better code.

---

## Standard Prompt Structure

Every implementation request should contain the following information.

```
Task
↓
Business Goal
↓
Design Source
↓
Technical Stack
↓
Existing Architecture
↓
Constraints
↓
Expected Result
↓
Definition of Done
```

Do not skip sections.

---

## Required Context

Every prompt should answer these questions.

## What should be implemented?

Example:

```
Implement the Hero section.
```

---

## Why does it exist?

Example:

```
This section is the primary marketing CTA.
```

---

## Which technologies are used?

Example:

```
WordPress

Divi

PHP

TypeScript

SCSS

React

Next.js
```

---

## Which architecture should be respected?

Example:

```
Reuse existing components.

Do not duplicate business logic.

Follow the existing design system.

Use semantic HTML.

Follow project coding standards.
```

---

## Which files are relevant?

Example:

```
Current component

Existing Button component

Typography utilities

Theme variables

Shared SCSS
```

---

## Which restrictions exist?

Examples:

```
Do not change unrelated files.

Do not rename public APIs.

Preserve backward compatibility.

Avoid unnecessary dependencies.

Reuse existing CSS variables.

Follow existing naming conventions.
```

---

## Required AI Workflow

Every implementation request should explicitly require AI to perform these steps.

```
Analyze Figma

↓

Analyze Existing Code

↓

Find Reusable Components

↓

Detect Design Tokens

↓

Create Implementation Plan

↓

Implement

↓

Review Own Changes

↓

Compare Against Design

↓

Return Final Result
```

Skipping analysis should be considered an error.

---

## Prompt Template

```
Task

Implement the Hero section from the provided Figma design.

Requirements

- Follow the project architecture.
- Reuse existing components.
- Preserve semantic HTML.
- Preserve accessibility.
- Preserve responsive behavior.

Before implementation:

1. Analyze the complete design.

2. Search the existing codebase.

3. Explain the implementation plan.

4. List reusable components.

5. Identify dynamic content.

6. Implement.

7. Review your own work.

8. Compare the result with the Figma design.

Do not implement anything until analysis has been completed.
```

---

## WordPress Example

```
Implement this section as a reusable WordPress component.

Requirements:

- Content must be editable.
- Reuse existing template parts.
- Reuse existing Gutenberg blocks if possible.
- Do not hardcode content.
- Follow project coding standards.
```

---

## Divi Example

```
Implement this section using Divi.

Requirements:

- Prefer native Divi modules.
- Create custom modules only if necessary.
- Keep content editable.
- Preserve responsive behavior.
- Avoid unnecessary custom CSS.
```

---

## React Example

```
Implement this section as a reusable React component.

Requirements:

- Functional component.
- TypeScript.
- Existing design system.
- Existing Button component.
- Existing Typography component.
- Responsive.
- Accessible.
```

---

## Next.js Example

```
Implement this page in Next.js.

Requirements:

- App Router.
- Server Components where appropriate.
- Optimize images.
- Preserve SEO.
- Avoid unnecessary client components.
```

---

## Review Prompt

Before considering the task complete, ask AI to perform a review.

```
Review your implementation.

Check:

- Design accuracy.
- Responsive behavior.
- Accessibility.
- Performance.
- Code duplication.
- Naming consistency.
- Existing component reuse.

Return every issue found before finishing.
```

---

## Anti-Patterns

Avoid prompts such as:

```
Implement this.

Make it look like Figma.

Fix the layout.

Improve this.

Make it responsive.
```

These prompts lack engineering context.

---

## Definition of Done Prompt

Every implementation should finish with confirmation that:

- requirements were satisfied;
- existing components were reused;
- design matches Figma;
- responsive behavior is correct;
- accessibility has been verified;
- unnecessary code has been avoided;
- implementation is production-ready.

---

## AI Checklist

Before starting:

☐ Requirements understood.

☐ Design analyzed.

☐ Existing code reviewed.

☐ Components identified.

☐ Architecture understood.

---

Before finishing:

☐ Design reviewed.

☐ Responsive verified.

☐ Accessibility verified.

☐ Performance reviewed.

☐ Self-review completed.

☐ Ready for production.

---

## Examples

**Good Example** — the prompt carries the node, the constraints, and the definition of done

```text
Implement the Product Card from Figma file KEY, node 44:12.

Context
  - Tokens already exist in src/styles/tokens.css as CSS custom properties.
  - Use the existing <Button> component from src/components/button.tsx.
  - The project uses CSS modules; no utility framework.

Constraints
  - Semantic HTML: the title is an <h3>, the action is a <button>.
  - Auto layout maps to flexbox; do not use absolute positioning.
  - Only 1440 and 375 frames exist. Do not invent an intermediate breakpoint —
    make the layout fluid between them.

Done when
  - Every colour and spacing value references a token, no literals.
  - The image declares width and height and has meaningful alt text.
  - npm run verify passes (typecheck, lint, unit tests).
```

**Bad Example** — a request with no anchor and no constraints

```text
Build the product card from the Figma design, make it look good and responsive.
```

There is no node id, so the wrong component may be built; no token instruction, so hex values
will be hardcoded; no breakpoint policy, so intermediate breakpoints will be invented; and no
definition of done, so "responsive" is settled by whoever reviews it.

---

## Summary

High-quality AI output begins with high-quality instructions.

The purpose of this standard is not to make prompts longer.

The purpose is to provide enough engineering context for AI to make correct decisions before writing code.

## Related

- `knowledge/figma/01-figma-analysis.md`
- `knowledge/figma/11-ai-design-review.md`
- `knowledge/prompts/01-code-review.md`
