# 阶段文档契约、写作规范与生命周期

## 1. 目录结构与文档权威

默认目录结构：

```text
AGENTS.md                              仓库级协作约定与实际命令
requirement.md                         用户原始需求（如已提供）
docs/ARCHITECTURE.md                   当前项目架构与公共契约（跨阶段延续）
docs/DECISIONS.md                      重要决策与跨阶段技术债（跨阶段延续）
docs/workflow/current.md               当前阶段身份、状态与文档路径映射
docs/workflow/stages/01-stage-name/    当前阶段工作目录
   REQUIREMENTS.md                     阶段需求、背景目标、排除范围与覆盖表
   TASKS.md                            任务依赖图、模型分层概览与施工任务卡
   PROGRESS.md                         进度看板、阻塞项、待拍板决策与技术债
   ACCEPTANCE.md                       验收证据账本
   PROMPT_TEMPLATE.md                  单卡派发模板与本阶段实现红线
docs/workflow/archive/01-stage-name/   已归档阶段快照、交接单与校验清单
```

`docs/workflow/current.md` 用 `**键名:** 相对路径` 维护映射（为保证脚本与历史项目兼容，键名固定为 `Stage`、`Status`、`Requirements`、`Tasks`、`Progress`、`Acceptance`、`Prompt`、`Architecture`、`Decisions`、`Instructions`，路径均为仓库相对路径）。

如果仓库原本已有架构、决策或任务文档，通过初始化脚本的 `--paths` 参数直接映射沿用，绝不为了迎合默认路径而复制一套新文档。旧的根目录工作流文档仍然可以被校验脚本识别。

**权威层级：** 用户最新确认的需求与仓库规则 > 项目架构 > 阶段任务卡 > 进度记录与历史归档。

## 2. 写作规范：人看得懂，子代理跑不偏

写每一份文档时，牢记以下四条硬标准：

1. **拒绝黑话堆砌与电报体**：用自然流畅的中文把事说清楚。避免一整段无换行塞满 10 个抽象概念；复杂规则用编号步骤或对照表呈现。
2. **必须有面向人类的解释层**：
   - `REQUIREMENTS.md` 开头写清“为什么要做、现在痛点在哪、做完后直观变化是什么”；
   - `ARCHITECTURE.md` 开头讲清“系统分工原则与核心设计取舍”；
   - `PROGRESS.md` 顶部提供**2–4 句人话总结 + 全阶段状态看板表 + 阻塞与待拍板决策 + 方向变更与技术债**，让人不用翻十几个文件就能把握全局；
   - `DECISIONS.md` 同步记录**为什么选 A 放弃 B**，以及**暂时妥协留下的技术债和后续清理触发条件**。
3. **禁止悬空指代**：不许写“修改现有组件”“调用已有接口”“使用约定文案”“跑相关单测”这类含糊表述，必须写明具体路径、符号、字符串值或命令。
4. **把“施工步骤”和“防跑偏禁区”写进任务卡与派发模板**：子代理在全新上下文开工，看不到主代理和用户的讨论过程；主代理少写一行具体步骤，子代理就多一分脑补跑偏的风险。

## 3. 各文档核心职责

### 项目级文档（跨阶段持续维护）
- **`docs/ARCHITECTURE.md`**：当前系统的设计原则、技术取舍、端到端数据流、模块代码定位表（含明确路径与越界禁止）、核心数据规则、接口约定、安全隐私与运行验证基线。接口或核心规则变动时，先改架构再派发依赖它的任务。
- **`docs/DECISIONS.md`**：持久保存关键架构/产品决策（含备选方案、理由、后果及取代关系）和**跨阶段技术债表**。被取代的旧决策保留原文并标注新决策编号。
- **`AGENTS.md`**：记录本项目真实的安装/测试/类型检查/构建命令、目录归属、分级验证规则与授权边界，避免放空泛的模板口号。

