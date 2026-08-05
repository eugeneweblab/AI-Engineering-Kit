---
id: cicd/23-monitoring
topic: cicd
slug: monitoring
title: "CI/CD Monitoring"
type: doc
order: 23
status: ready
tags: [cicd, monitoring, rate, version, GIT_SHA]
related: [cicd/10-deployment, cicd/12-canary-deployment, cicd/14-rollbacks, cicd/24-notifications]
when_to_use: "Read before wiring deployment health signals, DORA metrics, or post-deploy verification into a pipeline."
---
# CI/CD Monitoring

## Purpose

This document defines how to close the loop between the pipeline and production: how a
deploy proves it is healthy, which signals gate and roll back a release, and which delivery
metrics tell you whether the pipeline itself is healthy. It covers post-deploy verification,
SLO-based release gates, the four DORA metrics, and deployment markers — enough for an agent
to make a pipeline that *knows* whether the change it shipped is working.

Monitoring here means two things: monitoring the *release* (is this deploy healthy?) and
monitoring the *pipeline* (is delivery itself healthy?). Both are required to ship safely.

## Why It Matters

A deploy that reports "success" the moment `kubectl apply` returns has verified nothing —
it confirms the API accepted the manifest, not that users can log in. Most bad releases pass
that check and then fail in production, undetected until a customer complains. Wiring real
signals into the pipeline turns "we deployed" into "we deployed and it works," and lets the
pipeline itself trigger a [rollback](14-rollbacks.md) before humans are paged. Measuring
delivery (DORA) is the same discipline pointed at the pipeline: you cannot improve lead time
or change-failure rate you do not measure.

## Core Principles

- **A deploy is not done until it is verified healthy.** Follow every deploy with a
  post-deploy check (smoke test + error-rate/latency query) before declaring success. The
  cost is a minute of pipeline time; the payoff is catching a bad release in seconds.
- **Gate on symptoms, roll back automatically.** Watch the signals users feel — error rate,
  latency, saturation — and let a breach auto-abort the rollout. A human-in-the-loop
  rollback is minutes too slow.
- **Emit a deployment marker.** Every deploy should annotate your observability system with
  the version and commit SHA, so a spike on the dashboard lines up with the release that
  caused it. Without markers, correlation is guesswork.
- **Measure the four DORA metrics.** Deployment frequency, lead time for changes, change
  failure rate, and mean time to restore are the standard, comparable measures of delivery
  health. Track them from real pipeline and incident data, not vibes.
- **Alerting belongs on SLOs, not on the pipeline log.** A green pipeline is not an SLA.
  Production health is judged by production signals.

## Best Practices

- Add a **post-deploy smoke test** stage that hits a real user path (login, checkout) and
  fails the pipeline if it does not pass.
- Query your metrics backend (Prometheus/Datadog/CloudWatch) for error rate and p99 latency
  over a short bake window after deploy; fail and roll back on an SLO breach.
- Use progressive delivery ([canary](12-canary-deployment.md)) with automated analysis
  (Argo Rollouts/Flagger) so a subset of traffic is judged before the full rollout.
- Emit a **deployment event/marker** with `version`, `commit_sha`, and `actor` to Grafana,
  Datadog, or Sentry from the deploy job.
- Compute DORA metrics from pipeline and incident data (deploy timestamps, `git` lead time,
  rollback/incident counts) and review them per team, not per individual.
- Route alerts by severity to the right channel and page only on user-facing SLO breaches —
  see [notifications](24-notifications.md); noisy alerts get muted and then miss the real one.
- Verify observability early: assert in CI that new services expose `/metrics` and health
  endpoints, so nothing ships blind.

## Examples

**Good Example** — deploy, then verify against real signals and auto-roll-back

```bash
# Deploy step emits a marker, then GATES on production error rate before success
deploy_and_verify() {
  ./deploy.sh
  # 1. Annotate the dashboard so any spike is tied to this exact release
  curl -s -X POST "$GRAFANA/api/annotations" \
    -d "{\"text\":\"deploy $GIT_SHA\",\"tags\":[\"deploy\"]}"

  # 2. Bake: query the 5xx rate over a short window from Prometheus
  sleep 60
  rate=$(promtool query instant "$PROM" \
    'sum(rate(http_requests_total{status=~"5.."}[2m])) / sum(rate(http_requests_total[2m]))' \
    | awk '{print $2}')

  # 3. Symptom-based gate: breach → automatic rollback, not a page
  if (( $(echo "$rate > 0.02" | bc -l) )); then
    echo "error rate ${rate} > 2% SLO — rolling back"
    kubectl rollout undo deployment/myapp
    exit 1
  fi
}
```

**Bad Example** — declares success on apply, no verification, no marker

```bash
kubectl apply -f deployment.yaml
echo "Deploy successful"   # verifies only that the API accepted the manifest
# No smoke test, no error-rate query, no bake window → a broken release looks green.
# No deployment marker → when the graph spikes, nobody can tie it to this deploy.
```

## Common Mistakes

- Treating `kubectl apply` / `deploy.sh` exit 0 as "healthy" without any production check.
- No bake window or smoke test, so a crash-looping release passes the pipeline.
- Alerting on pipeline failures but not on user-facing SLOs — the app can be down while CI is green.
- No deployment markers, making it impossible to correlate a metric spike with a release.
- Manual rollback only, so recovery time (MTTR) is measured in the minutes it takes to notice.
- Vanity metrics (build count, line coverage) instead of the four DORA metrics.
- Shipping a service with no `/metrics` or health endpoint, i.e. deploying blind.

## Production Tips

- Define **SLOs and error budgets** and let budget burn gate releases; when the budget is
  spent, the pipeline should slow or freeze risky deploys.
- Track **MTTR** explicitly — it is the metric a good pipeline improves most, via fast
  detection (post-deploy checks) plus fast [rollback](14-rollbacks.md).
- Keep dashboards and alert rules **as code** in the repo so they are versioned and reviewed
  like the pipeline itself.
- Run synthetic checks continuously (not only at deploy) so degradation between deploys is
  still caught.

## AI Review Checklist

- Does the deploy job verify health (smoke test + metrics query) before reporting success?
- Is there a bake window with an automatic rollback on an SLO breach?
- Does each deploy emit a version/commit marker to the observability system?
- Are alerts based on user-facing SLOs, not just pipeline success/failure?
- Are the four DORA metrics tracked from real pipeline/incident data?
- Do new services expose `/metrics` and health endpoints, checked in CI?
- Are dashboards and alert rules stored as code alongside the pipeline?

## Related

- `knowledge/cicd/10-deployment.md`
- `knowledge/cicd/12-canary-deployment.md`
- `knowledge/cicd/14-rollbacks.md`
- `knowledge/cicd/24-notifications.md`
