---
id: devops/26-postmortems
topic: devops
slug: postmortems
title: "Postmortems"
type: doc
order: 26
status: ready
tags: [devops, postmortems]
related: [devops/25-incident-management, devops/24-change-management, devops/27-sre-principles, devops/30-engineering-principles, devops/13-observability]
when_to_use: "Read after any incident, or before defining your postmortem template and follow-up process."
---
# Postmortems

## Purpose

This document defines how a team learns from an incident: the written analysis that
turns a painful outage into durable improvements. It is written so an agent can author
or review a postmortem that finds systemic causes and produces action items that
actually get done — instead of a document that blames a person and is never reopened.

A postmortem is the retrospective for a single incident. It follows
[incident management](25-incident-management.md) (the live response) and feeds back
into [change management](24-change-management.md) and system design. Its purpose is
learning, not accountability theater.

## Why It Matters

An incident is expensive tuition already paid; a postmortem is how you collect what you
bought. Skip it and you will pay again for the same lesson. But a postmortem only works
if people tell the truth, and people only tell the truth when they are not afraid. The
moment a postmortem names a culprit, engineers start hiding details, and you lose the
very information that prevents recurrence. This is why the postmortem must be
**blameless**: it assumes everyone acted reasonably given what they knew, and it treats
"a human made a mistake" as evidence that the *system* let them, not as an endpoint.

## Core Principles

- **Blameless by default.** Focus on how the system and process allowed the failure,
  not on who typed the command. Blame kills the honesty the analysis depends on.
- **Human error is a symptom, not a cause.** When someone "ran the wrong script", ask
  why the system made that easy and why nothing caught it. Stop at the person and you
  fix nothing.
- **Ask why until you reach systemic causes.** A single root cause is usually a myth;
  incidents come from a chain of contributing factors. Trace the chain.
- **Every finding yields an owned, tracked action.** A lesson with no action item and
  no owner is not a lesson learned — it is a lesson to be relearned.
- **Trigger on criteria, not on severity of feelings.** Define upfront which incidents
  get a postmortem (e.g. any SEV1/SEV2, any customer-facing data issue) so it is
  automatic, not a judgment call made when everyone is tired.

## Best Practices

- Use a consistent template: summary, impact (who/how many/how long), timeline,
  contributing factors, what went well, what went poorly, action items.
- Quantify impact — duration, users affected, error budget consumed, revenue if known.
  Vague impact leads to vague prioritization.
- Write the timeline from the live incident log, in UTC, with detection, mitigation,
  and resolution timestamps. It exposes where time was actually lost (usually
  detection, not the fix).
- Make action items **SMART**: specific, owned, and tracked in your normal backlog with
  a due date. Prevent-recurrence items should outrank new features.
- Include "what went well" so good instincts and useful tooling get reinforced, not
  just failures.
- Share postmortems widely and readably. The value compounds when other teams learn
  from an incident they did not have.

## Examples

**Good Example** — blameless, systemic, actionable

```markdown
### Contributing factors
- A config change disabled connection pooling; the pipeline had no test asserting
  pool size, so it passed CI.               # system gap, not "Priya's mistake"
- Alert fired on DB CPU (a cause) not on checkout latency (the symptom), so
  detection lagged 12 min behind user impact.

### Action items
- [ ] Add CI check asserting pool config invariants.  @dana  due 2026-07-14
- [ ] Add SLO alert on checkout p99 latency.          @sam   due 2026-07-10
# WHY: each factor maps to a concrete, owned, dated change that removes the gap.
```

**Bad Example** — blame, single "root cause", no follow-through

```markdown
Root cause: Priya deployed a bad config.        # blames a person, ends inquiry
Resolution: Priya reverted it. Told the team to be more careful next time.
Action items: none.
# WHY THIS IS WRONG:
#  - "Be more careful" is not an action; the same class of bug will recur.
#  - Naming Priya makes the next engineer hide details.
#  - No system change: CI still can't catch it, alerting still lags.
```

## Common Mistakes

- Naming or implicitly blaming an individual, which suppresses honest detail.
- Stopping at "human error" instead of asking why the system permitted it.
- Declaring a single tidy root cause and ignoring the chain of contributing factors.
- Action items with no owner, no due date, and no place in the real backlog.
- Writing the postmortem and never verifying the action items shipped.
- Only doing postmortems for the "big" ones, so near-misses teach nothing.

## Production Tips

- Review open postmortem action items in a recurring meeting; unshipped prevention
  work is a leading indicator of the next incident.
- Keep a searchable archive of postmortems; patterns across incidents reveal the fragile
  parts of the system worth investing in.
- Consider postmortems for near-misses and successful "the SLO caught it" saves too —
  they are free lessons with no user impact.

## AI Review Checklist

- Is the analysis blameless — focused on system/process, not on a named person?
- Does it trace contributing factors rather than asserting one root cause?
- Is user impact quantified (duration, count, error budget)?
- Does every finding map to a specific, owned, dated action item in the backlog?
- Do prevent-recurrence items take priority over new feature work?
- Is there a defined trigger for which incidents require a postmortem?

## Related

- `knowledge/devops/25-incident-management.md`
- `knowledge/devops/24-change-management.md`
- `knowledge/devops/27-sre-principles.md`
- `knowledge/devops/30-engineering-principles.md`
- `knowledge/devops/13-observability.md`