### 阶段级文档（每个阶段独立一套）
- **`REQUIREMENTS.md`**：一句话目标与背景、用户确认依据与讨论共识、核心场景与预期行为、需求清单与任务覆盖表、明确不做（范围排除）与约束、阶段完成标准、上一阶段遗留问题与技术债处置。
- **`TASKS.md`**：阶段顶部附**依赖关系与提交批次图**及**模型分层概览**；正文是按依赖排列的任务卡。每张卡包含：
  - `依赖`、`执行者`、`路由理由`、`关联需求`
  - `任务背景`（人话说明意图与上下游位置）
  - `修改范围`（确切文件路径、涉及函数/类及明确排除区域）
  - `实施步骤`（分步具体做法，写清复用什么既有模块、怎么改）
  - `禁区与约束`（明确不能碰什么、不能用什么错误做法）
  - `边界与异常`（具体边界值与异常行为）
  - `验收标准`（`- A1.`、`- A2.` 逐条分行、可客观核对）
  - `验证方式`（L0–L3 级别 + 精确可执行命令、测试路径与预期输出）
  - 可选 `提交策略`（标明“独立提交”或“随批次 X 合并提交”）
- **`PROGRESS.md`**：人话进度总览、任务状态看板表、当前阻塞项与待用户拍板的决策、重要方向变更与已知技术债、精简执行/返工记录。只由主代理维护。
- **`ACCEPTANCE.md`**：记录实际验收证据（证据编号、覆盖的卡号与验收项、具体命令或检查内容、实际结果、测试代码基线与环境、复用/失效条件、重跑或跳过原因）。
- **`PROMPT_TEMPLATE.md`**：实例化派发输入清单、**本阶段全局实现红线**、执行者开工前核对协议、执行自检纪律与标准回报格式。

## 4. 标杆任务卡范例

下面两张卡片展示了健康拆解与详实描述的标准——请参照这种具体程度编写新任务卡，不要压缩成几行空话。

### 范例 A：低配确定性切片（`spec-worker-luna-max`）

```markdown
### [ ] T01 — 新增早晚刊档期纯函数模块与边界单测

**依赖:** 无
**执行者:** spec-worker-luna-max
**路由理由:** 纯时间换算与档期常量模块，输入输出和边界规则完全确定，不涉及数据库、网络或跨模块状态协调，适合交由 luna-max 快速准确完成。
**关联需求:** [R01](REQUIREMENTS.md)，架构 §4
**任务背景:** 调度器和前端都需要把北京时间映射到“晨刊（08:00）/ 午刊（14:00）/ 凌晨基础版”三个档期。先把这套纯函数规则抽成零副作用的共享模块，供后续后端调度卡（T02）和前端展示卡（T03）直接复用。
**修改范围:**
- 新增 `src/shared/journal-schedule.ts`（档期常量与纯函数）
- 新增 `tests/unit/journal-schedule.test.ts`（全边界单元测试）
- 排除：不修改 `src/server/journal/`、`src/components/` 或任何数据库文件。
**实施步骤:**
1. 在 `src/shared/journal-schedule.ts` 中导出 `JournalEditionSlot = 'morning' | 'afternoon'`、常量 `MORNING_CHECK_HOUR = 8`、`AFTERNOON_CHECK_HOUR = 14`、`PRE_MORNING_CHECK_HOUR = 0`、`JOURNAL_WEATHER_MAX_AGE_MS = 12 * 60 * 60_000`。
2. 实现纯函数 `scheduledEditionSlot(date: Date)`（`00:00–07:59` 返回 `null`，`08:00–13:59` 返回 `'morning'`，`14:00–23:59` 返回 `'afternoon'`，按 `Asia/Shanghai` 计算）、`scheduledCheckHour(date)`、`visitCheckHour(date)`（凌晨返回 `0`）与 `slotStartMs(date)`。
3. 在 `tests/unit/journal-schedule.test.ts` 中补齐北京时间 `00:00`、`07:59`、`08:00`、`13:59`、`14:00`、`23:59` 与跨 UTC 日界用例。
**禁区与约束:**
- 严禁引入 `node:crypto`、`fs` 等服务端专用模块（前端浏览器会直接引用本文件）。
- 严禁依赖系统本地默认时区，必须显式按 `Asia/Shanghai` 换算。
**边界与异常:** 传入非法 `Date`（`Number.isNaN(date.getTime())`）时抛出明确的 `RangeError`；不涉及并发或外部 I/O。
**验收标准:**
- A1. `00:00` / `07:59` 返回 `scheduledEditionSlot === null` 且 `visitCheckHour === 0`；`08:00` / `13:59` 返回 `'morning'` 与 `8`；`14:00` / `23:59` 返回 `'afternoon'` 与 `14`。
- A2. 无论运行环境 `TZ` 为 `UTC` 还是 `America/New_York`，结果均与北京时间一致。
- A3. 模块无任何 Node 专属依赖，TypeScript 严格编译通过。
**验证方式:** L1。执行 `TZ=UTC pnpm exec vitest run tests/unit/journal-schedule.test.ts`（覆盖 A1/A2）与 `pnpm typecheck`（覆盖 A3），预期单测全绿、类型检查 0 报错。
**提交策略:** 随本批次（T01–T02）合并提交
```

