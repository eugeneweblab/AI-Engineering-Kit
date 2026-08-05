#!/usr/bin/env python3
"""Guardrail: structural, link, and code-block integrity for the knowledge base.

`check-ready-not-stub.py` protects against empty docs claiming `status: ready`.
This linter protects against the defect classes a full-base audit found in docs
that were neither empty nor stale — broken cross-links, wrong language tags, and
code blocks that do not parse in the language they claim:

  - `env: { TOKEN: ${{ github.token }} }` — a flow mapping that is not valid YAML,
    so the workflow it documents would not run;
  - backticks inside a `gql`/template literal, which terminate the string early;
  - `<pod>` / `<digest>` placeholders inside ```bash, which are shell redirects;
  - JSX inside a ```ts fence, CSS inside a ```js fence, Redis commands inside
    ```bash — all of which read as correct but break on copy.

None of these are visible by inspection; all of them are caught by handing each
block to the real parser for its declared language.

Checks
------
  structure   every standard topic has README/00/98/99/100 and no gap in 01..30
  frontmatter id/topic/order agree with the path; status/title/when_to_use present
  duplicates  no duplicate `id`, no duplicate `order` inside a topic
  links       markdown links, `related:` ids, and `knowledge/...md` paths resolve
  fences      every ``` fence is closed
  blocks      each fenced block parses as the language it is tagged with

Language coverage: Python, JSON (incl. JSONC and multi-document), YAML, shell.
PHP and JS/TS are checked only when `php` / `npx` are available, and only against
a baseline — see "Baseline" below.

Baseline
--------
Documentation legitimately contains code *fragments*: class-method excerpts, NestJS
parameter decorators, Bad/Good pairs that reuse a name, lists of sibling JSX
elements or function signatures. These never parse standalone and are not defects.
Rather than pretend otherwise, the PHP and JS/TS checks compare against
`scripts/codeblock-baseline.json`: known-acceptable blocks are ignored and a *new*
failure fails the build. Regenerate after an intentional change:

    python3 scripts/check-knowledge.py --update-baseline

Baseline entries are keyed by `<path>#<hash of the block source>`, not by position,
so inserting a section above a known fragment does not invalidate it — while editing
the fragment itself does, which is when it should be looked at again.

Exit code 0 = clean, 1 = violations found, 2 = bad invocation.

Usage:
    python3 scripts/check-knowledge.py [knowledge_dir]
    python3 scripts/check-knowledge.py --skip-external   # no php / npx
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Topics with their own layout, per docs/structure/frozen-structure-v1.md.
CUSTOM_STRUCTURE = {
    "ai", "engineering", "workflows", "figma",
    "examples", "templates", "prompts", "playbooks", "checklists", "snippets",
}
REQUIRED_ORDERS = {0, 98, 99, 100} | set(range(1, 31))

BASELINE_PATH = Path(__file__).with_name("codeblock-baseline.json")

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
FENCE_RE = re.compile(r"^```([a-zA-Z0-9_+.-]*)\s*$")
MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
BARE_PATH_RE = re.compile(r"`(knowledge/[\w./-]+\.md)`")

# Fence tag -> file extension handed to the parser.
JS_FAMILY = {"ts": "ts", "typescript": "ts", "tsx": "tsx",
             "js": "js", "javascript": "js", "jsx": "jsx"}
SHELL_TAGS = {"bash", "sh", "shell", "zsh"}
PYTHON_TAGS = {"python", "py"}
JSON_TAGS = {"json", "jsonc", "json5"}
YAML_TAGS = {"yaml", "yml"}


class Doc:
    """A parsed knowledge document: frontmatter fields, body, and fenced blocks."""

    def __init__(self, path: Path, root: Path):
        self.path = path
        self.rel = path.relative_to(root.parent)
        text = path.read_text(encoding="utf-8", errors="replace")
        m = FRONTMATTER_RE.match(text)
        self.has_frontmatter = m is not None
        self.fm: dict[str, str] = {}
        self.related: list[str] = []
        if m:
            self._parse_frontmatter(m.group(1))
            self.body = text[m.end():]
        else:
            self.body = text
        self.lines = text.split("\n")
        self.blocks = self._parse_blocks()

    def _parse_frontmatter(self, raw: str) -> None:
        key = None
        for line in raw.split("\n"):
            kv = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
            if kv:
                key, value = kv.group(1), kv.group(2).strip()
                self.fm[key] = value
                if key == "related" and value.startswith("["):
                    self.related = [
                        v.strip().strip("\"'") for v in value[1:-1].split(",") if v.strip()
                    ]
                continue
            item = re.match(r"^\s+-\s+(.*)$", line)
            if item and key == "related":
                self.related.append(item.group(1).strip().strip("\"'"))

    def _parse_blocks(self) -> list[tuple[str, str, int]]:
        """Return [(tag, source, opening_line_number)] for every fenced block."""
        blocks: list[tuple[str, str, int]] = []
        i = 0
        while i < len(self.lines):
            m = FENCE_RE.match(self.lines[i])
            if not m:
                i += 1
                continue
            opened_at, tag, body = i + 1, m.group(1).lower(), []
            i += 1
            while i < len(self.lines) and not self.lines[i].startswith("```"):
                body.append(self.lines[i])
                i += 1
            i += 1
            blocks.append((tag, "\n".join(body), opened_at))
        return blocks

    @property
    def fences_balanced(self) -> bool:
        return sum(1 for line in self.lines if line.startswith("```")) % 2 == 0

    def body_without_code(self) -> str:
        stripped = re.sub(r"```.*?```", "", self.body, flags=re.DOTALL)
        return re.sub(r"`[^`\n]*`", "", stripped)


def strip_jsonc(src: str) -> str:
    """Remove // and /* */ comments outside string literals, and trailing commas."""
    out, i, n, in_string, escaped = [], 0, len(src), False, False
    while i < n:
        ch = src[i]
        if in_string:
            out.append(ch)
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            i += 1
            continue
        if ch == '"':
            in_string = True
            out.append(ch)
            i += 1
            continue
        if ch == "/" and i + 1 < n and src[i + 1] == "/":
            while i < n and src[i] != "\n":
                i += 1
            continue
        if ch == "/" and i + 1 < n and src[i + 1] == "*":
            i += 2
            while i + 1 < n and not (src[i] == "*" and src[i + 1] == "/"):
                i += 1
            i += 2
            continue
        out.append(ch)
        i += 1
    return re.sub(r",(\s*[}\]])", r"\1", "".join(out))


