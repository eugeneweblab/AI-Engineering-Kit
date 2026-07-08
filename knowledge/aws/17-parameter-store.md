---
id: aws/17-parameter-store
topic: aws
slug: parameter-store
title: "Parameter Store"
type: doc
order: 17
status: ready
tags: [aws, parameter-store]
related: [aws/16-secrets-manager, aws/02-iam, aws/12-lambda, aws/14-cloudwatch, aws/28-best-practices]
when_to_use: "Read before storing application configuration or non-rotating secrets in AWS Systems Manager Parameter Store."
---
# Parameter Store

## Purpose

This document defines how to use AWS Systems Manager Parameter Store for configuration and
secrets: parameter types, encryption, hierarchy, versioning, and access control. It is
written so an agent can externalize configuration cleanly and know when Parameter Store is
the right tool versus [Secrets Manager](16-secrets-manager.md).

Parameter Store holds configuration values — feature flags, endpoints, tuning knobs — and,
via `SecureString`, KMS-encrypted secrets. It is cheap, versioned, and hierarchical, which
makes it the default home for the settings an application should not hardcode.

## Why It Matters

Configuration baked into code or images turns every config change into a redeploy and
every environment difference into a copy-paste bug. Externalizing config into a versioned,
access-controlled store lets you change behavior without shipping code and audit who
changed what. The cost of getting it wrong is subtle: a `String` parameter used for a
password stores it in plaintext, and a missing distinction between config and secrets
leads teams to either over-pay (everything in Secrets Manager) or under-protect
(secrets sitting unencrypted).

## Core Principles

- **Encrypt secrets with `SecureString`; never a plain `String`.** A `String` value is
  stored and returned unencrypted. Any credential must be `SecureString` backed by KMS.
- **Use a hierarchy that mirrors environments.** Names like `/app/prod/db/host` allow
  path-based fetch and path-scoped IAM. Flat, ad-hoc names cannot be governed.
- **Least-privilege by path.** Grant `ssm:GetParameter*` on a path prefix (and the KMS
  key for `SecureString`), not on `*`.
- **Fetch at runtime and cache.** Read parameters at startup, cache them, and refresh on a
  schedule. Do not read on every request — calls are rate-limited and billed at higher tiers.
- **Choose Parameter Store vs Secrets Manager deliberately.** Parameter Store for config
  and static secrets (cheaper, no built-in rotation); Secrets Manager when you need
  automatic rotation, generated secrets, or cross-account sharing.

## Best Practices

- Store secrets as `SecureString` with a **customer-managed KMS key** so decryption is a
  separately auditable control; the standard tier is free for the parameter itself.
- Organize by `/service/environment/...` and fetch whole subtrees with `GetParametersByPath`
  to load an environment's config in one call.
- Reference parameters by name from IaC and, where supported, from
  [Lambda](12-lambda.md)/ECS directly (e.g. `valueFrom` in a task definition) rather than
  copying values into plaintext env vars.
- Use the **advanced tier** only when you need parameters larger than 4 KB, more than the
  standard-tier limit, or parameter policies (expiration, change notification) — it is
  billed per parameter, so do not default to it.
- Enable **parameter policies** to expire short-lived values and to emit a change event you
  can alarm on via EventBridge/[CloudWatch](14-cloudwatch.md).
- Rely on automatic **versioning**: every write creates a new version, so you can pin to a
  version and roll back config safely.

## Examples

**Good Example** — SecureString, path fetch, cached, scoped IAM

```python
import boto3
from functools import lru_cache

_ssm = boto3.client("ssm")

@lru_cache(maxsize=1)                               # load once, reuse across invocations
def config():
    resp = _ssm.get_parameters_by_path(
        Path="/orders/prod/",
        Recursive=True,
        WithDecryption=True,                        # decrypts SecureString values
    )
    return {p["Name"].split("/")[-1]: p["Value"] for p in resp["Parameters"]}
```

```json
// IAM: read only this service's prod subtree, plus decrypt with its key.
{
  "Effect": "Allow",
  "Action": ["ssm:GetParameter", "ssm:GetParametersByPath"],
  "Resource": "arn:aws:ssm:us-east-1:111122223333:parameter/orders/prod/*"
}
```

**Bad Example** — plaintext secret, no scope, per-request fetch

```python
import boto3

def handler(event, context):
    ssm = boto3.client("ssm")                       # new client per call
    # Stored as type "String" → the DB password sits in plaintext, readable by anyone
    # with ssm:GetParameter, and it is NOT decrypted-on-read because it was never encrypted.
    pw = ssm.get_parameter(Name="/db_password")["Parameter"]["Value"]
    # Fetched on every invocation → throttling and cost under load.
    # Paired policy: { "Action": "ssm:*", "Resource": "*" }  # far too broad
    return connect(pw)
```

## Common Mistakes

- Storing a credential as `String` instead of `SecureString`, leaving it in plaintext.
- Granting `ssm:*` on `*` rather than `GetParameter*` on a path prefix.
- Forgetting `WithDecryption=True`, then treating an encrypted blob as if it were the value.
- Reading parameters on every request instead of caching, hitting throttle limits.
- Using Parameter Store for secrets that genuinely need rotation — that is Secrets
  Manager's job; here you would have to build rotation yourself.
- Defaulting to the advanced tier and paying per parameter without needing its features.

## Production Tips

- Use the Parameters and Secrets Lambda extension to cache parameters locally and cut
  `GetParameter` calls, which are both rate-limited and billed above the standard throughput.
- Alarm on parameter changes to production paths via EventBridge so config drift is visible.
- Keep the KMS key policy for `SecureString` parameters tight; whoever can decrypt the key
  can read the secret regardless of the SSM policy.
- Version-pin critical config in deploys and roll back by referencing the previous
  parameter version rather than hand-editing values.

## AI Review Checklist

- Are all secrets stored as `SecureString`, never plain `String`?
- Is `SecureString` read with `WithDecryption=True` and backed by a KMS key?
- Is IAM scoped to a path prefix and the specific KMS key, not `*`?
- Are parameters fetched at startup and cached, not read per request?
- Is the choice of Parameter Store (vs Secrets Manager) justified by no rotation need?
- Is the advanced tier used only when its features are actually required?

## Related

- `knowledge/aws/16-secrets-manager.md`
- `knowledge/aws/02-iam.md`
- `knowledge/aws/12-lambda.md`
- `knowledge/aws/14-cloudwatch.md`
- `knowledge/aws/28-best-practices.md`
