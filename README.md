# Agent Skills Collection

A collection of modular agent skills compatible with [`skills.sh`](https://skills.sh) and modern AI coding assistants (Claude Code, Cursor, Antigravity, OpenCode, Windsurf, Cline, Aider, GitHub Copilot).

---

## 📦 Available Skills

| Skill | Description | Location |
| :--- | :--- | :--- |
| **`loop-engineering-generator`** | Designs, scaffolds, audits, and executes autonomous closed-loop workflows with objective evidence gates, maker-checker separation, bounded iteration budgets, and zero comprehension debt. Adapts to existing repository standards or grills on greenfield projects. | [`skills/loop-engineering-generator`](./skills/loop-engineering-generator) |

---

## 🚀 Installation & Usage

Install directly using the `skills` CLI:

```bash
# Install loop-engineering-generator into your project
npx skills add hanssagita/agent-skills/skills/loop-engineering-generator
```

### Slash Command / Invocation

Once installed, trigger the skill via:
- `/loop-engineering`
- `"run a loop engineering cycle to fix..."`
- `"scaffold a loop contract for..."`
- `"audit this agent loop failure..."`

---

## ⚡ Operational Modes

1. **Scaffold Mode:** Generate production contracts (`LOOP.md`), test runners, and objective gates.
   ```bash
   python3 skills/loop-engineering-generator/scripts/scaffold_loop.py --type code-tdd --goal "Fix webhook auth"
   ```
   *Auto-detects existing repository standards (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, etc.) and sets the verifier command to match the native test runner.*

2. **In-Session Execution Mode:** Follows the closed **Plan → Do → Verify → Decide → Promote Context** loop:
   - **Plan:** State single next surgical action and test hypothesis.
   - **Do (Maker):** Minimal code change adhering to simplicity constraints.
   - **Verify (Checker):** Run objective test command (exit code 0).
   - **Decide:** Exit on pass; feed errors back; hard stop at max 4 iterations.
   - **Promote Context:** On pass, record decisions in `.ai-context/decisions/` and update `.ai-context/features/`.

3. **Audit & Diagnosis Mode:** Diagnoses whether agent failure stems from **Harness**, **Loop**, **Graph**, or **Environment** layers.

---

## 🧠 Durable AI Context Memory (`.ai-context/`)

Every finished loop promotes learned context into `.ai-context/` to prevent AI amnesia:

- **Architecture Decision Records (ADRs):**
  - Path: `.ai-context/decisions/NNN-<kebab-slug>.md`
  - Records: Problem context, decision, alternatives rejected, affected files.
- **Feature Context Notes:**
  - Path: `.ai-context/features/<feature-slug>.md`
  - Records: Where code lives, key flows, gotchas/conventions, and related ADR links.
  - *Rule: Updates existing feature notes rather than creating duplicates.*

---

## 🛡️ The Environment Discovery Protocol

Before building or running any loop:

- **Path A: Existing (Brownfield) Repository:**
  - Inspects workspace manifests (`package.json`, `Cargo.toml`, `pyproject.toml`, `pom.xml`, `README.md`, `AGENTS.md`).
  - Calibrates the loop verifier to the repo's native package manager and test runner (e.g. `pnpm test`, `pytest`, `cargo test`).
  - Respects established lint rules and architectural conventions.

- **Path B: Greenfield (New Project) Interview & Grill Gate:**
  - If no codebase exists, the skill **refuses to make silent assumptions**.
  - Proactively interviews and grills the user on:
    1. Language & Runtime (e.g. TypeScript/Node, Python, Go, Rust)
    2. Framework & Architecture
    3. Tooling & Package Manager (e.g. pnpm, cargo, poetry)
    4. Testing Harness (Vitest, Pytest, Go test — or scaffolds tests first)
    5. Binary Success Definition & Iteration Budget

---

## 🧠 Core Principles

- **100% LLM & IDE Agnostic:** Operates identically in Claude Code, Cursor, Antigravity, OpenCode, Windsurf, Cline, Aider, or pure terminal shell scripts.
- **Do not loop on confidence. Loop on evidence.** An agent saying "it looks good" is not a stop condition.
- **Stop engineering the agent. Start engineering the environment.** Leverage lives in the harness and verifier gates.
- **Maker-Checker Split:** The agent writing code must not be the sole evaluator of correctness.
- **Comprehension Debt Protection:** Bounded iterations ($\le 4$) and surgical diffs prevent unreviewable codebase rot.

