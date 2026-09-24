#!/usr/bin/env python3
"""
scaffold_loop.py — Universal Loop Engineering Contract & Scaffolding Generator

Principles:
  - Do not loop on confidence. Loop on evidence.
  - Surface assumptions. Minimal code. Surgical edits.
  - Maker-Checker split: maker builds, checker validates against objective gates.
  - Respect existing repository standards (package.json, pyproject.toml, Cargo.toml, etc.).
  - Durable AI context memory promotion (.ai-context/ decisions and feature notes).
  - LLM-agnostic & IDE-agnostic.
"""

import argparse
import json
import os
import sys
from pathlib import Path

TEMPLATES = {
    "code-tdd": {
        "title": "TDD Implementation & Bugfix Loop",
        "description": "Closed-loop code development with automated test verification and diff bounding.",
        "trigger": "Failing test, bug report, or new feature specification.",
        "goal": "Make target test suite pass with zero regressions and no superfluous code changes.",
        "action_policy": "Edit only source code and test files directly related to the issue. Max 50 lines changed per iteration. No refactoring unrelated code.",
        "verifier": "Native test suite exit code == 0 && git diff line count within budget.",
        "max_iterations": 4,
        "maker_checker": "Maker edits code and runs targeted tests. Checker independently runs full test suite and diff check.",
    },
    "refactor": {
        "title": "Surgical Code Simplification Loop",
        "description": "Simplify code complexity while keeping all existing behavior and tests strictly passing.",
        "trigger": "Complex file, cyclomatic complexity warning, or abstraction cleanup request.",
        "goal": "Reduce cyclomatic complexity / lines of code while 100% of existing regression tests pass.",
        "action_policy": "Surgically touch target functions only. Do not alter external APIs or behavior.",
        "verifier": "Existing test suite passes 100% && complexity score decreases.",
        "max_iterations": 3,
        "maker_checker": "Maker performs atomic refactorings. Checker runs regression test suite and checks for API drift.",
    },
    "research-doc": {
        "title": "Evidence-Grounded Research & Synthesis Loop",
        "description": "Iterative document or PRD generation grounded in cited primary sources and verifiable rubrics.",
        "trigger": "Research brief, technical RFC requirement, or quantitative evaluation request.",
        "goal": "Generate document satisfying rubric score >= 8/10 on clarity, factual citations, and technical feasibility.",
        "action_policy": "Synthesize verified claims only. Every non-trivial assertion must cite an existing source or benchmark.",
        "verifier": "Citation resolver passes (100% links/sources valid) && rubric checker gives >= 8/10 across all categories.",
        "max_iterations": 3,
        "maker_checker": "Maker synthesizes content. Checker validates citation integrity and scores rubric independently.",
    },
    "general": {
        "title": "Closed Autonomous Engineering Loop",
        "description": "General purpose closed-loop workflow with bounded iterations and verifiable success criteria.",
        "trigger": "Specific task requiring iterative refinement.",
        "goal": "Achieve objective success criteria with verifiable evidence.",
        "action_policy": "Make minimal necessary modifications. Log progress after each iteration.",
        "verifier": "Objective verification script or schema check exits with 0.",
        "max_iterations": 3,
        "maker_checker": "Maker implements solution. Checker runs verification gates.",
    }
}

LOOP_MD_TEMPLATE = """# LOOP CONTRACT: {title}

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

```
           ┌─────────────────────────────────────────┐
           │        1. PLAN (State Next Step)         │
           └────────────────────┬────────────────────┘
                                │
                   ┌────────────┴────────────┐
                   │    2. DO (Maker Phase)   │
                   │ (Minimal Surgical Edit) │
                   └────────────┬────────────┘
                                │
                   ┌────────────┴────────────┐
                   │  3. VERIFY (Checker)    │
                   │ (Run Objective Gate)    │
                   └────────────┬────────────┘
                                │
                   ┌────────────┴────────────┐
                   │   4. DECIDE (Stop/Iter) │
                   │ Passed? -> Step 5       │
                   │ Failed? -> Log & Loop   │
                   └────────────┬────────────┘
                                │
                   ┌────────────┴────────────┐
                   │ 5. PROMOTE CONTEXT      │
                   │ (.ai-context/ ADR & Doc)│
                   └─────────────────────────┘
```

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
"""

