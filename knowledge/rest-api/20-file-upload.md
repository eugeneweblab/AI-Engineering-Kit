---
id: rest-api/20-file-upload
topic: rest-api
slug: file-upload
title: "File Upload"
type: doc
order: 20
status: ready
tags: [rest-api, file-upload]
related: [rest-api/08-validation, rest-api/24-security, rest-api/09-error-handling, rest-api/16-authorization, rest-api/25-performance]
when_to_use: "Read before building any endpoint that accepts user-uploaded files — avatars, documents, media, or imports."
---
# File Upload

## Purpose

This document defines how to accept files over HTTP safely and at scale: choosing a
transfer mechanism, enforcing size and type limits, validating content, storing files
outside the app, and streaming large payloads. File upload is where untrusted binary
data enters your system, so it is treated as a security surface, not a convenience.

Upload answers "how do I let a client send me bytes without letting them exhaust,
poison, or breach my server?".

## Why It Matters

An upload endpoint hands an attacker a way to push arbitrary bytes into your
infrastructure. Without limits, a single request can fill your disk or exhaust memory
(a denial-of-service in one line). Without content validation, a file named `avatar.png`
can actually be an executable, an HTML page that runs script when viewed, or a
zip-bomb. Without access control on retrieval, private documents leak through guessable
URLs. Uploads also strain the request pipeline: buffering a 2 GB file in memory to
"just parse it" will take a server down. The correct design streams, validates, and
isolates — because the input is hostile and large by nature.

## Core Principles

- **Cap size before you read the body.** Enforce a maximum via `Content-Length` checks
  and a hard streaming limit, so an oversized upload is rejected early with `413`,
  never buffered whole.
- **Never trust the client-supplied name or type.** The filename and `Content-Type`
  are attacker-controlled. Detect the real type from magic bytes and derive a safe,
  server-generated storage name.
- **Store files outside the application and the web root.** Put bytes in object storage
  (S3/GCS) or a dedicated volume — never in a path the server will execute or serve
  raw. This neutralizes uploaded scripts.
- **Stream, do not buffer.** Pipe the upload straight to storage (or scan it in chunks)
  so memory use stays flat regardless of file size.
- **Access control belongs on retrieval too.** An upload is only as private as its
  download path. Serve files through authorization checks or short-lived signed URLs,
  not permanent public links.

## Best Practices

- Use `multipart/form-data` for browser uploads and mixed form fields; use a raw body
  (`PUT` with a binary `Content-Type`) for single-file API clients.
- Set explicit limits: max file size, max number of files, and max total request size.
  Return `413 Payload Too Large` when exceeded.
- Allow-list accepted types by verifying magic bytes (e.g. via `file-type`), not the
  extension or the `Content-Type` header. Reject anything not on the list.
- Generate the stored filename yourself (UUID + validated extension). Strip path
  separators to prevent path-traversal (`../../etc/passwd`).
- For large files, prefer **pre-signed direct-to-storage uploads**: the client uploads
  straight to object storage using a short-lived URL your API grants, so bytes never
  transit your app servers.
- Run untrusted files through a malware scan and process images with a hardened
  library (re-encode to strip embedded payloads) before serving them back.
- Serve downloads with `Content-Disposition: attachment` and a correct `Content-Type`,
  plus `X-Content-Type-Options: nosniff`, so browsers do not execute the content.

## Examples

**Good Example** — streamed, size-capped, content-validated upload

```ts
// POST /avatars (multipart). Limit enforced by the parser BEFORE the body is read.
const upload = multer({ limits: { fileSize: 5 * 1024 * 1024, files: 1 } }); // 5 MB, 1 file

router.post("/avatars", requireAuth, upload.single("file"), async (req, res) => {
  const buf = req.file.buffer;

  // Verify the REAL type from magic bytes; the client's Content-Type is ignored.
  const kind = await fileTypeFromBuffer(buf);
  const allowed = { "image/png": "png", "image/jpeg": "jpg" };
  const ext = allowed[kind?.mime ?? ""];
  if (!ext) throw new HttpError(415, "Only PNG or JPEG allowed");

  // Server-generated name → no path traversal, no attacker-controlled filename.
  const key = `avatars/${req.user.id}/${randomUUID()}.${ext}`;
  await storage.put(key, buf, { contentType: kind.mime });

  res.status(201).json({ url: await storage.signedUrl(key, "10m") }); // scoped, expiring
});
```

**Bad Example** — trusts the client, buffers everything, writes to web root

```ts
router.post("/avatars", async (req, res) => {
  const { filename, data } = req.body; // full file buffered in memory: OOM risk

  // Uses the CLIENT's filename verbatim → "../../public/index.html" overwrites files,
  // and a ".png" that is really HTML gets served and executed by the browser.
  fs.writeFileSync(`./public/uploads/${filename}`, Buffer.from(data, "base64"));

  res.json({ url: `/uploads/${filename}` }); // public, permanent, unauthenticated
});
```

## Common Mistakes

- No size limit, allowing a single request to exhaust memory or disk (DoS).
- Validating the extension or `Content-Type` header instead of the actual bytes.
- Writing uploads into the web root or an executable path, enabling remote code
  execution via a disguised script.
- Using the client filename directly, opening path-traversal and overwrite attacks.
- Buffering entire files in memory rather than streaming to storage.
- Public, guessable download URLs with no authorization on retrieval.
- Returning the raw uploaded image without re-encoding, passing through embedded
  exploits.

## Production Tips

- Offload big files to pre-signed direct uploads; your API only issues and later
  confirms the upload, keeping app servers thin.
- Scan asynchronously and mark files `pending` until the scan clears; serve only
  `clean` files.
- Store an integrity checksum (SHA-256) at upload time to detect corruption and
  deduplicate identical files.

## AI Review Checklist

- Is a hard size limit enforced before the body is fully read, returning `413`?
- Is the file type verified by magic bytes and allow-listed, not by header/extension?
- Is the stored filename server-generated and free of path separators?
- Are files stored outside the web root / execution path?
- Is the upload streamed rather than buffered whole in memory?
- Are downloads authorized (or served via short-lived signed URLs) and sent with
  `nosniff` + `Content-Disposition: attachment`?

## Related

- `knowledge/rest-api/08-validation.md`
- `knowledge/rest-api/24-security.md`
- `knowledge/rest-api/09-error-handling.md`
- `knowledge/rest-api/16-authorization.md`
- `knowledge/rest-api/25-performance.md`
