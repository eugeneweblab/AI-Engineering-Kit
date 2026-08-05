---
id: html/04-links
topic: html
slug: links
title: "HTML Links"
type: doc
order: 4
status: ready
tags: [html, links]
related: [html/02-semantic-html, html/03-text-elements, html/11-accessibility, html/19-security, html/12-seo]
when_to_use: "Read before adding, reviewing, or refactoring any <a> element, navigation, or anchor target."
---
# HTML Links

## Purpose

This document defines how to use the anchor element `<a>` correctly: when a link is the
right element (versus a button), how to write accessible link text, how to target new tabs
safely, and how to secure and annotate outbound links. It is written so an agent produces
links that are navigable, safe, and understandable out of context.

Links are the connective tissue of the web and the primary affordance for keyboard and
screen-reader users. Getting them right is both an accessibility and a [security](19-security.md)
concern.

## Why It Matters

Links are what search crawlers follow, what screen-reader users list and jump between, and
what the entire web is built from. A link with the text "click here" is useless when a
screen reader reads the page's links as a standalone list — the destination is invisible. A
link that should have been a button hijacks navigation semantics; a button that should have
been a link breaks "open in new tab" and back-button behavior. And a `target="_blank"` link
without `rel="noopener"` hands the opened page scripting access back to yours — a real
security hole. Each of these renders fine and fails silently for exactly the users and tools
that depend on links most.

## Core Principles

- **Links navigate; buttons act.** Use `<a href>` when the result is going somewhere (a URL,
  a fragment, a download). Use `<button>` when the result is an action on the current page.
  Never swap them.
- **A link needs an `href`.** An `<a>` without `href` is not focusable and not a link.
  Never use `<a href="#" onclick>` as a button — that is a button.
- **Link text must make sense alone.** The accessible name should describe the destination
  without surrounding context. Avoid "click here", "read more", "this link".
- **Opening a new tab is a security and UX decision.** `target="_blank"` requires
  `rel="noopener"` and should be reserved for cases where leaving the page loses work.
- **Annotate untrusted and special links.** Use `rel` values to declare intent to browsers
  and crawlers.

## Best Practices

- Write self-describing link text: `<a href="/pricing">View pricing plans</a>`, not
  "click here". If the visible text must be generic, add `aria-label` with the full meaning.
- For same-page navigation use fragment links (`href="#section-id"`) targeting an element
  with a matching `id`; ensure the target can receive focus.
- On `target="_blank"`, always add `rel="noopener"` (modern browsers imply it, but declare
  it) and add `noreferrer` when you do not want to leak the referring URL.
- On user-generated or untrusted outbound links, add `rel="nofollow ugc"` (and `noopener
  noreferrer`) so you do not vouch for or expose data to them.
- Use protocol links where appropriate: `mailto:`, `tel:`, and `download` on `<a>` for file
  downloads; give `download` a filename when you control it.
- Style `:focus-visible` distinctly and never remove focus outlines — keyboard users rely on
  them to see which link is active. See [accessibility](11-accessibility.md).
- Do not disable browser back/forward or hijack normal link clicks in a way that breaks
  middle-click, Ctrl/Cmd-click, or "open in new tab".

## Examples

**Good Example** — descriptive, safe, correct element

```html
<!-- Navigation → <a>. Text describes the destination on its own. -->
<a href="/reports/q2-2026">Download the Q2 2026 report (PDF)</a>

<!-- New tab: noopener prevents the target from scripting this page via window.opener -->
<a href="https://partner.example.com" target="_blank" rel="noopener noreferrer">
  Partner portal (opens in a new tab)
</a>

<!-- Action on this page → <button>, not a link -->
<button type="button" data-action="expand">Show more details</button>
```

**Bad Example** — vague text, unsafe target, link-as-button

```html
<a href="/reports/q2-2026">click here</a>       <!-- text meaningless out of context -->

<a href="https://partner.example.com" target="_blank">Partner portal</a>
<!-- missing rel="noopener": opened page gets window.opener access to this one -->

<a href="#" onclick="expand()">Show more</a>
<!-- link with no real destination used as a button: breaks keyboard + navigation semantics -->
```

## Common Mistakes

- Non-descriptive link text ("click here", "read more") that fails when links are read as a list.
- Using `<a href="#">` or `<a>` with only `onclick` instead of a `<button>` for actions.
- `target="_blank"` without `rel="noopener"`, exposing your page to reverse tabnabbing.
- Removing `:focus` outlines for aesthetics, stranding keyboard users.
- Fragment links pointing to an `id` that does not exist, or a target that cannot take focus.
- Not marking untrusted user-submitted links with `rel="nofollow ugc noopener noreferrer"`.

## Production Tips

- Crawl the site in CI for broken internal links and dangling fragment targets; dead links
  erode trust and SEO.
- For links that open documents, state the format and size in the text ("(PDF, 2 MB)") so
  users are not surprised by a large download or a new file type.
- Prefer relative or root-relative internal URLs so links survive domain and environment changes.

## AI Review Checklist

- Is every navigational action an `<a href>` and every in-page action a `<button>`?
- Does each link's text describe its destination without relying on surrounding context?
- Do all `target="_blank"` links include `rel="noopener"` (and `noreferrer` where needed)?
- Are untrusted/outbound links annotated with appropriate `rel` values?
- Do focus styles remain visible, and do links honor modifier-click/new-tab behavior?
- Do fragment links resolve to an existing, focusable target `id`?

## Related


- `knowledge/html/02-semantic-html.md`
- `knowledge/html/03-text-elements.md`
- `knowledge/html/11-accessibility.md`
- `knowledge/html/19-security.md`
- `knowledge/html/12-seo.md`
