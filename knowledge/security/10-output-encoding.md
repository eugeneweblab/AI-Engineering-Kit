---
id: security/10-output-encoding
topic: security
slug: output-encoding
title: "Output Encoding"
type: doc
order: 10
status: ready
tags: [security, output-encoding, v-html, "javascript:", https, dangerouslySetInnerHTML, http, steal]
related: [security/11-xss, security/09-input-validation, security/13-sql-injection, security/20-csp]
when_to_use: "Read before rendering any dynamic data into HTML, JS, SQL, shell, URLs, or other interpreted output."
---
# Output Encoding

## Purpose

This document defines how to safely place untrusted data into an output context — HTML, HTML
attributes, JavaScript, URLs, CSS, SQL, shell, JSON, headers. Output encoding (a.k.a.
escaping) transforms data so the receiving interpreter treats it as *data*, never as *code
or markup*. It is the primary defense against injection at the point of use.

Encoding is the mirror image of [input validation](09-input-validation.md): validation
decides whether to accept input; encoding decides how to render it safely. Injection bugs
live at the *output* boundary, so this is where they are truly fixed.

## Why It Matters

Injection happens when a parser cannot tell your data from your instructions. `'; DROP TABLE`
is dangerous only because a string got concatenated into SQL; `<script>` is dangerous only
because it landed in an HTML parser unescaped. Correct encoding removes that ambiguity: the
interpreter sees a literal string. The reason this matters so much is that the *same* piece
of data is safe in one context and lethal in another — a value that is fine in an HTML body
can break out of a `<script>` block or a URL. Encoding must therefore be chosen per sink, at
the moment of output, or the defense silently does not apply.

## Core Principles

- **Encode for the destination context, at the point of output.** HTML body, HTML attribute,
  JS, URL, and CSS each need *different* escaping. Encoding once for the wrong context is no
  protection.
- **Prefer parameterization / structured APIs over string escaping.** Parameterized queries,
  argument arrays, and DOM APIs keep data and code in separate channels so no escaping is
  needed. Manual escaping is the fallback, not the default.
- **Never build interpreted strings by concatenation.** SQL, shell, and HTML assembled with
  `+` or template strings from untrusted input are injection by construction.
- **Let the framework encode; do not defeat it.** Modern template engines auto-escape.
  Bypasses (`dangerouslySetInnerHTML`, `|safe`, `v-html`, raw output) turn the safety off —
  each use needs a specific, justified reason.
- **Encode late, store raw.** Store the original value; encode when rendering. Encoding on the
  way in corrupts data and still fails for other sinks.

## Best Practices

- **SQL:** use parameterized queries / prepared statements or a query builder that binds
  parameters. Never interpolate values into the query text.
- **Shell:** pass arguments as an array to `execFile`/`spawn` without a shell; never
  concatenate into a shell string. See [command injection](14-command-injection.md).
- **HTML:** rely on the template engine's auto-escaping; for rich text, sanitize with a
  vetted allowlist library (e.g. DOMPurify) rather than escaping by hand.
- **JavaScript / JSON:** serialize with `JSON.stringify` (and escape `<`/`>`/`&` when
  embedding in `<script>`); never hand-build JS from user data.
- **URLs:** use `encodeURIComponent` for each component and validate the scheme
  (`http`/`https` only) to block `javascript:` and `data:` URLs.
- **Headers / redirects:** strip CR/LF and validate against an allowlist to prevent response
  splitting and open redirects.

## Examples

**Good Example** — parameterized query and context-correct HTML escaping

```ts
// SQL: value travels in a separate channel; the driver never parses it as SQL.
const rows = await db.query(
  "SELECT * FROM users WHERE email = $1", // placeholder, not string concatenation
  [email],
);

// HTML: the template engine escapes for the HTML-body context automatically.
res.render("profile", { bio: user.bio }); // `<` becomes &lt; → rendered as text, not markup
```

**Bad Example** — concatenation and escaping-off bypass

```ts
// SQL injection: input is spliced into the query text and parsed as code.
const rows = await db.query(
  `SELECT * FROM users WHERE email = '${email}'`, // ' OR '1'='1 breaks out
);

// XSS: framework escaping is explicitly bypassed with no sanitization.
element.innerHTML = user.bio; // <img src=x onerror=steal()> executes
```

## Common Mistakes

- Building SQL, shell, or HTML with string concatenation / template literals.
- Encoding for one context (HTML body) and injecting into another (JS, attribute, URL).
- Using `innerHTML`, `dangerouslySetInnerHTML`, `|safe`, or `v-html` on untrusted data.
- Escaping on input and storing the escaped value, corrupting data and missing other sinks.
- Sanitizing rich HTML with a hand-rolled regex instead of a vetted, allowlist sanitizer.
- Forgetting URL/scheme validation, allowing `javascript:` links to execute.
- Passing user data into shell strings instead of an argument array.

## Production Tips

- Enable a strict [Content Security Policy](20-csp.md) as defense-in-depth so an encoding
  miss cannot easily execute injected script.
- Add lint rules that flag raw-HTML sinks and string-built SQL so bypasses require an
  explicit, reviewed override.
- Keep sanitizer libraries updated; bypasses are found and patched regularly.

## AI Review Checklist

- Is every dynamic value encoded for its *specific* output context at render time?
- Are all SQL statements parameterized (no concatenated values)?
- Are shell commands built from argument arrays, never shell strings?
- Is framework auto-escaping left on, with each bypass justified and sanitized?
- Is untrusted HTML run through a vetted allowlist sanitizer rather than manual escaping?
- Are URLs component-encoded and schemes restricted to `http`/`https`?
- Is data stored raw and encoded on output, not encoded on input?

## Related

- `knowledge/security/11-xss.md`
- `knowledge/security/09-input-validation.md`
- `knowledge/security/13-sql-injection.md`
- `knowledge/security/20-csp.md`
