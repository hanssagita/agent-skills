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
MAX_DIFF_LINES = 50

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

def load_template(filename: str) -> str:
    """Loads a template file from the skill's assets/ directory."""
    return (ASSETS_DIR / filename).read_text(encoding="utf-8")

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

    root_template = load_template("ai_context/root_readme.template.md")
    decisions_template = load_template("ai_context/decisions_readme.template.md")
    features_template = load_template("ai_context/features_readme.template.md")

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

    loop_md_template = load_template("LOOP_CONTRACT.template.md")
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

    verifier_template = load_template("verify_gate.template.py")
    verifier_content = verifier_template.format(verifier_cmd_repr=verifier_cmd_repr, max_diff_lines=MAX_DIFF_LINES)
    verifier_path = scripts_dir / "verify_gate.py"
    if write_file(verifier_path, verifier_content, force=force):
        try:
            verifier_path.chmod(0o755)
        except Exception:
            pass

    runner_template = load_template("run_loop.template.sh")
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
