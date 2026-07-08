---
id: wordpress/06-security
topic: wordpress
slug: security
title: "WordPress Security"
type: doc
order: 6
status: ready
tags: [wordpress, security]
related: []
when_to_use: "Read before handling input, endpoints, or authentication in a WordPress project."
---
# WordPress Security

## Purpose

This document defines the security principles for developing WordPress applications.

Security is a fundamental engineering responsibility rather than a final review step.

Every feature, endpoint, integration, and administrative interface should be designed with security in mind from the beginning.

---

## Core Principle

Never trust external input.

Every value originating from:

- users;
- browsers;
- APIs;
- databases;
- uploaded files;
- cookies;
- query parameters;
- request headers;

should be considered untrusted until validated.

---

## Security Mindset

Every implementation should answer the following questions:

- Who can access this feature?
- What data can they modify?
- What data can they read?
- How is the request verified?
- How is the input validated?
- How is the output protected?

Security begins before writing code.

---

## Authentication

Authentication verifies identity.

Always rely on the existing WordPress authentication system unless project requirements specify otherwise.

Examples:

- logged-in users;
- application passwords;
- JWT authentication;
- OAuth providers;
- SSO integrations.

Never implement custom authentication without a strong justification.

---

## Authorization

Authentication does not imply authorization.

Always verify permissions before allowing operations.

Examples:

```php
current_user_can( 'edit_posts' );

current_user_can( 'manage_options' );

current_user_can( 'edit_user', $user_id );
```

Every privileged action should perform an explicit capability check.

---

## Nonce Verification

Protect state-changing requests with nonces.

Examples:

- form submissions;
- AJAX requests;
- admin actions;
- REST requests when applicable.

Never rely solely on hidden form fields.

---

## Input Validation

Validate every input.

Examples:

- required fields;
- string length;
- numeric ranges;
- email format;
- URLs;
- UUIDs;
- enum values;
- dates.

Reject invalid input as early as possible.

---

## Data Sanitization

Sanitize data before storing it.

Examples:

```php
sanitize_text_field()

sanitize_email()

sanitize_key()

sanitize_title()

sanitize_file_name()
```

Store clean data whenever possible.

---

## Output Escaping

Escape data immediately before rendering.

Examples:

```php
esc_html()

esc_attr()

esc_url()

wp_kses_post()
```

The escaping function depends on the output context.

Never escape data when storing it.

---

## SQL Safety

Prefer WordPress APIs.

When direct SQL is necessary:

- use `$wpdb->prepare()`;
- validate identifiers;
- avoid dynamic SQL generation;
- minimize privileges.

Never concatenate untrusted input into SQL queries.

---

## REST API Security

Every endpoint should verify:

- authentication;
- authorization;
- request validation;
- response filtering.

Permission callbacks are mandatory.

Sensitive fields should never be returned unless explicitly required.

---

## File Upload Security

Before accepting uploads verify:

- file type;
- MIME type;
- file size;
- upload permissions;
- destination directory.

Never trust the client-provided filename or extension.

---

## Cross-Site Scripting (XSS)

Prevent XSS by:

- validating input;
- sanitizing stored content;
- escaping rendered output;
- limiting allowed HTML.

Output context determines the correct escaping strategy.

---

## Cross-Site Request Forgery (CSRF)

Protect state-changing actions with:

- nonces;
- capability checks;
- request validation.

Do not rely on HTTP method alone.

---

## Sensitive Data

Never expose:

- passwords;
- API keys;
- tokens;
- private configuration;
- internal identifiers when unnecessary.

Store secrets outside the repository whenever possible.

---

## Logging

Log security-relevant events.

Examples:

- failed authentication;
- permission failures;
- suspicious requests;
- repeated validation failures;
- external API failures.

Logs should support investigation without exposing sensitive information.

---

## Dependencies

Regularly review:

- plugins;
- themes;
- Composer packages;
- npm packages;
- external services.

Remove unused dependencies.

Update supported dependencies promptly after reviewing compatibility.

---

## AI Execution Checklist

## Investigation

☐ Identify protected resources.

☐ Review authentication.

☐ Review authorization.

☐ Review data flow.

☐ Review external integrations.

---

## Implementation

☐ Validate every input.

☐ Sanitize stored data.

☐ Escape rendered output.

☐ Verify capabilities.

☐ Verify nonces.

☐ Protect SQL queries.

☐ Secure file uploads.

---

## Verification

☐ Verify unauthorized access.

☐ Verify permission checks.

☐ Verify validation.

☐ Verify escaping.

☐ Review logs.

☐ Review exposed data.

---

## Common Mistakes

Avoid:

Trusting client input.

Skipping capability checks.

Skipping nonce verification.

Escaping data before storage.

Returning excessive API data.

Hardcoding secrets.

Using direct SQL without prepared statements.

Ignoring uploaded file validation.

---

## Completion Criteria

A feature is considered secure when:

- authentication is correct;
- authorization is enforced;
- every input is validated;
- stored data is sanitized;
- rendered output is escaped;
- sensitive information is protected;
- common attack vectors have been considered.

---

## Summary

Security is achieved through multiple layers of protection rather than a single defensive mechanism.

Well-designed WordPress applications validate every request, authorize every action, protect every output, and minimize the impact of potential failures.