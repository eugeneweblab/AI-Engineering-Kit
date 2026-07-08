---
id: aws/26-monitoring
topic: aws
slug: monitoring
title: "Monitoring"
type: doc
order: 26
status: ready
tags: [aws, monitoring]
related: [aws/14-cloudwatch, aws/15-cloudtrail, aws/23-eventbridge, aws/27-production, aws/29-well-architected-framework]
when_to_use: "Read before shipping a workload to production, defining alarms, or diagnosing an incident where you cannot tell what the system is doing."
---
# Monitoring

## Purpose

This document defines how to make an AWS workload observable: metrics, logs, traces,
alarms, and dashboards that let you answer "is it healthy?" and "why did it break?"
quickly. It is written so an agent can instrument a system and set alarms that page a
human on real problems without drowning them in noise.

Monitoring spans the three telemetry signals — **metrics** (numbers over time), **logs**
(discrete events), and **traces** (a request's path across services) — plus the alarms
and dashboards built on top. On AWS these are CloudWatch, CloudWatch Logs, and X-Ray,
tied together by EventBridge. This is the observability face of the operational-excellence
and reliability pillars of the [Well-Architected Framework](29-well-architected-framework.md).

## Why It Matters

A system you cannot observe is a system you cannot operate. Without instrumentation, the
first sign of failure is an angry customer, and diagnosis is guesswork over a system you
have no visibility into. But the opposite failure is just as costly: hundreds of alarms
on raw resource metrics that page at 3 a.m. for a CPU blip nobody cares about. Teams that
get paged for non-problems learn to ignore the pager, and then miss the real outage.
Effective monitoring is deliberate: measure what users feel, alarm on symptoms, and make
every page actionable.

## Core Principles

- **Alarm on symptoms, not causes.** Page on what the user experiences — elevated error
  rate, high latency, a failing health check — not on every underlying metric. One bad
  deploy should page once, not fifty times.
- **The four golden signals.** For any service, watch **latency, traffic, errors, and
  saturation**. They catch the vast majority of user-visible problems.
- **Emit structured logs, then query them.** Log JSON with correlation IDs so
  CloudWatch Logs Insights can slice by request, tenant, or error type.
- **Every alarm has an owner and a runbook.** An alarm that no one knows how to act on is
  noise. If a page has no defined response, it should be a dashboard, not an alarm.
- **Instrument before you need it.** You cannot add observability during an incident. Bake
  metrics, tracing, and log correlation into the service from the start.

## Best Practices

- Define **SLIs/SLOs** (e.g., 99.9% of requests under 300 ms) and alarm when the error
  budget burns fast. This ties paging to user impact, not to raw infrastructure noise.
- Use **CloudWatch alarms** with sensible evaluation periods and `M-of-N` datapoints so a
  single transient spike does not page; treat missing data explicitly (`notBreaching` vs
  `breaching`) based on what "no data" means for that metric.
- Publish **custom business/application metrics** via Embedded Metric Format (EMF) —
  request counts, queue depth, checkout success rate — not just CPU and memory.
- Set **log retention** on every group, log **structured JSON**, and add a correlation/
  request ID to every line so you can trace one request end-to-end.
- Enable **X-Ray** (or OpenTelemetry via the ADOT collector) on distributed workloads to
  find which hop in a call chain is slow or failing.
- Route alarms through **SNS → PagerDuty/Slack** and drive automated remediation with
  **EventBridge** (e.g., an alarm triggers a Lambda that recycles a task).
- Build **dashboards per service** that show the golden signals at a glance, plus
  deploy markers so you can correlate a regression with the release that caused it.

## Examples

**Good Example** — symptom alarm on a user-facing SLI, resilient to transient blips

```hcl
# Pages when the 5xx RATE is sustained — a symptom users feel — not on a one-off spike.
resource "aws_cloudwatch_metric_alarm" "api_5xx_rate" {
  alarm_name          = "api-5xx-rate-high"
  comparison_operator = "GreaterThanThreshold"
  threshold           = 5          # percent of requests failing
  evaluation_periods  = 5
  datapoints_to_alarm = 3          # 3-of-5: rides out a single transient blip
  treat_missing_data  = "notBreaching"  # no traffic != an outage for this metric

  metric_query {
    id          = "error_rate"
    expression  = "100 * (errors / requests)"  # a rate, not a raw count
    return_data = true
  }
  metric_query { id = "errors"   metric { metric_name = "5XXError" namespace = "AWS/ApplicationELB" period = 60 stat = "Sum" } }
  metric_query { id = "requests" metric { metric_name = "RequestCount" namespace = "AWS/ApplicationELB" period = 60 stat = "Sum" } }

  alarm_actions = [aws_sns_topic.pager.arn]  # goes to a human with a runbook
}
```

**Bad Example** — noisy cause-based alarm on a raw metric

```hcl
resource "aws_cloudwatch_metric_alarm" "cpu" {
  alarm_name          = "cpu-high"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  threshold           = 80
  evaluation_periods  = 1          # one 60s blip pages — pure noise
  comparison_operator = "GreaterThanThreshold"
  # High CPU is not a problem if latency and errors are fine; this pages on a cause
  # that users never feel, and one deploy across 30 instances pages 30 times.
  alarm_actions = [aws_sns_topic.pager.arn]
}
# No log retention, no structured logs, no tracing: when it does break, you are blind.
```

## Common Mistakes

- Alarming on every raw resource metric (CPU, memory) instead of user-facing symptoms.
- `evaluation_periods = 1`, so transient spikes page and everyone learns to ignore the pager.
- Ignoring `treat_missing_data`, so a scaled-to-zero service pages or silently hides outages.
- Unstructured logs with no correlation ID — impossible to trace one request across services.
- No SLOs, so there is no principled threshold for "how bad is bad enough to page?"
- Dashboards full of vanity metrics but missing latency/error/saturation for each service.
- Alarms with no runbook and no owner.

## Production Tips

- Add **deploy annotations** to dashboards so regressions line up with the release that
  caused them.
- Use **composite alarms** to suppress downstream pages when an upstream dependency is
  already alarming — one root-cause page, not a storm.
- Run periodic **synthetic canaries** (CloudWatch Synthetics) against critical user
  journeys so you detect breakage before real users do.
- Review alarm quality after every incident: did it page too late, too early, or not at all?

## AI Review Checklist

- Does every service expose latency, traffic, errors, and saturation?
- Do alarms fire on user-facing symptoms, with `M-of-N` datapoints and explicit missing-data handling?
- Are logs structured JSON with a correlation ID and a finite retention?
- Is distributed tracing (X-Ray/OTel) enabled on multi-service call paths?
- Does every alarm route to an owner and map to a runbook?
- Are there SLIs/SLOs defining what "healthy" means, not just raw thresholds?

## Related

- `knowledge/aws/14-cloudwatch.md`
- `knowledge/aws/15-cloudtrail.md`
- `knowledge/aws/23-eventbridge.md`
- `knowledge/aws/27-production.md`
- `knowledge/aws/29-well-architected-framework.md`
