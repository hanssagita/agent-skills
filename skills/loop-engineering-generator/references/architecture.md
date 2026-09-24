# Loop Engineering & Agent Systems Architecture

---

## 1. The 4 Systems Layers

When an agent moves beyond toy demos into real codebases, terminals, and production workflows, you are no longer just prompting a model. You are designing a system.

Four distinct layers sit around the model:

```
┌─────────────────────────────────────────────────────────────┐
│                 4. Environment Engineering                  │
│       (Durable runtime context, workspace contracts)        │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                  3. Graph Engineering                   │ │
│ │             (Workflow topology & routing)               │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │                 2. Loop Engineering                 │ │ │
│ │ │        (Iterative work-and-feedback cycles)         │ │ │
│ │ │ ┌─────────────────────────────────────────────────┐ │ │ │
│ │ │ │              1. Harness Engineering             │ │ │ │
│ │ │ │           (Operating conditions & tools)        │ │ │ │
│ │ │ │                  [ THE MODEL ]                  │ │ │ │
│ │ │ └─────────────────────────────────────────────────┘ │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

| Layer | Question Answered | Core Responsibilities |
| :--- | :--- | :--- |
| **1. Harness** | *Can the model operate?* | Context injection, action surfaces (tools/APIs), persistence, token budgets, safety sandbox. |
| **2. Loop** | *How does work improve?* | Trigger, goal, state, action policy, evidence, feedback, stop rule. |
| **3. Graph** | *What is allowed next?* | Topology, explicit nodes/edges, parallel joins, human escalation branches. |
| **4. Environment** | *Does context endure?* | Workspace contracts, durable memory promotion, review boundaries, cross-run stability. |

---

## 2. Model & Environment Agnosticism

Loop engineering does not depend on a specific LLM or a specific IDE.
- **Model Independence:** The loop contract and objective verifiers work identically whether powered by Claude, GPT-4o, Gemini, Llama, DeepSeek, or specialized fine-tunes.
- **IDE Independence:** The contract is authored as a portable `LOOP.md` markdown file accompanied by native test commands or standard Python/Bash scripts. It executes smoothly in Claude Code, Cursor, Antigravity, OpenCode, Windsurf, Cline, Aider, GitHub Copilot, or automated CI/CD runners.

---

## 3. Adapting to the Environment: Brownfield vs. Greenfield

### Path A: Brownfield (Existing Repositories)
A production loop must never force alien tooling on an established codebase.
1. **Auto-Discovery:** Inspect existing manifests:
   - Node: `package.json`, `pnpm-lock.yaml`, `yarn.lock`, `bun.lockb`
   - Python: `pyproject.toml`, `setup.cfg`, `requirements.txt`, `pytest.ini`
   - Rust: `Cargo.toml`
   - Go: `go.mod`
   - Java: `pom.xml`, `build.gradle`
2. **Conventions Ingestion:** Read existing guides (`README.md`, `AGENTS.md`, `CLAUDE.md`, `.cursorrules`).
3. **Verifier Calibration:** Wire the primary verification gate to the repository's native test suite (e.g. `pnpm test`, `pytest tests/`, `cargo test`).

### Path B: Greenfield (New Projects) — The Interview & Grill Protocol
When starting from scratch, silence is dangerous. The agent must proactively interrogate the human operator before scaffolding:
- **Language & Runtime:** Exact version and ecosystem.
- **Framework & Libraries:** Target architecture and packages.
- **Test Framework:** What tool will act as the objective checker (e.g. Vitest, Pytest, Go test)?
- **Binary Success Definition:** What exact command or output confirms completion?
- **Iteration Ceiling:** Hard cap on loops (default $\le 4$).

---

## 4. Core Stance: Loop on Evidence, Not Confidence

### The Confidence Fallacy
LLMs are trained to speak with high confidence even when hallucinating or delivering broken code. When an agent says:
> *"I have verified the implementation and everything is working properly."*

**That is confidence, not evidence.** A loop that terminates on the agent's self-reported satisfaction is an open liability.

### Objective Evidence Defined
A valid stop condition requires objective, non-LLM or externally verifiable proof:
1. **Automated test suite exits with code 0** (`pytest`, `npm test`, `cargo test`).
2. **Deterministic schema validation passes** (`pydantic`, `zod`, `jq`).
3. **Static linters and type checkers report zero errors** (`tsc`, `ruff`, `eslint`).
4. **Targeted regression checks pass** without touching out-of-scope files.
5. **Diff bounds are respected** (e.g., `< 50 lines changed`, zero unprompted refactoring).

---

## 5. The 6 Building Blocks of a Production Loop

Every resilient loop consists of six explicit components:

```
Trigger ──> Context ──> Action ──> Verification ──> State ──> Stop Condition
```

1. **Automation (Heartbeat Trigger):** What initiates the cycle? (Git push, failed CI job, user task, schedule).
2. **Context (Hot & Warm State):** What does the agent read before acting? (Repo conventions, error logs, contract, diff budget).
3. **Action Policy (Boundaries):** What tool calls or edits is the agent allowed to execute? (Surgical edits only; no package additions without authorization).
4. **Verification Gate (Checker):** How is output verified? (Automated gate command, external tester, schema parser).
5. **State Persistence (Durable Memory):** Where is progress recorded? (Task log, git branch, state file).
6. **Stop Conditions (Binary Exits):**
   - **Success Exit:** Verifier passes with 0 errors.
   - **Failure Exit:** Max iterations ($N \le 4$) reached without passing.
   - **Escalation Exit:** Unrecoverable environment failure or contradictory requirement detected.

---

## 6. The Maker-Checker Split

Self-review has identical blind spots to generation. A single agent attempting to generate code and evaluate its own correctness suffers from confirmation bias.

### The Protocol
- **The Maker (Builder):**
  - Focuses on minimal, surgical execution.
  - Generates small diffs aligned strictly with the goal.
  - Follows the Simplicity Rule: *Minimum code that solves the problem. Nothing speculative.*
- **The Checker (Auditor/Gate):**
  - Completely detached from the creation process.
  - Executes objective verification commands.
  - Checks for diff noise, unexpected file modifications, and behavioral regressions.
  - Returns binary pass/fail evidence with exact error outputs.

---

## 7. Diagnostic Guide: Diagnosing the Bottleneck Layer

When an agentic system fails or produces low-quality work, diagnose the failure layer before modifying anything:

```
                    ┌─────────────────────────┐
                    │ System Is Malfunctioning│
                    └────────────┬────────────┘
                                 │
           ┌─────────────────────┼─────────────────────┐
           ▼                     ▼                     ▼
