---
id: aws/20-ecr
topic: aws
slug: ecr
title: "ECR"
type: doc
order: 20
status: ready
tags: [aws, ecr, jsonencode, "@sha"]
related: [aws/18-ecs, aws/19-eks, aws/02-iam, aws/25-security, aws/15-cloudtrail]
when_to_use: "Read before creating an ECR repository, push/pull pipeline, or image policy."
---
# ECR

## Purpose

This document defines how to store and distribute container images with Amazon ECR
(Elastic Container Registry) correctly: repository configuration, tagging, scanning,
lifecycle policies, and access. It is written so an agent can set up a registry that
serves ECS/EKS reliably without shipping vulnerable images, losing track of what is
running, or paying for junk layers forever.

ECR is the supply-chain root for everything you deploy on [ECS](18-ecs.md) and
[EKS](19-eks.md). What lands here is what runs in production, so the registry's job is to
make the running version knowable, scanned, and immutable.

## Why It Matters

The registry is where deployment provenance lives or dies. If tags are mutable, `:latest`
can point at different bytes tomorrow than today, and rollback becomes guesswork. If
scanning is off, known CVEs sail straight into production. If lifecycle policies are
missing, orphaned images accumulate silently until storage cost balloons — or worse, a
`prod-v42` tag someone still deploys gets deleted by a careless cleanup. ECR sits at the
boundary between CI and runtime; a weak registry undermines every control downstream of
it.

## Core Principles

- **Tags must be immutable in production.** Enable `IMMUTABLE` tag mutability so a tag,
  once pushed, can never be overwritten. This makes the running version provably fixed
  and rollback deterministic.
- **Deploy by digest, treat tags as labels.** A `sha256:` digest is content-addressed and
  cannot lie about what runs; a tag is a human-friendly pointer. Pin runtime references to
  digests.
- **Scan on push, and act on findings.** Enhanced scanning (Amazon Inspector) surfaces
  OS and language CVEs continuously — but a scan you never read is theater.
- **Encrypt and lock down access.** Repositories are private by default; keep them that
  way, encrypt with KMS, and grant push/pull through least-privilege IAM.
- **Expire images automatically.** Lifecycle policies bound storage cost and blast radius
  by deleting untagged and stale images on a rule, not by hand.

## Best Practices

- Set repository **tag immutability to `IMMUTABLE`** so CI cannot overwrite an existing
  tag; a fixed tag then always means the same image.
- Enable **scan-on-push** (enhanced/Inspector scanning) and fail the pipeline on
  critical/high findings above your agreed threshold. The cost is occasional build
  friction; the payoff is CVEs stopped at the gate.
- Add a **lifecycle policy**: expire untagged images after a few days and cap the count of
  old tagged images. Keep enough history to roll back, no more.
- Encrypt repositories with a **customer-managed KMS key** when you need key rotation and
  audit control; the default AES-256 is fine for lower-sensitivity images.
- Grant access with **IAM policies and repository policies** scoped to specific
  repositories and actions (`ecr:GetDownloadUrlForLayer`, `ecr:BatchGetImage` for pull;
  push separately). Never grant `ecr:*` broadly.
- Use **pull-through cache** rules for upstream public images (Docker Hub, Quay) so builds
  do not depend on—or get rate-limited by—external registries.
- Sign images and verify signatures at deploy time when you need supply-chain integrity.
- Reference images by digest in task definitions and manifests; use tags for humans and CI
  bookkeeping.

## Examples

**Good Example** — immutable tags, scan-on-push, lifecycle cleanup (Terraform)

```hcl
resource "aws_ecr_repository" "orders" {
  name                 = "orders"
  image_tag_mutability = "IMMUTABLE"                 # a pushed tag can never be overwritten
  image_scanning_configuration { scan_on_push = true } # CVEs caught at the gate
  encryption_configuration {
    encryption_type = "KMS"
    kms_key         = aws_kms_key.ecr.arn
  }
}

resource "aws_ecr_lifecycle_policy" "orders" {
  repository = aws_ecr_repository.orders.name
  policy = jsonencode({ rules = [{
    rulePriority = 1
    description  = "Expire untagged images after 7 days"   # bounds storage + blast radius
    selection    = { tagStatus = "untagged", countType = "sinceImagePushed", countUnit = "days", countNumber = 7 }
    action       = { type = "expire" }
  }] })
}
```

```bash
# Deploy by digest, not tag — the running bytes are then provable and rollback is exact.
IMAGE=111122223333.dkr.ecr.eu-west-1.amazonaws.com/orders@sha256:9c4f...
```

**Bad Example** — mutable `:latest`, no scanning, no cleanup

```hcl
resource "aws_ecr_repository" "orders" {
  name                 = "orders"
  image_tag_mutability = "MUTABLE"   # CI can silently overwrite :latest -> unknowable version
  # scan_on_push omitted            -> vulnerable images ship undetected
  # no lifecycle policy             -> storage grows forever, cost creeps
}
# Deploying `orders:latest` means "whatever was pushed last" — no reliable rollback.
```

## Common Mistakes

- Leaving tag mutability `MUTABLE`, so `:latest` (or any tag) points at different bytes
  over time and rollback is unreliable.
- Deploying by tag instead of digest, so what runs is not provable.
- Skipping scan-on-push, letting known CVEs reach production unnoticed.
- No lifecycle policy, so untagged layers pile up and storage cost quietly rises.
- Over-broad `ecr:*` grants that let any principal push over production images.
- Depending on Docker Hub at build time and hitting rate limits instead of using
  pull-through cache.

## Production Tips

- Wire scan findings to EventBridge so a new critical CVE on an already-deployed image
  raises an alert, not just a dashboard entry.
- Replicate repositories to a second region if your deployment targets multiple regions;
  cross-region pulls add latency and a cross-region dependency.
- Record push/pull activity via CloudTrail data events to audit who shipped what.
- Keep a documented retention floor (e.g. last 10 tagged images) so cleanup never deletes
  an image you might roll back to.

## AI Review Checklist

- Is tag mutability set to `IMMUTABLE` for production repositories?
- Do deployments reference images by digest, not a mutable tag?
- Is scan-on-push enabled, and does the pipeline act on critical findings?
- Is there a lifecycle policy expiring untagged and stale images?
- Are push and pull permissions least-privilege, scoped per repository?
- Is the repository encrypted (KMS where key control is required)?
- Are upstream public images pulled through a cache, not directly?

## Related

- `knowledge/aws/18-ecs.md`
- `knowledge/aws/19-eks.md`
- `knowledge/aws/02-iam.md`
- `knowledge/aws/25-security.md`
- `knowledge/aws/15-cloudtrail.md`
