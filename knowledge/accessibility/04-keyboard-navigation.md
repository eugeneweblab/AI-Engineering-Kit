---
id: accessibility/04-keyboard-navigation
topic: accessibility
slug: keyboard-navigation
title: "Keyboard Navigation"
type: doc
order: 4
status: ready
tags: [accessibility, keyboard-navigation]
related: [accessibility/05-focus-management, accessibility/03-semantic-html, accessibility/07-aria, accessibility/16-dialogs, accessibility/02-pour-principles]
when_to_use: "Read before building any interactive widget or reviewing a component, to guarantee it is fully operable without a mouse."
---
# Keyboard Navigation

## Purpose

This document defines how to make every interactive element operable from the keyboard
alone: what is focusable, in what order, and which keys do what. Keyboard operability is
the baseline that switch access, voice control, and most screen-reader use depend on. If a
feature works only with a mouse, it is broken for a large population — no exceptions.

## Why It Matters

Keyboard access is the [Operable pillar](02-pour-principles.md) in its purest form. Users
with motor disabilities, blind users (who cannot target a moving cursor), power users, and
anyone whose pointing device fails all navigate by Tab, Shift+Tab, arrow keys, Enter,
Space, and Escape. A single unreachable control or a keyboard *trap* — a place Tab enters
but cannot leave — can strand a user on the page with no way forward. Because a developer
testing with a mouse never hits these walls, keyboard failures ship silently unless you
deliberately unplug the mouse and try.

## Core Principles

- **Everything interactive is reachable and operable by keyboard.** Reachable via Tab;
  operable via the keys its role implies (Enter/Space for buttons, arrows for
  radio/menu/tabs). WCAG 2.1.1.
- **No keyboard traps.** Focus that enters a component must be able to leave it with Tab or
  Escape. WCAG 2.1.2. The exception — a modal dialog — traps *intentionally* but must
  release on close. See [dialogs](16-dialogs.md).
- **Focus order follows reading order.** Tab moves in a logical sequence that matches the
  visual/DOM order. Never use positive `tabindex` to reorder — it breaks the natural flow.
- **Use the right `tabindex`.** `tabindex="0"` adds a custom element to the tab order;
  `tabindex="-1"` makes it focusable only programmatically (for `.focus()`); positive
  values are an anti-pattern.
- **Honor platform key conventions.** Follow the ARIA Authoring Practices Guide for
  composite widgets: arrow keys move within a group (menu, tabs, listbox), Tab moves
  *between* widgets. Don't invent bindings.

## Best Practices

- Prefer native controls so keyboard behavior comes for free; see
  [semantic HTML](03-semantic-html.md). Reach for custom key handling only for genuine
  custom widgets.
- Provide a **"Skip to main content"** link as the first focusable element so keyboard
  users bypass repeated nav. It may be visually hidden until focused.
- Support **Escape** to dismiss dialogs, menus, and popovers, and **Enter/Space** to
  activate buttons — users expect these.
- Implement a **roving tabindex** (or `aria-activedescendant`) for composite widgets: one
  stop in the tab order for the whole group, arrows to move inside it. A menu with ten
  items should be one Tab stop, not ten.
- Never remove focus outlines without replacing them with an equally visible indicator;
  see [focus management](05-focus-management.md).

## Examples

**Good Example** — a custom toggle that is fully keyboard-operable

```html
<button type="button" id="mute" aria-pressed="false">Mute</button>
<script>
  const btn = document.getElementById("mute");
  // Because it's a real <button>, it is already focusable and fires on
  // BOTH Enter and Space with no key handling. We only toggle state.
  btn.addEventListener("click", () => {
    const on = btn.getAttribute("aria-pressed") === "true";
    btn.setAttribute("aria-pressed", String(!on)); // state announced to AT
  });
</script>
```

**Bad Example** — a div toggle that a keyboard cannot reach or operate

```html
<div class="toggle" onclick="toggleMute()">Mute</div>
<!-- Not in the tab order (no tabindex), so Tab skips it entirely.
     Even if focused, it has no key handler: Enter and Space do nothing.
     A keyboard or switch user can never mute the audio. -->
```

## Common Mistakes

- Click handlers on non-focusable elements (`<div>`, `<span>`) — unreachable by Tab and
  deaf to Enter/Space.
- Adding `tabindex="0"` but forgetting the key handlers, so the element focuses but can't
  be activated.
- Positive `tabindex` values (`tabindex="3"`) that scramble focus order and are a
  maintenance trap.
- Custom dropdowns/menus that make every item a Tab stop instead of using roving tabindex.
- Keyboard traps: a widget (often a modal or embedded editor) that Tab cannot escape.
- Removing `:focus` outlines for aesthetics, leaving keyboard users unable to see where
  they are.

## Production Tips

- Test the whole flow with the mouse physically unplugged (or hands off it): Tab from the
  top, reach every control, activate each, and confirm Tab always escapes.
- Add automated coverage where feasible — e.g. `@testing-library` `userEvent.tab()` to
  assert focus order and that dialogs trap and release correctly.

## AI Review Checklist

- Can every interactive element be reached with Tab and operated with its expected keys?
- Is there a keyboard trap anywhere, and does every intentional trap (modal) release on
  close?
- Does focus order match reading order, with no positive `tabindex`?
- Do composite widgets use a roving tabindex / `aria-activedescendant` (one Tab stop, arrow
  navigation inside)?
- Are Escape (dismiss) and Enter/Space (activate) wired up where expected?
- Is a "skip to content" link present as the first focusable element?

## Related

- `knowledge/accessibility/05-focus-management.md`
- `knowledge/accessibility/03-semantic-html.md`
- `knowledge/accessibility/07-aria.md`
- `knowledge/accessibility/16-dialogs.md`
- `knowledge/accessibility/02-pour-principles.md`
