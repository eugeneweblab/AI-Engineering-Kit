---
id: workflows/06-investigate-production-bug
topic: workflows
slug: investigate-production-bug
title: "Workflow — Investigate a Production Bug"
type: workflow
order: 6
status: ready
tags: [workflows, investigate-production-bug]
related: [workflows/02-fix-a-bug, playbooks/01-site-down, templates/03-incident-report]
  - devops/25-incident-management
  - devops/26-postmortems
  - devops/13-observability
  - devops/14-logging
  - devops/12-monitoring
  - devops/07-deployment-strategies
  - cicd/13-feature-flags
  - cicd/14-rollbacks
  - cicd/16-environments
  - security/26-incident-response
  - engineering/03-debugging-methodology
  - git/18-history
  - git/19-reflog
  - databases/17-migrations
  - testing/25-production-testing
  - devops/98-production-checklist
  - devops/99-ai-review-checklist
  - devops/100-common-antipatterns
when_to_use: "Follow this workflow when investigating an incident occurring in a production environment."
---
# Workflow — Investigate a Production Bug

## Purpose

This workflow defines the standard process for investigating issues that occur in a production environment.

Production incidents require a different approach than bugs discovered during development.

The primary objective is to restore service safely, identify the root cause, and prevent the incident from occurring again.

---

## Goal

Resolve the production issue while:

- minimizing customer impact;
- preserving data integrity;
- avoiding unnecessary changes;
- collecting sufficient evidence;
- documenting findings.

Production stability always takes priority over feature development.

---

## Workflow Overview

```
Receive Incident
        ↓
Assess Severity
        ↓
Collect Evidence
        ↓
Contain the Issue
        ↓
Identify Root Cause
        ↓
Plan the Fix
        ↓
Implement Safely
        ↓
Validate in Production
        ↓
Document Findings
        ↓
Prevent Recurrence
```

---

## Step 1 — Assess the Incident

Determine:

- affected users;
- affected environments;
- affected services;
- business impact;
- data integrity risk;
- security implications;
- urgency.

Classify the incident before making changes.

---

## Step 2 — Preserve Evidence

Before modifying anything, collect evidence.

Examples:

- application logs;
- server logs;
- stack traces;
- HTTP requests;
- API responses;
- database state;
- monitoring alerts;
- deployment history;
- configuration changes.

Do not destroy evidence during the investigation.

---

## Step 3 — Determine Recent Changes

Review changes that occurred before the incident.

Examples:

- deployments;
- configuration updates;
- infrastructure changes;
- dependency upgrades;
- database migrations;
- environment variable updates.

Recent changes often provide valuable clues.

---

## Step 4 — Reproduce the Issue

Whenever possible, reproduce the issue outside production.

Preferred environments:

Development

↓

Staging

↓

Production (only when absolutely necessary)

Avoid experimenting directly in production.

---

## Step 5 — Contain the Incident

If the issue is actively affecting users, determine whether temporary mitigation is possible.

Examples:

- disable a feature flag;
- rollback a deployment;
- scale infrastructure;
- redirect traffic;
- enable maintenance mode.

Temporary mitigation is not the final solution.

---

## Step 6 — Identify the Root Cause

Continue investigating until the underlying cause is known.

Review:

- application logic;
- infrastructure;
- networking;
- authentication;
- third-party services;
- caching;
- concurrency;
- database behavior.

Avoid treating symptoms as causes.

---

## Step 7 — Plan the Fix

Before implementation identify:

- required code changes;
- infrastructure changes;
- deployment strategy;
- rollback strategy;
- verification plan;
- monitoring requirements.

Production changes should always have a rollback strategy.

---

## Step 8 — Implement Carefully

Apply the smallest safe change.

During implementation:

- preserve architecture;
- preserve existing behavior where possible;
- avoid unrelated refactoring;
- avoid speculative improvements.

Emergency fixes should remain focused.

---

## Step 9 — Validate the Resolution

Verify:

- the original issue is resolved;
- logs are healthy;
- monitoring shows normal behavior;
- affected users can complete critical workflows;
- no additional regressions are introduced.

Do not close the incident immediately after deployment.

---

## Step 10 — Prevent Recurrence

Determine how similar incidents can be prevented.

