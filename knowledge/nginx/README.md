---
id: nginx/readme
topic: nginx
slug: readme
title: "Nginx Engineering Standards"
type: index
order: -1
status: ready
tags: [nginx, readme, Host, see, fit, docs]
related: []
when_to_use: "Read first when starting any nginx work, to see how this section's docs fit together."
---
# Nginx Engineering Standards

## Purpose

This section defines the engineering standards and configuration practices for operating
Nginx as a web server, reverse proxy, and load balancer. Nginx behavior is driven almost
entirely by its declarative configuration, so most reliability, security, and performance
outcomes come down to how server blocks, location matching, proxying, and caching are
written and ordered.

The objective is a consistent approach to production Nginx: correct server and location
block design, robust reverse proxying and load balancing, effective caching and
compression, and modern protocol support (HTTP/2, HTTP/3). It extends to the hardening and
operations that matter at scale — TLS, security headers, rate limiting, authentication,
logging, monitoring, high availability, and debugging — as well as integration patterns
for application backends, WebSockets, FastCGI/PHP-FPM, and Docker.

These standards apply to both human operators and AI coding assistants, so that generated
configuration follows the same security, caching, and proxy-correctness rules as
hand-authored configs.

---

## Scope

This documentation covers:

- Installation and configuration structure
- Server blocks and location blocks
- Reverse proxy and load balancing
- Static file serving, caching, and compression
- HTTP/2, HTTP/3, and SSL/TLS
- Security, rate limiting, and authentication
- Logging, monitoring, and performance
- Proxying applications, WebSockets, FastCGI, and PHP-FPM
- Docker, debugging, and high availability
- Production operations, tooling, and engineering principles

---

## Learning Path

Study the documents in the following order.

### Foundations

- 00. Overview
- 01. Installation
- 02. Configuration
- 03. Server Blocks
- 04. Location Blocks

### Traffic Handling

- 05. Reverse Proxy
- 06. Load Balancing
- 07. Static Files
- 08. Caching
- 09. Compression

### Protocols & TLS

- 10. HTTP/2
- 11. HTTP/3
- 12. SSL/TLS

### Security & Access

- 13. Security
- 14. Rate Limiting
- 15. Authentication

### Application Integration

- 19. Proxying Applications
- 20. WebSockets
- 21. FastCGI
- 22. PHP-FPM
- 23. Docker

### Operations

- 16. Logging
- 17. Monitoring
- 18. Performance
- 24. Debugging
- 25. Production
- 26. Best Practices
- 27. High Availability
- 28. Tooling
- 29. Troubleshooting
- 30. Engineering Principles

### Verification

- 98. Production Checklist
- 99. AI Review Checklist
- 100. Common Anti-Patterns

---

## Engineering Principles

Every Nginx configuration should satisfy the following principles:

- Understand location matching order; specificity and precedence drive routing correctness.
- Terminate TLS with modern ciphers and enforce HTTPS and security headers by default.
- Set correct proxy headers (`Host`, `X-Forwarded-*`) so backends see accurate requests.
- Cache deliberately, with explicit keys and invalidation, not by accident.
- Bound the edge: apply rate limiting, connection limits, and timeouts.
- Compress responses where it helps and avoid double-compressing binary content.
- Keep configuration modular and DRY with includes and upstreams.
- Test config with `nginx -t` and reload gracefully; never hot-edit blindly.
- Log meaningfully and monitor upstream health, latency, and error rates.
- Design for high availability; no single Nginx node should be a hard dependency.

---

## Intended Audience

These standards are intended for:

- DevOps and Platform Engineers
- Site Reliability Engineers
- Backend Engineers deploying services
- Infrastructure and Network Engineers
- Security Engineers
- AI Coding Assistants
- Code Reviewers

---

## Summary

Following these standards keeps Nginx fast, secure, and reliable at the edge — so it
strengthens the systems behind it rather than becoming a single point of failure.
