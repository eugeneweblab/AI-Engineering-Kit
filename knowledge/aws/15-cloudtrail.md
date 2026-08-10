---
id: aws/15-cloudtrail
topic: aws
slug: cloudtrail
title: "CloudTrail"
type: doc
order: 15
status: ready
tags: [aws, cloudtrail, GetAtt, CloudWatch, audit, investigating, resource]
related: [aws/14-cloudwatch, aws/02-iam, aws/04-s3, aws/25-security, aws/16-secrets-manager]
when_to_use: "Read before configuring audit logging, or when investigating who changed or accessed an AWS resource."
---
# CloudTrail

## Purpose

This document defines how to configure AWS CloudTrail so every action in your account is
recorded, tamper-evident, and available when you need it — for security investigation,
compliance, and change forensics. It is written so an agent sets up an audit trail that
would actually stand up during an incident.

CloudTrail records API activity across your AWS account: who did what, from where, and
when. It is the answer to "who deleted that bucket?" and "was this key used after we
thought it was revoked?". Without it, those questions have no answer.

## Why It Matters

During a security incident, the audit log is the single most valuable artifact — and it
is worthless if it was not already running, or if the attacker could turn it off or edit
it. The failure mode is quiet: an account with no organization trail, or a trail with no
log-file validation, looks fine every day until the day you need history that does not
exist. CloudTrail is insurance you must buy *before* the fire, configured so it cannot be
trivially disabled or altered.

## Core Principles

- **Enable a trail everywhere, always on.** Use an organization trail covering all
  accounts and all regions. Gaps in coverage are blind spots an attacker will use.
- **Protect the log from the operator.** Deliver logs to a dedicated, locked-down
  [S3](04-s3.md) bucket in a separate security account, so someone with power in the
  workload account cannot delete their own tracks.
- **Make tampering detectable.** Enable log-file integrity validation; a log you cannot
  prove is unaltered is not evidence.
- **Capture the events that matter.** Management events are on by default; enable data
  events selectively for sensitive resources (specific S3 buckets, Lambda) where
  object-level access must be audited.
- **Route to alerting, not just storage.** A log nobody watches catches problems late.
  Stream to [CloudWatch](14-cloudwatch.md) Logs / EventBridge and alarm on dangerous
  actions in near real time.

## Best Practices

- Create a **multi-region organization trail**; do not rely on per-account, per-region
  trails that drift out of coverage.
- Store logs in an S3 bucket with **Object Lock** (WORM), bucket policy denying delete,
  SSE-KMS encryption, and Block Public Access — in a dedicated logging/security account.
- Turn on **log-file validation** (`EnableLogFileValidation`) so digest files prove the
  chain is intact.
- Enable **data events** only for sensitive resources; account-wide data events on all S3
  objects can be extremely high volume and cost.
- Send events to CloudWatch Logs and create metric-filter alarms for high-risk API calls:
  `StopLogging`, `DeleteTrail`, root-account usage, `DisableKey`, IAM policy changes,
  security-group opens.
- Restrict who can call `cloudtrail:StopLogging`, `DeleteTrail`, or `UpdateTrail` to a
  tiny break-glass role, and alarm when they are used.
- Set a retention/lifecycle policy that matches your compliance requirement (often 1–7
  years) rather than deleting logs early.

## Examples

**Good Example** — org trail, validated, locked, alarmed (CloudFormation)

```yaml
AuditTrail:
  Type: AWS::CloudTrail::Trail
  Properties:
    IsOrganizationTrail: true            # covers every account in the org
    IsMultiRegionTrail: true             # no region is a blind spot
    IncludeGlobalServiceEvents: true     # captures IAM, STS, etc.
    EnableLogFileValidation: true        # produces tamper-evident digests
    S3BucketName: !Ref AuditLogBucket    # locked bucket in the security account
    KMSKeyId: !Ref AuditKmsKey           # encrypt logs at rest
    CloudWatchLogsLogGroupArn: !GetAtt TrailLogGroup.Arn   # stream for real-time alarms
    CloudWatchLogsRoleArn: !GetAtt TrailToCwRole.Arn
    IsLogging: true
```

**Bad Example** — single region, deletable, unvalidated

```yaml
Trail:
  Type: AWS::CloudTrail::Trail
  Properties:
    IsMultiRegionTrail: false            # activity in other regions is invisible
    EnableLogFileValidation: false       # logs could be edited undetectably
    S3BucketName: !Ref AppBucket         # same account/team can delete their own trail
    # No CloudWatch stream → nobody is alerted when StopLogging is called.
```

## Common Mistakes

- No organization trail; new accounts or regions silently have no audit coverage.
- Storing logs in the same account (or a bucket the workload team controls), so an
  insider or attacker can erase evidence.
- Log-file validation disabled, so the trail is not defensible as evidence.
- Enabling data events for all S3 objects account-wide and getting a surprise bill.
- No alarms on `StopLogging`/`DeleteTrail`, so disabling the audit log goes unnoticed.
- Deleting logs before the compliance retention window ends.

## Production Tips

- Use EventBridge rules on CloudTrail events to trigger automated response (e.g. quarantine
  a security group that was opened to `0.0.0.0/0`).
- Query historical activity with Athena over the S3 logs, or CloudTrail Lake, for
  incident investigation without standing up custom infrastructure.
- Reconcile CloudTrail with [CloudWatch](14-cloudwatch.md): symptoms in metrics plus the
  causing API call in the trail gives a full timeline.
- Periodically test that you can actually retrieve and validate a log file — an untested
  audit trail is an assumption, not a control.

## AI Review Checklist

- Is a multi-region organization trail enabled and logging?
- Are logs delivered to a locked, encrypted bucket in a separate security account?
- Is log-file integrity validation turned on?
- Are data events enabled only for sensitive resources, not blanket account-wide?
- Are there alarms on `StopLogging`, `DeleteTrail`, root usage, and IAM/security changes?
- Is `StopLogging`/`DeleteTrail` restricted to a break-glass role?
- Does log retention meet the compliance requirement?

## Related

- `knowledge/aws/14-cloudwatch.md`
- `knowledge/aws/02-iam.md`
- `knowledge/aws/04-s3.md`
- `knowledge/aws/25-security.md`
- `knowledge/aws/16-secrets-manager.md`