VERIFIER_SCRIPT_TEMPLATE = """#!/usr/bin/env python3
\"\"\"
Objective Verification Gate for Loop
Exits 0 on success, non-zero on failure.
\"\"\"

import subprocess
import sys

def run_check(cmd, description):
    print(f"[*] Checking: {{description}}...")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[FAIL] {{description}} failed!")
        print(res.stdout)
        print(res.stderr)
        return False
    print(f"[PASS] {{description}} passed.")
    return True

def main():
    # Verification checks tailored to project standards:
    checks = [
        ("{verifier_cmd}", "Primary Verification Gate"),
    ]

    for cmd, desc in checks:
        if not run_check(cmd, desc):
            sys.exit(1)

    print("\\n[SUCCESS] All verification gates passed. Loop stop condition met.")
    sys.exit(0)

if __name__ == "__main__":
    main()
"""

RUNNER_SCRIPT_TEMPLATE = """#!/usr/bin/env bash
set -euo pipefail

# Closed Loop Execution Harness
MAX_ITER={max_iterations}
ITER=1

echo "=================================================="
echo " Starting Closed Loop: {title}"
echo " Max Iterations: $MAX_ITER"
echo "=================================================="

while [ "$ITER" -le "$MAX_ITER" ]; do
    echo ""
    echo ">>> Iteration $ITER of $MAX_ITER..."

    # Check if verifier passes
    if {verifier_cmd}; then
        echo ""
        echo "[SUCCESS] Verifier passed on iteration $ITER! Exiting loop."
        exit 0
    fi

    echo "[INFO] Verifier failed on iteration $ITER."
    if [ "$ITER" -eq "$MAX_ITER" ]; then
        echo "[STOP] Reached maximum iterations ($MAX_ITER) without passing verifier."
        echo "[ACTION] Escalate to human operator. Do not continue blind looping."
        exit 1
    fi

    ITER=$((ITER + 1))
done
"""

AI_CONTEXT_ROOT_README = """# AI Context & Durable Memory

This directory stores durable architecture knowledge and feature context across development loops and agent sessions. It ensures that neither human engineers nor future AI agents suffer from amnesia.

## Directory Layout
- `decisions/`: Architecture Decision Records (ADRs) named `NNN-<kebab-slug>.md`.
- `features/`: Feature context, key flows, and gotchas named `<feature-slug>.md`.

## Lifecycle in Loops
1. **Loop Start:** Read relevant files in `decisions/` and `features/` to absorb existing rules and past architectural decisions before taking action.
2. **Loop Finish:** Promote new architectural decisions to `decisions/` and update or create feature notes in `features/`.
"""

AI_CONTEXT_DECISIONS_README = """# Architecture Decision Records (ADRs)

This directory contains lightweight records of architectural decisions made during development loops.

## Naming Formula
`NNN-<kebab-slug>.md`
- `NNN`: 3-digit zero-padded incremental number (e.g. `001-state-management.md`, `015-payment-webhook.md`).
- `<kebab-slug>`: concise description of the decision.

## Format & Template

```markdown
# ADR NNN: <short title>
- Date: YYYY-MM-DD
- Status: Accepted | Superseded | Rejected
- RFC: docs/rfcs/<slug>.md   (or Lark/Wiki URL if applicable)
- JIRA: CAS-xxxx, CAS-xxxx (if applicable)

## Context
<1–3 sentences: the problem / PRD driver / technical constraint>

## Decision
<chosen approach, 1–3 sentences>

## Alternatives rejected
- <approach> — <why not>

## Affected files / modules
- <path or module> — <what changes>
```
"""

AI_CONTEXT_FEATURES_README = """# Feature Context Notes

This directory maintains persistent domain knowledge, layout, conventions, and gotchas for features across the codebase.

## Naming Formula
`<feature-slug>.md`
- Matches the feature domain or directory name (e.g. `auth.md`, `cash-loan.md`, `checkout.md`).
- **Rule:** When modifying an existing feature, **update the existing file** rather than duplicating.

## Format & Template

```markdown
# Feature: <name>
<!-- Last updated: YYYY-MM-DD -->

## Where it lives
- Components: <path to UI components>
- Hooks / models: <path to hooks/stores/models>
- Routes: <page or endpoint routes>
- Tests: <path to test suites>

## Key flows
- <flow name> — <entry point> → <outcome>

## Conventions / gotchas
- <thing future agents/developers must know: project gating, SWR keys, translation namespace, retry rules, auth checks, etc.>

## Related decisions
- [[NNN-<slug>]] — <one line summary linking to decision ADR>
```
"""

