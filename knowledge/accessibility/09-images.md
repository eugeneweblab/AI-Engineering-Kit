---
id: accessibility/09-images
topic: accessibility
slug: images
title: "Accessibility Images"
type: doc
order: 9
status: ready
tags: [accessibility, images, cart]
related: [accessibility/03-semantic-html, accessibility/06-screen-readers, accessibility/07-aria, accessibility/10-color-and-contrast, accessibility/15-media]
when_to_use: "Read before adding any image, icon, chart, or graphic — or when writing alt text."
---
# Accessibility Images

## Purpose

This document defines how to make images perceivable to users who cannot see them:
choosing correct alternative text, hiding decoration, and describing complex graphics.
It is written so an agent can decide *whether* an image needs a text alternative and
*what* that text should say — the two decisions that get alt text wrong.

Alt text is not a caption and not a keyword dump. It is the answer to one question: *if
this image were replaced by words, what words would preserve the same meaning and
function?* Everything below follows from that.

## Why It Matters

Images carry information — a chart's trend, a button's action, a photo's content — that is
lost entirely to screen reader users if there is no text alternative. Empty or wrong alt
text is common and consequential: a missing `alt` makes the reader announce the file name
(`IMG_4821.png`), and a decorative flourish with verbose alt text floods the user with
noise. Alt text is also the single most-audited item in automated tools and legal reviews,
so getting it right is both a usability and a compliance requirement.

## Core Principles

- **Function over description.** Describe what the image *does or means* in context, not
  every pixel. A logo that links home should read "Home", not "blue circular logo".
- **Decorative images get empty alt.** If an image adds no information (spacers, ambient
  photos beside self-sufficient text), use `alt=""` so the reader skips it entirely.
- **Every `<img>` needs an `alt` attribute — even if empty.** A *missing* `alt` differs
  from an *empty* one: missing makes the reader fall back to the file name.
- **Text in images is a last resort.** Real text is selectable, translatable, and scalable;
  text baked into an image is none of these and must be repeated in `alt`.
- **Complex graphics need a longer description elsewhere.** Charts, diagrams, and maps carry
  more than one `alt` string can hold; provide the data in adjacent text or a table.

## Best Practices

- Write `alt` for the context: the same photo may be decorative in a hero and informative in
  a gallery. Judge by what the surrounding content already says.
- For linked or button images, the `alt` describes the *destination or action*, not the
  picture: `alt="Download the 2026 report (PDF)"`.
- Keep informative `alt` concise (roughly a sentence); put detail in a caption or body text.
  Do not start with "Image of" — the role already says it is an image.
- Mark decorative inline SVGs and icons with `aria-hidden="true"` and `focusable="false"`;
  give meaningful SVGs a `role="img"` and an accessible name.
- For charts, give a one-line `alt` summary plus a data table or text description nearby, so
  the actual numbers are available.
- Use `<figure>`/`<figcaption>` for images that need a visible caption; the caption
  complements `alt`, it does not replace it.
- Do not convey information by image alone when contrast or color also matters; see
  [color and contrast](10-color-and-contrast.md).

## Examples

**Good Example** — alt matched to function and decoration hidden

```html
<!-- Informative: the alt states the action the linked image performs. -->
<a href="/cart"><img src="cart.svg" alt="View cart (3 items)" /></a>

<!-- Decorative: adds nothing the caption doesn't; empty alt = skipped by readers. -->
<figure>
  <img src="team.jpg" alt="" />
  <figcaption>Our support team in the Berlin office.</figcaption>
</figure>

<!-- Meaningful icon: role + name make the SVG announce; decorative sibling hidden. -->
<button type="button">
  <svg role="img" aria-label="Delete"><!-- trash icon --></svg>
</button>
```

**Bad Example** — file name leak, redundant and useless alt

```html
<!-- No alt attribute: screen reader announces "IMG_4821.png". -->
<img src="IMG_4821.png" />

<!-- Redundant prefix and no function: the link's purpose is never conveyed. -->
<a href="/cart"><img src="cart.svg" alt="Image of a shopping cart icon" /></a>

<!-- Decorative image forced into speech, adding noise before the real caption. -->
<img src="divider.png" alt="decorative divider line separating sections" />
```

## Common Mistakes

- Omitting the `alt` attribute entirely, causing file-name announcements.
- Writing `alt` that describes the picture instead of its function (linked logos, icon
  buttons).
- Giving decorative images non-empty `alt`, cluttering the reading experience.
- Starting `alt` with "Image of" / "Picture of" — the role is already announced.
- Baking body text into an image (banners, quotes) with no equivalent in `alt` or nearby.
- Treating a chart's `alt` as sufficient, leaving the underlying data unavailable.
- Unlabeled meaningful SVGs, or decorative SVGs left visible to the accessibility tree.

## Production Tips

- Make `alt` a required field in your CMS/component API, with an explicit "decorative"
  checkbox that emits `alt=""` — this prevents both missing and lazy alt text.
- For data visualizations, generate the `alt` summary and an off-screen data table from the
  same source data so they cannot drift apart.
- Audit with automated tools for *missing* alt, but review text quality manually — no tool
  can tell whether the words are correct for the context.

## AI Review Checklist

- Does every `<img>` have an `alt` attribute (empty for decorative, descriptive otherwise)?
- Does informative `alt` describe the image's function/meaning, not its appearance?
- For linked/button images, does `alt` describe the destination or action?
- Are decorative images/SVGs given `alt=""` or `aria-hidden="true"`?
- Do complex graphics have a longer text or table equivalent nearby?
- Is text-in-image avoided, or fully duplicated in the alternative text?

## Related

- `knowledge/accessibility/03-semantic-html.md`
- `knowledge/accessibility/06-screen-readers.md`
- `knowledge/accessibility/07-aria.md`
- `knowledge/accessibility/10-color-and-contrast.md`
- `knowledge/accessibility/15-media.md`
