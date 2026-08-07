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
  frontmatter id/topic/order agree with the path; status/when_to_use present; title
              matches the document's H1
  duplicates  no duplicate `id`, no duplicate `title`, no duplicate `order` in a topic
  links       markdown links, `related:` ids, and `knowledge/...md` paths resolve
  fences      every ``` fence is closed; no zero-width characters in the body
  blocks      each fenced block parses as the language it is tagged with
  tables      no unescaped `|` inside a table cell
  plan        docs/structure/ still describes the tree that exists on disk
  pointers    98/99 checklists route each themed section to the rule behind it

Language coverage: Python, JSON (incl. JSONC and multi-document), YAML, XML, nginx,
HCL, INI, GraphQL, Dockerfile, HTTP, diff, cron, Makefile, Redis, Go, Lua, shell.
PHP, JS/TS, SQL, HTML, and CSS are checked only when `php`, `npx`, or `sqlfluff`
is available, and only against a baseline — see "Baseline" below.

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

A language whose parser is unavailable is skipped and named in the output. Pass
`--require-tools` to make that a failure instead — use it in CI, where a silently
skipped language means the build went green without checking anything.

Usage:
    python3 scripts/check-knowledge.py [knowledge_dir]
    python3 scripts/check-knowledge.py --require-tools    # skip == failure
    python3 scripts/check-knowledge.py --skip-external    # no php / npx / hadolint
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

# `type` tells an agent what kind of artifact this is, so it can filter by role:
# a rule document, the topic index, a verification list, a copyable template.
DOC_TYPES = {"doc", "index", "checklist", "antipatterns", "workflow",
             "template", "playbook", "prompt", "snippet", "example"}

# Variants a document can be specific to. Applying a rule under the wrong variant
# is not a near miss — App Router caching advice is simply wrong on the Pages
# Router, and block-theme guidance does not apply to a classic theme.
VARIANTS = {"app-router", "pages-router", "block-theme", "classic-theme",
            "typeorm", "prisma"}

BASELINE_PATH = Path(__file__).with_name("codeblock-baseline.json")

# Languages whose parser was unavailable this run. A missing tool must never read as
# "clean": a silent skip is how a green build stops checking anything at all.
SKIPPED: dict[str, str] = {}

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
FENCE_RE = re.compile(r"^```([a-zA-Z0-9_+.-]*)\s*$")
MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
# Deliberately loose: a strict character class silently skips a malformed reference
# instead of reporting it, which is how `knowledge/"react/21-testing".md` once slipped
# through. Match anything backticked that starts with knowledge/, then validate it.
BARE_PATH_RE = re.compile(r"`(knowledge/[^`\n]*)`")

# Fence tag -> file extension handed to the parser.
JS_FAMILY = {"ts": "ts", "typescript": "ts", "tsx": "tsx",
             "js": "js", "javascript": "js", "jsx": "jsx"}
SHELL_TAGS = {"bash", "sh", "shell", "zsh"}
SQL_TAGS = {"sql"}
HTML_TAGS = {"html"}
CSS_TAGS = {"css", "scss"}
# sqlfluff needs a dialect; the base is Postgres-flavoured except where a topic
# is explicitly MySQL-family.
MYSQL_TOPICS = {"mysql", "wordpress", "woocommerce", "divi"}
PYTHON_TAGS = {"python", "py"}
JSON_TAGS = {"json", "jsonc", "json5"}
YAML_TAGS = {"yaml", "yml"}
XML_TAGS = {"xml", "svg"}
NGINX_TAGS = {"nginx", "conf", "apache"}
HCL_TAGS = {"hcl", "tf"}
INI_TAGS = {"ini", "gitconfig", "neon"}
GRAPHQL_TAGS = {"graphql", "gql"}
DOCKERFILE_TAGS = {"dockerfile", "containerfile"}
HTTP_TAGS = {"http", "rest"}
DIFF_TAGS = {"diff", "patch"}
CRON_TAGS = {"cron", "crontab"}
MAKE_TAGS = {"makefile", "make"}
REDIS_TAGS = {"redis"}
GO_TAGS = {"go", "golang"}
LUA_TAGS = {"lua"}
# hadolint codes that mean the Dockerfile is wrong, not merely unidiomatic. Style
# rules are excluded: a Bad Example uses `:latest` and shell-form CMD on purpose,
# and an excerpt legitimately does not begin with FROM (DL3061).
HADOLINT_CODES = {"DL1000", "DL3021", "DL3022", "DL3023", "DL3024"}


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


