---
id: devops/08-infrastructure-as-code
topic: devops
slug: infrastructure-as-code
title: "Infrastructure As Code"
type: doc
order: 8
status: ready
tags: [devops, infrastructure-as-code]
related: [devops/09-configuration-management, devops/17-secrets-management, devops/11-orchestration, devops/24-change-management, devops/18-disaster-recovery]
when_to_use: "Read before provisioning or modifying cloud infrastructure, or reviewing any Terraform/Pulumi/CloudFormation change."
---
# Infrastructure As Code

## Purpose

This document defines how to describe infrastructure — networks, compute, databases,
IAM — as version-controlled, reviewable code that a tool applies deterministically. It
is written so an agent can author or review IaC without creating drift, leaking secrets,
or making changes nobody can reproduce.

IaC is about **provisioning** the resources. Shaping what runs *on* them is
[configuration management](09-configuration-management.md); handing secrets to those
resources is [secrets management](17-secrets-management.md). Keep those concerns in
separate layers.

## Why It Matters

Infrastructure created by hand in a console is invisible, unrepeatable, and unowned:
nobody can review it, diff it, or recreate it after a region outage. IaC turns
infrastructure into an artifact you can code-review, test, and roll back like any other
code — and, crucially, rebuild from scratch in a disaster. The failure mode of *not*
using IaC is a "pet" environment that only one person understands and that cannot be
reproduced when it dies.

## Core Principles

- **Declarative over imperative.** Describe the desired end state and let the tool
  compute the diff. Imperative scripts ("create X, then Y") drift and are not idempotent.
- **The repository is the source of truth.** No out-of-band console changes. If it is not
  in code, it does not exist — and anything changed by hand becomes untracked drift.
- **Plan before apply.** Every change produces a reviewable diff of exactly what will be
  created, changed, or destroyed *before* it touches real infrastructure.
- **Idempotent and reproducible.** Applying the same code twice yields the same state.
  You must be able to destroy and recreate an environment from code alone.
- **State is precious and shared.** The state file maps code to real resources; corrupt
  or lose it and the tool no longer knows what it owns.

## Best Practices

- Store state in a **remote, locked, versioned backend** (e.g. S3 + DynamoDB lock, GCS,
  Terraform Cloud). Never commit state to git and never keep it only on a laptop —
  concurrent applies without a lock corrupt it.
- Run `plan` in CI on every PR and require the diff to be reviewed; run `apply` only from
  a protected pipeline, never from an engineer's machine with personal credentials.
- **Never hardcode secrets** in IaC. Reference a secrets manager or inject at apply time;
  remember that most secrets typed into IaC also land in *state* as plaintext.
- Modularize by reuse boundary and parameterize per environment (dev/staging/prod share
  modules, differ by variables). Avoid copy-pasted environment folders that silently diverge.
- Pin provider and module versions. An unpinned provider can change behavior on the next
  apply and rewrite infrastructure you did not intend to touch.
- Tag every resource with owner, environment, and cost-center so infrastructure is
  attributable and reapable.
- Make deletes deliberate: protect stateful resources (databases, buckets) with
  `prevent_destroy` / deletion protection so a careless diff cannot wipe data.

## Examples

**Good Example** — declarative, parameterized, state-safe, no secrets

```hcl
# Remote, locked state so concurrent applies can't corrupt it.
terraform {
  backend "s3" {
    bucket         = "acme-tf-state"
    key            = "prod/network.tfstate"
    dynamodb_table = "acme-tf-locks"   # advisory lock prevents concurrent apply
    encrypt        = true
  }
  required_providers { aws = { source = "hashicorp/aws", version = "~> 5.40" } } # pinned
}

variable "environment" { type = string }             # same module, differs by variable

resource "aws_db_instance" "main" {
  identifier   = "app-${var.environment}"
  engine       = "postgres"
  # Secret comes from a manager, never a literal — and note it will be stored in state,
  # so state itself must be encrypted (see backend "encrypt = true" above).
  password     = data.aws_secretsmanager_secret_version.db.secret_string
  storage_encrypted   = true
  deletion_protection = true                          # a stray diff can't drop the DB
}
```

**Bad Example** — imperative, hardcoded secret, local state, mutable

```hcl
resource "aws_db_instance" "main" {
  identifier = "app-prod"
  engine     = "postgres"
  password   = "S3cr3t-prod-pw"   # hardcoded secret, also written to state as plaintext
  # No deletion_protection: renaming identifier forces destroy+recreate — data gone.
}
# No backend block → state lives on whoever ran it last; two engineers = corrupted state.
# No provider version pin → next apply may silently rewrite resources.
```

## Common Mistakes

- Making changes in the cloud console, creating drift the code no longer matches.
- Keeping state locally or in git instead of a locked remote backend.
- Hardcoding secrets in `.tf` files (and forgetting they leak into state).
- Unpinned providers/modules that change behavior between applies.
- No `prevent_destroy` on databases, so a resource rename silently recreates and wipes data.
- Running `apply` from a workstation with a human's broad credentials instead of CI.
- Copy-pasting per-environment directories that drift apart over time.

## Production Tips

- Detect drift on a schedule (`plan` in CI nightly); alert when reality diverges from code.
- Encrypt state and restrict who can read it — it contains secrets and full topology.
- Import existing hand-made resources into IaC rather than leaving them unmanaged.
- Keep `apply` behind an approval gate for production; auto-apply is fine for ephemeral envs.

## AI Review Checklist

- Is all infrastructure declarative and defined in version control (no console changes)?
- Is state in a remote, encrypted, locked backend — never git, never local?
- Is a reviewed `plan` required before `apply`, with `apply` run only from CI?
- Are there zero hardcoded secrets, and is state encrypted since secrets land there?
- Are providers and modules version-pinned?
- Do stateful resources have deletion protection against accidental destroy?

## Related

- `knowledge/devops/09-configuration-management.md`
- `knowledge/devops/17-secrets-management.md`
- `knowledge/devops/11-orchestration.md`
- `knowledge/devops/24-change-management.md`
- `knowledge/devops/18-disaster-recovery.md`
