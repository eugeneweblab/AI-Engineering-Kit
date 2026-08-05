---
id: architecture/15-security
topic: architecture
slug: security
title: "Architecture Security"
type: doc
order: 15
status: ready
tags: [architecture, security, AWS_KEY, PutObject, GetObject, DB_PASSWORD]
related: [architecture/11-api-first, architecture/12-integration-patterns, architecture/17-fault-tolerance, architecture/18-observability, architecture/22-cloud-architecture]
when_to_use: "Read when designing the security posture of a system: trust boundaries, secrets, data protection, and defense in depth."
---
# Architecture Security

## Purpose

This document defines security at the *architecture* level: where the trust
boundaries are, how services authenticate to each other, how secrets and data are
protected, and how a single compromise is contained. It is written so an agent can
design or review a system that is secure by structure, not by hope.

This is the architectural view. It complements — does not replace — the application
security topics (authentication, authorization, input validation) in the `security`
knowledge base. Here we care about the shape of the system: what trusts what, and
what happens when one part is breached.

## Why It Matters

Security failures at the architecture level are the ones that make headlines: a flat
network where one compromised service reaches the whole database, a secret hardcoded in
a repo, an internal API that trusts any caller. These are not bugs in a function — they
are properties of the design, so they cannot be patched away; they must be architected
out. The cost asymmetry is brutal: a trust boundary omitted in design is nearly free to
add up front and enormously expensive after a breach, when it is also a disclosure event.
Assume breach — design so that one compromised component is a contained incident, not a
total loss.

## Core Principles

- **Least privilege everywhere.** Every service, credential, and user gets the minimum
  access needed and nothing more. Broad permissions turn a small compromise into a large one.
- **Defense in depth.** No single control is trusted to hold. Layer network boundaries,
  authentication, authorization, and validation so one failure is caught by the next.
- **Assume breach; contain the blast radius.** Segment the system so a compromised service
  cannot reach data or systems it never needed. Design for the incident, not just prevention.
- **Never trust the network.** Traffic inside the perimeter is not safe. Authenticate and
  encrypt service-to-service calls (zero trust); an internal endpoint is still a target.
- **Secure by default.** The default configuration must be the safe one — encryption on,
  ports closed, access denied — so a forgotten setting fails closed, not open.

## Best Practices

- Keep secrets out of code, images, and env files committed to git. Use a secrets manager
  (Vault, cloud KMS/Secrets Manager) with rotation and audited access.
- Give each service its own scoped identity and credentials (workload identity/IAM role),
  so you can revoke or rotate one without touching others and trace who did what.
- Encrypt data in transit (TLS everywhere, including internal hops) and at rest (disk/DB
  encryption). Treat "internal only" as a network detail, not a security guarantee.
- Segment the network so tiers (public edge, app, data) are isolated; the database accepts
  connections only from the app tier, never from the internet.
- Validate and authorize at every trust boundary, not just the outer edge — an internal
  API must still check the caller's identity and permissions.
- Keep an auditable log of security-relevant events (auth, access, config change) that is
  tamper-resistant and separate from the systems it records.
- Patch and inventory dependencies; scan images and IaC in CI so a known CVE or an open
  security group fails the build.

## Examples

**Good Example** — scoped identity, secret from a manager, deny by default

```yaml
# Each service runs as its own workload identity with a narrow policy. WHY: if the
# orders service is compromised, its credential can read only the orders bucket,
# so the blast radius is one bucket, not the whole account.
serviceAccount: svc-orders
iamPolicy:
  - effect: Allow
    action: [s3:GetObject, s3:PutObject]
    resource: arn:aws:s3:::orders-data/*   # scoped to exactly what it needs
secrets:
  DB_PASSWORD:
    from: secretsManager://prod/orders/db-password  # never in the image or repo
network:
  ingress: deny-all                        # secure by default; open ports explicitly
  allow: [{ from: api-tier, port: 5432 }]  # DB reachable only from the app tier
```

**Bad Example** — shared god-credential, secret in code, flat trust

```python
# One admin key with full account access, hardcoded and shared by every service.
# WHY this is a disaster: leaking any service leaks total control, the secret is
# in git history forever, and nothing distinguishes one caller from another.
AWS_KEY = "AKIA_SUPER_ADMIN_FULL_ACCESS"   # in source, unrotatable, in every log risk

def read(bucket, key):
    # Any service can read ANY bucket; no least privilege, no segmentation.
    return s3(AWS_KEY).get(bucket, key)
```

## Common Mistakes

- Secrets committed to git or baked into container images, where they live in history forever.
- One shared, over-privileged credential used by every service, so any leak is total compromise.
- A flat network with no segmentation, letting a compromised web node reach the database directly.
- Trusting internal traffic implicitly — internal APIs that skip authentication and authorization.
- Encrypting only the public edge and leaving internal hops and backups in plaintext.
- Treating security as a final review gate instead of a design input, so boundaries have to be
  retrofitted.
- No audit trail, so after a breach you cannot tell what was accessed or by whom.

## Production Tips

- Rotate credentials and keys on a schedule and automate it; a secret that cannot be rotated
  quickly is a liability during an incident.
- Run least-privilege reviews on IAM policies periodically — permissions accrete over time and
  drift toward "allow all."
- Have a breach playbook: how to revoke credentials, isolate a service, and preserve logs.
- Ship security scanning (SAST, dependency, IaC) in CI so misconfigurations are caught before
  deploy, not in an audit.

## AI Review Checklist

- Are secrets loaded from a secrets manager, never hardcoded or committed?
- Does each service have its own least-privilege identity, not a shared god-credential?
- Is the network segmented so the data tier is unreachable from the public edge?
- Is traffic encrypted in transit and data encrypted at rest, including internal hops?
- Are identity and authorization checked at every trust boundary, not only the outer one?
- Does the design contain a single compromise (blast radius), assuming breach?
- Is there a tamper-resistant audit log of security-relevant events?

## Related

- `knowledge/architecture/11-api-first.md`
- `knowledge/architecture/12-integration-patterns.md`
- `knowledge/architecture/17-fault-tolerance.md`
- `knowledge/architecture/18-observability.md`
- `knowledge/architecture/22-cloud-architecture.md`
