---
id: devops/25-incident-management
topic: devops
slug: incident-management
title: "Incident Management"
type: doc
order: 25
status: ready
tags: [devops, incident-management]
related: [devops/15-alerting, devops/26-postmortems, devops/24-change-management, devops/27-sre-principles, devops/18-disaster-recovery]
when_to_use: "Read before defining on-call, alert response, incident roles, or building any runbook or paging setup."
---
# Incident Management

## Purpose

This document defines how a team detects, responds to, and resolves a production
incident — the roles, the communication, and the decisions made under pressure. It is
written so an agent can build or review an incident process that restores service
quickly and produces the facts a [postmortem](26-postmortems.md) will need.

An incident is any unplanned disruption or degradation of a service that matters to
users. Incident management is about the *live* response; learning from it afterward is
covered separately in [postmortems](26-postmortems.md). The single goal during an
incident is to restore service — not to find root cause, not to assign blame.

## Why It Matters

During an incident every minute maps directly to user harm, lost revenue, and eroded
trust. Yet incidents are exactly when humans perform worst: adrenaline is high,
information is incomplete, and multiple people improvise in parallel. Without a
pre-agreed structure, responders duplicate work, step on each other's changes, and
leave stakeholders in the dark. A rehearsed process converts panic into a checklist.
The measure of maturity is not "we have no incidents" — you will — it is *time to
restore* (MTTR) and whether each incident is calmer than the last.

## Core Principles

- **Mitigate first, diagnose later.** The job is to stop the bleeding — roll back,
  fail over, shed load, disable a feature. Understanding *why* it broke can wait until
  users are served again.
- **One Incident Commander (IC).** A single person owns coordination and decisions.
  They do not fix the problem themselves; they direct. This prevents two engineers
  from applying conflicting mitigations at once.
- **Declare early, escalate freely.** It is cheaper to declare an incident and stand
  it down than to under-react. Nobody is ever punished for paging for help.
- **Communicate on a cadence.** Stakeholders get regular updates even when the update
  is "still investigating". Silence makes people improvise their own responses.
- **Everything is reversible under control.** Mitigations are themselves changes — make
  one at a time, announce it, and watch its effect before the next.

## Best Practices

- Define severity levels (e.g. SEV1 total outage, SEV2 major degradation, SEV3 minor)
  with explicit response expectations for each. Severity drives who is paged and how
  loud the alarm is.
- Assign clear roles: **Incident Commander** (coordinates), **Communications Lead**
  (updates stakeholders/status page), **Operations/Subject-matter experts** (apply
  fixes). On a small team one person may hold several, but the roles are still explicit.
- Keep a live incident timeline — a running log of what was observed and done, with
  timestamps. This is the raw material for the postmortem and prevents "wait, did we
  already try that?".
- Write runbooks for known failure modes and link them from the alert, so the first
  responder has a concrete first action instead of a blank page.
- Only page on symptoms users feel; route everything else to a dashboard. See
  [alerting](15-alerting.md). A pager that cries wolf gets ignored during the real fire.
- Rehearse. Run game days / chaos drills so the process is muscle memory, not a
  document nobody has opened.

## Examples

**Good Example** — a runbook step that mitigates before diagnosing

```markdown
## Runbook: Checkout error rate > 5% (SEV2)
1. DECLARE incident, assign IC, open incident channel. (do this first)
2. MITIGATE: disable `new_checkout_flow` flag → reverts to known-good path.
   # WHY: restores users in seconds without needing to know the cause yet.
3. VERIFY: confirm error rate drops on the dashboard before anything else.
4. COMMUNICATE: post status-page update + first stakeholder update.
5. THEN investigate root cause with users already served.
```

**Bad Example** — heroics with no structure

```text
09:02  Alert fires. Priya starts reading logs to find the bug.
09:07  Sam, unaware, restarts the DB to "see if it helps".
09:09  Raj rolls back the deploy at the same time Sam re-enables the flag.
        # No IC: three people apply conflicting changes; nobody watches the
        # combined effect. No timeline: the postmortem can't reconstruct order.
        # No comms: support is telling customers "everything is fine."
09:40  Service recovers — nobody is sure which action fixed it.
```

## Common Mistakes

- Diagnosing root cause while users are down, instead of mitigating first.
- No single Incident Commander, so responders make conflicting changes in parallel.
- Applying several mitigations at once, so you cannot tell which one worked.
- Going silent — no status-page or stakeholder updates during the incident.
- Alerting on causes/noise rather than user-facing symptoms, so real incidents drown.
- No timeline, leaving the postmortem to reconstruct events from memory.

## Production Tips

- Automate incident bootstrap: a single command spins up the channel, pages the IC,
  starts the timeline, and posts an initial status-page entry.
- Keep a maintained on-call rotation with a defined escalation path and a backup — a
  page that no one answers is not a process.
- Track MTTA (acknowledge) and MTTR (restore) per incident to see if response is
  improving over time.
- Keep the status page separate from your primary infrastructure so it survives when
  the main system is down.

## AI Review Checklist

- Do responders mitigate (roll back / fail over / flag off) before root-causing?
- Is there exactly one Incident Commander who coordinates rather than fixes?
- Are severity levels defined with matching paging and response expectations?
- Is a timestamped incident timeline captured live for the postmortem?
- Do alerts page only on user-facing symptoms, with a runbook linked?
- Are stakeholders updated on a fixed cadence via an independent status page?

## Related

- `knowledge/devops/15-alerting.md`
- `knowledge/devops/26-postmortems.md`
- `knowledge/devops/24-change-management.md`
- `knowledge/devops/27-sre-principles.md`
- `knowledge/devops/18-disaster-recovery.md`
