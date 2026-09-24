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
import shlex
import sys
from pathlib import Path

# Base directory for loading asset templates
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

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

FALLBACK_LOOP_MD_TEMPLATE = """# LOOP CONTRACT: {title}

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
"""

FALLBACK_VERIFIER_TEMPLATE = """#!/usr/bin/env python3
\"\"\"
Objective Verification Gate for Loop
Exits 0 on success, non-zero on failure.
\"\"\"

import subprocess
import sys
import os

def check_diff_budget(max_lines=100):
    \"\"\"Optional check ensuring uncommitted diffs remain surgical.\"\"\"
    try:
        res = subprocess.run("git diff --shortstat", shell=True, capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            import re
            m_ins = re.search(r'(\\d+)\\s+insertions?\\(\\+\\)', res.stdout)
            m_del = re.search(r'(\\d+)\\s+deletions?\\(-\\)', res.stdout)
            ins = int(m_ins.group(1)) if m_ins else 0
            dels = int(m_del.group(1)) if m_del else 0
            total = ins + dels
            if total > max_lines:
                print(f"[FAIL] Diff budget exceeded: {{total}} lines changed (max: {{max_lines}}). Keep changes surgical!")
                return False
            print(f"[PASS] Diff budget check: {{total}}/{{max_lines}} lines changed.")
    except Exception as e:
        print(f"[WARN] Diff budget check skipped: {{e}}")
    return True

def run_check(cmd, description):
    print(f"[*] Checking: {{description}}...")
    if not cmd or "TODO: Configure your verification command" in cmd:
        print("[FAIL] No verification command configured! Please set a valid test command in scripts/verify_gate.py.")
        return False

    if "verify_gate.py" in cmd:
        print("[FAIL] Self-referential command detected! verify_gate.py cannot invoke itself.")
        return False

    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[FAIL] {{description}} failed!")
        if res.stdout:
            print(res.stdout)
        if res.stderr:
            print(res.stderr)
        return False
    print(f"[PASS] {{description}} passed.")
    return True

def main():
    # Verification checks tailored to project standards:
    checks = [
        ({verifier_cmd_repr}, "Primary Verification Gate"),
    ]

    for cmd, desc in checks:
        if not run_check(cmd, desc):
            sys.exit(1)

    print("\\n[SUCCESS] All verification gates passed. Loop stop condition met.")
    sys.exit(0)

if __name__ == "__main__":
    main()
"""

FALLBACK_RUNNER_TEMPLATE = """#!/usr/bin/env bash
set -euo pipefail

# Closed Loop Execution Harness
# Usage:
#   ./scripts/run_loop.sh                (Interactive step mode: prompts between iterations)
#   ./scripts/run_loop.sh "<command>"    (Automated worker mode: runs <command> each iteration before verifying)

MAX_ITER={max_iterations}
STEP_CMD="${{1:-}}"
VERIFIER_CMD={verifier_sh_cmd}

echo "=================================================="
echo " Starting Closed Loop: {title}"
echo " Max Iterations: $MAX_ITER"
if [ -n "$STEP_CMD" ]; then
    echo " Step Command: $STEP_CMD"
else
    echo " Mode: Interactive (make changes between iterations)"
fi
echo "=================================================="

ITER=1
while [ "$ITER" -le "$MAX_ITER" ]; do
    echo ""
    echo ">>> Iteration $ITER of $MAX_ITER..."

    # If an automated step command was supplied, run it first
    if [ -n "$STEP_CMD" ]; then
        echo "[STEP] Executing: $STEP_CMD"
        eval "$STEP_CMD" || true
    fi

    # Run the verification check
    if eval "$VERIFIER_CMD"; then
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

    # In interactive mode, wait for user/agent edit
    if [ -z "$STEP_CMD" ]; then
        if [ -t 0 ]; then
            echo ""
            read -r -p "Apply surgical edit, then press [Enter] to run iteration $((ITER + 1)) (or Ctrl+C to abort)..."
        else
            echo "[INFO] Non-interactive execution without step command; stopping after single verification check."
            exit 1
        fi
    fi

    ITER=$((ITER + 1))
done
"""

def load_template(filename: str, fallback: str) -> str:
    """Loads a template file from assets/ if available, otherwise returns fallback string."""
    template_path = ASSETS_DIR / filename
    if template_path.exists():
        try:
            return template_path.read_text(encoding="utf-8")
        except Exception:
            pass
    return fallback