Possible improvements:

- automated tests;
- better validation;
- improved monitoring;
- additional logging;
- deployment safeguards;
- documentation;
- runbooks;
- alerts.

Every incident should improve the system.

---

## AI Execution Checklist

## Investigation

☐ Assess severity.

☐ Preserve evidence.

☐ Review logs.

☐ Review recent deployments.

☐ Review configuration changes.

☐ Review monitoring.

☐ Identify the root cause.

---

## Planning

☐ Define mitigation strategy.

☐ Define implementation plan.

☐ Define rollback strategy.

☐ Define verification strategy.

---

## Implementation

☐ Modify the smallest possible area.

☐ Preserve architecture.

☐ Avoid unrelated changes.

☐ Keep rollback possible.

---

## Verification

☐ Verify production behavior.

☐ Review monitoring.

☐ Review logs.

☐ Verify critical user flows.

☐ Confirm system stability.

☐ Update documentation.

---

## Severity Guidelines

## Critical

Examples:

- complete outage;
- payment failures;
- authentication failures;
- data corruption;
- security incident.

Requires immediate response.

---

## High

Examples:

- major feature unavailable;
- degraded performance;
- high error rate.

Requires urgent investigation.

---

## Medium

Examples:

- isolated feature failures;
- intermittent errors;
- limited user impact.

Should be resolved promptly.

---

## Low

Examples:

- cosmetic issues;
- minor usability problems;
- non-critical logging issues.

Can be scheduled according to normal priorities.

---

## Examples

**Good Example** — stabilise, then investigate with the evidence preserved

```bash
# 1. Stop the bleeding first, and say so — mitigation is not diagnosis.
kubectl rollout undo deployment/api          # back to the last known-good release
# → error rate back to baseline at 14:22. Incident mitigated, NOT resolved.

# 2. Preserve the evidence before it rotates out of retention.
kubectl logs deployment/api --previous --since=2h > incident-2026-08-04.log
curl -sS "$LOGS_API/query?q=status:500 AND route:/api/orders&from=13:00&to=14:30" \
  > incident-2026-08-04.json
```

```text
3. Narrow with the data, not with guesses
   All 500s carry plan:"legacy" — 2% of traffic, 100% of failures.
   Deploys in the window: 3. Only 8f2c1a9 touched pricing.
   8f2c1a9 made plan.discountPercent required; legacy rows have it null.

4. Reproduce off production
   Seeded one legacy plan locally → same stack trace. Cause confirmed.

5. Fix forward, with a regression test, and write the incident report:
   timeline, cause, why monitoring did not catch it, what changes.
```

**Bad Example** — investigate on production, in the dark

```text
14:20  Restarted the pods. Still failing.
14:30  Increased the memory limit "in case it's OOM". No change.
14:40  Edited the config map directly on the cluster to disable the pricing cache.
14:50  Errors stopped. Marked resolved. Did not record what was changed.
15:30  Next deploy overwrote the manual config change; errors returned.
```

The cluster no longer matches the repository, nobody knows which change helped, the logs from
the failure window have rotated away, and the same incident happens again after every deploy.

---

## Common Mistakes

Avoid:

Debugging directly in production.

Deleting logs before investigation.

Changing multiple systems simultaneously.

Deploying large refactorings during an incident.

Ignoring rollback planning.

Closing the incident without monitoring.

Assuming the first identified issue is the root cause.

---

## Completion Criteria

The investigation is complete only if:

- service has been restored;
- the root cause is known;
- the fix has been verified;
- monitoring confirms stability;
- rollback is no longer required;
- lessons learned have been documented;
- preventive actions have been identified.

---

## Expected AI Output

After completing the workflow, the AI should provide:

Incident Summary

Business Impact

Root Cause Analysis

Evidence Collected

Changes Implemented

Verification Performed

Remaining Risks

Preventive Recommendations

---

## Summary

Production incidents require discipline, evidence, and careful decision-making.

The objective is not simply to restore service, but to understand why the incident occurred and strengthen the system to reduce the likelihood of future failures.

## Related

- `knowledge/workflows/02-fix-a-bug.md`
- `knowledge/playbooks/01-site-down.md`
- `knowledge/templates/03-incident-report.md`
