---
id: docker/11-multi-stage-builds
topic: docker
slug: multi-stage-builds
title: "Multi Stage Builds"
type: doc
order: 11
status: ready
tags: [docker, multi-stage-builds]
related: [docker/08-dockerfile, docker/09-image-optimization, docker/10-buildkit, docker/18-security, docker/03-images]
when_to_use: "Read before building any image for a compiled or bundled app, so build tooling and source never ship to production."
---
# Multi Stage Builds

## Purpose

This document defines how to use **multi-stage builds** to separate the environment that
*builds* an application from the environment that *runs* it. A build stage carries
compilers, dev dependencies, and source; the final stage copies only the finished artifact
into a minimal base. This is the single highest-leverage technique for
[image optimization](09-image-optimization.md) and reducing attack surface.

One Dockerfile, multiple `FROM` lines. Each `FROM` starts a new stage; the last stage is
the image you ship. Earlier stages are discarded — nothing in them reaches production
unless you explicitly `COPY --from` it.

## Why It Matters

Without multi-stage builds, everything needed to compile the app also ships to production:
the compiler toolchain, the entire `node_modules` including devDependencies, the source
code, and often build-time secrets. That is hundreds of MB of pull time and a large CVE
surface for code that never runs. It is also a leak risk — source and tokens end up in a
layer someone can pull. Multi-stage builds make the boundary explicit and enforced by
default: the runtime image contains only what you copy into it.

## Core Principles

- **Each `FROM` begins a new, independent stage.** Only the final stage becomes the image;
  earlier stages exist solely to produce artifacts.
- **`COPY --from=<stage>` is the only bridge.** Nothing crosses from a build stage to the
  final image unless you copy it explicitly, so tooling and source stay behind.
- **Name stages (`FROM x AS build`) for clarity and reuse.** Named stages are easy to
  reference and let you target one with `--target`.
- **The final base should be minimal.** Copy the artifact onto `distroless`, `-slim`, or
  `scratch` so the runtime carries no shell or compiler.
- **BuildKit runs independent stages in parallel** and skips stages the target does not
  need — structure stages to exploit that; see [BuildKit](10-buildkit.md).

## Best Practices

- Put all build tooling (compilers, `-dev` packages, full dependency tree) in a builder
  stage and copy only the compiled binary, bundle, or pruned `node_modules` forward.
- Name every stage and, for languages that produce a static binary (Go, Rust), copy onto
  `scratch` or `distroless` for a tiny, shell-less runtime.
- Keep the dependency-install step early in the builder stage with the manifest copied
  first, preserving the cache across source edits (see [Dockerfile](08-dockerfile.md)).
- Use a `--target` to build intermediate stages in CI (e.g. a `test` stage) without
  shipping them.
- Copy with correct ownership (`COPY --from=build --chown=appuser:appuser ...`) and switch
  to a non-root `USER` in the final stage.
- Combine with [BuildKit](10-buildkit.md) cache and secret mounts so the builder stage is
  both fast and leak-free.

## Examples

**Good Example** — Go binary compiled in a builder, shipped on distroless

```dockerfile
# syntax=docker/dockerfile:1

# --- build stage: has the Go toolchain, source, and module cache ---
FROM golang:1.23 AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN --mount=type=cache,target=/go/pkg/mod go mod download   # cached across builds
COPY . .
RUN CGO_ENABLED=0 go build -o /app/server ./cmd/server

# --- final stage: only the compiled binary, no compiler, no shell ---
FROM gcr.io/distroless/static:nonroot
COPY --from=build /app/server /server   # the ONLY thing that ships
USER nonroot:nonroot                    # unprivileged runtime
EXPOSE 8080
ENTRYPOINT ["/server"]
# Result: a ~15 MB image with no toolchain, no source, minimal CVE surface.
```

**Bad Example** — single stage ships the entire build environment

```dockerfile
FROM golang:1.23            # ~800 MB base with full toolchain
WORKDIR /src
COPY . .                    # all source ships to production
RUN go build -o server ./cmd/server
# The compiler, module cache, source code, and a fat base all remain in the
# final image. It is ~50x larger than needed and exposes source + build tools.
ENTRYPOINT ["/src/server"]
```

## Common Mistakes

- Shipping a single-stage image that carries the compiler, devDependencies, and source.
- Forgetting `COPY --from`, so the final stage is missing the artifact and fails at start.
- Choosing a heavy final base (full distro) that undoes the size win of separating stages.
- Copying artifacts as root and never setting a non-root `USER` in the final stage.
- Not naming stages, making `COPY --from=0` positional and fragile to reorder.
- Copying the whole builder `/app` (including intermediate junk) instead of just the
  artifact.

## Production Tips

- Add a `test` or `lint` stage and run it via `--target` in CI so quality gates share the
  build cache but never ship.
- Pin every stage's base image by tag or digest so both build and runtime are reproducible.
- Pair with a CVE scan on the final image; a distroless final stage typically yields near-
  zero OS-package findings. See [Security](18-security.md).
- For interpreted languages, copy a pruned production dependency set (`npm ci --omit=dev`
  in the builder) forward rather than reinstalling in the final stage.

## AI Review Checklist

- Does the build use separate stages, with the final stage on a minimal base?
- Is `COPY --from` used to bring *only* the artifact into the final image?
- Are compilers, dev dependencies, and source absent from the final stage?
- Are stages named (`AS build`) rather than referenced by index?
- Does the final stage run as a non-root `USER`?
- Are all stage base images pinned to a tag or digest?

## Related

- `knowledge/docker/08-dockerfile.md`
- `knowledge/docker/09-image-optimization.md`
- `knowledge/docker/10-buildkit.md`
- `knowledge/docker/18-security.md`
- `knowledge/docker/03-images.md`
