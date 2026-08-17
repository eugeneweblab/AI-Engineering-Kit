# Document Template

Copy this scaffold when creating a new topic document. The canonical rules for
**how** to write live in [`engineering/WRITING_STANDARD.md`](engineering/WRITING_STANDARD.md);
this file defines the required **shape**.

Every document MUST begin with the frontmatter block below, then follow the section
order. Delete this intro and the fenced markers when you fill it in.

---

## Required frontmatter

```yaml
---
id: <topic>/<NN-slug>        # e.g. nextjs/03-app-router
topic: <topic>               # folder name
slug: <slug>                 # e.g. app-router
title: "<Human Title>"       # matches the first H1
type: doc                    # doc | index
order: <NN>                  # numeric prefix as an integer
status: draft                # draft until complete, then: ready
maturity: unverified         # unverified | reviewed | validated
tags: [<topic>, <slug>]      # retrieval keywords
related: []                  # ids of related docs
when_to_use: ""              # one line: when an agent should read this doc
verified_against: ""         # product/runtime/version or standard revision
source_urls: []              # primary sources used to verify the rule
last_reviewed: ""            # quoted ISO date: YYYY-MM-DD
review_after: ""             # quoted ISO date; forces a freshness decision
---
```

Flip `status` to `ready` only when the Definition of Done in `WRITING_STANDARD.md`
is met. Use `maturity: reviewed` or `validated` only with the four provenance fields
filled; otherwise leave it `unverified`. After editing, regenerate the index:
`python3 scripts/build-index.py`.

---

## Body structure

````markdown
# Title

## Purpose

What this document covers and who it is for.

## Why It Matters

The problem, risk, or outcome this knowledge addresses.

## Core Principles

The high-level ideas that guide decisions in this area.

## Best Practices

- Specific, enforceable guidance. State what to do and why.

## Examples

**Good Example**

```ts
// correct, modern, production-ready
```

**Bad Example**

```ts
// the common mistake, with a note on why it fails
```

## Common Mistakes

- Anti-patterns and how to avoid them.

## Production Tips

- Operational advice (optional; include when it adds value).

## AI Review Checklist

- Correct?
- Secure?
- Performant?
- Readable?
- Tested?
- Production-ready?

## Related

- `knowledge/<topic>/<doc>.md`
````
