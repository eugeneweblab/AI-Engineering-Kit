<!-- Captured during the trial described in docs/trials/README.md. The agent was
given the repository path and one instruction: read AGENTS.md and follow it. -->

# Protocol log

Format: `ACTION | file or query | why | what it told you`

## Protocol bootstrap

READ | /Users/devrocketteam2/Downloads/active_projects/AI-Engineering-Kit/AGENTS.md | Instructed entrypoint; CLAUDE.md redirects here | Retrieval loop: grep `knowledge/INDEX.json` / `knowledge/SIGNALS.json` (never read them whole — ~310k/~260k tokens), filter `status: "ready"`, rank matches: repo/diff signal > `when_to_use` > topic/tags > title words; read the chosen doc in full; self-verify against the topic's `98`/`99`/`100` checklists; never cite a `status: draft` stub.
BASH | `ls knowledge/` + `wc -l INDEX.json SIGNALS.json` | Learn which topics exist before guessing paths | Topics include nextjs, prisma, kubernetes, aws, seo, react, workflows. INDEX.json 38.7k lines, SIGNALS.json 42.6k lines — one entry per line, so grep is the right access mode.

## T1 — Next.js 16 Server Action, rename product, immediate for the editor

GREP | `"revalidateTag":` in SIGNALS.json | Symbol from the task ("cached under tag") → governing docs | nextjs/08-rendering-strategies, nextjs/10-caching, nextjs/28-best-practices.
GREP | `"updateTag":` in SIGNALS.json | Suspected the Next 16 read-your-writes API exists in the KB | nextjs/09-data-fetching, nextjs/10-caching, nextjs/100-common-antipatterns, nextjs/11-server-actions, nextjs/28-best-practices — confirms `updateTag` is a real, documented API here.
GREP | `"refresh":` in SIGNALS.json | Third candidate invalidation API | Only security/08-oauth (token refresh) — not the Next.js router API; the caching doc covers it instead.
GREP | `"id": "nextjs/10-caching"` etc. in INDEX.json | Check `status` before relying on any of them | All four candidates are `status: ready`; 10-caching and 11-server-actions carry `applies_to: [app-router]`, which matches the task.
READ | knowledge/nextjs/11-server-actions.md (full) | Chosen by `when_to_use`: "Read before implementing form submissions or data mutations with Server Actions" | An action is a public HTTP endpoint: authorise first, validate FormData with a schema, scope the write to the caller (`updateMany` + `count === 0`), then invalidate. Good example ends with `updateTag(...)` for read-your-writes.
READ | knowledge/nextjs/10-caching.md (full) | Owns the invalidation-API choice | Decision table: `revalidateTag(tag, "max")` = mark stale, nobody waiting; `updateTag(tag)` = expire **and** refresh in the same request, Server Actions only, "the person who made the change is looking at the page"; `refresh()` = client router only. Since Next 16 the 2nd arg of `revalidateTag` is **required**. Its good example is literally `renameProduct`: `updateTag(\`product:${id}\`)` + `revalidateTag('products', 'max')`.
READ | knowledge/nextjs/100-common-antipatterns.md (full) | Step 4 self-verification for the two Next.js tasks | #5 params/cookies are async in 15+ and the sync shim is **gone in 16**; #6 actions must validate + authorise; #11 mutations must revalidate; #2 keep db/secrets server-only.
GREP | knowledge/nextjs/99-ai-review-checklist.md, 98-production-checklist.md | Named self-verify step | "Is `revalidatePath`/`revalidateTag` called after mutations…", "Does every Server Action validate its input with a schema before use?" — both satisfied by t1.ts.
GREP | `updateTag` in knowledge/nextjs/09-data-fetching.md | Cross-check the invalidation granularity rule | "After a write, invalidate exactly what changed … not the whole path, not the whole site."

## T2 — Prisma 7 + PostgreSQL