def run_dockerfile_checks(blocks: list[tuple[str, str, str]]) -> list[tuple[str, str]] | None:
    """hadolint, restricted to the codes that break a build.

    `COPY a b # comment` is not a comment — Docker treats a mid-line `#` as an
    argument, so the instruction gets an extra one and the build fails. That is
    DL3021; DL1000 is the parser itself.
    """
    if not shutil.which("hadolint"):
        return None
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir, names = Path(tmp), {}
        for n, (block_id, src, _) in enumerate(blocks):
            name = f"b{n}.Dockerfile"
            names[name] = block_id
            (tmpdir / name).write_text(src, encoding="utf-8")
        proc = subprocess.run(
            ["hadolint", "--format", "json", *sorted(names)],
            capture_output=True, text=True, cwd=tmpdir,
        )
        try:
            report = json.loads(proc.stdout or "[]")
        except ValueError:
            return None
        return [
            (names[entry["file"]], f"{entry['code']}: {entry['message'][:80]}")
            for entry in report
            if entry.get("code") in HADOLINT_CODES and entry.get("file") in names
        ]


HTTP_METHODS = {"GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "TRACE",
                "CONNECT"}
HTTP_VERSIONS = {"1.0", "1.1", "2", "3"}
HTTP_REQUEST_RE = re.compile(r"^([A-Z]+)\s+(\S+)\s+HTTP/(\d(?:\.\d)?)\s*$")
HTTP_STATUS_RE = re.compile(r"^HTTP/(\d(?:\.\d)?)\s+(\d{3})(?:\s+(.*))?$")
HTTP_VERBLESS_RE = re.compile(r"^([A-Z][A-Z-]{2,})\s+(\S+)")


def check_http(src: str) -> str | None:
    """Request and status lines. The version is optional: `.http` client files write
    `GET {{baseUrl}}/orders` with no version, and that form is used here too."""
    for n, raw in enumerate(src.split("\n"), 1):
        line = re.sub(r"\s+#.*$", "", raw).rstrip()
        if not line or line.startswith(("#", "//")):
            continue
        if line.startswith("HTTP/"):
            m = HTTP_STATUS_RE.match(line)
            if not m:
                return f"line {n}: malformed status line: {line[:50]}"
            if m.group(1) not in HTTP_VERSIONS:
                return f"line {n}: HTTP/{m.group(1)} is not a version"
            if not 100 <= int(m.group(2)) <= 599:
                return f"line {n}: status {m.group(2)} is outside 100-599"
            continue
        m = HTTP_REQUEST_RE.match(line)
        if m:
            if m.group(1) not in HTTP_METHODS:
                return f"line {n}: {m.group(1)!r} is not an HTTP method"
            if m.group(3) not in HTTP_VERSIONS:
                return f"line {n}: HTTP/{m.group(3)} is not a version"
            continue
        m = HTTP_VERBLESS_RE.match(line)
        if m and ":" not in m.group(1) and m.group(1) not in HTTP_METHODS:
            return f"line {n}: {m.group(1)!r} is not an HTTP method"
    return None


DIFF_META = ("diff ", "index ", "--- ", "+++ ", "new file", "deleted file",
             "similarity", "rename ", "old mode", "new mode")


def check_diff(src: str) -> str | None:
    """Every line of a patch carries a prefix. One without it is dropped by
    `git apply`, so the example does not apply as shown."""
    for n, line in enumerate(src.split("\n"), 1):
        if not line.strip() or line.startswith(DIFF_META):
            continue
        if not line.startswith((" ", "+", "-", "\\", "@")):
            return f"line {n}: no ' ', '+' or '-' prefix — the patch drops it: {line[:50]}"
    return None


CRON_FIELD_RE = re.compile(r"^[\d*/,\-]+$")
CRON_SPECIAL = {"@reboot", "@yearly", "@annually", "@monthly", "@weekly", "@daily",
                "@midnight", "@hourly"}
CRON_RANGES = ((0, 59), (0, 23), (1, 31), (1, 12), (0, 7))


def check_cron(src: str) -> str | None:
    for n, line in enumerate(src.split("\n"), 1):
        s = line.strip()
        if not s or s.startswith("#") or re.match(r"^[A-Z_][A-Z0-9_]*=", s):
            continue
        if s.split()[0] in CRON_SPECIAL:
            continue
        parts = s.split()
        if len(parts) < 6:
            return f"line {n}: fewer than five schedule fields plus a command: {s[:50]}"
        for i, field in enumerate(parts[:5]):
            if not CRON_FIELD_RE.match(field):
                return f"line {n}: field {i + 1} {field!r} is not a schedule field"
            low, high = CRON_RANGES[i]
            for number in re.findall(r"\d+", field):
                if not low <= int(number) <= high:
                    return f"line {n}: field {i + 1} value {number} is outside {low}-{high}"
    return None


