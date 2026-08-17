#!/usr/bin/env python3
"""Guardrail: every rule in the base must be findable by someone who does not know it exists.

`selftest-retrieval.py` asks 56 questions and all 56 land. That is a floor, not a
measurement: the questions were written alongside the metadata they match, and 56 of
1439 documents is 3.9% of the base. A document nobody wrote a question for can be
unreachable for a year without any check going red.

This asks the inverse, for every `ready` document: build a query from the document's
own *body* — `## Purpose` prose and its non-boilerplate headings, text no part of the
retrieval protocol scores against — and see whether the document comes back. Then it
checks the two paths `AGENTS.md` actually offers besides ranking:

    rank    the document is in the top five for a query drawn from its own content
    symbol  it is in `SIGNALS.symbols`, so an API name in a diff resolves to it
    index   the significant words of its title isolate it in `INDEX.md`, which is
            what `grep -i 'transactions' knowledge/INDEX.md` does

Losing `rank` is a metadata defect and is recorded in a baseline: 300-odd documents
lose it today, mostly by placing sixth behind five documents of the same subject, and
`grep` still finds every one of them. Losing **all three** is a hole — a rule that is
in the base and reachable only by someone who already knows its name. That fails
outright and is not baseline-able.

`--ablate` is why this exists as more than a regression net. The 52-question ablation
reports `terms` as worth exactly nothing; across all 1439 documents it is worth 20.
An ablation over 52 samples cannot tell a dead source of evidence from a rare one.

Exit code 0 = clean, 1 = a hole, or a document that lost `rank` since the baseline.

Usage:
    python3 scripts/check-reachability.py
    python3 scripts/check-reachability.py --ablate           # what each source is worth
    python3 scripts/check-reachability.py --selftest         # prove it can fail
    python3 scripts/check-reachability.py --update-baseline
"""
from __future__ import annotations

import functools
import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KB = ROOT / "knowledge"
BASELINE = ROOT / "scripts" / "data" / "reachability-baseline.json"

# A title has to isolate its document among this many INDEX.md rows to count as
# greppable. Twelve is the width of a topic's worth of near-namesakes — the eleven
# other `*/12-error-handling.md` rows plus the one wanted — and a reader scanning a
# dozen lines has found it. Two hundred is not finding it.
INDEX_ROWS = 12

# Headings every topic carries. They say nothing about the subject, so a query built
# from them would match the whole base equally.
BOILERPLATE = {
    "purpose", "related", "common mistakes", "examples", "why it matters",
    "ai review checklist", "core principles", "best practices", "production tips",
    "summary", "core principle", "verification", "completion criteria",
    "ai execution checklist", "investigation", "checklist", "rules", "overview",
    "good example", "bad example", "when to use", "notes", "references",
}


def load_protocol():
    """`selftest-retrieval.py` owns the scorer. Import it rather than restating it —
    two copies of a ranking rule drift, and then this check measures a protocol no
    agent follows."""
    spec = importlib.util.spec_from_file_location(
        "selftest_retrieval", ROOT / "scripts" / "selftest-retrieval.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    # Every document's `when_to_use` is tokenised once per query, 1439 times per run.
    # The function is pure and `retrieve` reads it off the module, so memoising it
    # here is free and turns minutes into seconds.
    module.tokens = functools.lru_cache(maxsize=None)(module.tokens)
    return module.Protocol()


def body_queries(path: Path) -> list[str]:
    """Two queries, both from text the scorer never sees: the Purpose prose, and the
    headings that name the document's own rules. Frontmatter and code are stripped —
    scoring a document against its own metadata would prove only that the file is
    internally consistent."""
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S)
    text = re.sub(r"```.*?```", " ", text, flags=re.S)

    queries = []
    purpose = re.search(r"^## Purpose\s*\n(.+?)(?=\n## |\Z)", text, flags=re.S | re.M)
    if purpose:
        queries.append(" ".join(purpose.group(1).split())[:400])
    headings = [
        h.strip() for h in re.findall(r"^##+\s+(.+?)\s*$", text, flags=re.M)
        if h.strip().lower() not in BOILERPLATE
    ]
    if headings:
        queries.append(" ".join(headings[:12]))
    return [q for q in queries if q.strip()]


