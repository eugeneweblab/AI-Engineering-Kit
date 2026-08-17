"""One strict YAML frontmatter parser shared by every knowledge-base tool."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # fail loudly; a regex fallback previously hid corrupt YAML
    raise SystemExit(
        "PyYAML is required for knowledge metadata: python3 -m pip install pyyaml"
    ) from exc


FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n?", re.DOTALL)
FIELDS = {
    "id", "topic", "slug", "title", "type", "order", "status", "tags",
    "applies_to", "related", "defers_to", "when_to_use", "maturity",
    "verified_against", "source_urls", "last_reviewed", "review_after",
}
LIST_FIELDS = {"tags", "applies_to", "related", "source_urls"}
STRING_FIELDS = {
    "id", "topic", "slug", "title", "type", "status", "defers_to",
    "when_to_use", "maturity", "verified_against", "last_reviewed", "review_after",
}


class FrontmatterError(ValueError):
    pass


def parse_text(text: str, source: str = "<text>") -> tuple[dict[str, Any] | None, str]:
    """Return (metadata, body); metadata is None when no frontmatter exists."""
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None, text
    try:
        metadata = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        raise FrontmatterError(f"{source}: invalid YAML frontmatter: {exc}") from exc
    if not isinstance(metadata, dict):
        raise FrontmatterError(f"{source}: frontmatter must be a YAML mapping")
    return metadata, text[match.end():]


def parse_path(path: Path) -> tuple[dict[str, Any] | None, str]:
    return parse_text(path.read_text(encoding="utf-8", errors="replace"), str(path))


def schema_errors(metadata: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    unknown = sorted(set(metadata) - FIELDS)
    if unknown:
        errors.append(f"unknown field(s): {', '.join(unknown)}")
    for field in sorted(LIST_FIELDS):
        if field in metadata and not isinstance(metadata[field], list):
            errors.append(f"{field} must be a YAML list")
        elif field in metadata and not all(isinstance(v, str) for v in metadata[field]):
            errors.append(f"{field} entries must all be strings")
    for field in sorted(STRING_FIELDS):
        if field in metadata and not isinstance(metadata[field], str):
            errors.append(f"{field} must be a string")
    if "order" in metadata and not isinstance(metadata["order"], int):
        errors.append("order must be an integer")
    return errors
