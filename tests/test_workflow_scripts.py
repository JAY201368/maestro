#!/usr/bin/env python3
"""Maestro 工作流脚本、新中文规范预警与向后兼容性自动化测试套件。"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import validate_workflow  # noqa: E402


def _run_script(script_name: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / script_name), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _write_clean_stage_docs(repo: Path, stage: str, tasks_md: str) -> None:
    stage_dir = repo / "docs/workflow/stages" / stage
    (stage_dir / "REQUIREMENTS.md").write_text(
        "# Demo — 阶段需求\n\n"
        "## 一句话目标与背景\n\n"
        "解决原流程档期混乱的问题，改为早晚两刊。\n\n"
        "## 需求清单\n\n"
        "| 编号 | 内容 | 任务卡 |\n| --- | --- | --- |\n| R01 | 早晚两刊档期 | T01–T04 |\n\n"
        "## 明确不做\n\n"
        "- 不修改移动端排版，不升级框架版本。\n",
        encoding="utf-8",
    )
    (stage_dir / "PROGRESS.md").write_text(
        "# Demo — 阶段进度看板\n\n"
        "## 进度总览\n\n"
        "已完成规划，准备启动首批任务。\n\n"
        "## 任务状态看板\n\n"
        "| 任务卡 | 标题 | 执行者配置 | 状态 |\n"
        "| --- | --- | --- | --- |\n"
        "| T01 | 纯函数模块 | `spec-worker-luna-max` | 待派发 |\n\n"
        "## 当前阻塞项与待用户拍板的决策\n\n"
        "暂无阻塞与待拍板项。\n\n"
        "## 已知技术债\n\n"
        "暂无。\n",
        encoding="utf-8",
    )
    (stage_dir / "PROMPT_TEMPLATE.md").write_text(
        "# Demo — 单卡派发模板\n\n"
        "## 1. 上下文\n\n"
        "附仓库路径、映射文档与完整任务卡。\n\n"
        "## 2. 本阶段实现红线（防跑偏禁区）\n\n"
        "1. 严禁修改冻结目录 `src/domain/`。\n\n"
        "## 3. 开工前核对\n\n"
        "先读源码核对卡片前提，遇歧义立即停下回报主代理。\n",
        encoding="utf-8",
    )
    (stage_dir / "ACCEPTANCE.md").write_text(
        "# Demo — 验收证据账本\n\n"
        "## T01-E1 · 档期纯函数\n\n"
        "单测 12/12 通过。\n",
        encoding="utf-8",
    )
    (repo / "docs/DECISIONS.md").write_text(
        "# Demo 关键决策与技术债账本\n\n"
        "<!-- 示例注释里的 请替换为 不应误触占位符警告 -->\n\n"
        "## 关键架构与产品决策\n\n"
        "### D01 · 档期规则\n\n采用 08:00 与 14:00 两刊。\n",
        encoding="utf-8",
    )
    (stage_dir / "TASKS.md").write_text(tasks_md, encoding="utf-8")


VALID_TASKS_MD = """# Demo — 阶段 01-demo 任务卡

## 依赖关系与执行批次

T01 -> T02 -> T03 -> T04

## 模型分层概览

- `luna-max`：2 | `sol-medium`：1 | `sol-high`：1

---

### [ ] T01 — 新增早晚刊档期纯函数与单测

**依赖:** 无
**执行者:** spec-worker-luna-max
**路由理由:** 纯时间换算与常量定义，边界明确且零外部依赖，适合 luna-max 快速准确完成。
**关联需求:** [R01](REQUIREMENTS.md)
**任务背景:** 调度器和前端共用同一套北京时间早晚刊档期判断逻辑，先抽成独立纯函数模块供后续任务复用。
**修改范围:**
- 新增 `src/shared/schedule.ts` 与 `tests/unit/schedule.test.ts`
- 排除：不触碰 `src/server/` 与 `src/components/`。
**实施步骤:**
1. 在 `src/shared/schedule.ts` 导出档期常量与 `scheduledSlot(date)` 纯函数。
2. 在 `tests/unit/schedule.test.ts` 覆盖 `00:00`、`07:59`、`08:00`、`14:00`、`23:59` 边界。
**禁区与约束:**
- 严禁引入 `node:crypto` 等服务端专用模块。
**边界与异常:** 非法 `Date` 抛出 `RangeError`；纯函数无并发问题。
**验收标准:**
- A1. 北京时间各边界返回正确档期。
- A2. UTC 时区下运行结果一致。
**验证方式:** L1。执行 `TZ=UTC pnpm exec vitest run tests/unit/schedule.test.ts` 与 `pnpm typecheck`，全部通过。
**提交策略:** 随批次 1（T01–T02）合并提交

