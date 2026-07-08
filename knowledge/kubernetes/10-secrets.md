---
id: kubernetes/10-secrets
topic: kubernetes
slug: secrets
title: "Secrets"
type: doc
order: 10
status: ready
tags: [kubernetes, secrets]
related: [kubernetes/09-configmaps, kubernetes/18-rbac, kubernetes/22-security, kubernetes/11-volumes]
when_to_use: "Read before handling any credential, token, key, or certificate in a cluster — creation, injection, or review."
---
# Secrets

## Purpose

This document defines how to store and inject confidential data — passwords, API tokens,
private keys, TLS certificates — with a Kubernetes Secret. A Secret is a namespaced object
that holds `data` (base64-encoded values) and injects it into Pods as environment
variables or mounted files, keeping credentials out of the container image and out of the
application manifest.

A Secret is not a [ConfigMap](09-configmaps.md) and not encryption. It is the *right
place* to put credentials, but it provides confidentiality only when the cluster is
configured for it. Treat everything below as required, not optional.

## Why It Matters

Secrets are the highest-value target in the cluster. The dangerous misconception is that
"Secret" means "encrypted". By default, Secret data is only **base64-encoded** — trivially
reversible — and stored in etcd. Without encryption-at-rest and tight RBAC, anyone who can
read the namespace or reach etcd reads every credential. A single leaked Secret can
compromise a database, a cloud account, or every user at once. Because the failure is
silent and the blast radius is total, Secret handling is held to the authentication bar:
assume the manifest, the logs, and Git history are all hostile.

## Core Principles

- **Base64 is encoding, not encryption.** `data` values are readable by anyone who can
  `get secret`. Enable etcd encryption-at-rest so the raw store is not plaintext.
- **Never commit Secrets to Git.** A plaintext Secret manifest in a repo is a permanent
  leak — Git history keeps it forever. Use sealed/external secrets or a secrets manager.
- **Prefer file mounts over environment variables.** Env vars leak into crash dumps,
  child processes, `kubectl describe pod`, and logs. Mounted files are `tmpfs`-backed and
  do not appear in the Pod's environment.
- **Restrict access with RBAC.** `get`/`list` on Secrets is a privileged permission. Scope
  it to the specific workloads and people that need it (see [RBAC](18-rbac.md)).
- **Rotate and revoke.** A Secret is a liability that ages. Assume it will leak eventually;
  make rotation routine and revocation possible.

## Best Practices

- Store secrets in an external system (cloud secrets manager, Vault) and sync them in with
  the External Secrets Operator, or encrypt them at rest before Git with Sealed Secrets.
  Never keep plaintext Secret manifests in version control.
- Enable [encryption at rest](22-security.md) for Secrets in etcd (a KMS provider), so a
  stolen etcd snapshot does not hand over every credential.
- Mount secrets as files (`tmpfs`), not env vars, to keep them out of process
  environments and diagnostic output.
- Lock down RBAC: no wildcard `get secrets` at cluster scope; grant per-namespace,
  per-name where possible.
- Use typed Secrets where they exist — `kubernetes.io/tls` for certs,
  `kubernetes.io/dockerconfigjson` for registry creds — so consumers validate structure.
- Set `imagePullSecrets` for private registries; do not bake registry credentials into
  nodes.
- Rotate on a schedule and immediately on suspected exposure; ensure the app re-reads
  mounted secrets or is restarted on rotation.

## Examples

**Good Example** — sourced from a secrets manager, mounted as a read-only file

```yaml
# Secret is created by External Secrets Operator from a cloud secrets manager,
# NOT stored in Git. Shown here only to illustrate consumption.
apiVersion: v1
kind: Secret
metadata:
  name: checkout-db
type: Opaque
stringData:
  password: "<synced-from-secrets-manager>"   # never a real value in a committed file
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: checkout
spec:
  template:
    spec:
      containers:
        - name: web
          image: checkout:1.8.2
          volumeMounts:
            - name: db
              mountPath: /etc/secrets   # app reads /etc/secrets/password (tmpfs, not env)
              readOnly: true
      volumes:
        - name: db
          secret:
            secretName: checkout-db
            defaultMode: 0400          # owner read-only
```

**Bad Example** — plaintext in Git, injected as an env var

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: checkout-db
type: Opaque
data:
  password: czNjcjN0LXByb2QtcHc=   # base64("s3cr3t-prod-pw") — reversible, committed to Git forever
---
    env:
      - name: DB_PASSWORD
        valueFrom:
          secretKeyRef:
            name: checkout-db
            key: password           # env var leaks into `describe pod`, logs, child processes
```

## Common Mistakes

- Believing base64 encoding provides confidentiality.
- Committing plaintext Secret manifests to Git (a permanent, unrevocable leak).
- Injecting secrets as environment variables, exposing them in diagnostics and child
  processes.
- Running the cluster without etcd encryption-at-rest for Secrets.
- Broad RBAC granting `get secrets` cluster-wide to service accounts or users.
- Never rotating credentials, so one old leak stays valid indefinitely.
- Logging the full environment or config at startup, which dumps env-injected secrets.

## Production Tips

- Audit Secret access via the API audit log; alert on unusual `get`/`list` on Secrets.
- Automate rotation and wire deployments to restart or re-read on new secret versions.
- Scan repositories and CI logs for committed credentials; treat any hit as an incident
  and rotate immediately — deleting the commit does not remove it from history.

## AI Review Checklist

- Is confidential data in a Secret (not a ConfigMap), and is no plaintext Secret committed
  to Git?
- Are secrets sourced from a secrets manager / sealed, rather than raw manifests?
- Is etcd encryption-at-rest enabled for Secrets?
- Are secrets mounted as files rather than injected as environment variables?
- Is RBAC on Secrets scoped narrowly (no cluster-wide wildcard `get`)?
- Is there a rotation and revocation path, and does the app pick up rotated values?

## Related

- `knowledge/kubernetes/09-configmaps.md`
- `knowledge/kubernetes/18-rbac.md`
- `knowledge/kubernetes/22-security.md`
- `knowledge/kubernetes/11-volumes.md`
- `knowledge/kubernetes/08-ingress.md`
