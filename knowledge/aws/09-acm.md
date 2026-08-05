---
id: aws/09-acm
topic: aws
slug: acm
title: "ACM"
type: doc
order: 9
status: ready
tags: [aws, acm, us-east-1, CloudFront]
related: [aws/07-route53, aws/08-cloudfront, aws/10-elastic-load-balancer, aws/25-security]
when_to_use: "Read before requesting, validating, or attaching a TLS certificate to CloudFront, an ALB, or API Gateway."
---
# ACM

## Purpose

This document defines how to issue and manage TLS certificates with AWS Certificate
Manager (ACM): requesting a cert, DNS validation, region rules, auto-renewal, and where
certs can and cannot be attached. It is written so an agent can put valid, auto-renewing
HTTPS on a service without hitting the region trap or shipping a cert that silently fails
to renew and expires in the middle of the night.

TLS is not optional. ACM makes public certificates free and auto-renewing — the failure
mode is almost always configuration, not the certificate itself.

## Why It Matters

Certificate mistakes produce two classic outages. First, the **region trap**:
CloudFront reads certificates only from `us-east-1`, so a cert issued in your app's
region cannot attach and the distribution serves the wrong name — a browser-blocking
error. Second, **failed auto-renewal**: ACM renews DNS-validated certs automatically
*only while the validation `CNAME` still exists*; delete that record and renewal fails
silently, then the cert expires and every client sees a security warning at once. Both
are invisible until they bite, and an expired cert takes down the whole endpoint, not
one user. That total, delayed blast radius is why cert setup deserves review.

## Core Principles

- **Use DNS validation, not email.** DNS validation renews automatically forever as long
  as the `CNAME` stays in the zone; email validation requires a human every renewal and
  breaks unattended infrastructure.
- **Region matters and differs by service.** CloudFront + certs live in `us-east-1`.
  ALB, NLB, and API Gateway (regional) use a cert in **their own region**. Issue the cert
  where the consuming service reads it.
- **Never delete the validation `CNAME`.** It is what proves ongoing control and what
  auto-renewal depends on. Manage it in the same IaC as the cert so it cannot drift.
- **ACM public certs cannot be exported.** You cannot put an ACM public cert on an EC2
  instance or on-prem box directly — it only attaches to integrated AWS services. Use
  ACM Private CA or import a cert for those cases.
- **Prefer `EXAMPLE.com` + `*.example.com` on one cert** so subdomains are covered
  without a new cert per host.

## Best Practices

- Request certs with **DNS validation** and create the validation record via IaC
  (`aws_acm_certificate_validation` gates dependent resources until issued).
- For CloudFront, declare the ACM provider/alias in `us-east-1` explicitly, separate from
  the region hosting the rest of the stack.
- Attach certs to **ALB/NLB listeners, CloudFront, and API Gateway** — the integrated
  services that handle renewal transparently.
- Monitor the **`DaysToExpiry` CloudWatch metric** and ACM/EventBridge renewal events;
  auto-renewal usually works, but alert so a rare failure is caught before expiry.
- Cover apex and wildcard subject alternative names on a single certificate to reduce
  moving parts.

## Examples

**Good Example** — DNS-validated cert wired to its Route 53 record

```hcl
resource "aws_acm_certificate" "app" {
  domain_name               = "example.com"
  subject_alternative_names = ["*.example.com"]
  validation_method         = "DNS" # renews automatically while the CNAME exists
}

# Create the validation CNAME in Route 53 and keep it under IaC so it never gets deleted.
resource "aws_route53_record" "validation" {
  for_each = {
    for o in aws_acm_certificate.app.domain_validation_options : o.domain_name => o
  }
  zone_id = aws_route53_zone.main.zone_id
  name    = each.value.resource_record_name
  type    = each.value.resource_record_type
  records = [each.value.resource_record_value]
  ttl     = 60
}

# Downstream resources depend on THIS so they never attach a not-yet-issued cert.
resource "aws_acm_certificate_validation" "app" {
  certificate_arn         = aws_acm_certificate.app.arn
  validation_record_fqdns = [for r in aws_route53_record.validation : r.fqdn]
}
```

**Bad Example** — email validation, cert issued in the wrong region for CloudFront

```hcl
resource "aws_acm_certificate" "app" {
  provider          = aws.eu_west_1 # CloudFront only reads certs from us-east-1 — won't attach
  domain_name       = "example.com"
  validation_method = "EMAIL"       # needs a human to click a link at every renewal → silent expiry
}
```

## Common Mistakes

- Issuing a CloudFront cert outside `us-east-1`, so it cannot attach and the distribution
  serves the default cert for the wrong hostname.
- Using email validation on unattended infra, guaranteeing a missed renewal eventually.
- Deleting the validation `CNAME` after issuance, silently killing auto-renewal.
- Trying to install an ACM public cert on an EC2 instance — public ACM certs are not
  exportable.
- Assuming renewal "just works" and never alarming on `DaysToExpiry`, so a rare failure
  becomes a hard outage.
- Requesting a new cert per subdomain instead of using a wildcard SAN.

## Production Tips

- Gate every listener/distribution on `aws_acm_certificate_validation` so deploys fail
  fast instead of half-attaching an unissued cert.
- Keep certs in the same Terraform state as the DNS zone; cross-account or cross-repo
  splits are where validation records get orphaned.
- For private/internal TLS or workloads that need the private key, use **ACM Private CA**
  or import a cert — do not fight the public-cert export restriction.

## AI Review Checklist

- Is the certificate DNS-validated (not email)?
- For CloudFront, is the cert issued in `us-east-1`? For ALB/API Gateway, in that
  service's region?
- Is the validation `CNAME` managed in IaC so it cannot be deleted?
- Do dependent listeners/distributions wait on validation before attaching?
- Is there an alarm on `DaysToExpiry` in case auto-renewal fails?
- Does the cert cover apex plus wildcard so subdomains are handled?

## Related

- `knowledge/aws/07-route53.md`
- `knowledge/aws/08-cloudfront.md`
- `knowledge/aws/10-elastic-load-balancer.md`
- `knowledge/aws/25-security.md`
