---
name: loop-engineering-generator
description: Designs, scaffolds, audits, and executes autonomous closed-loop workflows with objective evidence gates, maker-checker split, bounded iteration budgets, zero comprehension debt, and durable AI context memory (.ai-context/ ADRs & feature notes). Adapts to existing repository standards or conducts a rigorous discovery interview for greenfield projects. Make sure to use this skill whenever the user mentions /loop-engineering, loop engineering, agent loops, feedback loops, iterative development, autonomous coding loops, TDD iteration, eval gates, or wants an agent to work in a loop until tests or verification criteria pass.
license: MIT
compatibility: Universal. Compatible with all AI coding agents (Claude Code, Cursor, Antigravity, OpenCode, Windsurf, Cline, Aider, Codex CLI, GitHub Copilot) and any model provider.
metadata:
  version: 1.2.0
  author: agent-skills
  tags:
    - loop-engineering
    - autonomous-agents
    - feedback-loops
    - verifier-gates
    - tdd
    - systems-architecture
    - ai-context
    - adr
---

# Loop Engineering Generator

Most people still use AI manually.

They type one prompt. They wait for one answer. They review the output themselves. They spot what is broken. They write another prompt.

It feels like the AI is doing the work. But if you look closely, the human is still the engine.

Loop engineering changes that: You do not just prompt the model. You design the work-and-feedback system around the model.

> **The Core Stance:**
> Prompting gives the AI an instruction.
> Loop engineering gives the AI a job.
> **Do not loop on confidence. Loop on evidence.**

---

### Universal LLM & IDE Agnostic Design

This workflow is 100% agnostic of model provider and development environment.

- **Models:** Claude, GPT, Gemini, Llama, DeepSeek, or local open-weights models.
- **Environments:** Claude Code, Cursor, Antigravity, OpenCode, Windsurf, Cline, Aider, GitHub Copilot CLI, or standalone terminal scripts.
- The contract (`LOOP.md`), verifiers, and memory records (`.ai-context/`) are plain Markdown, Python, and Shell. No proprietary runtime lock-in.

---

### The 30-Second Answer

Three ideas keep getting mixed together in agent architecture:
- **Harness engineering** builds the environment around the model (tools, memory, permissions).
- **Loop engineering** designs the repeated work-and-feedback cycle (trigger, verifier, stop rule).
- **Graph engineering** makes the workflow topology explicit (what is allowed to happen next).

A good mental model is: **Environment → Feedback → Flow**

- The harness gives the agent tools and operating conditions.
- The loop makes the work iterative and verifiable.
- The graph controls execution paths across specialists.

If you mix them up, you end up debugging the wrong layer.

---

### Step 0: The Environment Discovery Gate (MANDATORY)

Before constructing or running any loop, classify the project context into one of two paths:

```
                       ┌──────────────────────────────┐
                       │  Environment Discovery Gate  │
                       └──────────────┬───────────────┘
                                      │
              ┌───────────────────────┴───────────────────────┐
              ▼                                               ▼
   [PATH A: Existing Repository]                   [PATH B: Greenfield Project]
    Inspect Workspace Standards                     Interview & Grill Protocol
    - Check .ai-context/ (ADRs & features)          - Proactively question language,
    - README, package.json, pom.xml                   framework, test suite, and goals
    - pyproject.toml, Cargo.toml, go.mod            - Zero assumptions allowed
    - AGENTS.md, CLAUDE.md, .cursorrules            - Establish binary success gates
    - Test configs & linter rules                   - Define strict diff & iteration budget
    - Adapt verifier to native stack
```

#### PATH A: Existing (Brownfield / Legacy) Repository Standards
When working inside an existing codebase, **never assume or impose alien tools**.
1. **Inspect AI Context & Memory First:**
   - Look for `.ai-context/`:
     - Read `.ai-context/decisions/*.md` to absorb past architectural decisions and rejected alternatives.
     - Read `.ai-context/features/*.md` to understand component locations, flows, and known gotchas.
