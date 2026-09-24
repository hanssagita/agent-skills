# LOOP CONTRACT: [Task or Workflow Title]

> **Core Axiom:** Do not loop on confidence. Loop on evidence.
> **Comprehension Debt Warning:** Keep changes minimal and surgical. Every line must trace to the explicit goal.

---

## 1. Loop Metadata

| Attribute | Specification |
| :--- | :--- |
| **Goal** | [Precise, objective goal statement] |
| **Archetype** | `[code-tdd | refactor | research-doc | general]` |
| **Max Iterations** | `[3 to 4]` (Hard ceiling) |
| **Repo Standards** | `[Auto-detected from package.json/Cargo/etc. OR declared in greenfield interview]` |
| **Target Files** | `[List of files allowed to be modified]` |
| **Forbidden Actions** | [No unprompted refactoring, no editing config/lock files, no speculative features] |

---

## 2. The 6 Building Blocks

### 1. Automation (Trigger)
- **Initiated by:** `[e.g., /loop-engineering run, git pre-commit, failing CI test]`
- **Execution Mode:** Bounded discrete step loop.

### 2. Context (Hot & Warm State)
- **Required reading before iteration:**
  - `[Relevant test files, target source files, error logs]`
  - Karpathy principles: Think before coding, surgical edits, simplicity first.

### 3. Action Policy (Boundaries)
- Allowed actions: Edit only `[target file list]`.
- Diff budget: Under `[e.g., 50]` lines changed per iteration.
- Revert on regression: If an iteration breaks unrelated tests, revert immediately.

### 4. Verification Gate (The Checker)
- **Primary Command:**
  ```bash
  [Command that exits 0 on success, non-zero on failure. e.g. pytest tests/test_feature.py]
  ```
- **Secondary Checks:**
  - Linter / type check clean.
  - Diff check: `git diff --stat` confirms no out-of-scope files touched.

### 5. State Persistence
- Track progress in `loop_state.json` or git commit history.
- Log schema: `{"iteration": N, "action": "...", "gate_result": "PASS/FAIL", "notes": "..."}`

### 6. Stop Conditions
- **SUCCESS STOP:** Primary verifier passes with code 0 + secondary checks clean.
- **FAILURE STOP:** `[N]` iterations reached without passing verifier -> Escalate to human operator.
- **CIRCUIT BREAKER:** Stop immediately if the same error repeats twice consecutively.

---

## 3. Protocol (Plan → Do → Verify → Decide)

1. **PLAN:** State the single next surgical action and the expected impact on the verifier gate.
2. **DO:** Maker applies the edit. Touch only what is strictly necessary.
3. **VERIFY:** Checker runs the objective verification command.
4. **DECIDE:**
   - If verifier passes: Proceed to Step 5.
   - If verifier fails: Feed exact error back to next iteration. Increment counter. If counter >= Max Iterations, STOP.
5. **PROMOTE CONTEXT (.ai-context/):**
   - If architectural choice was made: write `.ai-context/decisions/NNN-<kebab-slug>.md`
   - If feature code/gotchas discovered: update `.ai-context/features/<feature-slug>.md`
   - Mark task COMPLETE and report verified diff + context documentation.
