---
id: react/20-accessibility
topic: react
slug: accessibility
title: "React Accessibility"
type: doc
order: 20
status: ready
tags: [react, accessibility]
related: []
when_to_use: "Read before building or reviewing React UI to ensure it is accessible to all users and assistive technologies."
---
# React Accessibility

## Purpose

This document defines the engineering standards for building accessible React applications.

The objective is to ensure that every user, regardless of ability or assistive technology, can successfully interact with the application.

Accessibility is a fundamental quality attribute and must be considered throughout the entire development lifecycle rather than added after implementation.

---

## Core Principle

Accessibility is built in.

Not added later.

Every component should be accessible by default.

---

## Accessibility Workflow

Every feature should follow this workflow.

```
Design
        ↓
Implementation
        ↓
Semantic HTML
        ↓
Keyboard Support
        ↓
Screen Reader Review
        ↓
Testing
        ↓
Release
```

Accessibility should be verified during every stage.

---

## Semantic HTML

Always prefer semantic HTML over generic elements.

Good:

```html
<button>Save</button>

<nav>...</nav>

<main>...</main>

<form>...</form>
```

Avoid:

```html
<div onclick="...">Save</div>
```

Semantic elements provide accessibility without additional effort.

---

## Keyboard Accessibility

Every interactive element must support keyboard navigation.

Verify:

- Tab
- Shift + Tab
- Enter
- Space
- Escape
- Arrow keys (where appropriate)

Users should never require a mouse.

---

## Focus Management

Focus should remain predictable.

Examples:

- dialogs receive focus when opened;
- focus returns after dialogs close;
- validation moves focus to invalid fields;
- page navigation updates focus appropriately.

Never remove visible focus indicators without providing an accessible alternative.

---

## Forms

Every form field should provide:

- associated label;
- accessible name;
- validation feedback;
- required state;
- error description.

Avoid using placeholders as labels.

---

## Images

Every meaningful image requires alternative text.

Good:

```html
<img
    src="avatar.jpg"
    alt="Profile photo of John Doe"
/>
```

Decorative images should use empty alternative text.

```html
alt=""
```

---

## Buttons

Buttons should describe the action they perform.

Good:

```
Save Changes

Delete Account

Download Invoice
```

Avoid:

```
Click Here

Go

OK
```

Button labels should remain meaningful outside their visual context.

---

## Links

Links should describe their destination.

Good:

```
View Product Details
```

Avoid:

```
Read More

Click Here
```

Screen reader users often navigate through links independently.

---

## Headings

Maintain a logical heading hierarchy.

Example:

```
H1

    H2

        H3

    H2
```

Avoid skipping heading levels.

---

## ARIA

Prefer semantic HTML before using ARIA.

Use ARIA only when native HTML cannot express the required behavior.

Examples:

- aria-label
- aria-labelledby
- aria-describedby
- aria-expanded
- aria-live

No ARIA is better than incorrect ARIA.

---

## Dynamic Content

Inform assistive technologies about important UI changes.

Examples:

- loading completion;
- validation errors;
- successful submissions;
- notifications.

Use appropriate live regions when necessary.

---

## Dialogs

Accessible dialogs should:

- trap keyboard focus;
- restore focus when closed;
- support Escape;
- provide an accessible title;
- prevent interaction with background content.

---

## Tables

Use tables only for tabular data.

Provide:

- table headers;
- proper row and column relationships;
- captions when appropriate.

Do not use tables for layout.

---

## Color

Never communicate information using color alone.

Provide additional indicators such as:

- icons;
- text;
- patterns;
- labels.

Ensure sufficient color contrast.

---

## Motion

Respect user motion preferences.

Reduce or disable unnecessary animations when users request reduced motion.

Animations should never interfere with usability.

---

## Testing

Accessibility should be verified using multiple methods.

Examples:

- keyboard testing;
- screen reader testing;
- automated accessibility tools;
- manual review.

Automated tools cannot detect every accessibility issue.

---

## AI Execution Checklist

## Investigation

☐ Semantic structure reviewed.

☐ Keyboard interaction reviewed.

☐ Focus behavior reviewed.

☐ Form accessibility reviewed.

---

## Planning

☐ Select semantic HTML.

☐ Define accessible names.

☐ Plan keyboard support.

☐ Plan dynamic announcements.

---

## Verification

☐ Keyboard navigation works.

☐ Focus management correct.

☐ Semantic HTML used.

☐ Images have appropriate alternative text.

☐ Forms are accessible.

☐ Color is not the only indicator.

---

## Common Mistakes

Avoid:

Replacing buttons with clickable div elements.

Using placeholders as labels.

Removing focus outlines.

Skipping heading levels.

Using incorrect ARIA attributes.

Communicating only through color.

Ignoring keyboard users.

Testing accessibility only after implementation.

---

## Completion Criteria

Accessibility implementation is complete when:

- semantic HTML has been used;
- keyboard navigation is fully supported;
- focus management is correct;
- accessible names are present;
- forms provide appropriate feedback;
- dynamic content is announced when necessary;
- accessibility testing has been completed.

---

## Summary

Accessible React applications are built through thoughtful design, semantic HTML, and consistent engineering practices.

By treating accessibility as a core requirement rather than an optional enhancement, applications become more usable, inclusive, and maintainable for every user.