def check_makefile(src: str) -> str | None:
    """A recipe line must start with a tab. Spaces are the classic Makefile error:
    make reports "missing separator" and the target does nothing."""
    in_recipe = False
    for n, line in enumerate(src.split("\n"), 1):
        if not line.strip():
            in_recipe = False
            continue
        if line.startswith("#"):
            continue
        if re.match(r"^[^\s#].*:", line):
            in_recipe = ";" not in line.split(":", 1)[1]
            continue
        if re.match(r"^[A-Za-z_.][\w.]*\s*[:?+]?=", line):
            in_recipe = False
            continue
        if in_recipe and line.startswith(" ") and not line.startswith("\t"):
            return f"line {n}: recipe indented with spaces, not a tab: {line[:40]!r}"
    return None


REDIS_COMMANDS = set("""
GET SET SETNX SETEX PSETEX MSET MGET GETSET GETDEL GETEX APPEND STRLEN INCR DECR INCRBY
DECRBY INCRBYFLOAT DEL UNLINK EXISTS EXPIRE PEXPIRE EXPIREAT TTL PTTL PERSIST TYPE RENAME
KEYS SCAN RANDOMKEY DBSIZE FLUSHDB FLUSHALL LPUSH RPUSH LPOP RPOP LRANGE LLEN LINDEX LSET
LREM LTRIM LMOVE RPOPLPUSH BLPOP BRPOP BLMOVE SADD SREM SMEMBERS SISMEMBER SMISMEMBER SCARD
SPOP SRANDMEMBER SINTER SUNION SDIFF SINTERSTORE SUNIONSTORE SDIFFSTORE SSCAN ZADD ZREM
ZSCORE ZINCRBY ZCARD ZCOUNT ZRANGE ZREVRANGE ZRANGEBYSCORE ZREVRANGEBYSCORE ZRANK ZREVRANK
ZREMRANGEBYRANK ZREMRANGEBYSCORE ZSCAN ZPOPMIN ZPOPMAX ZRANGESTORE HSET HSETNX HGET HMGET
HGETALL HDEL HEXISTS HLEN HKEYS HVALS HINCRBY HSCAN HRANDFIELD XADD XLEN XRANGE XREVRANGE
XREAD XREADGROUP XGROUP XACK XPENDING XCLAIM XAUTOCLAIM XTRIM XDEL XINFO SUBSCRIBE
UNSUBSCRIBE PSUBSCRIBE PUNSUBSCRIBE PUBLISH PUBSUB SPUBLISH SSUBSCRIBE MULTI EXEC DISCARD
WATCH UNWATCH EVAL EVALSHA SCRIPT FUNCTION FCALL PFADD PFCOUNT PFMERGE SETBIT GETBIT
BITCOUNT BITOP BITPOS BITFIELD GEOADD GEOSEARCH GEODIST GEOPOS GEOHASH INFO CONFIG CLIENT
COMMAND MEMORY SLOWLOG LATENCY MONITOR DEBUG ACL AUTH PING ECHO SELECT SWAPDB WAIT RESET
HELLO CLUSTER REPLICAOF SLAVEOF FAILOVER SAVE BGSAVE BGREWRITEAOF LASTSAVE SHUTDOWN LOLWUT
OBJECT DUMP RESTORE MIGRATE COPY MOVE TOUCH SORT SETRANGE GETRANGE SINTERCARD LPOS SMOVE
ZDIFF ZUNION ZINTER ZMSCORE
""".split())


def check_redis(src: str) -> str | None:
    for n, line in enumerate(src.split("\n"), 1):
        s = re.sub(r"\s+#.*$", "", line).strip()
        if not s or s.startswith("#") or s.startswith((">", "$", "(", '"', "'")):
            continue
        if s[0].islower():
            continue
        first = s.split()[0].upper().rstrip(":")
        if first.isalpha() and first not in REDIS_COMMANDS:
            return f"line {n}: {first!r} is not a Redis command"
    return None