def write_file(path: Path, content: str, force: bool = False) -> bool:
    """Writes content to path, respecting force flag to avoid clobbering existing files."""
    if path.exists() and not force:
        print(f"  ~ Skipped {path} (already exists, use --force to overwrite)")
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  + Created {path}")
    return True

def detect_repository_standards(target_dir: Path) -> dict:
    """Inspects workspace to detect language, package manager, test runner, and AI context."""
    standards = {
        "stacks": [],
        "default_test_cmd": None,
        "configs_found": []
    }

    # Check for existing .ai-context
    ai_ctx = target_dir / ".ai-context"
    if ai_ctx.exists():
        standards["configs_found"].append(".ai-context/")
        adrs = [f.name for f in (ai_ctx / "decisions").glob("*.md")] if (ai_ctx / "decisions").exists() else []
        feats = [f.name for f in (ai_ctx / "features").glob("*.md")] if (ai_ctx / "features").exists() else []
        adrs_clean = [f for f in adrs if f != "README.md"]
        feats_clean = [f for f in feats if f != "README.md"]
        if adrs_clean or feats_clean:
            standards["configs_found"].append(f"AI-Context({len(adrs_clean)} ADRs, {len(feats_clean)} Features)")

    # JavaScript / TypeScript detection
    pkg_json = target_dir / "package.json"
    if pkg_json.exists():
        standards["configs_found"].append("package.json")
        is_ts = (target_dir / "tsconfig.json").exists()
        lang = "TypeScript" if is_ts else "JavaScript"

        # Detect package manager
        if (target_dir / "pnpm-lock.yaml").exists():
            pm = "pnpm"
        elif (target_dir / "yarn.lock").exists():
            pm = "yarn"
        elif (target_dir / "bun.lockb").exists():
            pm = "bun"
        else:
            pm = "npm"

        has_test_script = False
        try:
            with open(pkg_json, "r", encoding="utf-8") as f:
                data = json.load(f)
            scripts = data.get("scripts", {})
            if "test" in scripts:
                has_test_script = True
        except Exception:
            pass

        stack_name = f"{lang}/Node ({pm})"
        standards["stacks"].append(stack_name)
        if has_test_script and not standards["default_test_cmd"]:
            standards["default_test_cmd"] = f"{pm} test"

    # Python detection
    pyproject = target_dir / "pyproject.toml"
    pytest_ini = target_dir / "pytest.ini"
    reqs = target_dir / "requirements.txt"
    setup_py = target_dir / "setup.py"
    if pyproject.exists() or pytest_ini.exists() or reqs.exists() or setup_py.exists():
        standards["stacks"].append("Python")
        if not standards["default_test_cmd"]:
            standards["default_test_cmd"] = "pytest"
        if pyproject.exists():
            standards["configs_found"].append("pyproject.toml")
        if pytest_ini.exists():
            standards["configs_found"].append("pytest.ini")
        if reqs.exists():
            standards["configs_found"].append("requirements.txt")

    # Rust
    cargo = target_dir / "Cargo.toml"
    if cargo.exists():
        standards["stacks"].append("Rust (cargo)")
        standards["configs_found"].append("Cargo.toml")
        if not standards["default_test_cmd"]:
            standards["default_test_cmd"] = "cargo test"

    # Go
    gomod = target_dir / "go.mod"
    if gomod.exists():
        standards["stacks"].append("Go")
        standards["configs_found"].append("go.mod")
        if not standards["default_test_cmd"]:
            standards["default_test_cmd"] = "go test ./..."

    # Java / Maven / Gradle
    if (target_dir / "pom.xml").exists():
        standards["stacks"].append("Java (Maven)")
        standards["configs_found"].append("pom.xml")
        if not standards["default_test_cmd"]:
            standards["default_test_cmd"] = "mvn test"
    elif (target_dir / "build.gradle").exists() or (target_dir / "build.gradle.kts").exists():
        standards["stacks"].append("Java/Kotlin (Gradle)")
        standards["configs_found"].append("build.gradle")
        if not standards["default_test_cmd"]:
            standards["default_test_cmd"] = "./gradlew test"

    # Agent / Project Guides
    for guide in ["README.md", "AGENTS.md", "CLAUDE.md", ".cursorrules"]:
        if (target_dir / guide).exists():
            standards["configs_found"].append(guide)

    return standards

