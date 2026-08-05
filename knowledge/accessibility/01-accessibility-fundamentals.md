---
id: accessibility/01-accessibility-fundamentals
topic: accessibility
slug: accessibility-fundamentals
title: "Accessibility Fundamentals"
type: doc
order: 1
status: ready
tags: [accessibility, accessibility-fundamentals, nothing, closeDialog, prefers-color-scheme, prefers-reduced-motion]
related: [accessibility/02-pour-principles, accessibility/03-semantic-html, accessibility/06-screen-readers, accessibility/23-wcag, accessibility/26-legal-requirements]
when_to_use: "Read before your first UI task on a project, to understand who assistive technology serves and what standard we build to."
---
# Accessibility Fundamentals

## Purpose

This document establishes the shared vocabulary and mental model for the whole topic:
who uses assistive technology, how that technology consumes your markup, and what
standard ("WCAG 2.2 AA") we conform to. An agent that internalizes this will make the
right structural choices in every later doc rather than memorizing rules in isolation.

## Why It Matters

Roughly one in six people lives with a disability, and *every* user is temporarily or
situationally impaired at times — a broken arm, bright sunlight, a noisy room, a
trackpad that died. Accessibility work is not a niche accommodation; it is baseline
quality that widens who can use the product. The catch is that the harm is invisible to
a sighted developer using a mouse: the app looks perfect while a screen-reader user hits
a wall. Because you cannot see the failure, you must build to a *standard* and *verify*
against assistive tech, not against your own experience.

## Core Principles

- **The accessibility tree, not the pixels, is what assistive tech reads.** Browsers
  build a parallel tree from your DOM (roles, names, states). Screen readers, voice
  control, and switch access all consume it. If it is not expressed in markup, it does
  not exist to these users. See [screen readers](06-screen-readers.md).
- **Disability is a spectrum, and often temporary or situational.** Design for a range —
  visual (blindness, low vision, color blindness), motor (limited dexterity, no mouse),
  auditory (deafness), cognitive (memory, attention, dyslexia) — not one archetype.
- **Conform to WCAG 2.2 Level AA.** It is the shared, testable definition of "accessible"
  that laws reference. AA is the standard target; A is a floor; AAA is selective.
- **Accessible by default beats accessible by exception.** Native controls come with
  correct roles and keyboard behavior; custom ones start with none.

## Best Practices

- Learn the four **POUR** pillars (Perceivable, Operable, Understandable, Robust) and use
  them to categorize any issue you find. See [POUR principles](02-pour-principles.md).
- Know the main assistive technologies you must support: screen readers (VoiceOver on
  macOS/iOS, NVDA and JAWS on Windows, TalkBack on Android), screen magnifiers, voice
  control (Dragon, Voice Control), switch access, and keyboard-only navigation.
- Treat keyboard operability as the non-negotiable baseline — it underlies switch access
  and much of screen-reader use. See [keyboard navigation](04-keyboard-navigation.md).
- Prefer system settings over custom toggles: honor `prefers-reduced-motion`,
  `prefers-color-scheme`, and OS font-size/zoom instead of reinventing them.
- Include people with disabilities in usability testing; nothing substitutes for it.

## Examples

**Good Example** — a native control the accessibility tree understands

```html
<!-- <button> exposes role=button, is focusable, fires on Enter AND Space,
     and is announced as "Close, button" — all for free, on every platform. -->
<button type="button" aria-label="Close dialog">✕</button>
```

**Bad Example** — a control that exists only as pixels

```html
<!-- A <div> has no role, is not focusable, does not respond to Enter/Space,
     and is announced as nothing (or "clickable" at best). A screen-reader or
     keyboard user cannot perceive OR operate it — it is invisible to them. -->
<div class="btn" onclick="closeDialog()">✕</div>
```

## Common Mistakes

- Believing accessibility means "add alt text and ship." It is structural: semantics,
  keyboard, focus, contrast, and names all matter.
- Designing for a single disability (usually blindness) and ignoring motor and cognitive
  users, for whom timeouts, tiny targets, and motion are the real barriers.
- Confusing "looks fine to me" with "is accessible." The developer is rarely the user
  who is blocked.
- Treating WCAG AAA as the goal everywhere; some AAA criteria are impractical for general
  content. AA is the contract.

## Production Tips

- Add an accessibility statement page and a contact path for reporting barriers — it is
  often a legal requirement and a fast feedback channel. See
  [legal requirements](26-legal-requirements.md).
- Budget a manual assistive-tech pass into each release; automation alone is insufficient.

## AI Review Checklist

- Is every interactive thing a real control (or a properly-authored custom widget), not a
  bare `<div>`/`<span>` with a click handler?
- Does the change express role, name, and state in markup so the accessibility tree
  reflects it?
- Is the stated target WCAG 2.2 AA, and does the change hold to it?
- Are motor and cognitive users considered (target size, timeouts, motion), not only
  vision?
- Were system preferences honored rather than overridden?

## Related

- `knowledge/accessibility/02-pour-principles.md`
- `knowledge/accessibility/03-semantic-html.md`
- `knowledge/accessibility/06-screen-readers.md`
- `knowledge/accessibility/23-wcag.md`
- `knowledge/accessibility/26-legal-requirements.md`
