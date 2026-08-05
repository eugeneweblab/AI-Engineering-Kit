---
id: linux/100-common-antipatterns
topic: linux
slug: common-antipatterns
title: "Linux Common Antipatterns"
type: antipatterns
order: 100
status: ready
tags: [linux, common-antipatterns, chown, shellcheck, nohup, enable]
related: [linux/24-scripting, linux/05-permissions, linux/08-systemd, linux/17-security, linux/99-ai-review-checklist]
when_to_use: "Read when writing or reviewing Linux scripts, permissions, or service config to recognize and avoid the classic mistakes."
---
# Linux Common Antipatterns

## Purpose

A catalog of the Linux mistakes that recur across real systems, each with why it
is wrong and the concrete fix. These are the failure modes behind most production
incidents on Linux hosts. Use this alongside the
[ai-review-checklist](99-ai-review-checklist.md) to catch them in review, and
[engineering-principles](30-engineering-principles.md) for the reasoning underneath.

## Why It Matters

Every antipattern here has shipped an outage. They persist because each one
"works" on the happy path — the unquoted variable is fine until a filename has a
space, the root service is fine until it is exploited, the missing backup is fine
until the disk dies. Naming them makes the latent bug visible before it fires.

## Antipatterns

### 1. Unquoted variable expansions

- **Why it is wrong:** `$var` undergoes word-splitting and glob expansion. A path
  with a space or a `*` becomes multiple arguments, so `rm $file` can delete the
  wrong things. It passes every test where the value happens to be simple.
- **The fix:** Always quote: `rm "$file"`, `"${array[@]}"`. Run `shellcheck` in CI
  to catch these mechanically. See [scripting](24-scripting.md).

### 2. Scripts without `set -euo pipefail`

- **Why it is wrong:** By default Bash ignores command failures and treats unset
  variables as empty. A failed `cd` followed by `rm -rf "$dir"/*` runs in the
  wrong directory. Errors compound silently instead of stopping the script.
- **The fix:** Start scripts with `set -euo pipefail`. Guard destructive paths
  further with `rm -rf "${dir:?dir is unset}"` so an empty variable aborts.

### 3. `curl | sudo bash`

- **Why it is wrong:** You are handing an unaudited, mutable remote file a root
  shell. The content can change between runs, and you cannot review what executes.
- **The fix:** Download, inspect, and pin the artifact, or install from a signed
  package repository. Verify a checksum or signature before running anything as root.

### 4. `chmod 777` (or `chmod -R 777`)

- **Why it is wrong:** It grants every user read, write, and execute — including
  the ability to replace the file or scripts within it. It "fixes" a permission
  error by removing the security boundary entirely. Recursive `777` is worse.
- **The fix:** Grant the least access that works. Set correct *ownership* first
  (`chown`), then narrow modes (`640` for data, `600` for secrets, `755` for
  executables). See [permissions](05-permissions.md).

### 5. Running services as root

- **Why it is wrong:** Any compromise or bug in the service becomes root on the
  host — full filesystem access, ability to load kernel modules, total game over.
  There is rarely a real need after binding a privileged port.
- **The fix:** Run under [systemd](08-systemd.md) with a dedicated `User=`, add
  `NoNewPrivileges=true`, and use `AmbientCapabilities=CAP_NET_BIND_SERVICE` if a
  low port is needed instead of full root.

### 6. Backgrounding services with `nohup`/`&` instead of an init system

- **Why it is wrong:** The process dies with the session, never restarts on crash,
  has no defined logs, and vanishes on reboot. Nothing supervises it.
- **The fix:** Define a systemd unit with `Restart=on-failure`, `enable` it for
  boot, and let journald capture its output. The init system owns lifecycle.

### 7. Editing config on live hosts by hand

- **Why it is wrong:** The running state diverges from every file and repo that
  claims to describe it. The next rebuild or automation run silently reverts your
  fix, or worse, no one can reproduce the host at all — configuration drift.
- **The fix:** Change config in version-controlled provisioning code and apply it
  through [automation](23-automation.md). Treat hosts as rebuildable, not as pets.

### 8. Parsing `ls` output in scripts

- **Why it is wrong:** `ls` output is for humans; filenames can contain spaces,
  newlines, and glob characters that break `for f in $(ls)`. It fails exactly on
  the hostile filenames an attacker would craft.
- **The fix:** Use globs (`for f in ./*`) or `find . -print0 | xargs -0` to handle
  arbitrary filenames safely.

### 9. Cron jobs that discard output and never lock

- **Why it is wrong:** A silent cron job that fails leaves no trace, and a slow one
  can overlap itself, running two copies that corrupt shared state.
- **The fix:** Redirect output to a log or logger, alert on non-zero exit, and wrap
  the command in `flock -n /run/lock/job.lock` to prevent concurrent runs. See [cron](14-cron.md).

### 10. Secrets in the environment, repo, or shell history

- **Why it is wrong:** Environment variables are visible in `/proc/<pid>/environ`
  and process listings; committed secrets live forever in git history; typed
  secrets land in `~/.bash_history`. Any of these is a leak waiting to be found.
- **The fix:** Store secrets in a mode-`600` file owned by the service user or a
  secrets manager, load them at runtime, and keep them out of version control.

### 11. No monitoring for disk and inode usage

- **Why it is wrong:** A full disk (or exhausted inodes) wedges databases, logs,
  and the OS itself, often with cryptic errors. It is the single most common
  avoidable Linux outage.
- **The fix:** Monitor disk *and* inode usage with alerts well below 100%, cap log
  growth with rotation, and put data on a filesystem separate from `/`.

### 12. Backups that were never restore-tested

- **Why it is wrong:** A backup that has never been restored is a hypothesis, not a
  recovery plan. Silent corruption, wrong paths, or missing databases surface only
  during the disaster you needed the backup for.
- **The fix:** Automate backups *and* schedule a periodic full restore into a
  scratch environment to prove they work end-to-end. See [backups](20-backups.md).

## AI Review Checklist

- Are all variable expansions quoted and does the script use `set -euo pipefail`?
- Are permissions least-privilege, with no `777` and no services running as root?
- Is process lifecycle owned by systemd, not a backgrounded shell command?
- Is host config managed as code, with no undocumented hand edits?
- Are secrets kept out of the environment, repo, and history?
- Are disk usage monitored and backups restore-tested?

## Related

- `knowledge/linux/24-scripting.md`
- `knowledge/linux/05-permissions.md`
- `knowledge/linux/08-systemd.md`
- `knowledge/linux/17-security.md`
- `knowledge/linux/99-ai-review-checklist.md`
