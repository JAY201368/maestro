#!/usr/bin/env python3
"""检查工作流结构与新规范质量预警（向后兼容旧版中英文记录）；语义验收仍归主代理。"""
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

from workflow_common import FILE_KEYS, read_index, safe_path

REQUIRED_FILES = ("requirement.md", "ARCHITECTURE.md", "TASKS.md", "AGENTS.md",
                  "PROMPT_TEMPLATE.md", "PROGRESS.md", "DECISIONS.md")
TASK_HEADING = re.compile(
    r"^### \[([ xX])\] (T\d+[A-Za-z]?)(?:\s+[—-]\s+|\s*[：:]\s+)(.+?)\s*$",
    re.MULTILINE,
)
TASK_ID = re.compile(r"\bT\d+[A-Za-z]?\b")
FIELD = re.compile(
    r"^\*\*([^*：:\n]+)(?:[：:]\*\*|\*\*[：:])[ \t]*(.*?)"
    r"(?=^\*\*[^*：:\n]+(?:[：:]\*\*|\*\*[：:])|\Z)",
    re.MULTILINE | re.DOTALL,
)
FIELD_ALIASES = {
    "依赖": "Dependencies",
    "前置依赖": "Dependencies",
    "前置": "Dependencies",
    "执行者": "Worker",
    "工作者": "Worker",
    "模型配置": "Worker",
    "路由理由": "Routing rationale",
    "选型理由": "Routing rationale",
    "关联需求": "Requirements",
    "需求": "Requirements",
    "任务背景": "Context",
    "背景": "Context",
    "目标与背景": "Context",
    "修改范围": "Scope",
    "范围": "Scope",
    "代码范围": "Scope",
    "实施步骤": "Implementation",
    "实施方案": "Implementation",
    "具体措施": "Implementation",
    "执行步骤": "Implementation",
    "禁区与约束": "Guardrails",
    "实现约束": "Guardrails",
    "实现红线": "Guardrails",
    "禁止项": "Guardrails",
    "预期行为": "Behavior",
    "行为": "Behavior",
    "边界与异常": "Boundaries",
    "边界": "Boundaries",
    "异常与边界": "Boundaries",
    "验收标准": "Acceptance",
    "验收": "Acceptance",
    "验证方式": "Verification",
    "验证": "Verification",
    "验证方法": "Verification",
    "验收证据": "Evidence",
    "证据": "Evidence",
    "未完成处置": "Disposition",
    "处置": "Disposition",
    "提交策略": "Commit strategy",
    "提交方式": "Commit strategy",
}
WORKER_PROFILES = {"spec-worker-luna-max"} | {
    f"spec-worker-{model}-{effort}"
    for model in ("sol", "astra")
    for effort in ("medium", "high", "xhigh", "max")
}
LOW_MID_PROFILES = {"spec-worker-luna-max", "spec-worker-sol-medium"}
HIGH_PROFILES = WORKER_PROFILES - LOW_MID_PROFILES

PLACEHOLDER = re.compile(
    r"\b(?:TODO|TBD)\b|\{\{|\[insert|请替换为|待填写|【待补充】",
    re.IGNORECASE,
)
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
NO_DEP = re.compile(
    r"^(?:none|n/a|无|无依赖|-)(?:[（(][^）)\n]{0,24}[）)])?[。.]?$",
    re.IGNORECASE,
)