def detect_repository_standards(target_dir: Path) -> dict:
    """Inspects workspace to detect language, package manager, test runner, and AI context."""
    standards = {
        "stack": "unknown",
        "default_test_cmd": "python3 scripts/verify_gate.py",
        "configs_found": []
    }

    # Check for existing .ai-context
    ai_ctx = target_dir / ".ai-context"
    if ai_ctx.exists():
        standards["configs_found"].append(".ai-context/")
        adrs = list((ai_ctx / "decisions").glob("*.md")) if (ai_ctx / "decisions").exists() else []
        feats = list((ai_ctx / "features").glob("*.md")) if (ai_ctx / "features").exists() else []
        adrs_clean = [f.name for f in adrs if f.name != "README.md"]
        feats_clean = [f.name for f in feats if f.name != "README.md"]
        if adrs_clean or feats_clean:
            standards["configs_found"].append(f"AI-Context({len(adrs_clean)} ADRs, {len(feats_clean)} Features)")

    # JavaScript / TypeScript
    pkg_json = target_dir / "package.json"
    if pkg_json.exists():
        standards["configs_found"].append("package.json")
        try:
            with open(pkg_json, "r", encoding="utf-8") as f:
                data = json.load(f)
            scripts = data.get("scripts", {})
            if "test" in scripts:
                if (target_dir / "pnpm-lock.yaml").exists():
                    standards["stack"] = "TypeScript/Node (pnpm)"
                    standards["default_test_cmd"] = "pnpm test"
                elif (target_dir / "yarn.lock").exists():
                    standards["stack"] = "TypeScript/Node (yarn)"
                    standards["default_test_cmd"] = "yarn test"
                else:
                    standards["stack"] = "JavaScript/Node (npm)"
                    standards["default_test_cmd"] = "npm test"
        except Exception:
            pass

    # Python
    pyproject = target_dir / "pyproject.toml"
    pytest_ini = target_dir / "pytest.ini"
    reqs = target_dir / "requirements.txt"
    if pyproject.exists() or pytest_ini.exists() or reqs.exists():
        standards["stack"] = "Python"
        standards["default_test_cmd"] = "pytest"
        if pyproject.exists():
            standards["configs_found"].append("pyproject.toml")
        if pytest_ini.exists():
            standards["configs_found"].append("pytest.ini")

    # Rust
    cargo = target_dir / "Cargo.toml"
    if cargo.exists():
        standards["stack"] = "Rust (cargo)"
        standards["default_test_cmd"] = "cargo test"
        standards["configs_found"].append("Cargo.toml")

    # Go
    gomod = target_dir / "go.mod"
    if gomod.exists():
        standards["stack"] = "Go"
        standards["default_test_cmd"] = "go test ./..."
        standards["configs_found"].append("go.mod")

    # Java / Maven / Gradle
    if (target_dir / "pom.xml").exists():
        standards["stack"] = "Java (Maven)"
        standards["default_test_cmd"] = "mvn test"
        standards["configs_found"].append("pom.xml")
    elif (target_dir / "build.gradle").exists() or (target_dir / "build.gradle.kts").exists():
        standards["stack"] = "Java/Kotlin (Gradle)"
        standards["default_test_cmd"] = "./gradlew test"
        standards["configs_found"].append("build.gradle")

    # Agent / Project Guides
    for guide in ["README.md", "AGENTS.md", "CLAUDE.md", ".cursorrules"]:
        if (target_dir / guide).exists():
            standards["configs_found"].append(guide)

    return standards

