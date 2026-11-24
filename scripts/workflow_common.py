"""Shared paths and atomic index handling for stage workflows."""
from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path

INDEX = Path("docs/workflow/current.md")
STAGE_KEYS = ("Requirements", "Tasks", "Progress", "Acceptance", "Prompt")
GLOBAL_KEYS = ("Architecture", "Decisions", "Instructions")
FILE_KEYS = STAGE_KEYS + GLOBAL_KEYS
TEMPLATES = dict(zip(FILE_KEYS, (
    "REQUIREMENTS.md", "TASKS.md", "PROGRESS.md", "ACCEPTANCE.md",
    "PROMPT_TEMPLATE.md", "ARCHITECTURE.md", "DECISIONS.md", "AGENTS.md",
)))
FIELD = re.compile(r"^\*\*([^*：:\n]+)(?:[：:]\*\*|\*\*[：:])[ \t]*(.*)$", re.MULTILINE)


def safe_path(repo: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or not value.strip():
        raise ValueError(f"Expected repository-relative path: {value!r}")
    resolved = (repo / path).resolve()
    if not resolved.is_relative_to(repo.resolve()):
        raise ValueError(f"Path escapes repository: {value}")
    return resolved


def read_index(repo: Path) -> dict[str, str] | None:
    path = repo / INDEX
    if not path.exists():
        return None
    entries = FIELD.findall(path.read_text(encoding="utf-8"))
    fields = dict(entries)
    if len(entries) != len(fields):
        raise ValueError("current.md has duplicate fields")
    for key in ("Stage", "Status") + FILE_KEYS:
        if not fields.get(key):
            raise ValueError(f"current.md is missing {key}")
    if fields["Status"] not in {"active", "archived"}:
        raise ValueError("Status must be active or archived")
    check_stage(fields["Stage"])
    paths = [safe_path(repo, fields[key]) for key in FILE_KEYS]
    if len(set(paths)) != len(paths):
        raise ValueError("Each document must have a distinct path")
    return fields


def check_stage(stage: str) -> None:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.\-\u0080-\uffff]*", stage) or stage in {".", ".."}:
        raise ValueError("Stage must be a single directory name")


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def write_index(repo: Path, fields: dict[str, str]) -> None:
    text = "# Current workflow\n\n" + "".join(
        f"**{key}:** {fields[key]}\n" for key in ("Stage", "Status") + FILE_KEYS
    )
    atomic_text(repo / INDEX, text)


def defaults(stage: str) -> dict[str, str]:
    base = Path("docs/workflow/stages") / stage
    return {"Stage": stage, "Status": "active", **{
        key: str(base / TEMPLATES[key]) for key in STAGE_KEYS
    }, "Architecture": "docs/ARCHITECTURE.md", "Decisions": "docs/DECISIONS.md",
        "Instructions": "AGENTS.md"}
