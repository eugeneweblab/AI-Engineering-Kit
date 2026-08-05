---
id: accessibility/28-real-world-patterns
topic: accessibility
slug: real-world-patterns
title: "Accessibility Real World Patterns"
type: doc
order: 28
status: ready
tags: [accessibility, real-world-patterns, aria-expanded, closeDialog, focus, aria-activedescendant, aria-selected, aria-live]
related: [accessibility/16-dialogs, accessibility/08-forms, accessibility/19-live-regions, accessibility/05-focus-management, accessibility/07-aria]
when_to_use: "Read before implementing a common interactive widget (modal, menu, tabs, autocomplete, toast, infinite scroll) so you follow the accessible pattern instead of inventing one."
---
# Accessibility Real World Patterns

## Purpose

This document shows accessible implementations of the widgets teams build over and over —
the ones that go wrong the most because they have no native HTML element and must be
assembled from ARIA, focus management, and keyboard handling. Each pattern names the parts
that make it work so an agent can build it correctly the first time or spot what a broken
one is missing.

These patterns compose the primitives from [ARIA](07-aria.md),
[focus management](05-focus-management.md), and [live regions](19-live-regions.md) into
the components users actually touch.

## Why It Matters

Custom widgets are where accessibility most often breaks, because the developer must
supply by hand everything a native element gives for free: role, state, keyboard behavior,
and focus. A modal that doesn't trap focus, a menu that ignores arrow keys, a toast the
screen reader never announces — each is a common, shippable defect that a demo never
reveals. Following the established pattern (WAI-ARIA Authoring Practices) means inheriting
a design that assistive-tech users already know, instead of debugging a novel one under a
deadline.

## Core Principles

- **Prefer native first.** Before building a custom widget, check whether `<dialog>`,
  `<details>`, `<select>`, or a semantic control already does the job with less code and
  more correctness.
- **Match the standard pattern.** Use the expected roles, states, and keys from the ARIA
  Authoring Practices so behavior meets user expectation.
- **Focus is part of the component.** Where focus goes on open, close, and interaction is
  as much a feature as the visuals. Design it explicitly.
- **Announce what changed.** If content appears, updates, or disappears without user focus,
  a live region must speak it or it is invisible to screen-reader users.
- **Test with the keyboard and a screen reader.** These widgets pass or fail on operation,
  not appearance; only real assistive tech confirms it.

## Best Practices

- **Modal dialog:** `role="dialog"` + `aria-modal="true"`, labeled by its title
  (`aria-labelledby`). Move focus into the dialog on open, **trap** Tab within it, close on
  **Escape**, and **return focus** to the trigger on close. See [dialogs](16-dialogs.md).
- **Menu / dropdown:** trigger with `aria-expanded` and `aria-controls`; items navigable by
  **arrow keys**, **Home/End**, and type-ahead; **Escape** closes and returns focus.
- **Tabs:** `role="tablist"/"tab"/"tabpanel"`, `aria-selected` on the active tab, arrow-key
  navigation, and roving `tabindex` so Tab enters the group once, not per tab.
- **Accordion / disclosure:** a real `<button>` toggles it with `aria-expanded`; prefer
  native `<details>`/`<summary>` when the styling allows.
- **Autocomplete / combobox:** follow the ARIA combobox pattern (`role="combobox"`,
  `aria-expanded`, `aria-activedescendant`); announce result counts via a live region.
- **Toast / notification:** render inside an `aria-live` region (`polite`, or `assertive`
  for errors) so it is announced without stealing focus. See [live regions](19-live-regions.md).
- **Infinite scroll / load-more:** provide a real "Load more" control as an alternative,
  manage focus to the first new item, and announce that items were added.

## Examples

**Good Example** — modal with the four load-bearing behaviors

```html
<button id="open" aria-haspopup="dialog">Edit profile</button>

<div role="dialog" aria-modal="true" aria-labelledby="dlgTitle" hidden id="dlg">
  <h2 id="dlgTitle">Edit profile</h2>
  <!-- ...fields... -->
  <button id="close">Cancel</button>
</div>

<script>
  // 1) Move focus IN on open  2) trap Tab  3) Escape closes  4) focus RETURNS on close.
  open.onclick = () => { dlg.hidden = false; dlg.querySelector("button,input").focus(); };
  dlg.addEventListener("keydown", (e) => { if (e.key === "Escape") closeDialog(); });
  function closeDialog() { dlg.hidden = true; open.focus(); } // return focus to trigger
</script>
```

**Bad Example** — a modal that is only visual

```html
<!-- No role, so it is not announced as a dialog. Focus stays on the page behind it,
     so a keyboard user tabs into the hidden content underneath. Escape does nothing.
     On close, focus is lost to <body>. It looks like a modal; it behaves like a div. -->
<div class="modal">
  <h2>Edit profile</h2>
  <button onclick="hide()">Cancel</button>
</div>
```

## Common Mistakes

- A modal that does not trap focus, so Tab escapes to the page behind it.
- Not returning focus to the trigger when a dialog, menu, or popover closes.
- Menus and tabs that respond to Tab per item instead of arrow keys with roving tabindex.
- Toasts and validation results that update the DOM silently, with no live region.
- Reinventing `<select>`, `<details>`, or `<dialog>` as divs and omitting their behaviors.
- Autocomplete lists with no announced result count, leaving SR users unsure what appeared.
- Infinite scroll with no keyboard path and no announcement of new content.

## Production Tips

- Wrap each pattern in a reviewed, reusable component; these are exactly the widgets whose
  correctness must not depend on each developer remembering every ARIA detail.
- Lean on a maintained headless library (e.g., Radix, React Aria, Headless UI) for the hard
  patterns; they encode focus and keyboard behavior you would otherwise re-derive and get wrong.
- Add a keyboard-and-screen-reader test for each widget's open/navigate/close cycle, since
  those transitions are where these patterns fail.

## AI Review Checklist

- Do dialogs set `aria-modal`, **trap focus**, close on **Escape**, and **return focus** to the trigger?
- Do menus, tabs, and listboxes use **arrow-key** navigation with roving `tabindex`, not Tab-per-item?
- Do toasts and async results announce via an **`aria-live`** region?
- Are the correct **roles and states** (`aria-expanded`, `aria-selected`, `aria-activedescendant`) present and updated?
- Was a **native element** considered before building the custom widget?
- Was each widget verified with a **keyboard and screen reader** through its full interaction cycle?

## Related

- `knowledge/accessibility/16-dialogs.md`
- `knowledge/accessibility/08-forms.md`
- `knowledge/accessibility/19-live-regions.md`
- `knowledge/accessibility/05-focus-management.md`
- `knowledge/accessibility/07-aria.md`