GREP | `prisma/schema.prisma` in SIGNALS.json (`stack` section) | Repository-signal lookup, the strongest match class | `when: prisma/schema.prisma` → prisma/02-schema, prisma/06-client, prisma/05-migrations.
GREP | `prisma.config.ts` / `prisma/config` in SIGNALS.json | The task asks "any config file Prisma 7 requires" | prisma/27-tooling and prisma/01-installation own it.
GREP | `"PrismaClient":` in SIGNALS.json | Symbol for the shared-instance file | prisma/06-client (plus 100-antipatterns, 12/13/14/19/20).
GREP | INDEX.json for prisma/01-installation, 27-tooling, 06-client, 02-schema | Confirm `status` | All `ready`.
READ | knowledge/prisma/01-installation.md (full) | `when_to_use`: adding Prisma / setting up DATABASE_URL and the Client | v7 shape: datasource carries **no** `url`; generator provider is `prisma-client` (`prisma-client-js` removed); `output` required; URL moves to `prisma.config.ts` via `defineConfig`/`env` from `"prisma/config"`; pin CLI and client to one version; `postinstall: prisma generate`.
READ | knowledge/prisma/27-tooling.md (full) | Owns generator/datasource/CLI config | Confirms both generator fields required in v7 and that a `url` in `datasource` is a **validation error**, not a deprecation; `migrations.seed` lives in the config file.
READ | knowledge/prisma/06-client.md (full) | `when_to_use`: before instantiating PrismaClient | One client per process; Prisma 7 **requires a driver adapter** (`new PrismaClient()` with no args does not type-check) — `@prisma/adapter-pg` for Postgres; import from the generated `output` path, not `@prisma/client`; cache on `globalThis` in dev; `$disconnect()` on shutdown; `warn`/`error` logging only.
READ | knowledge/prisma/02-schema.md (head) | Schema-file structure rules | Exactly one datasource + one generator block; comment in its good example states the v7 no-`url` rule.
GREP | Good Example in knowledge/prisma/03-models.md | Field conventions for the `Product` model | `@id @default(cuid())` (opaque id, no enumeration / row-count leak) over `autoincrement()`; include `createdAt`/`updatedAt` for an audit trail.
GREP | headings of knowledge/prisma/100-common-antipatterns.md | Self-verify | #1 "A new PrismaClient per request" — the singleton in t2-db.ts is the fix.

## T3 — Kubernetes Deployment