### [ ] T02 — 同步订阅说明文档与示例配置

**依赖:** T01
**执行者:** spec-worker-luna-max
**路由理由:** 纯文档与配置文案更新，范围限定两个文件，适合 luna-max 完成。
**关联需求:** [R01](REQUIREMENTS.md)
**任务背景:** 让运维与开发者文档同步反映新的早晚刊时刻。
**修改范围:**
- 修改 `docs/OPERATIONS.md` 与 `.env.example`
- 排除：不改任何运行代码。
**实施步骤:**
1. 更新 `docs/OPERATIONS.md` 的定时档期说明为 08:00 与 14:00。
2. 同步 `.env.example` 中的档期注释。
**禁区与约束:**
- 严禁写入真实密钥或修改 `.env` 私有文件。
**边界与异常:** 纯文本改动，不涉及运行状态或并发。
**验收标准:**
- A1. 两份文件均已同步为 08:00 / 14:00，无残留旧时刻。
**验证方式:** L0。检查 `git diff --check` 与文档链接。
**提交策略:** 随批次 1（T01–T02）合并提交

### [ ] T03 — 适配前端报头与订阅选项文案

**依赖:** T01
**执行者:** spec-worker-sol-medium
**路由理由:** 涉及 3 个前端组件与 1 个单测文件，展示文案与字段名均已写死，无复杂状态机，适合 sol-medium 完成。
**关联需求:** [R01](REQUIREMENTS.md)
**任务背景:** 把接口返回的 `slot` 字段渲染到报头和订阅单选框中。
**修改范围:**
- 修改 `src/components/header.tsx`、`src/components/subscribe.tsx`、`tests/unit/header.test.tsx`
- 排除：不改全局样式与后端代码。
**实施步骤:**
1. 在 `src/components/header.tsx` 中依据 `edition.slot` 显示“晨刊”或“午刊”。
2. 在 `src/components/subscribe.tsx` 中将单选项更新为 `08:00` 与 `14:00`。
3. 更新 `tests/unit/header.test.tsx` 覆盖两种档期与基础版。
**禁区与约束:**
- 严禁新增免责套话或改动桌面布局尺寸。
**边界与异常:** `slot` 缺失时回退显示“基础版”，不出现空白。
**验收标准:**
- A1. 报头正确渲染晨刊/午刊/基础版。
- A2. 订阅单选默认选中 08:00 并可切换到 14:00。
**验证方式:** L2。执行 `pnpm exec vitest run tests/unit/header.test.tsx` 与 `pnpm typecheck`。
**提交策略:** 独立提交

### [ ] T04 — 改造后端事务去重与跨档刷新状态机

