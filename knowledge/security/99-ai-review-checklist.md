---
id: security/99-ai-review-checklist
topic: security
slug: ai-review-checklist
title: "Security AI Review Checklist"
type: doc
order: 99
status: ready
tags: [security, ai-review-checklist]
related: [security/29-security-review, security/28-owasp-top10, security/09-input-validation, security/04-authorization, security/98-production-checklist]
when_to_use: "Read before reviewing a diff or generating code that touches auth, input handling, secrets, or network surfaces."
---
# Security AI Review Checklist

## Purpose

This is the checklist an AI agent runs while reviewing or writing code, before that code
merges. Unlike the [production checklist](98-production-checklist.md), which gates the
deployed system, this gates the *diff*: it catches the security defects an agent can find
by reading the change and its immediate context. Every item is answerable from the code in
front of you.

## Why It Matters

Agents generate plausible code fast, and plausible code hides insecure defaults — a
concatenated query, a missing authorization check, a logged secret, a trusted client value.
These slip past review because they look normal. A concrete per-diff checklist forces the
agent to look for the specific shapes of failure instead of skimming for "looks fine."
The cost is a few minutes per review; the payoff is not shipping a class of known bugs.

## How To Use

- Run these questions against the diff and the functions it calls, not the whole codebase.
- Any "no" or "can't tell" is a review comment, not a silent pass. "Can't tell" means the
  code does not make the safe behavior evident — that itself is a finding.
- Prefer pointing at the exact line and the fix over a general warning.

## Trust Boundaries and Input

- [ ] Is every external input (body, query, header, param, file, upstream response) validated against an allowlist schema?
- [ ] Is validation at the boundary, before the data reaches business logic or storage?
- [ ] Are numeric/enum/length bounds enforced, not just type?
- [ ] Is no client-supplied value (role, price, userId, isAdmin) trusted for a security decision?

## Injection

- [ ] Are all SQL/NoSQL queries parameterized — zero string concatenation with input?
- [ ] Do OS/shell calls use argument arrays and avoid `shell: true`/interpolation?
- [ ] Is user data never passed to `eval`, template compilation, or dynamic `require`/import?
- [ ] Is output encoded for its exact sink (HTML body, attribute, JS, URL, header)?

## AuthN / AuthZ

- [ ] Does every new endpoint/handler enforce authentication and an explicit authorization check?
- [ ] Is object-level ownership verified (this user may act on *this* resource)?
- [ ] Is the default deny, so a missing check fails closed rather than open?
- [ ] Are auth errors uniform in message and timing (no account-existence leak)?

## Secrets and Data

- [ ] Are there zero hardcoded secrets, keys, or tokens in the diff?
- [ ] Are credentials, tokens, session IDs, and PII kept out of logs and error messages?
- [ ] Are secrets read from a manager/env, not written to source or config files?
- [ ] Is sensitive data encrypted where the design requires it, using a vetted library?

## Errors and Responses

- [ ] Do client-facing errors omit stack traces, SQL, file paths, and internal detail?
- [ ] Does the code fail closed on exceptions (deny access, not grant it)?
- [ ] Are constant-time comparisons used for secrets/tokens/HMACs?

## Dependencies

- [ ] Does the diff avoid adding an unvetted, unmaintained, or typosquat-suspect package?
- [ ] Are new dependencies pinned in the lockfile?

## Examples

**Good** — the reviewable shape a checklist wants to see

```ts
// Parameterized query + explicit ownership check + generic error.
async function getInvoice(req: Req) {
  const id = InvoiceId.parse(req.params.id);        // validated at boundary
  const inv = await db.query(
    "SELECT * FROM invoices WHERE id = $1", [id],    // no string concat
  );
  if (!inv || inv.ownerId !== req.user.id) {         // object-level authz, default deny
    throw new NotFound("Invoice not found");         // uniform, leaks nothing
  }
  return inv;
}
```

**Bad** — every checklist item fails, yet it "works"

```ts
async function getInvoice(req: Req) {
  const inv = await db.query(
    `SELECT * FROM invoices WHERE id = ${req.params.id}`, // SQL injection
  );
  // no authz check → any user reads any invoice (IDOR)
  return inv; // and on error, the raw DB message reaches the client
}
```

## Common Mistakes

- Approving a diff because tests pass; these defects rarely have failing tests.
- Reviewing only the changed lines and missing that a called helper skips authorization.
- Accepting "can't tell" as a pass instead of requesting the code make safety evident.
- Flagging a problem without naming the concrete fix, so it gets waved through.

## AI Review Checklist

- Did I answer each question above against this specific diff and its callees?
- Did I convert every "no"/"can't tell" into a line-anchored comment with a fix?
- Did I check the highest-impact classes first: injection, broken authz, secret exposure?
- Did I confirm the change fails closed on error rather than open?

## Related

- `knowledge/security/29-security-review.md`
- `knowledge/security/28-owasp-top10.md`
- `knowledge/security/09-input-validation.md`
- `knowledge/security/04-authorization.md`
- `knowledge/security/98-production-checklist.md`
