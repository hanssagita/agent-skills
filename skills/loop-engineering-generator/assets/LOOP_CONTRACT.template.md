# LOOP CONTRACT: {title}

> **Core Axiom:** Do not loop on confidence. Loop on evidence.
> **Comprehension Debt Warning:** Keep diffs surgical. If the loop cannot verify progress automatically, stop and ask the human.

---

## 1. Loop Profile

| Dimension | Specification |
| :--- | :--- |
| **Archetype** | `{archetype}` |
| **Goal** | {goal} |
| **Trigger** | {trigger} |
| **Max Iterations** | {max_iterations} (hard stop) |
| **Detected Standards** | {detected_standards} |
| **AI Context Memory** | `.ai-context/` (ADRs & Feature Notes) |
| **Estimated Cost Gate** | Stop if tokens exceed allocated budget or 3 consecutive iterations fail same gate |

---

## 2. The 6 Building Blocks

### 1. Automation (Heartbeat)
- Initiated by: `{trigger}`
- Cadence: Discrete step execution.
- LLM / IDE: Agnostic (Compatible with Claude Code, Cursor, Antigravity, OpenCode, Windsurf, Cline, CLI).

### 2. Context (Hot & Warm State)
- Read contract: `LOOP.md`
- Durable AI Context: Inspect `.ai-context/decisions/` and `.ai-context/features/` for past gotchas and decisions.
- Repository standards: Follow rules in `README.md`, `package.json`, `pyproject.toml`, `AGENTS.md` (if present).
- Target files: Inspect specific workspace files before making changes.
- Ground rules: Think before coding, surgical edits, simplicity first.

### 3. Action Policy (Boundaries)
- {action_policy}
- Forbidden: Unprompted refactoring, editing lock files without reason, ignoring test failures.

### 4. Verification Gate (Checker)
- **Primary Verifier:** `{verifier}`
- Verification command:
  ```bash
  {verifier_cmd}
  ```
- Pass condition: Clean exit code (0), zero regressions, zero unverified assumptions.

### 5. State Persistence & AI Context
- Progress tracked in `loop_state.json` or git commit history.
- Schema: `[iteration_number, changes_made, verifier_output, outcome]`
- On completion: Learned context promoted to `.ai-context/`.

### 6. Stop Conditions
- **SUCCESS STOP:** Primary verifier passes with zero warnings.
- **FAILURE STOP:** `{max_iterations}` iterations reached without passing verifier.
- **ESCALATION STOP:** Unrecoverable environment/harness error or contradictory requirements detected.

---

## 3. Maker-Checker Execution Protocol

1. **PLAN:** Explicitly state the single next step and what hypothesis it tests.
2. **DO:** Maker applies surgical modification adhering to detected repository standards.
3. **VERIFY:** Checker executes the objective verification command:
   ```bash
   {verifier_cmd}
   ```
4. **DECIDE:**
   - If verifier succeeds: Proceed to step 5.
   - If verifier fails: Feed error back into context, increment iteration count, repeat until `{max_iterations}`.
5. **PROMOTE CONTEXT (.ai-context/):**
   - **Architectural Decision (ADR):** If an architectural or design choice was made, record it in `.ai-context/decisions/NNN-<kebab-slug>.md`.
   - **Feature Context Notes:** If feature code/structure was created or modified, update `.ai-context/features/<feature-slug>.md` with components, key flows, and gotchas.
   - Mark task COMPLETE and summarize verified diff + updated context files.

---

## 4. Production Checklist (Before Launching Loop)

- [ ] Has the repository stack been detected or grilled (language, test runner, package manager)?
- [ ] Were existing `.ai-context/` notes and ADRs reviewed before starting?
- [ ] Is "done" completely objective? (No subjective "looks good")
- [ ] Can the agent run the verifier autonomously without human typing?
- [ ] Is the failure stop condition strictly bounded (<= {max_iterations} iterations)?
- [ ] Is the action surface restricted to only the necessary files?
