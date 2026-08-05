---
id: snippets/readme
topic: snippets
slug: readme
title: "Snippets"
type: index
order: -1
status: ready
tags: [snippets]
related: []
when_to_use: "Read first to find a reusable code snippet in this collection."
---
# Snippets

## Purpose

Short, copy-ready implementations of things that are easy to get subtly wrong: money
formatting, debouncing, WordPress escaping, safe shell scripts.

These are not a library. Each snippet is small enough to read in full before pasting, and
the reason it exists is written next to it — a snippet you cannot explain is a snippet you
should not paste.

---

## What's Here

| Collection | Contents |
|---|---|
| [01. TypeScript Utilities](01-typescript-utilities.md) | Money, dates, async control, type guards |
| [02. PHP and WordPress](02-php-wordpress.md) | Escaping, capability checks, queries, transients |
| [03. Shell Scripts](03-shell-scripts.md) | Safe defaults, argument handling, cleanup traps |

---

## How to Use a Snippet

- **Read it before pasting.** Every one has a comment explaining the non-obvious part; that
  comment is the reason it is here.
- **Adapt names and error handling** to the surrounding code rather than importing a
  different style.
- **Check whether the platform already does it.** Several of these existed because the
  runtime lacked them, and some are now redundant on modern targets.
- **A snippet used three times is a shared function.** Copying is fine twice; the third time,
  extract it — see [Engineering Principles](../engineering/00-engineering-principles.md).

---

## Related Topics

- [TypeScript](../typescript/00-overview.md) · [JavaScript](../javascript/00-overview.md) · [PHP](../php/00-overview.md) · [Linux](../linux/00-overview.md)
- [Examples](../examples/README.md) — complete worked implementations rather than fragments.
- [Templates](../templates/README.md) — document scaffolds rather than code.

---

## Summary

Small implementations of things that are easy to get wrong, each with the reason it is
written that way. Read before pasting, adapt to the surrounding code, and extract to a shared
function once it recurs.
