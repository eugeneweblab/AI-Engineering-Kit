---
id: docker/27-troubleshooting
topic: docker
slug: troubleshooting
title: "Docker Troubleshooting"
type: doc
order: 27
status: ready
tags: [docker, troubleshooting, localhost, inspect, SIGKILL, arm64, ExitCode]
related: [docker/20-container-debugging, docker/16-logging, docker/17-resource-limits, docker/15-healthchecks, docker/24-monitoring]
when_to_use: "Read when a container will not build, will not start, exits unexpectedly, or misbehaves at runtime."
---
# Docker Troubleshooting

## Purpose

This document gives a systematic method for diagnosing broken containers: how to
read exit codes, why a container restart-loops, where logs and events live, and
how to inspect a container that will not stay up. It is written so an agent can
narrow a failure to its cause instead of changing things at random.

It complements [container debugging](20-container-debugging.md), which covers
interactive inspection of a *running* container. This doc focuses on the failure
itself — the container that exits, crashes, or never becomes healthy.

## Why It Matters

Container failures are noisy but low-signal by default: a container exits with code
`137` and no message, or restart-loops so fast you cannot attach to it. Guessing
wastes time and often makes things worse — people bump memory limits when the real
cause is a missing env var, or rebuild the image when the problem is the mount. A
repeatable diagnostic order turns a mysterious failure into a bounded search. The
cost of not having one is measured in hours of thrash and in fixes that mask the
symptom while the cause remains.

## Core Principles

- **Read the exit code first.** It is the cheapest signal. `137` = OOM/SIGKILL,
  `143` = SIGTERM, `139` = segfault, `1`/`2` = app error. It tells you which
  direction to look.
- **Separate "won't build" from "won't run".** Build failures are about the
  Dockerfile and context; run failures are about config, mounts, network, and
  resources. Do not debug one as the other.
- **Change one variable at a time.** Each change should test one hypothesis.
  Shotgun edits destroy your ability to attribute the fix.
- **Get inside or reproduce.** If it restart-loops, override the entrypoint to get
  a shell; if it exits, run it in the foreground and read the error.
- **Distinguish image from container from host.** The same image behaves
  differently across hosts due to arch, kernel, mounts, and limits.

## Best Practices

- Start with `docker ps -a` (state + exit code) and `docker logs <id>` (last
  output). For fatal startup errors the log usually names the cause.
- For a restart-looping container, break the loop: `docker run --entrypoint sh -it
  <image>` to get a shell without running the failing command.
- Check `docker inspect <id>` for `State.OOMKilled`, mount paths, env, and the
  resolved command — misconfigured mounts and missing env are common root causes.
- Read daemon-level failures with `docker events` and the host's journal; some
  failures (pull errors, OOM kills) surface there, not in app logs.
- For "connection refused" between containers, verify they share a
  [network](07-networks.md) and use the service name, not `localhost` — each
  container's `localhost` is itself.
- For "works locally, fails in CI/prod", suspect architecture (`arm64` vs `amd64`),
  a missing build arg, or a bind [mount](06-bind-mounts.md) that exists only on
  your machine.
- Reproduce with the exact image digest, not the tag, so you debug the same bytes
  that failed.

## Examples

**Good Example** — methodical: state, code, logs, then inspect

```bash
# 1. What state and exit code? 137 → killed by SIGKILL (usually OOM).
docker ps -a --filter name=api --format '{{.Names}}\t{{.Status}}'

# 2. What did it say before dying?
docker logs --tail 50 api

# 3. Confirm the hypothesis instead of guessing: was it OOM-killed?
docker inspect api --format '{{.State.OOMKilled}} {{.State.ExitCode}}'
# → "true 137": raise the memory limit or fix the leak — not a code bug.

# 4. Restart-loop? Get a shell without the failing entrypoint.
docker run --rm -it --entrypoint sh myorg/api:1.4.2
```

**Bad Example** — guessing and mutating state blindly

```bash
docker restart api          # "turn it off and on again" — no diagnosis, loops again
docker system prune -af     # nukes images/caches, destroys the evidence
docker run --memory=8g api  # bumps memory on a hunch; real cause was a bad env var
# no logs read, no exit code checked, nothing learned, problem returns
```

## Common Mistakes

- Not reading the exit code, so an OOM kill (137) gets debugged as an application
  crash.
- Running `docker system prune` while diagnosing, deleting the very image and logs
  you needed.
- Treating a build failure and a run failure the same way.
- Using `localhost` to reach another container instead of the service name on a
  shared [network](07-networks.md).
- Debugging a *tag* that has since changed instead of the exact digest that failed.
- Attaching to a restart-looping container instead of overriding the entrypoint to
  get a stable shell.
- Ignoring [healthcheck](15-healthchecks.md) status, then wondering why the
  orchestrator keeps killing a slow-starting container.

## Production Tips

- Keep logs flowing to an external sink ([logging](16-logging.md)) so a crashed,
  replaced container's last words survive.
- When a limit is the suspect, correlate with [monitoring](24-monitoring.md): an
  OOM-kill metric confirms in seconds what inspection guesses at.
- Capture a failing container's `inspect` and logs into the incident record before
  you remediate — remediation destroys the evidence.
- For heisenbugs that only fail in prod, run the prod image locally with prod-like
  limits and env, not your dev defaults.

## AI Review Checklist

- Does the diagnosis start from the exit code and logs, not a rebuild or restart?
- Is the failure classified as build vs run before any fix is attempted?
- For OOM/`137`, was `State.OOMKilled` actually confirmed before changing limits?
- Are inter-container connections using service names on a shared network, not
  `localhost`?
- Is the exact image digest reproduced, not a mutable tag?
- Is evidence (logs, `inspect`) captured before destructive remediation?
- Are only one variable changed per test iteration?

## Related

- `knowledge/docker/20-container-debugging.md`
- `knowledge/docker/16-logging.md`
- `knowledge/docker/17-resource-limits.md`
- `knowledge/docker/15-healthchecks.md`
- `knowledge/docker/24-monitoring.md`
