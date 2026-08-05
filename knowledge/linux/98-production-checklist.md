---
id: linux/98-production-checklist
topic: linux
slug: production-checklist
title: "Linux Production Checklist"
type: doc
order: 98
status: ready
tags: [linux, production-checklist]
related: [linux/25-production, linux/17-security, linux/08-systemd, linux/15-logging, linux/20-backups]
when_to_use: "Read before promoting any Linux host or service to production or signing off a go-live."
---
# Linux Production Checklist

## Purpose

A verifiable, pre-flight checklist for putting a Linux host or service into
production. Each item is a yes/no an agent or reviewer can confirm against the
actual system, not an aspiration. If an item cannot be checked "yes," the host is
not ready. This complements the reasoning in
[engineering-principles](30-engineering-principles.md) and the detailed guidance
in [production](25-production.md).

## Why It Matters

Production Linux failures are rarely exotic — they are the same unchecked boxes
every time: no backups, disk fills up, service dies and never restarts, root SSH
left open. A checklist converts hard-won incident knowledge into a repeatable gate
so the same outage does not happen twice. The cost of running it is minutes; the
cost of skipping it is a 2am page.

## Provisioning & Reproducibility

**Rules:** [Package Management](12-package-management.md) · [Automation](23-automation.md)

- [ ] The host is built from version-controlled config (cloud-init/Ansible/image), not by hand.
- [ ] The OS is a supported LTS release still receiving security updates.
- [ ] All installed packages come from signed repositories; no `curl | bash` installs remain.
- [ ] Package versions or the base image are pinned so a rebuild is deterministic.
- [ ] Timezone is UTC and NTP/`systemd-timesyncd` is syncing the clock.

## Access & Security

**Rules:** [SSH](10-ssh.md) · [Firewall](21-firewall.md)

- [ ] SSH allows key-based auth only; `PasswordAuthentication no` and `PermitRootLogin no`.
- [ ] Every human logs in as a named user; shared accounts are eliminated.
- [ ] `sudo` is granted per-user, logged, and scoped — no blanket `NOPASSWD: ALL`.
- [ ] A host firewall ([firewall](21-firewall.md)) denies inbound by default; only needed ports are open.
- [ ] Automatic or scheduled security updates are enabled and verified to apply.
- [ ] No secrets are present in shell history, environment listings, world-readable files, or the repo.

## Services & Process Lifecycle

**Rules:** [Systemd](08-systemd.md) · [Processes](06-processes.md)

- [ ] Every service runs under [systemd](08-systemd.md) as a dedicated non-root user.
- [ ] Units set `Restart=on-failure` and are `enable`d to start on boot.
- [ ] Sandboxing is applied where possible (`NoNewPrivileges`, `ProtectSystem`, `ReadWritePaths`).
- [ ] Resource limits (`MemoryMax`, `TasksMax`, `LimitNOFILE`) prevent one process from starving the host.
- [ ] A clean reboot brings every required service back up unattended.

## Storage & Data

**Rules:** [Storage](11-storage.md) · [Backups](20-backups.md)

- [ ] Disk usage and inode usage are monitored with alerts before they reach 100%.
- [ ] Backups run on a schedule and a restore has been tested end-to-end ([backups](20-backups.md)).
- [ ] Log rotation (`logrotate`/journald limits) caps disk growth from logs.
- [ ] Filesystems for data are separate from `/`, so a full data disk cannot wedge the OS.

## Observability

**Rules:** [Logging](15-logging.md) · [Monitoring](16-monitoring.md)

- [ ] Every service logs to journald or a central sink with a known retention ([logging](15-logging.md)).
- [ ] Host metrics (CPU, memory, disk, load) are collected and dashboarded ([monitoring](16-monitoring.md)).
- [ ] Alerts fire on error *rates* and resource thresholds, not just on total outage.
- [ ] A documented health endpoint or command confirms each service is actually serving.

## Resilience & Recovery

**Rules:** [Backups](20-backups.md) · [Troubleshooting](27-troubleshooting.md)

- [ ] The host survives a reboot and an OOM event without manual intervention.
- [ ] An out-of-band recovery path (console/rescue) exists for when SSH is down.
- [ ] A rollback plan exists for the deployment and has been rehearsed.
- [ ] An on-call owner and a runbook for the top failure modes are documented.

## AI Review Checklist

- [ ] Could this host be destroyed and rebuilt from config with no manual steps?
- [ ] Is root SSH disabled and inbound traffic default-denied?
- [ ] Does every service auto-restart and survive a reboot?
- [ ] Has a backup restore actually been tested, not just configured?
- [ ] Will someone be paged before the disk fills, not after?

## Related

- `knowledge/linux/25-production.md`
- `knowledge/linux/17-security.md`
- `knowledge/linux/08-systemd.md`
- `knowledge/linux/15-logging.md`
- `knowledge/linux/20-backups.md`
