---
id: kubernetes/07-services
topic: kubernetes
slug: services
title: "Services"
type: doc
order: 7
status: ready
tags: [kubernetes, services]
related: [kubernetes/08-ingress, kubernetes/05-deployments, kubernetes/04-pods, kubernetes/17-network-policies]
when_to_use: "Read before exposing a workload to other Pods or the network, or debugging why traffic never reaches your Pods."
---
# Services

## Purpose

This document defines how to give a set of Pods a stable network identity with a Service.
Pods are ephemeral: they are created and destroyed, and each gets a new IP. A Service is
a stable virtual IP and DNS name that load-balances to a changing set of healthy Pods
selected by labels. It decouples callers from the individual Pods behind it.

A Service handles L4 (TCP/UDP) routing inside and at the edge of the cluster. For L7
(HTTP host/path) routing, TLS termination, and a single external entry point, use an
[Ingress](08-ingress.md) in front of Services.

## Why It Matters

Without a Service, callers would have to track Pod IPs that change on every restart —
impossible to keep correct. The Service's selector is what determines which Pods receive
traffic. If the selector matches no Pods, the Service silently blackholes every request:
no error, just timeouts. If it matches the *wrong* Pods, requests are routed to the wrong
workload. Because the failure is a silent timeout rather than an exception, a broken
selector is one of the most common and most confusing outages in Kubernetes.

## Core Principles

- **Match on labels; keep the selector aligned with the Pods.** A Service routes to Pods
  whose labels match `spec.selector`. If they drift, traffic stops with no error.
- **`port` is the Service port; `targetPort` is the container port.** They are
  independent. Callers hit `port`; the Service forwards to `targetPort` on the Pod.
- **Default to `ClusterIP`.** In-cluster traffic should never use `NodePort` or
  `LoadBalancer`. Reserve those for genuine external exposure — the cost of a
  `LoadBalancer` is a real cloud load balancer (and bill) per Service.
- **Only ready Pods receive traffic.** Endpoints are populated from Pods that pass their
  readiness probe. No readiness probe means traffic hits Pods that are still starting.
- **Address Services by DNS, not IP.** Use `name.namespace.svc.cluster.local` (or just
  `name` within the namespace). Cluster IPs are stable but not guaranteed across recreate.

## Best Practices

- Use `ClusterIP` for internal traffic; expose externally through an
  [Ingress](08-ingress.md) or Gateway, not a `LoadBalancer` per app.
- Name your ports (`name: http`) so an Ingress or another Service can reference the port
  by name and survive port-number changes.
- Give every workload a readiness probe so the Service removes unready Pods from rotation
  during rollouts and startup.
- Set `sessionAffinity: ClientIP` only when the app genuinely needs sticky sessions; it
  weakens load distribution.
- Use a headless Service (`clusterIP: None`) when clients need the individual Pod IPs —
  required for [StatefulSets](13-statefulsets.md) and some databases.
- Restrict who can reach a Service with a [NetworkPolicy](17-network-policies.md); a
  Service does not authorize callers, it only routes them.

## Examples

**Good Example** — internal ClusterIP with named ports and a readiness-gated backend

```yaml
apiVersion: v1
kind: Service
metadata:
  name: checkout
spec:
  type: ClusterIP            # internal only; no cloud load balancer created
  selector:
    app: checkout           # must match the Pods' labels exactly
  ports:
    - name: http            # named so an Ingress can target "http" by name
      port: 80              # clients call checkout:80
      targetPort: 8080      # forwarded to container port 8080
---
# Backend Pods carry app: checkout AND a readiness probe, so only ready
# Pods appear in this Service's Endpoints.
```

**Bad Example** — selector drift and per-app LoadBalancer

```yaml
apiVersion: v1
kind: Service
metadata:
  name: checkout
spec:
  type: LoadBalancer        # provisions (and bills for) a cloud LB for internal traffic
  selector:
    app: checkout-v2        # Pods are labelled app: checkout → matches NOTHING
  ports:
    - port: 80
      targetPort: 80        # container actually listens on 8080 → connection refused
# Result: an external IP that silently times out. No error is logged anywhere.
```

## Common Mistakes

- A `selector` that matches no Pods (typo or label drift), producing silent timeouts.
- `targetPort` not matching the container's actual listen port.
- Using `LoadBalancer` or `NodePort` for traffic that never leaves the cluster.
- Forgetting readiness probes, so the Service sends traffic to Pods that are still
  starting or already shutting down.
- Hardcoding a Service's ClusterIP instead of using its DNS name.
- Assuming a Service authenticates or authorizes callers — it does neither; add a
  NetworkPolicy and app-level auth.

## Production Tips

- Verify routing with `kubectl get endpoints <svc>` — an empty list means the selector
  matches no ready Pods. This is the first thing to check on a "Service not working" bug.
- Set `externalTrafficPolicy: Local` on external Services to preserve the client source
  IP and avoid an extra hop, at the cost of uneven distribution across nodes.
- Prefer a shared Ingress/Gateway over many `LoadBalancer` Services to control cost and
  centralize TLS.

## AI Review Checklist

- Does `spec.selector` match the labels on the target Pods exactly?
- Is `type` `ClusterIP` for internal traffic, with `LoadBalancer`/`NodePort` reserved for
  real external exposure?
- Does `targetPort` match the container's actual listen port?
- Do the backing Pods have a readiness probe so only ready Pods get traffic?
- Are ports named so Ingresses and other resources can reference them by name?
- Do callers use the Service DNS name rather than a hardcoded IP?

## Related

- `knowledge/kubernetes/08-ingress.md`
- `knowledge/kubernetes/05-deployments.md`
- `knowledge/kubernetes/04-pods.md`
- `knowledge/kubernetes/17-network-policies.md`
- `knowledge/kubernetes/13-statefulsets.md`
