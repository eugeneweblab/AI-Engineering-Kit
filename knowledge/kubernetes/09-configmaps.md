---
id: kubernetes/09-configmaps
topic: kubernetes
slug: configmaps
title: "Configmaps"
type: doc
order: 9
status: ready
tags: [kubernetes, configmaps, ConfigMap, LOG_LEVEL, DB_PASSWORD, pods, settings, configuration]
related: [kubernetes/10-secrets, kubernetes/11-volumes, kubernetes/05-deployments, kubernetes/04-pods, kubernetes/26-production]
when_to_use: "Read before externalizing non-secret application configuration or wiring environment-specific settings into Pods."
---
# Configmaps

## Purpose

This document defines how to externalize non-confidential configuration with a ConfigMap.
A ConfigMap holds key-value pairs or whole config files that you inject into Pods as
environment variables or mounted files. It separates configuration from the container
image, so the same image runs unchanged across dev, staging, and production.

A ConfigMap is for *non-secret* data only. Passwords, tokens, keys, and certificates
belong in a [Secret](10-secrets.md). The two objects look similar on purpose, but only
Secrets get the intended (limited) confidentiality handling — never put secrets here.

## Why It Matters

The one rule people break is putting secrets in ConfigMaps. ConfigMap data is stored and
returned in plaintext, is readable by anyone with `get configmap` in the namespace, and
is trivial to leak in `kubectl describe` output, logs, or a Git-committed manifest. The
image is built once and promoted through environments; a ConfigMap is how you change
behavior between them without a rebuild. Get the injection method wrong — env var vs
mounted file, and whether updates propagate — and you ship stale config that no rollout
seems to fix.

## Core Principles

- **ConfigMaps are plaintext and non-secret.** Anyone who can read the namespace can read
  every value. If a value would harm you if leaked, it is a Secret, not a ConfigMap.
- **Env vars are captured at container start; they do not update.** A Pod reads env vars
  once. Changing the ConfigMap does nothing until the Pod restarts.
- **Mounted files update in place; consumers must re-read.** A ConfigMap volume is
  refreshed by the kubelet after a short delay, but the app only sees it if it re-reads
  the file or watches for changes.
- **Config is environment-specific; keep it out of the image.** Bake defaults into the
  app, override per environment via ConfigMap. The image stays identical everywhere.
- **A missing key can crash the Pod.** Referencing an absent ConfigMap or key with
  `optional: false` (the default) prevents the container from starting.

## Best Practices

- Inject whole files as a volume mount for config the app reads from disk; use `env`/
  `envFrom` for a handful of simple settings.
- To force a rollout on config change, either template a content hash into the Pod
  template annotation or version the ConfigMap name (`app-config-v3`). Editing a
  ConfigMap in place does **not** restart Pods consuming it via env vars.
- Keep one ConfigMap per concern and per environment; do not stuff unrelated settings
  into one giant map.
- Set `immutable: true` on ConfigMaps that should never change after creation — it
  prevents accidental edits and reduces API-server watch load at scale.
- Store ConfigMap manifests in Git and apply them declaratively; never `kubectl edit`
  production config by hand.
- Never reference a Secret's value into a ConfigMap, and never log the full config at
  startup — you will eventually log something that migrated into it by mistake.

## Examples

**Good Example** — file-style config mounted as a volume, rollout pinned by hash

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: checkout-config
data:
  app.yaml: |            # whole config file, read from disk by the app
    logLevel: info
    featureFlags:
      newCheckout: true
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: checkout
spec:
  selector: { matchLabels: { app: checkout } }
  template:
    metadata:
      labels: { app: checkout }        # must match the selector above
      annotations:
        checksum/config: "b21f...e3"   # hash of the ConfigMap → changes trigger a rollout
    spec:
      containers:
        - name: web
          image: checkout:1.8.2
          volumeMounts:
            - name: config
              mountPath: /etc/checkout   # app reads /etc/checkout/app.yaml
              readOnly: true
      volumes:
        - name: config
          configMap:
            name: checkout-config
```

**Bad Example** — secret in a ConfigMap, env vars that never update

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: checkout-config
data:
  LOG_LEVEL: info
  DB_PASSWORD: "s3cr3t-prod-pw"   # SECRET in plaintext, readable by the whole namespace
```

Consumed via `envFrom`, values are captured at container start. Editing this
ConfigMap later changes nothing until every Pod is restarted, so operators
"update config" and are baffled that nothing takes effect.

```yaml
# inside the Pod's container spec
    envFrom:
      - configMapRef:
          name: checkout-config
```

## Common Mistakes

- Storing passwords, tokens, or keys in a ConfigMap instead of a Secret.
- Expecting env-var config to update live — it is frozen at container start.
- Editing a ConfigMap and assuming Pods pick it up without a rollout.
- Assuming a mounted-file update is seen instantly — there is propagation delay and the
  app must re-read the file.
- One monolithic ConfigMap shared across environments, making per-environment overrides
  error-prone.
- Referencing a ConfigMap or key that does not exist, which blocks the container from
  starting.

## AI Review Checklist

- Does this ConfigMap contain only non-secret data? (Any credential belongs in a Secret.)
- Is the injection method correct — mounted file for on-disk config, env for simple flags?
- If config changes must trigger a rollout, is there a content hash or versioned name?
- Are ConfigMaps scoped per concern/environment rather than one giant catch-all?
- Are manifests source-controlled and applied declaratively, not hand-edited in prod?
- Should this ConfigMap be `immutable: true` to prevent accidental changes?

## Related

- `knowledge/kubernetes/10-secrets.md`
- `knowledge/kubernetes/11-volumes.md`
- `knowledge/kubernetes/05-deployments.md`
- `knowledge/kubernetes/04-pods.md`
- `knowledge/kubernetes/26-production.md`
