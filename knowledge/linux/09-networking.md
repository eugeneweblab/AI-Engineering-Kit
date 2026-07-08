---
id: linux/09-networking
topic: linux
slug: networking
title: "Networking"
type: doc
order: 9
status: ready
tags: [linux, networking]
related: [linux/10-ssh, linux/21-firewall, linux/17-security, linux/19-debugging, linux/16-monitoring]
when_to_use: "Read before binding a port, configuring interfaces, or diagnosing connectivity on a Linux host."
---
# Networking

## Purpose

This document defines how to configure and reason about networking on a Linux host: what
address a service binds to, how to inspect connections and routes, how to resolve names,
and how to diagnose "it can't connect" without guessing. It is written so an agent can set
up and debug host networking without accidentally exposing a service or chasing the wrong
layer.

It is deliberately host-level (interfaces, sockets, ports, DNS, routing). Locking those
ports down is [firewall](21-firewall.md); securing remote shells is [ssh](10-ssh.md).

## Why It Matters

Networking mistakes are among the most dangerous a machine can make because they are
invisible locally and total remotely. Binding a database to `0.0.0.0` instead of
`127.0.0.1` exposes it to the whole internet while every local test still passes. A wrong
DNS assumption or a stale route produces intermittent failures that look like application
bugs. And connectivity problems span layers — link, IP, routing, DNS, firewall, the app —
so debugging without a method wastes hours at the wrong layer. Knowing which tool answers
which question is the difference between a two-minute diagnosis and an afternoon.

## Core Principles

- **The bind address is a security decision.** `127.0.0.1` is reachable only from the host;
  `0.0.0.0` (or `::`) is reachable from every interface. Bind to the narrowest address that
  works and never default to `0.0.0.0` for anything not meant to be public.
- **Debug bottom-up, layer by layer.** Link (`ip link`) -> address (`ip addr`) -> route
  (`ip route`) -> DNS (`resolvectl`/`dig`) -> port (`ss`) -> app. Confirm each layer before
  blaming the next.
- **DNS and reachability are separate failures.** "Name doesn't resolve" and "host doesn't
  answer" are different problems; test them separately (`dig` vs `ping`/`curl`).
- **`ip` and `ss` are the current tools.** `ifconfig`, `netstat`, and `route` are
  deprecated and often absent; use `ip` and `ss` (from iproute2).
- **A closed connection is not always the app.** "Connection refused" means nothing is
  listening; a timeout usually means a firewall or route is dropping packets silently. The
  two point at different fixes.

## Best Practices

- Bind internal services to `127.0.0.1` (or a private interface / Unix socket) and expose
  them only through an intended proxy or firewall rule. The cost is one config line; the
  benefit is not shipping an open database to the internet.
- Verify what is actually listening with `ss -tlnp` before and after a deploy; do not assume
  the config took effect.
- Resolve names with `getent hosts <name>` or `dig`, matching what glibc/NSS actually does,
  rather than assuming `/etc/hosts` or a specific resolver.
- Make network configuration declarative and persistent (NetworkManager, `systemd-networkd`,
  or netplan) instead of live `ip` commands that vanish on reboot.
- When a connection fails, capture the layer: `ping` for reachability, `ss` for listeners,
  `dig` for resolution, `curl -v` / `traceroute` for the path. Name the failing layer before
  changing anything.
- Prefer hostnames and service discovery over hard-coded IPs; IPs change and hard-coding
  them turns a re-IP into an outage.

## Examples

**Good Example** — bind to loopback, then verify what is exposed

```bash
# App config: listen only on the loopback interface
#   listen_address = 127.0.0.1:5432        # DB is unreachable from outside the host

# Confirm reality matches intent after (re)starting the service:
ss -tlnp                     # list TCP listeners with their bind address + process
# LISTEN  127.0.0.1:5432  users:(("postgres",...))   <- good: loopback only

# Diagnose a client that "can't connect", one layer at a time:
ping -c1 db.internal         # reachable at all?
dig +short db.internal       # does the name resolve, and to what?
ss -tlnp | grep :5432        # is anything actually listening there?
curl -v telnet://db.internal:5432   # can we open the socket, or refused/timeout?
```

**Bad Example** — exposed bind and guess-driven debugging

```bash
# App config
#   listen_address = 0.0.0.0:5432   # binds ALL interfaces -> DB open to the internet;
#                                   # local tests still pass, so the hole is invisible

# "It can't connect" — thrashing without isolating the layer:
sudo systemctl restart postgres     # restart-and-pray, no evidence gathered
sudo systemctl restart networking   # random layer, unrelated to the symptom
ping 8.8.8.8                        # tests the wrong host entirely
# never ran `ss` to see the bind address or `dig` to check resolution
```

## Common Mistakes

- Binding services to `0.0.0.0` by default, exposing internal ports to the network.
- Using deprecated `ifconfig`/`netstat`/`route` and getting different or missing output.
- Conflating DNS failure with connectivity failure and fixing the wrong one.
- Configuring interfaces with live `ip` commands that disappear on reboot.
- Hard-coding IP addresses that later change, turning a re-IP into an outage.
- Restarting services blindly instead of isolating the failing network layer first.

## Production Tips

- Treat "refused vs timeout" as a diagnosis: refused = wrong/no listener, timeout =
  firewall/route dropping. They lead to different fixes.
- Check MTU on tunnels and overlays — mismatched MTU causes large packets to hang while
  small ones (and pings) succeed, a classic "some requests work" mystery.
- Record listener inventory (`ss -tlnp`) in monitoring so a newly exposed port is caught.

## AI Review Checklist

- Are internal services bound to `127.0.0.1` / a private interface, not `0.0.0.0`?
- Is the actual bind address verified with `ss -tlnp` rather than assumed?
- Does debugging isolate the layer (link/IP/route/DNS/port/app) before changing anything?
- Are the current tools (`ip`, `ss`) used instead of deprecated `ifconfig`/`netstat`?
- Is network config persistent (networkd/NetworkManager/netplan), not ephemeral `ip` calls?
- Are hostnames/service discovery used instead of hard-coded IPs?

## Related

- `knowledge/linux/10-ssh.md`
- `knowledge/linux/21-firewall.md`
- `knowledge/linux/17-security.md`
- `knowledge/linux/19-debugging.md`
- `knowledge/linux/16-monitoring.md`