**依赖:** T01
**执行者:** spec-worker-sol-high
**路由理由:** 涉及 PostgreSQL 事务租约、同档复用与 14:00 跨档必刷新的强状态一致性，已将纯档期函数（T01）和前端展示（T03）拆出，剩余事务状态机无法继续拆细降级到 sol-medium。
**关联需求:** [R01](REQUIREMENTS.md)
**任务背景:** 在不破坏租约与权限撤回的前提下，把每小时调度切换为早晚两刊并防止跨档误复用晨刊。
**修改范围:**
- 修改 `src/server/scheduler.ts`、`src/server/store.ts`、`tests/contracts/scheduler.test.ts`
- 排除：不改 `src/domain/` 冻结目录。
**实施步骤:**
1. 在 `src/server/store.ts` 中复用 `check_hour`（0 / 8 / 14）完成档期去重写入。
2. 在 `src/server/scheduler.ts` 中拦截 14:00 跨档复用晨刊，并在同档内保留时间投影。
3. 在 `tests/contracts/scheduler.test.ts` 补齐 00:00、08:00、14:00 隔离库契约用例。
**禁区与约束:**
- 严禁新增破坏性数据库表结构迁移，严禁跳过租约 fence 校验。
**边界与异常:** 覆盖并发领取、配置版本切换撤权与 12 小时天气过期边界。
**验收标准:**
- A1. 00:00–07:59 零自动 AI 生成，首访仅拉基础版。
- A2. 14:00 必触发午刊生成，绝不跨档复用晨刊。
**验证方式:** L3。执行 `pnpm test tests/contracts/scheduler.test.ts` 与 `pnpm typecheck`。
**提交策略:** 独立提交
"""


class WorkflowScriptsTests(unittest.TestCase):
    def test_bootstrap_validate_and_archive_full_chinese_lifecycle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            boot = _run_script(
                "bootstrap_workflow.py",
                "--repo", str(repo),
                "--project-name", "Demo",
                "--stage", "01-demo",
            )
            self.assertEqual(boot.returncode, 0, boot.stderr + boot.stdout)

            # 刚初始化未替换占位符时应报 ERROR
            initial_check = _run_script("validate_workflow.py", "--repo", str(repo))
            self.assertEqual(initial_check.returncode, 1)
            self.assertIn("ERROR", initial_check.stdout)

            # 写入符合新规范的内容后应 0 ERROR 且 0 WARN
            _write_clean_stage_docs(repo, "01-demo", VALID_TASKS_MD)
            tasks, errors, warnings = validate_workflow.inspect_workflow(repo)
            self.assertEqual(len(tasks), 4)
            self.assertEqual(errors, [])
            self.assertEqual(warnings, [])

            strict_ok = _run_script(
                "validate_workflow.py", "--repo", str(repo), "--strict-warnings"
            )
            self.assertEqual(strict_ok.returncode, 0, strict_ok.stdout)
            self.assertIn("0 warnings", strict_ok.stdout)

            # 勾选 T01–T03，T04 留未完成并写中文未完成处置，验证归档与幂等重试
            closing_tasks = (
                VALID_TASKS_MD
                .replace("### [ ] T01", "### [x] T01")
                .replace("### [ ] T02", "### [x] T02")
                .replace("### [ ] T03", "### [x] T03")
                .replace(
                    "**提交策略:** 随批次 1（T01–T02）合并提交",
                    "**提交策略:** 随批次 1（T01–T02）合并提交\n**验收证据:** [T01-E1](ACCEPTANCE.md#t01-e1--档期纯函数) 已通过。",
                )
                .replace(
                    "**提交策略:** 独立提交\n\n### [ ] T04",
                    "**提交策略:** 独立提交\n**验收证据:** [T01-E1](ACCEPTANCE.md#t01-e1--档期纯函数) 已通过。\n\n### [ ] T04",
                )
                + "\n**未完成处置:** 用户确认 T04 移交下一阶段 02-next 处理。\n"
            )
            (repo / "docs/workflow/stages/01-demo/TASKS.md").write_text(
                closing_tasks, encoding="utf-8"
            )
            handoff = repo / "handoff.md"
            handoff.write_text("# 阶段 01 交接\n\n已完成 T01–T03，T04 经确认移交 02-next。\n", encoding="utf-8")

            arch1 = _run_script(
                "archive_stage.py",
                "--repo", str(repo),
                "--handoff", str(handoff),
                "--confirmed",
            )
            self.assertEqual(arch1.returncode, 0, arch1.stdout + arch1.stderr)
            # 幂等重试
            arch2 = _run_script(
                "archive_stage.py",
                "--repo", str(repo),
                "--handoff", str(handoff),
                "--confirmed",
            )
            self.assertEqual(arch2.returncode, 0, arch2.stdout + arch2.stderr)

            # 开启下一阶段应沿用全局路径
            boot2 = _run_script(
                "bootstrap_workflow.py",
                "--repo", str(repo),
                "--project-name", "Demo",
                "--stage", "02-next",
            )
            self.assertEqual(boot2.returncode, 0, boot2.stdout + boot2.stderr)
            self.assertTrue((repo / "docs/workflow/stages/02-next/TASKS.md").is_file())

    def test_document_contracts_benchmark_cards_have_zero_errors_and_zero_warnings(self) -> None:
        contracts = (REPO_ROOT / "references/document-contracts.md").read_text(encoding="utf-8")
        blocks = re.findall(r"```markdown\n(### \[ \] T\d+[\s\S]*?)\n```", contracts)
        self.assertGreaterEqual(len(blocks), 2, "document-contracts.md 应包含至少两张标杆范例卡")

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _run_script("bootstrap_workflow.py", "--repo", str(repo), "--project-name", "Demo", "--stage", "01-bench")
            tasks_md = (
                "# Demo — 标杆范例校验\n\n"
                "## 模型分层概览\n\n"
                "- `luna-max`：1 | `sol-medium`：1\n\n"
                + "\n\n".join(blocks)
                + "\n"
            )
            _write_clean_stage_docs(repo, "01-bench", tasks_md)
            tasks, errors, warnings = validate_workflow.inspect_workflow(repo)
            self.assertEqual(len(tasks), 2)
            self.assertEqual(errors, [])
            self.assertEqual(warnings, [], f"标杆范例卡不应触发任何警告，但出现：{warnings}")

    def test_backward_compatibility_english_and_legacy_with_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _run_script("bootstrap_workflow.py", "--repo", str(repo), "--project-name", "Legacy", "--stage", "01-old")
            stage_dir = repo / "docs/workflow/stages/01-old"
            (stage_dir / "REQUIREMENTS.md").write_text("# Old stage\n\nSimple goal.\n", encoding="utf-8")
            (stage_dir / "PROGRESS.md").write_text("# Progress\n\nPlain text only.\n", encoding="utf-8")
            (stage_dir / "PROMPT_TEMPLATE.md").write_text("# Prompt\n\nDispatch worker.\n", encoding="utf-8")
            (repo / "docs/DECISIONS.md").write_text("# Decisions\n\nNone.\n", encoding="utf-8")
            old_tasks = """# Old Tasks

