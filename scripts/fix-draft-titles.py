#!/usr/bin/env python3
"""Fix acronym casing in DRAFT titles (frontmatter + H1). Ready docs untouched."""
import os, re

KB = "/Users/devrocketteam2/Downloads/active_projects/AI-Engineering-Kit/knowledge"

ACRONYMS = {w: w.upper() for w in (
    "api seo sql ssl tls http https jwt rbac dto cqrs ddd orm cli css html jsx tsx "
    "ui ux ci cd aws ec2 s3 rds vpc iam sqs sns ecs eks ecr acm cdn dns ip tcp udp "
    "grpc json jsonb xml yaml npm pwa spa ssr csr isr wcag i18n lfs psr oop mvc sre "
    "iac url uri ttl cors csrf xss svg fpm ide cpu gpu sdk crud acid dml ddl lts"
).split()}

SPECIAL = {
    "graphql": "GraphQL", "openapi": "OpenAPI", "postgresql": "PostgreSQL",
    "mysql": "MySQL", "nodejs": "Node.js", "nextjs": "Next.js", "nestjs": "NestJS",
    "javascript": "JavaScript", "typescript": "TypeScript", "github": "GitHub",
    "gitlab": "GitLab", "woocommerce": "WooCommerce", "wordpress": "WordPress",
    "dataloader": "DataLoader", "codeql": "CodeQL", "dependabot": "Dependabot",
    "cloudfront": "CloudFront", "cloudwatch": "CloudWatch", "cloudtrail": "CloudTrail",
    "eventbridge": "EventBridge", "fastcgi": "FastCGI", "http2": "HTTP/2",
    "http3": "HTTP/3", "route53": "Route 53", "n1": "N+1", "codespaces": "Codespaces",
}

def titleize(slug):
    words = slug.split("-")
    out = []
    for w in words:
        if w in SPECIAL:
            out.append(SPECIAL[w])
        elif w in ACRONYMS:
            out.append(ACRONYMS[w])
        else:
            out.append(w[:1].upper() + w[1:])
    return " ".join(out)

fixed = 0
for topic in sorted(os.listdir(KB)):
    tdir = os.path.join(KB, topic)
    if not os.path.isdir(tdir):
        continue
    for fn in sorted(os.listdir(tdir)):
        if not fn.endswith(".md"):
            continue
        path = os.path.join(tdir, fn)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        status = re.search(r"^status:\s*(\S+)", text, re.M)
        slug = re.search(r"^slug:\s*(\S+)", text, re.M)
        if not status or status.group(1) != "draft" or not slug:
            continue
        new_title = titleize(slug.group(1))
        new = re.sub(r'^title:\s*".*"$', f'title: "{new_title}"', text, count=1, flags=re.M)
        new = re.sub(r'^#\s+.*$', f"# {new_title}", new, count=1, flags=re.M)
        if new != text:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new)
            fixed += 1

print(f"draft titles fixed={fixed}")
