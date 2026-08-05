---
id: kubernetes/22-security
topic: kubernetes
slug: security
title: "Kubernetes Security"
type: doc
order: 22
status: ready
tags: [kubernetes, security, securityContext, emptyDir, "@sha", runAsUser, readOnlyRootFilesystem, audit]
related: [kubernetes/18-rbac, kubernetes/17-network-policies, kubernetes/10-secrets, kubernetes/99-ai-review-checklist]
when_to_use: "Read before deploying any workload to a shared or production cluster, or when reviewing a pod's securityContext, image, or privilege settings."
---
# Kubernetes Security

## Purpose

This document defines workload-level security for Kubernetes: how to run a container with
the least Linux privilege it needs (`securityContext`), harden images, and admit only
safe pods (Pod Security Standards). It is written so an agent can ship a workload that
does not become a foothold if its process is compromised.

This is the in-container and admission layer. It complements [RBAC](18-rbac.md) (who may
call the API), [network policies](17-network-policies.md) (what may talk to what), and
[Secrets](10-secrets.md) (how credentials are handled). Cluster security is the union of
all four; none alone is sufficient.

## Why It Matters

A container shares the host kernel with every other pod on the node. If a process runs as
root, with a writable filesystem and extra Linux capabilities, an RCE in that process can
tamper with itself, escalate through the kernel, or pivot to the node. Defaults are
permissive for backward compatibility, so a pod with no `securityContext` runs far more
privileged than any app needs. Security here is about shrinking the blast radius *before*
an exploit, because after one you have already lost.

## Core Principles

- **Run as non-root, always.** Set `runAsNonRoot: true` and a high UID. Root in a
  container is root on the node kernel if isolation fails.
- **Drop every capability, add back none (or few).** `capabilities.drop: ["ALL"]`.
  Almost no app needs `NET_ADMIN`, `SYS_ADMIN`, or the rest.
- **Read-only root filesystem.** `readOnlyRootFilesystem: true` stops an attacker
  writing tools or modifying binaries; mount an `emptyDir` for genuine scratch needs.
- **No privilege escalation.** `allowPrivilegeEscalation: false` blocks setuid paths to
  more privilege. Never set `privileged: true`.
- **Minimal, pinned, scanned images.** Distroless or slim base, pinned by digest, scanned
  for CVEs. Every extra binary is an extra tool for an attacker.
- **Enforce at admission.** Pod Security Standards (`restricted`) reject unsafe pods at
  the namespace boundary — defense that does not depend on every author remembering.

## Best Practices

- Apply the built-in Pod Security Admission label
  `pod-security.kubernetes.io/enforce: restricted` on production namespaces so
  non-compliant pods are rejected, not just warned.
- Set a full `securityContext` at both pod and container level; container settings win
  where they overlap.
- Pin images by digest (`image@sha256:...`), not by mutable tags like `latest`, so the
  running bits are reproducible and cannot silently change.
- Never mount the Docker socket or host paths like `/`, `/var/run`, or `/proc` into a
  container — they hand over the node.
- Set `automountServiceAccountToken: false` unless the pod calls the Kubernetes API.
- Use `seccompProfile: { type: RuntimeDefault }` to filter dangerous syscalls.
- Scan images in CI and block on high-severity CVEs; rebuild regularly so base-image
  patches land.

## Examples

**Good Example** — hardened, non-root, locked-down container

```yaml
spec:
  automountServiceAccountToken: false   # pod does not call the API
  securityContext:
    runAsNonRoot: true
    runAsUser: 10001                    # high, non-root UID
    fsGroup: 10001
    seccompProfile: { type: RuntimeDefault }
  containers:
    - name: app
      image: registry.example.com/app@sha256:8f2c...   # pinned by digest
      securityContext:
        allowPrivilegeEscalation: false  # no setuid path to more privilege
        readOnlyRootFilesystem: true     # attacker cannot write tools/binaries
        capabilities:
          drop: ["ALL"]                  # start from zero Linux capabilities
      volumeMounts:
        - { name: tmp, mountPath: /tmp } # writable scratch via emptyDir, not root fs
  volumes:
    - name: tmp
      emptyDir: {}
```

**Bad Example** — privileged root container from a mutable tag

```yaml
spec:
  containers:
    - name: app
      image: app:latest              # mutable tag: running bits can change silently
      securityContext:
        privileged: true             # full access to host devices and kernel
        runAsUser: 0                 # root: container root == node root on escape
        # readOnlyRootFilesystem defaults false → attacker can write anywhere
      volumeMounts:
        - name: docker-sock
          mountPath: /var/run/docker.sock   # mounts host Docker socket → owns the node
  volumes:
    - name: docker-sock
      hostPath: { path: /var/run/docker.sock }
```

## Common Mistakes

- Running as root because the base image defaults to it and nobody overrode `runAsUser`.
- Leaving `readOnlyRootFilesystem` and `allowPrivilegeEscalation` at their unsafe
  defaults.
- Keeping all Linux capabilities instead of dropping `ALL`.
- Using `:latest` or floating tags, making deployments non-reproducible.
- Mounting the Docker socket or host paths for "convenience," handing over the node.
- Auto-mounting a ServiceAccount token into pods that never use it.
- Relying on authors to remember hardening instead of enforcing Pod Security Admission.

## Production Tips

- Enforce `restricted` Pod Security in prod namespaces; run it in `warn`/`audit` mode
  first to find violations without breaking deploys.
- Gate CI on image scans and fail builds on fixable high/critical CVEs.
- Rotate and rebuild base images on a schedule so kernel/library patches reach running
  pods.

## AI Review Checklist

- Does the container set `runAsNonRoot: true` with a non-zero UID?
- Is `allowPrivilegeEscalation: false` and `privileged` unset?
- Is `readOnlyRootFilesystem: true` with writable scratch via `emptyDir`?
- Are all capabilities dropped (`drop: ["ALL"]`) and `seccompProfile` set?
- Is the image pinned by digest and scanned for CVEs?
- Are host paths and the Docker socket kept out of the pod?
- Is the namespace enforcing the `restricted` Pod Security Standard?

## Related

- `knowledge/kubernetes/18-rbac.md`
- `knowledge/kubernetes/17-network-policies.md`
- `knowledge/kubernetes/10-secrets.md`
- `knowledge/kubernetes/99-ai-review-checklist.md`
