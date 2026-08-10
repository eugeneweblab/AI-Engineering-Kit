#!/usr/bin/env python3
"""Guardrail: TypeScript examples must type-check against the real libraries.

`check-knowledge.py` parses 1707 JS/TS blocks with esbuild, which proves they are
syntactically valid and nothing else. `revalidateTag('posts')` parses. So does
`new PrismaClient()`. Both are compile errors against the libraries the base claims
to teach, and both were here — the first found by hand during the Next.js migration,
the second by this check.

What it does: installs a fixed set of the libraries the base actually imports,
extracts every block that imports one of them, and compiles the lot with `tsc`.

The hard part is not compiling. It is that most blocks are excerpts — they reference
`logger`, `db`, a model that only exists in the reader's project. Those produce
TS2304 (cannot find name) and TS2307 (cannot find module) by the hundred, and any
attempt to filter them by error code also throws away real findings: the missing
`await` on `cookies()` shows up as TS2339, which is also what an undefined local
produces.

So nothing is filtered by cleverness. Every diagnostic is recorded in
`scripts/data/types-baseline.json` keyed by document and message shape, and the
check fails only on diagnostics that are not in it. A new type error gets exactly
one review. That is the same contract as check-dangerous-sinks, for the same reason:
a heuristic that is right twice out of twenty-eight is not a gate.

The baseline holds a *count* per key. Keying alone was not enough: a second
`TS2304` in a document that already had one passed unseen, which injection caught
one commit after this check shipped.

`--refresh-env` reinstalls the library set and regenerates the Prisma client. The
installed versions are pinned in `scripts/data/types-env.json` so a run is
reproducible and a deliberate library upgrade is a visible commit.

Exit code 0 = clean, 1 = a block does not compile against the real types.

Usage:
    python3 scripts/check-types.py
    python3 scripts/check-types.py --refresh-env      # (re)build the library sandbox
    python3 scripts/check-types.py --update-baseline  # accept current diagnostics
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KB = ROOT / "knowledge"
DATA = ROOT / "scripts" / "data"
BASELINE = DATA / "types-baseline.json"
ENV_LOCK = DATA / "types-env.json"
SANDBOX = Path(os.environ.get("KB_TYPES_SANDBOX", "/tmp/kb-types"))

FENCE = re.compile(r"^```(ts|tsx|typescript)\s*$\n(.*?)^```\s*$", re.DOTALL | re.MULTILINE)
IMPORT = re.compile(r"""(?:from|require\()\s*['"]([^'"]+)['"]""")
DIAGNOSTIC = re.compile(r"^blocks/(b\d+\.tsx?)\((\d+),\d+\): error (TS\d+): (.*)$")

# The libraries the base imports most, which is what makes a block checkable at all.
LIBRARIES = [
    "typescript", "@types/node",
    "next", "react", "react-dom", "@types/react", "@types/react-dom",
    "@nestjs/common", "@nestjs/core", "@nestjs/config", "@nestjs/typeorm",
    "typeorm", "class-validator", "class-transformer", "rxjs",
    "zod", "@prisma/client", "prisma", "@prisma/adapter-pg",
    "express", "@types/express",
]

TSCONFIG = {
    "compilerOptions": {
        "target": "ES2022", "module": "ESNext", "moduleResolution": "bundler",
        "jsx": "react-jsx", "noEmit": True, "skipLibCheck": True,
        "strict": False, "noImplicitAny": False, "esModuleInterop": True,
        "allowSyntheticDefaultImports": True, "allowImportingTsExtensions": True,
        "experimentalDecorators": True, "emitDecoratorMetadata": True,
        "types": ["node"],
        "paths": {"@/generated/prisma/client": ["./generated/prisma/client.ts"]},
    },
    "include": ["blocks/**/*"],
}

PRISMA_SCHEMA = """generator client {
  provider = "prisma-client"
  output   = "../generated/prisma"
}

datasource db {
  provider = "postgresql"
}

model User {
  id        String    @id @default(uuid())
  email     String    @unique
  firstName String?
  lastName  String?
  deletedAt DateTime?
  posts     Post[]
}

model Post {
  id        String    @id @default(uuid())
  title     String
  published Boolean   @default(false)
  createdAt DateTime  @default(now())
  deletedAt DateTime?
  authorId  String?
  author    User?     @relation(fields: [authorId], references: [id])
}
"""


def refresh_env() -> int:
    SANDBOX.mkdir(parents=True, exist_ok=True)
    (SANDBOX / "package.json").write_text(
        json.dumps({"name": "kb-types", "private": True, "type": "module"}) + "\n",
        encoding="utf-8",
    )
    print(f"installing {len(LIBRARIES)} libraries into {SANDBOX} …")
    proc = subprocess.run(
        ["npm", "install", "--silent", "--no-audit", "--no-fund", *LIBRARIES],
        cwd=SANDBOX, capture_output=True, text=True,
    )
    if proc.returncode != 0:
        print(proc.stderr[-2000:])
        return 1

    # The Prisma Client is generated source since v7, so it has to exist before any
    # block importing it can be compiled.
    (SANDBOX / "prisma").mkdir(exist_ok=True)
    (SANDBOX / "prisma" / "schema.prisma").write_text(PRISMA_SCHEMA, encoding="utf-8")
    (SANDBOX / "prisma.config.ts").write_text(
        'import { defineConfig, env } from "prisma/config";\n'
        'export default defineConfig({\n'
        '  schema: "prisma/schema.prisma",\n'
        '  datasource: { url: env("DATABASE_URL") },\n'
        '});\n',
        encoding="utf-8",
    )
    generated = subprocess.run(
        ["npx", "prisma", "generate"], cwd=SANDBOX, capture_output=True, text=True,
        env={**os.environ, "DATABASE_URL": "postgresql://u:p@localhost:5432/db"},
    )
    if generated.returncode != 0:
        print(generated.stdout[-1500:], generated.stderr[-1500:])
        return 1

    versions = {}
    for library in LIBRARIES:
        manifest = SANDBOX / "node_modules" / library / "package.json"
        if manifest.exists():
            versions[library] = json.loads(manifest.read_text(encoding="utf-8"))["version"]
    ENV_LOCK.write_text(json.dumps(versions, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"sandbox ready: {len(versions)} libraries pinned in "
          f"{ENV_LOCK.relative_to(ROOT)}, Prisma Client generated.")
    return 0


def installed_packages() -> set[str]:
    modules = SANDBOX / "node_modules"
    if not modules.exists():
        return set()
    names = set()
    for entry in modules.iterdir():
        if entry.name.startswith("@"):
            names.update(f"{entry.name}/{sub.name}" for sub in entry.iterdir())
        else:
            names.add(entry.name)
    return names


def package_of(specifier: str) -> str:
    if specifier.startswith("@"):
        return "/".join(specifier.split("/")[:2])
    return specifier.split("/")[0]


def main(argv: list[str]) -> int:
    if "--refresh-env" in argv:
        return refresh_env()

    if not (SANDBOX / "node_modules").exists():
        print(f"error: no library sandbox at {SANDBOX}.\n"
              f"  Run: python3 scripts/check-types.py --refresh-env")
        return 1

    packages = installed_packages()
    blocks_dir = SANDBOX / "blocks"
    shutil.rmtree(blocks_dir, ignore_errors=True)
    blocks_dir.mkdir()

    origin: dict[str, str] = {}
    count = 0
    for path in sorted(KB.rglob("*.md")):
        for _, source in FENCE.findall(path.read_text(encoding="utf-8", errors="replace")):
            specifiers = [
                s for s in IMPORT.findall(source) if not s.startswith((".", "/"))
            ]
            checkable = [
                s for s in specifiers
                if package_of(s) in packages or s.startswith("@/generated/prisma")
            ]
            if not checkable:
                continue
            count += 1
            name = f"b{count:04d}.tsx"
            (blocks_dir / name).write_text(source, encoding="utf-8")
            origin[name] = path.relative_to(KB).as_posix()

    (SANDBOX / "tsconfig.json").write_text(json.dumps(TSCONFIG, indent=1), encoding="utf-8")
    proc = subprocess.run(
        ["npx", "tsc", "-p", "tsconfig.json"], cwd=SANDBOX, capture_output=True, text=True
    )

    baseline: dict[str, str] = (
        json.loads(BASELINE.read_text(encoding="utf-8")) if BASELINE.exists() else {}
    )
    found: dict[str, int] = {}
    where: dict[str, str] = {}
    sample: dict[str, str] = {}
    problems: list[str] = []
    for line in (proc.stdout + proc.stderr).split("\n"):
        match = DIAGNOSTIC.match(line.strip())
        if not match:
            continue
        block, _, code, message = match.groups()
        document = origin.get(block, block)
        # Keyed on the document and the message with identifiers generalised, so a
        # block moving down a file does not invalidate its entry.
        shape = re.sub(r"'[^']*'", "'…'", message)[:160]
        key = f"{document}|{code}|{shape}"
        found[key] = found.get(key, 0) + 1
        where[key] = document
        sample.setdefault(key, message)

    if "--update-baseline" in argv:
        BASELINE.write_text(json.dumps(found, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print(f"baseline updated: {sum(found.values())} diagnostics recorded across "
              f"{len(set(where.values()))} documents.")
        return 0

    for key, seen in sorted(found.items()):
        known = baseline.get(key, 0)
        if seen > known:
            document, code, _ = key.split("|", 2)
            problems.append(
                f"{document}: {code} {sample.get(key, '')[:180]}"
                + (f"  ({seen - known} more than the {known} reviewed)" if known else "")
            )
    for key in sorted(set(baseline) - set(found)):
        problems.append(
            f"baseline: {key.split('|')[0]} no longer produces {key.split('|')[1]}. "
            f"Run --update-baseline."
        )

    if problems:
        print(f"FAIL: {len(problems)} type diagnostic(s) not previously reviewed\n")
        for problem in sorted(problems)[:60]:
            print(f"  {problem}")
        if len(problems) > 60:
            print(f"  … and {len(problems) - 60} more")
        print("\nThese blocks parse. They do not compile against the libraries they "
              "import.\nFix the example, or record a deliberate excerpt with "
              "--update-baseline.")
        return 1

    versions = json.loads(ENV_LOCK.read_text(encoding="utf-8")) if ENV_LOCK.exists() else {}
    headline = ", ".join(
        f"{name} {versions[name]}" for name in ("next", "react", "@nestjs/common", "@prisma/client")
        if name in versions
    )
    print(f"OK: {count} TypeScript blocks compile against the real libraries "
          f"({headline}; {sum(baseline.values())} reviewed excerpts).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