def check_json(src: str) -> str | None:
    """Accept one JSON value, or several concatenated ones (a listing of examples)."""
    text = strip_jsonc(src).strip()
    if not text:
        return None
    decoder, idx = json.JSONDecoder(), 0
    try:
        while idx < len(text):
            _, end = decoder.raw_decode(text, idx)
            idx = end
            while idx < len(text) and text[idx] in " \t\r\n,":
                idx += 1
    except ValueError as exc:
        return str(exc).split("\n")[0]
    return None


def check_python(src: str) -> str | None:
    import ast
    try:
        ast.parse(src)
    except SyntaxError as exc:
        return f"{exc.msg} (line {exc.lineno})"
    return None


def check_yaml(src: str, yaml_mod) -> str | None:
    try:
        # compose_all parses structure without resolving aliases or constructing objects
        list(yaml_mod.compose_all(src))
    except Exception as exc:  # noqa: BLE001 — any parser error is a finding
        return str(exc).split("\n")[0]
    return None


def run_shell_checks(blocks: list[tuple[str, str, str]]) -> list[tuple[str, str]]:
    """blocks: [(block_id, source, _)] -> [(block_id, error)] using `bash -n`."""
    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        script = Path(tmp) / "block.sh"
        for block_id, src, _ in blocks:
            script.write_text(src, encoding="utf-8")
            proc = subprocess.run(
                ["bash", "-n", str(script)], capture_output=True, text=True
            )
            if proc.returncode != 0:
                message = (proc.stderr or "").strip().split("\n")[-1]
                failures.append((block_id, message.replace(str(script), "block")))
    return failures


def run_php_checks(blocks: list[tuple[str, str, str]]) -> list[tuple[str, str]]:
    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        script = Path(tmp) / "block.php"
        for block_id, src, _ in blocks:
            source = src if src.lstrip().startswith("<?php") else "<?php\n" + src
            script.write_text(source, encoding="utf-8")
            proc = subprocess.run(
                ["php", "-l", str(script)], capture_output=True, text=True
            )
            if proc.returncode != 0:
                out = (proc.stdout or proc.stderr or "").strip().split("\n")[0]
                out = re.sub(r" in /.*", "", out).replace("PHP Parse error:  ", "")
                failures.append((block_id, out.strip()))
    return failures


ESBUILD_ERROR_RE = re.compile(r"✘ \[ERROR\] ([^\n]+)\n\n\s+([\w.\-]+):(\d+):")


