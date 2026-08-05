---
id: aws/14-cloudwatch
topic: aws
slug: cloudwatch
title: "CloudWatch"
type: doc
order: 14
status: ready
tags: [aws, cloudwatch, CloudWatch, dumps, symptom, emit, time, handle]
related: [aws/15-cloudtrail, aws/12-lambda, aws/26-monitoring, aws/13-api-gateway, aws/24-cost-optimization]
when_to_use: "Read before instrumenting logging, metrics, alarms, or dashboards for any AWS workload."
---
# CloudWatch

## Purpose

This document defines how to make an AWS workload observable with CloudWatch: structured
logs, meaningful metrics, actionable alarms, and controlled cost. It is written so an
agent can instrument a service such that operators find out about a problem from an alarm,
not from a customer.

CloudWatch is the operational eyes of AWS: logs, metrics, alarms, dashboards, and events.
It answers "is the system healthy, and if not, where does it hurt?" Instrumentation is not
optional polish — a service with no metrics or alarms is a service you operate blind.

## Why It Matters

You cannot fix what you cannot see. Without alarms, failures are discovered by users;
without structured logs, an incident becomes an archaeology dig; without metric filters,
you learn about an error spike hours late. CloudWatch also has a cost dimension that bites
silently: verbose logs, high-cardinality custom metrics, and short retention defaults can
quietly become one of the larger lines on an AWS bill. Getting observability right means
seeing problems early *and* not paying for noise.

## Core Principles

- **Log structured, not prose.** Emit JSON with stable keys (level, request id, event,
  duration). Structured logs are queryable in Logs Insights; free text is not.
- **Alarm on symptoms users feel.** Alert on error rate, latency, and saturation — not on
  every metric. An alarm that does not require action trains people to ignore alarms.
- **Every alarm has an owner and a runbook.** An alarm with no response is noise. If
  nobody acts on it, delete it or fix the threshold.
- **Set retention deliberately.** Log groups default to never-expire, which accrues cost
  forever. Choose a retention that matches compliance and debugging needs.
- **Metrics over log scraping for hot paths.** Emit custom metrics (or Embedded Metric
  Format) for numbers you alarm on; do not derive critical alarms from parsing log text
  at query time.

## Best Practices

- Send application logs as JSON to a log group with an explicit `retentionInDays`
  (e.g. 30 for app logs, longer for audit). Never leave retention at "never expire".
- Use **metric filters** or **Embedded Metric Format (EMF)** to turn log fields into
  metrics without a second write path.
- Create alarms with `TreatMissingData` set intentionally (usually `notBreaching` for
  sparse metrics, `breaching` for a heartbeat you require) — missing data is a decision,
  not a default.
- Use **composite alarms** to suppress alarm storms: page on one root-cause alarm, not on
  twenty correlated child alarms.
- Route alarm notifications to [SNS](22-sns.md) → a pager/on-call tool, not to an email
  nobody reads.
- Redact secrets and PII before logging. Logs are widely readable; a token in a log is a
  leaked token.
- Dashboard the golden signals (latency, traffic, errors, saturation) per service so an
  operator sees health at a glance.

## Examples

**Good Example** — structured log + EMF metric, retained and alarmable

```python
import json, time

def emit(event, duration_ms, ok):
    # Embedded Metric Format: one structured log line CloudWatch reads AS a metric.
    print(json.dumps({
        "_aws": {
            "Timestamp": int(time.time() * 1000),
            "CloudWatchMetrics": [{
                "Namespace": "Orders",
                "Dimensions": [["Service"]],
                "Metrics": [{"Name": "LatencyMs"}, {"Name": "Errors"}],
            }],
        },
        "Service": "checkout",
        "event": event,        # stable key → queryable in Logs Insights
        "LatencyMs": duration_ms,
        "Errors": 0 if ok else 1,
        # No card number, no token — secrets never reach the log.
    }))
```

```yaml
# Alarm on the symptom (error rate), with missing-data handled deliberately.
CheckoutErrors:
  Type: AWS::CloudWatch::Alarm
  Properties:
    Namespace: Orders
    MetricName: Errors
    Statistic: Sum
    Period: 60
    EvaluationPeriods: 5
    Threshold: 10
    ComparisonOperator: GreaterThanThreshold
    TreatMissingData: notBreaching   # no traffic ≠ failing
    AlarmActions: [!Ref PagerTopic]
```

**Bad Example** — prose logs, no retention, vanity alarm

```python
def handle(req):
    print(f"processing {req}")               # unstructured, not queryable, may log secrets
    # Log group left at default retention → grows and bills forever.
    # Alarm (elsewhere) fires on CPUUtilization > 5% → pages on nothing, gets muted.
```

## Common Mistakes

- Unstructured, free-text logs that cannot be searched or turned into metrics.
- Log groups left at never-expire retention, silently growing the bill.
- Logging secrets, tokens, or PII into a widely readable log group.
- Alarms on causes or vanity metrics instead of user-facing symptoms, so alerts get muted.
- `TreatMissingData` left at default, causing false alarms on sparse metrics or missed
  outages on a dead heartbeat.
- High-cardinality custom metrics (a dimension per user/request) exploding metric cost.

## Production Tips

- Use Logs Insights saved queries for common incident questions (top errors, slow
  requests) so responders are not writing queries under pressure.
- Add anomaly-detection alarms for metrics without a fixed sane threshold.
- Set a billing/anomaly alarm on CloudWatch spend itself; observability cost regressions
  are easy to miss.
- Pair CloudWatch with [CloudTrail](15-cloudtrail.md): CloudWatch tells you *what broke*,
  CloudTrail tells you *who changed what* just before it broke.

## AI Review Checklist

- Are application logs structured JSON with stable keys?
- Does every log group have an explicit, non-infinite retention?
- Are secrets and PII kept out of logs?
- Do alarms fire on user-facing symptoms, and does each have a notification target?
- Is `TreatMissingData` set intentionally per alarm?
- Are hot-path numbers emitted as metrics/EMF rather than scraped from text at query time?
- Is custom-metric cardinality bounded?

## Related

- `knowledge/aws/15-cloudtrail.md`
- `knowledge/aws/12-lambda.md`
- `knowledge/aws/26-monitoring.md`
- `knowledge/aws/13-api-gateway.md`
- `knowledge/aws/24-cost-optimization.md`
