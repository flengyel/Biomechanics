# Design Contract

## Scope

Build a Python package that represents student biomechanics work as structured force-torque diagrams and returns structured diagnostic failures.

## Current Guardrails

- Do not begin with a graphical UI, full-body simulation, finite element analysis, machine learning, reinforcement learning, or a game engine.
- Do not infer answer keys from slide appearance alone.
- Treat external standards pages as metadata references unless an instructor explicitly supplies values.
- Keep student-facing language separate from the diagnostic engine.
- Report the earliest blocking conceptual error before downstream errors.
