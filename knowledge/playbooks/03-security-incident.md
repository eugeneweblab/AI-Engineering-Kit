---
id: playbooks/03-security-incident
topic: playbooks
slug: security-incident
title: "Playbook — Security Incident"
type: playbook
order: 3
status: ready
tags: [playbooks, security-incident, DEPLOY_TOKEN]
related: [playbooks/01-site-down, security/26-incident-response, security/16-secrets-management, templates/03-incident-report, tools/29-observability-tools]
when_to_use: "Follow when a credential has leaked, unauthorized access is suspected, or a compromise is reported."
---
# Playbook — Security Incident

## Purpose

Contain the exposure, preserve the evidence, and work out what was reachable. A security
incident differs from an outage in three ways that change the procedure: the clock started
before you noticed, evidence is destroyed by ordinary remediation, and there may be legal
obligations with deadlines.

---

## Step 0 — Before anything else

**If a credential is exposed, assume it is compromised.** Not "probably fine because the repo
is private", not "it was only in a log". Rotation is cheap; the alternative is not.

**Do not tamper with evidence.** Do not delete the leaked commit, wipe the compromised
container, or clear the logs until you have copies. Deleting a commit does not un-leak the
secret — it is in every clone, every fork, and the platform's own history — and it destroys
the record of when it was introduced.

**Escalate immediately** if any of these are true:
- Customer data may have been accessed.
- The access is ongoing.
- Regulatory notification may apply (GDPR, CCPA, PCI, sector-specific rules).

Those cases have deadlines and are not an engineer's decision alone.

---

## Step 1 — Contain (minutes, not hours)

Cut off access first. Investigate after.

**Leaked credential:**

```bash
# Rotate at the provider — issuing a new key does not disable the old one.
# Revoke explicitly, then verify the old value is rejected.
curl -sS -o /dev/null -w '%{http_code}\n' \
  -H "Authorization: Bearer $OLD_TOKEN" https://api.provider.example/v1/me
# expect 401
```

Rotate everything the exposure could reach, not only the one key you saw: a leaked `.env` is
every value in that file, and a compromised CI token is everything that token could deploy.

**Suspected account compromise:** invalidate sessions, force a password reset, revoke API
tokens and OAuth grants, and check for attacker-created persistence — new users, new SSH
keys, new tokens, changed webhook endpoints, forwarding rules.

**Suspected host compromise:** isolate rather than terminate. Remove it from the load
balancer and restrict its egress, but keep it running — terminating destroys memory,
process state, and open connections you will want later.

---

## Step 2 — Preserve evidence

Before remediating further, take copies:

```bash
# Snapshot rather than delete
aws ec2 create-snapshot --volume-id vol-xxxx --description "INC-2026-07-14 forensics"

# Export the relevant log window before rotation clears it
aws logs create-export-task --log-group-name /app/prod \
  --from 1752460000000 --to 1752470000000 --destination incident-evidence

# Record the exposure itself
git log --all --oneline -S 'AKIA' -- .env      # when the secret entered history
```

Note the times, the commands, and who ran them. If this becomes a legal or contractual
matter, the chain of custody matters as much as the findings.

---

## Step 3 — Determine the blast radius

Answer three questions, in order:

1. **What did the credential permit?** Read or write, which resources, which environment.
   Check the actual policy or scope rather than assuming — keys are routinely broader than
   their intended use.
2. **Was it used?** Provider audit logs, database access logs, your own request logs.
   Absence of evidence is weak evidence here: say "no signs of use in the logs we retain"
   rather than "it was not used".
3. **How long was it exposed?** From introduction to revocation. A key committed eighteen
   months ago in a public repository is a different incident from one pasted into a private
   channel an hour ago.

```bash
# Where else has this value been used or copied?
rg -n 'AKIA[0-9A-Z]{16}' --hidden --glob '!.git'
git log --all -S '<secret fragment>' --oneline
```

Public exposure — a public repository, a published package, a client-side bundle — should be
treated as used. Automated scanners find committed keys within minutes.

---

## Step 4 — Close the path

Rotation stops the current exposure; it does not stop the next one.

- **Remove the secret from where it lived** and move it to a secrets manager or environment
  variable — see [Security — Secrets Management](../security/16-secrets-management.md).
- **History rewriting is optional and usually not worth it.** Rewriting git history is
  disruptive and does not help: the value is already compromised, and rotation is what
  actually resolves it. Rewrite only when required by policy, and rotate regardless.
- **Add detection**: secret scanning in pre-commit and in CI, so the next one is caught
  before it lands.
- **Narrow the scope**: if the key permitted more than its use required, fix that now while
  the reason is fresh.

---

## Step 5 — Report

Security incidents need the same report as any other, with additions:

- **Exposure window** — introduced when, revoked when, exposed where.
- **Access assessment** — what the credential permitted, and what the logs show.
- **Data involved** — whether personal or regulated data was reachable, stated precisely.
- **Notification** — whether legal or customer notification applies, and who owns it.

Keep the report blameless and factual. Someone committed a key; the finding is that a key
could be committed and reach production undetected. See
[Incident Report](../templates/03-incident-report.md).

---

## What Not to Do

- **Do not delete the commit and move on.** The secret is compromised the moment it is
  pushed; deletion only removes your ability to reconstruct the timeline.
- **Do not issue a new key without revoking the old one.** Rotation is two actions.
- **Do not terminate a suspect host** before snapshotting it.
- **Do not discuss the incident in the compromised system.** If the breach may include chat
  or email, coordinate elsewhere.
- **Do not conclude "no evidence of use" is "not used"** when your retention window is
  shorter than the exposure.
- **Do not decide the notification question alone.** Escalate it.

---

## Examples

**Good Example** — contain without destroying evidence, then rotate and disclose

```bash
# 1. Contain. Isolate rather than delete — the disk is evidence.
kubectl cordon node-7                       # stop new scheduling
kubectl scale deployment/api --replicas=0   # stop the workload, keep the volume
aws ec2 create-snapshot --volume-id vol-0abc --description "incident-2026-08-04"

# 2. Revoke access along every path, not just the one that was used.
aws iam delete-access-key --access-key-id AKIA... --user-name deploy
gh api -X DELETE /orgs/acme/actions/secrets/DEPLOY_TOKEN
psql -c "ALTER ROLE app WITH PASSWORD 'new-secret';"

# 3. Invalidate anything derived from the compromised secret.
redis-cli --scan --pattern 'session:*' | xargs -r redis-cli DEL   # force re-auth
```

```text
4. Preserve the timeline: who accessed what, when, from where.
   Access logs, audit logs, and the snapshot are copied to a separate account
   the compromised credentials could not reach.

5. Disclose on the legal clock, not when the investigation finishes.
   GDPR: 72 hours from becoming aware. The report can say "investigation ongoing".
```

**Bad Example** — clean up first, ask questions later

```bash
# Destroys the evidence needed to establish what was accessed and for how long.
kubectl delete pod api-7d9f8                # the compromised container, gone
rm -rf /var/log/nginx/access.log*           # the record of what was requested
docker system prune -af                     # the image that would show the change

# Rotates one key and calls it contained, while the same credential is still
# in three other places.
aws iam delete-access-key --access-key-id AKIA...
```

Without the logs, "we found no evidence of data access" is not a finding — it is the absence
of the ability to make one, and regulators read it that way.

---

## Related

- `knowledge/playbooks/01-site-down.md`
- `knowledge/security/26-incident-response.md`
- `knowledge/security/16-secrets-management.md`
- `knowledge/templates/03-incident-report.md`
- `knowledge/tools/29-observability-tools.md`
