---
id: nginx/28-tooling
topic: nginx
slug: tooling
title: "Nginx Tooling"
type: doc
order: 28
status: ready
tags: [nginx, tooling]
related: [nginx/24-debugging, nginx/13-security, nginx/17-monitoring, nginx/26-best-practices, nginx/23-docker]
when_to_use: "Read before choosing how to validate, lint, test, or observe an nginx config, or when setting up CI for nginx changes."
---
# Nginx Tooling

## Purpose

This document maps the tools that make nginx work safe and repeatable: the built-in
validators (`nginx -t`, `nginx -T`), config linters and formatters, security scanners,
metrics exporters, and how to wire them into CI so a bad config cannot reach
production. It tells an agent which tool answers which question, and how to combine
them into a gate.

The tools here support the practices in [best practices](26-best-practices.md) and the
diagnosis loop in [debugging](24-debugging.md); this document is the toolbox, they are
the technique.

## Why It Matters

nginx has no type system and no runtime error for a semantically wrong-but-valid
config: `nginx -t` passing means the syntax parses, not that the config does what you
meant. Most nginx incidents are self-inflicted config mistakes that a linter or a
merged-config review would have caught. Standardizing on a small set of tools — a
validator in CI, a security scanner, a metrics exporter — converts "we hope this
config is right" into "the pipeline proved it is at least not obviously wrong."

## Core Principles

- **Validate mechanically, every time.** `nginx -t` in CI and in the deploy script is
  non-negotiable; humans forget, pipelines do not.
- **Review the merged config, not the fragments.** `nginx -T` expands all includes and
  shows inherited/overridden directives — that is what actually runs.
- **Lint for the mistakes syntax can't catch.** A security linter finds SSRF-prone
  `proxy_pass`, missing headers, and weak TLS that `-t` happily accepts.
- **Prefer the smallest tool that answers the question.** Reach for `curl` and `nginx -T`
  before standing up a full test harness.
- **Make observability a tool, not an afterthought.** An exporter and dashboards are
  part of the toolchain, not a separate project.

## Best Practices

- Gate every config change in CI on `nginx -t` against the real config, ideally inside
  the same image that runs in production (`docker run --rm nginx:1.27 nginx -t -c ...`),
  so version-specific directives are validated against the right binary.
- Run `gixy` (open-source nginx security linter) in CI to catch SSRF via unvalidated
  `proxy_pass`, `add_header` inheritance loss, referrer/host spoofing, and origin issues
  that `nginx -t` cannot see.
- Format consistently with `nginxfmt` (or `nginxbeautifier`) so diffs show real changes,
  not whitespace churn.
- Expose metrics with the `nginx-prometheus-exporter` (scrapes `stub_status`) or nginx
  Plus's richer API, and ship them to Prometheus/Grafana — see [monitoring](17-monitoring.md).
- Use `curl -v`, `--resolve`, and `openssl s_client -connect host:443` as the first-line
  tools for reproducing and inspecting requests and TLS.
- For request-level tracing under load, use `wrk`/`k6` to load-test the config and
  `ngxtop` or the access log to see live request distribution.
- Keep the toolchain versions pinned (in CI config and Dockerfiles) so a tool upgrade
  cannot silently change what passes.

## Examples

**Good Example** — a CI gate that validates, lints, and checks the merged config

```bash
#!/usr/bin/env bash
set -euo pipefail

IMAGE="nginx:1.27"   # pin to the version that runs in prod

# 1. Syntax + directive validation against the real binary
docker run --rm -v "$PWD/nginx:/etc/nginx:ro" "$IMAGE" nginx -t

# 2. Dump the fully-merged config so reviewers see inheritance/overrides
docker run --rm -v "$PWD/nginx:/etc/nginx:ro" "$IMAGE" nginx -T > merged.conf

# 3. Security lint: SSRF, missing headers, weak TLS — things `nginx -t` ignores
gixy nginx/nginx.conf

echo "nginx config validated, merged, and security-scanned"
```

**Bad Example** — "it works on my machine" with no mechanical check

```bash
# Edit nginx.conf by hand on the server, then:
sudo systemctl restart nginx   # restart (drops connections) and no `nginx -t` first
# If the config is broken, nginx fails to start → full outage, discovered by users.
# No linter, so an SSRF-prone `proxy_pass $http_x_target;` ships unnoticed.
```

## Common Mistakes

- Relying on `nginx -t` alone and assuming "syntax valid" means "behaves correctly."
- Reviewing config fragments instead of the `nginx -T` merged output, missing inheritance
  and override effects.
- Skipping a security linter, so SSRF-prone or header-dropping config reaches production.
- Validating against a different nginx version than production runs, so version-specific
  directives fail only at deploy.
- `restart` in the deploy script — a broken config takes the site down instead of
  aborting the rollout (use `nginx -t && nginx -s reload`).
- Treating metrics/exporters as optional, leaving the running config unobservable.

## Production Tips

- Put the validate-lint-merge steps in a pre-merge CI job *and* re-run `nginx -t` in the
  deploy step; the pipeline and the box can drift.
- Store the `nginx -T` output as a deploy artifact so you have an exact record of what
  each release actually ran.
- Run `gixy` and `nginx -t` inside the production container image in CI so what you test
  is byte-for-byte what you ship (see [Docker](23-docker.md)).

## AI Review Checklist

- Does CI run `nginx -t` against the same nginx version that runs in production?
- Is the merged config (`nginx -T`) reviewed, not just the fragments?
- Is a security linter (`gixy`) run to catch SSRF, header, and TLS issues?
- Is the config formatted consistently so diffs are meaningful?
- Are metrics exported (`stub_status`/exporter) and dashboarded?
- Does the deploy use `nginx -t && reload`, never a blind `restart`?
- Are tool and image versions pinned so results are reproducible?

## Related

- `knowledge/nginx/24-debugging.md`
- `knowledge/nginx/13-security.md`
- `knowledge/nginx/17-monitoring.md`
- `knowledge/nginx/26-best-practices.md`
- `knowledge/nginx/23-docker.md`