def run_go_checks(blocks: list[tuple[str, str, str]]) -> list[tuple[str, str]] | None:
    """`gofmt -e`. A fragment is wrapped so it becomes parseable Go: documents show a
    method or a few statements, never a whole file."""
    if not shutil.which("gofmt"):
        return None
    top_level = re.compile(r"^\s*(package|import|func|type|var|const)\b")
    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "block.go"
        for block_id, src, _ in blocks:
            first = next(
                (l for l in src.split("\n") if l.strip() and not l.strip().startswith("//")),
                "",
            )
            if first.startswith("package "):
                source = src
            elif top_level.match(first):
                source = "package p\n\n" + src
            else:
                source = "package p\n\nfunc _() {\n" + src + "\n}"
            path.write_text(source, encoding="utf-8")
            proc = subprocess.run(["gofmt", "-e", "-l", str(path)],
                                  capture_output=True, text=True)
            if proc.stderr.strip():
                message = proc.stderr.strip().split("\n")[0].split(":", 1)[-1]
                failures.append((block_id, message[:90]))
    return failures


def run_lua_checks(blocks: list[tuple[str, str, str]]) -> list[tuple[str, str]] | None:
    if not shutil.which("luac"):
        return None
    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "block.lua"
        for block_id, src, _ in blocks:
            path.write_text(src, encoding="utf-8")
            proc = subprocess.run(["luac", "-p", "-o", "/dev/null", str(path)],
                                  capture_output=True, text=True)
            if proc.returncode:
                failures.append((block_id, proc.stderr.strip().split(":", 2)[-1][:90]))
    return failures


def check_nginx(src: str) -> str | None:
    """crossplane, with context and argument validation off.

    A doc shows a `server {}` or `location {}` on its own; crossplane would reject
    those as "not allowed here" because the enclosing `http {}` is not in the excerpt.
    Only the syntax is ours to check.
    """
    try:
        import crossplane
    except ImportError:
        SKIPPED["nginx"] = "crossplane"
        return None
    with tempfile.NamedTemporaryFile("w", suffix=".conf", delete=False, encoding="utf-8") as fh:
        fh.write(src)
        path = fh.name
    payload = crossplane.parse(path, catch_errors=True, check_ctx=False, check_args=False)
    for entry in payload.get("errors") or []:
        message = str(entry.get("error"))
        if "No such file" in message:      # an `include` the excerpt cannot resolve
            continue
        return message[:90]
    return None


def check_hcl(src: str) -> str | None:
    try:
        import hcl2
    except ImportError:
        SKIPPED["hcl"] = "hcl2"
        return None
    try:
        hcl2.loads(src)
    except Exception as exc:  # noqa: BLE001
        return str(exc).split("\n")[0][:90]
    return None


def check_ini(src: str) -> str | None:
    """A synthetic section header: postgresql.conf and php.ini fragments are
    key/value without one, and that is correct for the file they come from.

    `allow_no_value` stays off deliberately: with it on, configparser accepts almost
    any line and the check has no power — it did not notice an unclosed `[section`.
    """
    import configparser
    parser = configparser.ConfigParser(strict=False, allow_no_value=False, interpolation=None)
    try:
        parser.read_string("[__root__]\n" + src)
    except Exception as exc:  # noqa: BLE001
        return str(exc).split("\n")[0][:90]
    return None


def check_graphql(src: str) -> str | None:
    try:
        from graphql import parse as graphql_parse
    except ImportError:
        SKIPPED["graphql"] = "graphql-core"
        return None
    try:
        graphql_parse(src)
    except Exception as exc:  # noqa: BLE001
        return str(exc).split("\n")[0][:90]
    return None


def check_xml(src: str) -> str | None:
    """A sitemap or feed is rejected outright when the declaration is not first."""
    import xml.etree.ElementTree as ET
    try:
        ET.fromstring(src.strip())
    except Exception as exc:  # noqa: BLE001
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


def have(tool: str) -> bool:
    """Is the tool runnable? `pip install sqlfluff` puts the console script in a bin
    directory that is not always on PATH, while the module is importable either way —
    a PATH-only check silently skipped 214 SQL blocks."""
    if shutil.which(tool):
        return True
    if tool in PIP_TOOLS:
        return subprocess.run([sys.executable, "-m", tool, "--version"],
                              capture_output=True).returncode == 0
    return False


PIP_TOOLS = {"sqlfluff"}


