---
id: html/24-html-email
topic: html
slug: html-email
title: "HTML Email"
type: doc
order: 24
status: ready
tags: [html, html-email, track, height, width, style, position]
related: [html/05-images, html/10-metadata, html/11-accessibility, html/19-security, html/08-forms]
when_to_use: "Read before building or reviewing any transactional or marketing email template."
---
# HTML Email

## Purpose

This document defines how to write HTML that renders correctly inside email clients.
Email is not the web: the markup is parsed by dozens of rendering engines — Outlook on
Windows uses Microsoft Word, Gmail strips your `<head>`, Apple Mail uses WebKit — none
of which behave like a modern browser. The goal is a single template that degrades
predictably everywhere, not one that is pretty in one client and broken in the rest.

## Why It Matters

An email cannot be patched after it is sent. Once a broadcast leaves the server it lands
in millions of inboxes exactly as written, and a layout that collapses in Outlook or a
CTA button that vanishes in dark mode costs conversions you can never recover. Email
clients are frozen a decade behind browsers: no external CSS, no flexbox or grid in
older Outlook, unreliable `<style>` support, and aggressive content clipping. Treat
email as a hostile, legacy rendering target and build defensively.

## Core Principles

- **Layout with tables, not `<div>` + CSS.** Flexbox and grid are unsupported or buggy
  across major clients. Nested `<table role="presentation">` is the only layout
  primitive that works everywhere.
- **Inline every style.** Gmail and others strip or ignore `<head><style>`. Styles must
  live in `style` attributes on each element, applied by an inliner at build time.
- **Assume no support for anything modern.** No JavaScript (stripped), no external
  stylesheets, no web fonts guaranteed, no `position`, limited background images.
- **Design for both light and dark mode.** Clients recolor your email; set explicit
  colors and test the dark rendering.
- **Every image is optional.** Many clients block images by default. The email must be
  legible and actionable with images off.

## Best Practices

- Use a fixed-width outer table (typically 600px) for consistency, with a single-column
  layout that reflows on mobile via a `max-width` media query.
- Set the character encoding and viewport in `<meta>`; declare
  `<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" ...>` — Outlook expects it.
- Give every `<img>` a meaningful `alt`, an explicit `width`/`height`, and
  `style="display:block"` to kill the gap under images.
- Build buttons as `<a>` styled with padding and background (bulletproof buttons), not
  as `<button>`; wrap in Outlook VML conditional comments if you need rounded corners.
- Provide a plain-text alternative part in the MIME message — it improves deliverability
  and serves clients that reject HTML.
- Include a visible unsubscribe link and a physical mailing address (legally required by
  CAN-SPAM / GDPR for marketing mail).
- Keep total HTML under ~100KB; Gmail clips messages past that and hides your footer.

## Examples

**Good Example** — table layout, inlined styles, accessible bulletproof button

```html
<!-- role="presentation" tells screen readers this table is layout, not data -->
<table role="presentation" width="600" cellpadding="0" cellspacing="0"
       style="margin:0 auto; background:#ffffff;">
  <tr>
    <td style="padding:24px; font-family:Arial,sans-serif; color:#111111;">
      <!-- explicit alt so the message works with images blocked -->
      <img src="https://cdn.example.com/logo.png" width="120" height="32"
           alt="Acme" style="display:block; border:0;">
      <p style="font-size:16px; line-height:24px;">Confirm your address.</p>
      <!-- a styled <a>, not a <button>: buttons render inconsistently in email -->
      <a href="https://example.com/confirm?t=abc"
         style="display:inline-block; padding:12px 24px; background:#0b5;
                color:#ffffff; text-decoration:none; border-radius:4px;">Confirm</a>
    </td>
  </tr>
</table>
```

**Bad Example** — browser assumptions that break in email

```html
<!-- flexbox is unsupported in Outlook; layout collapses -->
<div style="display:flex; gap:16px;">
  <!-- external stylesheet is stripped by Gmail: this class does nothing -->
  <link rel="stylesheet" href="/email.css">
  <div class="card">
    <!-- no alt, no dimensions: blocked-image state is a broken box -->
    <img src="/logo.png">
    <!-- JavaScript is removed by every client -->
    <button onclick="track()">Confirm</button>
  </div>
</div>
```

## Common Mistakes

- Using `<div>`/flexbox/grid for layout instead of nested presentation tables.
- Leaving styles in a `<style>` block that Gmail strips — always inline before sending.
- Omitting `alt` text and image dimensions, so image-blocking yields a broken layout.
- Relying on JavaScript, `<form>` submission, or web fonts to be honored — they aren't.
- Forgetting dark-mode testing, so dark text lands on a dark background.
- Shipping over 100KB and getting clipped by Gmail, hiding the unsubscribe link.

## Production Tips

- Run templates through a CSS inliner (e.g. as part of MJML or a build step) rather than
  hand-inlining; hand-inlining drifts out of sync with edits.
- Test on real clients with a service like Litmus or Email on Acid before every send;
  Outlook desktop and Gmail dark mode catch the most regressions.
- Author in MJML or a table-based framework so you write semantic blocks and the tool
  emits the bulletproof table soup for you.
- Use tracked, tokenized links (not inline JS) for click analytics.

## AI Review Checklist

- Is layout built from `role="presentation"` tables, not flex/grid `<div>`s?
- Are all styles inlined on elements, not left in a `<style>` block?
- Does every `<img>` have `alt`, explicit `width`/`height`, and `display:block`?
- Are CTAs styled `<a>` links rather than `<button>` or JavaScript?
- Does the email read correctly with images blocked and in dark mode?
- Is there a plain-text part, an unsubscribe link, and a sender address?
- Is the HTML under ~100KB to avoid Gmail clipping?

## Related

- `knowledge/html/05-images.md`
- `knowledge/html/10-metadata.md`
- `knowledge/html/11-accessibility.md`
- `knowledge/html/19-security.md`
- `knowledge/html/08-forms.md`
