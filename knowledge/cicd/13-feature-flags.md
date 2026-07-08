---
id: cicd/13-feature-flags
topic: cicd
slug: feature-flags
title: "Feature Flags"
type: doc
order: 13
status: ready
tags: [cicd, feature-flags]
related: [cicd/12-canary-deployment, cicd/14-rollbacks, cicd/10-deployment, cicd/09-release-management, cicd/16-environments]
when_to_use: "Read before decoupling a code deploy from a feature release, or reviewing any runtime toggle."
---
# Feature Flags

## Purpose

This document defines how to use feature flags (feature toggles) to control whether code
paths are active at runtime, independent of deployment. It is written so an agent can add
a flag that ships safely, is cleanly removable, and does not become permanent technical
debt.

A feature flag separates *deploy* (code is in production) from *release* (users see the
behavior). This enables trunk-based development, dark launches, gradual rollouts, kill
switches, and A/B tests without redeploying. It complements
[canary deployment](12-canary-deployment.md): canaries control traffic to a *version*,
flags control exposure to a *feature*.

## Why It Matters

Without flags, "release" and "deploy" are the same event, so every risky change forces a
redeploy to turn off — minutes of downtime and a full CI cycle during an incident. A
kill-switch flag turns that into a one-line config change that takes effect in seconds.
Flags also let unfinished code merge to main behind an off switch, keeping branches short
and avoiding painful long-lived merges. The trade-off is real: every flag is a branch in
your code, and unmanaged flags multiply the states you must test and eventually rot into
dead code. Disciplined lifecycle management is the price of the safety.

## Core Principles

- **Fail safe on evaluation error.** If the flag service is unreachable, return a
  hard-coded, safe default — never crash and never assume "on." Availability of your app
  must not depend on availability of the flag service.
- **Default new features to off.** A flag ships disabled and is enabled deliberately.
  Code merged behind an off flag must be inert.
- **Every flag has an owner and an expiry.** A flag is temporary infrastructure. Record
  who owns it and when it should be removed; audit stale flags.
- **Keep flag checks at the edges, not scattered deep.** Evaluate once near the entry
  point and branch, rather than sprinkling the same check through many layers.
- **Never store secrets or authorization logic in a flag.** Flags decide *whether* a
  feature runs, not *who is allowed* — that is [authorization](../security/04-authorization.md).

## Best Practices

- Categorize each flag: **release** (temporary, remove after rollout), **ops/kill-switch**
  (long-lived, disables a subsystem), **permission/entitlement** (per-plan), or
  **experiment** (A/B, remove after the test). The category dictates its lifecycle.
- Use a managed flag system (LaunchDarkly, Unleash, OpenFeature-compatible SDK) rather
  than hand-rolled environment booleans once you have more than a handful.
- Evaluate against a stable user key so a given user gets a consistent variant across
  requests; log the variant with the user id for debugging and analysis.
- Remove release flags as soon as the feature is fully rolled out — schedule the cleanup
  ticket at creation time, not "later."
- Test both states in CI: the flag on and the flag off. An untested branch is a latent
  outage.
- Change flag values through an audited, access-controlled path — flag changes are
  production changes and belong in the change log.
- Keep the number of live flags small; a combinatorial explosion of flags is untestable.

## Examples

**Good Example** — safe default, single evaluation point, typed variant

```ts
// Fail closed to the OLD behavior if the flag service errors — availability first.
async function getCheckoutFlow(user: User): Promise<CheckoutFlow> {
  const enabled = await flags.getBooleanValue("new-checkout", false, {
    targetingKey: user.id, // stable key => consistent variant per user
  }); // second arg is the default returned on ANY error or timeout

  return enabled ? newCheckout : legacyCheckout; // one branch, at the edge
}
```

**Bad Example** — crashes on failure, defaults on, scattered checks

```ts
function getCheckoutFlow(user: User): CheckoutFlow {
  // No default: if the flag service throws, the whole request 500s.
  const enabled = flagClient.mustGet("new-checkout");
  // Deep in three other modules, the same string is re-checked and can drift.
  return enabled ? newCheckout : legacyCheckout;
}
// Elsewhere: `if (flagClient.mustGet("new-checkout")) { ... }`  // duplicated, unremovable
```

## Common Mistakes

- Failing open (or crashing) when the flag backend is down, coupling app uptime to the
  flag service.
- Leaving release flags in the code after full rollout, accumulating dead branches no
  one dares delete.
- Defaulting new flags to on, so unfinished code activates the moment it deploys.
- Reading the flag in many places with the raw string, making the feature impossible to
  remove cleanly.
- Using flags for authorization or to gate secret access — a flag is not an access
  control.
- Never testing the "off" path, so the fallback you rely on during an incident is broken.

## Production Tips

- Wire kill-switch flags into your incident runbook: the fastest [rollback](14-rollbacks.md)
  for a flagged feature is flipping the switch, not redeploying.
- Cache flag evaluations locally with streaming updates so evaluation is fast and
  survives brief backend outages.
- Emit metrics per variant so you can compare error/latency across flag states.

## AI Review Checklist

- Does every flag evaluation pass an explicit safe default and fail closed on error?
- Do new feature flags default to off?
- Is each flag categorized, owned, and given an expiry/cleanup ticket?
- Are both flag states (on and off) covered by tests?
- Is the flag evaluated at a single edge point rather than duplicated deep in the code?
- Are flag changes audited and access-controlled like other production changes?
- Are release flags removed promptly after full rollout?

## Related

- `knowledge/cicd/12-canary-deployment.md`
- `knowledge/cicd/14-rollbacks.md`
- `knowledge/cicd/10-deployment.md`
- `knowledge/cicd/09-release-management.md`
- `knowledge/cicd/16-environments.md`
