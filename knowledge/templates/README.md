---
id: templates/readme
topic: templates
slug: readme
title: "Template Templates"
type: index
order: -1
status: ready
tags: [templates]
related: []
when_to_use: "Read first to find the right document or code template before creating a new file."
---
# Template Templates

## Purpose

Copy-ready document templates for artifacts that recur across projects: pull request
descriptions, architecture decision records, and incident reports.

Each template exists because the artifact is written under time pressure — at the end of a
task, mid-incident, or during a contested design discussion — and a blank page at that
moment produces something worse than a filled-in structure.

---

## What's Here

| Template | Use when | Written by |
|---|---|---|
| [01. Pull Request](01-pull-request.md) | Opening any non-trivial PR | The author, before review |
| [02. Architecture Decision Record](02-architecture-decision-record.md) | A decision is hard to reverse or will be questioned later | Whoever made the call |
| [03. Incident Report](03-incident-report.md) | After a user-visible failure | The responder, within days |

---

## How to Use These

- **Copy the whole thing, then delete what does not apply.** A section removed deliberately
  is better than a section nobody thought about.
- **Fill in the "why", not just the "what".** The diff already shows what changed; the
  template exists to capture what the diff cannot.
- **Keep them in the repository**, not in a wiki. Templates that live next to the code get
  updated when the process changes.

Most platforms will apply these automatically if placed conventionally:

```
.github/PULL_REQUEST_TEMPLATE.md
.github/ISSUE_TEMPLATE/
docs/adr/0000-record-architecture-decisions.md
docs/incidents/
```

---

## Related Topics

- [Workflow — Review a Pull Request](../workflows/05-review-pull-request.md) — the reviewer's side of the PR template.
- [Architecture — Architecture Decision Records](../architecture/26-architecture-decision-records.md) — when an ADR is warranted.
- [Security — Incident Response](../security/26-incident-response.md) — the process the incident report documents.
- [Playbooks](../playbooks/README.md) — what to do during the incident; the report comes after.

---

## Summary

These templates capture the reasoning that a diff, a commit, or a resolved alert does not.
Copy them, fill in the why, and keep them versioned with the code they describe.
