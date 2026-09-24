# AI Context & Durable Memory

This directory stores durable architecture knowledge and feature context across development loops and agent sessions. It ensures that neither human engineers nor future AI agents suffer from amnesia.

## Directory Layout
- `decisions/`: Architecture Decision Records (ADRs) named `NNN-<kebab-slug>.md`.
- `features/`: Feature context, key flows, and gotchas named `<feature-slug>.md`.

## Lifecycle in Loops
1. **Loop Start:** Read relevant files in `decisions/` and `features/` to absorb existing rules and past architectural decisions before taking action.
2. **Loop Finish:** Promote new architectural decisions to `decisions/` and update or create feature notes in `features/`.
