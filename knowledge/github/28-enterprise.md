---
id: github/28-enterprise
topic: github
slug: enterprise
title: "Enterprise"
type: doc
order: 28
status: ready
tags: [github, enterprise, features, GITHUB_TOKEN, DEFAULT_BRANCH]
related: [github/19-organizations, github/20-teams, github/21-permissions, github/18-rulesets, github/13-security]
when_to_use: "Read before configuring enterprise-level SSO, policies, or rulesets, or auditing an enterprise account."
---
# Enterprise

## Purpose

This document defines how to govern GitHub at the **enterprise account** level — the tier above
individual [organizations](19-organizations.md). It covers SSO/SAML, SCIM provisioning, managed
users (EMU), enterprise policies and rulesets, IP allow lists, and the audit log. The concern
here is central control: setting guardrails once at the top so every org and repo inherits them,
rather than trusting each org to configure itself correctly.

An enterprise account is where security and compliance are enforced for the whole company.
Policies set here are floors, not suggestions — organizations cannot loosen a policy the
enterprise has locked.

## Why It Matters

At enterprise scale, the failure of a single control multiplies across thousands of repos and
users. If SSO is not enforced, a departed employee's personal account keeps access. If SCIM is
not wired up, deprovisioning is manual and forgotten. If policies are set per-org instead of at
the enterprise, one misconfigured org becomes the weak link an attacker walks through. The audit
log is your only record of who changed what. Getting enterprise governance right means one
correct configuration protects everyone; getting it wrong means the blast radius is the entire
company, and you may not have the audit trail to reconstruct what happened.

## Core Principles

- **Enforce identity centrally.** Require SSO (SAML/OIDC) and provision/deprovision via SCIM so
  access is tied to your IdP. The cost is IdP integration work; the benefit is that offboarding
  a user in the IdP instantly removes their GitHub access.
- **Set policy at the enterprise, inherit downward.** Configure security features, allowed
  actions, and rulesets once at the top and lock them, so no org can weaken them.
- **Prefer Managed Users (EMU) when you need full lifecycle control.** EMU accounts exist only
  inside your enterprise and cannot access personal repos or the public network — stronger
  isolation at the cost of some open-source workflow flexibility.
- **Make the audit log immutable and monitored.** Stream it to your SIEM; the enterprise audit
  log is the authoritative record for incident response and compliance.
- **Least privilege for enterprise owners.** Enterprise-owner is the most powerful role — grant
  it to the fewest people, require MFA, and review it regularly.

## Best Practices

- Require **SAML/OIDC SSO** and **SCIM** provisioning; disable non-SSO access paths and enforce
  MFA at the enterprise level so every org inherits it.
- Choose the model deliberately: **EMU** for tightly governed identity, standard enterprise for
  mixed open-source/internal work. EMU can be irreversible per-enterprise, so decide early.
- Define **enterprise rulesets** for branch protection, required workflows, and naming that
  apply across all orgs; lock security features (secret scanning, push protection, Dependabot,
  code scanning) on so orgs cannot turn them off. See [rulesets](18-rulesets.md).
- Restrict **allowed GitHub Actions** enterprise-wide (verified creators + SHA allowlist) and
  set default `GITHUB_TOKEN` permissions to read.
- Configure **IP allow lists** to limit access to corporate networks/VPN where policy requires it.
- Stream the **audit log** (including Git events) to a SIEM; alert on enterprise-owner changes,
  policy changes, and SSO configuration changes.
- Manage org and team membership through your IdP groups (via SCIM/team sync), not by hand.

## Examples

**Good Example** — enterprise ruleset enforced org-wide, locked on

```yaml
# Enterprise-level ruleset (conceptual): applies to ALL orgs/repos; orgs cannot weaken it.
name: enterprise-baseline
enforcement: active                 # not "evaluate" — actually blocks violations
target: branch
conditions:
  ref_name: { include: ["~DEFAULT_BRANCH"] }
rules:
  - type: pull_request
    parameters: { required_approving_review_count: 1, dismiss_stale_reviews_on_push: true }
  - type: required_status_checks
    parameters: { required_checks: [ci] }
  - type: non_fast_forward          # blocks force-push over history
# Security features (secret scanning, push protection) are set to "enforced" at the enterprise,
# so an individual org owner cannot disable them.
```

**Bad Example** — policy left to each org, no central identity

```text
Enterprise settings:
  SSO: optional            # departed employees keep personal-account access
  SCIM: not configured     # deprovisioning is manual and gets forgotten
  Security features: "no policy" (each org decides) # one org disables push protection → leak
  Actions: "allow all"     # any org can run an unvetted third-party action
  Audit log streaming: off # no record for incident response or compliance
# Result: the enterprise is only as secure as its least-careful org owner.
```

## Common Mistakes

- SSO optional instead of enforced, leaving personal-account access after offboarding.
- No SCIM, so deprovisioning is manual and stale accounts linger.
- Setting security policy per-org rather than enforcing it at the enterprise, creating weak links.
- Too many enterprise owners, or enterprise owners without required MFA.
- Not streaming the audit log, so there is no trail during an incident.
- Choosing EMU (or not) without understanding it can be irreversible and blocks personal-repo access.
- "Allow all actions" at the enterprise, permitting unvetted third-party code company-wide.

## Production Tips

- Test SSO/SCIM against a pilot org before rolling out enterprise-wide; a broken SCIM mapping can
  lock out real users.
- Keep a break-glass enterprise-owner account with a securely stored credential in case SSO fails.
- Review enterprise-owner list, IP allow lists, and locked policies on a schedule; drift is the
  norm without periodic audit.
- For compliance, confirm data-residency and retention settings match your obligations, and
  document them alongside the audit-log stream.

## AI Review Checklist

- Is SSO (SAML/OIDC) enforced and SCIM provisioning configured at the enterprise level?
- Are security features (secret scanning, push protection, Dependabot, code scanning) locked on?
- Are enterprise rulesets applied and inherited so no org can weaken the baseline?
- Are allowed Actions restricted and default `GITHUB_TOKEN` permissions read-only?
- Is the audit log streamed to a SIEM with alerts on policy and owner changes?
- Is the number of enterprise owners minimal, all with MFA, and reviewed periodically?
- Was the EMU-vs-standard decision made deliberately with its trade-offs understood?

## Related

- `knowledge/github/19-organizations.md`
- `knowledge/github/20-teams.md`
- `knowledge/github/21-permissions.md`
- `knowledge/github/18-rulesets.md`
- `knowledge/github/13-security.md`
