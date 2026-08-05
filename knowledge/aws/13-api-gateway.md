---
id: aws/13-api-gateway
topic: aws
slug: api-gateway
title: "API Gateway"
type: doc
order: 13
status: ready
tags: [aws, api-gateway, prod, Throttle, GetAtt]
related: [aws/12-lambda, aws/02-iam, aws/14-cloudwatch, aws/09-acm, aws/25-security]
when_to_use: "Read before exposing any HTTP or WebSocket API through Amazon API Gateway."
---
# API Gateway

## Purpose

This document defines how to expose services through Amazon API Gateway so the edge is
authenticated, throttled, observable, and cheap. It covers HTTP vs REST API choice,
authorizers, throttling, request validation, and stage configuration so an agent can
publish an endpoint without leaving it open, unmetered, or unmonitored.

API Gateway is the front door to your backend. It terminates TLS, authenticates callers,
enforces quotas, and routes to Lambda, HTTP backends, or AWS services. Everything it does
not enforce, your backend must — so misconfiguring it pushes load and attack surface
straight through to code that assumed it was protected.

## Why It Matters

The gateway is where a public request first meets your system, so it is where cost and
abuse are cheapest to stop. An endpoint with no throttling can be turned into a bill or a
denial-of-service against your own Lambda. An authorizer that fails open lets anonymous
callers reach private data. Because the gateway sits in front of everything, one
misconfigured stage or route exposes every backend behind it at once.

## Core Principles

- **Authenticate at the edge, authorize in the backend.** Use an authorizer (JWT/OIDC,
  Cognito, or IAM) to reject unauthenticated calls before they cost you compute; enforce
  fine-grained permissions in the service.
- **Every route is throttled.** Set account, stage, and per-route rate and burst limits.
  An unthrottled route is an open cost and abuse channel.
- **Validate at the boundary.** Reject malformed requests at the gateway with a request
  schema so invalid input never reaches (or bills) the backend.
- **Pick the right API type for the job.** HTTP APIs are cheaper and lower-latency for
  most REST workloads; REST APIs exist for features HTTP APIs lack (API keys with usage
  plans, request/response transformation, WAF, private endpoints, fine-grained caching).
- **Fail closed on authorization.** If the authorizer errors, deny. Cache authorizer
  results briefly to cut latency, but never let a cache miss become an allow.

## Best Practices

- Put an authorizer on every non-public route. Prefer a JWT authorizer validating an
  OIDC token; use IAM auth for service-to-service calls.
- Configure default and per-route **throttling** and, for REST APIs, usage plans + API
  keys to meter and cap per-client traffic.
- Enable **request validation** (body against a JSON Schema, required params/headers) so
  the backend receives only well-formed input.
- Serve behind a custom domain with an [ACM](09-acm.md) certificate; enforce TLS 1.2+.
- Turn on **access logging** and execution metrics to [CloudWatch](14-cloudwatch.md);
  log request id, route, status, latency, and caller — never the request body if it holds
  secrets.
- For public REST APIs, attach **AWS WAF** for rate-based rules and common exploit
  protection.
- Use stages (`dev`, `prod`) with stage variables; never edit a live stage by hand —
  deploy through infrastructure-as-code.

## Examples

**Good Example** — JWT authorizer + explicit throttle (AWS SAM / OpenAPI)

```yaml
# HTTP API: authenticate every route, cap throughput at the edge.
MyApi:
  Type: AWS::Serverless::HttpApi
  Properties:
    Auth:
      DefaultAuthorizer: OidcJwt          # every route requires a valid token by default
      Authorizers:
        OidcJwt:
          IdentitySource: "$request.header.Authorization"
          JwtConfiguration:
            issuer: https://auth.example.com
            audience: [api://orders]        # reject tokens minted for other audiences
    RouteSettings:
      "POST /orders":
        ThrottlingRateLimit: 50            # steady-state cap protects the backend
        ThrottlingBurstLimit: 100          # short spike allowance
    AccessLogSettings:
      DestinationArn: !GetAtt ApiLogGroup.Arn
```

**Bad Example** — open route, no limits, no logs

```yaml
MyApi:
  Type: AWS::Serverless::HttpApi
  Properties:
    # No DefaultAuthorizer → every route is public.
    # No RouteSettings → no throttle: one client can drive unbounded Lambda cost.
    # No AccessLogSettings → no record of who called what when an incident happens.
    Description: "orders api"
```

## Common Mistakes

- Leaving routes public because "the Lambda checks auth" — the call still costs you and
  reaches your code before any check.
- No throttling or usage plan, turning a public endpoint into an unmetered cost sink.
- Authorizer configured to fail open, or with a long cache TTL that keeps allowing a
  revoked token.
- Not validating the audience/issuer on JWTs, accepting tokens minted for another service.
- Editing a live stage manually so `dev` and `prod` silently diverge.
- No access logging, leaving no forensic trail when abuse or an outage occurs.

## Production Tips

- Alarm on `4XXError`, `5XXError`, `Latency` p99, and `Throttle` counts per stage.
- Enable caching (REST API) for idempotent GETs to cut backend load and cost — but set a
  short TTL and never cache authenticated, user-specific responses without a cache key.
- Use a canary deployment on the stage to shift a small percentage of traffic to a new
  version before full rollout.
- Keep payloads small; API Gateway has a hard request/response size limit, so stream
  large objects via [S3](04-s3.md) presigned URLs instead of proxying them.

## AI Review Checklist

- Does every non-public route have an authorizer that fails closed?
- Are JWT issuer and audience validated?
- Is throttling (and a usage plan for REST) set at stage and route level?
- Is request validation enabled so malformed input is rejected at the edge?
- Is the API behind a custom domain with an ACM cert and TLS 1.2+?
- Is access logging to CloudWatch enabled, without logging secret bodies?
- Are stages managed through IaC rather than hand-edited?

## Related

- `knowledge/aws/12-lambda.md`
- `knowledge/aws/02-iam.md`
- `knowledge/aws/14-cloudwatch.md`
- `knowledge/aws/09-acm.md`
- `knowledge/aws/25-security.md`
