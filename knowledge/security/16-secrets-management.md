---
id: security/16-secrets-management
topic: security
slug: secrets-management
title: "Secrets Management"
type: doc
order: 16
status: ready
tags: [security, secrets-management]
related: [security/17-encryption, security/18-https, security/23-dependency-security, security/24-supply-chain-security]
when_to_use: "Read before adding an API key, database password, token, or signing key to any code, config, or deploy pipeline."
---
# Secrets Management

## Purpose

This document defines how applications obtain, store, and rotate secrets — API
keys, database passwords, private keys, signing keys, tokens — without leaking
them. A secret is any value that grants access and cannot be regenerated freely.
The goal is that secrets never appear in source control, never sit in plaintext at
rest, and can be rotated quickly when exposed.

Secrets protect everything else, so their handling is upstream of most other
controls. Storing them safely at rest relies on [encryption](17-encryption.md);
moving them safely relies on [HTTPS/TLS](18-https.md).

## Why It Matters

A leaked secret is a skeleton key: it grants an attacker exactly the access the
application has, with no exploit required. Credentials committed to Git are the
single most common cloud-breach cause — automated scanners find public-repo keys
within seconds, and history means a secret committed once is exposed forever unless
the history is rewritten and the key rotated. Because a leak is silent, you must
assume any secret that ever touched a repo, log, or CI artifact is compromised.

## Core Principles

- **Never commit secrets to source control.** Not in code, config, tests, or
  history. Git history is permanent; a deleted-but-committed secret is still leaked.
- **Separate secrets from configuration and from code.** Inject them at runtime
  from a dedicated store; the codebase should contain references, not values.
- **Encrypt at rest, transmit over TLS.** Secrets must never sit or travel in
  plaintext outside a trusted boundary.
- **Least privilege and short lifetimes.** Each secret grants the minimum access;
  prefer short-lived, automatically rotated credentials over long-lived static keys.
- **Assume compromise; make rotation cheap.** You must be able to revoke and
  replace any secret quickly, without a code change or redeploy of the secret value.

## Best Practices

- Store secrets in a dedicated manager (HashiCorp Vault, AWS/GCP/Azure secret
  managers, cloud KMS-backed stores) and fetch them at startup or on demand. These
  provide encryption, access control, audit logging, and rotation.
- Inject secrets as environment variables or mounted files from that manager at
  deploy time; keep `.env` files local-only and in `.gitignore`. Prefer workload
  identity / IAM roles over any long-lived key when the platform supports it.
- Add automated secret scanning (pre-commit hooks and CI, e.g. gitleaks/trufflehog)
  so a secret is caught before it merges, not after it leaks.
- Scope each credential to the minimum resources and permissions, and give each
  service its own credential so one leak doesn't expose the fleet.
- Rotate secrets on a schedule and immediately on suspected exposure; design apps to
  reload credentials without downtime so rotation is painless.
- Keep secrets out of logs, error messages, stack traces, URLs (query strings get
  logged), and client-side code. Redact known secret patterns in log pipelines.

## Examples

**Good Example** — secret fetched at runtime from a manager, never in code

```python
import boto3, json

def get_db_password() -> str:
    client = boto3.client("secretsmanager")
    # Secret lives in the manager: encrypted at rest, access-controlled, audited,
    # and rotatable without touching or redeploying application code.
    resp = client.get_secret_value(SecretId="prod/db/credentials")
    return json.loads(resp["SecretString"])["password"]

DB_PASSWORD = get_db_password()  # resolved at startup; the repo holds only the SecretId
```

**Bad Example** — secret hardcoded and committed

```python
# Committed to Git: now in history forever and readable by anyone with repo access.
# Automated scanners find public-repo keys in seconds; rotation is the only fix.
DB_PASSWORD = "S3cr3t-prod-password!"          # plaintext secret in source
STRIPE_KEY = "sk_live_51H8xY2eZvKf..."         # live key, full account access
```

## Common Mistakes

- Committing `.env`, key files, or config with real values; assuming a later delete
  removes them (history still holds the secret — rotate it).
- Putting secrets in front-end code or public config, where any user can read them.
- Logging request bodies, headers, or full URLs that contain tokens or keys.
- Sharing one long-lived key across every service and environment, so one leak is total.
- Baking secrets into container images or build args, which persist in image layers.
- Treating an exposed secret as "cleaned up" by deleting it rather than rotating it.

## Production Tips

- Enable audit logging on the secret store and alert on unusual access patterns.
- Automate rotation end to end (manager rotates, app reloads) and test it in staging;
  a rotation path you never exercise will fail during an incident.
- On any suspected leak, rotate first and investigate second — revocation is the only
  action that actually closes the exposure.

## AI Review Checklist

- Are all secrets loaded at runtime from a manager or injected env, never hardcoded?
- Is there a secret-scanning check in pre-commit and CI?
- Are `.env` and key files git-ignored, and is history clean of committed secrets?
- Is each credential least-privilege and scoped per service/environment?
- Are secrets kept out of logs, URLs, error output, and client-side code?
- Can every secret be rotated and revoked without a code change?

## Related

- `knowledge/security/17-encryption.md`
- `knowledge/security/18-https.md`
- `knowledge/security/23-dependency-security.md`
- `knowledge/security/24-supply-chain-security.md`