### 范例 B：契约清晰的中等实现切片（`spec-worker-sol-medium`）

```markdown
### [ ] T03 — 前台报头、出处抽屉与订阅预览同步为晨刊/午刊文案

**依赖:** T01
**执行者:** spec-worker-sol-medium
**路由理由:** 涉及 4 个前端展示与交互文件的文案和选项同步，公共 DTO 的 `slot` 字段和每一处确切展示文案都已在卡片写死，无复杂状态机或架构不确定性，适合 sol-medium 一次完成。
**关联需求:** [R03](REQUIREMENTS.md)，架构 §4、§6
**任务背景:** 后端已把 `edition.slot`（`'morning' | 'afternoon'`）输出到共享读取接口。本卡把前台报纸报头、外拍手册天头、出处抽屉和订阅预览纸单同步为新的“晨刊 / 午刊（08:00 / 14:00）”呈现，并保持原有视觉风格不变。
**修改范围:**
- 修改 `src/components/prototype-frontend/journal-view.ts`（`journalStatus`、`journalBookHtml`、`journalIdentity`、`journalSourcesHtml`）
- 修改 `src/components/prototype-frontend/index.tsx`（无障碍状态栏文本）
- 修改 `src/components/prototype-frontend/template.ts` 与 `src/components/prototype-frontend/runtime.ts`（订阅预览单选时段与白名单）
- 更新 `tests/unit/prototype-adapter.test.ts` 与 `tests/e2e/subscription-overlay.spec.ts`
- 排除：不改 CSS 材质与布局，不碰 `prototype/` 原型目录和后端 `src/server/`。
**实施步骤:**
1. 在 `journal-view.ts` 中依据 `edition.slot` 将正式期次标签统一渲染为“晨刊”或“午刊”；无正式期次保持“基础版”/“天气与摄影基础版”；凌晨准备态（`scheduledEditionSlot(projectedAt) === null`）显示“正在准备当地天气与基础版。”。
2. 在 `journalSourcesHtml` 的 `<dl>` 首位新增 `<dt>当前期次</dt><dd>晨刊（08:00） · 第 N 期</dd>`（午刊对应 `午刊（14:00） · 第 N 期`；基础版显示 `天气与摄影基础版`）。
3. 同步更新 `index.tsx` 无障碍状态栏，并将 `template.ts` 与 `runtime.ts` 中的订阅时段从 `07:00 / 12:00` 更新为 `08:00`（默认）与 `14:00`。
4. 更新单测断言和订阅预览 E2E 用例，补齐晨刊、午刊、凌晨基础版三种渲染分支。
**禁区与约束:**
- 严禁在任何新增静态文案里加入免责套话或多余提示语。
- 严禁新增按钮、装饰徽章或改动现有桌面排版尺寸。
**边界与异常:** 缺失期号时详情行省略“ · 第 N 期”而不出现 `undefined`；订阅表单提交非 `08:00`/`14:00` 值时保持既有校验拒绝逻辑。
**验收标准:**
- A1. 晨刊/午刊分别在报纸报头、手册天头、无障碍状态栏准确显示“晨刊”/“午刊”，详情抽屉首位显示对应档期与期号。
- A2. 订阅预览纸单默认选中 `晨刊 08:00`，切换到 `午刊 14:00` 提交与回执正常。
- A3. 静态文案人工复核零免责声明，且桌面单测、E2E 与类型检查全通。
**验证方式:** L2。执行 `pnpm exec vitest run tests/unit/prototype-adapter.test.ts`（A1）、`pnpm exec playwright test tests/e2e/subscription-overlay.spec.ts`（A2）与 `pnpm typecheck`（A3），并审阅 diff 确认文案红线与未改动排除目录。
**提交策略:** 独立提交
```

