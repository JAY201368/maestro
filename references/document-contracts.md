# Stage documents and lifecycle

## Paths and authority

Default layout:

```text
AGENTS.md
requirement.md                         original user requirement, when supplied
docs/ARCHITECTURE.md                  current project contracts
docs/DECISIONS.md                     durable project choices
docs/workflow/current.md             stage identity, status and path map
docs/workflow/stages/01-name/
   REQUIREMENTS.md
   TASKS.md
   PROGRESS.md
   ACCEPTANCE.md
   PROMPT_TEMPLATE.md
docs/workflow/archive/01-name/        closed-stage documents and handoff
```

`current.md` maps `Stage`, `Status`, `Requirements`, `Tasks`, `Progress`, `Acceptance`, `Prompt`, `Architecture`, `Decisions`, and `Instructions` using lines such as `**Tasks:** docs/workflow/stages/01-name/TASKS.md`. Paths are repository-relative. Preserve existing project organization using mapped paths. Read the bootstrap help for path-map input syntax. Legacy root-level workflows remain readable by the validator and can be adapted without rewriting completed work.

User instructions and applicable repository rules govern work. The original requirement remains a preserved source. Stage requirements link source requirements and agreed changes, define scope and closure criteria, and map every included requirement to tasks. An exclusion or transfer needs explicit user agreement when it changes requested scope.

## Project-level context

Architecture describes current goals, quality attributes, modules, contracts, data and state invariants, concurrency/retry behavior, security, deployment and verification assumptions as applicable. Update affected contracts before dependent implementation. Keep its established path.

Decisions record durable choices, reasons and consequences. Retain the history of superseded choices and clearly identify the current decision. These records persist across stages. Repository instructions contain actual commands, ownership rules and proportionate verification rules; avoid generic mandatory test/build matrices.

## Stage-level documents

- **REQUIREMENTS** — confirmed discussion summary and confirmation basis (the user message or other verifiable source and the scope it covers), key scenarios, boundaries, constraints, observable acceptance, confirmed goal, source links and requirement IDs, included outcomes, explicit exclusions, closure criteria, task coverage and inherited issues. Each inherited item gets a disposition during planning.
- **TASKS** — a dependency DAG of independently acceptable slices. Use stable task IDs within the stage and stage-qualified IDs across stages. Cards include Dependencies, Worker, Routing rationale, Requirements, Scope, Behavior, Boundaries, Acceptance and Verification. Behavior covers entry points, inputs/outputs and applicable states. Boundaries covers errors, concurrency, exclusions and relevant edge cases. Each acceptance item maps to a check or inspection. Keep simple tasks short but concrete.
- **PROGRESS** — current observable system state, accepted work, active task ownership, attempts/blockers, pending decisions and next ready tasks. Record worker identity/profile for lifecycle traceability. The main agent alone updates shared records.
- **ACCEPTANCE** — evidence IDs, task/criterion coverage, exact command or inspection, result, tested revision or file state, relevant environment, and invalidation conditions. Record why reused evidence remains valid and why any rerun was needed. A completed task's Evidence field references its evidence record. Preserve meaningful failures and skips.
- **PROMPT_TEMPLATE** — absolute repo root, mapped document paths, full card, owned files and exclusions, dependency evidence, profile/model/effort, verification plan and reusable evidence. Workers report proposed contract changes and decisions to the main agent. They do not edit shared workflow records.

Example card:

```markdown
### [ ] T01 — Show the saved display name

**Dependencies:** None
**Worker:** spec-worker-luna-max
**Routing rationale:** Existing read API and local rendering with explicit states.
**Requirements:** R01 in REQUIREMENTS.md
**Scope:** Profile header component and its directly relevant test.
**Behavior:** On profile load, render the saved display name from the existing profile API. Preserve loading and error states.
**Boundaries:** Escape user text. Empty names use the agreed account label. No profile editing or API changes.
**Acceptance:**
- A1. A saved nonempty name appears in the header as text.
- A2. Empty names and loading/error states follow the existing contract.
**Verification:** L1. Existing focused component check covers A1/A2, plus diff inspection for escaping and scope.
```

