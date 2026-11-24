<div align="center">

**English** &nbsp; · &nbsp; [简体中文](README.zh-CN.md)

✳ &nbsp; **M A E S T R O** &nbsp; ✳

# Maestro

**Requirement-driven orchestration for complex software development.**

Architecture, development planning, tiered subagents, and stage control — connected through durable project records.

[Explore the illustrated guide ↗](https://jay201368.github.io/maestro/) &nbsp; · &nbsp; [Install](#install) &nbsp; · &nbsp; [Read the skill](SKILL.md)

</div>

---

## Start with the user's requirements

Complex development often spans more work than a single conversation can retain. Architecture decisions, dependencies, acceptance criteria, and unfinished work all need to survive context changes.

Maestro is a Codex orchestration skill that organizes this work into a software engineering process. The user's requirements drive the architecture, the development plan, and the acceptance criteria. Project documents preserve the current contracts and delivery state, so fresh subagents can pick up bounded tasks and the main agent can resume coordination from recorded evidence.

## Clarify the requirements together

Maestro includes a grilling-style discussion before a new project, stage, or material requirement change. It maps dependent decisions, asks every currently answerable question in a round, and recommends an answer for each. Fresh investigators look up repository facts while the user decides product tradeoffs.

Once the relevant branches are resolved, Maestro summarizes the shared understanding for explicit user confirmation. That agreement drives initialization, architecture design and task planning. Confirmed conclusions carry into small changes and resumed work; new ambiguity reopens the affected branches. The protocol is bundled with Maestro.

## How the system fits together

![Maestro system map — user requirements guide the main agent, which maintains architecture and task plans, dispatches fresh workers, reviews results, and updates shared project records.](docs/assets/system-map.jpg)

The main agent maintains the architecture and dependency plan, dispatches bounded work, and accepts results. Shared project records provide the context for each fresh worker and resumed session.

## Follow one stage

![Maestro stage flow — discuss requirements, confirm shared understanding, initialize the stage, design architecture, plan tasks, repeat the dispatch and acceptance loop, then review, confirm, and archive the stage. Correction and remaining-task loops return work to the appropriate step.](docs/assets/stage-flow.jpg)

- **Discuss and confirm** the requirements before initialization. Resolve the relevant decision tree and confirm the shared understanding.
- **Plan** the architecture and task graph from that agreement before dispatch.
- **Execute** dependency-ready tasks with a fresh worker each time. Diagnose failed acceptance and retry the same task. Record and commit accepted work, then select the next ready task.
- **Close** the stage after reviewing its outcomes and resolving unfinished requirements through completion or an explicitly approved scope change. Confirm closure, archive the handoff, and plan the next stage.

The main agent creates one scoped local Git commit for each workflow/stage setup, each material workflow change, each saved or updated discussion handoff, and each completed stage archive. For task acceptance, core or high-risk cards commit individually, while tightly related low/mid-tier small cards (`luna-max` / `sol-medium`) may commit together as a planned mini-batch to reduce orchestration overhead.

## How execution stays coordinated

The main agent owns architecture decisions, upfront codebase fact-finding, fine-grained task slicing, routing, shared records, integration, and final acceptance. Each worker owns one task card with explicit file paths, step-by-step implementation actions, and anti-drift guardrails. Independent tasks can run in parallel, with a default limit of two implementation workers. Coupled work follows its dependency order.

Routing follows a **slice-first, default-downward, justify-escalation** discipline—actively offloading read-only investigations, pure utility modules, UI copy tweaks, dead-code cleanup, unit tests, and contract-defined implementations to lower tiers instead of defaulting everything to `sol-high+`. The nine bundled Chinese worker profiles carry tier-differentiated instructions:

| Model | Reasoning levels | Typical work |
| --- | --- | --- |
| Luna | max | Read-only codebase investigation, pure utility/type modules, UI copy/config tweaks, dead-code cleanup, unit tests, and doc sync |
| Sol | medium · high · xhigh · max | `medium` for contract-defined standard features & adapters; `high+` for cross-module state consistency, transactional/security logic, and hard debugging |
| Astra | medium · high · xhigh · max | Design uncertainty, tradeoff synthesis, cross-system architecture, and high-stakes core challenges |

Genuinely complex tasks can start directly at higher tiers, provided the routing rationale explains why slicing or clearer steps cannot bring them down to `luna-max` / `sol-medium`. Failed acceptance first triggers diagnosis of the requirement, environment, implementation, or reasoning issue. See the [routing guide](references/worker-routing.md) for selection and correction rules.

## Continue across context boundaries

The skill, references, templates, and worker profiles are written in plain, jargon-free Simplified Chinese to serve both humans tracking direction/progress and fresh subagents executing tasks without guesswork. Stage documents include executive context, a task-status dashboard, blockers, pending decisions, and technical debt tracking; task cards specify concrete paths, implementation steps, guardrails, and exact verification commands.

| Persistent context | Purpose |
| --- | --- |
| Architecture and decisions | Carry design principles, module code maps, durable rationale, and cross-stage technical debt |
| Stage requirements and tasks | Preserve goals, exclusions, dependency/batch map, model-tier summary, and actionable task cards |
| Progress and acceptance records | Provide a scannable status dashboard, blockers, direction changes, and reusable verification evidence |
| Archived stages and handoffs | Preserve delivered behavior, changes, open technical debt, and inputs to the next stage |

Verification follows the risk of the change, and applicable evidence is reused across worker review and stage acceptance. `scripts/validate_workflow.py` stays fully backward-compatible with legacy and English stage records while surfacing non-compliant quality gaps—such as missing steps/guardrails, vague paths or commands, oversized cards, missing escalation rationale, or 0% low/mid-tier routing—via explicit `WARN` diagnostics (with optional `--strict-warnings`). See the [document contracts](references/document-contracts.md) for the complete lifecycle.

## Install

Clone the repository into your Codex skills directory, then install the worker profiles.

```bash
git clone https://github.com/JAY201368/maestro.git ~/.codex/skills/maestro
mkdir -p ~/.codex/agents
cp ~/.codex/skills/maestro/assets/worker-profiles/*.toml ~/.codex/agents/
```

Start a new chat after installing or updating the profiles so Codex can discover them. Invoke the skill with:

```text
$maestro
```

Describe the outcome you need and provide existing requirements or project documents. Maestro starts by clarifying unresolved decisions with you and confirming the shared understanding. Maestro can adapt to the repository's document paths. Available models and effective runtime settings depend on your Codex environment.

## Repository contents

| Path | What it contains |
| --- | --- |
| [SKILL.md](SKILL.md) | The orchestration workflow and control rules |
| [references/](references/) | Document contracts and worker routing guidance |
| [assets/templates/](assets/templates/) | Starter documents for stage planning and execution |
| [assets/worker-profiles/](assets/worker-profiles/) | Nine custom worker configurations |
| [scripts/](scripts/) | Helpers to initialize, validate, and archive stage records |

---

<div align="center">

[Illustrated guide ↗](https://jay201368.github.io/maestro/) &nbsp; · &nbsp; [MIT License](LICENSE)

</div>