def run_js_checks(blocks: list[tuple[str, str, str]]) -> list[tuple[str, str]] | None:
    """One esbuild invocation over every block. Returns None if esbuild is unavailable."""
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir, names = Path(tmp), {}
        for n, (block_id, src, ext) in enumerate(blocks):
            name = f"b{n}.{ext}"
            names[name] = block_id
            (tmpdir / name).write_text(src, encoding="utf-8")
        # NestJS parameter decorators (@Body(), @Param()) are valid TypeScript only
        # with experimentalDecorators. Enable it so real defects are not buried under
        # 80 spurious errors.
        tsconfig = '{"compilerOptions":{"experimentalDecorators":true}}'
        proc = subprocess.run(
            ["npx", "--yes", "esbuild@0.24.0", "--log-limit=0",
             f"--tsconfig-raw={tsconfig}",
             f"--outdir={tmpdir / '_out'}", *sorted(names)],
            capture_output=True, text=True, cwd=tmpdir,
        )
        output = (proc.stderr or "") + (proc.stdout or "")
        if not ESBUILD_ERROR_RE.search(output) and proc.returncode != 0:
            return None  # esbuild could not run at all (offline, npx missing)
        return [
            (names[name], message)
            for message, name, _ in ESBUILD_ERROR_RE.findall(output)
            if name in names
        ]


def collect(root: Path) -> list[Doc]:
    return [Doc(p, root) for p in sorted(root.rglob("*.md"))]


def check_structure(root: Path, problems: list[str]) -> None:
    for topic_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        topic = topic_dir.name
        if topic in CUSTOM_STRUCTURE:
            continue
        names = {f.name for f in topic_dir.glob("*.md")}
        orders = {int(m.group(1)) for f in names if (m := re.match(r"^(\d+)-", f))}
        if "README.md" not in names:
            problems.append(f"{topic}/: no README.md")
        for missing in sorted(REQUIRED_ORDERS - orders):
            problems.append(f"{topic}/: no document with order {missing:02d}")


def check_docs(root: Path, docs: list[Doc], problems: list[str]) -> None:
    seen_ids: dict[str, str] = {}
    seen_orders: dict[tuple[str, int], str] = {}
    for doc in docs:
        rel = doc.rel
        if not doc.has_frontmatter:
            if doc.path.parent == root:
                continue  # README/TEMPLATE/STYLE_GUIDE at the root carry no frontmatter
            problems.append(f"{rel}: no frontmatter")
            continue
        if not doc.fences_balanced:
            problems.append(f"{rel}: unbalanced ``` fence")

        topic = doc.path.parent.name
        fm = doc.fm
        if doc.path.name != "README.md":
            expected_id = f"{topic}/{doc.path.stem}"
            if fm.get("id") != expected_id:
                problems.append(f"{rel}: id is {fm.get('id')!r}, expected {expected_id!r}")
            if fm.get("topic") != topic:
                problems.append(f"{rel}: topic is {fm.get('topic')!r}, expected {topic!r}")
            prefix = re.match(r"^(\d+)-", doc.path.name)
            if prefix:
                want = str(int(prefix.group(1)))
                if fm.get("order") != want:
                    problems.append(f"{rel}: order is {fm.get('order')!r}, expected {want!r}")
                key = (topic, int(want))
                if key in seen_orders:
                    problems.append(f"{rel}: order {want} already used by {seen_orders[key]}")
                seen_orders[key] = str(rel)

        if fm.get("status") not in ("ready", "draft"):
            problems.append(f"{rel}: status is {fm.get('status')!r}, expected ready or draft")
        if not fm.get("title"):
            problems.append(f"{rel}: title is empty")
        if not fm.get("when_to_use", "").strip('"\' '):
            problems.append(f"{rel}: when_to_use is empty")

        doc_id = fm.get("id")
        if doc_id:
            if doc_id in seen_ids:
                problems.append(f"{rel}: duplicate id {doc_id!r} (also {seen_ids[doc_id]})")
            seen_ids[doc_id] = str(rel)


def check_links(root: Path, docs: list[Doc], problems: list[str]) -> int:
    repo = root.parent
    checked = 0
    for doc in docs:
        for target in MD_LINK_RE.findall(doc.body_without_code()):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            checked += 1
            path, _, anchor = target.partition("#")
            if not path:
                continue
            if not (doc.path.parent / path).exists() and not (repo / path).exists():
                problems.append(f"{doc.rel}: broken link -> {target}")
        for related_id in doc.related:
            checked += 1
            if not (root / f"{related_id}.md").exists() and not (root / related_id).exists():
                problems.append(f"{doc.rel}: related -> {related_id} does not exist")
        for bare in BARE_PATH_RE.findall(doc.body):
            checked += 1
            if not (repo / bare).exists():
                problems.append(f"{doc.rel}: path reference -> {bare} does not exist")
    return checked