def run_sql_checks(blocks: list[tuple[str, str, str]]) -> list[tuple[str, str]] | None:
    """`sqlfluff lint --rules PRS`, one process per dialect.

    Per-block invocation cost ~2s of interpreter startup, which put a full run past
    ten minutes; batching by dialect brings it under a second.
    """
    # pip installs the console script into a bin directory that is not always on
    # PATH; the module is there either way. Falling back on it is the difference
    # between checking 214 SQL blocks and silently skipping them.
    if shutil.which("sqlfluff"):
        sqlfluff = ["sqlfluff"]
    elif have("sqlfluff"):
        sqlfluff = [sys.executable, "-m", "sqlfluff"]
    else:
        return None
    failures: list[tuple[str, str]] = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        names: dict[str, str] = {}
        by_dialect: dict[str, list[str]] = {}
        for n, (block_id, src, dialect) in enumerate(blocks):
            sub = root / dialect
            sub.mkdir(exist_ok=True)
            name = f"b{n}.sql"
            (sub / name).write_text(src, encoding="utf-8")
            names[f"{dialect}/{name}"] = block_id
            by_dialect.setdefault(dialect, []).append(name)

        for dialect in by_dialect:
            proc = subprocess.run(
                [*sqlfluff, "lint", "--format", "json",
                 "--dialect", dialect, "--rules", "PRS", dialect],
                capture_output=True, text=True, cwd=root,
            )
            try:
                report = json.loads(proc.stdout or "[]")
            except ValueError:
                return None
            for entry in report:
                key = entry.get("filepath", "").lstrip("./")
                block_id = names.get(key)
                violations = [v for v in entry.get("violations", []) if v.get("code") == "PRS"]
                if block_id and violations:
                    failures.append((block_id, violations[0].get("description", "unparsable")[:90]))
    return failures


HTML_SYNTAX_RULES = {"parser-error", "close-order", "unclosed-element"}


def run_html_checks(blocks: list[tuple[str, str, str]]) -> list[tuple[str, str]] | None:
    """html-validate, restricted to the syntax rules. Style and a11y rules are not
    applied: a Bad Example is often invalid on purpose, but never unparseable."""
    if not shutil.which("npx"):
        return None
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir, names = Path(tmp), {}
        (tmpdir / ".htmlvalidate.json").write_text(
            json.dumps({"root": True, "extends": ["html-validate:recommended"]}),
            encoding="utf-8",
        )
        for n, (block_id, src, _) in enumerate(blocks):
            name = f"b{n}.html"
            names[name] = block_id
            (tmpdir / name).write_text(src, encoding="utf-8")
        # Write the report to a file: Node truncates a large stdout pipe on exit,
        # which silently cut the JSON at 64 KiB and made this check a no-op.
        report_path = tmpdir / "report.json"
        subprocess.run(
            ["npx", "--yes", "html-validate@8", f"--formatter=json={report_path.name}", "*.html"],
            capture_output=True, text=True, cwd=tmpdir,
        )
        if not report_path.exists():
            return None
        try:
            report = json.loads(report_path.read_text(encoding="utf-8") or "[]")
        except ValueError:
            return None
        out = []
        for entry in report:
            block_id = names.get(Path(entry["filePath"]).name)
            for msg in entry.get("messages", []):
                if block_id and msg.get("ruleId") in HTML_SYNTAX_RULES:
                    out.append((block_id, f"{msg['ruleId']}: {msg['message'][:80]}"))
        return out


def run_css_checks(blocks: list[tuple[str, str, str]]) -> list[tuple[str, str]] | None:
    """stylelint with no rules enabled reports parse errors and nothing else."""
    if not shutil.which("npx"):
        return None
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir, names = Path(tmp), {}
        (tmpdir / ".stylelintrc.json").write_text('{"rules": {}}', encoding="utf-8")
        for n, (block_id, src, ext) in enumerate(blocks):
            name = f"b{n}.{ext}"
            names[name] = block_id
            (tmpdir / name).write_text(src, encoding="utf-8")
        report_path = tmpdir / "report.json"
        subprocess.run(
            ["npx", "--yes", "stylelint@16", "*.css", "*.scss",
             "--formatter=json", "--output-file", report_path.name],
            capture_output=True, text=True, cwd=tmpdir,
        )
        if not report_path.exists():
            return None
        try:
            report = json.loads(report_path.read_text(encoding="utf-8") or "[]")
        except ValueError:
            return None
        out = []
        for entry in report:
            block_id = names.get(Path(entry["source"]).name)
            for w in entry.get("warnings", []):
                if block_id and "SyntaxError" in str(w.get("rule")):
                    out.append((block_id, w.get("text", "")[:90]))
        return out


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