def scaffold_ai_context(target_dir: Path, force: bool = False):
    """Scaffolds .ai-context structure with guides and templates loaded from assets."""
    ai_ctx_dir = target_dir / ".ai-context"

    root_template = load_template("ai_context/root_readme.template.md", "# AI Context\n")
    decisions_template = load_template("ai_context/decisions_readme.template.md", "# ADRs\n")
    features_template = load_template("ai_context/features_readme.template.md", "# Features\n")

    write_file(ai_ctx_dir / "README.md", root_template, force=force)
    write_file(ai_ctx_dir / "decisions" / "README.md", decisions_template, force=force)
    write_file(ai_ctx_dir / "features" / "README.md", features_template, force=force)

def scaffold(output_dir: Path, archetype: str, goal: str = None, verifier_cmd: str = None, with_ai_context: bool = True, force: bool = False):
    output_dir.mkdir(parents=True, exist_ok=True)
    spec = TEMPLATES.get(archetype, TEMPLATES["general"])

    # Detect existing repo standards
    detected = detect_repository_standards(output_dir)
    if not detected["configs_found"] and output_dir.resolve() != Path.cwd().resolve():
        detected = detect_repository_standards(Path.cwd())

    actual_goal = goal if goal else spec["goal"]

    # Prevent self-referential / infinite loops:
    # If no verifier specified and no stack detected, use an instructive placeholder error command
    if verifier_cmd:
        actual_verifier_cmd = verifier_cmd
    elif detected["default_test_cmd"]:
        actual_verifier_cmd = detected["default_test_cmd"]
    else:
        actual_verifier_cmd = 'echo "TODO: Configure your verification command in scripts/verify_gate.py" && exit 1'

    # Safe escaping for code templates:
    # verifier_cmd_repr is a valid Python string literal escaping quotes and backslashes
    verifier_cmd_repr = json.dumps(actual_verifier_cmd)
    # verifier_sh_cmd is safely quoted for bash execution
    verifier_sh_cmd = shlex.quote(actual_verifier_cmd)

    stacks_str = ", ".join(detected["stacks"]) if detected["stacks"] else "unknown"
    detected_summary = f"{stacks_str} (found: {', '.join(detected['configs_found']) if detected['configs_found'] else 'none'})"

    loop_md_template = load_template("LOOP_CONTRACT.template.md", FALLBACK_LOOP_MD_TEMPLATE)
    loop_md = loop_md_template.format(
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
    write_file(loop_md_path, loop_md, force=force)

    scripts_dir = output_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    verifier_template = load_template("verify_gate.template.py", FALLBACK_VERIFIER_TEMPLATE)
    verifier_content = verifier_template.format(verifier_cmd_repr=verifier_cmd_repr)
    verifier_path = scripts_dir / "verify_gate.py"
    if write_file(verifier_path, verifier_content, force=force):
        try:
            verifier_path.chmod(0o755)
        except Exception:
            pass

    runner_template = load_template("run_loop.template.sh", FALLBACK_RUNNER_TEMPLATE)
    runner_content = runner_template.format(
        title=spec["title"],
        max_iterations=spec["max_iterations"],
        verifier_sh_cmd=verifier_sh_cmd
    )
    runner_path = scripts_dir / "run_loop.sh"
    if write_file(runner_path, runner_content, force=force):
        try:
            runner_path.chmod(0o755)
        except Exception:
            pass

    if with_ai_context:
        scaffold_ai_context(output_dir, force=force)

    print("\n[OK] Scaffolding process complete.")
    print(f"Review your contract: {loop_md_path}")

def main():
    parser = argparse.ArgumentParser(description="Scaffold an autonomous closed loop contract adhering to project standards and AI context memory.")
    parser.add_argument("--type", choices=list(TEMPLATES.keys()), default="general", help="Loop archetype")
    parser.add_argument("--goal", type=str, help="Specific goal statement")
    parser.add_argument("--verifier", type=str, help="Verification command (e.g. 'pytest', 'pnpm test')")
    parser.add_argument("--output", type=str, default=".", help="Directory where files will be created")
    parser.add_argument("--no-ai-context", action="store_true", help="Skip creating .ai-context/ directory")
    parser.add_argument("--force", "-f", action="store_true", help="Force overwrite existing files")

    args = parser.parse_args()
    scaffold(
        output_dir=Path(args.output),
        archetype=args.type,
        goal=args.goal,
        verifier_cmd=args.verifier,
        with_ai_context=not args.no_ai_context,
        force=args.force
    )

if __name__ == "__main__":
    main()