After acceptance add **Evidence** with the ledger reference and concise actual results, then mark `[x]`. For an unfinished card removed from scope by the user, retain `[ ]` and add **Disposition** with the explicit approval, reason and destination. An approved transfer cannot satisfy a dependency in the current stage.

The validator checks structure and declared evidence fields. Manually check semantic completeness, all requirement-to-task coverage, public contracts, proof applicability and actual approval. Passing a script does not establish those facts.

## Discussion before setup

Follow [requirements-discussion.md](requirements-discussion.md) for new projects/stages and material changes. Confirm the shared understanding before formal initialization, architecture design and task planning. Reuse relevant prior confirmations. Active-stage unresolved questions belong in progress; a new project or uninitialized next stage stays in conversation until confirmed. An archived stage's progress remains immutable; save any needed discussion handoff separately. Save a concise discussion handoff only when continuity across contexts requires it, then incorporate the confirmed outcome into requirements.

Bootstrap is a scaffolding utility. Its invocation assumes the main agent has obtained the required confirmation; script success does not establish approval. Existing documents remain usable without a retroactive interview. Reopen affected branches when a new ambiguity or material change appears.

## Setup and within-stage changes

Resolve `<skill-dir>` from the currently loaded Maestro `SKILL.md` path. For the default Codex installation, use `~/.codex/skills/maestro`, including when it is a symlink to a moved checkout. If an older chat or project record points to a missing script, check the current Maestro path before reporting it missing.

```bash
python <skill-dir>/scripts/bootstrap_workflow.py --repo <root> --project-name "Project" --stage 01-name
python <skill-dir>/scripts/validate_workflow.py --repo <root>
```

Bootstrap creates missing files and retains existing content. Use `--dry-run` to inspect destinations and `--paths <json-file>` to supply repository-relative document overrides when adapting a project. For example, a JSON object can contain `{"Architecture": "docs/ARCHITECTURE.md", "Decisions": "docs/DECISIONS.md", "Tasks": "existing/TASKS.md"}`. Omitted keys use defaults. Review the proposed map to reuse all established authoritative documents. The bootstrap does not move existing documents or change an active map implicitly. Replace scaffold placeholders before dispatch. Stage requirements may link an existing root requirement instead of copying it.

Within a stage, discuss and confirm material requirement changes before affected planning or implementation, then amend its existing documents. Clear small changes reuse the applicable confirmed understanding. Update the affected architecture, dependency edges and evidence validity when requirements change. Do not create a new stage for each small fix. After task-structure changes run the focused structural validator once; reuse that result until relevant structure changes.

## Closure, archival and recovery

1. Reconcile stage requirements, task status and applicable evidence. Obtain only missing integration evidence.
2. Resolve every unfinished requirement through completion or explicit user-approved scope adjustment and destination. Keep unfinished task boxes unchecked.
3. Prepare a handoff with delivered capabilities, interface/data/environment changes, known issues, transferred requirements and approvals, evidence applicability, and next-stage planning inputs.
4. Present the complete stage summary and obtain user confirmation to close/archive. Prior authorization is sufficient if it explicitly covers this concrete closure.
5. Run `python <skill-dir>/scripts/archive_stage.py --repo <root> --handoff <prepared-handoff.md> --confirmed` after confirmation. Use `--dry-run` to inspect closure readiness. `--confirmed` represents obtained approval; it must never be supplied as a substitute for approval. Include the prepared handoff. The archive preserves mapped stage documents, the full standard stage directory including evidence attachments, the original path map and snapshots of project context. Snapshots live under `archive/<stage>/files/<original-repository-relative-path>`, with `HANDOFF.md` and a hash manifest alongside them. Source documents remain in place; the current pointer switches to archived snapshots. The next stage uses new stage-document paths while preserving the original global-document paths.
6. If interrupted, rerun for the same stage with the same handoff. Inspect any conflict instead of replacing historical content. Keep closure recoverable and the current-stage pointer accurate.
7. Discuss the new stage after confirmation to enter it. Review every handoff item and resolve its destination with the user. Confirm shared understanding before bootstrapping a new, uniquely named stage with its own document set, then design its architecture and task graph. Project-level documents continue in place.

Do not treat all checked boxes as sufficient closure evidence. A user-approved transfer preserves an unmet requirement and its destination. Archive history stays immutable; corrective work belongs in the active stage with a reference to the closed record.