TREE_DIR_RE = re.compile(r"^[├└]──\s+([a-z0-9-]+)/\s*$", re.MULTILINE)
LIST_DIR_RE = re.compile(r"^knowledge/([a-z0-9-]+)/\s*$")
LIST_FILE_RE = re.compile(r"^([0-9]{2,3}-[a-z0-9-]+\.md|README\.md|WRITING_STANDARD\.md)$")


def check_planning_docs(root: Path, problems: list[str]) -> None:
    """The structure spec and file list must still describe the tree on disk.

    Both drifted silently once — 21 topics existed with no entry in the file list,
    and `figma/` was named under Exceptions but absent from the directory tree.
    Nothing caught either, because nothing compared them to reality.
    """
    spec_dir = root.parent / "docs" / "structure"
    tree_doc = spec_dir / "frozen-structure-v1.md"
    list_doc = spec_dir / "canonical-file-list.md"
    if not tree_doc.exists() or not list_doc.exists():
        return  # running against a bare knowledge/ copy

    on_disk = {p.name for p in root.iterdir() if p.is_dir() and not p.name.startswith(".")}

    tree_text = tree_doc.read_text(encoding="utf-8", errors="replace")
    root_section = re.search(r"^# Root\s*$(.*?)^---", tree_text, re.DOTALL | re.MULTILINE)
    if root_section:
        in_tree = set(TREE_DIR_RE.findall(root_section.group(1)))
        for topic in sorted(on_disk - in_tree):
            problems.append(f"frozen-structure-v1.md: {topic}/ exists on disk but is not in the root tree")
        for topic in sorted(in_tree - on_disk):
            problems.append(f"frozen-structure-v1.md: {topic}/ is in the root tree but not on disk")

    listed: dict[str, set[str]] = {}
    current = None
    for line in list_doc.read_text(encoding="utf-8", errors="replace").split("\n"):
        stripped = line.strip()
        directory = LIST_DIR_RE.match(stripped)
        if directory:
            current = directory.group(1)
            listed.setdefault(current, set())
            continue
        filename = LIST_FILE_RE.match(stripped)
        if filename and current:
            listed[current].add(filename.group(1))

    for topic in sorted(on_disk - set(listed)):
        problems.append(f"canonical-file-list.md: no part for {topic}/")
    for topic in sorted(set(listed) - on_disk):
        problems.append(f"canonical-file-list.md: part for {topic}/, which does not exist")

    for topic in sorted(set(listed) & on_disk):
        actual = {f.name for f in (root / topic).glob("*.md")}
        for name in sorted(listed[topic] - actual):
            problems.append(f"canonical-file-list.md: lists {topic}/{name}, which does not exist")
        for name in sorted(actual - listed[topic]):
            problems.append(f"canonical-file-list.md: {topic}/{name} exists but is not listed")


MIN_RULES_LINES = 3


def check_checklist_pointers(root: Path, docs: list[Doc], problems: list[str]) -> None:
    """Topic checklists must route a failed check back to the rule that explains it.

    `98`/`99` are what AGENTS.md tells an agent to run, and they are standalone: an
    item that fails there has no context unless it names the document it came from.
    Each themed section carries a `**Rules:**` line; this only checks that the lines
    did not disappear wholesale, since the per-section mapping is editorial.
    """
    for doc in docs:
        if not doc.path.name.startswith(("98-", "99-")):
            continue
        found = len(re.findall(r"^\*\*Rules:\*\*", doc.body, re.MULTILINE))
        if found < MIN_RULES_LINES:
            problems.append(
                f"{doc.rel}: only {found} `**Rules:**` pointer(s); "
                f"each themed section should route to the doc that explains it"
            )


