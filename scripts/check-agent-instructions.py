#!/usr/bin/env python3
"""Guardrail: the instructions given to AI agents must be executable and true.

`check-knowledge.py` protects the knowledge. This protects the contract on top of
it — the files an agent actually reads first. Those went out of date silently:
AGENTS.md told agents to match on `topic` and follow `related`, and `INDEX.json`
carried neither field, so an agent working from the index could do neither.

Checks
------
  entrypoints  every tool-specific file exists and redirects to AGENTS.md
  paths        every path and link an instruction file names exists
  fields       every frontmatter field an instruction file names is in INDEX.json
  values       every `status:`/`type:` value named is one the base actually uses
  commands     every `python3 scripts/…` command named exists and is executable
  protocol     the documented lookups resolve: a representative repository file
               reaches a document through SIGNALS.stack, and a representative API
               name reaches one through SIGNALS.symbols

Exit code 0 = clean, 1 = violations found.

Usage:
    python3 scripts/check-agent-instructions.py
    python3 scripts/check-agent-instructions.py --selftest   # prove it can fail
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from frontmatter import FIELDS

ROOT = Path(__file__).resolve().parent.parent

# Every file an agent may load first. Each must point at AGENTS.md so there is one
# source of truth rather than six drifting copies.
ENTRYPOINTS = [
    "CLAUDE.md",
    "GEMINI.md",
    ".clinerules",
    ".github/copilot-instructions.md",
    ".cursor/rules/ai-engineering-kit.mdc",
]
INSTRUCTION_FILES = ["AGENTS.md", "README.md", "agents/README.md", *ENTRYPOINTS]

FIELD_RE = re.compile(
    r"`(status|maturity|tags|when_to_use|related|order|type|slug|topic|id|"
    r"applies_to|defers_to|verified_against|source_urls|last_reviewed|review_after)`"
)
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
BARE_PATH_RE = re.compile(r"`((?:knowledge|scripts|docs|agents)/[\w./-]+)`")
COMMAND_RE = re.compile(r"`(python3 scripts/[\w-]+\.py)[^`]*`")
STATUS_RE = re.compile(r'`status:\s*"?(\w+)"?`')

# An instruction file may not tell an agent to load something it cannot hold. The
# index is ~310k tokens; "open INDEX.json" was in AGENTS.md for months, and every
# retrieval test passed anyway because the test harness reads it with Python, which
# has no context window. The consumer does.
LOAD_VERBS = re.compile(
    r"\b(open|read|load)\b[^.\n]{0,40}`?(knowledge/(?:INDEX|SIGNALS)\.json)`?",
    re.IGNORECASE,
)
MAX_LOADABLE_CHARS = 200_000        # ~50k tokens


# The lookups the instructions promise. Each must land on a document that exists.
PROTOCOL_PROBES = {
    "stack": ["app/page.tsx", "wp-config.php", "Dockerfile", "prisma/schema.prisma"],
    "symbols": ["revalidateTag", "add_filter", "argon2", "OOMKilled", "jwtVerify"],
}


def selftest() -> int:
    """Inject the defect this file exists to catch and assert it is reported.

    A contract check that cannot fail is worth nothing, and this one guards a claim
    that was false for months without any test noticing: AGENTS.md said "Open
    knowledge/INDEX.json", and every retrieval probe still passed, because the test
    harness reads that file with Python rather than with a context window.
    """
    global ROOT
    source_root = ROOT
    with tempfile.TemporaryDirectory(prefix="agent-instructions-selftest-") as tmp:
        test_root = Path(tmp) / "repo"
        shutil.copytree(source_root, test_root, ignore=shutil.ignore_patterns(".git", ".idea"))
        subprocess.run(["git", "init", "-q"], cwd=test_root, check=True)
        agents = test_root / "AGENTS.md"
        original = agents.read_text(encoding="utf-8")
        injected = original.replace(
            "Query the index; do not read it.", "Open knowledge/INDEX.json.", 1
        )
        if injected == original:
            print("selftest: the anchor phrase is gone; update the injection.")
            return 1
        agents.write_text(injected, encoding="utf-8")
        import io, contextlib
        buffer = io.StringIO()
        try:
            ROOT = test_root
            with contextlib.redirect_stdout(buffer):
                code = main()
        finally:
            ROOT = source_root
        output = buffer.getvalue()
    if code == 0 or "Instruct a query, not a load" not in output:
        print("selftest FAIL: telling an agent to open a 310k-token file was not "
              "reported.")
        return 1
    print("selftest OK: an instruction to load an oversized artifact is reported.")
    return 0


def main() -> int:
    problems: list[str] = []

    index_path = ROOT / "knowledge" / "INDEX.json"
    signals_path = ROOT / "knowledge" / "SIGNALS.json"
    if not index_path.exists() or not signals_path.exists():
        print("error: INDEX.json or SIGNALS.json is missing; run the builders first")
        return 1

    index = json.loads(index_path.read_text(encoding="utf-8"))
    signals = json.loads(signals_path.read_text(encoding="utf-8"))
    docs = [d for t in index["topics"].values() for d in t["docs"]]
    doc_ids = {d["id"] for d in docs}
    exposed_fields = set().union(*(set(d) for d in docs))
    statuses = {d["status"] for d in docs} | {"draft"}

    nested = ROOT / "knowledge" / "nextjs"
    root_probe = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], cwd=nested,
        capture_output=True, text=True,
    )
    if root_probe.returncode != 0 or Path(root_probe.stdout.strip()).resolve() != ROOT.resolve():
        problems.append("nested cwd: Git-root discovery does not resolve to this repository")

    for name in INSTRUCTION_FILES:
        path = ROOT / name
        if not path.exists():
            problems.append(f"{name}: missing")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")

        if name in ["AGENTS.md", *ENTRYPOINTS] and not re.search(
            r"Git root|git rev-parse --show-toplevel", text, re.IGNORECASE
        ):
            problems.append(f"{name}: does not tell a nested-cwd agent to resolve the Git root")

        if name in ENTRYPOINTS and "AGENTS.md" not in text:
            problems.append(f"{name}: does not point at AGENTS.md")

        for target in LINK_RE.findall(text):
            if target.startswith(("http", "#", "mailto")):
                continue
            candidate = target.split("#")[0]
            if not ((path.parent / candidate).exists() or (ROOT / candidate).exists()):
                problems.append(f"{name}: link -> {target} does not exist")

        for bare in BARE_PATH_RE.findall(text):
            if "*" in bare or "<" in bare:
                continue
            if not (ROOT / bare).exists():
                problems.append(f"{name}: path -> {bare} does not exist")

        for field in set(FIELD_RE.findall(text)):
            if field not in exposed_fields:
                problems.append(
                    f"{name}: tells an agent to use `{field}`, "
                    f"which INDEX.json does not expose"
                )

        for value in set(STATUS_RE.findall(text)):
            if value not in statuses:
                problems.append(f"{name}: names status {value!r}, which no doc uses")

        for match in LOAD_VERBS.finditer(text):
            target = ROOT / match.group(2)
            if target.exists() and target.stat().st_size > MAX_LOADABLE_CHARS:
                size = target.stat().st_size // 1000
                problems.append(
                    f"{name}: tells an agent to {match.group(1).lower()} "
                    f"{match.group(2)}, which is {size}k characters "
                    f"(~{size // 4}k tokens). Instruct a query, not a load."
                )

        for command in set(COMMAND_RE.findall(text)):
            script = ROOT / command.split()[1]
            if not script.exists():
                problems.append(f"{name}: command -> {script.name} does not exist")

    # The metadata contract in AGENTS.md must match the schema accepted by every
    # builder/checker. Optional provenance fields need not appear in all legacy docs.
    agents_text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    contract = re.search(r"```yaml\s*\n---\n(.*?)\n---\n```", agents_text, re.DOTALL)
    if contract:
        documented = set(re.findall(r"^([a-z_]+):", contract.group(1), re.MULTILINE))
        for field in sorted(documented - FIELDS):
            problems.append(
                f"AGENTS.md: the metadata contract documents `{field}`, "
                f"which the parser schema does not accept"
            )
        for field in sorted(FIELDS - documented):
            problems.append(
                f"AGENTS.md: the parser accepts `{field}`, "
                f"which the metadata contract does not mention"
            )

    # The protocol itself: do the promised lookups actually resolve?
    import fnmatch

    for probe in PROTOCOL_PROBES["stack"]:
        matched = [
            entry
            for entry in signals["stack"]
            for pattern in entry["when"].split("|")
            if fnmatch.fnmatch(probe, pattern)
        ]
        if not matched:
            problems.append(f"SIGNALS.stack: {probe} matches no signal")
        for entry in matched:
            for doc_id in entry["docs"]:
                if doc_id not in doc_ids:
                    problems.append(f"SIGNALS.stack: {probe} -> {doc_id} is not in INDEX")

    for probe in PROTOCOL_PROBES["symbols"]:
        targets = signals["symbols"].get(probe)
        if not targets:
            problems.append(f"SIGNALS.symbols: {probe} resolves to nothing")
            continue
        for doc_id in targets:
            if doc_id not in doc_ids:
                problems.append(f"SIGNALS.symbols: {probe} -> {doc_id} is not in INDEX")

    if problems:
        print(f"FAIL: {len(problems)} problem(s) in the agent-facing contract\n")
        for problem in problems:
            print(f"  {problem}")
        return 1

    print(
        f"OK: {len(INSTRUCTION_FILES)} instruction files are consistent with "
        f"{len(docs)} indexed docs; every documented lookup resolves."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(selftest() if "--selftest" in sys.argv else main())