2. **Inspect repository configuration files:**
   - Package & dependency manifests: `package.json`, `pnpm-lock.yaml`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `pom.xml`, `build.gradle`, `composer.json`, `Gemfile`.
   - Workspace instructions: `README.md`, `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `.agent/`, `rules/`.
   - Quality & testing configs: `pytest.ini`, `jest.config.*`, `vitest.config.*`, `Makefile`, `.eslintrc.*`, `ruff.toml`, `tsconfig.json`.
3. **Extract native workflow commands:**
   - Package manager: `pnpm`, `npm`, `yarn`, `bun`, `poetry`, `uv`, `cargo`, `go`.
   - Test runner command: `pnpm test`, `pytest tests/`, `cargo test`, `go test ./...`.
   - Linter / typecheck commands: `tsc --noEmit`, `ruff check`, `npm run lint`.
4. **Calibrate the Loop:**
   - Plug the repository's native test command directly into the verifier gate.
   - Respect repository coding conventions, folder layout, and diff constraints.

#### PATH B: Greenfield (New Project) Interview & Grill Protocol
If no codebase exists, or the workspace is empty, or the user states they are starting a new initiative:
**DO NOT guess or proceed on assumptions.** (Think Before Coding).
Immediately conduct a discovery interview and grill the user on 6 dimensions:
1. **Language & Runtime:** What programming language and runtime/version are we building in?
2. **Framework & Architecture:** What framework or libraries are planned?
3. **Tooling & Package Manager:** What package manager and build system are preferred?
4. **Testing Harness:** What automated test framework will provide the objective verification gate? *(If no test suite exists yet, Step 1 of the loop must be scaffolding the test harness!)*
5. **Objective Definition of Done:** What exact binary criteria or command proves the task is complete?
6. **Iteration Budget:** What is the hard iteration cap (default 3–4)?

---

### Layer Diagnosis: Diagnose Before You Fix

When an agentic system fails or drifts, diagnose the bottleneck layer first:

| Failure Symptom | Bottleneck Layer | The Real Fix |
| :--- | :--- | :--- |
| Agent cannot run tools, loses state, or times out | **Harness Layer** | Fix permissions, repair CLI/API tools, clean noisy context. |
| Agent runs tools but produces broken, unverified code | **Loop Layer** | Introduce binary verifier gate, split Maker from Checker, enforce stop rules. |
| Agent loses track of workflow, skips steps, or deadlocks | **Graph Layer** | Define explicit state schema, node transitions, and human approval checkpoints. |
| Agent resets completely across sessions with zero memory | **Environment Layer**| Establish `.ai-context/` records, workspace contracts, and review boundaries. |

---

### The 4 Eligibility Questions

Not every task deserves a loop. Before putting an agent into an iterative cycle, answer four questions:

1. **Does the task repeat?**
2. **Can the result be verified automatically?** *(Most important!)*
3. **Can the agent act end-to-end?**
4. **Is "done" completely objective?**

If you answer "No" to any of these, **keep the task manual**. Do not build an open loop on subjective judgment.

---

### The 6 Building Blocks of a Loop

Every resilient loop must explicitly define these six blocks:

1. **Automation (Heartbeat):** What triggers a cycle? (CLI command, failing test, webhook).
2. **Context (Hot & Warm State):** The minimal files, repo rules, and `.ai-context/` records the agent reads before acting.
3. **Action Policy (Boundaries):** Strictly what the agent is allowed to touch. No unprompted refactoring. Diffs kept surgical (<50-100 lines).
4. **Verification Gate (The Checker):** Automated command that produces binary proof (exit code 0).
5. **State Persistence & AI Context:** Durable memory outside LLM context (`loop_state.json`, git commits, and `.ai-context/`).
6. **Stop Conditions:**
   - **Success Stop:** Verifier exits 0 with clean diffs.
   - **Failure Stop:** Hard cap at 3 to 4 iterations. Stop and escalate to the human.

---

### The Maker-Checker Split

**Never let the agent that wrote the code be the sole judge of whether the code is correct.**

LLMs share blind spots between generation and self-evaluation. Asking an agent *"Are you sure this works?"* results in hallucinated confidence.

- **Maker Role:** Generates surgical diffs. Adheres to simplicity principles (minimum code, zero speculative features).
- **Checker Role:** Runs detached objective verification. Inspects diff sizes, runs test suites, verifies schemas.

---

## The AI Context Memory System (`.ai-context/`)

Every finished loop that resolves an issue, makes an architectural decision, or modifies a feature MUST promote its context to the durable `.ai-context/` directory.

### 1. Architecture Decision Records (ADRs)
- **Location:** `.ai-context/decisions/`
- **Naming Formula:** `NNN-<kebab-slug>.md` (e.g. `001-payment-auth.md`, `015-webhook-retry.md`)
- **Template & Guide:** See [decisions_readme.template.md](assets/ai_context/decisions_readme.template.md) for full schema (Context, Decision, Alternatives Rejected, Affected Files).

### 2. Feature Context Notes
- **Location:** `.ai-context/features/`
- **Naming Formula:** `<feature-slug>.md` (e.g. `auth.md`, `billing.md`, `checkout.md`)
- **Rule:** When modifying an existing feature, **update the existing file** rather than creating duplicates.
- **Template & Guide:** See [features_readme.template.md](assets/ai_context/features_readme.template.md) for full schema (Where it lives, Key flows, Conventions/gotchas, Related decisions).

---

## Operational Modes

### Mode 1: Scaffold a Loop Contract (`scaffold`)

Use when setting up a new loop harness for a project or repository.

Run the bundled CLI tool:
```bash
python3 scripts/scaffold_loop.py --type [code-tdd|refactor|research-doc|general] --goal "Specific goal" --verifier "test command" --output .
```

The tool auto-detects existing repository standards (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, etc.) and sets the verifier command to match the native test runner. It also safely skips existing files unless `--force` is passed.

This generates:
- `LOOP.md`: Complete loop contract with boundaries, gates, and AI context promotion steps.
- `scripts/verify_gate.py`: Objective Python test harness that exits 0 on success.
- `scripts/run_loop.sh`: Bounded execution runner supporting both interactive step pauses and automated commands.
- `.ai-context/`: Architecture Decision Records (`decisions/`) and Feature Context Notes (`features/`).

---

### Mode 2: Run an In-Session Development Loop (`run`)

Use when you (the AI assistant) are asked to execute a task iteratively right now.

Follow the **Plan → Do → Verify → Decide → Promote Context** protocol:

```
1. PLAN   ──> State single next surgical action and test hypothesis.
2. DO     ──> Apply minimal code change. Keep diffs under 50-100 lines.
3. VERIFY ──> Execute the objective verifier command in shell.
4. DECIDE ──> If verifier exits 0: Proceed to step 5.
              If verifier fails: Extract exact error, feed to next turn.
              If iteration == Max (default 4): STOP. Escalate to human.
