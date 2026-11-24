#!/usr/bin/env python3
"""Initialize or resume stage scaffolding after confirmed requirements discussion, preserving existing documents."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from workflow_common import (FILE_KEYS, INDEX, STAGE_KEYS, TEMPLATES, check_stage,
                             atomic_text, defaults, read_index, safe_path, write_index)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--project-name", required=True)
    parser.add_argument("--stage", default="01-initial")
    parser.add_argument("--paths", type=Path, help="JSON object mapping document keys to relative paths")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    repo = args.repo.expanduser().resolve()
    try:
        if not repo.is_dir():
            raise ValueError(f"Repository does not exist: {repo}")
        check_stage(args.stage)
        existing = read_index(repo)
        if (repo / "docs/workflow/archive" / args.stage).exists():
            raise ValueError("Stage ID already has an archive; use archive_stage.py to finish interrupted closure")
        fields = defaults(args.stage)
        if existing and existing["Status"] == "active":
            if existing["Stage"] != args.stage:
                raise ValueError("Archive the active stage before starting another")
            fields = existing.copy()
        if existing and existing["Status"] == "archived":
            if existing["Stage"] == args.stage:
                raise ValueError("Archived stage IDs cannot be reused")
            # Global working documents remain at their pre-archive paths.
            manifest_path = repo / "docs/workflow/archive" / existing["Stage"] / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            for key in ("Architecture", "Decisions", "Instructions"):
                fields[key] = manifest["source"][key]
        if args.paths:
            overrides = json.loads(args.paths.read_text(encoding="utf-8"))
            if not isinstance(overrides, dict) or set(overrides) - set(FILE_KEYS):
                raise ValueError("--paths must contain only document keys")
            if any(not isinstance(value, str) for value in overrides.values()):
                raise ValueError("Path values must be strings")
            if existing and existing["Status"] == "active" and any(
                fields[key] != value for key, value in overrides.items()
            ):
                raise ValueError("Active path mapping changes require explicit document migration")
            fields.update(overrides)
        destinations = {key: safe_path(repo, fields[key]) for key in FILE_KEYS}
        if len(set(destinations.values())) != len(destinations):
            raise ValueError("Each document must have a distinct path")
        reserved = repo / "docs/workflow/archive"
        if any(path.is_relative_to(reserved) or path == repo / INDEX for path in destinations.values()):
            raise ValueError("Active documents cannot use archive or index paths")
        if existing and existing["Status"] == "archived":
            for key in STAGE_KEYS:
                if destinations[key].exists():
                    raise ValueError(f"New stage requires a new document path: {fields[key]}")
        template_dir = Path(__file__).resolve().parent.parent / "assets/templates"
        # Read all templates before any mutation.
        contents = {key: (template_dir / TEMPLATES[key]).read_text(encoding="utf-8")
                    .replace("{{PROJECT_NAME}}", args.project_name)
                    .replace("{{STAGE_ID}}", args.stage) for key in FILE_KEYS}
        for destination in destinations.values():
            if destination.exists() and not destination.is_file():
                raise ValueError(f"Document path is not a file: {destination}")
        # Persist the new identity first so interrupted creation can resume safely.
        if not args.dry_run:
            write_index(repo, fields)
        for key, destination in destinations.items():
            if destination.exists():
                if not destination.is_file():
                    raise ValueError(f"Document path is not a file: {destination}")
                print(f"SKIP {destination}")
                continue
            print(f"CREATE {destination}" + (" (dry run)" if args.dry_run else ""))
            if not args.dry_run:
                atomic_text(destination, contents[key])
        if not args.dry_run:
            write_index(repo, fields)
        print("请先将已确认的需求共识写入 REQUIREMENTS.md，补齐架构与具体任务卡后，运行 validate_workflow.py 检查结构与质量警告，再开始派发。")
        return 0
    except (ValueError, OSError, json.JSONDecodeError) as error:
        print(f"ERROR {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
