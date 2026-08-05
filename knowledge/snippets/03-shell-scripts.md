---
id: snippets/03-shell-scripts
topic: snippets
slug: shell-scripts
title: "Shell Script Snippets"
type: doc
order: 3
status: ready
tags: [snippets, shell-scripts]
related: [snippets/01-typescript-utilities, linux/00-overview, tools/19-task-runners, tools/20-local-environments, devops/00-overview]
when_to_use: "Copy when writing a shell script that will run unattended — deploys, backups, CI steps, maintenance jobs."
---
# Shell Script Snippets

## The Header

Every script that runs unattended starts with these three lines. Without them, a failing
command is ignored and the script continues doing damage with bad state.

```bash
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'
```

| Flag | Prevents |
|---|---|
| `-e` | Continuing after a command fails |
| `-u` | Silently expanding an unset variable to an empty string — `rm -rf "$DIR/"` becomes `rm -rf /` |
| `-o pipefail` | A pipeline reporting success when an earlier stage failed |
| `IFS=$'\n\t'` | Word-splitting on spaces, which breaks any path containing one |

`set -e` has a known exception: a command in a condition (`if cmd; then`) or followed by
`||` does not trigger it. That is intentional — it is how you check something that may fail.

---

## Cleanup That Always Runs

```bash
#!/usr/bin/env bash
set -euo pipefail

workdir="$(mktemp -d)"

# Runs on normal exit, on error, and on Ctrl-C. Without a trap, an interrupted
# script leaves the temp directory behind on every run until the disk fills.
cleanup() {
  local exit_code=$?
  rm -rf "$workdir"
  exit "$exit_code"
}
trap cleanup EXIT INT TERM

# ... work in "$workdir"
```

---

## Failing With a Useful Message

```bash
die() {
  echo "error: $*" >&2   # errors go to stderr, so they survive a redirect of stdout
  exit 1
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || die "$1 is required but not installed"
}

require_command jq
require_command rsync

: "${DATABASE_URL:?DATABASE_URL is required}"   # fails with the variable's name
```

The `:?` form is the shortest correct way to require an environment variable: it names the
missing variable rather than failing later with an empty string.

---

## Arguments

```bash
#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: deploy.sh --env <staging|production> [--dry-run]

  --env       Target environment (required)
  --dry-run   Print what would happen, change nothing
  -h, --help  Show this message
EOF
}

env_name=""
dry_run=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --env)     env_name="${2:-}"; shift 2 ;;
    --dry-run) dry_run=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *)         usage >&2; die "unknown argument: $1" ;;
  esac
done

[[ -n "$env_name" ]] || { usage >&2; exit 1; }
```

A `--dry-run` flag on anything destructive is worth the ten lines it costs:

```bash
run() {
  if [[ "$dry_run" == true ]]; then
    echo "[dry-run] $*"
  else
    "$@"
  fi
}

run rsync -a --delete ./dist/ "deploy@$host:/var/www/app/"
```

---

## Quoting

Almost every shell bug is an unquoted variable.

```bash
# Wrong: breaks on spaces, and expands * as a glob
cp $source $dest
for f in $(ls *.txt); do echo $f; done

# Right
cp "$source" "$dest"
for f in *.txt; do echo "$f"; done       # globs directly; never parse ls output

# Arrays keep arguments separate — a string does not
args=(--exclude '.git' --exclude 'node_modules')
rsync -a "${args[@]}" ./src/ ./dest/

# Filenames from find, safely: -print0 pairs with -d ''
while IFS= read -r -d '' file; do
  echo "processing: $file"
done < <(find . -name '*.log' -print0)
```

---

## Waiting for a Service

```bash
wait_for() {
  local name="$1" host="$2" port="$3" timeout="${4:-30}"
  local deadline=$(( SECONDS + timeout ))

  until nc -z "$host" "$port" 2>/dev/null; do
    (( SECONDS < deadline )) || die "$name did not become ready within ${timeout}s"
    sleep 1
  done

  echo "$name is ready"
}

wait_for "postgres" localhost 5432
wait_for "redis" localhost 6379 10
```

