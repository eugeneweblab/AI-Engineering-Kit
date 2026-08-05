---
id: playbooks/readme
topic: playbooks
slug: readme
title: "Playbooks"
type: index
order: -1
status: ready
tags: [playbooks, readme]
related: []
when_to_use: "Read first to find the right operational playbook for the task at hand."
---
# Playbooks

## Purpose

Step-by-step procedures for the situations where thinking clearly is hardest: production is
down, a deploy broke something, or a credential leaked.

A playbook is not documentation to read for understanding — it is a sequence to follow while
under pressure. It exists because the first ten minutes of an incident are otherwise spent
on decisions that could have been made calmly in advance.

---

## What's Here

| Playbook | Trigger |
|---|---|
| [01. Site Down](01-site-down.md) | The application is unreachable or erroring for most users |
| [02. Failed Deployment](02-failed-deployment.md) | A release broke production, or a deploy will not complete |
| [03. Security Incident](03-security-incident.md) | A credential leaked, or unauthorized access is suspected |

---

## How to Use a Playbook

- **Follow it in order.** The sequence exists because step 3 is misleading before step 2.
- **Stabilize before diagnosing.** Restoring service and finding the cause are different
  activities; do them in that order.
- **Write down what you do as you do it.** The timeline is nearly impossible to reconstruct
  afterwards, and it is what the incident report needs.
- **Escalate on a clock, not on a feeling.** Each playbook states when to bring in more
  people — set a timer rather than deciding in the moment.

---

## Before You Need One

A playbook is only executable if the prerequisites exist. Confirm these while nothing is
broken:

☐ Someone on call knows where the alerts go and has access to act.

☐ Rollback is one command, and someone has run it in the last quarter.

☐ Database backups exist, are off-site, and a restore has been tested.

☐ Credentials can be rotated without a deploy.

☐ The status page and its update path are known before they are needed.

☐ A channel exists for incident coordination, separate from normal traffic.

---

## Related Topics

- [Templates — Incident Report](../templates/03-incident-report.md) — what to write once service is restored.
- [Security — Incident Response](../security/26-incident-response.md) — the process these playbooks operate inside.
- [Workflow — Investigate a Production Bug](../workflows/06-investigate-production-bug.md) — the diagnosis workflow, for after stabilization.
- [Tools — Observability Tools](../tools/29-observability-tools.md) — the signals these playbooks read.

---

## Summary

Playbooks trade flexibility for speed under pressure. Follow the sequence, stabilize before
diagnosing, log as you go, and escalate on a timer rather than on instinct.
