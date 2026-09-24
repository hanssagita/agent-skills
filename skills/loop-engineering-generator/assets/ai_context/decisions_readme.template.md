# Architecture Decision Records (ADRs)

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
- RFC: docs/rfcs/<slug>.md   (or internal doc link if applicable)
- Issue / Ticket: PROJ-1234 (if applicable)

## Context
<1–3 sentences: the problem / PRD driver / technical constraint>

## Decision
<chosen approach, 1–3 sentences>

## Alternatives rejected
- <approach> — <why not>

## Affected files / modules
- <path or module> — <what changes>
```