def index_rows(index_md: str) -> list[str]:
    return [line for line in index_md.splitlines() if line.startswith("|")]


def greppable(doc: dict, rows: list[str], stopwords: set[str]) -> bool:
    """What `grep -i '<subject>' knowledge/INDEX.md` returns. A title that pulls back
    two hundred rows has not located anything.

    Short words are kept. Dropping them on length — the obvious filter — throws away
    `CI`, `CD`, `AI`, `S3`, `VM`, and then reports `CI/CD Overview` as unreachable
    while `grep -i 'ci/cd' knowledge/INDEX.md` lands on it directly. Only stopwords
    carry no subject."""
    words = [
        w for w in re.split(r"[^a-z0-9]+", doc["title"].lower())
        if len(w) > 1 and w not in stopwords
    ]
    if not words:
        return False
    hits = [r for r in rows if all(w in r.lower() for w in words)]
    return 0 < len(hits) <= INDEX_ROWS and any(doc["path"] in r for r in hits)


def assess(protocol, docs: list[dict], rows: list[str], read: callable,
           without: str = "") -> dict[str, dict]:
    """Per document: which of the three paths reach it. `read` is injected so the
    selftest can hand in a document whose body exists only in memory."""
    symbols = {d for ids in protocol.signals["symbols"].values() for d in ids}
    stopwords = sys.modules["selftest_retrieval"].STOPWORDS
    out = {}
    for doc in docs:
        queries = read(doc)
        # Body queries carry no repository files. Without assuming this document's
        # own variant, every `applies_to` rule is skipped and looks like a regression.
        ranked = any(
            doc["id"] in protocol.retrieve(
                q, [], [], without=without,
                assume_variants=doc.get("applies_to") or None,
            ) for q in queries
        )
        out[doc["id"]] = {
            "rank": ranked,
            "symbol": doc["id"] in symbols,
            "index": greppable(doc, rows, stopwords),
            "queried": bool(queries),
        }
    return out


def ready_docs() -> list[dict]:
    index = json.loads((KB / "INDEX.json").read_text(encoding="utf-8"))
    return [
        d for topic in index["topics"].values() for d in topic["docs"]
        if d["status"] == "ready"
    ]


def selftest(protocol, rows: list[str]) -> int:
    """A guardrail that has never failed is not evidence. Feed it one document that no
    path can reach and one that every path can, and require it to tell them apart."""
    hole = {
        "id": "phantom/01-unreachable", "topic": "phantom", "slug": "unreachable",
        "title": "Zzyzx Qwertyuiop", "path": "knowledge/phantom/01-unreachable.md",
        "tags": [], "when_to_use": "", "status": "ready",
    }
    real = dict(ready_docs()[0])
    bodies = {hole["id"]: ["zzyzx qwertyuiop plainly nonsense"],
              real["id"]: body_queries(ROOT / real["path"])}
    result = assess(protocol, [hole, real], rows, lambda d: bodies[d["id"]])

    failures = []
    if any(result[hole["id"]][path] for path in ("rank", "symbol", "index")):
        failures.append("a document reachable by nothing was reported as reachable")
    if not any(result[real["id"]][path] for path in ("rank", "symbol", "index")):
        failures.append(f"{real['id']} is reachable in the base but was reported as a hole")
    owned = next((d for d in ready_docs() if d["id"] == "nextjs/03-app-router"), None)
    if owned:
        owned_result = assess(
            protocol, [owned], rows, lambda d: body_queries(ROOT / d["path"]),
        )
        if not owned_result[owned["id"]]["rank"]:
            failures.append(
                "nextjs/03-app-router did not rank from its own body — "
                "applies_to is skipping it as if the repo were not App Router"
            )
    for message in failures:
        print(f"SELFTEST FAIL: {message}")
    if failures:
        return 1
    print("OK: the check separates a document nothing can reach from one the base can.")
    return 0


