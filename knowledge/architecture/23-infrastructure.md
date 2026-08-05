---
id: architecture/23-infrastructure
topic: architecture
slug: infrastructure
title: "Infrastructure"
type: doc
order: 23
status: ready
tags: [architecture, infrastructure, plan, apply, DB_PASSWORD]
related: [architecture/22-cloud-architecture, architecture/24-deployment, architecture/16-high-availability, architecture/18-observability, architecture/15-security]
when_to_use: "Read before provisioning environments, writing infrastructure-as-code, or when environments drift or cannot be reproduced."
---
# Infrastructure

## Purpose

This document defines how to provision and manage the compute, network, and storage a system
runs on: infrastructure as code, environment parity, secrets, and change management. It is
written so an agent can create or modify infrastructure that is reproducible, reviewable, and
recoverable rather than a hand-tuned artifact no one can rebuild.

Infrastructure is code that happens to provision machines instead of computing values. It
deserves the same rigor: version control, review, testing, and repeatable builds. The goal is
that any environment can be recreated from source in one command, and that no critical state
lives only in a running server's memory or a console someone clicked.

## Why It Matters

Infrastructure created by hand rots. Someone SSHes in to fix a bug, tweaks a config, and now
production differs from staging in a way no file records — a "snowflake" server. Six months
later it fails, and no one can rebuild it because the knowledge left with the person who typed
it. This is where the worst outages come from: not a code bug, but an environment nobody can
reproduce or reason about. Infrastructure as code turns servers into disposable, versioned
artifacts. The payoff is that disaster recovery, scaling, and onboarding all reduce to running
the same code again. The cost is discipline: no manual changes, ever.

## Core Principles

- **Everything is code, in version control.** Every server, network rule, and DNS record is
  declared in a file, reviewed in a pull request, and applied by automation — never by hand.
  If it is not in the repo, it does not exist.
- **Infrastructure is immutable.** Replace, do not patch. To change a server, build a new image
  and roll it out; never mutate a running one. Mutation causes drift; replacement guarantees a
  known state.
- **Environments must be at parity.** Dev, staging, and production are the same code with
  different variables. Divergence is how "works in staging" becomes a production incident.
- **State is precious and shared.** IaC state files (Terraform state) describe reality; store
  them remotely with locking so two applies cannot corrupt them.
- **Least privilege and no plaintext secrets.** Automation and services get scoped credentials;
  secrets live in a secrets manager and are injected at runtime, never committed.

## Best Practices

- Declare infrastructure with a mature IaC tool (Terraform, Pulumi, CDK). Keep modules small and
  composable, and pin provider and module versions so applies are reproducible.
- Store IaC state remotely (e.g. S3 + DynamoDB lock, Terraform Cloud) with locking and
  encryption. Never keep state on a laptop or commit it to git.
- Run `plan` in CI on every pull request and require the diff to be reviewed before `apply`. The
  plan is the change; a surprising plan is a caught incident.
- Bake immutable machine images (Packer/container images) and roll forward by replacing
  instances. Forbid interactive SSH changes to production; if you SSHed to fix it, it is drift.
- Keep environments identical by construction: one module, per-environment variable files. Diff
  environments in CI and fail on unexpected divergence.
- Manage secrets in a dedicated store (Vault, cloud secrets manager) with rotation; inject via
  environment or mounted files at deploy time. Scan the repo to block committed secrets.
- Make provisioning idempotent and re-runnable: applying the same code twice changes nothing.
  Non-idempotent scripts cannot be trusted in recovery.
- Test infrastructure: linting (tflint), policy-as-code (OPA/Sentinel) for guardrails, and a
  disposable staging apply/destroy in CI.

## Examples

**Good Example** — declarative, versioned, parameterized, remote state

```hcl
terraform {
  required_version = "~> 1.9"
  backend "s3" {                       # remote, locked, encrypted state -> safe for a team
    bucket = "acme-tfstate"
    key    = "app/terraform.tfstate"
    dynamodb_table = "tf-locks"        # lock prevents two concurrent applies corrupting state
  }
}

# Same module for every environment; only the variables differ -> guaranteed parity.
module "app" {
  source        = "./modules/service"
  environment   = var.environment      # "staging" | "production"
  instance_type = var.instance_type
  db_password   = data.aws_secretsmanager_secret_version.db.secret_string  # never hardcoded
}
```

**Bad Example** — manual, non-reproducible, secrets in code

```bash
# Provisioned by hand over SSH -> nothing records this; the box is a snowflake.
ssh prod-01
sudo apt-get install -y myapp=1.2.3          # version chosen live; staging has 1.2.1 -> drift
export DB_PASSWORD="s3cr3t-prod-pw"          # plaintext secret, now in shell history + memory
# no file describes this server; if it dies, no one can rebuild it
```

## Common Mistakes

- Making manual changes to running servers, creating drift no file records ("snowflake" servers).
- Committing IaC state or secrets to git, or keeping state on a single laptop.
- Letting environments diverge, so staging cannot predict production behavior.
- Mutating servers in place instead of replacing immutable images, accumulating hidden state.
- Applying infrastructure changes without a reviewed `plan`, so surprises reach production.
- Non-idempotent provisioning scripts that fail or double-apply on a re-run during recovery.
- Hardcoding credentials in Terraform, Dockerfiles, or CI config instead of a secrets manager.

## Production Tips

- Rehearse disaster recovery by rebuilding an environment from scratch on a schedule; if you have
  not rebuilt it, you do not know you can.
- Enforce guardrails as policy-as-code (deny public buckets, require encryption) so mistakes are
  blocked at plan time, not discovered in an audit.
- Detect drift continuously (scheduled `plan`) and alert; drift is silent until it causes an outage.
- Keep a break-glass procedure for emergency manual access that is logged and auto-reverted.

## AI Review Checklist

- Is every piece of infrastructure declared in version-controlled code, not created by hand?
- Is IaC state stored remotely with locking and encryption, never committed or on a laptop?
- Does every change go through a reviewed `plan` in CI before `apply`?
- Are servers immutable (replaced, not patched), with no interactive production changes?
- Are dev/staging/production the same modules with only variables differing?
- Are secrets in a managed store and injected at runtime, never committed?
- Is provisioning idempotent and re-runnable for disaster recovery?

## Related

- `knowledge/architecture/22-cloud-architecture.md`
- `knowledge/architecture/24-deployment.md`
- `knowledge/architecture/16-high-availability.md`
- `knowledge/architecture/18-observability.md`
- `knowledge/architecture/15-security.md`