验收通过后，在卡片末尾追加 `**验收证据:**`（引用 `ACCEPTANCE.md` 中的证据编号并简述实测结果），再勾选 `[x]`。对于经用户批准移出或移交下一阶段的未完成卡，保持 `[ ]` 未勾选并追加 `**未完成处置:**`（写明用户批准依据、原因和去向）。已移交的未完成卡不能算作当前阶段的已完成依赖。

## 5. 初始化、校验与阶段内变更

执行脚本前，先从当前加载的 Maestro `SKILL.md` 所在目录解析 `<skill-dir>`（Codex 默认安装路径为 `~/.codex/skills/maestro`，含软链接场景）。

```bash
python3 <skill-dir>/scripts/bootstrap_workflow.py --repo <仓库根目录> --project-name "项目名" --stage 01-stage-name
python3 <skill-dir>/scripts/validate_workflow.py --repo <仓库根目录>
```

- **初始化**：`bootstrap_workflow.py` 只创建缺失文件，不覆盖已有文档。可先用 `--dry-run` 预览目标路径，用 `--paths <映射.json>` 复用项目既有文档（例如 `{"Architecture": "docs/ARCHITECTURE.md", "Decisions": "docs/DECISIONS.md"}`）。初始化后必须把模板里的占位说明替换成真实内容再派发任务。
- **结构与质量校验**：`validate_workflow.py` 同时兼容新中文规范与历史英文/旧格式文档：
  - `ERROR`（退出码 1）：缺必填文件、缺核心字段、占位符未清、非法执行者名、依赖环或未闭合处置等结构错误，必须修复。
  - `WARN`（默认退出码 0，可用 `--strict-warnings` 转为失败）：暴露不符合新规范的质量问题——例如缺少任务背景/实施步骤/禁区与约束、修改范围未写具体文件路径、验收标准未分行、验证方式缺少具体命令、单卡范围过大、高配路由未说明为何不能拆细降级、全阶段中低配模型占比为 0、进度看板或派发红线缺失等。
  - **主代理必须认真处理每一条新阶段产生的 `WARN`**：能补齐的直接补齐，确实合理的特殊情况要在文档中写明理由。脚本通过不代表需求覆盖和语义完整，仍须人工复核。
- **阶段内变更**：重大需求改动先走受影响分支的讨论确认，再同步修订当前阶段文档、架构、依赖与受影响的证据有效性，不要为每个小改动都新建阶段。任务结构变动后重跑一次校验即可。

## 6. 收尾、归档与中断恢复

1. 逐条核对阶段需求、任务卡状态和有效证据，只补做缺失的阶段级集成检查。
2. 所有未完成需求必须完成或取得用户明确的范围调整与去向批准，对应任务保持 `[ ]` 并补充 `**未完成处置:**`。
3. 编写阶段交接文档，写清：已交付能力、接口/数据/环境变化、已知问题与**遗留技术债**、未完成需求的批准去向、证据适用范围，以及下一阶段规划输入。
4. 把完整收尾总结发给用户确认。
5. **拿到用户明确确认后**，执行归档脚本（先 `--dry-run` 预检再正式运行；绝不能在未获确认时私自传 `--confirmed`）：

```bash
python3 <skill-dir>/scripts/archive_stage.py --repo <仓库根目录> --handoff <交接文件.md> --confirmed --dry-run
python3 <skill-dir>/scripts/archive_stage.py --repo <仓库根目录> --handoff <交接文件.md> --confirmed
```

归档会把所有映射文档、阶段目录附件、项目级文档快照、交接单 `HANDOFF.md` 与 SHA-256 清单 `manifest.json` 原子写入 `docs/workflow/archive/<阶段名>/`，保留源文档不动，并把 `current.md` 状态切为 `archived`。若中途中断，用同一阶段名和同一交接文件重试即可恢复，遇哈希冲突须人工排查，绝不覆盖历史归档。

开启下一阶段时，先带着交接单里的遗留项和技术债与用户讨论确认，再以新的阶段名运行 `bootstrap_workflow.py`（自动沿用项目级架构、决策与仓库约定路径）。
