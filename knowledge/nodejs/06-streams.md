---
id: nodejs/06-streams
topic: nodejs
slug: streams
title: "Streams"
type: doc
order: 6
status: ready
tags: [nodejs, streams]
related: [nodejs/07-buffers, nodejs/05-file-system, nodejs/09-http, nodejs/16-error-handling, nodejs/20-memory-management]
when_to_use: "Read before moving large files, HTTP bodies, or any dataset too big to hold in memory at once."
---
# Streams

## Purpose

This document defines how to process data incrementally in Node.js using streams:
readable, writable, duplex, and transform streams, and how to connect them safely.
It is written so an agent can move gigabytes of data through a process that only ever
holds kilobytes in memory, without losing data or leaking file descriptors.

A stream is a sequence of chunks that arrives over time. You use one whenever the data
is larger than you want resident in RAM, or arrives too slowly to block on — files, HTTP
request/response bodies, sockets, compression, and encryption are all stream-shaped.

## Why It Matters

The naive alternative — `readFileSync` then process then write — loads the entire
payload into memory. A 2 GB upload handled that way spikes RSS by 2 GB per concurrent
request and takes the process down under load. Streams keep memory flat regardless of
payload size. But streams trade that win for a hard requirement: **backpressure**. If a
fast source outruns a slow sink and you ignore the signal, unbounded data buffers in
memory and you have reinvented the crash you were avoiding. Getting stream wiring and
error handling right is the difference between a service that scales and one that OOMs
at 3 a.m.

## Core Principles

- **Prefer `pipeline()` over `.pipe()`.** `pipeline` (from `node:stream/promises`)
  propagates errors, awaits completion, and destroys every stream on failure. Bare
  `.pipe()` does none of that and leaks the source on downstream errors.
- **Respect backpressure.** When `writable.write()` returns `false`, stop writing until
  the `'drain'` event. `pipeline` handles this for you; manual loops must not.
- **Every stream needs an error handler.** An unhandled `'error'` on a stream throws and
  can crash the process. There is no such thing as a stream that "can't fail".
- **Destroy streams you abandon.** If you stop reading early, call `.destroy()` to close
  the underlying resource (fd, socket). Otherwise it leaks until GC, or never.
- **Choose object mode deliberately.** Byte streams carry `Buffer`/string chunks;
  object mode carries arbitrary values one at a time. Do not mix them on one pipe.

## Best Practices

- Use `pipeline(source, ...transforms, dest)` for every multi-stage flow; `await` it so
  callers see completion and errors.
- For transforming data, subclass `Transform` (or use `Transform` with a `transform`
  function) rather than buffering the whole stream and mapping an array.
- Set a `highWaterMark` only when profiling shows the default (16 KB / 16 objects) is
  wrong; do not cargo-cult large buffers.
- Convert to and from other paradigms with the built-ins: `Readable.from(iterable)`,
  `stream.Readable.toWeb()`, and async iteration (`for await (const chunk of readable)`).
- Handle client disconnects on HTTP: when the response stream errors or closes, the
  `pipeline` rejects — clean up the source there.
- Use `stream.finished(s)` when you need to know a stream ended but did not build the
  pipe yourself.

## Examples

**Good Example** — `pipeline` gzips a file with backpressure and error handling for free

```js
import { pipeline } from "node:stream/promises";
import { createReadStream, createWriteStream } from "node:fs";
import { createGzip } from "node:zlib";

async function gzipFile(src, dest) {
  // pipeline awaits completion, honors backpressure across all three stages,
  // and destroys every stream if any one errors — no fd or memory leak.
  await pipeline(
    createReadStream(src),
    createGzip(),
    createWriteStream(dest),
  );
}
```

**Bad Example** — bare `.pipe()` swallows errors and leaks the source

```js
import { createReadStream, createWriteStream } from "node:fs";
import { createGzip } from "node:zlib";

function gzipFile(src, dest) {
  createReadStream(src)
    .pipe(createGzip())
    .pipe(createWriteStream(dest));
  // No error handler: a disk error rejects nowhere and can crash the process.
  // If the writable errors, the readable is never destroyed — the fd leaks.
  // The caller has no way to know when (or whether) the write finished.
}
```

## Common Mistakes

- Using `.pipe()` without `stream.finished`/`pipeline`, so errors and completion vanish.
- Ignoring the `false` return of `write()` and the `'drain'` event, buffering unbounded
  data in memory.
- Reading a whole stream into an array or concatenated `Buffer` "just to transform it",
  defeating the point of streaming.
- Forgetting to `.destroy()` a stream you stop consuming early (e.g. after an HTTP range
  request), leaking file descriptors.
- Attaching an `'error'` handler to only one stream in a chain and assuming it covers the
  rest — each stream emits its own errors.
- Mixing object-mode and byte-mode streams on the same pipe, producing `[object Object]`
  or type errors.

## Production Tips

- Set a timeout/abort on long-lived streams (`AbortController` is accepted by
  `pipeline`'s options) so a stalled peer cannot pin a connection forever.
- Log stream errors with the resource identity (path, request id) — a bare `EPIPE` with
  no context is unactionable.
- Under load, watch RSS and event-loop lag: a memory climb that tracks request count is
  the classic signature of a missing backpressure or missing `destroy`.

## AI Review Checklist

- Is every multi-stage flow built with `pipeline`, not chained `.pipe()`?
- Does every stream (or the `pipeline` wrapping them) have error handling?
- Is backpressure respected — no manual `write()` loop that ignores the `false` return?
- Are abandoned streams explicitly `.destroy()`ed to release fds and sockets?
- Is the code streaming end-to-end, not buffering the whole payload into memory first?
- Are object-mode and byte-mode streams kept separate on each pipe?

## Related

- `knowledge/nodejs/07-buffers.md`
- `knowledge/nodejs/05-file-system.md`
- `knowledge/nodejs/09-http.md`
- `knowledge/nodejs/16-error-handling.md`
- `knowledge/nodejs/20-memory-management.md`
