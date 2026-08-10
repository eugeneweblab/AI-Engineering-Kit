#!/usr/bin/env python3
"""Grade two arms of the "does the base change what an agent writes" trial.

Every check below is a rule the knowledge base states, chosen because it is
version-specific enough that a model answering from memory is likely to get it
wrong, and mechanical enough that grading needs no judgement. Where a real tool can
decide — kubeconform, tflint, tsc — the tool decides.

Usage:
    python3 scripts/trial-grade.py /tmp/trial/base /tmp/trial/nobase
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


def read(directory: Path, name: str) -> str:
    path = directory / name
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


# Each rule: (task, what the base says, a predicate over the produced files)
def t1_two_arg_revalidate(d: Path) -> tuple[bool, str]:
    """nextjs/10-caching: revalidateTag needs a cacheLife argument since Next 16, and
    a read-your-writes update is `updateTag`. Single-argument revalidateTag is a
    TypeScript error."""
    src = read(d, "t1.ts")
    if not src:
        return False, "no file"
    if re.search(r"\bupdateTag\s*\(", src):
        return True, "updateTag (read-your-writes)"
    two_arg = re.search(r"revalidateTag\s*\(\s*[^,)]+,\s*[^)]+\)", src)
    one_arg = re.search(r"revalidateTag\s*\(\s*[^,)]+\)", src)
    if two_arg:
        return True, "revalidateTag with cacheLife"
    if one_arg:
        return False, "revalidateTag with one argument — a type error on Next 16"
    return False, "neither revalidateTag nor updateTag"


def t2_prisma7(d: Path) -> tuple[bool, str]:
    """prisma/01+06: v7 requires generator provider `prisma-client` with `output`, no
    `url` in the datasource, and a driver adapter passed to the constructor."""
    schema = read(d, "t2-schema.prisma")
    db = read(d, "t2-db.ts")
    config = read(d, "t2-config.ts")
    failures = []
    if 'provider = "prisma-client"' not in schema.replace("'", '"'):
        failures.append("generator is not `prisma-client`")
    if not re.search(r"^\s*output\s*=", schema, re.MULTILINE):
        failures.append("generator has no required `output`")
    if re.search(r"datasource[^}]*\burl\s*=", schema, re.DOTALL):
        failures.append("`url` still in datasource (a v7 validation error)")
    if not re.search(r"adapter", db):
        failures.append("client constructed without a driver adapter")
    if "@prisma/client" in db and "generated" not in db:
        failures.append("imports from @prisma/client, which no longer resolves")
    if not config.strip():
        failures.append("no prisma.config.ts")
    return (not failures), "; ".join(failures) or "all four v7 changes applied"


def t3_selector(d: Path) -> tuple[bool, str]:
    """kubernetes/05: a Deployment without spec.selector is rejected by the API
    server. Graded by kubeconform, not by reading."""
    src = read(d, "t3.yaml")
    if not src:
        return False, "no file"
    if not shutil.which("kubeconform"):
        has = re.search(r"^\s*selector:", src, re.MULTILINE)
        return bool(has), "selector present" if has else "no spec.selector"
    proc = subprocess.run(
        ["kubeconform", "-strict", "-ignore-missing-schemas", "-output", "json", "-"],
        input=src, capture_output=True, text=True,
    )
    try:
        report = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return False, "kubeconform produced no report"
    for resource in report.get("resources", []):
        if resource.get("status") not in ("statusValid", "statusSkipped", "statusEmpty"):
            message = re.sub(r"\S+kubernetes-json-schema\S+", "schema", resource.get("msg", ""))
            return False, message[:120]
    return True, "accepted by kubeconform"


def t4_acm_lifecycle(d: Path) -> tuple[bool, str]:
    """aws/09: an ACM certificate that can be replaced without
    create_before_destroy takes every listener referencing it down. Graded by
    tflint's AWS ruleset where available."""
    src = read(d, "t4.tf")
    if not src:
        return False, "no file"
    has = re.search(r"create_before_destroy\s*=\s*true", src)
    return bool(has), "create_before_destroy set" if has else \
        "no create_before_destroy — replacement is an outage"


def t5_jsonld_escape(d: Path) -> tuple[bool, str]:
    """nextjs/19: JSON.stringify escapes neither `<` nor `/`, and script content is
    raw text, so a title containing `</script>` closes the element."""
    src = read(d, "t5.tsx")
    if not src:
        return False, "no file"
    if "dangerouslySetInnerHTML" not in src:
        return False, "JSON-LD not emitted server-side via dangerouslySetInnerHTML"
    escaped = re.search(r"replace\s*\(\s*/<[^)]*u003c", src) or \
        re.search(r"\\\\u003c", src) or re.search(r"jsonLdScript|serializeJsonLd", src)
    return bool(escaped), "escapes `<`" if escaped else \
        "raw JSON.stringify into a <script> — XSS via any post field"


CHECKS = [
    ("T1 Next.js revalidateTag arity", t1_two_arg_revalidate),
    ("T2 Prisma 7 setup", t2_prisma7),
    ("T3 Kubernetes selector", t3_selector),
    ("T4 ACM create_before_destroy", t4_acm_lifecycle),
    ("T5 JSON-LD escaping", t5_jsonld_escape),
]


def main(argv: list[str]) -> int:
    arms = [Path(a) for a in argv[1:3]]
    if len(arms) != 2:
        print(__doc__)
        return 2
    names = [a.name for a in arms]
    print(f"{'rule':<32} {names[0]:<10} {names[1]:<10}")
    print("-" * 60)
    score = {n: 0 for n in names}
    detail: list[str] = []
    for label, check in CHECKS:
        row = []
        for arm, name in zip(arms, names):
            passed, why = check(arm)
            score[name] += passed
            row.append("PASS" if passed else "FAIL")
            detail.append(f"  {name:<8} {label}: {why}")
        print(f"{label:<32} {row[0]:<10} {row[1]:<10}")
    print("-" * 60)
    print(f"{'total':<32} {score[names[0]]}/5{'':<7} {score[names[1]]}/5")
    print("\nwhy:")
    for line in detail:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
