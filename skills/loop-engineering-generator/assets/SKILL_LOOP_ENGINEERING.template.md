---
name: loop-engineering
description: Executes autonomous closed-loop workflows with objective evidence gates, maker-checker split, bounded iteration budgets, zero comprehension debt, and durable AI context memory (.ai-context/ ADRs & feature notes). Use whenever the user asks to run an autonomous loop, implement a feature iteratively, fix failing tests, run /loop-engineering, or work in a loop until tests or verification criteria pass.
license: MIT
compatibility: Universal. Compatible with all AI coding agents (Antigravity, Claude Code, Cursor, Windsurf, OpenCode, Cline, Aider, GitHub Copilot).
metadata:
  version: 1.0.0
  author: hanssoegiarto
  tags:
    - loop-engineering
    - autonomous-agents
    - feedback-loops
    - verifier-gates
    - tdd
    - ai-context
    - adr
---

# Loop Engineering Protocol

You are executing an autonomous closed-loop engineering task governed by this repository's `LOOP.md` and `AGENTS.md`.

## Core Stance
- **Never loop on confidence. Loop on evidence.** Never self-declare success. Success is determined solely by objective exit code 0 from the verification gate.
- **Surgical diffs.** Keep changes minimal (<50 lines per iteration). Do not refactor unrelated code.
- **Maker-Checker split.** The maker produces minimal changes; the checker runs verification commands and inspects diffs.
- **Durable AI context memory.** Promote discoveries and decisions into `.ai-context/`.

---

## The 5-Step Execution Cycle

Whenever triggered (via `/loop-engineering`, bugfix request, or iterative task), follow this cycle:

```
1. PLAN   ──> State single next surgical action and test hypothesis.
2. DO     ──> Apply minimal code change. Keep diffs under 50 changed lines.
3. VERIFY ──> Execute the objective verifier command in shell:
              {verifier_cmd}
4. DECIDE ──> If verifier exits 0: Proceed to step 5.
              If verifier fails: Feed error into context, refine hypothesis, retry.
              If iteration reaches {max_iterations}: STOP. Escalate to human review.
5. PROMOTE AI CONTEXT (.ai-context/):
          ──> If architectural choice made: write .ai-context/decisions/NNN-<slug>.md
          ──> If feature logic touched: update .ai-context/features/<feature-slug>.md
          ──> Summarize verified diff and context updates, then mark COMPLETE.
```

---

## Operational Instructions

### Step 1: Pre-Flight Check
Before editing any code:
1. Inspect `LOOP.md` for target files, boundaries, and active verification command.
2. Read `.ai-context/decisions/` to absorb past architectural decisions and avoid repeating rejected approaches.
3. Read `.ai-context/features/` to review component layouts, entry points, and domain gotchas.
4. Run the baseline verification command to observe current test status:
   ```bash
   {verifier_cmd}
   ```

### Step 2: Surgical Iteration (Strict Cap: {max_iterations} Iterations)
For each iteration:
- **Plan:** Announce the hypothesis (e.g. *"Fixing parameter validation in `service.py` to handle None values"*).
- **Do:** Apply the minimal surgical change.
- **Verify:** Run the verification gate:
   ```bash
   python3 scripts/verify_gate.py
   # or run the native verifier directly:
   {verifier_cmd}
   ```
- **Decide:**
  - If exit code is 0: Success. Move to Step 3.
  - If exit code is non-zero: Inspect the failure, check diff lines with `git diff --stat`, and retry.
  - If iteration reaches `{max_iterations}` without passing: **Halt.** Do not keep burning tokens or looping blindly. Escalate to the user with the exact failure log and current diff.

### Step 3: Promote AI Context (`.ai-context/`)
Once verification passes:
1. **Architecture Decision Records:** If a structural or architectural decision was made, document it in `.ai-context/decisions/NNN-<slug>.md` using the ADR schema.
2. **Feature Context Notes:** If feature logic or flows were changed, update or create `.ai-context/features/<slug>.md`.
3. Report a clear summary of verified changes, test results, and promoted context notes.