def check_blocks(docs: list[Doc], problems: list[str], skip_external: bool,
                 baseline: dict, update_baseline: bool) -> dict[str, int]:
    try:
        import yaml as yaml_mod
    except ImportError:
        yaml_mod = None

    counts = {"python": 0, "json": 0, "yaml": 0, "shell": 0, "php": 0, "js": 0}
    shell_blocks: list[tuple[str, str, str]] = []
    php_blocks: list[tuple[str, str, str]] = []
    js_blocks: list[tuple[str, str, str]] = []

    for doc in docs:
        for tag, src, line in doc.blocks:
            if tag in JS_FAMILY:
                family = "js"
            elif tag == "php":
                family = "php"
            elif tag in SHELL_TAGS:
                family = "shell"
            elif tag in PYTHON_TAGS:
                family = "python"
            elif tag in JSON_TAGS:
                family = "json"
            elif tag in YAML_TAGS:
                family = "yaml"
            else:
                continue
            # Key by content hash, not position: inserting a section above a known
            # fragment must not invalidate its baseline entry.
            digest = hashlib.sha1(src.encode("utf-8")).hexdigest()[:10]
            block_id = f"{doc.rel}#{digest}"
            counts[family] += 1

            if family == "python":
                if (err := check_python(src)):
                    problems.append(f"{doc.rel}:{line}: ```python does not parse — {err}")
            elif family == "json":
                if (err := check_json(src)):
                    problems.append(f"{doc.rel}:{line}: ```{tag} does not parse — {err}")
            elif family == "yaml" and yaml_mod:
                if (err := check_yaml(src, yaml_mod)):
                    problems.append(f"{doc.rel}:{line}: ```{tag} does not parse — {err}")
            elif family == "shell":
                shell_blocks.append((block_id, src, tag))
            elif family == "php":
                php_blocks.append((block_id, src, tag))
            elif family == "js":
                js_blocks.append((block_id, src, JS_FAMILY[tag]))

    if yaml_mod is None:
        print("  note: PyYAML not installed — YAML blocks were not checked")

    for block_id, err in run_shell_checks(shell_blocks):
        problems.append(f"{block_id}: shell block does not parse — {err}")

    # PHP and JS/TS are fragment-heavy; compare against the baseline instead.
    for family, blocks, runner, tool in (
        ("php", php_blocks, run_php_checks, "php"),
        ("js", js_blocks, run_js_checks, "npx"),
    ):
        if skip_external or not blocks or not shutil.which(tool):
            if not skip_external and blocks and not shutil.which(tool):
                print(f"  note: `{tool}` not found — {family} blocks were not checked")
            baseline.setdefault(family, baseline.get(family, []))
            continue
        result = runner(blocks)
        if result is None:
            print(f"  note: esbuild unavailable — {family} blocks were not checked")
            continue
        failing = sorted({block_id for block_id, _ in result})
        if update_baseline:
            baseline[family] = failing
            continue
        known = set(baseline.get(family, []))
        for block_id, err in result:
            if block_id not in known:
                problems.append(f"{block_id}: {family} block does not parse — {err}")
    return counts


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    flags = {a for a in argv[1:] if a.startswith("--")}
    unknown = flags - {"--skip-external", "--update-baseline"}
    if unknown:
        print(f"error: unknown option(s): {', '.join(sorted(unknown))}", file=sys.stderr)
        return 2
    root = Path(args[0]) if args else Path("knowledge")
    if not root.exists():
        print(f"error: {root} not found", file=sys.stderr)
        return 2

    update_baseline = "--update-baseline" in flags
    baseline = {}
    if BASELINE_PATH.exists():
        baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))

    docs = collect(root)
    problems: list[str] = []

    check_structure(root, problems)
    check_docs(root, docs, problems)
    n_links = check_links(root, docs, problems)
    counts = check_blocks(docs, problems, "--skip-external" in flags,
                          baseline, update_baseline)

    if update_baseline:
        baseline["_comment"] = (
            "Code blocks that are intentional fragments — class-method excerpts, "
            "parameter decorators, Bad/Good pairs reusing a name, lists of sibling "
            "JSX elements or function signatures. They never parse standalone and "
            "are not defects. Regenerate with: "
            "python3 scripts/check-knowledge.py --update-baseline"
        )
        ordered = {"_comment": baseline["_comment"]}
        for key in sorted(k for k in baseline if k != "_comment"):
            ordered[key] = baseline[key]
        BASELINE_PATH.write_text(json.dumps(ordered, indent=2) + "\n", encoding="utf-8")
        total = sum(len(v) for k, v in ordered.items() if k != "_comment")
        print(f"Baseline written to {BASELINE_PATH} ({total} known fragments).")
        return 0

    summary = ", ".join(f"{v} {k}" for k, v in counts.items() if v)
    print(f"Checked {len(docs)} docs, {n_links} links, code blocks: {summary}.")

    if problems:
        print(f"\nFAIL: {len(problems)} problem(s)\n")
        for problem in problems:
            print(f"  {problem}")
        return 1

    print("OK: structure, frontmatter, links, and code blocks are all clean.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
