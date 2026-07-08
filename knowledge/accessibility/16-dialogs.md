---
id: accessibility/16-dialogs
topic: accessibility
slug: dialogs
title: "Dialogs"
type: doc
order: 16
status: ready
tags: [accessibility, dialogs]
related: [accessibility/05-focus-management, accessibility/04-keyboard-navigation, accessibility/07-aria, accessibility/19-live-regions, accessibility/08-forms]
when_to_use: "Read before building any modal, dialog, popover, drawer, or overlay that takes over the screen."
---
# Dialogs

## Purpose

This document defines how to build a modal dialog that traps and returns focus
correctly, announces itself to a screen reader, and closes on `Escape`. A dialog is one
of the most commonly broken widgets on the web because it demands precise focus
management (see [focus management](05-focus-management.md)) — get any step wrong and a
keyboard or screen-reader user is either stranded inside it or lost behind it.

It is written so an agent can implement a modal that satisfies the WAI-ARIA Authoring
Practices dialog pattern without hand-rolling the fragile parts.

## Why It Matters

A modal makes a claim: "the rest of the page is inert; deal with me first." For a sighted
mouse user the dimmed backdrop enforces that claim. For a keyboard or screen-reader user,
nothing enforces it unless you write it. If focus is not moved into the dialog, the
screen reader keeps reading the page *behind* it. If focus is not trapped, `Tab` walks
out into the hidden page and the user is operating controls they cannot see. If focus is
not returned on close, it resets to the top of the document and the user loses their
place entirely.

Each of these is invisible to a mouse-based QA pass and immediately breaks the experience
for the users who rely on the keyboard.

## Core Principles

- **Move focus into the dialog on open**, to the dialog itself or its first meaningful
  control — never leave focus on the now-hidden trigger.
- **Trap focus while open.** `Tab` and `Shift+Tab` cycle within the dialog; focus never
  reaches the inert background.
- **Return focus to the trigger on close.** The user resumes exactly where they were.
- **`Escape` closes** a non-destructive dialog. Provide a visible, labelled close control
  too.
- **Announce it as a dialog** with `role="dialog"` (or `role="alertdialog"` for
  confirmations), `aria-modal="true"`, and an accessible name via `aria-labelledby`.
- **Make the background inert**, so assistive tech and pointer/keyboard cannot reach it.

## Best Practices

- Prefer the native `<dialog>` element with `dialog.showModal()`. It provides focus
  trapping, `Escape`-to-close, backdrop inertness, and top-layer stacking for free —
  reimplementing these in JS is where most bugs live.
- Label the dialog: point `aria-labelledby` at the heading, and use `aria-describedby`
  for supporting text if needed.
- Use `role="alertdialog"` for confirmations that interrupt (e.g., "Discard changes?") so
  screen readers treat it with urgency and read the message immediately.
- On close, restore focus to the element that opened the dialog; store that reference
  before opening.
- Make the backdrop click and `Escape` dismiss non-destructive dialogs, but require an
  explicit choice for destructive ones (do not let a stray click discard data).
- If you cannot use native `<dialog>`, apply `inert` to the rest of the page (or
  `aria-hidden="true"` on sibling landmarks) while the modal is open, and implement the
  focus trap explicitly.
- Prevent background scroll while the modal is open, but keep the dialog itself scrollable
  if its content overflows.

## Examples

**Good Example** — native `<dialog>`, focus and Escape handled by the platform

```html
<button id="open">Edit profile</button>

<dialog id="editDialog" aria-labelledby="editTitle">
  <h2 id="editTitle">Edit profile</h2>
  <form method="dialog">
    <!-- fields … -->
    <button value="cancel">Cancel</button>
    <button value="save">Save</button>
  </form>
</dialog>

<script>
  const dlg = document.getElementById("editDialog");
  const openBtn = document.getElementById("open");
  // showModal() traps focus, makes the background inert, closes on Escape,
  // and renders in the top layer. On close, the browser returns focus to
  // openBtn automatically because it had focus when showModal() was called.
  openBtn.addEventListener("click", () => dlg.showModal());
</script>
```

**Bad Example** — a div "modal" that never manages focus

```html
<!-- No role, no aria-modal, no focus move, no trap, no Escape, no return.
     A screen reader keeps reading the page behind this; a keyboard user
     tabs straight out of it into hidden controls and is lost. -->
<div class="modal" style="position:fixed">
  <h2>Edit profile</h2>
  <button onclick="hide()">Close</button>
</div>
```

## Common Mistakes

- Not moving focus into the dialog, so the screen reader keeps reading the page behind it.
- No focus trap, letting `Tab` escape to inert background controls.
- Not returning focus to the trigger on close, dropping the user at the top of the page.
- Missing `role="dialog"`/`aria-modal` and accessible name, so it is not announced as a
  dialog.
- `Escape` does not close it, or there is no keyboard-reachable close button.
- Background remains reachable (not `inert`), so users interact with hidden content.
- Using `role="alertdialog"` for routine dialogs, over-interrupting the screen reader.

## Production Tips

- Prefer native `<dialog>`; if a component library predates solid support, verify its
  focus trap and return with an actual keyboard, not a snapshot test.
- Write an end-to-end test that opens the dialog, asserts focus is inside, `Tab`s past the
  last control and asserts focus stayed in, presses `Escape`, and asserts focus returned
  to the trigger.

## AI Review Checklist

- Does focus move into the dialog on open and return to the trigger on close?
- Is focus trapped so `Tab`/`Shift+Tab` cannot reach the background?
- Does `Escape` close non-destructive dialogs, and is there a labelled close control?
- Does the dialog have `role="dialog"`/`aria-modal="true"` and an accessible name?
- Is the background made `inert` (or the native `<dialog>` used) so it is unreachable?
- Is `role="alertdialog"` used only for interrupting confirmations, not routine modals?
- Is background scroll prevented while the dialog is open?

## Related

- `knowledge/accessibility/05-focus-management.md`
- `knowledge/accessibility/04-keyboard-navigation.md`
- `knowledge/accessibility/07-aria.md`
- `knowledge/accessibility/19-live-regions.md`
- `knowledge/accessibility/08-forms.md`
