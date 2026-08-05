---
id: nodejs/07-buffers
topic: nodejs
slug: buffers
title: "Buffers"
type: doc
order: 7
status: ready
tags: [nodejs, buffers, Buffer, toString, equals, crypto.timingSafeEqual, timingSafeEqual, randomBytes]
related: [nodejs/06-streams, nodejs/05-file-system, nodejs/18-security, nodejs/20-memory-management, nodejs/16-error-handling]
when_to_use: "Read before allocating, slicing, encoding, or comparing raw binary data in Node.js."
---
# Buffers

## Purpose

This document defines how to handle raw binary data in Node.js with the `Buffer` class:
allocating it safely, encoding and decoding text, slicing it without corrupting data, and
comparing secrets without leaking timing. It is written so an agent can manipulate bytes
without introducing memory-disclosure bugs or multibyte-character corruption.

A `Buffer` is a fixed-length view over off-heap memory holding a sequence of bytes. It is
what streams, sockets, the file system, and crypto hand you. It is not a string and not a
JavaScript array — treating it like either is where the bugs start.

## Why It Matters

Buffers expose raw, uninitialized memory. The historical `new Buffer(size)` handed back
whatever bytes were previously in that memory — including other users' passwords and keys
— and shipped them if you did not overwrite them. That class of bug is why the constructor
is deprecated and why allocation API choice is a security decision, not a style one.
Beyond disclosure, buffers make it easy to slice a multibyte UTF-8 character in half, to
compare secrets in variable time, or to hold a giant `Buffer` resident when a stream would
do. Each of these is silent: the code runs, the data is wrong or the secret is leaked.

## Core Principles

- **Never use `new Buffer()` or `Buffer.allocUnsafe()` for data you will hand out.**
  `allocUnsafe` returns uninitialized memory that may contain old secrets. Use
  `Buffer.alloc(size)` (zero-filled) unless you immediately and fully overwrite it.
- **A `Buffer` slice shares memory.** `buf.subarray()`/`buf.slice()` returns a view over
  the same bytes, not a copy. Mutating one mutates the other. Copy with `Buffer.from(buf)`
  when you need isolation.
- **Encoding is explicit or wrong.** Always name the encoding (`'utf8'`, `'base64'`,
  `'hex'`). Defaults have bitten people; multibyte text needs whole-buffer decoding.
- **Compare secrets with `crypto.timingSafeEqual`.** `Buffer.compare`/`equals` and `===`
  short-circuit and leak length/content timing.
- **Buffers are byte-length, not character-length.** `buf.length` counts bytes;
  `Buffer.byteLength(str)` gives the byte length of a string.

## Best Practices

- Allocate with `Buffer.alloc(n)` for zeroed memory, or `Buffer.from(source)` to wrap
  existing data (string, array, ArrayBuffer). Reserve `allocUnsafe` for hot paths where
  you overwrite every byte before reading.
- Decode a whole buffer with `buf.toString('utf8')`; never decode arbitrary byte slices of
  multibyte text. If you must decode streamed chunks, use `string_decoder`'s
  `StringDecoder`, which holds partial multibyte sequences across chunks.
- Concatenate many buffers with `Buffer.concat([...], totalLength)` rather than repeated
  `+`/string coercion.
- Prefer streaming (see streams doc) over accumulating a large `Buffer`; a multi-hundred-MB
  buffer is a memory risk and cannot exceed `buffer.constants.MAX_LENGTH`.
- Zero out buffers holding secrets (`buf.fill(0)`) when done, to shrink the window they sit
  in memory.

## Examples

**Good Example** — safe allocation, explicit encoding, constant-time compare

```js
import { timingSafeEqual, randomBytes } from "node:crypto";

const token = randomBytes(32);              // cryptographically random, zero-fill not needed
const encoded = token.toString("base64url"); // explicit, URL-safe encoding

function tokensMatch(a, b) {
  // Both must be equal length for timingSafeEqual; check that first (length is not secret).
  if (a.length !== b.length) return false;
  // Constant-time: does not short-circuit on the first differing byte.
  return timingSafeEqual(a, b);
}
```

**Bad Example** — uninitialized memory and a timing-leaking compare

```js
const buf = Buffer.allocUnsafe(32); // may contain leftover secrets from freed memory
sendToClient(buf);                  // ...which you just disclosed if not overwritten

function tokensMatch(a, b) {
  return a.toString() === b.toString(); // === short-circuits → timing leak
  // Also: default toString() encoding is implicit; a sliced multibyte token corrupts.
}
```

## Common Mistakes

- Using `Buffer.allocUnsafe()` (or legacy `new Buffer()`) and shipping the bytes without
  overwriting them, disclosing arbitrary process memory.
- Assuming `buf.subarray()`/`slice()` copies — then being surprised when mutating the view
  changes the original.
- Comparing tokens, HMACs, or password hashes with `===` or `buf.equals`, leaking timing.
- Decoding a partial chunk of UTF-8 with `toString()`, splitting a multibyte character and
  producing replacement characters.
- Confusing byte length with character length when sizing buffers or offsets.
- Accumulating an unbounded `Buffer` from a stream instead of processing incrementally.

## Production Tips

- Prefer `base64url` over `base64` for anything that travels in URLs or headers — no `+`,
  `/`, or `=` to escape.
- When wrapping an `ArrayBuffer` from a Web API or worker, remember `Buffer.from(arrayBuffer)`
  shares memory; copy if the source may be reused or transferred.
- Set alerts on RSS: a steadily growing heap alongside large buffer use usually means a
  buffer that should have been a stream.

## AI Review Checklist

- Is untrusted or outbound memory allocated with `Buffer.alloc`, never `allocUnsafe`/`new Buffer`?
- Are all encodings named explicitly (`'utf8'`, `'base64url'`, `'hex'`)?
- Are secrets compared with `crypto.timingSafeEqual`, not `===`/`equals`?
- Is multibyte text decoded whole (or via `StringDecoder`), never sliced mid-character?
- Are slices copied with `Buffer.from` where the caller must not see later mutations?
- Is large binary data streamed rather than held in one big `Buffer`?

## Related

- `knowledge/nodejs/06-streams.md`
- `knowledge/nodejs/05-file-system.md`
- `knowledge/nodejs/18-security.md`
- `knowledge/nodejs/20-memory-management.md`
- `knowledge/nodejs/16-error-handling.md`
