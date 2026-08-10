---
id: kubernetes/08-ingress
topic: kubernetes
slug: ingress
title: "Ingress"
type: doc
order: 8
status: ready
tags: [kubernetes, ingress, ClusterIP, outside, edge, tls]
related: [kubernetes/07-services, kubernetes/10-secrets, kubernetes/17-network-policies, kubernetes/22-security, kubernetes/05-deployments]
when_to_use: "Read before exposing HTTP(S) services to the outside world or configuring host/path routing and TLS at the cluster edge."
---
# Ingress

## Purpose

This document defines how to route external HTTP and HTTPS traffic into the cluster with
an Ingress. An Ingress is an L7 rule set — host and path matches that map to backend
[Services](07-services.md) — plus TLS termination at the edge. It lets many apps share a
single external IP and certificate instead of one load balancer per app.

An Ingress is only a set of rules; it does nothing without an **Ingress controller**
(NGINX, Traefik, an cloud ALB controller, etc.) running in the cluster to enforce them.
For richer routing, gRPC, and cross-namespace delegation, the Gateway API is the modern
successor, but Ingress remains widely deployed and is the baseline you must understand.

## Why It Matters

The Ingress is the cluster's front door to the internet. A wrong rule can route one app's
traffic to another, or expose an internal admin service publicly. A missing or expired
TLS Secret drops the site to plaintext or breaks it entirely. Because the Ingress
controller merges rules from every Ingress object in the cluster, one team's careless
host or path rule can shadow or hijack another team's traffic. Edge misconfiguration is
directly attacker-facing, so it is held to the same bar as authentication code.

## Core Principles

- **An Ingress needs a controller and an IngressClass.** Without a running controller and
  a matching `ingressClassName`, the object exists but routes nothing.
- **Rules are host + path → Service + port.** Be specific. Overly broad hosts or a `/`
  prefix catch-all can swallow traffic meant for another app.
- **TLS lives in a Secret, referenced by the Ingress.** The certificate and key are a
  `kubernetes.io/tls` Secret; the Ingress names it. Automate renewal (cert-manager).
- **`pathType` changes matching semantics.** `Prefix` matches path segments;
  `ImplementationSpecific` is controller-dependent and non-portable. Prefer `Prefix` or
  `Exact` so behavior is predictable across controllers.
- **The Ingress terminates TLS; the backend hop may be plaintext.** Traffic from the
  controller to the Service is inside the cluster — secure it with a
  [NetworkPolicy](17-network-policies.md) or mTLS if the threat model requires it.

## Best Practices

- Set `ingressClassName` explicitly. Relying on a default class is how traffic ends up on
  the wrong controller after a cluster change.
- Terminate TLS at the Ingress with a cert-manager–issued Secret; never paste certs into
  manifests or Git. Redirect HTTP to HTTPS.
- Use specific hosts and `pathType: Prefix`/`Exact`. Avoid a bare `/` catch-all unless the
  app truly owns the whole host.
- Keep controller-specific tuning in annotations, and document why each is set — they are
  not portable across controllers.
- Do not expose internal-only or admin Services through a public Ingress; put them behind
  authentication and a separate internal Ingress or leave them `ClusterIP`.
- Set request size, timeout, and rate-limit annotations appropriate to the backend to
  blunt abuse at the edge (see [security](22-security.md)).

## Examples

**Good Example** — explicit class, TLS from a Secret, specific host and path

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: checkout
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod   # cert auto-issued + renewed
    nginx.ingress.kubernetes.io/ssl-redirect: "true"   # force HTTP → HTTPS
spec:
  ingressClassName: nginx      # explicit controller, no reliance on a default
  tls:
    - hosts: [checkout.example.com]
      secretName: checkout-tls # kubernetes.io/tls Secret, managed by cert-manager
  rules:
    - host: checkout.example.com
      http:
        paths:
          - path: /
            pathType: Prefix   # predictable, portable segment matching
            backend:
              service:
                name: checkout
                port:
                  name: http   # reference the Service port by name
```

**Bad Example** — no class, no TLS, catch-all host that hijacks traffic

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: checkout
spec:
  # no ingressClassName → may bind to the wrong controller or none
  rules:
    - http:                    # no host → matches EVERY hostname, shadows other apps
        paths:
          - path: /
            pathType: ImplementationSpecific  # non-portable, controller-defined matching
            backend:
              service:
                name: admin-internal   # internal admin service exposed publicly, no auth
                port: { number: 8080 }
  # no tls block → served as plaintext HTTP
```

## Common Mistakes

- Creating an Ingress with no controller installed, then wondering why nothing routes.
- Omitting `ingressClassName` and landing on the wrong (or no) controller.
- A host-less rule or `/` catch-all that swallows traffic intended for other apps.
- Missing or expired TLS Secret, silently serving plaintext or breaking the site.
- Exposing internal/admin Services through the public Ingress without authentication.
- Relying on `ImplementationSpecific` path behavior, which differs between controllers.
- Pasting certificates into the manifest instead of a managed `kubernetes.io/tls` Secret.

## Production Tips

- Automate certificate issuance and renewal with cert-manager; alert well before expiry.
- Watch controller access logs and 4xx/5xx rates — the edge is where abuse first appears.
- Consider the Gateway API for new deployments needing header/method routing, traffic
  splitting, or safe cross-namespace delegation; it addresses Ingress's expressiveness
  gaps.

## AI Review Checklist

- Is `ingressClassName` set explicitly and does a matching controller run in the cluster?
- Is TLS configured with a managed `kubernetes.io/tls` Secret, and is HTTP redirected to
  HTTPS?
- Are hosts specific and `pathType` set to `Prefix` or `Exact` (not
  `ImplementationSpecific`) unless a controller feature requires otherwise?
- Do any rules unintentionally act as a catch-all that could shadow other apps?
- Are internal/admin Services kept off the public Ingress or protected by auth?
- Are certificates and keys sourced from Secrets, never embedded in the manifest?

## Related

- `knowledge/kubernetes/07-services.md`
- `knowledge/kubernetes/10-secrets.md`
- `knowledge/kubernetes/17-network-policies.md`
- `knowledge/kubernetes/22-security.md`
- `knowledge/kubernetes/05-deployments.md`