### [ ] T01 — Build retrieval adapter

**Dependencies:** None
**Worker:** spec-worker-sol-high
**Routing rationale:** Cross-module retrieval logic.
**Requirements:** R01 in REQUIREMENTS.md
**Scope:** Retrieval port and existing SQL/keyword adapter with tests.
**Behavior:** Read snapshots from storage and validate revocation.
**Boundaries:** Reject stale or revoked sources.
**Acceptance:** A1. Reads SQL corpus. A2. Rejects revoked source.
**Verification:** L2. Run relevant contract tests and typecheck.

### [ ] T02 — Build model config

**Dependencies:** T01
**Worker:** spec-worker-sol-high
**Routing rationale:** Credential wrapping across services.
**Requirements:** R01 in REQUIREMENTS.md
**Scope:** Model config module and CLI.
**Behavior:** Save and switch named profiles.
**Boundaries:** Never leak credentials.
**Acceptance:** A1. Profiles switch cleanly. A2. Old versions revoked.
**Verification:** L3. Run isolated database tests.

### [ ] T03 — Build pipeline engine

**Dependencies:** T02
**Worker:** spec-worker-sol-xhigh
**Routing rationale:** Multi-stage execution state.
**Requirements:** R01 in REQUIREMENTS.md
**Scope:** Generation engine and prompts.
**Behavior:** Execute pipeline end to end.
**Boundaries:** Respect timeout limits.
**Acceptance:** A1. Produces full edition. A2. Reuses passed items.
**Verification:** L2. Run engine regression checks.
"""
            (stage_dir / "TASKS.md").write_text(old_tasks, encoding="utf-8")

            # validate() 原签名保持 0 errors
            tasks, errors = validate_workflow.validate(repo)
            self.assertEqual(len(tasks), 3)
            self.assertEqual(errors, [])

            # CLI 默认退出码 0，同时暴露全部新规范 Warning
            res = _run_script("validate_workflow.py", "--repo", str(repo))
            self.assertEqual(res.returncode, 0, res.stdout)
            self.assertIn("WARN T01: 缺少“任务背景”字段", res.stdout)
            self.assertIn("WARN T01: 缺少“实施步骤”字段", res.stdout)
            self.assertIn("WARN T01: 缺少“禁区与约束”字段", res.stdout)
            self.assertIn("WARN T01: “修改范围”未给出具体文件或目录路径", res.stdout)
            self.assertIn("WARN T01: “验收标准”建议逐条分行编写", res.stdout)
            self.assertIn("WARN T01: “验证方式”缺少具体可执行的命令或测试文件路径", res.stdout)
            self.assertIn("WARN T01: 选用了高配执行者", res.stdout)
            self.assertIn("WARN [路由分布] 本阶段共 3 张任务卡，但 luna-max 与 sol-medium 占比为 0%", res.stdout)
            self.assertIn("WARN [PROGRESS.md]", res.stdout)
            self.assertIn("WARN [PROMPT_TEMPLATE.md]", res.stdout)
            self.assertIn("WARN [REQUIREMENTS.md]", res.stdout)

            # --strict-warnings 返回 1
            strict_res = _run_script(
                "validate_workflow.py", "--repo", str(repo), "--strict-warnings"
            )
            self.assertEqual(strict_res.returncode, 1)

    def test_legacy_root_layout_still_supported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            for name in validate_workflow.REQUIRED_FILES:
                (repo / name).write_text(f"# {name}\n\nReady.\n", encoding="utf-8")
            (repo / "TASKS.md").write_text(
                "# Legacy\n\n### [ ] T01 — Quick fix\n\n"
                "**依赖:** 无\n"
                "**Worker:** spec-worker-luna-max\n"
                "**Routing rationale:** Single file fix.\n"
                "**范围:** `src/util.py`\n"
                "**验收:** - A1. Fix works.\n"
                "**Verification:** L1. `python3 -m unittest tests/test_util.py`\n",
                encoding="utf-8",
            )
            tasks, errors = validate_workflow.validate(repo)
            self.assertEqual(len(tasks), 1)
            self.assertEqual(errors, [])

    def test_granularity_and_high_ratio_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _run_script("bootstrap_workflow.py", "--repo", str(repo), "--project-name", "Demo", "--stage", "01-ratio")
            # 4 张卡里 3 张高配（75% > 70%）且 T01 涉及 10 个文件（> 8）
            huge_scope_tasks = VALID_TASKS_MD.replace(
                "- 新增 `src/shared/schedule.ts` 与 `tests/unit/schedule.test.ts`",
                "- 修改 `src/a/{f1.ts,f2.ts,f3.ts,f4.ts,f5.ts}`、`src/b/{g1.ts,g2.ts,g3.ts,g4.ts}`、`tests/unit/schedule.test.ts`",
            ).replace(
                "**执行者:** spec-worker-luna-max\n**路由理由:** 纯文档与配置文案更新",
                "**执行者:** spec-worker-sol-high\n**路由理由:** 已拆分无关项但仍涉及强耦合状态，无法拆细降级。",
            ).replace(
                "**执行者:** spec-worker-sol-medium",
                "**执行者:** spec-worker-sol-high",
            )
            _write_clean_stage_docs(repo, "01-ratio", huge_scope_tasks)
            _, errors, warnings = validate_workflow.inspect_workflow(repo)
            self.assertEqual(errors, [])
            joined = "\n".join(warnings)
            self.assertIn("T01: “修改范围”涉及较多路径/文件", joined)
            self.assertIn("[路由分布] 本阶段高配任务卡占比偏高（3/4，75%）", joined)

            # 确认“超时拆解”这类业务词不会误判为“已论证不可拆细降级”
            false_positive_tasks = VALID_TASKS_MD.replace(
                "涉及 PostgreSQL 事务租约、同档复用与 14:00 跨档必刷新的强状态一致性，已将纯档期函数（T01）和前端展示（T03）拆出，剩余事务状态机无法继续拆细降级到 sol-medium。",
                "涉及固定安全传输层改造与流式超时拆解，需要严谨处理部分响应与取消边界。",
            )
            _write_clean_stage_docs(repo, "01-ratio", false_positive_tasks)
            _, errors2, warnings2 = validate_workflow.inspect_workflow(repo)
            self.assertEqual(errors2, [])
            self.assertIn("T04: 选用了高配执行者（spec-worker-sol-high）", "\n".join(warnings2))

    def test_worker_profile_tomls_valid_and_differentiated(self) -> None:
        expected = {
            "spec-worker-luna-max": ("gpt-6-luna", "max"),
            "spec-worker-sol-medium": ("gpt-6.2-sol", "medium"),
            "spec-worker-sol-high": ("gpt-6.2-sol", "high"),
            "spec-worker-sol-xhigh": ("gpt-6.2-sol", "xhigh"),
            "spec-worker-sol-max": ("gpt-6.2-sol", "max"),
            "spec-worker-astra-medium": ("gpt-6.2-astra", "medium"),
            "spec-worker-astra-high": ("gpt-6.2-astra", "high"),
            "spec-worker-astra-xhigh": ("gpt-6.2-astra", "xhigh"),
            "spec-worker-astra-max": ("gpt-6.2-astra", "max"),
        }
        profiles = sorted((REPO_ROOT / "assets/worker-profiles").glob("*.toml"))
        self.assertEqual(len(profiles), 9)
        unique_instructions: set[str] = set()
        for path in profiles:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["name"], path.stem)
            self.assertEqual(
                (data["model"], data["model_reasoning_effort"]),
                expected[path.stem],
            )
            self.assertIn("任务卡", data["developer_instructions"])
            unique_instructions.add(data["developer_instructions"].strip())
        self.assertGreaterEqual(len(unique_instructions), 5)


if __name__ == "__main__":
    unittest.main()
