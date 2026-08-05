---
id: docker/04-containers
topic: docker
slug: containers
title: "Docker Containers"
type: doc
order: 4
status: ready
tags: [docker, containers, SIGTERM, CMD, SIGKILL, ENTRYPOINT, drain, close]
related: [docker/03-images, docker/05-volumes, docker/15-healthchecks, docker/17-resource-limits, docker/20-container-debugging]
when_to_use: "Read before running, designing, or debugging a container's lifecycle, signal handling, or state."
---
# Docker Containers

## Purpose

This document defines the runtime side of Docker: what a container is, its
lifecycle, how signals and PID 1 work, and why containers must be stateless and
disposable. An [image](03-images.md) is the static artifact; a container is a
running (or stopped) instance of it. Getting the runtime model right is what makes
containers restart cleanly, shut down gracefully, and never lose data.

## Why It Matters

Containers fail in ways ordinary processes do not: they hang on shutdown because PID
1 ignores signals, they leave orphaned zombie processes, or they lose data because
someone wrote it to the container's ephemeral layer. Orchestrators send `SIGTERM`
and expect a clean exit within a grace period; a container that ignores it gets
`SIGKILL`ed mid-request, dropping in-flight work. Because containers are meant to be
killed and recreated constantly, any assumption of persistence is a latent bug.

## Core Principles

- **Containers are disposable.** Design so any container can be killed and replaced
  at any moment with no data loss and no manual fix-up.
- **State lives outside the container.** Anything that must survive a restart goes in
  a [volume](05-volumes.md) or an external service, never the writable layer.
- **PID 1 has special duties.** It must forward signals and reap zombie children.
  Most app runtimes do not do this, so run an init or exec the process directly.
- **One main concern per container.** A container is a process supervised by the
  orchestrator, not a host running many daemons.
- **The writable layer is ephemeral.** It exists only for the container's life and
  is deleted with `docker rm`.

## Best Practices

- Use exec form for `CMD`/`ENTRYPOINT` (`CMD ["node", "server.js"]`) so your process
  becomes PID 1 and receives signals — shell form wraps it in `/bin/sh -c`, which
  swallows `SIGTERM`.
- Handle `SIGTERM` in the app: stop accepting new work, drain in-flight requests,
  close connections, exit. This is what makes rolling deploys graceful.
- Add `--init` (or Tini) when the process cannot reap children itself, to avoid
  zombie accumulation.
- Run as a non-root user (`USER app`) and drop capabilities; a container escape from
  root is a host compromise. See [18-security](18-security.md).
- Set resource limits (`--memory`, `--cpus`) so one container cannot starve the host.
  See [17-resource-limits](17-resource-limits.md).
- Define a [healthcheck](15-healthchecks.md) so the platform knows when the container
  is actually ready, not merely started.
- Prefer `--rm` for throwaway runs and treat `docker exec` as a debugging tool, not a
  deployment step. See [20-container-debugging](20-container-debugging.md).

## Examples

**Good Example** — exec form, non-root, graceful shutdown

```dockerfile
FROM node:20-slim
WORKDIR /app
COPY --chown=app:app . .
USER app                       # not root: an escape is far less dangerous
# Exec form → node is PID 1 and receives SIGTERM directly.
CMD ["node", "server.js"]
```

```js
// The app cooperates with the orchestrator's shutdown signal.
process.on("SIGTERM", async () => {
  server.close();             // stop accepting new connections
  await db.drain();           // finish in-flight work, then exit cleanly
  process.exit(0);
});
```

**Bad Example** — shell form, root, writes state into the container

```dockerfile
FROM node:latest
WORKDIR /app
COPY . .
# Shell form: the real process is a child of /bin/sh, which does NOT forward
# SIGTERM. The container hangs until the orchestrator SIGKILLs it mid-request.
CMD node server.js && echo "started"
# Runs as root by default → container escape == host root.
# App writes uploads to /app/data (the ephemeral layer) → lost on every restart.
```

## Common Mistakes

- Using shell-form `CMD`, so the app never receives `SIGTERM` and shutdown is a hard
  kill that drops in-flight requests.
- Writing persistent data (uploads, DB files, logs to keep) to the container layer,
  losing it on `docker rm` or the next deploy.
- Running as root because it was the default, turning any escape into host root.
- Running an SSH server or cron inside the app container instead of treating the
  container as a single supervised process.
- No `--init`, so a process that spawns children leaks zombies over time.
- Relying on `docker exec` fixes that vanish the moment the container is recreated.

## Production Tips

- Set the orchestrator's termination grace period to match your real drain time; too
  short and clean shutdowns get `SIGKILL`ed anyway.
- Log to stdout/stderr and let the platform collect it, rather than writing log files
  inside the container. See [16-logging](16-logging.md).
- Use `docker stats` and platform metrics to confirm containers respect their limits
  and restart cleanly under load.
- Make startup idempotent and fast so the orchestrator can recreate containers
  freely.

## AI Review Checklist

- Is `CMD`/`ENTRYPOINT` in exec form so the app is PID 1 and gets signals?
- Does the app handle `SIGTERM` and drain gracefully?
- Is all persistent state in a volume or external service, not the container layer?
- Does the container run as a non-root user with reduced capabilities?
- Are memory/CPU limits and a healthcheck defined?
- Is `--init` used when the process spawns children it cannot reap?

## Related

- `knowledge/docker/03-images.md`
- `knowledge/docker/05-volumes.md`
- `knowledge/docker/15-healthchecks.md`
- `knowledge/docker/17-resource-limits.md`
- `knowledge/docker/20-container-debugging.md`