A bounded wait beats `sleep 10`: it is faster when the service is ready and fails with a
clear message when it is not.

---

## Locking

```bash
# Prevents overlapping runs when a job takes longer than its interval.
# -n fails immediately rather than queueing; the exit tells you it was already running.
exec 9>/var/lock/acme-sync.lock
flock -n 9 || { echo "already running"; exit 0; }

# ... the work; the lock releases when the script exits
```

---

## A Complete Backup Script

```bash
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

readonly BACKUP_DIR="${BACKUP_DIR:-/backups}"
readonly RETENTION_DAYS="${RETENTION_DAYS:-14}"
readonly STAMP="$(date -u +%Y%m%d-%H%M%S)"

die() { echo "error: $*" >&2; exit 1; }

command -v pg_dump >/dev/null || die "pg_dump not found"
: "${DATABASE_URL:?DATABASE_URL is required}"

mkdir -p "$BACKUP_DIR"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT INT TERM

# Write to a temp path first: an interrupted dump must not look like a valid backup.
pg_dump "$DATABASE_URL" --format=custom --file="$tmp/db-$STAMP.dump"
mv "$tmp/db-$STAMP.dump" "$BACKUP_DIR/"

# Verify the artifact is readable before trusting it.
pg_restore --list "$BACKUP_DIR/db-$STAMP.dump" >/dev/null \
  || die "backup is unreadable: db-$STAMP.dump"

find "$BACKUP_DIR" -name 'db-*.dump' -mtime "+$RETENTION_DAYS" -delete

echo "backup complete: $BACKUP_DIR/db-$STAMP.dump"
```

Two properties make it safe: the dump is written to a temp path and moved into place only on
success, and the artifact is verified before old backups are deleted.

---

## Checking Your Own Scripts

```bash
shellcheck deploy.sh backup.sh    # catches quoting bugs, unreachable code, misused tests
bash -n deploy.sh                 # syntax check without executing
```

Run ShellCheck in CI. Nearly every mistake above is one it reports.

---

## Examples

**Good Example** — fails loudly, quotes everything, cleans up after itself

```bash
#!/usr/bin/env bash
# -e stop on error, -u error on unset variable, -o pipefail catch failures
# anywhere in a pipe rather than only in its last command.
set -euo pipefail

readonly BACKUP_DIR="${BACKUP_DIR:?BACKUP_DIR must be set}"
readonly STAMP="$(date -u +%Y%m%dT%H%M%SZ)"

workdir="$(mktemp -d)"
# Runs on success, on failure, and on Ctrl-C — so nothing is left behind.
trap 'rm -rf "$workdir"' EXIT

# Quoted: survives paths and values containing spaces.
mysqldump --single-transaction --quick "$DB_NAME" > "$workdir/dump.sql"

# Verify before trusting: a zero-byte dump is the classic silent backup failure.
if [[ ! -s "$workdir/dump.sql" ]]; then
	echo "error: dump is empty" >&2
	exit 1
fi

gzip -9 "$workdir/dump.sql"
mv "$workdir/dump.sql.gz" "$BACKUP_DIR/db-$STAMP.sql.gz"
echo "wrote $BACKUP_DIR/db-$STAMP.sql.gz"
```

**Bad Example** — continues after failure, unquoted, leaves temp files

```bash
#!/bin/bash
# No `set -e`: every command below runs even if the one before it failed.

BACKUP_DIR=/backups/$SITE          # unquoted and possibly unset → /backups/
cd $BACKUP_DIR                     # unquoted: breaks on a path with a space

# If mysqldump fails, the redirect still creates a 0-byte file, gzip compresses
# it happily, and the backup "succeeds" every night for a year.
mysqldump $DB_NAME > dump.sql
gzip dump.sql

rm -rf $BACKUP_DIR/*               # if BACKUP_DIR is unset, this is rm -rf /*
```

---

## Related


- `knowledge/snippets/01-typescript-utilities.md`
- `knowledge/linux/00-overview.md`
- `knowledge/tools/19-task-runners.md`
- `knowledge/tools/20-local-environments.md`
- `knowledge/devops/00-overview.md`
