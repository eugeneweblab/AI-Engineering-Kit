---
id: aws/08-cloudfront
topic: aws
slug: cloudfront
title: "CloudFront"
type: doc
order: 8
status: ready
tags: [aws, cloudfront, us-east-1, CloudFront, no-store, GetObject, X-Content-Type-Options]
related: [aws/04-s3, aws/07-route53, aws/09-acm, aws/25-security, aws/26-monitoring]
when_to_use: "Read before putting a CDN in front of S3, an ALB, or an API — configuring origins, caching, TLS, or access control."
---
# CloudFront

## Purpose

This document defines how to run Amazon CloudFront as a CDN and TLS front door:
origins, origin access control, cache and origin-request policies, TLS/HTTPS behavior,
and security headers. It is written so an agent can put a distribution in front of S3 or
an ALB that is fast, cacheable, and closed to origin bypass — not one that serves stale
private data or leaves the bucket world-readable.

CloudFront is where correctness (which requests share a cached response) meets security
(who can reach the origin directly).

## Why It Matters

A misconfigured CDN causes silent, wide-blast-radius bugs. If the cache key omits a
header the origin varies on, **one user's response is served to everyone** — a cache
poisoning / data-leak incident. If it includes too much (cookies, query strings the
origin ignores), the hit rate collapses to zero and you pay origin cost for a CDN that
caches nothing. Separately, if S3 stays publicly readable "so CloudFront can reach it,"
anyone can bypass the CDN, your WAF, and your logging by hitting the bucket URL directly.
These failures are invisible in normal testing and only surface under real traffic.

## Core Principles

- **The cache key defines correctness.** Cache exactly the request attributes the origin
  actually varies its response on — no more, no less. Caching a personalized response
  without keying on the auth cookie leaks it to the next visitor.
- **Lock the origin to CloudFront only.** Use **Origin Access Control (OAC)** for S3 and
  keep the bucket private; use a secret header + WAF for custom/ALB origins. A public
  origin makes the CDN optional and the security posture a lie.
- **HTTPS end to end.** Redirect viewers to HTTPS and set the origin protocol policy to
  `https-only`. TLS at the edge but plaintext to the origin defeats the point.
- **Separate cache policy from origin-request policy.** What you *forward* to the origin
  (origin-request policy) is not the same as what you *key the cache on* (cache policy).
  Confusing them is the root of most caching bugs.
- **Static and dynamic paths need different behaviors.** Long TTLs and aggressive caching
  for assets; `no-store`/short TTL for authenticated or API paths.

## Best Practices

- Front private S3 with **OAC** (OAI is legacy) and a bucket policy that allows only the
  distribution's service principal. Keep **Block Public Access** on.
- Use AWS **managed policies**: `CachingOptimized` for static assets,
  `CachingDisabled` for dynamic/authenticated paths, `AllViewerExceptHostHeader` origin
  request policy for ALB origins.
- Set `viewer_protocol_policy = "redirect-to-https"` and a modern
  `minimum_protocol_version` (TLSv1.2_2021 or later).
- Attach **AWS WAF** and a **response-headers policy** (HSTS, `X-Content-Type-Options`,
  CSP) at the distribution.
- Serve TLS with an **ACM certificate in `us-east-1`** — CloudFront only reads certs
  from that region regardless of where your app runs.
- Send access logs to S3 and set alarms on 5xx rate and origin latency.

## Examples

**Good Example** — private S3 origin locked to CloudFront via OAC

```hcl
resource "aws_cloudfront_origin_access_control" "s3" {
  name                              = "s3-oac"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

# Bucket stays private; only THIS distribution's principal may read it.
data "aws_iam_policy_document" "bucket" {
  statement {
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.assets.arn}/*"]
    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.cdn.arn]
    }
  }
}
```

**Bad Example** — public bucket, HTTP allowed, cookies not in the cache key

```hcl
resource "aws_cloudfront_distribution" "cdn" {
  default_cache_behavior {
    viewer_protocol_policy = "allow-all"   # plaintext HTTP permitted at the edge
    # Personalized responses vary on the session cookie, but the cache key ignores it,
    # so one user's private page is served from cache to the next viewer.
    forwarded_values {
      cookies { forward = "none" }
      query_string = false
    }
  }
  # ...and the S3 bucket is left public, so anyone can bypass CloudFront + WAF entirely.
}
```

## Common Mistakes

- Leaving S3 public "so CloudFront can read it" instead of using OAC — the CDN, WAF, and
  logs become bypassable.
- Caching authenticated responses without keying on the auth cookie/header — cross-user
  data leak.
- Putting the ACM certificate in the app's region instead of `us-east-1`, so the custom
  domain silently falls back to the default `*.cloudfront.net` cert.
- Forwarding cookies/all query strings on static assets, driving the cache-hit rate to
  zero and paying full origin cost.
- Setting long TTLs on HTML/API responses, serving stale content after a deploy.
- `allow-all` viewer protocol policy, permitting downgrade to HTTP.

## Production Tips

- Invalidate paths on deploy (or use versioned asset filenames) so users get new builds;
  prefer content-hashed filenames over broad `/*` invalidations, which cost money.
- Use **CloudFront Functions** for cheap edge logic (redirects, header rewrites) and
  **Lambda@Edge** only when you need the heavier runtime.
- Watch the cache-hit ratio metric; a drop after a change usually means the cache key
  grew.
- Set an origin **custom error caching** TTL low so a transient origin 5xx is not pinned
  in the cache.

## AI Review Checklist

- Is the S3 origin private with OAC, and is Block Public Access still on?
- For custom/ALB origins, is direct origin access blocked (secret header + WAF)?
- Does the cache key include every attribute (cookie, header, query) the origin varies on?
- Is `redirect-to-https` set with `minimum_protocol_version` TLSv1.2_2021+?
- Is the ACM certificate in `us-east-1`?
- Are static assets versioned or invalidated on deploy, and dynamic paths uncached?

## Related

- `knowledge/aws/04-s3.md`
- `knowledge/aws/07-route53.md`
- `knowledge/aws/09-acm.md`
- `knowledge/aws/25-security.md`
- `knowledge/aws/26-monitoring.md`
