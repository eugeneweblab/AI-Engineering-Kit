---
id: aws/readme
topic: aws
slug: readme
title: "AWS Engineering Standards"
type: index
order: -1
status: ready
tags: [aws]
related: []
when_to_use: "Read first when starting any AWS work, to see how this section's docs fit together."
---
# AWS Engineering Standards

## Purpose

This section defines the engineering standards for provisioning and operating
infrastructure on Amazon Web Services. Its goal is narrow and practical: resources that are
secure by default, least-privilege, cost-aware, and reproducible from code rather than
click-configured in the console.

AWS defaults optimize for "it works," not "it is safe." A resource created from a wizard or
a copied snippet is frequently public, over-permissioned, unencrypted, or un-tagged, and
those mistakes do not fail loudly. The docs cover the global substrate, the identity control
plane, compute and storage, networking, operations, and the cross-cutting disciplines of
security and cost that apply to every service.

These standards apply to both human developers and AI coding assistants.

---

## Scope

This documentation covers:

- Global infrastructure: Regions and Availability Zones
- Identity and access management (IAM)
- Compute: EC2, Lambda, ECS, EKS, Auto Scaling, load balancing
- Storage and data: S3, RDS, ECR
- Networking: VPC, Route 53, CloudFront, ACM
- Operations: CloudWatch, CloudTrail, Secrets Manager, Parameter Store
- Messaging: SQS, SNS, EventBridge
- Cost optimization, security, and monitoring
- The Well-Architected Framework and engineering principles

---

## Learning Path

Study the documents in the following order.

## Foundations

- 00. Overview
- 01. Global Infrastructure
- 02. IAM
- 30. Engineering Principles

## Compute

- 03. EC2
- 10. Elastic Load Balancer
- 11. Auto Scaling
- 12. Lambda
- 13. API Gateway
- 18. ECS
- 19. EKS
- 20. ECR

## Storage & Data

- 04. S3
- 05. RDS

## Networking

- 06. VPC
- 07. Route 53
- 08. CloudFront
- 09. ACM

## Operations & Messaging

- 14. CloudWatch
- 15. CloudTrail
- 16. Secrets Manager
- 17. Parameter Store
- 21. SQS
- 22. SNS
- 23. EventBridge

## Cross-Cutting Guidance

- 24. Cost Optimization
- 25. Security
- 26. Monitoring
- 27. Production
- 28. Best Practices
- 29. Well-Architected Framework

## Verification

- 98. Production Checklist
- 99. AI Review Checklist
- 100. Common Anti-Patterns

---

## Engineering Principles

Every AWS change should satisfy the following principles:

- Provision everything as infrastructure-as-code; never click-configure in the console.
- Grant least privilege to every identity, role, and security group; treat `*` as a red flag.
- Encrypt data at rest and in transit by default.
- Tag and budget from day one; treat cost as a design constraint.
- Design for failure by spreading workloads across Availability Zones.
- Prefer managed services over self-managed equivalents unless there is a concrete reason.
- Keep environments in separate accounts so a mistake in one cannot reach another.
- Lock away the root account behind MFA and use it almost never.
- Consult the specific service doc rather than guessing at API shapes.

---

## Intended Audience

These standards are intended for:

- Cloud and Platform Engineers
- DevOps and SRE Engineers
- Backend Engineers deploying to AWS
- Security Engineers
- AI Coding Assistants
- Code Reviewers

---

## Summary

Following these standards keeps AWS infrastructure secure, least-privilege, cost-aware, and
reproducible, so a single misconfiguration cannot quietly expose or break the system.