5. PROMOTE AI CONTEXT (.ai-context/):
          ──> If architectural choice made: write .ai-context/decisions/NNN-<slug>.md
          ──> If feature logic touched: update .ai-context/features/<feature-slug>.md
          ──> Summarize verified diff and context updates, then mark COMPLETE.
```

**Active Coding Rules during the loop:**
- **Think Before Coding:** State assumptions explicitly. Read `.ai-context/` before editing.
- **Simplicity First:** Write the minimum code to satisfy the verifier. No speculative abstractions.
- **Surgical Changes:** Touch only files relevant to the goal. Do not touch adjacent code or formatting.
- **Zero Comprehension Debt:** Always record decisions and gotchas in `.ai-context/`.

---

### Mode 3: Audit an Existing Agent Loop (`audit`)

Use when a user shares logs, transcripts, or complains that their agent gets stuck in a loop.

1. **Check the Stop Rule:** Is the loop checking confidence (*"looks good"*) or evidence (*"tests pass"* exit code 0)?
2. **Check the Maker-Checker Boundary:** Is the same prompt generating and evaluating?
3. **Check Context Promotion:** Does the loop leave behind an audit trail in `.ai-context/` or does it suffer from amnesia?
4. **Check the Diff Budget:** Is the agent adding unasked features or refactoring adjacent code?
5. **Check the Iteration Cap:** Is there an ironclad circuit breaker at 3–4 iterations?
6. **Classify the Failure:** Output the Layer Diagnosis (Harness vs Loop vs Graph vs Environment) and the exact remediation.

---

## Production Checklist & Next Move

Before letting any loop run unattended, verify:

- [ ] Has the environment been checked (brownfield standards detected OR greenfield interview completed)?
- [ ] Were existing `.ai-context/` notes and ADRs reviewed before starting?
- [ ] Does the task pass all 4 Eligibility Questions?
- [ ] Is the primary verifier an objective script exiting with code 0?
- [ ] Is there a hard stop condition capped at $\le 4$ iterations?
- [ ] Is the action surface constrained to specific target files?
- [ ] Are surgical diff constraints active to avoid comprehension debt?
- [ ] Is there a post-completion hook to update `.ai-context/decisions/` and `.ai-context/features/`?

> [!WARNING]
> **Adjacent System Risk:**
> A fast autonomous loop operating without durable memory will repeatedly re-invent decisions and re-introduce past gotchas. Always promote verified learnings to `.ai-context/`.

---

## Bundled Resources

- [architecture.md](references/architecture.md) — Comprehensive 4-layer taxonomy, evidence gates, and `.ai-context/` durable memory architecture.
- [failure-modes.md](references/failure-modes.md) — Anti-patterns including amnesiac completion and tooling mismatch.
- [scaffold_loop.py](scripts/scaffold_loop.py) — Zero-dependency scaffolding utility with `.ai-context/` generation.
- [LOOP_CONTRACT.template.md](assets/LOOP_CONTRACT.template.md) — Standalone production contract template with context promotion.
- [ai_context templates](assets/ai_context/) — Templates for ADRs and Feature Context Notes.
