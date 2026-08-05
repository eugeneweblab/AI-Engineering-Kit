---
id: security/25-monitoring
topic: security
slug: monitoring
title: "Security Monitoring"
type: doc
order: 25
status: ready
tags: [security, monitoring, sha256, toISOString, Date]
related: [security/26-incident-response, security/03-authentication, security/21-rate-limiting, security/16-secrets-management, security/29-security-review]
when_to_use: "Read before adding logging, audit trails, or alerting to any security-relevant flow."
---
# Security Monitoring

## Purpose

This document defines how to observe a system so that an attack, a breach, or an
abuse pattern becomes *visible* while there is still time to react. It covers what
to log, what to alert on, and — just as important — what must never appear in a log.

Monitoring is the detective control that backs up your preventive controls. Even a
well-built system will be probed; the question is whether you notice. Without
monitoring, a compromise runs indefinitely and the first sign is a customer,
a researcher, or a ransom note. This is the input to [incident response](26-incident-response.md).

## Why It Matters

The median attacker dwells inside a network for weeks before discovery, and almost
always the evidence was in the logs the whole time — nobody was watching. Monitoring
turns "we were breached six months ago and never knew" into "we caught the anomaly in
minutes." It is also a *forensic* control: after an incident, logs are the only record
of what the attacker touched. If you did not capture it before the event, it is gone.
Finally, logs are themselves a security surface — a log that captures passwords or
tokens is a second copy of your secrets, often less protected than the first.

## Core Principles

- **Log security events, never secrets.** Record *that* a login failed, the user id,
  and the source IP — never the password, token, session id, or full card number.
- **Make logs tamper-evident.** An attacker's first move after entry is to erase
  tracks. Ship logs off-host in real time to append-only storage the app cannot delete.
- **Detect, then alert — alerting without detection is noise.** Define what "abnormal"
  means (thresholds, baselines) so a signal fires instead of drowning in volume.
- **Every log line needs identity and context.** Timestamp (UTC), actor, source IP,
  action, resource, and outcome. A log you cannot correlate is a log you cannot use.
- **Monitor the security controls themselves.** Alert when logging stops, when a WAF
  is disabled, or when an admin grants themselves a role. Silence is a signal.

## Best Practices

- Log authentication events (success, failure, lockout, MFA, password reset),
  authorization denials, and all privilege or role changes — see [authentication](03-authentication.md).
- Emit **structured** logs (JSON) with stable field names so alerts can query them.
  Free-text logs cannot be reliably searched under pressure.
- Alert on rate-based anomalies: spikes in 401/403, [rate-limit](21-rate-limiting.md)
  rejections, 5xx bursts, or a single IP fanning across many accounts.
- Redact or hash sensitive fields at the logging boundary, not downstream. Assume any
  log may be shipped to a third-party SIEM.
- Set retention deliberately: long enough for forensics (often 90–365 days), short
  enough to satisfy privacy law. Document the number and the reason.
- Synchronize clocks (NTP) and log in UTC so events across services can be ordered.
- Route logs and alerts to an on-call rotation, not an inbox nobody reads.

## Examples

**Good Example** — structured, redacted, correlatable security event

```ts
// Log the event and its context, never the credential itself.
logger.warn({
  event: "auth.login.failed",
  userId: user?.id ?? null,        // null when the account does not exist
  emailHash: sha256(email),        // hashed so logs can't enumerate valid emails
  sourceIp: req.ip,
  userAgent: req.headers["user-agent"],
  reason: "bad_password",
  ts: new Date().toISOString(),    // UTC, ISO-8601, sortable across services
});
// A downstream rule alerts when auth.login.failed from one IP exceeds N in 1 min.
```

**Bad Example** — logs the secret, unstructured, unqueryable

```ts
// Captures the plaintext password into a second, less-protected store.
console.log(`Login failed for ${email} with password ${password}`);
// Free text: no field to threshold on, no actor id, local time, and it leaks
// exactly the credentials an attacker would want from a log breach.
```

## Common Mistakes

- Logging passwords, tokens, session ids, API keys, or full PANs "for debugging."
- Storing logs only on the host that generated them — the first thing an intruder wipes.
- Alerting on everything, so real signals are buried and on-call learns to ignore pages.
- No alert when *logging itself* stops, so a silenced pipeline looks like calm.
- Using local timestamps, making cross-service correlation impossible during an incident.
- Retaining raw PII in logs indefinitely, turning the log store into a compliance liability.

## Production Tips

- Centralize into a SIEM or log platform with role-based access; treat log access as
  privileged and audit it.
- Build a small set of high-signal alerts first (auth-failure spikes, new admin,
  disabled control) rather than a large set of noisy ones.
- Run periodic detection drills: trigger a benign "attack" and confirm the alert fires.
- Sample high-volume non-security logs, but never sample security events — you need all of them.

## AI Review Checklist

- Are security events (auth, authz denials, privilege changes) logged with actor, IP, and outcome?
- Is it verified that no secret, token, session id, or full PAN reaches any log?
- Are logs shipped off-host to append-only/tamper-evident storage?
- Are logs structured (JSON) with stable field names and UTC timestamps?
- Is there at least one alert on abnormal rates (401/403 spikes, rate-limit rejections)?
- Is there an alert for the failure of a security control (logging stops, WAF off)?
- Is log retention set to a documented, privacy-compliant duration?

## Related

- `knowledge/security/26-incident-response.md`
- `knowledge/security/03-authentication.md`
- `knowledge/security/21-rate-limiting.md`
- `knowledge/security/16-secrets-management.md`
- `knowledge/security/29-security-review.md`
