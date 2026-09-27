# Agent Guidelines & Project Operating Manual

This repository uses **Loop Engineering** for autonomous, iterative development with objective verification gates, surgical diffs, and durable context memory.

---

## 🔁 Loop Engineering Protocol (`/loop-engineering`)

Whenever an AI assistant is asked to implement a feature, resolve a bug, refactor code, or run `/loop-engineering`:

### 1. Pre-Flight Context Inspection
Before modifying any files:
- Inspect `LOOP.md` for active boundaries, target files, and primary verification gates.
- Read `.ai-context/decisions/` to absorb past architectural decisions and avoid repeating rejected approaches.
- Read `.ai-context/features/` to review component layouts, entry points, and domain gotchas.

### 2. Execution Cycle: Plan → Do → Verify → Decide → Promote Context
Follow this disciplined five-step protocol:
1. **PLAN:** Explicitly state the single next surgical action and the hypothesis being tested.
2. **DO (Maker):** Apply minimal code changes (<50–100 lines). Adhere to simplicity: no unprompted refactoring, no speculative abstractions.
3. **VERIFY (Checker):** Run the objective verification gate in shell:
   ```bash
   {verifier_cmd}
   ```
   **Core Axiom: Do not loop on confidence. Loop on evidence.** Never self-declare success. Only proceed when the verification command exits cleanly with code 0.
   *(Tip: In large repos, run targeted tests like `pytest tests/unit/test_foo.py` during inner iterations to avoid slow runs, and run full suite before completion).*
4. **DECIDE:**
   - If verifier passes: Proceed to Step 5.
   - If verifier fails: Feed the exact error into context, increment iteration count, and retry (strictly bounded to {max_iterations} iterations).
5. **PROMOTE AI CONTEXT (.ai-context/):**
   - **ADRs (Decisions):** Record in `.ai-context/decisions/NNN-<kebab-slug>.md` **only** if an architectural or structural choice was made (avoid ADR fatigue for trivial bugfixes).
   - **Feature Notes:** If feature logic or flows were touched: update `.ai-context/features/<feature-slug>.md`.
   - Summarize verified diffs and context updates, then mark complete.

---

## 🧠 Durable AI Context Memory (`.ai-context/`)

- **Architecture Decision Records (ADRs):** `.ai-context/decisions/NNN-<kebab-slug>.md`
  - Purpose: Record non-trivial architecture decisions and rejected alternatives.
  - Format: Context, Decision, Alternatives Rejected, Affected Files.
- **Feature Context Notes:** `.ai-context/features/<feature-slug>.md`
  - Purpose: Living documentation of system components, entry points, and domain gotchas.
  - Format: Where it lives, Key flows, Conventions/gotchas, Related decisions.
  - *Rule: Update existing feature notes rather than creating duplicates.*

---

## 🛡️ Coding Discipline & Safety Gates

1. **Think Before Coding:** State assumptions explicitly. If requirements are ambiguous, clarify before executing.
2. **Simplicity First:** Write the minimum code necessary to satisfy the verifier gate.
3. **Surgical Diffs:** Touch only files relevant to the active goal. Do not modify adjacent formatting or comments.
4. **Hard Iteration Ceilings:** Never exceed {max_iterations} iterations. If tests fail repeatedly, halt and escalate to human review.
5. **Targeted Verification:** Scope verification commands to affected test suites to prevent token waste and slow loops.
6. **Repository Standards:** Respect detected project conventions: `{detected_standards}`.
