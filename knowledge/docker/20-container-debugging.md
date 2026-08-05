---
id: docker/20-container-debugging
topic: docker
slug: container-debugging
title: "Container Debugging"
type: doc
order: 20
status: ready
tags: [docker, container-debugging, exec, OOMKilled, container, netshoot, inspect, ExitCode]
related: [docker/16-logging, docker/15-healthchecks, docker/04-containers, docker/17-resource-limits, docker/27-troubleshooting]
when_to_use: "Read when a container crashes, restarts, hangs, or behaves differently than it did locally."
---
# Container Debugging

## Purpose

This document defines how to diagnose a misbehaving container: reading exit codes and
logs, inspecting a live or dead container, and getting a shell into an image that has no
shell. It is written so an agent can find root cause without guessing or mutating the
image under test.

Debugging a container is different from debugging a process on a host. The filesystem,
network, environment, and process namespace are all isolated, so the first job is to
observe from the right vantage point rather than assume the host's view applies.

## Why It Matters

A container that "works on my machine" but crash-loops in production is the single most
common Docker failure, and the wrong debugging move makes it worse: `docker exec`-ing in,
installing tools, and hand-editing files produces a fix that vanishes on the next
restart and cannot be reproduced. Effective debugging is about reading the evidence the
runtime already gives you — exit codes, logs, `inspect`, events — before you change
anything. Time spent here is recovered many times over in avoided false fixes.

## Core Principles

- **Read the exit code first.** It tells you the failure class: `137` = SIGKILL (often
  OOM), `143` = SIGTERM, `1` = app error, `126/127` = command not found/executable.
- **Observe before you mutate.** A running container is evidence. Changing it destroys
  the state you need to understand the failure.
- **The container is disposable; fixes belong in the image or config.** Anything you
  `exec` in and change is gone on restart. Fix the Dockerfile or compose file.
- **Bring your tools to the container, not tools into the image.** Debug a minimal image
  from the outside (a sidecar/ephemeral debug container), don't fatten the image.
- **Reproduce, don't speculate.** Recreate the failing condition (same env, limits,
  read-only fs) locally before proposing a cause.

## Best Practices

- Start with `docker ps -a` and `docker inspect` to read exit code, `OOMKilled`,
  restart count, and the last state.
- Read `docker logs --tail=100 --timestamps <id>`; for crash loops add `--previous`
  semantics by checking the exited container, not the restarted one.
- For a distroless/no-shell image, attach an ephemeral debug container sharing its
  namespaces: `docker debug` or `docker run --pidns/--net container:<id>` with a tools
  image, rather than adding a shell to the image.
- Use `docker exec -it <id> <shell>` only on images that already ship a shell, and only
  to read state — never to apply a "fix".
- Override the entrypoint to inspect a broken build:
  `docker run -it --entrypoint sh myimage` to poke at the filesystem.
- Check `docker events` and `docker stats` to catch OOM kills and resource starvation in
  real time.
- Reproduce with the production constraints: same `--memory`, `--read-only`, and env, or
  you will "fix" a bug that only exists without them.

## Examples

**Good Example** — diagnose from the outside, fix the image

```bash
# 1. Exit code and OOM flag tell you the failure class before you read a single log line.
docker inspect --format='{{.State.ExitCode}} OOM={{.State.OOMKilled}}' myapp
# -> 137 OOM=true   (SIGKILL from the OOM killer)

# 2. Confirm from logs of the *exited* container, with timestamps.
docker logs --tail=50 --timestamps myapp

# 3. Distroless image has no shell? Attach tools via a shared debug container.
docker run -it --rm --pid=container:myapp --net=container:myapp \
  nicolaka/netshoot   # inspect processes/network without touching the image

# 4. Root cause is a low memory limit -> fix it in the compose file, not by exec.
#    (deploy.resources.limits.memory: 512M)
```

**Bad Example** — mutate the container, lose the fix

```bash
# Exec in and "fix" the running container...
docker exec -it myapp sh
# ...install tools into the running container (gone on restart)...
apk add curl && vi /app/config.json   # edits vanish; not reproducible
# Restart wipes every change; the bug returns and no one knows why.
docker restart myapp
```

## Common Mistakes

- Ignoring the exit code and reading logs blind — `137` immediately points at OOM, saving
  a long hunt.
- `exec`-ing in to edit files or install packages, producing a fix that disappears on
  restart and cannot be reproduced.
- Reading logs of the *restarted* container instead of the crashed one, so the actual
  error is already gone.
- Adding a shell, `curl`, or `vim` to the production image just to debug it, permanently
  enlarging attack surface.
- Debugging without the production memory limit or read-only filesystem, then being
  surprised the "fix" fails in prod.
- Relying on `docker attach` (which shares stdin and can kill the process) instead of
  `logs`/`exec`.

## Production Tips

- Ship structured logs to stdout/stderr (see [logging](16-logging.md)) so you rarely need
  to enter a container at all.
- Keep a vetted debug image (e.g. `netshoot`) available so responders never `apk add` into
  production containers.
- Ensure healthchecks (see [healthchecks](15-healthchecks.md)) surface the failing state so
  the orchestrator's events already name the problem.
- Retain crashed containers (`restart` policy that does not immediately remove) long enough
  to inspect them.

## AI Review Checklist

- Did the diagnosis start from the exit code and `OOMKilled` flag, not guesswork?
- Are logs read from the crashed/previous container, not the restarted one?
- Is debugging done from outside (ephemeral/sidecar container), leaving the image
  unchanged?
- Is the proposed fix in the Dockerfile/compose file, not an `exec`-time edit?
- Was the failure reproduced with production limits and read-only settings?
- Does the image stay minimal — no debug tools added permanently?

## Related

- `knowledge/docker/16-logging.md`
- `knowledge/docker/15-healthchecks.md`
- `knowledge/docker/04-containers.md`
- `knowledge/docker/17-resource-limits.md`
- `knowledge/docker/27-troubleshooting.md`
