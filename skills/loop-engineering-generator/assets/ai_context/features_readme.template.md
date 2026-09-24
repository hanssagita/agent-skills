# Feature Context Notes

This directory maintains persistent domain knowledge, layout, conventions, and gotchas for features across the codebase.

## Naming Formula
`<feature-slug>.md`
- Matches the feature domain or directory name (e.g. `auth.md`, `billing.md`, `checkout.md`).
- **Rule:** When modifying an existing feature, **update the existing file** rather than duplicating.

## Format & Template

```markdown
# Feature: <name>
<!-- Last updated: YYYY-MM-DD -->

## Where it lives
- Components: <path to UI components, e.g. src/features/<feature>/components/>
- Hooks / models: <path to hooks/stores/models, e.g. src/features/<feature>/{hooks,models}/>
- Routes: <page or endpoint routes>
- Tests: <path to test suites, e.g. tests/component/.../<feature>/>

## Key flows
- <flow name> — <entry point> → <outcome>

## Conventions / gotchas
- <thing future agents/developers must know: project gating, cache keys, translation namespace, retry rules, auth checks, etc.>

## Related decisions
- [[NNN-<slug>]] — <one line summary linking to decision ADR>
```
