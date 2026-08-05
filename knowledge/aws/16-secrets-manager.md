---
id: aws/16-secrets-manager
topic: aws
slug: secrets-manager
title: "Secrets Manager"
type: doc
order: 16
status: ready
tags: [aws, secrets-manager, lru_cache, get_secret_value, "@lru", DB_PASSWORD, client, loads]
related: [aws/17-parameter-store, aws/02-iam, aws/12-lambda, aws/05-rds, aws/15-cloudtrail]
when_to_use: "Read before storing, retrieving, or rotating any credential, API key, or database password in AWS."
---
# Secrets Manager

## Purpose

This document defines how to manage secrets — database passwords, API keys, tokens — with
AWS Secrets Manager so they are encrypted, access-controlled, rotated, and never end up in
code or logs. It is written so an agent can wire an application to a secret correctly and
avoid the most common way credentials leak.

Secrets Manager stores a secret encrypted with KMS, controls who can read it via IAM, and
can rotate it automatically. It exists so that a credential lives in exactly one governed
place instead of being copied into environment variables, repos, and CI configs where it
cannot be tracked or revoked.

## Why It Matters

A leaked long-lived credential is one of the most common and most damaging cloud
incidents. Secrets hardcoded in source, baked into images, or pasted into env vars spread
uncontrollably and rarely get rotated, so a single old checkout can compromise production
years later. Centralizing secrets makes them auditable ([CloudTrail](15-cloudtrail.md)
records every read), revocable, and rotatable. The whole point is to shrink the window
during which a compromised secret is still valid.

## Core Principles

- **A secret lives in one governed store, never in code.** No credentials in source, in
  Docker images, in plaintext env files, or in CI variables. If it grants access, it goes
  in Secrets Manager.
- **Grant read access narrowly.** Only the specific role that needs a secret gets
  `secretsmanager:GetSecretValue` on that specific secret ARN — not `*`.
- **Rotate automatically.** A secret that never changes is a secret that has effectively
  leaked over time. Enable rotation so exposure has a bounded lifetime.
- **Fetch at runtime, cache in memory, never log.** Retrieve the secret when the process
  starts (or via the caching layer), keep it in memory, and never write it to a log line.
- **Encrypt with a customer-managed KMS key for sensitive secrets** so key access is a
  second, separately auditable control.

## Best Practices

- Reference secrets by ARN and read them at application start; in [Lambda](12-lambda.md),
  read at init and cache in the container (or use the Secrets Manager Lambda extension /
  Parameters and Secrets extension to cache and cut API calls and cost).
- Enable **managed rotation** for supported databases ([RDS](05-rds.md), Redshift,
  DocumentDB); for others, provide a rotation Lambda. Choose a rotation interval that
  matches your risk tolerance (e.g. 30–90 days).
- Scope IAM policies to a single secret ARN and, where possible, a `secretsmanager:VersionStage`
  condition. Deny broad `secretsmanager:*`.
- Use resource-based policies on the secret plus KMS key policy so cross-account access is
  explicit and reviewable.
- Prefer Secrets Manager over [Parameter Store](17-parameter-store.md) when you need
  built-in rotation, cross-account sharing, or generated secrets; use Parameter Store for
  plain config and to save cost on non-rotating values.
- Never store a secret in a version-control system, even encrypted, if the decryption path
  is also in the repo.

## Examples

**Good Example** — fetch at init, cache, scoped IAM

```python
import json, boto3
from functools import lru_cache

_client = boto3.client("secretsmanager")

@lru_cache(maxsize=1)                       # fetched once per container, kept in memory
def db_creds():
    resp = _client.get_secret_value(SecretId="prod/orders/db")
    return json.loads(resp["SecretString"])  # never printed / logged

def connect():
    c = db_creds()
    return open_pool(user=c["username"], password=c["password"], host=c["host"])
```

```json
// IAM policy: read exactly one secret, nothing else.
{
  "Effect": "Allow",
  "Action": "secretsmanager:GetSecretValue",
  "Resource": "arn:aws:secretsmanager:us-east-1:111122223333:secret:prod/orders/db-*"
}
```

**Bad Example** — hardcoded, unrotated, over-broad

```python
DB_PASSWORD = "S3cr3t-prod-password"        # in source control → leaked forever, unrotatable
print(f"connecting with {DB_PASSWORD}")     # now it is in CloudWatch logs too

# Paired IAM policy that makes it worse:
# { "Action": "secretsmanager:*", "Resource": "*" }  # any secret, any operation
```

## Common Mistakes

- Hardcoding secrets in source, images, or plaintext env vars where they cannot be rotated
  or revoked.
- Logging the secret value (or an error object that contains it).
- Granting `secretsmanager:GetSecretValue` on `*` instead of a single secret ARN.
- Never enabling rotation, so a leaked credential stays valid indefinitely.
- Fetching the secret on every request instead of caching, adding latency and API cost.
- Using the default AWS-managed KMS key for highly sensitive secrets when a
  customer-managed key with its own policy is warranted.

## Production Tips

- Use the Parameters and Secrets Lambda extension (or an SDK cache) to serve cached
  secrets locally and reduce `GetSecretValue` calls, which are billed and rate-limited.
- Alarm on unusual `GetSecretValue` patterns via [CloudTrail](15-cloudtrail.md) +
  CloudWatch — a spike can signal a compromised role enumerating secrets.
- Test rotation end-to-end in staging; a rotation that breaks the app at 2 a.m. is worse
  than manual rotation. Support the two-version (AWSCURRENT / AWSPENDING) handoff.
- Delete unused secrets with a recovery window rather than immediately, so an accidental
  delete can be undone.

## AI Review Checklist

- Are there zero credentials in source, images, env files, or CI variables?
- Is each `GetSecretValue` grant scoped to a specific secret ARN, not `*`?
- Is automatic rotation enabled with a defined interval?
- Is the secret fetched at init and cached, never logged?
- Are sensitive secrets encrypted with a customer-managed KMS key?
- Is secret access auditable via CloudTrail and alarmed for anomalies?

## Related

- `knowledge/aws/17-parameter-store.md`
- `knowledge/aws/02-iam.md`
- `knowledge/aws/12-lambda.md`
- `knowledge/aws/05-rds.md`
- `knowledge/aws/15-cloudtrail.md`