def scaffold_ai_context(target_dir: Path):
    """Scaffolds .ai-context structure with guides and templates."""
    ai_ctx_dir = target_dir / ".ai-context"
    decisions_dir = ai_ctx_dir / "decisions"
    features_dir = ai_ctx_dir / "features"

    decisions_dir.mkdir(parents=True, exist_ok=True)
    features_dir.mkdir(parents=True, exist_ok=True)

    root_readme = ai_ctx_dir / "README.md"
    if not root_readme.exists():
        root_readme.write_text(AI_CONTEXT_ROOT_README, encoding="utf-8")
        print(f"  + Created {root_readme}")

    decisions_readme = decisions_dir / "README.md"
    if not decisions_readme.exists():
        decisions_readme.write_text(AI_CONTEXT_DECISIONS_README, encoding="utf-8")
        print(f"  + Created {decisions_readme}")

    features_readme = features_dir / "README.md"
    if not features_readme.exists():
        features_readme.write_text(AI_CONTEXT_FEATURES_README, encoding="utf-8")
        print(f"  + Created {features_readme}")

def scaffold(output_dir: Path, archetype: str, goal: str = None, verifier_cmd: str = None, with_ai_context: bool = True):
    output_dir.mkdir(parents=True, exist_ok=True)
    spec = TEMPLATES.get(archetype, TEMPLATES["general"])

    # Detect existing repo standards
    detected = detect_repository_standards(output_dir)
    if not detected["configs_found"] and output_dir.resolve() != Path.cwd().resolve():
        detected = detect_repository_standards(Path.cwd())

    actual_goal = goal if goal else spec["goal"]
    
    if verifier_cmd:
        actual_verifier_cmd = verifier_cmd
    elif detected["stack"] != "unknown":
        actual_verifier_cmd = detected["default_test_cmd"]
    else:
        actual_verifier_cmd = "python3 scripts/verify_gate.py"

    detected_summary = f"{detected['stack']} (found: {', '.join(detected['configs_found']) if detected['configs_found'] else 'none'})"

    loop_md = LOOP_MD_TEMPLATE.format(
        archetype=archetype,
        title=spec["title"],
        goal=actual_goal,
        trigger=spec["trigger"],
        max_iterations=spec["max_iterations"],
        action_policy=spec["action_policy"],
        verifier=spec["verifier"],
        verifier_cmd=actual_verifier_cmd,
        detected_standards=detected_summary
    )

    loop_md_path = output_dir / "LOOP.md"
    loop_md_path.write_text(loop_md, encoding="utf-8")
    print(f"  + Created {loop_md_path} (Detected: {detected_summary})")

    scripts_dir = output_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    verifier_path = scripts_dir / "verify_gate.py"
    verifier_content = VERIFIER_SCRIPT_TEMPLATE.format(verifier_cmd=actual_verifier_cmd)
    verifier_path.write_text(verifier_content, encoding="utf-8")
    verifier_path.chmod(0o755)
    print(f"  + Created {verifier_path}")

    runner_path = scripts_dir / "run_loop.sh"
    runner_content = RUNNER_SCRIPT_TEMPLATE.format(
        title=spec["title"],
        max_iterations=spec["max_iterations"],
        verifier_cmd=actual_verifier_cmd
    )
    runner_path.write_text(runner_content, encoding="utf-8")
    runner_path.chmod(0o755)
    print(f"  + Created {runner_path}")

    if with_ai_context:
        scaffold_ai_context(output_dir)

    print("\n[OK] Loop contract, execution scaffolding, and .ai-context successfully created.")
    print(f"Review your contract: {loop_md_path}")

def main():
    parser = argparse.ArgumentParser(description="Scaffold an autonomous closed loop contract adhering to project standards and AI context memory.")
    parser.add_argument("--type", choices=list(TEMPLATES.keys()), default="general", help="Loop archetype")
    parser.add_argument("--goal", type=str, help="Specific goal statement")
    parser.add_argument("--verifier", type=str, help="Verification command (e.g. 'pytest', 'pnpm test')")
    parser.add_argument("--output", type=str, default=".", help="Directory where files will be created")
    parser.add_argument("--no-ai-context", action="store_true", help="Skip creating .ai-context/ directory")

    args = parser.parse_args()
    scaffold(
        output_dir=Path(args.output),
        archetype=args.type,
        goal=args.goal,
        verifier_cmd=args.verifier,
        with_ai_context=not args.no_ai_context
    )

if __name__ == "__main__":
    main()
