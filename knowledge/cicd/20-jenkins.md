---
id: cicd/20-jenkins
topic: cicd
slug: jenkins
title: "Jenkins"
type: doc
order: 20
status: ready
tags: [cicd, jenkins]
related: [cicd/02-pipeline-design, cicd/15-secrets, cicd/18-gitlab-ci, cicd/21-docker-integration]
when_to_use: "Read before writing or reviewing a Jenkinsfile or Jenkins pipeline job."
---
# Jenkins

## Purpose

This document defines how to write a correct, secure Jenkins pipeline using a **declarative
Jenkinsfile** kept in the repository. It covers stages and agents, credentials binding,
the difference between declarative and scripted pipelines, shared libraries, and the
controller/agent security boundary. The goal is an agent that can build or review a
Jenkins pipeline without leaking credentials or running untrusted code on the controller.

Jenkins is older and more flexible than hosted CI, which means more ways to get it wrong.
The general [pipeline design](02-pipeline-design.md) rules apply; this doc covers the
Jenkins-specific mechanics agents most often mishandle.

## Why It Matters

Jenkins runs arbitrary Groovy with real infrastructure access. A pipeline that binds a
credential into a shell command, runs a build on the controller instead of an agent, or
uses `sh "deploy $USER_INPUT"` is a direct path to credential theft or remote code
execution. Unlike hosted runners, Jenkins gives you the whole machine — including the
foot-guns. The controller holds every secret in the system, so what runs *where* is a
first-order security decision, not an implementation detail.

## Core Principles

- **Declarative over scripted.** Declarative pipelines (`pipeline { ... }`) have a fixed,
  reviewable structure and safer defaults. Reach for scripted (`node { ... }`) only for
  genuinely dynamic logic, and isolate it in a `script { }` block. The cost is less
  flexibility; the payoff is a pipeline a reviewer can actually reason about.
- **Never build on the controller.** Set `agent { label '...' }` so work runs on agents.
  The controller holds all credentials — running build steps there exposes them and risks
  RCE. Enforce this at the controller level, not just by convention.
- **Bind credentials, do not interpolate them.** Use `withCredentials` / `credentials()`
  to inject secrets as environment variables. Never build a shell string with a secret in
  Groovy — `sh "curl -H token:${TOKEN}"` leaks it to the process table and the log.
- **Keep the Jenkinsfile in the repo.** Pipeline-as-code is versioned, reviewed, and diffed
  like any other code. "Configure in the UI" is unreviewable and undeployable.
- **Pin everything.** Pin agent images, tool versions, and shared-library versions by tag
  or commit. An unpinned shared library changes your pipeline behind your back.

## Best Practices

- Store secrets in the **Jenkins Credentials store** (or an external vault) and bind them
  with `withCredentials`; scope each credential to the folder/job that needs it.
- Run inside pinned container agents (`agent { docker { image 'node:22.11.0' } }`) so the
  toolchain is reproducible and isolated from the host.
- Use `options { timeout(...) }` and `disableConcurrentBuilds()` on deploy jobs to prevent
  hung builds and racing deploys.
- Version **shared libraries** with `@Library('my-lib@1.4.0')` — a specific tag, never
  `@main`, so library changes are deliberate.
- Use the `post { }` block for cleanup, notifications, and `always`-run artifact archiving,
  so a failed stage still reports and tidies up.
- Enable **Script Security** / sandbox for pipeline scripts and require admin approval for
  any non-sandboxed method — do not disable the sandbox to make a build pass.
- Quote and validate any external input passed to `sh`; prefer passing values via env vars
  over string interpolation to avoid injection.

## Examples

**Good Example** — declarative, pinned agent, bound credential

```groovy
pipeline {
  agent { docker { image 'node:22.11.0' } }   // pinned, isolated agent (not controller)
  options { timeout(time: 20, unit: 'MINUTES'); disableConcurrentBuilds() }

  stages {
    stage('Build & Test') {
      steps { sh 'npm ci && npm run build && npm test' }
    }
    stage('Deploy') {
      when { branch 'main' }                   // deploy only from main, explicitly
      steps {
        // credential injected as env var, never interpolated into the command string
        withCredentials([string(credentialsId: 'deploy-token', variable: 'DEPLOY_TOKEN')]) {
          sh './deploy.sh'                      // reads $DEPLOY_TOKEN from the environment
        }
      }
    }
  }
  post { always { archiveArtifacts artifacts: 'dist/**', allowEmptyArchive: true } }
}
```

**Bad Example** — runs on controller, interpolates secret, unpinned library

```groovy
@Library('my-lib') _                 // no version → library can change silently
pipeline {
  agent any                          // may land on the controller, exposing all secrets
  stages {
    stage('Deploy') {
      steps {
        // secret interpolated into the command → visible in log and process table
        sh "curl -H 'Authorization: ${env.DEPLOY_TOKEN}' https://api.example.com/deploy"
      }
    }
  }
}
```

## Common Mistakes

- `agent any` or building on the controller, exposing the credential store.
- Interpolating a secret into an `sh` string instead of binding it as an env var.
- Configuring build steps in the Jenkins UI instead of a committed Jenkinsfile.
- Using `@Library('my-lib')` with no version, so shared-library changes are silent.
- Disabling the Groovy sandbox / Script Security to make a script run.
- No `timeout` or `disableConcurrentBuilds`, allowing hung or racing deploys.
- Scripted pipelines used where declarative would do, making review harder.

## Production Tips

- Put deploy jobs behind an `input` step or a folder-scoped credential so a human (or a
  protected branch) gates production.
- Keep the controller lean and patched; run all workloads on ephemeral agents (Kubernetes
  or cloud agents) that are destroyed after each build.
- Rotate credentials in the Credentials store and audit `Script Approval` regularly —
  approved unsafe methods accumulate into a real attack surface.
- Back up `JENKINS_HOME` (jobs + credentials) and treat controller config as code via JCasC
  so the whole instance is reproducible.

## AI Review Checklist

- Is the pipeline declarative, with scripted logic confined to `script { }` blocks?
- Does every stage run on a pinned agent, never on the controller (`agent any`)?
- Are secrets bound via `withCredentials`/`credentials()`, never string-interpolated?
- Is the Jenkinsfile in the repo rather than configured in the UI?
- Are shared libraries pinned to a specific tag/commit?
- Do deploy jobs have `timeout` and `disableConcurrentBuilds`?
- Is the Groovy sandbox left enabled (no unsafe method approvals to force a pass)?

## Related

- `knowledge/cicd/02-pipeline-design.md`
- `knowledge/cicd/15-secrets.md`
- `knowledge/cicd/18-gitlab-ci.md`
- `knowledge/cicd/21-docker-integration.md`
