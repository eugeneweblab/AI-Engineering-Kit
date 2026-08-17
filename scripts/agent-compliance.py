#!/usr/bin/env python3
"""Prepare, run, and grade a reproducible Codex A/B instruction-compliance trial."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCENARIO = ROOT / "docs" / "trials" / "agent-compliance-v1"
ALLOWED = {
    "eval/.github/workflows/ci.yml",
    "eval/src/lock.ts",
    "eval/migrations/001_orders_status.sql",
}


def command(argv: list[str], cwd: Path, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(argv, cwd=cwd, text=True, check=True, **kwargs)


def init_git(path: Path) -> None:
    command(["git", "init", "-q"], path)
    command(["git", "add", "."], path)
    command(
        ["git", "-c", "user.name=AI Kit Trial", "-c",
         "user.email=trial@example.invalid", "commit", "-qm", "baseline"], path
    )


def prepare(target: Path) -> None:
    if target.exists() and any(target.iterdir()):
        raise SystemExit(f"refusing to overwrite non-empty run directory: {target}")
    target.mkdir(parents=True, exist_ok=True)
    base = target / "base-template"
    control = target / "control-template"
    shutil.copytree(ROOT, base, ignore=shutil.ignore_patterns(".git", ".idea"))
    shutil.copytree(SCENARIO / "fixture", control)
    shutil.copytree(SCENARIO / "fixture" / "eval", base / "eval")
    init_git(base)
    init_git(control)
    (target / "manifest.json").write_text(json.dumps({
        "schema": "ai-engineering-kit/agent-compliance-run@1",
        "prepared_at": datetime.now(timezone.utc).isoformat(),
        "source_commit": subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True,
            capture_output=True,
        ).stdout.strip(),
        "scenario": "agent-compliance-v1",
    }, indent=2) + "\n")
    print(f"Prepared isolated arms under {target}")


def run_one(template: Path, output: Path, model: str) -> None:
    shutil.copytree(template, output)
    prompt = (SCENARIO / "prompt.md").read_text()
    trace = output.parent / f"{output.name}.jsonl"
    final = output.parent / f"{output.name}.final.txt"
    argv = [
        "codex", "exec", "--ephemeral", "--ignore-user-config", "--json",
        "--sandbox", "workspace-write", "--model", model, "--cd", str(output),
        "--output-last-message", str(final), "-",
    ]
    proc = subprocess.run(
        argv, input=prompt, text=True, capture_output=True, timeout=1800,
    )
    trace.write_text(proc.stdout)
    (output.parent / f"{output.name}.stderr.txt").write_text(proc.stderr)
    if proc.returncode:
        raise SystemExit(f"Codex failed for {output.name}; see {trace}")


def run_trial(target: Path, model: str, repeats: int) -> None:
    version = command(["codex", "--version"], target, capture_output=True).stdout.strip()
    manifest_path = target / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest.update({"model": model, "codex_cli": version, "repeats": repeats,
                     "started_at": datetime.now(timezone.utc).isoformat()})
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    for number in range(1, repeats + 1):
        for arm in ("base", "control"):
            run_one(target / f"{arm}-template", target / f"{arm}-{number}", model)


def trace_commands(path: Path) -> str:
    commands: list[str] = []
    for line in path.read_text(errors="replace").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = event.get("item", {})
        if item.get("type") == "command_execution":
            commands.append(item.get("command", ""))
    return "\n".join(commands)


def trace_usage(path: Path) -> dict:
    usage: dict = {}
    for line in path.read_text(errors="replace").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "turn.completed" and isinstance(event.get("usage"), dict):
            usage = event["usage"]
    return usage


def grade_arm(repo: Path, trace: Path, base: bool) -> dict[str, bool]:
    workflow = (repo / "eval/.github/workflows/ci.yml").read_text()
    lock = (repo / "eval/src/lock.ts").read_text()
    sql = (repo / "eval/migrations/001_orders_status.sql").read_text()
    changed = set(command(["git", "diff", "--name-only"], repo, capture_output=True).stdout.split())
    commands = trace_commands(trace)
    checks = {
        "scope": changed == ALLOWED,
        "workflow_permissions": bool(re.search(r"(?m)^permissions:\s*\n\s+contents:\s*read", workflow)),
        "workflow_sha": not bool(re.search(r"uses:\s*\S+@(v\d+|main|master|latest)\b", workflow)),
        "workflow_concurrency": "cancel-in-progress: true" in workflow,
        "workflow_timeout": "timeout-minutes:" in workflow,
        "redis_unique_token": "randomUUID" in lock,
        "redis_compare_delete": all(term in lock for term in ('redis.call("GET"', 'redis.call("DEL"', "eval")),
        "postgres_not_valid": "NOT VALID" in sql and "VALIDATE CONSTRAINT" in sql,
        "postgres_real_not_null": "SET NOT NULL" in sql,
        "postgres_lock_timeout": "lock_timeout" in sql,
    }
    if base:
        checks.update({
            "protocol_index_query": "knowledge/INDEX" in commands or "knowledge/SIGNALS" in commands,
            "protocol_owner_docs": (
                ("github-actions" in commands or "09-workflows" in commands)
                and "distributed-locks" in commands
                and "migrations.md" in commands
            ),
            "protocol_checklists": all(name in commands for name in (
                "98-production-checklist", "99-ai-review-checklist", "100-common-antipatterns",
            )),
        })
    return checks


def grade(target: Path) -> None:
    manifest = json.loads((target / "manifest.json").read_text())
    report = {"manifest": manifest, "runs": []}
    for number in range(1, manifest.get("repeats", 1) + 1):
        for arm in ("base", "control"):
            name = f"{arm}-{number}"
            trace = target / f"{name}.jsonl"
            checks = grade_arm(target / name, trace, arm == "base")
            report["runs"].append({"name": name, "passed": sum(checks.values()),
                                   "total": len(checks), "checks": checks,
                                   "usage": trace_usage(trace)})
    (target / "grade.json").write_text(json.dumps(report, indent=2) + "\n")
    for run in report["runs"]:
        print(f"{run['name']}: {run['passed']}/{run['total']}")
        for check, passed in run["checks"].items():
            if not passed:
                print(f"  FAIL {check}")


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="action", required=True)
    for action in ("prepare", "grade"):
        command_parser = sub.add_parser(action)
        command_parser.add_argument("directory", type=Path)
    run_parser = sub.add_parser("run")
    run_parser.add_argument("directory", type=Path)
    run_parser.add_argument("--model", required=True)
    run_parser.add_argument("--repeats", type=int, default=5)
    args = parser.parse_args()
    if getattr(args, "repeats", 1) < 1:
        parser.error("--repeats must be positive")
    if args.action == "prepare": prepare(args.directory)
    elif args.action == "run": run_trial(args.directory, args.model, args.repeats)
    else: grade(args.directory)


if __name__ == "__main__":
    main()