def check_docs(root: Path, docs: list[Doc], problems: list[str]) -> None:
    seen_ids: dict[str, str] = {}
    seen_orders: dict[tuple[str, int], str] = {}
    seen_titles: dict[str, str] = {}
    for doc in docs:
        rel = doc.rel
        if not doc.has_frontmatter:
            if doc.path.parent == root:
                continue  # README/TEMPLATE/STYLE_GUIDE at the root carry no frontmatter
            problems.append(f"{rel}: no frontmatter")
            continue
        # Zero-width and BOM characters survive copy-paste into filenames, commands,
        # and identifiers, and hide fences from every tool that looks for ``` at the
        # start of a line — which is how TEMPLATE.md's example blocks went unchecked.
        for ch, label in (("\u200b", "U+200B zero-width space"), ("\ufeff", "U+FEFF BOM")):
            if ch in doc.body:
                line = doc.body[: doc.body.index(ch)].count("\n") + 1
                problems.append(f"{rel}: {label} in the body, near line {line}")

        # An unescaped pipe inside a table cell splits the row, even within inline
        # code — the table renders with the wrong number of columns.
        in_fence = False
        for lineno, raw_line in enumerate(doc.body.split("\n"), 1):
            if raw_line.startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            stripped = raw_line.strip()
            if not (stripped.startswith("|") and stripped.endswith("|")):
                continue
            for span in re.findall(r"`([^`]*)`", stripped):
                if "|" in span.replace("\\|", ""):
                    problems.append(
                        f"{rel}:{lineno}: unescaped `|` inside a table cell — escape it as \\|"
                    )

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

        if fm.get("type") not in DOC_TYPES:
            problems.append(f"{rel}: type is {fm.get('type')!r}, expected one of {sorted(DOC_TYPES)}")
        if fm.get("status") not in ("ready", "draft"):
            problems.append(f"{rel}: status is {fm.get('status')!r}, expected ready or draft")
        if not fm.get("title"):
            problems.append(f"{rel}: title is empty")
        else:
            # `title` is the agent-facing label in INDEX.json. When it drifts from the
            # H1 it is usually an automated title-casing pass mangling an acronym —
            # "Oauth", "Cicd", "Aria" all reached the index that way.
            heading = re.search(r"^#\s+(.+)$", doc.body, re.MULTILINE)
            title = fm["title"].strip("\"'")
            if heading:
                want = heading.group(1).strip().replace("`", "")
                if title != want:
                    problems.append(f"{rel}: title is {title!r} but the H1 is {want!r}")
            # Titles are unique across the base: 36 documents called "Overview" make the
            # index unusable the moment a title is quoted outside its topic. Qualify a
            # generic name with its topic — "AWS Overview", "Docker Best Practices".
            if title in seen_titles:
                problems.append(
                    f"{rel}: title {title!r} is already used by {seen_titles[title]}"
                )
            seen_titles[title] = str(rel)
        if not fm.get("when_to_use", "").strip('"\' '):
            problems.append(f"{rel}: when_to_use is empty")

        raw_applies = fm.get("applies_to", "")
        if raw_applies:
            values = [v.strip() for v in raw_applies.strip("[]").split(",") if v.strip()]
            for v in values:
                if v not in VARIANTS:
                    problems.append(
                        f"{rel}: applies_to {v!r} is not a known variant {sorted(VARIANTS)}"
                    )

        owner = fm.get("defers_to")
        if owner:
            # Two topics can legitimately cover one subject; `defers_to` names which
            # of them states the rule, so an agent that finds both knows which wins.
            if not (root / f"{owner}.md").exists():
                problems.append(f"{rel}: defers_to -> {owner} does not exist")
            elif owner == fm.get("id"):
                problems.append(f"{rel}: defers_to points at itself")
            elif owner not in doc.related:
                problems.append(f"{rel}: defers_to {owner} but does not list it in `related`")

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
            if "<" in bare:
                continue  # `knowledge/<topic>/` documents the shape, it is not a link
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

    counts = {"python": 0, "json": 0, "yaml": 0, "xml": 0, "nginx": 0, "hcl": 0,
              "ini": 0, "graphql": 0, "dockerfile": 0, "http": 0, "diff": 0,
              "cron": 0, "makefile": 0, "redis": 0, "go": 0, "lua": 0, "shell": 0, "sql": 0, "html": 0, "css": 0,
              "php": 0, "js": 0}
    shell_blocks: list[tuple[str, str, str]] = []
    dockerfile_blocks: list[tuple[str, str, str]] = []
    go_blocks: list[tuple[str, str, str]] = []
    lua_blocks: list[tuple[str, str, str]] = []
    sql_blocks: list[tuple[str, str, str]] = []
    html_blocks: list[tuple[str, str, str]] = []
    css_blocks: list[tuple[str, str, str]] = []
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
            elif tag in SQL_TAGS:
                family = "sql"
            elif tag in HTML_TAGS:
                family = "html"
            elif tag in CSS_TAGS:
                family = "css"
            elif tag in PYTHON_TAGS:
                family = "python"
            elif tag in JSON_TAGS:
                family = "json"
            elif tag in YAML_TAGS:
                family = "yaml"
            elif tag in XML_TAGS:
                family = "xml"
            elif tag in NGINX_TAGS:
                family = "nginx"
            elif tag in HCL_TAGS:
                family = "hcl"
            elif tag in INI_TAGS:
                family = "ini"
            elif tag in GRAPHQL_TAGS:
                family = "graphql"
            elif tag in DOCKERFILE_TAGS:
                family = "dockerfile"
            elif tag in HTTP_TAGS:
                family = "http"
            elif tag in DIFF_TAGS:
                family = "diff"
            elif tag in CRON_TAGS:
                family = "cron"
            elif tag in MAKE_TAGS:
                family = "makefile"
            elif tag in REDIS_TAGS:
                family = "redis"
            elif tag in GO_TAGS:
                family = "go"
            elif tag in LUA_TAGS:
                family = "lua"
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
            elif family == "xml":
                if (err := check_xml(src)):
                    problems.append(f"{doc.rel}:{line}: ```{tag} does not parse — {err}")
            elif family in ("nginx", "hcl", "ini", "graphql", "http", "diff",
                            "cron", "makefile", "redis"):
                checker = {"nginx": check_nginx, "hcl": check_hcl,
                           "ini": check_ini, "graphql": check_graphql,
                           "http": check_http, "diff": check_diff,
                           "cron": check_cron, "makefile": check_makefile,
                           "redis": check_redis}[family]
                if (err := checker(src)):
                    problems.append(f"{doc.rel}:{line}: ```{tag} does not parse — {err}")
            elif family == "shell":
                shell_blocks.append((block_id, src, tag))
            elif family == "dockerfile":
                dockerfile_blocks.append((block_id, src, tag))
            elif family == "go":
                go_blocks.append((block_id, src, tag))
            elif family == "lua":
                lua_blocks.append((block_id, src, tag))
            elif family == "sql":
                dialect = "mysql" if doc.path.parent.name in MYSQL_TOPICS else "postgres"
                sql_blocks.append((block_id, src, dialect))
            elif family == "html":
                html_blocks.append((block_id, src, tag))
            elif family == "css":
                css_blocks.append((block_id, src, "scss" if tag == "scss" else "css"))
            elif family == "php":
                php_blocks.append((block_id, src, tag))
            elif family == "js":
                js_blocks.append((block_id, src, JS_FAMILY[tag]))

    if yaml_mod is None:
        SKIPPED["yaml"] = "pyyaml"
        print("  note: PyYAML not installed — YAML blocks were not checked")

    for block_id, err in run_shell_checks(shell_blocks):
        problems.append(f"{block_id}: shell block does not parse — {err}")

    # PHP and JS/TS are fragment-heavy; compare against the baseline instead.
    for family, blocks, runner, tool in (
        ("php", php_blocks, run_php_checks, "php"),
        ("js", js_blocks, run_js_checks, "npx"),
        ("sql", sql_blocks, run_sql_checks, "sqlfluff"),
        ("html", html_blocks, run_html_checks, "npx"),
        ("css", css_blocks, run_css_checks, "npx"),
        ("dockerfile", dockerfile_blocks, run_dockerfile_checks, "hadolint"),
        ("go", go_blocks, run_go_checks, "gofmt"),
        ("lua", lua_blocks, run_lua_checks, "luac"),
    ):
        if skip_external or not blocks or not have(tool):
            if not skip_external and blocks and not have(tool):
                SKIPPED[family] = tool
                print(f"  note: `{tool}` not found — {family} blocks were not checked")
            baseline.setdefault(family, baseline.get(family, []))
            continue
        result = runner(blocks)
        if result is None:
            SKIPPED[family] = tool
            print(f"  note: {tool} could not run — {family} blocks were not checked")
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
    unknown = flags - {"--skip-external", "--update-baseline", "--require-tools"}
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
    check_planning_docs(root, problems)
    check_checklist_pointers(root, docs, problems)
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

    if "--require-tools" in flags and SKIPPED:
        for family, tool in sorted(SKIPPED.items()):
            problems.append(
                f"{family} blocks were not checked: `{tool}` is unavailable. "
                f"A skipped language must not pass as clean — install it or drop "
                f"--require-tools deliberately."
            )

    summary = ", ".join(f"{v} {k}" for k, v in counts.items() if v)
    print(f"Checked {len(docs)} docs, {n_links} links, code blocks: {summary}.")
    if SKIPPED:
        print(f"  skipped: {', '.join(sorted(SKIPPED))}")

    if problems:
        print(f"\nFAIL: {len(problems)} problem(s)\n")
        for problem in problems:
            print(f"  {problem}")
        return 1

    print("OK: structure, frontmatter, links, and code blocks are all clean.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
