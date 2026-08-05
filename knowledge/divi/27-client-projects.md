---
id: divi/27-client-projects
topic: divi
slug: client-projects
title: "Client Projects"
type: doc
order: 27
status: ready
tags: [divi, client-projects, remove_cap, get_role, add_action]
related: [divi/24-best-practices, divi/23-maintenance, divi/06-global-elements, divi/22-deployment, divi/12-accessibility]
when_to_use: "Read when building a Divi site that a non-technical client will own and edit after handoff."
---
# Client Projects

## Purpose

This document covers what changes when a Divi site is built *for a client* rather than for
yourself: the goal is a site the client can safely edit after you are gone, without breaking
the layout or the performance work. It focuses on handoff, guardrails, and the build
decisions that make a site survive non-technical editing.

Most Divi sites are agency or freelance client work. The main risk is not the initial
build; it is what happens on the first client edit six weeks later.

## Why It Matters

Divi's biggest selling point to clients — "you can edit it yourself" — is also the biggest
threat to the build. A client dragging modules around, pasting styled text from Word, or
deleting a global element can undo hours of design and performance work in minutes. If the
build has no guardrails, every client edit is a support ticket. Designing for the client's
future editing is what makes a project profitable instead of an open-ended maintenance
liability.

## Core Principles

- **Lock down what must not change.** Use Divi's role editor and locked/global modules so a
  client can edit copy and images but not restructure the layout or delete the header.
- **Give editors one obvious place to edit.** Content the client updates should be in clearly
  labeled, unlocked modules; everything structural should be global or template-driven.
- **Reduce the ways to break it.** Fewer plugins, presets instead of inline CSS, and Theme
  Builder templates mean fewer surfaces where a client edit can go wrong.
- **Hand off knowledge, not just a login.** A short guide and a walkthrough prevent the most
  common post-launch mistakes. See [maintenance](23-maintenance.md).

## Best Practices

- Configure the **Divi Role Editor**: restrict non-admin roles from disabling advanced
  settings, editing the Theme Builder, or accessing code — give editors only what they need.
- Mark structural sections as **global** or **locked** so a client cannot accidentally move
  or delete a header, footer, or CTA. See [global-elements](06-global-elements.md).
- Build editable content as **plainly labeled modules** (admin labels like "Hero headline")
  so the client finds the right thing to edit quickly.
- Keep the **plugin count minimal** and document each one's purpose; every plugin is a future
  update and a way for the site to break.
- Provide a **child theme** and keep all custom code there, so the client (or the next agency)
  can update Divi without losing customizations.
- Deliver a **handoff package**: a backup/export of layouts and Theme Builder templates, a
  credentials list, a short "how to edit your site" doc, and the update procedure. See
  [deployment](22-deployment.md).
- Verify **accessibility** before handoff — clients rarely maintain it, so it must be right
  at launch. See [accessibility](12-accessibility.md).

## Examples

**Good Example** — role-based guardrails

```php
// child-theme/functions.php — restrict what an 'editor' can do in Divi.
// WHY: editors can update text/images but cannot open the code fields,
// disable the builder, or edit the Theme Builder, so structure stays intact.
add_action( 'init', function () {
  $role = get_role( 'editor' );
  if ( $role ) {
    $role->remove_cap( 'unfiltered_html' ); // no pasting arbitrary script/style
  }
} );
// Divi Theme Options > Role Editor: set Editor role -> disable "Divi Library",
// "Theme Builder", and "Code" so those areas are hidden from clients.
```

**Bad Example** — full admin, no guardrails, verbal handoff

```
- Client gets an Administrator account "so they can do anything."
- Header/footer are plain (non-global) sections on every page.
- No child theme; custom CSS lives in module Advanced tabs.
- Handoff is a 10-minute call and a password.

// Result: the client deletes the footer on one page, pastes Word HTML that
// breaks styling, and the next Divi update wipes the customizations.
```

## Common Mistakes

- Giving clients Administrator access when an Editor role with a locked builder would do.
- Leaving structural sections non-global, so a client edit removes a header or CTA sitewide.
- Unlabeled modules, so the client edits the wrong element or gives up and calls support.
- No child theme, so a Divi update erases custom work the client depends on.
- Handing off without a backup, export, or written editing guide.
- Shipping an inaccessible site the client has no ability to fix later.

## Production Tips

- Take a full export/backup at handoff and keep a copy; it is your baseline if a client edit
  goes wrong.
- Record a short screen-capture walkthrough of common edits — it deflects most support
  requests and is cheaper than answering them one by one.
- Agree in writing on who owns updates and maintenance after launch to avoid surprise support.

## AI Review Checklist

- Are client roles restricted (no code fields, Theme Builder, or builder-disable) via the Role Editor?
- Are structural elements global/locked so a client edit cannot delete or move them?
- Are editable modules clearly labeled for a non-technical user?
- Is all custom code in a child theme so Divi updates are safe?
- Does the handoff include a backup/export, credentials, and a written editing guide?
- Was accessibility verified before handoff, since the client cannot maintain it?

## Related

- `knowledge/divi/06-global-elements.md`
- `knowledge/divi/12-accessibility.md`
- `knowledge/divi/22-deployment.md`
- `knowledge/divi/23-maintenance.md`
- `knowledge/divi/24-best-practices.md`
