---
id: divi/01-architecture
topic: divi
slug: architecture
title: "Divi Architecture"
type: doc
order: 1
status: ready
tags: [divi, architecture, post_content, functions.php]
related: [divi/00-overview, divi/03-modules, divi/04-custom-modules, divi/05-layouts, divi/10-performance]
when_to_use: "Read before editing Divi content or writing module code, to understand the content model and render pipeline."
---
# Divi Architecture

## Purpose

This document explains how Divi is built internally: the layout hierarchy, how content is
stored, and how a request becomes rendered HTML. Understanding this is a prerequisite for
editing content safely and for writing [custom modules](04-custom-modules.md).

## Why It Matters

Divi's power and its failure modes both come from its architecture. Content is not stored
as HTML — it is stored as a structured representation the builder owns. If you edit that
representation incorrectly, the front end may still render while the Visual Builder refuses
to load, which is the single most common way to break a Divi site. Knowing where content
lives and how it is parsed lets you edit with confidence and diagnose corruption instead of
guessing.

## Core Principles

- **The layout is a fixed tree: Section → Row → Column → Module.** Sections span the page
  width, rows sit inside sections and define the column grid, columns hold modules, and
  modules are the leaf content units. Nothing renders outside this tree.
- **Content is a structured model, not HTML.** In **Divi 4** the model is nested
  shortcodes stored in `post_content` (e.g. `[et_pb_section][et_pb_row]...`). In **Divi 5**
  it is a normalized JSON content object with a separate style layer. Respect whichever model
  the site uses.
- **Rendering is server-side plus a React builder.** The front end is rendered by PHP; the
  Visual Builder is a React app that reads the same model. Both must be able to parse it.
- **Styles are generated, not authored inline.** Divi compiles module settings into a CSS
  file (or inline critical CSS). You configure settings; Divi emits the CSS.
- **The parent theme is untouchable.** All PHP extension happens in a child theme or plugin.

## Best Practices

- Identify the storage model before editing. Check the Divi version; a Divi 4 shortcode edit
  applied to a Divi 5 site (or vice versa) corrupts the page.
- Keep the tree shallow. Deeply nested specialty sections and rows increase DOM weight and
  slow both the front end and the builder.
- Use the builder's import/export (portability) to move content, not manual database edits —
  it preserves the model's integrity and IDs.
- Put all code customization in a child theme's `functions.php` or a small plugin, loaded via
  WordPress hooks. See [wordpress-hooks](16-wordpress-hooks.md).
- Enable Divi's static CSS file generation and dynamic assets so only used module CSS ships.
  See [performance](10-performance.md).

## Examples

**Good Example** — a well-formed Divi 4 content model, edited through valid structure

Divi 4 stores layout as nested shortcodes in `post_content`. Every module lives inside
column → row → section; IDs and attributes are managed by the builder, so keep the nesting
intact.

```text
[et_pb_section fb_built="1" _builder_version="4.27"]
  [et_pb_row _builder_version="4.27"]
    [et_pb_column type="4_4" _builder_version="4.27"]
      [et_pb_text _builder_version="4.27"]Hello world[/et_pb_text]
    [/et_pb_column]
  [/et_pb_row]
[/et_pb_section]
```

**Bad Example** — module placed outside the required hierarchy

A module placed directly inside a section, with no row/column wrapper. The front end may
render, but the Visual Builder cannot parse this tree and will fail to load or silently drop
the module.

```text
[et_pb_section fb_built="1"]
  [et_pb_text]Orphaned module[/et_pb_text]
[/et_pb_section]
```

## Common Mistakes

- Pasting HTML or arbitrary shortcodes into `post_content` and breaking the model so the
  Visual Builder will not open.
- Mixing Divi 4 shortcode syntax into a Divi 5 site, or assuming one migration is automatic.
- Editing the parent theme's PHP, which the next update overwrites.
- Building extreme nesting (section-in-row-in-column-in-section) that bloats the DOM and CSS.
- Assuming styles can be added inline; Divi ignores stray inline styles it did not generate.

## Production Tips

- Before bulk edits, export the layout as a `.json` backup via Divi portability so a corrupt
  save can be rolled back.
- If the Visual Builder will not load, suspect a malformed shortcode/JSON tree first; validate
  nesting before blaming plugins.
- Keep `_builder_version` attributes intact when scripting edits — Divi uses them for
  migration logic.

## AI Review Checklist

- Is every module wrapped in a valid section → row → column tree?
- Is the edit written in the correct content model for the site's Divi version?
- Is all PHP customization in a child theme or plugin, never the parent theme?
- Is static CSS generation / dynamic assets enabled to avoid shipping unused CSS?
- Was a portability export taken before a risky content change?

## Related

- `knowledge/divi/00-overview.md`
- `knowledge/divi/03-modules.md`
- `knowledge/divi/04-custom-modules.md`
- `knowledge/divi/05-layouts.md`
- `knowledge/divi/10-performance.md`
