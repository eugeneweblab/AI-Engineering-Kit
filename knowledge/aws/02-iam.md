---
id: aws/02-iam
topic: aws
slug: iam
title: "IAM"
type: doc
order: 2
status: ready
tags: [aws, iam, Resource, "aws:PrincipalOrgID", PutObject, Action, SecureTransport, Condition, policy, role, granting]
related: [aws/00-overview, aws/25-security, aws/16-secrets-manager, aws/15-cloudtrail, aws/04-s3]
when_to_use: "Read before creating any user, role, policy, or granting a service access to another."
---
# IAM

## Purpose

This document defines how to control *who can do what* in AWS: **users**, **roles**,
**policies**, and the evaluation logic that decides whether a request is allowed. IAM is the
authorization layer of AWS. Get it wrong and every other control is moot — a compromised
over-permissioned role hands an attacker the whole account.

IAM is a *global* service: identities and policies apply across all Regions.

## Why It Matters

IAM misconfiguration is the single most common cause of AWS breaches. The failure mode is
always the same: a policy grants more than it needs — `"Action": "*"` or
`"Resource": "*"` — and that excess sits dormant until an attacker, a leaked key, or a
compromised dependency uses it. Over-permissioning never breaks the app, so it is never
noticed in testing; it is only ever discovered by an incident or an audit. Least privilege
is the one discipline that contains the blast radius when something else fails.

## Core Principles

- **Least privilege by default.** Grant the minimum actions on the minimum resources.
  Start from nothing and add permissions as concrete needs appear — never start from `*`
  and trim.
- **Roles for workloads, never long-lived keys.** EC2, Lambda, ECS, and CI should assume an
  IAM role via `sts:AssumeRole` and receive short-lived, auto-rotated credentials. Static
  access keys are the most-leaked secret in existence. The role's trust policy names who
  may call `AssumeRole`; its permission policy names what they may then do. Both are
  needed, and confusing them is the usual reason an assume fails.
- **Humans authenticate through an identity provider.** Use IAM Identity Center (SSO)
  federated to your corporate IdP, not per-person IAM users with passwords.
- **The root account is not for daily use.** Lock it with hardware MFA, remove its access
  keys, and use it only for the handful of tasks that require it.
- **Explicit deny always wins.** IAM evaluation denies by default; an allow can be
  overridden by any explicit deny (including SCPs and permission boundaries). Deny is the
  strongest guardrail.

## Best Practices

- Attach permissions to **roles and groups**, not individual users; manage membership, not
  per-person policy sprawl.
- Scope every statement to specific `Resource` ARNs and add `Condition` blocks (source IP,
  MFA present, `aws:PrincipalOrgID`) to tighten further.
- Use **permission boundaries** to cap what a delegated admin can grant, and **Service
  Control Policies (SCPs)** at the Organization level to set account-wide guardrails.
- Enable MFA for every human principal; require it via policy condition for sensitive
  actions.
- Turn on **IAM Access Analyzer** to surface resources shared outside your account and to
  generate least-privilege policies from CloudTrail history.
- Rotate any credential that must exist, and prefer temporary credentials from STS. Never
  commit access keys to source control.

## Examples

**Good Example** — a role scoped to one bucket prefix, assumed by a Lambda

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["s3:GetObject", "s3:PutObject"],   // only the two actions needed
    "Resource": "arn:aws:s3:::app-uploads/incoming/*", // one bucket, one prefix
    "Condition": {
      "Bool": { "aws:SecureTransport": "true" }   // reject non-TLS requests
    }
  }]
}
```

**Bad Example** — the "it just works" policy

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "*",        // every action in every service
    "Resource": "*"       // on every resource in the account
  }]
}
// Attached to a workload role, this is a full account takeover if the role is ever
// assumed by an attacker. It also passes every test, so nothing flags it.
```

## Common Mistakes

- Using `"Action": "*"` or `"Resource": "*"` because scoping felt tedious.
- Generating long-lived access keys for an EC2 instance or CI job instead of assigning a
  role.
- Doing daily work as the root user, or leaving root access keys active.
- Attaching AWS-managed `*FullAccess` policies broadly instead of writing scoped policies.
- Forgetting that an explicit deny (or an SCP) overrides an allow, then debugging a
  "mysterious" permission failure that is actually a guardrail working correctly.
- Embedding credentials in code or environment files that reach a repo or image layer.

## Production Tips

- Feed CloudTrail into IAM Access Analyzer to right-size policies from real usage before
  tightening them.
- Alert on root-account usage, access-key creation, and policy changes via CloudTrail +
  EventBridge.
- Set an org-wide SCP that denies disabling CloudTrail, GuardDuty, or config recorders so a
  compromised admin cannot go dark.
- Review IAM Access Analyzer external-access findings on a schedule; treat any unexpected
  cross-account share as an incident.

## AI Review Checklist

- Does every policy scope `Action` and `Resource` to the minimum needed — no bare `*`?
- Do workloads assume roles and use temporary credentials instead of static access keys?
- Is the root account locked down with MFA and no active access keys?
- Are permission boundaries and SCPs in place for delegated admins and accounts?
- Is MFA required for human principals and sensitive actions?
- Are there no hardcoded credentials in code, config, or container images?
- Is IAM Access Analyzer enabled and its findings triaged?

## Related

- `knowledge/aws/00-overview.md`
- `knowledge/aws/25-security.md`
- `knowledge/aws/16-secrets-manager.md`
- `knowledge/aws/15-cloudtrail.md`
- `knowledge/aws/04-s3.md`
