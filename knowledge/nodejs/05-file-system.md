---
id: nodejs/05-file-system
topic: nodejs
slug: file-system
title: "File System"
type: doc
order: 5
status: ready
tags: [nodejs, file-system, rename, resolve, writeFileSync, ENOENT, EACCES, writeFile]
related: [nodejs/06-streams, nodejs/02-event-loop, nodejs/07-buffers, nodejs/18-security, nodejs/16-error-handling]
when_to_use: "Read before reading, writing, watching, or building paths to files — especially when any part of the path comes from user input."
---
# File System

## Purpose

This document defines how to work with the file system in Node.js safely and without
blocking: the promise-based `fs` API, streaming large files, atomic writes, path
handling, and the path-traversal risks that turn a file read into a security hole. An
agent that follows it can do file I/O that is non-blocking, correct across platforms,
and safe against hostile input.

Node exposes the file system through `node:fs`. It offers three flavors: promise-based
(`fs/promises`, preferred), callback-based, and synchronous (`*Sync`). Which one you pick
determines whether you block the event loop.

## Why It Matters

File I/O is where two of Node's biggest failure modes meet. First, using synchronous
reads on a hot path blocks the single [event loop](02-event-loop.md) and stalls the whole
process. Second, building a file path from user input without validation lets an attacker
escape the intended directory (`../../etc/passwd`) and read or overwrite arbitrary files
— one of the most common and severe web vulnerabilities. Add unclosed file descriptors
(a slow resource leak) and non-atomic writes (corruption on crash), and file handling
becomes a frequent source of both outages and breaches.

## Core Principles

- **Use async `fs/promises` for everything but startup.** Synchronous calls block the
  loop; reserve `*Sync` for CLIs and boot scripts that do nothing concurrently.
- **Stream large files; never buffer what you cannot bound.** Reading a big file fully
  into memory risks OOM and blocks; pipe it instead (see [streams](06-streams.md)).
- **Never trust a path from user input.** Resolve it and confirm it stays inside an
  allowed base directory before touching disk.
- **Writes should be atomic.** Write to a temp file and `rename` it into place, so a
  crash mid-write cannot leave a half-written, corrupt file.
- **Release resources.** Close file handles (prefer the handle-scoped promise API); a
  descriptor leak eventually exhausts the process limit and crashes it.

## Best Practices

- Build paths with `node:path` (`path.join`, `path.resolve`) — never string
  concatenation — so separators and `..` segments are handled correctly on every OS.
- Validate user-supplied paths: `resolve` the full path, then check it
  `startsWith(baseDir + path.sep)`. Reject anything that escapes the base.
- For large or streaming data use `createReadStream`/`createWriteStream` (or
  `pipeline`), which apply backpressure and bound memory.
- Handle `ENOENT`, `EACCES`, and `EEXIST` explicitly; do not assume a file exists or is
  writable. Avoid the `existsSync`-then-open race — just open and catch the error.
- Always specify an encoding (`"utf8"`) when you want a string; otherwise `readFile`
  returns a raw [Buffer](07-buffers.md).
- Prefer the file-handle API (`fs.open` → `handle.readFile()` → `handle.close()` in a
  `finally`) when doing multiple operations on one file, so the descriptor is scoped.

## Examples

**Good Example** — async, path-validated, atomic write

```js
import { writeFile, rename } from "node:fs/promises";
import path from "node:path";

const BASE = path.resolve("/srv/uploads");

async function saveUpload(userPath, data) {
  // Resolve then confine: reject anything that escapes the upload directory.
  const target = path.resolve(BASE, userPath);
  if (!target.startsWith(BASE + path.sep)) {
    throw new Error("Path traversal blocked"); // stops ../../ escapes
  }
  const tmp = `${target}.${process.pid}.tmp`;
  await writeFile(tmp, data);   // write to temp first
  await rename(tmp, target);    // atomic swap: no half-written file on crash
}
```

**Bad Example** — blocking, unvalidated, non-atomic

```js
import fs from "node:fs";

function saveUpload(userPath, data) {
  // Concatenated path lets `../../etc/passwd` escape the intended directory.
  const target = "/srv/uploads/" + userPath;
  // Synchronous write blocks the event loop AND can leave a partial file on crash.
  fs.writeFileSync(target, data);
}
```

## Common Mistakes

- Using `readFileSync`/`writeFileSync` in request handlers, blocking the event loop.
- Concatenating user input into a path instead of resolving and confining it — classic
  path traversal.
- Loading a large file entirely into memory instead of streaming it.
- Checking `existsSync` before opening (a TOCTOU race); just attempt the op and handle
  the error.
- Overwriting a file in place, so a crash mid-write corrupts it.
- Leaking file descriptors by never closing handles opened with `fs.open`.

## Production Tips

- Set and monitor the process file-descriptor limit (`ulimit -n`); a slow handle leak
  shows up as `EMFILE` under load.
- Watch directories with `fs.watch` cautiously — its events differ across platforms and
  can fire duplicates; debounce and re-stat rather than trusting the event alone.
- Keep temp files on the same filesystem/volume as their target so the final `rename`
  stays atomic (a cross-device rename is a copy and is not atomic).

## AI Review Checklist

- Are all file operations async (`fs/promises`), with no `*Sync` on request paths?
- Are user-supplied paths resolved and confined to an allowed base directory?
- Are large files streamed rather than read fully into memory?
- Are writes made atomic via temp-file-plus-rename?
- Are `ENOENT`/`EACCES`/`EEXIST` handled instead of assumed away?
- Are file handles closed (ideally in a `finally`) so descriptors do not leak?

## Related

- `knowledge/nodejs/06-streams.md`
- `knowledge/nodejs/02-event-loop.md`
- `knowledge/nodejs/07-buffers.md`
- `knowledge/nodejs/18-security.md`
- `knowledge/nodejs/16-error-handling.md`
