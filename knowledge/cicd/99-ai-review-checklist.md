---
id: cicd/99-ai-review-checklist
topic: cicd
slug: ai-review-checklist
title: "AI Review Checklist"
type: doc
order: 99
status: ready
tags: [cicd, ai-review-checklist]
related: [cicd/02-pipeline-design, cicd/05-quality-gates, cicd/06-security-scanning, cicd/15-secrets, cicd/30-engineering-principles]
when_to_use: "Read when reviewing a pull request that adds or changes CI/CD pipeline configuration."
---
# AI Review Checklist

## Purpose

A checklist for an AI agent reviewing a change to CI/CD configuration — a workflow file,
a pipeline stage, a deploy script. It targets the failures that are easy to introduce and
hard to spot in a diff: unpinned inputs, leaked secrets, missing gates, and rollback gaps.
Use it to review the pipeline as code, holding it to the same bar as application code.

## Why It Matters

Pipeline changes are reviewed less carefully than application code, yet a single bad line
can leak a credential into logs, ship an untested artifact, or remove the gate that
protects production. These defects pass tests — the pipeline goes green — so the review is
the only place they are caught. A reviewer who scans YAML casually is the last line down.

## Correctness & Determinism

- [ ] Are all base images pinned by digest and actions/plugins pinned by SHA or exact tag?
- [ ] Are dependencies installed from a lockfile rather than resolved to latest?
- [ ] Is the artifact built once and promoted, rather than rebuilt per environment?
- [ ] Are cache keys derived from a hash of inputs, so stale caches cannot poison a build?
- [ ] Are jobs idempotent and safe to re-run without double-deploying or corrupting state?

## Gates & Flow

- [ ] Does the change keep required checks blocking on merge and deploy?
- [ ] Do fast, cheap stages (lint, unit) run before slow ones (integration, e2e)?
- [ ] Does a production deploy still require an explicit approval or protected environment?
- [ ] Are new stages wired with correct `needs`/dependencies so ordering is enforced?
- [ ] Does the change avoid `continue-on-error` or blanket retries that hide real failures?

## Security

- [ ] Are all secrets referenced from a secrets store, with none hardcoded in the diff?
- [ ] Could any added `echo`, `set -x`, or debug step print a secret to the logs?
- [ ] Do new jobs use least-privilege tokens (scoped, short-lived, or OIDC)?
- [ ] Does the change avoid running untrusted PR code with access to production secrets?
- [ ] Is dependency/image/secret scanning still present and still blocking on critical issues?

## Release Safety

- [ ] Does the change preserve a tested, one-step rollback path?
- [ ] Are database migrations backward-compatible and separable from the code deploy?
- [ ] Is every deploy still traceable (commit SHA, artifact digest, actor recorded)?
- [ ] Do health checks / smoke tests still gate traffic to a new version?

## Maintainability

- [ ] Is duplicated pipeline logic factored into reusable workflows/templates?
- [ ] Are hardcoded environment values replaced with variables/inputs?
- [ ] Does the pipeline stay within its time budget after this change?

## Related

- `knowledge/cicd/02-pipeline-design.md`
- `knowledge/cicd/05-quality-gates.md`
- `knowledge/cicd/06-security-scanning.md`
- `knowledge/cicd/15-secrets.md`
- `knowledge/cicd/30-engineering-principles.md`
