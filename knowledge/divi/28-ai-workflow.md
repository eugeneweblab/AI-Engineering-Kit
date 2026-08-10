---
id: divi/28-ai-workflow
topic: divi
slug: ai-workflow
title: "AI Workflow"
type: doc
order: 28
status: ready
tags: [divi, ai-workflow, post_content, wp_get_theme, get_stylesheet_directory_uri, wp_enqueue_style, add_action, agent, layout, content]
related: [divi/00-overview, divi/01-architecture, divi/04-custom-modules, divi/20-debugging, divi/29-review]
when_to_use: "Read before an AI agent generates, edits, or refactors any Divi content, code, or layout."
---
# AI Workflow

## Purpose

This document defines how an AI agent should work on a Divi project so it helps rather than
corrupts the build. Divi's content model (shortcodes in Divi 4, JSON in Divi 5) and its
Visual Builder make it uniquely easy for an agent to produce output that looks plausible but
silently breaks the builder. This doc sets the process that avoids that.

It is written for the agent itself: what to confirm before acting, what never to touch, and
how to hand work back in a form a human can verify.

## Why It Matters

An agent that treats Divi like ordinary HTML/PHP will corrupt layouts in ways that pass a
glance but fail at load: a hand-written shortcode with a malformed attribute, JSON that
doesn't match the Divi 5 schema, or PHP added to the parent theme that the next update wipes.
Because Divi content is data, not free-form markup, the safe workflow is different from a
normal codebase — and skipping it produces damage a client discovers weeks later when the
builder won't open.

## Core Principles

- **Identify the version first.** Divi 5 (JSON content model, new module API) and Divi 4
  (shortcode model) differ fundamentally. Guidance and generated content are not
  interchangeable. See [architecture](01-architecture.md).
- **Prefer the builder's mechanisms over raw content.** Recommend Theme Builder, presets,
  dynamic content, and layout import/export instead of hand-writing shortcodes/JSON.
- **Never hand-edit `post_content` blind.** If content must be generated, produce a valid,
  importable layout export — not a guessed shortcode string pasted into the database.
- **All code goes in a child theme, enqueued.** Generated PHP/CSS/JS must be update-safe; never
  edit the parent theme or paste `<script>` into a Code module. See [best-practices](24-best-practices.md).
- **Hand back verifiable steps.** Output should be reviewable and testable by a human in the
  builder and on the front end, not a black-box change.

## Best Practices

- **Confirm context before acting:** Divi version, whether a child theme exists, and whether
  the change belongs in the builder, the Theme Builder, or PHP.
- When generating a **custom module**, follow Divi's module API for the target version and
  place it in a child theme or plugin — not inline. See [custom-modules](04-custom-modules.md).
- When editing layout, **describe the builder actions** (which section/row/module, which
  setting) rather than emitting raw shortcode/JSON the user must trust unseen.
- For repeated design, generate a **preset or global module recommendation**, not duplicated
  markup — the same reuse rules apply to AI output as to human output.
- **State assumptions explicitly** ("assuming Divi 5 and an existing child theme") so a wrong
  assumption is caught before it causes damage.
- Provide a **rollback**: what to back up (layout export, database) before applying, so a bad
  generation is recoverable.
- Route debugging through [debugging](20-debugging.md) — read the actual error and builder
  console, don't guess-and-replace.

## Examples

**Good Example** — version-aware, child-theme, enqueued output

```php
// Agent confirmed: Divi 5, child theme present. Custom code placed update-safe.
// child-theme/functions.php
add_action( 'wp_enqueue_scripts', function () {
  wp_enqueue_style(
    'client-overrides',
    get_stylesheet_directory_uri() . '/assets/overrides.css',
    array( 'divi-style' ),
    wp_get_theme()->get( 'Version' )
  );
} );
// WHY: safe across Divi updates, versioned, dependency-declared, and the agent
// stated its version assumption so a human can catch a mismatch before applying.
```

**Bad Example** — guessed shortcode written straight to the database

```php
// Agent guessed a Divi 4 shortcode and told the user to paste it into post_content.
$content = '[et_pb_section][et_pb_row][et_pb_column type="4_4"]'
         . '[et_pb_text]Hello[/et_pb_text][/et_pb_column][/et_pb_row][/et_pb_section]';
// WHY it's wrong: no version confirmed, a single wrong/missing attribute makes the
// Visual Builder fail to load, and there is no backup or way to verify it in the UI.
```

## Common Mistakes

- Generating content without first confirming Divi 4 vs Divi 5.
- Hand-writing shortcodes/JSON into `post_content` instead of producing an importable export.
- Emitting PHP for the parent theme, so the next Divi update erases it.
- Pasting `<script>`/`<style>` into Code modules instead of enqueuing in a child theme.
- Duplicating markup where a preset or global module is the correct output.
- Applying changes with no backup or rollback path.

## Production Tips

- Always instruct the user to export the affected layout (or take a DB backup) before applying
  a generated change — it is the one step that makes AI edits safe.
- Prefer producing a Divi Library `.json` export the user can import over raw content strings;
  the import path validates structure, a hand-paste does not.
- Follow up generated code with a review pass against [review](29-review.md).

## AI Review Checklist

- Was the Divi version (4 vs 5) confirmed before generating content or code?
- Is generated code in a child theme and enqueued, never the parent or a Code module?
- Is layout output an importable/valid export, not a guessed shortcode/JSON string?
- Were assumptions stated and a backup/rollback path provided before applying?
- Does the output favor presets/global modules over duplication?

## Related

- `knowledge/divi/00-overview.md`
- `knowledge/divi/01-architecture.md`
- `knowledge/divi/04-custom-modules.md`
- `knowledge/divi/20-debugging.md`
- `knowledge/divi/29-review.md`
