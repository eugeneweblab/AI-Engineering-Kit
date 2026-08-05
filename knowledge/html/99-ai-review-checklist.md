---
id: html/99-ai-review-checklist
topic: html
slug: ai-review-checklist
title: "HTML AI Review Checklist"
type: doc
order: 99
status: ready
tags: [html, ai-review-checklist, pattern, onclick, autocomplete, defer, aria-labelledby]
related: [html/30-engineering-principles, html/100-common-antipatterns, html/02-semantic-html, html/11-accessibility, html/22-validation]
when_to_use: "Read when reviewing HTML in a pull request or generated output, to check the markup against objective criteria."
---
# HTML AI Review Checklist

## Purpose

This is the checklist an AI agent applies when *reviewing* HTML — its own output or a
human's diff. Each item is a concrete, verifiable question with a clear pass/fail answer
derived from the markup itself, not from taste. Report any failed item as a blocking
review comment with the specific line and fix.

## Why It Matters

HTML review is where invisible defects get caught before they reach users. A rendered
page cannot tell you whether a `<div>` should have been a `<button>`, whether headings
skip a level, or whether an input lacks a label — but the source can. A disciplined,
source-level checklist turns "the page looks fine" into a real correctness audit and
keeps subjective bikeshedding out of review.

## Semantics & Structure

**Rules:** [Semantic HTML](02-semantic-html.md) · [Document Structure](01-document-structure.md)

- [ ] Is each element chosen for meaning rather than appearance (no `<div>` where a
  semantic element fits)?
- [ ] Are interactive elements native (`<a>` for navigation, `<button>` for actions),
  not clickable `<div>`/`<span>`?
- [ ] Is there exactly one `<main>`, and are landmarks used correctly?
- [ ] Is the heading hierarchy logical with no skipped levels?
- [ ] Are all `id` values unique across the document?

## Accessibility

**Rules:** [Accessibility](11-accessibility.md)

- [ ] Does every `<img>` have an `alt` (descriptive or empty for decorative)?
- [ ] Is every form control associated with a `<label>`?
- [ ] Is all interactive content keyboard-operable with a visible focus indicator?
- [ ] Is ARIA used only where native HTML cannot express the semantics, with valid roles
  and no redundant roles?
- [ ] Are `aria-label`/`aria-labelledby` references pointing at existing elements?

## Correctness & Validity

**Rules:** [Validation](22-validation.md)

- [ ] Is the markup well-formed and spec-valid (correct nesting, required attributes,
  properly closed elements)?
- [ ] Are `<!DOCTYPE html>`, `<html lang>`, and `<meta charset>` present?
- [ ] Are attribute values quoted and boolean attributes used correctly?
- [ ] Are there no deprecated or obsolete elements/attributes (`<center>`, `<font>`,
  `align`, `bgcolor`)?

## Forms

**Rules:** [Forms](08-forms.md)

- [ ] Do inputs use the most specific `type` and appropriate `autocomplete`?
- [ ] Is native validation (`required`, `pattern`, `min`/`max`) used before JS?
- [ ] Does the form submit and function with JavaScript disabled?

## Security & Robustness

**Rules:** [Security](19-security.md) · [Progressive Enhancement](23-progressive-enhancement.md)

- [ ] Do `target="_blank"` links carry `rel="noopener"`?
- [ ] Is any dynamically inserted HTML sanitized against XSS?
- [ ] Is presentation kept in CSS and behavior in JS, with no inline styles or
  `onclick`-style handlers unless justified?

## Performance

**Rules:** [Performance](18-performance.md)

- [ ] Do images declare dimensions to avoid layout shift?
- [ ] Do non-critical images use `loading="lazy"` and scripts use `defer`/`async`?

## AI Review Checklist

- [ ] Have I flagged every non-semantic or inaccessible element with a specific fix?
- [ ] Have I verified the markup would pass an HTML validator and an `axe` scan?
- [ ] Have I confirmed the page works with JS and CSS disabled?
- [ ] Have I checked that no deprecated elements or duplicate `id`s remain?

## Related

- `knowledge/html/30-engineering-principles.md`
- `knowledge/html/100-common-antipatterns.md`
- `knowledge/html/02-semantic-html.md`
- `knowledge/html/11-accessibility.md`
- `knowledge/html/22-validation.md`