def main(argv: list[str]) -> int:
    protocol = load_protocol()
    rows = index_rows((KB / "INDEX.md").read_text(encoding="utf-8"))

    if "--selftest" in argv:
        return selftest(protocol, rows)

    docs = ready_docs()
    read = lambda d: body_queries(ROOT / d["path"])

    if "--ablate" in argv:
        print(f"What each source of evidence is worth, over all {len(docs)} documents.")
        print("A source the 52-question ablation calls worthless may simply be rare:\n")
        base = sum(1 for v in assess(protocol, docs, rows, read).values() if v["rank"])
        print(f"    every source        {base}/{len(docs)} reach their own content")
        # `stack` and `symbols` are not ablated here. A query drawn from a document's
        # body carries no repository files and no diff symbols, so both are already
        # empty and removing them would score a flat +0 — which would read as
        # "worthless" when it means "not under test". `selftest-retrieval.py --ablate`
        # is where those two are measured, because its cases supply them.
        for source in ("terms", "when_to_use", "tags", "task"):
            got = sum(
                1 for v in assess(protocol, docs, rows, read, without=source).values()
                if v["rank"]
            )
            print(f"    without {source:<12}{got}/{len(docs)}"
                  f"   ({got - base:+d})")
        print("\n`stack` and `symbols` are measured by selftest-retrieval.py --ablate; "
              "a query built\nfrom a document's own body supplies neither, so they "
              "cannot be ablated here.")
        return 0

    result = assess(protocol, docs, rows, read)
    by_id = {d["id"]: d for d in docs}
    holes = sorted(
        doc_id for doc_id, paths in result.items()
        if paths["queried"] and not any(paths[p] for p in ("rank", "symbol", "index"))
    )
    unranked = sorted(
        doc_id for doc_id, paths in result.items()
        if paths["queried"] and not paths["rank"]
    )

    if "--update-baseline" in argv:
        BASELINE.write_text(
            json.dumps(
                {"note": "Documents no longer in the top five for a query built from "
                         "their own body. Every one is still reachable by symbol or by "
                         "grep over INDEX.md; the cost is that ranking puts a sibling "
                         "first. A document that leaves this list has better metadata "
                         "than it did; one that joins it has worse.",
                 "unranked": unranked},
                indent=1,
            ) + "\n",
            encoding="utf-8",
        )
        print(f"baseline updated: {len(unranked)} documents recorded as rank-missed.")
        return 0

    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))["unranked"] \
        if BASELINE.exists() else []
    regressed = sorted(set(unranked) - set(baseline))

    reached = len(docs) - len(unranked)
    print(f"{len(docs)} ready documents")
    print(f"  reached by ranking their own content:  {reached}")
    print(f"  reached only by symbol or INDEX grep:  {len(unranked) - len(holes)}")
    print(f"  reached by nothing:                    {len(holes)}")

    if holes:
        print(f"\nFAIL: {len(holes)} document(s) state rules nothing can route an agent to.")
        for doc_id in holes[:25]:
            print(f"  {doc_id:<44} {by_id[doc_id].get('when_to_use', '')[:50]}")
        print("\nGive each one a `when_to_use` naming the situation it applies to, or a "
              "`tags`\nentry carrying an API name from its own examples, then rerun "
              "`build-signals.py`.")
        return 1

    if regressed:
        print(f"\nFAIL: {len(regressed)} document(s) lost their ranking since the baseline.")
        for doc_id in regressed[:25]:
            print(f"  {doc_id:<44} {by_id[doc_id].get('when_to_use', '')[:50]}")
        print("\nUsually a `when_to_use` edited into something more general than the "
              "document.\nIf the change is deliberate, record it with --update-baseline.")
        return 1

    recovered = sorted(set(baseline) - set(unranked))
    if recovered:
        print(f"\n{len(recovered)} document(s) now rank that did not: "
              f"{', '.join(recovered[:5])}"
              f"{'…' if len(recovered) > 5 else ''}")
        print("Run --update-baseline to keep the improvement from decaying back.")

    print(f"\nOK: every rule in the base is reachable, and no document's metadata "
          f"regressed\n({len(baseline)} recorded as reachable by symbol or grep but not "
          f"by rank).")
    print("by topic:", dict(Counter(d.split("/")[0] for d in unranked).most_common(8)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
