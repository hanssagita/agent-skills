# Loop Engineering Anti-Patterns & Failure Modes

> "A loop without a stop rule is not automation. It is an uncontrolled token leak."

---

## 1. Top 7 Loop Failure Modes

### 1. Looping on Confidence (The "Looks Good" Trap)
- **The Pattern:** The prompt instructs the agent: *"Keep improving until you are confident the code is bug-free."*
- **The Failure:** The model rewrites code 5 times, introduces subtle regressions, and concludes on turn 6: *"The implementation is now fully robust and verified."* No tests were executed.
- **The Fix:** Delete all requests for self-assessed confidence. Replace with binary, deterministic gates: `pytest tests/test_auth.py == 0` or `npm test`.

### 2. Silent Assumptions & Tooling Mismatch (Ignoring Environment Standards)
- **The Pattern:** An agent starts a loop by running arbitrary tools (e.g. `npm test` when the repo uses `pnpm`, or creating new frameworks without checking `package.json` or `pyproject.toml`). Or in a new project, it makes silent assumptions instead of asking.
- **The Failure:** The loop fails on environment setup, introduces incompatible package managers, or generates code in the wrong style.
- **The Fix:** Run the **Environment Discovery Gate**:
  - In existing codebases: inspect `README.md`, `package.json`, `Cargo.toml`, `pyproject.toml`, and `AGENTS.md`. Adapt the verifier to native commands.
  - In new projects: interview and grill the human first on language, framework, and test suite.

### 3. Open Loops & Token Leakage
- **The Pattern:** An unbounded loop runs without hard iteration caps, retrying on vague feedback like *"still failing, try again"*.
- **The Failure:** The agent exhausts context limits, repeats previous failed ideas, burns through token budgets, and generates hallucinated dependencies.
- **The Fix:** Enforce a hard cap of **3 to 4 iterations**. If the gate does not pass within the budget, stop, log exact failure telemetry, and escalate to the human.

### 4. Maker-as-Checker (Self-Grading Blind Spot)
- **The Pattern:** The same agent prompt that writes a function is immediately asked to judge whether the function meets requirements.
- **The Failure:** The model rationalizes edge-case omissions, skips edge checks, and confirms its own flawed assumptions.
- **The Fix:** Separate the Maker and Checker. Maker generates changes; an independent verifier script (or an independent checker agent with read-only access) runs tests and audits diffs.

### 5. Comprehension Debt & Speculative Over-Engineering
- **The Pattern:** The agent attempts to fix a 5-line bug by refactoring the module, adding generic helper classes, abstracting interfaces, and reformatting comments.
- **The Failure:** The human reviewer cannot comprehend what changed or verify safety. Review debt explodes.
- **The Fix:** Enforce Surgical Changes. Ban touching adjacent functions. Reject diffs that exceed the line-change budget.

### 6. Blaming the Model for Harness Failures
- **The Pattern:** An agent fails to complete a task because a shell command timed out, an environment variable was missing, or tool output was truncated. The developer swaps models or lengthens the prompt.
- **The Failure:** The issue was in the harness, not model intelligence. Prompting cannot fix a broken execution environment.
- **The Fix:** Run a Layer Diagnosis. If the agent cannot inspect files or run commands cleanly, fix the harness before touching the loop.

### 7. The "Infinite Exploration" Graph Anti-Pattern
- **The Pattern:** An agent is placed in an open loop with instructions to *"explore the codebase, find bugs, and fix them"*.
- **The Failure:** The agent wanders aimlessly, makes unnecessary modifications to stable code, breaks subtle invariants, and creates merge conflicts.
- **The Fix:** Only loop on tasks that pass the **4 Eligibility Questions**:
  1. Does the task repeat?
  2. Can the result be verified automatically?
  3. Can the agent act end-to-end?
  4. Is "done" completely objective?

### 8. Amnesiac Task Completion (No Context Promotion)
- **The Pattern:** The agent successfully finishes a loop, tests pass, and it outputs a brief message. When the user or a future agent opens a new session tomorrow, nobody knows why a library was chosen, what gotchas were discovered, or how the new feature hooks together.
- **The Failure:** Repeated wheel-reinvention, regression of subtle edge cases, and human comprehension debt.
- **The Fix:** Enforce Step 5 in every loop: promote learnings into `.ai-context/decisions/NNN-<kebab-slug>.md` and `.ai-context/features/<feature-slug>.md`.

---

## 2. Prevention Matrix

| Anti-Pattern | Root Cause | Preventive Guardrail |
| :--- | :--- | :--- |
| **Confidence Loop** | Vague stop rule | Binary automated verifier script (`exit code 0`) |
| **Tooling Mismatch** | Unchecked assumptions | Environment Discovery Gate (Brownfield audit / Greenfield grill) |
| **Runaway Iterations** | Missing termination bounds | Hard iteration cap ($N \le 4$) & token budget gate |
| **Self-Review Blindness** | Single agent role | Maker-Checker split with read-only verifier |
| **Comprehension Debt** | Speculative code bloat | Diff budget & zero-unprompted-refactoring rule |
| **Context Starvation** | Poor harness design | Context injection of specific targeted files only |
| **Aimless Wandering** | Open loop structure | Closed loop contract (`LOOP.md`) with explicit boundaries |
| **Amnesiac Loops** | Volatile session state | Post-completion `.ai-context/` promotion (ADRs & feature notes) |
