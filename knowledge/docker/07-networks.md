---
id: docker/07-networks
topic: docker
slug: networks
title: "Networks"
type: doc
order: 7
status: ready
tags: [docker, networks, EXPOSE, POSTGRES_PASSWORD_FILE, reachable, containers, publishing]
related: [docker/04-containers, docker/12-docker-compose, docker/18-security, docker/22-production, docker/15-healthchecks]
when_to_use: "Read before wiring containers together, publishing ports, or deciding what a service should be reachable from."
---
# Networks

## Purpose

This document defines how containers talk to each other and to the outside world:
network drivers, service discovery by name, publishing ports, and network segmentation.
It is written so an agent can connect services correctly without exposing internal
components to the internet.

The default question a network setup must answer is: *who is allowed to reach this
container, and by what name?* Getting that wrong either breaks connectivity or opens a
database straight to the public internet.

## Why It Matters

Networking decides your attack surface. Every published port is a door; every container
on the same network can reach every other one. The two most common failures are
opposites: a service that cannot find its dependency because it is on the wrong network,
and a database that is one `ports:` line away from the open internet. Both are invisible
until they bite — the first at startup, the second when it is scanned and breached. A
deliberate network topology is cheaper than either outage.

## Core Principles

- **User-defined bridge networks give DNS-based service discovery; the default bridge
  does not.** On a user-defined network, containers reach each other by service name.
  Never rely on container IPs — they change on restart.
- **Publishing a port (`-p`/`ports:`) exposes it to the host and beyond.** If a service
  is only consumed by other containers, it needs no published port at all.
- **`EXPOSE` documents intent; it does not publish.** It is metadata for readers and
  tools, not a firewall rule and not a port mapping.
- **Networks are the isolation boundary.** Containers can only talk if they share a
  network. Segment tiers (frontend, backend, data) into separate networks.
- **Bind published ports to the narrowest interface.** `127.0.0.1:5432:5432` exposes to
  localhost only; `5432:5432` exposes on all host interfaces, often the public one.

## Best Practices

- Create explicit user-defined networks per tier rather than dropping everything on the
  default bridge; you get DNS names and a real isolation boundary.
- Publish only the ports the outside world needs — typically just the reverse proxy or
  API gateway. Databases, caches, and internal services stay unpublished.
- When you must publish a host-only service, bind it to `127.0.0.1` so it is not reachable
  from other machines.
- Put data stores on an `internal: true` network that has no route to the outside; only
  app containers that also join that network can reach them.
- Reference dependencies by service name (`postgres:5432`), never by hardcoded IP.
- Use `host` networking only for special cases (high-throughput or port-scanning tools);
  it removes isolation and port remapping and is Linux-only.

## Examples

**Good Example** — segmented networks, database not published

```yaml
# docker-compose.yml — only the proxy is reachable from outside;
# the database sits on an internal network with no route to the host.
services:
  proxy:
    image: nginx:1.27
    ports:
      - "127.0.0.1:8080:80"   # bound to localhost, not every interface
    networks: [frontend]

  api:
    build: .
    networks: [frontend, backend]  # bridges the tiers, no published port

  db:
    image: postgres:16
    environment: { POSTGRES_PASSWORD_FILE: /run/secrets/db_pw }
    networks: [backend]      # reachable only by api, addressed as "db"

networks:
  frontend: {}
  backend:
    internal: true           # no gateway to the outside world
```

**Bad Example** — everything published, addressed by IP

```yaml
services:
  api:
    build: .
    ports:
      - "3000:3000"
  db:
    image: postgres:16
    ports:
      - "5432:5432"          # database exposed on ALL host interfaces → public
    # No user-defined network, so the api must reach the db by a brittle
    # container IP instead of the name "db", and DNS discovery is unavailable.
```

## Common Mistakes

- Publishing a database or cache port to the host "to connect a GUI," leaving it open to
  the internet.
- Using `-p 5432:5432` instead of `-p 127.0.0.1:5432:5432` and exposing a local-only
  service network-wide.
- Expecting DNS name resolution on the default bridge network, where it is unavailable.
- Hardcoding container IPs, which change on every recreate.
- Confusing `EXPOSE` with publishing and assuming the port is reachable (or that it is a
  security control).
- Putting all services on one flat network so a compromised frontend can reach the database.

## Production Tips

- Terminate ingress at one place (reverse proxy / load balancer) and keep every other
  service unpublished behind it.
- Treat the network topology as part of your security review: enumerate published ports
  and confirm each one is intentional. See [Security](18-security.md).
- In orchestrators (Kubernetes, Swarm), enforce the same segmentation with network
  policies; the Compose network model is the local rehearsal of production isolation.

## AI Review Checklist

- Are containers on a user-defined network so they can resolve each other by name?
- Is every published port actually required by something outside the container network?
- Are host-only services bound to `127.0.0.1` rather than all interfaces?
- Are data stores on an `internal` network with no route to the host?
- Are dependencies referenced by service name instead of hardcoded IP?
- Is `EXPOSE` being mistaken for a publish or a security control?

## Related

- `knowledge/docker/04-containers.md`
- `knowledge/docker/12-docker-compose.md`
- `knowledge/docker/18-security.md`
- `knowledge/docker/22-production.md`
- `knowledge/docker/15-healthchecks.md`