GREP | `"readinessProbe":` in SIGNALS.json | Symbol straight from the task | cicd/22-kubernetes-integration, kubernetes/30-engineering-principles — pointed at the topic, not yet the right doc.
BASH | `ls knowledge/kubernetes/` | Find the doc that owns Deployments | 05-deployments, 19-resource-management, 04-pods, 100-common-antipatterns are the candidates.
GREP | INDEX.json for those four | `status` + `when_to_use` | All `ready`. 05-deployments: "before creating or changing a stateless workload's rollout, replica count, or update strategy". 19-resource-management: "before setting CPU/memory requests and limits on any container" — so it, not 05, owns the resources decision.
GREP | `defers_to` across knowledge/kubernetes/*.md | Resolve which doc wins where they overlap | No `defers_to` anywhere in the topic → fall back to `when_to_use` specificity.
READ | knowledge/kubernetes/05-deployments.md (full) | Owns the manifest shape | Its good example is almost exactly this task (image `registry.example.com/web:1.4.2`, 3 replicas, `/healthz`:8080). Rules: `RollingUpdate` with `maxUnavailable: 0` / `maxSurge: 1`, readiness probe gates the rollout, ≥2 replicas + a `PodDisruptionBudget`, pinned tags, `revisionHistoryLimit`, `progressDeadlineSeconds`.
READ | knowledge/kubernetes/19-resource-management.md (full) | Owns requests/limits sizing | Memory `request == limit` → Guaranteed QoS; **prefer omitting the CPU limit** ("set one only when you need hard, predictable isolation") because CPU limits throttle and produce tail latency; units `m` / `Mi`; align the runtime heap to the cgroup limit.
READ | knowledge/kubernetes/04-pods.md (examples + checklist) | Owns the pod template (probes, securityContext) | Readiness **and** liveness probes (liveness with a delay), `runAsNonRoot`, `seccompProfile: RuntimeDefault`, `allowPrivilegeEscalation: false`, `readOnlyRootFilesystem: true`, drop ALL capabilities, handle SIGTERM.
READ | knowledge/kubernetes/100-common-antipatterns.md (full) | Step 4 self-verification | #1 no `:latest`; #3 readiness must be `httpGet` on a dependency-aware endpoint, not `tcpSocket`; #4 liveness must be generous or it restarts healthy pods under load; #6 single replica without a PDB; #8 root/privileged; #10 ignoring SIGTERM.

## T4 — Terraform ACM certificate + ALB HTTPS listener

GREP | `"aws_acm_certificate":` and `"aws_acm_certificate_validation":` in SIGNALS.json | Resource type names are the strongest available signal | aws/09-acm; validation also maps to aws/10-elastic-load-balancer, which is exactly the cert→listener seam.
GREP | INDEX.json for aws/09-acm, aws/10-elastic-load-balancer | `status` + `when_to_use` | Both `ready`; 09-acm "before requesting, validating, or attaching a TLS certificate to CloudFront, an ALB, or API Gateway"; 10-elb "…configuring listeners, health checks, or TLS termination".
READ | knowledge/aws/09-acm.md (full) | Owns the certificate | DNS validation (never EMAIL); apex + `*.example.com` on one cert; `lifecycle { create_before_destroy = true }` or a SAN change destroys the cert before the new one validates → listener outage; manage the validation CNAME in IaC (deleting it silently kills auto-renewal); gate dependents on `aws_acm_certificate_validation`; ALB reads the cert from **its own** region (only CloudFront needs us-east-1); alarm on `DaysToExpiry`.
READ | knowledge/aws/10-elastic-load-balancer.md (full) | Owns the listener | Listener takes `certificate_arn = aws_acm_certificate_validation.app.certificate_arn` (not the cert's own arn), `ssl_policy = "ELBSecurityPolicy-TLS13-1-2-2021-06"`; target group health check on `/healthz` with `interval 10` and thresholds 2, `matcher = "200"`; `deregistration_delay = 30`; redirect HTTP:80 → HTTPS:443.

## T5 — Article JSON-LD on a blog post page

GREP | `json-ld` / `jsonLdScript` in SIGNALS.json | Subject term and a helper name | Both map to exactly one doc: nextjs/19-seo.
GREP | INDEX.json for nextjs/19-seo | `status` | `ready`; related: nextjs/18-metadata, nextjs/08-rendering-strategies, seo/01-seo-fundamentals.
GREP | `json-ld|jsonLd|schema.org|dangerouslySetInnerHTML|script` in knowledge/nextjs/19-seo.md | Locate the structured-data section in an 875-line doc rather than reading blind | Hits at 354-434 (Structured Data) and 775-799 (Examples).
READ | knowledge/nextjs/19-seo.md lines 190-449 and 755-874 | The chosen sections, in full | Emit JSON-LD from a **Server Component** as `<script type="application/ld+json">`; build the object in JS; `JSON.stringify` does **not** escape `<`, and a value containing `</script>` closes the element early — an injection sink reachable by anyone who can edit content — so escape with `.replace(/</g, "\\u003c")` in a shared `jsonLdScript` helper and pass it through `dangerouslySetInnerHTML` (React's text escaping would corrupt the JSON, so `<script>{json}</script>` is not an option). Client-injected JSON-LD (`useEffect`) is the named anti-pattern. Also: `generateMetadata` + the page share the loader wrapped in React `cache()` so the record is fetched once; `params` is a `Promise`.

## Step 4 — self-verification (checklists)

CHECK | knowledge/nextjs/99-ai-review-checklist.md + 100-common-antipatterns.md | Against t1.ts and t5.tsx | Input validated with a schema; authorization re-checked server-side; cache invalidated after the mutation with the narrowest tag; `params` awaited; no `"use client"` on a page; JSON-LD server-rendered.
CHECK | knowledge/kubernetes/100-common-antipatterns.md + 04-pods / 19-resource-management review lists | Against t3.yaml | Pinned tag; requests set on CPU and memory; memory limit == request (Guaranteed); httpGet readiness on a dependency-aware path; slack liveness; 3 replicas + PDB; non-root, read-only rootfs, dropped caps; SIGTERM grace period. CPU limit deliberately omitted and the reason stated inline, which is what the checklist item "Are CPU limits omitted for burst workloads, or justified where present?" asks for.
CHECK | knowledge/prisma/100-common-antipatterns.md + 06-client/27-tooling review lists | Against t2-* | One shared client with a globalThis guard and `$disconnect` on shutdown; driver adapter supplied; URL only via `env()`; generator `output` set; CLI/client pinned to one version in the package.json note.
CHECK | knowledge/aws/09-acm + 10-elastic-load-balancer review lists | Against t4.tf | DNS validation; validation records in IaC; listener gated on `aws_acm_certificate_validation`; TLS 1.2+/1.3 policy; HTTP→HTTPS redirect; dependency-aware health check; deregistration delay; DaysToExpiry alarm.
NOTE | knowledge base | Read-only throughout | No file in the repository was created, edited, or deleted by this run. (`scripts/trial-grade.py` shows as untracked in git status; it was not created by this session.)
