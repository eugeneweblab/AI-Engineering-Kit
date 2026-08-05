---
id: cicd/06-security-scanning
topic: cicd
slug: security-scanning
title: "Security Scanning"
type: doc
order: 6
status: ready
tags: [cicd, security-scanning, runs-on]
related: [cicd/05-quality-gates, cicd/07-artifacts, cicd/15-secrets, cicd/21-docker-integration]
when_to_use: "Read before adding or reviewing any automated security scan in a CI/CD pipeline."
---
# Security Scanning

## Purpose

This document defines how to find vulnerabilities automatically inside the pipeline,
before code or images reach production. It covers the four scan families every pipeline
needs — dependency (SCA), static analysis (SAST), secret detection, and container/image
scanning — and how to wire them as [quality gates](05-quality-gates.md) that block bad
builds without drowning developers in noise.

Security scanning is a *shift-left* control: catch the flaw at commit time, when it costs
minutes to fix, instead of at incident time, when it costs an outage.

## Why It Matters

Most breaches trace back to something a scanner would have caught: a known-CVE
dependency, a hardcoded credential, an injection sink, a base image with a decade of
unpatched packages. These are cheap to detect and expensive to miss. The pipeline is the
only place you can enforce the check on *every* change, uniformly, with no human deciding
to skip it. A scan that runs but never blocks is theater — the value is in the gate, and
the discipline is in keeping the gate's signal-to-noise high enough that people trust it.

## Core Principles

- **Scan every change, block on severity.** Run scans on every PR and every main-branch
  build. Fail the build on new High/Critical findings; the cost is occasional friction,
  the payoff is that nothing ships with a known critical hole.
- **Pin the baseline, alert on regressions.** Gate on *newly introduced* issues, not the
  entire historical backlog, or the gate is red forever and gets ignored.
- **Four scan types, not one.** SCA, SAST, secrets, and image scanning find disjoint
  classes of bug. Running only one leaves the others wide open.
- **Fail fast and cheap.** Put fast scans (secrets, SCA) early; put slow scans (full SAST,
  image scan) after build. A secret leak should fail in seconds, not after a 10-minute job.
- **Suppress explicitly, with an expiry.** Every waiver names the finding, the reason, and
  a review date. Silent, permanent suppression is how known bugs live forever.

## Best Practices

- Run **SCA** (e.g. Trivy, Grype, `npm audit`, Dependabot) against a lockfile so the scan
  matches exactly what ships. Fail on Critical/High with a fix available.
- Run **SAST** (e.g. CodeQL, Semgrep) on changed code; scope rules to your languages so
  runtime stays under a few minutes on PRs.
- Run a **secret scanner** (e.g. Gitleaks, TruffleHog) on the full history for new
  branches and on the diff for PRs. A hit must fail the build *and* trigger rotation.
- Scan container images (Trivy, Grype) for OS and library CVEs *after* build, before push.
  Also scan IaC (Checkov, tfsec) if you ship Terraform/Kubernetes manifests.
- Upload results in **SARIF** so findings appear inline in the PR, not buried in logs.
- Cache vulnerability databases but refresh them each run — a stale DB misses yesterday's
  CVE.
- Keep scanner versions pinned and updated deliberately; a scanner that auto-updates can
  turn a green pipeline red with no code change.

## Examples

**Good Example** — layered scans, gate on new High/Critical, SARIF output

```yaml
# .github/workflows/security.yml — runs on every PR
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 } # full history so the secret scan sees new commits

      - name: Secrets
        uses: gitleaks/gitleaks-action@v2 # fails the job on any detected secret

      - name: Dependencies (SCA)
        uses: aquasecurity/trivy-action@0.28.0
        with:
          scan-type: fs
          severity: CRITICAL,HIGH        # ignore Low/Medium noise on the gate
          exit-code: '1'                 # block the build when a High/Critical is found
          ignore-unfixed: true           # do not fail on CVEs with no available patch
          format: sarif
          output: trivy.sarif

      - name: Publish findings
        uses: github/codeql-action/upload-sarif@v3
        with: { sarif_file: trivy.sarif } # findings show up inline on the PR
```

**Bad Example** — scan runs but never blocks, and hides output

```yaml
- name: Security scan
  run: trivy fs . || true   # `|| true` swallows the exit code — the gate never fails
  # No severity filter, so every Low CVE is "found" and nobody reads the wall of text.
  # No SARIF upload, so results die in the log and never reach the reviewer.
  # Net effect: a green check that certifies nothing.
```

## Common Mistakes

- Appending `|| true` or `continue-on-error: true` so the scan can never fail the build.
- Gating on the entire backlog instead of new findings, so the pipeline is permanently red
  and everyone learns to ignore it.
- Running only `npm audit` and calling the app "scanned" — no SAST, secrets, or image scan.
- Detecting a leaked secret but not rotating it; the scanner only tells you it is already
  compromised.
- Scanning source but shipping a container built from an unscanned base image.
- Suppressing findings with no expiry or justification, so waivers accumulate forever.

## Production Tips

- Track mean-time-to-remediate for Critical findings; it is the real health metric, not
  scan count.
- Feed scan results into an SBOM ([artifacts](07-artifacts.md)) so you can answer "are we
  affected by CVE-X?" in minutes during the next zero-day.
- Run a full scheduled scan (nightly) in addition to PR scans — new CVEs are disclosed
  against code you already merged.
- Give teams a self-service, auditable waiver path; if suppression is painful, people
  disable the scanner instead.

## AI Review Checklist

- Does the pipeline run all four scan types: SCA, SAST, secrets, and image/IaC?
- Does a High/Critical finding actually fail the build (no `|| true`, no swallowed exit)?
- Does the gate trigger on *new* findings rather than the full historical backlog?
- Are results uploaded as SARIF so they surface in the PR?
- Does a detected secret trigger rotation, not just a red build?
- Are suppressions explicit, justified, and time-bounded?
- Is the container's base image scanned, not just the application source?

## Related

- `knowledge/cicd/05-quality-gates.md`
- `knowledge/cicd/07-artifacts.md`
- `knowledge/cicd/15-secrets.md`
- `knowledge/cicd/21-docker-integration.md`
