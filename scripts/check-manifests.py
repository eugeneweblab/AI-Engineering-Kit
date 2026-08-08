#!/usr/bin/env python3
"""Guardrail: a YAML example must be valid to the tool that consumes it.

`check-knowledge.py` proves 244 YAML blocks are YAML. That is a much weaker claim
than it looks: a Kubernetes Deployment without `spec.selector` is valid YAML and is
rejected by the API server, a workflow job without `runs-on` is valid YAML and fails
to load, and both parse without complaint.

They were in the base. Thirteen Deployments across five topics had no `selector` —
including in `kubernetes/`, whose own `05-deployments.md` shows it correctly — so
every one of them would have failed `kubectl apply`. A release workflow declared no
`runs-on` on either job, and forwarded no `outputs` from the job that computes the
version, so `needs.release.outputs.release_created` was always empty and the deploy
job would never have run: a green pipeline that ships nothing.

Validated per kind, by the tool that actually consumes the format:

  Kubernetes   kubeconform -strict          (schema, offline after first fetch)
  Workflows    actionlint                   (syntax + expression types)
  Compose      docker compose config        (schema + cross-service references)

Blocks that are deliberately partial — a `compose.override.yaml` has no `image`
because it merges over a base file — are recorded in
`scripts/data/manifests-baseline.json` by content hash.

A tool that is absent is reported, never silently skipped; `--require-tools` turns
that into a failure so CI cannot go green on an unchecked format.

Exit code 0 = clean, 1 = an example its own tool rejects.

Usage:
    python3 scripts/check-manifests.py
    python3 scripts/check-manifests.py --require-tools
    python3 scripts/check-manifests.py --update-baseline
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

ROOT = Path(__file__).resolve().parent.parent
KB = ROOT / "knowledge"
BASELINE = ROOT / "scripts" / "data" / "manifests-baseline.json"

FENCE = re.compile(r"^```(?:yaml|yml)\s*$\n(.*?)^```\s*$", re.DOTALL | re.MULTILINE)
ENV_FILE = re.compile(r"env_file:\s*(?:\[([^\]]+)\]|(\S+))")

SKIPPED: dict[str, str] = {}


def classify(source: str) -> str | None:
    """Which tool owns this block, judged by the keys its format requires."""
    try:
        documents = [d for d in yaml.safe_load_all(source) if isinstance(d, dict)]
    except Exception:                                 # noqa: BLE001 - not our error to report
        return None                                   # check-knowledge owns YAML syntax
    if any("kind" in d and "apiVersion" in d for d in documents):
        return "kubernetes"
    for document in documents:
        jobs = document.get("jobs")
        # Most workflow examples are excerpts that omit `on:` to keep the point in
        # view. Requiring it here meant they were classified as nothing and checked
        # by nothing — the jobs, which is where the defects were, went unread.
        if isinstance(jobs, dict) and any(
            isinstance(job, dict) and ("steps" in job or "uses" in job)
            for job in jobs.values()
        ):
            return "workflow"
        if isinstance(document.get("services"), dict):
            return "compose"
    return None


def check_kubernetes(source: str, _: Path) -> str | None:
    proc = subprocess.run(
        ["kubeconform", "-strict", "-ignore-missing-schemas", "-output", "json", "-"],
        input=source, capture_output=True, text=True,
    )
    try:
        report = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return (proc.stderr or proc.stdout).strip()[:200] or "kubeconform produced no report"
    for resource in report.get("resources", []):
        if resource.get("status") not in ("statusValid", "statusSkipped", "statusEmpty"):
            kind = f"{resource.get('kind')}/{resource.get('name')}".strip("/")
            message = re.sub(r"\S+kubernetes-json-schema\S+", "schema", resource.get("msg", ""))
            return f"{kind}: {message}"[:300]
    return None


def check_workflow(source: str, workdir: Path) -> str | None:
    directory = workdir / ".github" / "workflows"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "w.yml"
    # An excerpt with no trigger is still a workflow excerpt; supply the smallest
    # valid one so the jobs get read. Only for validation — the document is unchanged.
    document = yaml.safe_load(source)
    prefix = "" if isinstance(document, dict) and ("on" in document or True in document) \
        else "on: push\n"
    path.write_text(prefix + source, encoding="utf-8")
    # shellcheck and pyflakes are separate concerns and are off: the base's shell
    # blocks are already parsed by check-knowledge, and their findings here would be
    # noise about example placeholders.
    proc = subprocess.run(
        ["actionlint", "-no-color", "-shellcheck=", "-pyflakes=", str(path)],
        capture_output=True, text=True, cwd=workdir,
    )
    if proc.returncode == 0:
        return None
    for line in (proc.stdout or proc.stderr).strip().split("\n"):
        if "w.yml:" in line:
            return line.split("w.yml:")[-1].strip()[:300]
    return (proc.stdout or proc.stderr).strip()[:200]


def check_compose(source: str, workdir: Path) -> str | None:
    path = workdir / "compose.yaml"
    path.write_text(source, encoding="utf-8")
    # `env_file: .env` is correct usage; the file simply is not in a temp directory.
    # Stub the referenced names so the run reports schema problems, not our sandbox.
    for group, single in ENV_FILE.findall(source):
        for name in (group or single).replace(",", " ").split():
            name = name.strip("'\"[]")
            if name and "/" not in name:
                (workdir / name).touch()
    proc = subprocess.run(
        ["docker", "compose", "-f", str(path), "config", "--quiet"],
        capture_output=True, text=True, cwd=workdir,
    )
    if proc.returncode == 0:
        return None
    return (proc.stderr or proc.stdout).strip().split("\n")[0][:300]


KINDS = {
    "kubernetes": ("kubeconform", check_kubernetes),
    "workflow": ("actionlint", check_workflow),
    "compose": ("docker", check_compose),
}


def main(argv: list[str]) -> int:
    if yaml is None:
        print("error: PyYAML is not installed; nothing could be classified")
        return 1

    baseline: dict[str, str] = (
        json.loads(BASELINE.read_text(encoding="utf-8")) if BASELINE.exists() else {}
    )
    found: dict[str, str] = {}
    problems: list[str] = []
    counts: dict[str, int] = {}

    for path in sorted(KB.rglob("*.md")):
        rel = path.relative_to(KB).as_posix()
        for source in FENCE.findall(path.read_text(encoding="utf-8", errors="replace")):
            kind = classify(source)
            if kind is None:
                continue
            tool, checker = KINDS[kind]
            if not shutil.which(tool):
                SKIPPED[kind] = tool
                continue
            counts[kind] = counts.get(kind, 0) + 1
            with tempfile.TemporaryDirectory() as tmp:
                failure = checker(source, Path(tmp))
            if not failure:
                continue
            key = hashlib.sha1(f"{rel}:{source}".encode()).hexdigest()[:10]
            found[key] = f"{rel} ({kind})"
            if key not in baseline:
                problems.append(f"{rel}: {kind} example is rejected by {tool}\n      {failure}")

    if "--update-baseline" in argv:
        BASELINE.write_text(
            json.dumps(found, indent=1, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(f"baseline updated: {len(found)} deliberately-partial blocks recorded.")
        return 0

    for key in sorted(set(baseline) - set(found)):
        problems.append(
            f"baseline: {baseline[key]} is recorded as deliberately partial but now "
            f"validates or no longer matches. Run --update-baseline."
        )

    for kind, tool in sorted(SKIPPED.items()):
        message = f"{kind} examples were not checked: `{tool}` is unavailable."
        if "--require-tools" in argv:
            problems.append(message)
        else:
            print(f"  note: {message}")

    if problems:
        print(f"\nFAIL: {len(problems)} problem(s)\n")
        for problem in problems:
            print(f"  {problem}")
        print("\nValid YAML is not a valid manifest. These parse and are still rejected "
              "by the tool\nthat would run them.")
        return 1

    summary = ", ".join(f"{count} {kind}" for kind, count in sorted(counts.items()))
    print(f"OK: every manifest is accepted by its own tool ({summary}; "
          f"{len(baseline)} deliberately partial).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
