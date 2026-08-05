---
id: playbooks/01-site-down
topic: playbooks
slug: site-down
title: "Playbook — Site Down"
type: doc
order: 1
status: ready
tags: [playbooks, site-down]
related: [playbooks/02-failed-deployment, templates/03-incident-report, workflows/06-investigate-production-bug, tools/29-observability-tools, performance/25-production-monitoring]
when_to_use: "Follow when the application is unreachable, erroring for most users, or failing its primary flow in production."
---
# Playbook — Site Down

## Purpose

Restore service, then find out why. This playbook covers the first hour of a user-visible
outage: confirming scope, stabilizing, and handing off to diagnosis.

**The order matters.** Diagnosing before stabilizing extends the outage for the sake of
curiosity that can be satisfied afterwards from logs.

---

## Step 1 — Confirm and scope it (2 minutes)

Before touching anything, establish what is actually broken:

```bash
curl -sS -o /dev/null -w '%{http_code} %{time_total}s\n' https://example.com/
curl -sS -o /dev/null -w '%{http_code} %{time_total}s\n' https://example.com/api/health
dig +short example.com                # DNS resolving?
curl -sSI https://example.com | head  # which layer answers — CDN, LB, or app?
```

Answer three questions:

- **Everyone or someone?** One region, one browser, or one account is a different incident
  from a total outage.
- **Everything or one path?** The home page loading while checkout 500s narrows the search
  enormously.
- **Since when?** Line the start time up against deploys, migrations, cron jobs, and
  third-party status pages.

If it is not user-visible, it is not this playbook — investigate normally.

---

## Step 2 — Declare it (1 minute)

Say it out loud in the incident channel, even if you expect to fix it in five minutes:

> **INC — checkout returning 500 for all users since ~14:10 UTC. I'm on it. Updates every 15
> minutes.**

Three reasons: it stops two people fixing it in opposite directions, it starts the timeline,
and it tells everyone else where to look for updates instead of asking.

Post a status-page update if customers are affected. "We are investigating an issue with
checkout" is enough — do not wait until you know the cause.

---

## Step 3 — Check the usual suspects (5 minutes)

Most outages are one of these. Check them in this order — cheapest and most likely first:

| Suspect | Check |
|---|---|
| A recent deploy | What shipped in the last hour? `git log --oneline --since='2 hours ago'` |
| A migration | Did a schema change run? Is a long lock still held? |
| Certificate expiry | `echo \| openssl s_client -connect example.com:443 2>/dev/null \| openssl x509 -noout -dates` |
| Disk full | `df -h` — logs and uploads fill disks silently |
| A dependency | Payment provider, auth provider, CDN — check their status pages |
| Credentials | Did an API key or token expire or get rotated? |
| Traffic | A spike, a crawler, or an attack — check request rate before assuming a bug |
| Cron / queue | A job stuck holding a lock, or a queue backed up |

```bash
# Error rate and recent failures — adapt to your stack
tail -n 200 /var/log/app/error.log
docker compose logs --tail=200 app
kubectl logs -l app=web --tail=200 --since=1h
```

---

## Step 4 — Stabilize

**Restore service with the fastest safe action, even if it is not the fix.**

In order of preference:

1. **Roll back** if a deploy correlates with the start time. This is almost always right,
   and it is reversible — see [Failed Deployment](02-failed-deployment.md).
2. **Disable the feature** if a flag exists for the broken path.
3. **Restart** the affected service if the failure looks like exhausted resources
   (connections, memory, file handles). Capture a snapshot first if you can — a restart
   destroys the evidence.
4. **Scale out** if the cause is load rather than a defect.
5. **Degrade deliberately** — serve cached content, disable the failing feature, show a
   maintenance page for one route rather than failing the whole site.

Confirm recovery from outside your network, not just by the metric that alerted:

```bash
curl -sS -o /dev/null -w '%{http_code} %{time_total}s\n' https://example.com/checkout
```

**Do not** apply a speculative fix to production while it is down. A wrong guess turns one
incident into two, and now you cannot tell which change caused what.

---

## Step 5 — Escalate on a timer

Set a 15-minute timer at declaration. If service is not restored when it fires, escalate —
regardless of how close you feel to the answer. That feeling is unreliable under pressure.

Escalate immediately, without waiting, if:

- Data may be being lost or corrupted.
- The cause looks like a security incident — switch to
  [Security Incident](03-security-incident.md).
- The fix requires access or authority you do not have.

---

## Step 6 — Keep a log

In the incident channel, as you go. One line per action, with times:

```
14:12 alerted — checkout 500s, ~100% of requests
14:15 declared, status page updated
14:18 ruled out deploy — last release 09:40
14:24 db connections at max (200/200); app pool healthy
14:31 found: analytics job opened a connection per row, never closed
14:33 killed job; connections draining
14:41 checkout recovering; error rate < 1%
14:46 confirmed recovered from external check
```

You will not remember this afterwards, and it is exactly what the incident report needs —
including the wrong turns. See [Incident Report](../templates/03-incident-report.md).

---

## Step 7 — Close out

- Confirm recovery from an external check, not only from your dashboard.
- Update the status page to resolved.
- Say explicitly in the channel that the incident is over.
- **If you mitigated rather than fixed** — restarted, disabled a feature, scaled up — open a
  ticket now, while the context is fresh. Mitigations become permanent by accident.
- Schedule the incident report within a few days.

---

## Common Mistakes

- **Diagnosing before stabilizing**, extending the outage to satisfy curiosity.
- **Not declaring**, so two people work in parallel and undo each other.
- **Restarting before capturing evidence**, destroying the only copy of the state that
  explains it.
- **Multiple simultaneous changes**, making the eventual recovery unattributable.
- **Trusting the alert that fired** as the definition of recovery; check what a user sees.
- **No log**, leaving the report to be reconstructed from memory a week later.
- **Silence**, so everyone asks for updates in the middle of the response.
- **Mitigation logged nowhere** and quietly becoming the permanent state.

---

## Related

- `knowledge/playbooks/02-failed-deployment.md`
- `knowledge/templates/03-incident-report.md`
- `knowledge/workflows/06-investigate-production-bug.md`
- `knowledge/tools/29-observability-tools.md`