FILE_EXT_PATTERN = (
    r"(?:ts|tsx|js|jsx|mjs|cjs|py|sql|md|json|toml|ya?ml|css|scss|html|"
    r"sh|go|rs|java|kt|swift|rb|php|c|cpp|h|hpp)"
)
CONCRETE_PATH_RE = re.compile(
    rf"(?:[A-Za-z0-9_.-]+/(?:[A-Za-z0-9_.*{{}},-]+(?:/[A-Za-z0-9_.*{{}},-]*)*)|"
    rf"[A-Za-z0-9_.*{{}}-]+\.{FILE_EXT_PATTERN}\b)"
)
ALL_CAPS_SLASH_RE = re.compile(r"^[A-Z0-9_-]+(?:/[A-Z0-9_-]+)+$")
EXCLUSION_LINE_RE = re.compile(
    r"^\s*[-*•]?\s*(?:排除|不修改|不改动|不触及|不含|不碰|暂不删除|Exclude|Out of scope)\s*[：: ]?",
    re.IGNORECASE,
)
INLINE_EXCLUSION_SPLIT_RE = re.compile(
    r"(?:[。；;]\s*|\s+)(?:排除[：:]|不修改|不改动|不触及|不碰|暂不删除|不负责|保留既有|保持[^。；;]*不变)"
)
STEP_BULLET_RE = re.compile(r"^\s*(?:\d+[.、)）]|[-*•])\s+\S", re.MULTILINE)
ACCEPTANCE_ITEM_RE = re.compile(r"^\s*(?:[-*•]\s*|A\d+[.、:：]|\d+[.、)）])\s*\S", re.MULTILINE)
ACCEPTANCE_TAG_RE = re.compile(r"\bA\d+[.、:：]")
VERIFICATION_CMD_RE = re.compile(
    r"`[^`\n]+`|"
    r"\b(?:pytest|vitest|jest|pnpm|npm|yarn|bun|python3?|go\s+test|cargo|"
    r"playwright|tsc|eslint|mypy|ruff|make|unittest|git\s+diff)\b|"
    r"(?:tests?|__tests__|spec)/[A-Za-z0-9_.*{},/-]+|"
    r"[A-Za-z0-9_.-]+\.(?:test|spec)\.[A-Za-z0-9]+|"
    r"\btest_[A-Za-z0-9_]+\.py\b",
    re.IGNORECASE,
)
DOWNGRADE_CONSIDERATION_RE = re.compile(
    r"拆细|拆卡|拆分|不可拆|无法拆|不能拆|降级|下沉|luna|sol-medium|"
    r"无法分解|不可分解|不能交给|不适合低|低配|中配|split|downgrade|lower[- ]tier",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Task:
    task_id: str
    checked: bool
    title: str
    dependencies: tuple[str, ...]
    body: str


def strip_html_comments(text: str) -> str:
    return HTML_COMMENT.sub("", text)


def _trim_card_footer(body: str) -> str:
    """移除卡片末尾水平分隔线之后的文档脚注（仅当分隔线后不再包含字段时）。"""
    parts = re.split(r"\n---[ \t]*(?:\n|\Z)", body, maxsplit=1)
    if len(parts) == 2 and not FIELD.search(parts[1]):
        return parts[0]
    return body


def fields_for(body: str) -> dict[str, str]:
    cleaned = _trim_card_footer(body)
    fields: dict[str, str] = {}
    for raw_key, raw_value in FIELD.findall(cleaned):
        key = raw_key.strip()
        canonical = FIELD_ALIASES.get(key, key)
        fields[canonical] = raw_value.strip()
    return fields


def _positive_scope_text(scope: str) -> str:
    kept_lines: list[str] = []
    for line in scope.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if EXCLUSION_LINE_RE.match(stripped):
            continue
        head = INLINE_EXCLUSION_SPLIT_RE.split(stripped, maxsplit=1)[0].strip()
        if head:
            kept_lines.append(head)
    return "\n".join(kept_lines)


def _extract_concrete_paths(text: str) -> list[str]:
    paths: list[str] = []
    seen: set[str] = set()
    for match in CONCRETE_PATH_RE.finditer(text):
        token = match.group(0).strip("`'\".,;:()[]<>，。；：（）")
        if not token:
            continue
        if ALL_CAPS_SLASH_RE.match(token):
            continue
        # 避免把纯英文斜杠并列短语（如 short/full、read/write）误当作路径，除非带扩展名、多级路径、末尾斜杠或已知目录前缀
        if "/" in token and not re.search(rf"\.{FILE_EXT_PATTERN}$", token) and not token.endswith("/"):
            segments = [s for s in token.split("/") if s]
            known_roots = {
                "src", "tests", "test", "docs", "scripts", "assets", "references",
                "app", "lib", "pkg", "cmd", "components", "server", "shared",
                "domain", "content", "config", "migrations", "packages", "apps",
                "agents", "public", "temp", "research", "journal", "workspace",
            }
            if len(segments) < 3 and segments[0].lower() not in known_roots:
                continue
        brace = re.search(r"\{([^{}]+)\}", token)
        if brace:
            prefix = token[:brace.start()]
            suffix = token[brace.end():]
            for item in brace.group(1).split(","):
                expanded = f"{prefix}{item.strip()}{suffix}"
                if expanded and expanded not in seen:
                    seen.add(expanded)
                    paths.append(expanded)
        elif token not in seen:
            seen.add(token)
            paths.append(token)
    return paths


def _is_l0_only(verification: str) -> bool:
    return bool(re.search(r"\bL0\b", verification, re.IGNORECASE)) and not bool(
        re.search(r"\bL[123]\b", verification, re.IGNORECASE)
    )


def _card_warnings(task_id: str, fields: dict[str, str]) -> list[str]:
    warnings: list[str] = []

    if not fields.get("Context"):
        warnings.append(
            f"{task_id}: 缺少“任务背景”字段，建议用 1–3 句说明任务意图与上下文，方便人和执行者理解"
        )

    impl = fields.get("Implementation", "")
    if not impl:
        warnings.append(
            f"{task_id}: 缺少“实施步骤”字段（仅写抽象 Behavior 容易让执行者脑补跑偏），建议补充具体分步做法"
        )
    else:
        compact_impl = re.sub(r"\s+", "", impl)
        if not STEP_BULLET_RE.search(impl) and len(compact_impl) < 30:
            warnings.append(
                f"{task_id}: “实施步骤”过于简短或未分步列出，建议写清具体修改动作"
            )

    if not fields.get("Guardrails"):
        warnings.append(
            f"{task_id}: 缺少“禁区与约束”字段，建议明确禁止修改的区域与防跑偏红线"
        )

    scope = fields.get("Scope", "")
    if scope:
        positive_scope = _positive_scope_text(scope)
        paths = _extract_concrete_paths(positive_scope)
        if not paths:
            warnings.append(
                f"{task_id}: “修改范围”未给出具体文件或目录路径，执行者容易改错位置或越界"
            )
        elif len(paths) > 8:
            warnings.append(
                f"{task_id}: “修改范围”涉及较多路径/文件（约 {len(paths)} 项），建议复核是否粒度过大、可按复杂度拆分为更小的任务切片"
            )

    acceptance = fields.get("Acceptance", "")
    if acceptance:
        acc_lines = [line for line in acceptance.splitlines() if line.strip()]
        tags = ACCEPTANCE_TAG_RE.findall(acceptance)
        if (len(tags) >= 2 and len(acc_lines) == 1) or (
            not ACCEPTANCE_ITEM_RE.search(acceptance) and len(re.sub(r"\s+", "", acceptance)) > 60
        ):
            warnings.append(
                f"{task_id}: “验收标准”建议逐条分行编写（如 - A1. ...），便于逐项核对证据"
            )

    verification = fields.get("Verification", "")
    if verification and not _is_l0_only(verification):
        if not VERIFICATION_CMD_RE.search(verification):
            warnings.append(
                f"{task_id}: “验证方式”缺少具体可执行的命令或测试文件路径，执行者难以按统一标准自检"
            )

    worker = fields.get("Worker", "").strip("`")
    rationale = fields.get("Routing rationale", "")
    if worker in HIGH_PROFILES and rationale:
        compact_rationale = re.sub(r"\s+", "", rationale)
        if len(compact_rationale) < 18 or not DOWNGRADE_CONSIDERATION_RE.search(rationale):
            warnings.append(
                f"{task_id}: 选用了高配执行者（{worker}），但“路由理由”未说明为何不能通过拆细卡片或补清步骤交由 luna-max / sol-medium 执行"
            )

    return warnings


def parse_tasks(
    content: str, legacy: bool = False
) -> tuple[list[Task], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    matches = list(TASK_HEADING.finditer(content))
    tasks: list[Task] = []
    valid_workers: list[str] = []

    if len(matches) >= 2:
        preamble = content[:matches[0].start()]
        if not re.search(r"模型分层|luna-max|sol-medium", preamble, re.IGNORECASE):
            warnings.append(
                "[TASKS.md] 建议在任务卡顶部增加“模型分层概览”，便于规划阶段一眼发现路由通胀"
            )

    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        body = _trim_card_footer(content[match.end():end])
        task_id = match.group(2)
        checked = match.group(1).lower() == "x"
        fields = fields_for(body)

        required = ["Dependencies", "Scope", "Acceptance", "Verification", "Worker", "Routing rationale"]
        if not legacy:
            required += ["Requirements", "Boundaries"]
            if checked:
                required.append("Evidence")

        for key in required:
            if not fields.get(key) or PLACEHOLDER.search(fields[key]):
                errors.append(f"{task_id} requires concrete {key}")

        if not legacy:
            has_behavior = bool(fields.get("Behavior")) and not PLACEHOLDER.search(fields["Behavior"])
            has_impl = bool(fields.get("Implementation")) and not PLACEHOLDER.search(fields["Implementation"])
            if not (has_behavior or has_impl):
                errors.append(f"{task_id} requires concrete Implementation or Behavior")

        for opt_key in ("Context", "Implementation", "Guardrails", "Commit strategy"):
            if fields.get(opt_key) and PLACEHOLDER.search(fields[opt_key]):
                errors.append(f"{task_id} contains placeholder in {opt_key}")

        worker = fields.get("Worker", "").strip("`")
        if worker not in WORKER_PROFILES:
            errors.append(f"{task_id} must name a supported Worker profile")
        else:
            valid_workers.append(worker)

        raw = fields.get("Dependencies", "")
        if not raw or NO_DEP.match(raw.strip()):
            dependencies: tuple[str, ...] = ()
        else:
            dependencies = tuple(TASK_ID.findall(raw))
            if not dependencies:
                errors.append(f"{task_id} has invalid Dependencies")

        warnings.extend(_card_warnings(task_id, fields))
        tasks.append(Task(task_id, checked, match.group(3), dependencies, body))

    total = len(valid_workers)
    if total >= 3:
        low_mid = sum(1 for w in valid_workers if w in LOW_MID_PROFILES)
        high = total - low_mid
        if low_mid == 0:
            warnings.append(
                f"[路由分布] 本阶段共 {total} 张任务卡，但 luna-max 与 sol-medium 占比为 0%（全员高配）。"
                "请复核是否任务拆得过粗，或把确定性工作混入了高配任务卡"
            )
        elif total >= 4 and high / total > 0.70:
            pct = round(high * 100 / total)
            warnings.append(
                f"[路由分布] 本阶段高配任务卡占比偏高（{high}/{total}，{pct}%），"
                "建议复核是否有调研、纯工具、文案、清理或单测任务可拆出交由 luna-max / sol-medium"
            )

    return tasks, errors, warnings


def find_cycle(tasks: dict[str, Task]) -> list[str] | None:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str, path: list[str]) -> list[str] | None:
        if task_id in visiting:
            return path[path.index(task_id):] + [task_id]
        if task_id in visited:
            return None
        visiting.add(task_id)
        for dependency in tasks[task_id].dependencies:
            if dependency in tasks:
                cycle = visit(dependency, path + [task_id])
                if cycle:
                    return cycle
        visiting.remove(task_id)
        visited.add(task_id)
        return None

    for task_id in tasks:
        cycle = visit(task_id, [])
        if cycle:
            return cycle
    return None


def check_links(text: str, base: Path, repo: Path) -> list[str]:
    errors = []
    resolved_repo = repo.expanduser().resolve()
    for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
        target = target.strip().strip("<>")
        if re.match(r"[a-zA-Z][\w+.-]*:", target) or target.startswith("#"):
            continue
        relative = unquote(target.split("#", 1)[0])
        path = (base / relative).resolve()
        if not path.is_relative_to(resolved_repo) or not path.is_file():
            errors.append(f"Missing or external local reference: {target}")
    return errors


def _stage_doc_warnings(paths: dict[str, Path]) -> list[str]:
    warnings: list[str] = []

    req_path = paths.get("Requirements")
    if req_path and req_path.is_file():
        req_text = strip_html_comments(req_path.read_text(encoding="utf-8"))
        if PLACEHOLDER.search(req_text):
            warnings.append("[REQUIREMENTS.md] 仍包含未替换的模板占位符")
        if not re.search(r"背景|目标|动机|Goal|Background", req_text, re.IGNORECASE):
            warnings.append("[REQUIREMENTS.md] 建议明确写清阶段目标与背景动机")
        if not re.search(r"不做|排除|不在本阶段|Out of scope|Exclusion", req_text, re.IGNORECASE):
            warnings.append("[REQUIREMENTS.md] 建议补充“明确不做”的范围排除边界，防止需求蔓延")

    prog_path = paths.get("Progress")
    if prog_path and prog_path.is_file():
        prog_text = strip_html_comments(prog_path.read_text(encoding="utf-8"))
        if PLACEHOLDER.search(prog_text):
            warnings.append("[PROGRESS.md] 仍包含未替换的模板占位符")
        has_table = bool(re.search(r"^\|.+\|\s*\n\|[ \t:|-]+\|", prog_text, re.MULTILINE))
        if not has_table:
            warnings.append("[PROGRESS.md] 建议包含 Markdown 表格形式的“任务状态看板”，方便人一眼把握全局进度")
        if not re.search(r"阻塞|待.*拍板|待.*决策|技术债|Issues|Decisions|Blocker", prog_text, re.IGNORECASE):
            warnings.append("[PROGRESS.md] 建议显式列出阻塞项、待拍板决策与已知技术债小节")

    prompt_path = paths.get("Prompt")
    if prompt_path and prompt_path.is_file():
        prompt_text = strip_html_comments(prompt_path.read_text(encoding="utf-8"))
        if PLACEHOLDER.search(prompt_text):
            warnings.append("[PROMPT_TEMPLATE.md] 仍包含未替换的模板占位符")
        if not re.search(r"红线|禁区|实现约束|Guardrails", prompt_text, re.IGNORECASE):
            warnings.append("[PROMPT_TEMPLATE.md] 建议补充“本阶段实现红线（防跑偏禁区）”小节")
        if not re.search(r"核对|歧义|停下|conflict|ambiguity", prompt_text, re.IGNORECASE):
            warnings.append("[PROMPT_TEMPLATE.md] 建议包含开工前代码核对及遇歧义停下汇报的约定")

    dec_path = paths.get("Decisions")
    if dec_path and dec_path.is_file():
        dec_text = strip_html_comments(dec_path.read_text(encoding="utf-8"))
        if PLACEHOLDER.search(dec_text):
            warnings.append("[DECISIONS.md] 仍包含未替换的模板占位符")

    return warnings


def inspect_workflow(
    repo: Path, closing: bool = False
) -> tuple[list[Task], list[str], list[str]]:
    repo = repo.expanduser().resolve()
    index = read_index(repo)
    paths = {key: safe_path(repo, index[key]) for key in FILE_KEYS} if index else {}
    required = list(paths.values()) if index else [repo / name for name in REQUIRED_FILES]
    errors = [
        f"missing required file: {path.relative_to(repo)}"
        for path in required
        if not path.is_file()
    ]
    warnings: list[str] = []
    if index:
        warnings.extend(_stage_doc_warnings(paths))

    tasks_path = paths.get("Tasks", repo / "TASKS.md")
    if not tasks_path.is_file():
        return [], errors, warnings

    tasks_text = strip_html_comments(tasks_path.read_text(encoding="utf-8"))
    parsed, parse_errors, parse_warnings = parse_tasks(tasks_text, legacy=index is None)
    errors.extend(parse_errors)
    warnings.extend(parse_warnings)

    by_id: dict[str, Task] = {}
    for task in parsed:
        if task.task_id in by_id:
            errors.append(f"duplicate task ID: {task.task_id}")
        by_id[task.task_id] = task

    for task in parsed:
        for dependency in task.dependencies:
            if dependency not in by_id:
                errors.append(f"{task.task_id} has unknown dependency {dependency}")
            elif task.checked and not by_id[dependency].checked:
                errors.append(f"checked task {task.task_id} has unchecked dependency {dependency}")
        fields = fields_for(task.body)
        if closing and not task.checked:
            disposition = fields.get("Disposition", "")
            if not disposition or PLACEHOLDER.search(disposition):
                errors.append(
                    f"{task.task_id} needs user-approved Disposition with reason and destination"
                )
        if index:
            for key in ("Requirements", "Evidence", "Disposition"):
                errors.extend(
                    f"{task.task_id}: {error}"
                    for error in check_links(fields.get(key, ""), tasks_path.parent, repo)
                )

    cycle = find_cycle(by_id)
    if cycle:
        errors.append(f"dependency cycle: {' -> '.join(cycle)}")
    if not parsed:
        errors.append("TASKS.md contains no recognized task cards")

    return parsed, errors, warnings


def validate(repo: Path, closing: bool = False) -> tuple[list[Task], list[str]]:
    """向后兼容的结构校验接口，供 archive_stage.py 等脚本调用。"""
    tasks, errors, _warnings = inspect_workflow(repo, closing=closing)
    return tasks, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument(
        "--closing",
        action="store_true",
        help="要求所有未勾选任务卡都已填写用户批准的未完成处置（Disposition）",
    )
    parser.add_argument(
        "--strict-warnings",
        action="store_true",
        help="将质量预警（WARN）也视为失败并返回退出码 1",
    )
    args = parser.parse_args()
    try:
        tasks, errors, warnings = inspect_workflow(args.repo.expanduser().resolve(), args.closing)
    except (ValueError, OSError) as error:
        tasks, errors, warnings = [], [str(error)], []

    for error in errors:
        print(f"ERROR {error}")
    for warning in warnings:
        print(f"WARN {warning}")

    if errors:
        return 1
    if args.strict_warnings and warnings:
        print(
            f"FAILED strict warning check ({len(tasks)} tasks, {len(warnings)} warnings)"
        )
        return 1
    print(
        f"OK workflow structure is valid ({len(tasks)} tasks, {len(warnings)} warnings); "
        "review warnings, requirement coverage and evidence validity manually"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