[Cannot Operate]       [Unreliable Quality]   [Process Stalls/Loops]
  Harness Issue             Loop Issue              Graph Issue
  - Missing tool/API        - No objective gate     - Ambiguous routing
  - Stale state             - Self-review bias      - Infinite cycles
  - Truncated context       - Unbounded attempts    - Missing join step
```

- **If the agent cannot operate at all:** Fix the **Harness**. (Tools are broken, permissions denied, prompt context noisy or truncated).
- **If the agent runs but produces broken or unverified results:** Fix the **Loop**. (Missing verifier gate, looping on confidence, no stop rule).
- **If the multi-step process loses its way or deadlocks:** Fix the **Graph**. (Unclear handoffs between roles, missing human checkpoints, unmanaged branching).
- **If the system loses all learning and context across sessions:** Fix the **Environment**. (No workspace contract, missing durable memory promotion).

---

## 8. Durable Memory Architecture: The `.ai-context/` System

Agents without durable environment memory die when the session ends. The next agent starts from zero: unaware of why past architectures were chosen, unaware of existing gotchas, and prone to repeating identical mistakes.

The `.ai-context/` directory acts as the **Review Boundary** and persistent memory layer:

```
┌─────────────────────────────────────────────────────────────┐
│                      .ai-context/                           │
│ ┌─────────────────────────────┐ ┌─────────────────────────┐ │
│ │         decisions/          │ │        features/        │ │
│ │    NNN-<kebab-slug>.md      │ │    <feature-slug>.md    │ │
│ │ (Architecture Decisions)    │ │   (Domain Gotchas & Map)│ │
│ └─────────────────────────────┘ └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 1. Architecture Decision Records (ADRs)
- **Path:** `.ai-context/decisions/`
- **Naming Formula:** `NNN-<kebab-slug>.md` (zero-padded, incremental: e.g. `001-swr-state-cache.md`).
- **Core Elements:**
  - `Context`: 1–3 sentences defining the problem / PRD driver.
  - `Decision`: Chosen technical approach.
  - `Alternatives rejected`: Specific alternatives considered and why they were discarded.
  - `Affected files / modules`: Explicit file paths impacted.

### 2. Feature Context Notes
- **Path:** `.ai-context/features/`
- **Naming Formula:** `<feature-slug>.md` (e.g. `auth.md`, `billing.md`, `checkout.md`).
- **Update Rule:** Never create duplicates; update the existing feature file as code evolves.
- **Core Elements:**
  - `Where it lives`: Components, hooks, models, routes, tests.
  - `Key flows`: Entry point → outcome mapping.
  - `Conventions / gotchas`: Project gating, cache keys, translation namespaces, retry policies.
  - `Related decisions`: `[[NNN-<slug>]]` links to ADRs.

### 3. Closed Memory Loop
1. **At Loop Launch:** Agent reads existing `.ai-context/decisions/` and `.ai-context/features/` to establish hot context.
2. **At Loop Finish:** Once all objective verifier gates pass, learnings, decisions, and new gotchas are promoted to `.ai-context/`.

---

## 9. Comprehension Debt & Cost Bounds

### Comprehension Debt
Comprehension debt accumulates when autonomous loops produce code faster than human operators can understand, audit, and review. Unchecked comprehension debt guarantees codebase rot.

**Defense against comprehension debt:**
1. **Surgical diffs:** Restrict loops to under 50–100 changed lines per iteration.
2. **Explicit iteration caps:** Hard cap at 3–4 iterations maximum.
3. **No drive-by refactoring:** Changing formatting, unrelated comments, or variable names in untouched functions is strictly disallowed.
4. **Verifiable commit logs & context notes:** Every accepted iteration must state what was verified and update `.ai-context/`.

