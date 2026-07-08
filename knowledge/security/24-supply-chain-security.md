---
id: security/24-supply-chain-security
topic: security
slug: supply-chain-security
title: "Supply Chain Security"
type: doc
order: 24
status: ready
tags: [security, supply-chain-security]
related: [security/23-dependency-security, security/16-secrets-management, security/25-monitoring, security/26-incident-response]
when_to_use: "Read before configuring CI/CD, package publishing, or build-artifact integrity controls."
---
# Supply Chain Security

## Purpose

This document defines how to protect the path from source code to running artifact against
tampering: the build pipeline, package registries, CI credentials, and the provenance of
what you ship. It is written so an agent can set up CI/CD and releases so that a compromised
dependency, a leaked token, or a poisoned build step cannot silently ship malicious code to
users.

Where [dependency security](23-dependency-security.md) is about *known-vulnerable* packages,
supply-chain security is about *actively malicious* or *tampered* artifacts and the systems
that build them — a broader, adversarial threat covering typosquats, compromised
maintainers, and pipeline injection.

## Why It Matters

The build pipeline is a force multiplier: whoever controls it ships code to every user, with
your signature on it, bypassing code review. Real incidents — SolarWinds, event-stream,
codecov, the xz backdoor — show the pattern: attackers target the pipeline or a trusted
dependency because it is the highest-leverage point in the whole system. A single leaked CI
token or a malicious `postinstall` script converts one compromise into a fleet-wide breach
that looks, to every downstream check, like a legitimate release. The defenses are about
integrity and provenance: prove that what you run is what you built from the source you
reviewed.

## Core Principles

- **Least privilege for the pipeline.** CI credentials are the crown jewels. Scope tokens
  to one job, make them short-lived (OIDC federation, not long-lived secrets), and never
  expose them to PRs from forks.
- **Verify integrity end to end.** Pin dependencies by hash, verify signatures/checksums on
  downloads, and produce signed provenance (SLSA, Sigstore/cosign) for your own artifacts so
  consumers can verify them.
- **Isolate untrusted code at build time.** Package install scripts (`postinstall`) run
  arbitrary code on the build machine. Disable them where possible and build in ephemeral,
  network-restricted sandboxes.
- **Pin your tools, not just your libraries.** GitHub Actions, base images, and CLIs are
  dependencies too. Pin Actions to a commit SHA (a tag is mutable) and base images to a
  digest.
- **Assume a dependency will turn hostile.** Design so one malicious package cannot exfiltrate
  secrets or reach production unchecked — no ambient credentials in the build, egress
  controls on the runner.

## Best Practices

- Use OIDC/workload-identity federation for cloud and registry auth instead of stored
  long-lived secrets; grant the minimum scope and the shortest lifetime.
- Pin GitHub Actions and other CI steps to a full commit SHA, and base container images to a
  digest (`@sha256:...`), so a moved tag cannot swap in new code.
- Enable dependency install without lifecycle scripts (`npm ci --ignore-scripts` where
  feasible; `pnpm` blocks build scripts by default) and allowlist the few packages that
  legitimately need them.
- Sign artifacts and generate provenance with Sigstore/cosign or SLSA attestations; verify
  signatures before deploy.
- Require 2FA and (ideally) hardware tokens for publishing to package registries; use scoped,
  granular publish tokens, never a personal all-scopes token.
- Restrict build-runner egress to known hosts so a malicious step cannot phone home or
  exfiltrate secrets; run builds in ephemeral, isolated environments.
- Protect the default branch: required reviews, signed commits, and no direct pushes, so
  source integrity precedes build integrity.

## Examples

**Good Example** — pinned Action, OIDC auth, scripts disabled

```yaml
permissions:
  id-token: write        # OIDC only; no long-lived cloud secret stored in CI
  contents: read
steps:
  # Pin to an immutable commit SHA — a tag like @v4 can be moved to point at new code.
  - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1
  - run: npm ci --ignore-scripts   # do not execute arbitrary postinstall code at build time
  - uses: sigstore/cosign-installer@59acb6260d9c0ba8f4a2f9d9b1d0e0c9f8b7c6d5 # pinned
  - run: cosign sign --yes $IMAGE  # signed provenance downstream can verify
```

**Bad Example** — mutable tag, long-lived secret, scripts enabled

```yaml
steps:
  - uses: actions/checkout@main          # mutable ref: whoever controls it runs code in your CI
  - run: npm install                     # runs every dependency's postinstall script unsandboxed
    env:
      NPM_TOKEN: ${{ secrets.NPM_TOKEN }} # broad, long-lived publish token exposed to the build
      AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_KEY }} # ambient prod credentials any dep can read
  # A single malicious transitive package exfiltrates both secrets on install.
```

## Common Mistakes

- Pinning Actions/images to mutable tags (`@v4`, `@latest`) instead of a SHA/digest.
- Storing long-lived, broadly-scoped CI secrets instead of short-lived OIDC tokens.
- Exposing production credentials to build steps that also run untrusted dependency code.
- Running dependency install scripts unsandboxed, with network access to the whole internet.
- Publishing from a personal token without 2FA, so one phished maintainer poisons the package.
- Shipping unsigned artifacts, so downstream cannot detect tampering.
- Trusting a lockfile hash for integrity while letting the build tool itself be unpinned.

## Production Tips

- Keep and monitor an SBOM plus signed provenance for every release so you can prove and
  trace exactly what shipped during an [incident](26-incident-response.md).
- Alert on anomalous CI behavior — new outbound hosts, unexpected secret access — via
  [monitoring](25-monitoring.md); pipeline compromise often shows as strange egress first.
- Rotate any secret that was ever exposed to a fork-triggered or third-party workflow; assume
  it leaked.
- Rehearse the "a package we use was backdoored" scenario: can you identify affected releases,
  revoke, and rebuild from a clean, pinned source?

## AI Review Checklist

- Are CI Actions pinned to commit SHAs and base images to digests, not mutable tags?
- Does the pipeline use short-lived OIDC tokens instead of long-lived stored secrets?
- Are production credentials kept out of steps that run untrusted dependency code?
- Are dependency lifecycle/install scripts disabled or explicitly allowlisted?
- Are published artifacts signed and their provenance verifiable (Sigstore/SLSA)?
- Is registry publishing protected by 2FA and scoped tokens?
- Is the default branch protected with required reviews before code reaches the build?

## Related

- `knowledge/security/23-dependency-security.md`
- `knowledge/security/16-secrets-management.md`
- `knowledge/security/25-monitoring.md`
- `knowledge/security/26-incident-response.md`
