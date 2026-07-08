---
id: security/30-engineering-principles
topic: security
slug: engineering-principles
title: "Engineering Principles"
type: doc
order: 30
status: ready
tags: [security, engineering-principles]
related: [security/27-best-practices, security/28-owasp-top10, security/01-security-fundamentals, security/02-threat-modeling, security/29-security-review]
when_to_use: "Read to internalize the durable mental models that should guide every security decision."
---
# Engineering Principles

## Purpose

This document names the durable *mental models* of secure engineering — the reasoning
that stays true regardless of language, framework, or the specific vulnerability at
hand. Where [best practices](27-best-practices.md) tells you what to do, this tells you
how to *think* so you make the right call in a situation no checklist anticipated.

These principles are the priors an agent should hold before reading a single line of a
diff. They are why the concrete rules elsewhere in this topic exist.

## Why It Matters

Rules cover the cases someone thought to write down; principles cover the ones nobody
did. Attackers innovate faster than checklists update, so an engineer who only follows
rules is always one step behind. Principles generalize: "fail closed" tells you what to
do with a novel error condition no rule mentions. Internalizing these models is what lets
an agent reason about a security question it has never seen before and still get it right —
which is the whole job.

## Core Principles

- **Least privilege.** Grant the minimum access needed, for the minimum time. The cost
  of a compromise is bounded by what the compromised thing could reach — so shrink it.
- **Defense in depth.** Assume any single control will fail; layer independent ones so
  the failure is caught by the next. No control is trusted alone.
- **Fail closed / secure by default.** When something breaks or is unspecified, deny.
  An error must never become an accidental "allow." Safety is the default, not the effort.
- **Never trust input.** All external data is hostile until proven otherwise at the
  trust boundary. The client is controlled by the attacker, always.
- **Minimize attack surface.** The most secure feature, dependency, permission, or byte
  of stored data is the one that doesn't exist. Less to attack means less to defend.
- **Complete mediation.** Check authorization on *every* access, every time — never
  cache "they were allowed a minute ago." Authority can be revoked between requests.
- **No security through obscurity.** A design must be safe even when the attacker knows
  exactly how it works. Secrecy of keys is fine; secrecy of mechanism is not.
- **Economy of mechanism.** Prefer simple, auditable designs. Complexity is where bugs
  hide, and you cannot secure what you cannot understand.

## Best Practices

- Apply the principles as a *default*, then relax only with a written, reviewed reason —
  the deviation, not the safe path, carries the burden of proof.
- When two principles seem to conflict, favor the one that bounds blast radius; contained
  damage is recoverable, unbounded damage often is not.
- Use principles to *design*, not just to review: pick the architecture that makes the
  insecure state impossible, not merely detectable — see [threat modeling](02-threat-modeling.md).
- Prefer making the secure path the easy path (safe wrappers, deny-by-default routers)
  so future code inherits the principle without thinking about it.
- Re-derive concrete rules from principles when facing an unfamiliar technology, rather
  than assuming the old rules transfer verbatim.

## Examples

**Good Example** — a router that embodies fail-closed and complete mediation

```ts
// Deny by default: access is granted only by an explicit, per-request policy check.
// A new route with no policy is unreachable, not wide open — the safe state is default.
function authorize(policy: Policy) {
  return (req, res, next) => {
    const decision = policy.check(req.user, req.method, req.path, req.params);
    if (decision !== "allow") return res.sendStatus(403); // any non-allow → deny
    next();
  };
}
app.use(defaultDeny);                    // anything without a policy is refused
app.get("/reports/:id", authorize(reportsPolicy), getReport); // checked every request
```

**Bad Example** — trust cached authority, fail open

```ts
// Checks permission once at login and stores "isAdmin" in the session forever.
// If the user is demoted, complete mediation is violated — stale authority persists.
if (req.session.isAdmin) return next();

// And when the policy service errors, it grants access "to avoid blocking users":
// this fails OPEN, turning an outage into an authorization bypass.
try { await policy.check(req.user); } catch { return next(); }
```

## Common Mistakes

- Treating principles as slogans on a wall instead of the tie-breaker in real decisions.
- Granting broad access for convenience, violating least privilege "just this once."
- Caching an authorization decision and reusing it, breaking complete mediation.
- Failing open on error because it "keeps the app working" — it keeps attackers working too.
- Relying on a secret design rather than a sound one (security through obscurity).
- Adding layers of complexity to a security control until no one can verify it is correct.

## AI Review Checklist

- Does each credential, role, and token hold the least privilege it needs?
- Are there at least two independent controls guarding any high-value action?
- On any error or unspecified branch, does the code deny rather than allow?
- Is all external input treated as hostile and validated at the boundary?
- Is authorization re-checked on every request, never cached as "already allowed"?
- Is the design safe even if the attacker fully understands it?
- Is the security-relevant code simple enough to audit with confidence?

## Related

- `knowledge/security/27-best-practices.md`
- `knowledge/security/28-owasp-top10.md`
- `knowledge/security/01-security-fundamentals.md`
- `knowledge/security/02-threat-modeling.md`
- `knowledge/security/29-security-review.md`
